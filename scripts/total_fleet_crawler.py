#!/usr/bin/env python3
"""Optional, operator-run fleet crawler.

Discovers sibling repositories under a GitHub organization (default:
``DJ-Goana-Coding``) and writes a *separate* artifact at
``fleet/fleet_discovery.json`` that ``scripts/build_global_manifest.py``
will merge into ``global_manifest.json → fleet_map`` if it exists.

Honesty contract:

* **Opt-in only.** This script does *nothing* unless ``GH_TOKEN`` (or
  ``GITHUB_TOKEN``) is set. CI must not run it; it is an operator tool.
* **Read-only.** Uses the GitHub REST API to list repos and fetch a few
  small files per repo: ``README.md``, root ``manifest.json``,
  ``system_manifest.json``, and ``inventory/file_index.json``. It never
  clones, never writes back.
* **No fabrication.** ``hf_space_url`` is populated *only* when a sibling
  self-declares it (in its own ``manifest.json``, or via the GitHub
  ``homepage`` / ``topics`` fields). Otherwise the field is omitted.
* **Schema-aligned.** Each entry has the same shape as
  ``fleet/fleet_registry.json`` plus enrichment fields
  (``has_system_manifest``, ``has_file_index``, ``manifest_sha``,
  ``module_count``). The build script never overrides registry entries
  with discovery entries; the registry remains authoritative.
"""

from __future__ import annotations

import argparse
import base64
import datetime as _dt
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_ORG = "DJ-Goana-Coding"
DEFAULT_OUTPUT_REL = "fleet/fleet_discovery.json"
GITHUB_API = "https://api.github.com"
USER_AGENT = "mapping-and-inventory-fleet-crawler/1.0"

# Files we look at per sibling. Anything else is ignored.
TARGET_FILES = (
    "README.md",
    "manifest.json",
    "system_manifest.json",
    "inventory/file_index.json",
)

# Module-counting extensions when reading a sibling's file_index.json.
MODULE_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx", ".cs", ".go", ".rs", ".java"}


class CrawlerError(RuntimeError):
    """Raised for unrecoverable crawler failures."""


# --------------------------------------------------------------------------- #
# Token / HTTP plumbing
# --------------------------------------------------------------------------- #
def _resolve_token() -> str | None:
    return os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def _http_get_json(url: str, token: str, opener: Any = None) -> Any:
    """GET ``url`` and return parsed JSON. Returns ``None`` on 404."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    req.add_header("User-Agent", USER_AGENT)
    open_fn = opener.open if opener is not None else urllib.request.urlopen
    try:
        with open_fn(req, timeout=30) as resp:
            body = resp.read()
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise CrawlerError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise CrawlerError(f"network error for {url}: {exc}") from exc
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CrawlerError(f"invalid JSON from {url}: {exc}") from exc


def _decode_contents(payload: Any) -> bytes | None:
    """Decode a GitHub ``contents`` API payload into raw bytes."""
    if not isinstance(payload, dict):
        return None
    if payload.get("type") != "file":
        return None
    encoding = payload.get("encoding")
    content = payload.get("content")
    if encoding == "base64" and isinstance(content, str):
        try:
            return base64.b64decode(content)
        except (ValueError, TypeError):
            return None
    if isinstance(content, str):
        return content.encode("utf-8", errors="replace")
    return None


# --------------------------------------------------------------------------- #
# Crawl
# --------------------------------------------------------------------------- #
def list_org_repos(org: str, token: str, opener: Any = None) -> list[dict]:
    """Page through ``/orgs/{org}/repos`` and return repo summaries."""
    repos: list[dict] = []
    page = 1
    while True:
        url = f"{GITHUB_API}/orgs/{urllib.parse.quote(org)}/repos?per_page=100&page={page}&type=all"
        batch = _http_get_json(url, token, opener=opener)
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 50:  # hard safety stop: 5,000 repos
            break
    return repos


def fetch_file(
    org: str, repo: str, path: str, token: str, opener: Any = None
) -> tuple[bytes | None, str | None]:
    """Fetch a single file's contents via the contents API.

    Returns ``(bytes_or_none, sha_or_none)``. Missing → ``(None, None)``.
    """
    url = f"{GITHUB_API}/repos/{urllib.parse.quote(org)}/{urllib.parse.quote(repo)}/contents/{urllib.parse.quote(path)}"
    payload = _http_get_json(url, token, opener=opener)
    if payload is None:
        return None, None
    sha = payload.get("sha") if isinstance(payload, dict) else None
    return _decode_contents(payload), (sha if isinstance(sha, str) else None)


def _extract_hf_space_url(self_manifest: dict | None, repo_meta: dict) -> str | None:
    """Return an HF Space URL only if the sibling self-declares one.

    Sources, in priority order:
      1. ``manifest.json`` field ``hf_space_url`` (string).
      2. GitHub ``homepage`` if it points at huggingface.co.
      3. ``topics`` containing a ``hf-space:<owner>/<name>`` marker.
    Anything else → ``None``. We never construct an URL.
    """
    if isinstance(self_manifest, dict):
        url = self_manifest.get("hf_space_url")
        if isinstance(url, str) and url.startswith("https://huggingface.co/"):
            return url
    homepage = repo_meta.get("homepage")
    if isinstance(homepage, str) and homepage.startswith("https://huggingface.co/"):
        return homepage
    topics = repo_meta.get("topics")
    if isinstance(topics, list):
        for t in topics:
            if isinstance(t, str) and t.startswith("hf-space:"):
                slug = t.split(":", 1)[1].strip()
                if slug:
                    return f"https://huggingface.co/spaces/{slug}"
    return None


def _count_modules(file_index_bytes: bytes | None) -> int | None:
    """Count source modules in a sibling's file_index.json."""
    if file_index_bytes is None:
        return None
    try:
        data = json.loads(file_index_bytes.decode("utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict):
        return None
    files = data.get("files")
    if not isinstance(files, list):
        return None
    n = 0
    for entry in files:
        if not isinstance(entry, dict):
            continue
        ext = entry.get("extension")
        if isinstance(ext, str) and ext.lower() in MODULE_EXTENSIONS:
            n += 1
    return n


def _enrich_repo(
    org: str, repo_meta: dict, token: str, opener: Any = None
) -> dict:
    name = repo_meta.get("name") or ""
    entry: dict = {
        "repo_name": name,
        "github_url": repo_meta.get("html_url") or f"https://github.com/{org}/{name}",
        "status": "archived" if repo_meta.get("archived") else "active",
    }
    description = repo_meta.get("description")
    if isinstance(description, str) and description:
        entry["description"] = description

    self_manifest_dict: dict | None = None

    # README presence (we don't ship its bytes anywhere — privacy + size).
    readme_bytes, _ = fetch_file(org, name, "README.md", token, opener=opener)
    entry["has_readme"] = readme_bytes is not None

    # manifest.json — used for self-declared HF Space URL and role.
    manifest_bytes, manifest_sha = fetch_file(org, name, "manifest.json", token, opener=opener)
    entry["has_manifest"] = manifest_bytes is not None
    if manifest_sha:
        entry["manifest_sha"] = manifest_sha
    if manifest_bytes is not None:
        try:
            self_manifest_dict = json.loads(manifest_bytes.decode("utf-8", errors="replace"))
            if isinstance(self_manifest_dict, dict):
                role = self_manifest_dict.get("role")
                if isinstance(role, str) and role:
                    entry["role"] = role
        except json.JSONDecodeError:
            self_manifest_dict = None

    # system_manifest.json presence.
    sys_bytes, sys_sha = fetch_file(org, name, "system_manifest.json", token, opener=opener)
    entry["has_system_manifest"] = sys_bytes is not None
    if sys_sha:
        entry["system_manifest_sha"] = sys_sha

    # inventory/file_index.json — the only file we actually parse for stats.
    fi_bytes, fi_sha = fetch_file(org, name, "inventory/file_index.json", token, opener=opener)
    entry["has_file_index"] = fi_bytes is not None
    if fi_sha:
        entry["file_index_sha"] = fi_sha
    mc = _count_modules(fi_bytes)
    if mc is not None:
        entry["module_count"] = mc

    hf = _extract_hf_space_url(self_manifest_dict, repo_meta)
    if hf:
        entry["hf_space_url"] = hf

    return entry


def crawl(org: str, token: str, opener: Any = None) -> dict:
    repos = list_org_repos(org, token, opener=opener)
    entries = [_enrich_repo(org, r, token, opener=opener) for r in repos if r.get("name")]
    entries.sort(key=lambda e: e["repo_name"])
    return {
        "schema_version": "1.0.0",
        "generated_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "generator": "scripts/total_fleet_crawler.py",
        "org": org,
        "entry_count": len(entries),
        "entries": entries,
    }


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--org", default=DEFAULT_ORG, help=f"GitHub org to crawl (default: {DEFAULT_ORG})"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=f"Path to write discovery JSON (default: <repo>/{DEFAULT_OUTPUT_REL})",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root, used to resolve --output default.",
    )
    args = parser.parse_args(argv)

    token = _resolve_token()
    if not token:
        print(
            "total_fleet_crawler: GH_TOKEN (or GITHUB_TOKEN) not set; nothing to do.\n"
            "  This tool is opt-in. Set a token and re-run to populate "
            f"{DEFAULT_OUTPUT_REL}.",
            file=sys.stderr,
        )
        return 0

    output: Path = args.output or (args.root.resolve() / DEFAULT_OUTPUT_REL)
    try:
        data = crawl(args.org, token)
    except CrawlerError as exc:
        print(f"total_fleet_crawler: {exc}", file=sys.stderr)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    output.write_text(text, encoding="utf-8")
    print(f"Wrote {output} ({data['entry_count']} repos)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
