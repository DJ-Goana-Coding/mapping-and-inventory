"""
Repository Harvester — GitHub Fleet Manifest Generator
=======================================================
Implements Tasks 1–3 from the mapping-and-inventory integration spec:

Task 1 — Global Repository Harvesting
    Uses the GitHub REST API (``GET /user/repos``) to collect all repositories
    associated with the authenticated account and produces ``fleet_manifest.json``
    at the repository root.

Task 2 — Lattice Connection / Shadow Links
    Repositories that are registered as git submodules under ``/nodes/`` or
    ``/lattice/`` receive a ``link_type`` of ``"submodule"``; all others receive
    ``"shadow"`` and a ``raw_content_url`` pointing to their GitHub API endpoint
    for on-demand metadata fetching.

Task 3 — Architectural Categorization
    Repositories are assigned a ``framework_tag`` (``"Tia"``, ``"Oracle"``, or
    ``"General"``) and a ``district_id`` (``"Intelligence"``, ``"Operations"``,
    ``"Archive"``, or ``"Research"``) based on topic analysis of their name,
    description, and detected language.

Security
--------
The GitHub Personal Access Token is read exclusively from the ``GITHUB_TOKEN``
environment variable (or ``GH_PAT`` as a fallback), which should be stored in
GitHub Secrets — never hard-coded.

Sanitization
------------
Repository descriptions are scrubbed through :func:`utils.path_sanitizer.sanitize`
before being written to the manifest.

Audit Logging
-------------
All HTTP requests, connection errors, and synchronization outcomes are written
to ``sync_audit.log`` in the repository root.

Usage::

    python -m agents.repo_harvester
    # or
    from agents.repo_harvester import harvest
    manifest = harvest()
"""
from __future__ import annotations

import json
import logging
import os
import pathlib
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any

import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).parent.parent
MANIFEST_PATH: pathlib.Path = _REPO_ROOT / "fleet_manifest.json"
AUDIT_LOG_PATH: pathlib.Path = _REPO_ROOT / "sync_audit.log"
INDEX_DIR: pathlib.Path = _REPO_ROOT / "District_05_OPEN_SOURCE_BIN" / "readme_index"

# ---------------------------------------------------------------------------
# Logging — dual output: console + sync_audit.log
# ---------------------------------------------------------------------------

_handler_console = logging.StreamHandler(sys.stdout)
_handler_file = logging.FileHandler(AUDIT_LOG_PATH, encoding="utf-8")
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[_handler_console, _handler_file],
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

_GITHUB_API_BASE = "https://api.github.com"
_METADATA_FIELDS = ("name", "full_name", "html_url", "description", "language", "updated_at")

# Sensitive-metadata patterns to strip from harvested descriptions
_SENSITIVE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"(?i)(api[_\s-]?key|token|secret|password|passw?d|auth)\s*[:=]\s*\S+"),
    re.compile(r"ghp_[A-Za-z0-9]{36,}"),          # GitHub PAT shape
    re.compile(r"sk-[A-Za-z0-9]{32,}"),            # OpenAI key shape
]


def _github_request(path: str, token: str, *, params: dict[str, str] | None = None) -> Any:
    """
    Execute a single authenticated GitHub API GET request.

    Parameters
    ----------
    path:
        API path starting with ``/``, e.g. ``/user/repos``.
    token:
        GitHub Personal Access Token.
    params:
        Optional query-string parameters.

    Returns
    -------
    Any
        Decoded JSON response body.

    Raises
    ------
    urllib.error.HTTPError
        On 4xx / 5xx responses.
    """
    url = _GITHUB_API_BASE + path
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mapping-and-inventory/repo-harvester",
        },
    )
    logger.debug("[API] GET %s", url)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_all_repos(token: str) -> list[dict[str, Any]]:
    """
    Page through ``GET /user/repos`` and return all repositories.

    Returns
    -------
    list[dict]
        Raw repository objects from the GitHub API.
    """
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        logger.info("[Harvester] Fetching repos — page %d …", page)
        try:
            batch = _github_request(
                "/user/repos",
                token,
                params={"per_page": "100", "page": str(page), "affiliation": "owner,collaborator,organization_member"},
            )
        except urllib.error.HTTPError as exc:
            logger.error("[Harvester] GitHub API error on page %d: %s %s", page, exc.code, exc.reason)
            raise
        except Exception as exc:
            logger.error("[Harvester] Unexpected error on page %d: %s", page, exc)
            raise

        if not batch:
            break
        repos.extend(batch)
        logger.info("[Harvester] Page %d → %d repo(s) received (running total: %d).", page, len(batch), len(repos))
        if len(batch) < 100:
            break
        page += 1
        time.sleep(0.5)   # be a good API citizen

    return repos


# ---------------------------------------------------------------------------
# Sanitization
# ---------------------------------------------------------------------------


def _sanitize_description(desc: str | None) -> str:
    """
    Remove sensitive tokens and local-path fragments from a repo description.

    Parameters
    ----------
    desc:
        Raw description string from the GitHub API (may be ``None``).

    Returns
    -------
    str
        Cleaned description safe for committing to the manifest.
    """
    if not desc:
        return ""

    try:
        from utils.path_sanitizer import sanitize as path_sanitize
        desc = path_sanitize(desc)
    except ImportError:
        pass

    for pattern in _SENSITIVE_PATTERNS:
        desc = pattern.sub("<REDACTED>", desc)

    return desc.strip()


# ---------------------------------------------------------------------------
# Categorization (Task 3)
# ---------------------------------------------------------------------------

# Keywords → Tia (AI / Intelligence layer)
_TIA_SIGNALS = frozenset(
    {
        "tia", "ai", "brain", "neural", "llm", "gpt", "chat",
        "voice", "mind", "intelligence", "cognitive", "rag", "vector",
        "embedding", "knowledge", "citadel", "command",
    }
)

# Keywords → Oracle (Trading / Data / Market layer)
_ORACLE_SIGNALS = frozenset(
    {
        "oracle", "trade", "trader", "trading", "market", "finance",
        "stock", "crypto", "signal", "analytics", "data", "quant",
        "pioneer", "vortex", "ccxt", "strategy",
    }
)

# District groupings
_DISTRICT_RULES: list[tuple[frozenset[str], str]] = [
    (frozenset({"ai", "brain", "tia", "intelligence", "neural", "llm", "gpt", "rag", "citadel"}), "Intelligence"),
    (frozenset({"trade", "trader", "trading", "market", "finance", "stock", "crypto", "signal", "pioneer", "oracle", "vortex"}), "Operations"),
    (frozenset({"archive", "backup", "history", "log", "audit", "manifest", "inventory", "harvest", "mapping"}), "Archive"),
]


def _tokenize(text: str) -> frozenset[str]:
    """Return lowercase word tokens from *text*."""
    return frozenset(re.findall(r"[a-z]+", text.lower()))


def _categorize(repo: dict[str, Any]) -> tuple[str, str]:
    """
    Return ``(framework_tag, district_id)`` for a repository.

    Parameters
    ----------
    repo:
        Raw GitHub API repository object.

    Returns
    -------
    tuple[str, str]
        ``framework_tag`` in ``{"Tia", "Oracle", "General"}`` and
        ``district_id`` in ``{"Intelligence", "Operations", "Archive", "Research"}``.
    """
    tokens = _tokenize(
        " ".join(
            filter(
                None,
                [repo.get("name", ""), repo.get("description", "") or "", repo.get("language", "") or ""],
            )
        )
    )

    tia_score = len(tokens & _TIA_SIGNALS)
    oracle_score = len(tokens & _ORACLE_SIGNALS)

    if tia_score >= oracle_score and tia_score > 0:
        framework_tag = "Tia"
    elif oracle_score > tia_score:
        framework_tag = "Oracle"
    else:
        framework_tag = "General"

    district_id = "Research"  # default
    for signal_set, district in _DISTRICT_RULES:
        if tokens & signal_set:
            district_id = district
            break

    return framework_tag, district_id


# ---------------------------------------------------------------------------
# Submodule registry (Task 2)
# ---------------------------------------------------------------------------


def _discover_submodules() -> set[str]:
    """
    Parse ``.gitmodules`` (if present) and return the set of full repo names
    (``owner/repo``) registered as submodules.

    Returns
    -------
    set[str]
        Full repository names found in ``.gitmodules``, lower-cased.
    """
    gitmodules = _REPO_ROOT / ".gitmodules"
    if not gitmodules.exists():
        return set()

    content = gitmodules.read_text(encoding="utf-8")
    # Extract ``url = https://github.com/owner/repo`` lines
    urls = re.findall(r"url\s*=\s*https://github\.com/([^/\s]+/[^\s]+)", content)
    return {u.lower().rstrip(".git") for u in urls}


# ---------------------------------------------------------------------------
# Manifest builder (Tasks 1–3)
# ---------------------------------------------------------------------------


def _build_entry(raw: dict[str, Any], submodule_names: set[str]) -> dict[str, Any]:
    """
    Convert a raw GitHub API repo object into a manifest entry.

    Parameters
    ----------
    raw:
        Full repository object from the API.
    submodule_names:
        Set of ``owner/repo`` names (lower-cased) currently registered as
        git submodules in this repository.

    Returns
    -------
    dict
        Manifest entry with cleaned metadata, link type, and classification.
    """
    full_name_lower = raw.get("full_name", "").lower()
    is_submodule = full_name_lower in submodule_names

    framework_tag, district_id = _categorize(raw)

    entry: dict[str, Any] = {
        "name": raw.get("name", ""),
        "full_name": raw.get("full_name", ""),
        "html_url": raw.get("html_url", ""),
        "description": _sanitize_description(raw.get("description")),
        "language": raw.get("language") or "",
        "updated_at": raw.get("updated_at", ""),
        "framework_tag": framework_tag,
        "district_id": district_id,
        "link_type": "submodule" if is_submodule else "shadow",
    }

    if not is_submodule:
        # Shadow Link: store raw content URL for on-demand metadata fetching
        entry["raw_content_url"] = f"https://api.github.com/repos/{raw.get('full_name', '')}"

    return entry


def harvest(token: str | None = None) -> dict[str, Any]:
    """
    Execute the full repository harvesting pipeline and write ``fleet_manifest.json``.

    Parameters
    ----------
    token:
        GitHub PAT.  When ``None``, read from ``GITHUB_TOKEN`` or ``GH_PAT``
        environment variables.

    Returns
    -------
    dict
        The assembled fleet manifest.

    Raises
    ------
    RuntimeError
        When no GitHub token is available.
    """
    if token is None:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT", "")

    if not token:
        logger.error(
            "[Harvester] No GitHub token found. "
            "Set GITHUB_TOKEN or GH_PAT in GitHub Secrets."
        )
        raise RuntimeError("Missing GitHub authentication token.")

    logger.info("[Harvester] Starting global repository harvest …")

    # ------------------------------------------------------------------ repos
    try:
        raw_repos = _fetch_all_repos(token)
    except Exception as exc:
        logger.error("[Harvester] Failed to fetch repositories: %s", exc)
        raise

    # ------------------------------------------------------------------ auth user
    try:
        user_info = _github_request("/user", token)
        owner_login = user_info.get("login", "")
    except Exception as exc:
        logger.warning("[Harvester] Could not resolve authenticated user: %s", exc)
        owner_login = ""

    # ------------------------------------------------------------------ submodules
    submodule_names = _discover_submodules()
    logger.info("[Harvester] Detected %d submodule(s).", len(submodule_names))

    # ------------------------------------------------------------------ entries
    entries: list[dict[str, Any]] = []
    for raw in raw_repos:
        try:
            entry = _build_entry(raw, submodule_names)
            entries.append(entry)
        except Exception as exc:
            logger.warning("[Harvester] Skipped repo '%s': %s", raw.get("full_name"), exc)

    # ------------------------------------------------------------------ district summary
    district_summary: dict[str, list[str]] = {}
    for entry in entries:
        district_id = entry["district_id"]
        district_summary.setdefault(district_id, []).append(entry["full_name"])

    manifest: dict[str, Any] = {
        "manifest_version": "3.0.0",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "owner": owner_login,
        "total_repositories": len(entries),
        "repositories": entries,
        "district_summary": {k: len(v) for k, v in district_summary.items()},
    }

    # ------------------------------------------------------------------ write
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with MANIFEST_PATH.open("w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    logger.info(
        "[Harvester] fleet_manifest.json written — %d repo(s) across %d district(s).",
        len(entries),
        len(district_summary),
    )
    return manifest


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        result = harvest()
        print(
            f"✅ Harvest complete — {result['total_repositories']} repo(s) written to fleet_manifest.json"
        )
    except RuntimeError as exc:
        print(f"❌ {exc}")
        sys.exit(1)
