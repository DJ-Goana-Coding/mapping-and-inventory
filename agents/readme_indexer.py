"""
README Indexer — Knowledge Extraction Agent
============================================
Implements Task 5 from the mapping-and-inventory integration spec.

Iterates through the ``fleet_manifest.json`` repository list, fetches each
repository's ``README.md`` (or falls back to a directory tree listing) via the
GitHub API, and stores a sanitized summary in::

    District_05_OPEN_SOURCE_BIN/readme_index/<owner>__<repo>.md

A single ``_index.json`` catalogue is also maintained in that directory to
facilitate cross-repository searching and inventory management.

Security
--------
The GitHub Personal Access Token is read exclusively from the ``GITHUB_TOKEN``
environment variable (or ``GH_PAT`` as a fallback).

Audit Logging
-------------
All fetch attempts and errors are appended to ``sync_audit.log`` at the repo
root (the same file used by :mod:`agents.repo_harvester`).

Usage::

    python -m agents.readme_indexer
    # or
    from agents.readme_indexer import index_readmes
    summary = index_readmes()
"""
from __future__ import annotations

import base64
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
# Logging
# ---------------------------------------------------------------------------

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------

_GITHUB_API_BASE = "https://api.github.com"
_MAX_README_BYTES = 64 * 1024   # cap at 64 KB per README


def _github_get(path: str, token: str) -> Any:
    """
    Perform a single authenticated GitHub API GET request.

    Returns the decoded JSON body, or raises on HTTP error.
    """
    url = _GITHUB_API_BASE + path
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mapping-and-inventory/readme-indexer",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_readme(full_name: str, token: str) -> str | None:
    """
    Fetch and decode the default-branch README for *full_name*.

    Content is capped at ``_MAX_README_BYTES`` (64 KB) to avoid storing
    extremely large README files; content beyond that limit is silently
    truncated.

    Returns the raw README text or ``None`` when no README is available or
    an error occurs.
    """
    try:
        data = _github_get(f"/repos/{full_name}/readme", token)
        encoded = data.get("content", "")
        raw_bytes = base64.b64decode(encoded)[:_MAX_README_BYTES]
        return raw_bytes.decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            logger.debug("[Indexer] No README for %s (404).", full_name)
        else:
            logger.warning("[Indexer] HTTP %d fetching README for %s.", exc.code, full_name)
        return None
    except Exception as exc:
        logger.warning("[Indexer] Could not fetch README for %s: %s", full_name, exc)
        return None


def _fetch_tree(full_name: str, token: str) -> str | None:
    """
    Fetch the root directory tree for *full_name* and return a markdown listing.

    Falls back to ``None`` on any error.
    """
    try:
        data = _github_get(f"/repos/{full_name}/git/trees/HEAD?recursive=0", token)
        items = data.get("tree", [])
        lines = [f"- `{item['path']}`" for item in items[:50]]
        header = f"## Directory Tree — {full_name}\n\n"
        return header + "\n".join(lines)
    except Exception as exc:
        logger.warning("[Indexer] Could not fetch tree for %s: %s", full_name, exc)
        return None


def _sanitize_content(text: str) -> str:
    """
    Apply sensitive-data scrubbing to README/tree content before storing.

    Leverages :func:`utils.path_sanitizer.sanitize` when available and
    additionally strips obvious credential patterns.
    """
    try:
        from utils.path_sanitizer import sanitize
        text = sanitize(text)
    except ImportError:
        pass

    # Strip obvious credential-shaped tokens from README content
    for pattern in (
        re.compile(r"(?i)(api[_\s-]?key|token|secret|password)\s*[:=]\s*\S+"),
        re.compile(r"ghp_[A-Za-z0-9]{36,}"),
        re.compile(r"sk-[A-Za-z0-9]{32,}"),
    ):
        text = pattern.sub("<REDACTED>", text)

    return text


# ---------------------------------------------------------------------------
# Main indexing routine
# ---------------------------------------------------------------------------


def index_readmes(token: str | None = None) -> dict[str, Any]:
    """
    Fetch README files for every repository in ``fleet_manifest.json`` and
    store sanitized summaries in ``District_05_OPEN_SOURCE_BIN/readme_index/``.

    Parameters
    ----------
    token:
        GitHub PAT.  Reads from ``GITHUB_TOKEN`` / ``GH_PAT`` env vars when
        ``None``.

    Returns
    -------
    dict
        Summary with ``indexed``, ``failed``, ``skipped``, and ``generated_utc``
        keys.

    Raises
    ------
    RuntimeError
        When no GitHub token is available.
    FileNotFoundError
        When ``fleet_manifest.json`` has not yet been generated.
    """
    if token is None:
        token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_PAT", "")

    if not token:
        logger.error(
            "[Indexer] No GitHub token found. "
            "Set GITHUB_TOKEN or GH_PAT in GitHub Secrets."
        )
        raise RuntimeError("Missing GitHub authentication token.")

    if not MANIFEST_PATH.exists():
        raise FileNotFoundError(
            f"fleet_manifest.json not found at {MANIFEST_PATH}. "
            "Run agents.repo_harvester first."
        )

    with MANIFEST_PATH.open(encoding="utf-8") as fh:
        manifest = json.load(fh)

    repositories: list[dict[str, Any]] = manifest.get("repositories", [])
    logger.info("[Indexer] Starting README indexing for %d repo(s) …", len(repositories))

    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    catalogue: list[dict[str, str]] = []
    indexed = 0
    failed = 0
    skipped = 0

    for repo in repositories:
        full_name: str = repo.get("full_name", "")
        if not full_name:
            skipped += 1
            continue

        safe_name = full_name.replace("/", "__")
        out_path = INDEX_DIR / f"{safe_name}.md"

        logger.info("[Indexer] Processing %s …", full_name)

        content = _fetch_readme(full_name, token)
        if content is None:
            content = _fetch_tree(full_name, token)

        if content is None:
            logger.warning("[Indexer] No content available for %s — skipping.", full_name)
            failed += 1
            catalogue.append(
                {
                    "full_name": full_name,
                    "file": str(out_path.relative_to(_REPO_ROOT)),
                    "status": "failed",
                }
            )
            time.sleep(0.3)
            continue

        sanitized = _sanitize_content(content)

        header = (
            f"# {full_name}\n\n"
            f"**URL:** {repo.get('html_url', '')}\n"
            f"**Language:** {repo.get('language', '')}\n"
            f"**Framework:** {repo.get('framework_tag', '')}\n"
            f"**District:** {repo.get('district_id', '')}\n"
            f"**Last Updated:** {repo.get('updated_at', '')}\n\n"
            f"---\n\n"
        )

        out_path.write_text(header + sanitized, encoding="utf-8")
        indexed += 1
        catalogue.append(
            {
                "full_name": full_name,
                "file": str(out_path.relative_to(_REPO_ROOT)),
                "status": "ok",
                "framework_tag": repo.get("framework_tag", ""),
                "district_id": repo.get("district_id", ""),
            }
        )
        logger.info("[Indexer] ✅ Saved %s.", out_path.name)
        time.sleep(0.3)   # rate-limit courtesy

    # Write index catalogue
    index_catalogue_path = INDEX_DIR / "_index.json"
    catalogue_doc: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "total": len(repositories),
        "indexed": indexed,
        "failed": failed,
        "skipped": skipped,
        "entries": catalogue,
    }
    with index_catalogue_path.open("w", encoding="utf-8") as fh:
        json.dump(catalogue_doc, fh, indent=2)

    logger.info(
        "[Indexer] README indexing complete — %d indexed, %d failed, %d skipped.",
        indexed,
        failed,
        skipped,
    )

    return {
        "indexed": indexed,
        "failed": failed,
        "skipped": skipped,
        "generated_utc": catalogue_doc["generated_utc"],
    }


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(AUDIT_LOG_PATH, encoding="utf-8"),
        ],
    )
    try:
        summary = index_readmes()
        print(
            f"✅ README indexing complete — "
            f"{summary['indexed']} indexed, "
            f"{summary['failed']} failed, "
            f"{summary['skipped']} skipped."
        )
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"❌ {exc}")
        sys.exit(1)
