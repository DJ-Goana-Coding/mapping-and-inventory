#!/usr/bin/env python3
"""Optional, operator-run cross-repo RAG corpus ingester.

Builds a *literal-text* corpus of the documentation/manifest "bibles"
across every sibling repository owned by ``DJ-Goana-Coding`` (or any
GitHub user/org passed via ``--owner``) and writes it as JSON-lines to
``fleet/fleet_corpus.jsonl``. Each line is a single record::

    {"repo": "<repo_name>", "path": "<repo-relative path>",
     "sha": "<git blob sha>", "content": "<utf-8 text>"}

Honesty contract (mirrors ``scripts/total_fleet_crawler.py``):

* **Opt-in only.** This script does *nothing* unless ``GH_TOKEN`` (or
  ``GITHUB_TOKEN``) is set. CI must not run it; it is an operator tool.
* **Read-only.** Uses the GitHub REST API to list repos and fetch a
  fixed allow-list of small text files per repo. It never clones, never
  writes back to any sibling repo.
* **No fabrication.** A record is only emitted when the API returns a
  file payload. Missing files are silently skipped — they are not
  invented as empty strings.
* **Bounded.** Per-file content is capped at ``MAX_CONTENT_BYTES``;
  oversized payloads are recorded with ``content`` truncated and
  ``truncated: true``. Non-text payloads (anything that is not valid
  UTF-8 / has NUL bytes) are skipped entirely so the JSONL stays
  ingestible by downstream RAG tooling.

The resulting ``fleet/fleet_corpus.jsonl`` is the literal text brain
that T.I.A. (or any other RAG runtime) can index. It is intentionally a
*separate* artifact from ``fleet/fleet_discovery.json`` (metadata) and
``rag_knowledge_base`` inside ``global_manifest.json`` (path index) —
the three layers do not overlap and may be regenerated independently.
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
from typing import Any, Iterable

DEFAULT_OWNER = "DJ-Goana-Coding"
DEFAULT_OUTPUT_REL = "fleet/fleet_corpus.jsonl"
GITHUB_API = "https://api.github.com"
USER_AGENT = "mapping-and-inventory-cross-repo-rag-ingest/1.0"

# Files whose literal text we want in the corpus. Anything not on this
# allow-list is ignored — keeps the artifact bounded and predictable.
TARGET_FILES: tuple[str, ...] = (
    "README.md",
    "ARCHITECTURE.md",
    "system_manifest.json",
    "manifest.json",
    "FOUNDATION_MANIFEST.md",
)

# Hard per-file cap. GitHub's contents API itself refuses files >1 MiB,
# but most RAG indexers prefer chunks well under this. Files larger than
# the cap are truncated and flagged.
MAX_CONTENT_BYTES = 256 * 1024  # 256 KiB

# Hard safety stop while paging through repo listings (5,000 repos).
MAX_REPO_PAGES = 50


class IngestError(RuntimeError):
    """Raised for unrecoverable ingestion failures."""


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
        raise IngestError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise IngestError(f"network error for {url}: {exc}") from exc
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise IngestError(f"invalid JSON from {url}: {exc}") from exc


def _decode_contents(payload: Any) -> tuple[bytes | None, str | None]:
    """Decode a GitHub ``contents`` API payload.

    Returns ``(bytes_or_none, sha_or_none)``. ``None`` for the bytes
    component means "not a regular file payload we can use".
    """
    if not isinstance(payload, dict):
        return None, None
    if payload.get("type") != "file":
        return None, None
    sha = payload.get("sha") if isinstance(payload.get("sha"), str) else None
    encoding = payload.get("encoding")
    content = payload.get("content")
    if encoding == "base64" and isinstance(content, str):
        try:
            return base64.b64decode(content), sha
        except (ValueError, TypeError):
            return None, sha
    if isinstance(content, str):
        return content.encode("utf-8", errors="replace"), sha
    return None, sha


# --------------------------------------------------------------------------- #
# Repo listing
# --------------------------------------------------------------------------- #
def list_owner_repos(owner: str, token: str, opener: Any = None) -> list[dict]:
    """Page through ``/users/{owner}/repos`` and return repo summaries.

    Uses the user endpoint (rather than ``/orgs/``) so it works whether
    ``owner`` is a personal account or an organisation — both expose
    public repositories through ``/users/{owner}/repos``.
    """
    repos: list[dict] = []
    page = 1
    while True:
        url = (
            f"{GITHUB_API}/users/{urllib.parse.quote(owner)}/repos"
            f"?per_page=100&page={page}&type=owner&sort=full_name"
        )
        batch = _http_get_json(url, token, opener=opener)
        if not isinstance(batch, list) or not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > MAX_REPO_PAGES:
            break
    return repos


# --------------------------------------------------------------------------- #
# Per-file ingestion
# --------------------------------------------------------------------------- #
def _looks_binary(data: bytes) -> bool:
    """Heuristic: treat anything containing a NUL byte as binary."""
    return b"\x00" in data


def _to_text(data: bytes) -> str | None:
    """Decode ``data`` as UTF-8 (replacement on errors). ``None`` if binary."""
    if _looks_binary(data):
        return None
    return data.decode("utf-8", errors="replace")


def fetch_file(
    owner: str, repo: str, path: str, token: str, opener: Any = None
) -> tuple[bytes | None, str | None]:
    """Fetch a single file's contents via the contents API.

    Returns ``(bytes_or_none, sha_or_none)``. Missing → ``(None, None)``.
    """
    url = (
        f"{GITHUB_API}/repos/{urllib.parse.quote(owner)}/"
        f"{urllib.parse.quote(repo)}/contents/{urllib.parse.quote(path)}"
    )
    payload = _http_get_json(url, token, opener=opener)
    if payload is None:
        return None, None
    return _decode_contents(payload)


def ingest_repo(
    owner: str,
    repo_meta: dict,
    token: str,
    target_files: Iterable[str] = TARGET_FILES,
    max_bytes: int = MAX_CONTENT_BYTES,
    opener: Any = None,
) -> list[dict]:
    """Return one corpus record per target file actually present in ``repo``.

    Each record has the shape ``{repo, path, sha, content}`` and may
    additionally carry ``truncated: true`` if the file exceeded
    ``max_bytes``. Binary or undecodable payloads are dropped without a
    record (we never write garbage into the corpus).
    """
    name = repo_meta.get("name") or ""
    if not name:
        return []
    records: list[dict] = []
    for path in target_files:
        data, sha = fetch_file(owner, name, path, token, opener=opener)
        if data is None:
            continue
        truncated = False
        if len(data) > max_bytes:
            data = data[:max_bytes]
            truncated = True
        text = _to_text(data)
        if text is None:
            # Binary — skip rather than corrupt the JSONL stream.
            continue
        record: dict = {
            "repo": name,
            "path": path,
            "sha": sha or "",
            "content": text,
        }
        if truncated:
            record["truncated"] = True
        records.append(record)
    return records


# --------------------------------------------------------------------------- #
# Corpus assembly
# --------------------------------------------------------------------------- #
def build_corpus(
    owner: str,
    token: str,
    target_files: Iterable[str] = TARGET_FILES,
    max_bytes: int = MAX_CONTENT_BYTES,
    opener: Any = None,
) -> tuple[list[dict], list[str]]:
    """Crawl every owner repo and return ``(records, repo_names)``.

    ``records`` are sorted by ``(repo, path)`` for deterministic output.
    ``repo_names`` lists every repo that was visited, even if it
    contributed zero records (useful for the run summary).
    """
    repos = list_owner_repos(owner, token, opener=opener)
    repo_names = sorted(r.get("name", "") for r in repos if r.get("name"))
    all_records: list[dict] = []
    for repo_meta in repos:
        all_records.extend(
            ingest_repo(
                owner,
                repo_meta,
                token,
                target_files=target_files,
                max_bytes=max_bytes,
                opener=opener,
            )
        )
    all_records.sort(key=lambda r: (r["repo"], r["path"]))
    return all_records, repo_names


def write_corpus(records: Iterable[dict], output: Path) -> int:
    """Write ``records`` as JSON-lines to ``output``. Returns count written."""
    output.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with output.open("w", encoding="utf-8") as fh:
        for record in records:
            fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True))
            fh.write("\n")
            n += 1
    return n


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--owner",
        default=DEFAULT_OWNER,
        help=f"GitHub user/org to ingest (default: {DEFAULT_OWNER})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=f"Path to write JSONL corpus (default: <repo>/{DEFAULT_OUTPUT_REL})",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root, used to resolve --output default.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int,
        default=MAX_CONTENT_BYTES,
        help="Per-file content cap in bytes (default: %(default)s).",
    )
    args = parser.parse_args(argv)

    token = _resolve_token()
    if not token:
        print(
            "cross_repo_rag_ingest: GH_TOKEN (or GITHUB_TOKEN) not set; "
            "nothing to do.\n"
            "  This tool is opt-in. Set a token and re-run to populate "
            f"{DEFAULT_OUTPUT_REL}.",
            file=sys.stderr,
        )
        return 0

    if args.max_bytes <= 0:
        print(
            "cross_repo_rag_ingest: --max-bytes must be positive.",
            file=sys.stderr,
        )
        return 2

    output: Path = args.output or (args.root.resolve() / DEFAULT_OUTPUT_REL)
    try:
        records, repo_names = build_corpus(
            args.owner, token, max_bytes=args.max_bytes
        )
    except IngestError as exc:
        print(f"cross_repo_rag_ingest: {exc}", file=sys.stderr)
        return 1

    written = write_corpus(records, output)
    summary = {
        "generated_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "owner": args.owner,
        "repos_visited": len(repo_names),
        "records_written": written,
        "output": str(output),
    }
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
