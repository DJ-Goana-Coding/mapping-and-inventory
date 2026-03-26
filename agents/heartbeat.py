"""
Heartbeat — Phase 23 All-Seeing Eye Telemetry Agent
====================================================
Implements the daily "Heartbeat Ping" required by Phase 23 Task 5.

For every sovereign node listed in ``spark_ui/fleet_manifest.json`` the agent
attempts a lightweight connectivity probe (GitHub API ``GET /repos/{owner}/{repo}``)
and updates the node's ``health_status`` field with one of:

* ``ONLINE & PURIFIED``   — repo is reachable and healthy
* ``UPGRADE REQUIRED``    — repo exists but is flagged for update
* ``CONNECTION SEVERED``  — repo cannot be reached or does not exist

The updated manifest is written back to ``spark_ui/fleet_manifest.json`` so
the hub always reflects live fleet health.

Schedule
--------
Run once per day (e.g. via cron, GitHub Actions schedule, or the Swarm
Controller's background loop).  The async entry-point is
:func:`run_heartbeat_cycle`.

Environment
-----------
``GITHUB_TOKEN`` or ``GH_PAT``  — GitHub Personal Access Token (read-only
``public_repo`` scope is sufficient for public repositories).

sovereignty_layer : Phase 23 — Lattice Purification & Omniscient Sync
last_purified_date: 2026-03-26
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
import urllib.error
import urllib.request
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = pathlib.Path(__file__).parent.parent
_MANIFEST_PATH = _REPO_ROOT / "spark_ui" / "fleet_manifest.json"

_GITHUB_API_BASE = "https://api.github.com"
_GITHUB_API_VERSION = "2022-11-28"

# Health-status constants
STATUS_ONLINE = "ONLINE & PURIFIED"
STATUS_UPGRADE = "UPGRADE REQUIRED"
STATUS_SEVERED = "CONNECTION SEVERED"

# Repos whose default branch is behind more than this many days are flagged
_UPGRADE_THRESHOLD_DAYS = 180


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _get_github_token() -> str:
    """Read GitHub PAT from environment variables (never hard-coded)."""
    return os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT", "")


def _probe_repo(full_name: str, token: str) -> dict[str, Any]:
    """
    Call ``GET /repos/{full_name}`` and return a status summary dict.

    Returns a dict with keys ``health_status``, ``pushed_at``, and
    ``default_branch``.
    """
    url = f"{_GITHUB_API_BASE}/repos/{full_name}"
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", _GITHUB_API_VERSION)
    if token:
        req.add_header("Authorization", f"Bearer {token}")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        logger.warning("[Heartbeat] HTTP %s for repo '%s'.", exc.code, full_name)
        return {"health_status": STATUS_SEVERED, "pushed_at": None, "default_branch": None}
    except OSError as exc:
        logger.warning("[Heartbeat] Network error probing '%s': %s", full_name, exc)
        return {"health_status": STATUS_SEVERED, "pushed_at": None, "default_branch": None}

    pushed_at_str: str | None = data.get("pushed_at")
    default_branch: str | None = data.get("default_branch")

    health_status = STATUS_ONLINE
    if pushed_at_str:
        try:
            pushed_at = datetime.fromisoformat(pushed_at_str.replace("Z", "+00:00"))
            age_days = (datetime.now(UTC) - pushed_at).days
            if age_days > _UPGRADE_THRESHOLD_DAYS:
                health_status = STATUS_UPGRADE
        except ValueError:
            pass

    return {
        "health_status": health_status,
        "pushed_at": pushed_at_str,
        "default_branch": default_branch,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def run_heartbeat_cycle(manifest_path: pathlib.Path = _MANIFEST_PATH) -> dict[str, Any]:
    """
    Probe every sovereign node in *manifest_path* and update its
    ``health_status``.  Returns a summary report dict.

    Parameters
    ----------
    manifest_path:
        Path to the fleet manifest JSON.  Defaults to
        ``spark_ui/fleet_manifest.json``.
    """
    if not manifest_path.exists():
        logger.error("[Heartbeat] Manifest not found: %s", manifest_path)
        return {"error": "manifest_not_found", "path": str(manifest_path)}

    with manifest_path.open(encoding="utf-8") as fh:
        manifest: dict[str, Any] = json.load(fh)

    token = _get_github_token()
    if not token:
        logger.warning(
            "[Heartbeat] No GitHub token found. "
            "Set GITHUB_TOKEN or GH_PAT for authenticated probes."
        )

    statuses: dict[str, str] = {}
    nodes_probed = 0

    for node in manifest.get("sovereign_nodes", []):
        repo: str | None = node.get("repo")
        if not repo:
            continue
        probe = _probe_repo(repo, token)
        node["health_status"] = probe["health_status"]
        node["last_heartbeat"] = datetime.now(UTC).isoformat()
        if probe["pushed_at"]:
            node["pushed_at"] = probe["pushed_at"]
        statuses[repo] = probe["health_status"]
        nodes_probed += 1
        logger.info(
            "[Heartbeat] %s → %s",
            repo,
            probe["health_status"],
        )

    # Update manifest metadata
    manifest["last_heartbeat"] = datetime.now(UTC).isoformat()
    manifest["phase"] = "Phase 23 — Lattice Purification & Omniscient Sync"

    with manifest_path.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2, ensure_ascii=False)

    report = {
        "cycle_completed": datetime.now(UTC).isoformat(),
        "nodes_probed": nodes_probed,
        "statuses": statuses,
        "online": sum(1 for s in statuses.values() if s == STATUS_ONLINE),
        "upgrade_required": sum(1 for s in statuses.values() if s == STATUS_UPGRADE),
        "severed": sum(1 for s in statuses.values() if s == STATUS_SEVERED),
    }
    logger.info(
        "[Heartbeat] Cycle complete — probed=%d online=%d upgrade=%d severed=%d",
        report["nodes_probed"],
        report["online"],
        report["upgrade_required"],
        report["severed"],
    )
    return report


# ---------------------------------------------------------------------------
# Stand-alone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _manifest = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else _MANIFEST_PATH
    result = run_heartbeat_cycle(_manifest)
    print("\n=== Heartbeat Report ===")
    print(f"  Nodes probed    : {result.get('nodes_probed', 0)}")
    print(f"  Online          : {result.get('online', 0)}")
    print(f"  Upgrade required: {result.get('upgrade_required', 0)}")
    print(f"  Severed         : {result.get('severed', 0)}")
