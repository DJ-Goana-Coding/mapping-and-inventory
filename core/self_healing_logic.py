"""
core/self_healing_logic.py — Spoke health monitor and auto-restart pusher.

Continuously (or on-demand) probes each registered spoke's HuggingFace Space
and GitHub repo.  When a spoke returns HTTP 503, 404, or times out:

1. Logs the failure to ``data/monitoring/self_healing_log.json``.
2. Attempts a self-healing "restart commit" — pushes a trivial whitespace
   change to the spoke's GitHub repo so HuggingFace rebuilds the Space.
3. If a pre-built ``deploy/skeleton/`` template exists for the spoke, it
   pushes the full skeleton (``app.py`` + ``requirements.txt`` + ``README.md``)
   to clear the "No Application File" error.

Authentication
--------------
Requires ``GH_TOKEN`` (or ``GITHUB_TOKEN``) in the environment with
``contents:write`` on the target org.  Without a token, the health check runs
but the auto-push is skipped with a warning.

Run modes
---------
* **One-shot CLI** (check and heal once)::

      python core/self_healing_logic.py
      python core/self_healing_logic.py --spoke ARK-CORE --dry-run

* **Daemon mode** (loop every N seconds)::

      python core/self_healing_logic.py --daemon --interval 300

* **Imported**::

      from core.self_healing_logic import SelfHealingMonitor
      monitor = SelfHealingMonitor()
      monitor.check_all()
"""
from __future__ import annotations

import argparse
import base64
import json
import logging
import os
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests

logger = logging.getLogger("self_healing")

REPO_ROOT = Path(__file__).resolve().parent.parent
MONITOR_DIR = REPO_ROOT / "data" / "monitoring"
HEAL_LOG_PATH = MONITOR_DIR / "self_healing_log.json"
HANDSHAKE_MANIFEST_PATH = REPO_ROOT / "data" / "handshake_manifest.json"
SKELETON_DIR = REPO_ROOT / "deploy" / "skeleton"

GITHUB_API = "https://api.github.com"
DEFAULT_ORG = "DJ-Goana-Coding"
PROBE_TIMEOUT = 8.0
RESTART_COMMIT_MSG = "♻️ Self-Heal: trigger Space rebuild [automated]"


# ---------------------------------------------------------------------------
# Status codes that indicate a broken Space
# ---------------------------------------------------------------------------

_BROKEN_HTTP_CODES = {503, 502, 500, 404}
_HEALTHY_HTTP_CODES = {200, 301, 302, 307, 308, 401, 403}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class SpokeHealthRecord:
    spoke_name: str
    checked_at: str
    hf_status: str          # "healthy" | "broken" | "no_space" | "timeout"
    hf_http_code: Optional[int]
    gh_status: str          # "healthy" | "broken" | "no_repo" | "timeout"
    gh_http_code: Optional[int]
    heal_attempted: bool
    heal_outcome: str       # "ok" | "skipped" | "no_token" | "error:<msg>"


@dataclass
class HealLog:
    version: str = "1.0.0"
    last_run: str = ""
    runs: int = 0
    records: List[SpokeHealthRecord] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_spoke_manifest() -> dict:
    if HANDSHAKE_MANIFEST_PATH.exists():
        try:
            return json.loads(HANDSHAKE_MANIFEST_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {"spokes": {}}


def _probe_url(url: str) -> tuple[str, Optional[int]]:
    """HEAD-probe a URL.  Returns (status_str, http_code_or_None)."""
    if not url:
        return "no_space", None
    try:
        resp = requests.head(url, timeout=PROBE_TIMEOUT, allow_redirects=True)
        code = resp.status_code
        if code in _HEALTHY_HTTP_CODES or (200 <= code < 400):
            return "healthy", code
        if code in _BROKEN_HTTP_CODES:
            return "broken", code
        return "unknown", code
    except requests.Timeout:
        return "timeout", None
    except requests.RequestException:
        return "unreachable", None


def _get_gh_token() -> Optional[str]:
    return os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")


def _get_file_sha(owner: str, repo: str, path: str, token: str) -> Optional[str]:
    """Return the blob SHA of an existing file (needed to update it)."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers={"Authorization": f"token {token}"}, timeout=15)
    if resp.status_code == 200:
        return resp.json().get("sha")
    return None


def _push_file(
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    token: str,
    branch: str = "main",
) -> bool:
    """Create or update a single file in a GitHub repo.  Returns True on success."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    payload: Dict = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    existing_sha = _get_file_sha(owner, repo, path, token)
    if existing_sha:
        payload["sha"] = existing_sha
    resp = requests.put(
        url,
        headers={"Authorization": f"token {token}", "Content-Type": "application/json"},
        json=payload,
        timeout=30,
    )
    if resp.status_code in (200, 201):
        return True
    logger.warning("GitHub push failed: %s %s → HTTP %d", owner, path, resp.status_code)
    return False


def _restart_commit(owner: str, repo: str, token: str) -> str:
    """Push a trivial whitespace bump to trigger a HF Space rebuild.

    Returns an outcome string.
    """
    # Touch a lightweight sentinel file rather than modifying app code.
    content = f"# Self-heal restart: {datetime.now(timezone.utc).isoformat()}\n"
    ok = _push_file(owner, repo, ".self_heal_ping", content, RESTART_COMMIT_MSG, token)
    return "ok" if ok else "error:push_failed"


def _push_skeleton(owner: str, repo: str, token: str) -> str:
    """Push the skeleton app.py/requirements.txt from deploy/skeleton/ if it exists."""
    if not SKELETON_DIR.is_dir():
        return "skipped:no_skeleton_dir"
    pushed = 0
    for fpath in SKELETON_DIR.glob("*"):
        if not fpath.is_file():
            continue
        try:
            content = fpath.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        ok = _push_file(owner, repo, fpath.name, content, RESTART_COMMIT_MSG, token)
        if ok:
            pushed += 1
    return f"ok:{pushed}_files" if pushed else "error:no_files_pushed"


def _load_heal_log() -> HealLog:
    if HEAL_LOG_PATH.exists():
        try:
            raw = json.loads(HEAL_LOG_PATH.read_text(encoding="utf-8"))
            records = [SpokeHealthRecord(**r) for r in raw.get("records", [])]
            return HealLog(
                version=raw.get("version", "1.0.0"),
                last_run=raw.get("last_run", ""),
                runs=raw.get("runs", 0),
                records=records,
            )
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return HealLog()


def _save_heal_log(log: HealLog) -> None:
    MONITOR_DIR.mkdir(parents=True, exist_ok=True)
    HEAL_LOG_PATH.write_text(
        json.dumps(log.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Core monitor
# ---------------------------------------------------------------------------


class SelfHealingMonitor:
    """Probe spokes and push restart commits when breakage is detected."""

    def __init__(
        self,
        dry_run: bool = False,
        push_skeleton_on_404: bool = True,
    ) -> None:
        self.dry_run = dry_run
        self.push_skeleton_on_404 = push_skeleton_on_404
        self._manifest = _load_spoke_manifest()

    def _heal_spoke(
        self,
        spoke_name: str,
        spoke_cfg: dict,
        hf_status: str,
        hf_code: Optional[int],
    ) -> str:
        """Attempt to push a restart commit for a broken spoke.

        Returns an outcome string.
        """
        gh_url = spoke_cfg.get("github_url", "")
        if not gh_url or "github.com" not in gh_url:
            return "skipped:no_github_url"

        token = _get_gh_token()
        if not token:
            return "no_token"

        # Parse owner/repo from URL
        parts = gh_url.rstrip("/").split("/")
        if len(parts) < 2:
            return "error:bad_github_url"
        owner, repo = parts[-2], parts[-1]

        if self.dry_run:
            logger.info("[DRY-RUN] Would push restart commit to %s/%s", owner, repo)
            return "skipped:dry_run"

        # If 404 and skeleton push is enabled, push the skeleton
        if hf_code == 404 and self.push_skeleton_on_404:
            outcome = _push_skeleton(owner, repo, token)
            if "ok" in outcome:
                return f"skeleton_pushed:{outcome}"

        return _restart_commit(owner, repo, token)

    def check_spoke(self, spoke_name: str, spoke_cfg: dict) -> SpokeHealthRecord:
        """Check a single spoke and heal if broken."""
        hf_url = spoke_cfg.get("hf_space_url", "")
        gh_url = spoke_cfg.get("github_url", "")

        hf_status, hf_code = _probe_url(hf_url)
        gh_status, gh_code = _probe_url(gh_url)

        needs_heal = hf_status in ("broken", "timeout", "unreachable")
        heal_attempted = False
        heal_outcome = "skipped"

        if needs_heal:
            logger.warning("Spoke '%s' is %s (HTTP %s) — attempting heal", spoke_name, hf_status, hf_code)
            heal_outcome = self._heal_spoke(spoke_name, spoke_cfg, hf_status, hf_code)
            heal_attempted = True
        else:
            logger.info("Spoke '%s' HF=%s (HTTP %s), GH=%s", spoke_name, hf_status, hf_code, gh_status)

        return SpokeHealthRecord(
            spoke_name=spoke_name,
            checked_at=datetime.now(timezone.utc).isoformat(),
            hf_status=hf_status,
            hf_http_code=hf_code,
            gh_status=gh_status,
            gh_http_code=gh_code,
            heal_attempted=heal_attempted,
            heal_outcome=heal_outcome,
        )

    def check_all(self, target_spokes: Optional[List[str]] = None) -> List[SpokeHealthRecord]:
        """Check all (or a subset of) registered spokes."""
        spokes = self._manifest.get("spokes", {})
        results: List[SpokeHealthRecord] = []

        for name, cfg in spokes.items():
            if target_spokes and name not in target_spokes:
                continue
            record = self.check_spoke(name, cfg)
            results.append(record)

        # Persist to heal log
        log = _load_heal_log()
        log.runs += 1
        log.last_run = datetime.now(timezone.utc).isoformat()
        log.records = (log.records + results)[-500:]  # keep last 500 records
        _save_heal_log(log)

        broken = [r for r in results if r.hf_status in ("broken", "timeout", "unreachable")]
        logger.info(
            "Health check complete: %d spokes checked, %d broken, %d healed",
            len(results),
            len(broken),
            sum(1 for r in broken if r.heal_attempted and "ok" in r.heal_outcome),
        )
        return results

    def run_daemon(self, interval_s: int = 300) -> None:
        """Run check_all in a loop indefinitely."""
        logger.info("Self-healing daemon started (interval=%ds)", interval_s)
        while True:
            try:
                self.check_all()
            except Exception:  # noqa: BLE001
                logger.exception("Unhandled error in health check cycle")
            time.sleep(interval_s)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _main(argv=None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(description="Spoke health monitor and auto-heal pusher")
    parser.add_argument("--spoke", nargs="+", default=None, help="Specific spokes to check")
    parser.add_argument("--dry-run", action="store_true", help="Check but do not push")
    parser.add_argument("--daemon", action="store_true", help="Run continuously")
    parser.add_argument("--interval", type=int, default=300, help="Daemon poll interval (seconds)")
    parser.add_argument("--no-skeleton", action="store_true", help="Disable skeleton push on 404")
    args = parser.parse_args(argv)

    monitor = SelfHealingMonitor(
        dry_run=args.dry_run,
        push_skeleton_on_404=not args.no_skeleton,
    )

    if args.daemon:
        monitor.run_daemon(args.interval)
    else:
        results = monitor.check_all(target_spokes=args.spoke)
        for r in results:
            icon = "✅" if r.hf_status == "healthy" else "❌"
            heal = f" → {r.heal_outcome}" if r.heal_attempted else ""
            print(f"  {icon} {r.spoke_name}: HF={r.hf_status}({r.hf_http_code}) GH={r.gh_status}{heal}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
