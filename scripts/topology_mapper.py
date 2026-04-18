#!/usr/bin/env python3
"""Optional, operator-run synaptic topology mapper.

Maps *existing* infrastructure across every sibling repository owned by
the configured GitHub user/org (default ``DJ-Goana-Coding``) and writes
two artifacts:

* ``fleet/fleet_topology.json`` — machine-readable graph of nodes
  (repos), per-node infrastructure artifacts grouped into three classes
  (bridges/tunnels, existing RAGs, automated workers), inferred
  cross-repo edges, and a list of orphan nodes.
* ``fleet/fleet_topology.md`` — short operator-readable companion that
  surfaces the orphan list so T.I.A. (and humans) can see at a glance
  which repos are isolated and waiting for a bridge.

Honesty contract (mirrors ``scripts/total_fleet_crawler.py`` and
``scripts/cross_repo_rag_ingest.py``):

* **Opt-in only.** Refuses to run unless ``GH_TOKEN`` (or
  ``GITHUB_TOKEN``) is set. CI must not run it; it is an operator tool.
* **Read-only.** Uses the GitHub REST API — one ``git/trees`` call per
  repo to enumerate paths, plus per-workflow content reads bounded by
  ``MAX_WORKFLOW_BYTES`` and ``MAX_WORKFLOWS_PER_REPO``. Never clones,
  never writes back to any sibling.
* **No fabrication.** A node, artifact, edge, or orphan flag is only
  emitted when supported by direct API evidence (a path the tree API
  returned, or a literal substring inside a workflow file we actually
  fetched). We never invent connections "to look complete".
* **Deterministic.** Nodes, artifacts, edges, and orphans are sorted;
  re-running on the same data yields byte-identical output.

This artifact is **not** consumed by ``build_global_manifest.py``; it
is a sibling map that downstream tools may read alongside
``fleet_registry.json`` / ``fleet_discovery.json`` / ``fleet_corpus.jsonl``.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from base64 import b64decode
from pathlib import Path
from typing import Any, Iterable

DEFAULT_OWNER = "DJ-Goana-Coding"
DEFAULT_OUTPUT_REL = "fleet/fleet_topology.json"
DEFAULT_REPORT_REL = "fleet/fleet_topology.md"
GITHUB_API = "https://api.github.com"
USER_AGENT = "mapping-and-inventory-topology-mapper/1.0"

# Hard safety stops.
MAX_REPO_PAGES = 50           # 5,000 repos
MAX_WORKFLOW_BYTES = 64 * 1024
MAX_WORKFLOWS_PER_REPO = 25


# --------------------------------------------------------------------------- #
# Artifact classifier
# --------------------------------------------------------------------------- #
#
# Each rule is ``(predicate, kind, category)``. ``predicate`` runs on the
# repo-relative POSIX path; the first rule that matches wins. Categories
# are the three buckets the topology graph is built around. Anything
# that doesn't match any rule is ignored — the topology only records
# *infrastructure* paths, not every file in the tree.

CAT_BRIDGE = "bridge"
CAT_RAG = "rag"
CAT_WORKER = "worker"


def _glob(*patterns: str):
    lowered = tuple(p.lower() for p in patterns)
    return lambda rel: any(
        fnmatch.fnmatchcase(rel.lower(), pat) for pat in lowered
    )


def _basename_glob(*patterns: str):
    lowered = tuple(p.lower() for p in patterns)
    return lambda rel: any(
        fnmatch.fnmatchcase(os.path.basename(rel).lower(), pat)
        for pat in lowered
    )


def _path_contains(*needles: str):
    lowered = tuple(n.lower() for n in needles)
    return lambda rel: any(n in rel.lower() for n in lowered)


# Order matters: workflow files MUST be classified as workers even
# though their YAML often contains bridge/RAG keywords.
ARTIFACT_RULES: tuple[tuple[Any, str, str], ...] = (
    # --- Workers ----------------------------------------------------------
    (_glob(".github/workflows/*.yml", ".github/workflows/*.yaml"),
     "github_workflow", CAT_WORKER),
    (_basename_glob("crontab", "crontab.*", "*.cron"),
     "cron_schedule", CAT_WORKER),
    (_basename_glob("*daemon*.py", "*daemon*.sh"),
     "daemon_script", CAT_WORKER),
    (_basename_glob("*worker*.py", "*worker*.sh"),
     "worker_script", CAT_WORKER),

    # --- Bridges / tunnels ------------------------------------------------
    (_basename_glob("rclone.conf", "rclone*.conf", "*rclone*.json"),
     "rclone_config", CAT_BRIDGE),
    (_path_contains("citadel-bot", "citadel_bot"),
     "citadel_bot_link", CAT_BRIDGE),
    (_basename_glob("*webhook*.json", "*webhook*.yml", "*webhook*.yaml"),
     "webhook_config", CAT_BRIDGE),
    (_basename_glob("*tunnel*.json", "*tunnel*.yml", "*tunnel*.yaml", "*tunnel*.conf"),
     "tunnel_config", CAT_BRIDGE),
    (_glob("bridge/*", "bridges/*"),
     "bridge_module", CAT_BRIDGE),

    # --- Existing RAGs ----------------------------------------------------
    (_glob("**/faiss_index/*", "faiss_index/*"),
     "faiss_index", CAT_RAG),
    (_basename_glob("*.faiss"),
     "faiss_artifact", CAT_RAG),
    (_glob("**/vector_store/*", "vector_store/*", "**/vectorstore/*", "vectorstore/*"),
     "vector_store", CAT_RAG),
    (_glob("**/chroma/*", "chroma/*", "**/chroma_db/*", "chroma_db/*"),
     "chroma_store", CAT_RAG),
    (_glob("**/embeddings/*", "embeddings/*"),
     "embeddings_store", CAT_RAG),
    (_basename_glob("rag_*.json", "*_rag.json"),
     "rag_manifest", CAT_RAG),
    (_basename_glob("system_manifest.json", "manifest.json", "global_manifest.json"),
     "system_manifest", CAT_RAG),
)


def classify_path(rel_path: str) -> tuple[str, str] | None:
    """Return ``(kind, category)`` for an infrastructure path, or ``None``."""
    for predicate, kind, category in ARTIFACT_RULES:
        if predicate(rel_path):
            return kind, category
    return None


# --------------------------------------------------------------------------- #
# Token / HTTP plumbing
# --------------------------------------------------------------------------- #
class TopologyError(RuntimeError):
    """Raised for unrecoverable mapping failures."""


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
        raise TopologyError(f"HTTP {exc.code} from {url}: {exc.reason}") from exc
    except urllib.error.URLError as exc:
        raise TopologyError(f"network error for {url}: {exc}") from exc
    if not body:
        return None
    try:
        return json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise TopologyError(f"invalid JSON from {url}: {exc}") from exc


# --------------------------------------------------------------------------- #
# Repo + tree enumeration
# --------------------------------------------------------------------------- #
def list_owner_repos(owner: str, token: str, opener: Any = None) -> list[dict]:
    """Page through ``/users/{owner}/repos``."""
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


def fetch_tree(
    owner: str, repo: str, branch: str, token: str, opener: Any = None
) -> tuple[list[str], bool]:
    """Return ``(blob_paths, truncated_flag)`` for the repo's default branch."""
    url = (
        f"{GITHUB_API}/repos/{urllib.parse.quote(owner)}/"
        f"{urllib.parse.quote(repo)}/git/trees/"
        f"{urllib.parse.quote(branch)}?recursive=1"
    )
    payload = _http_get_json(url, token, opener=opener)
    if not isinstance(payload, dict):
        return [], False
    truncated = bool(payload.get("truncated"))
    tree = payload.get("tree")
    if not isinstance(tree, list):
        return [], truncated
    paths: list[str] = []
    for entry in tree:
        if not isinstance(entry, dict):
            continue
        if entry.get("type") != "blob":
            continue
        path = entry.get("path")
        if isinstance(path, str) and path:
            paths.append(path)
    return paths, truncated


def fetch_workflow_text(
    owner: str,
    repo: str,
    path: str,
    token: str,
    opener: Any = None,
    max_bytes: int = MAX_WORKFLOW_BYTES,
) -> str | None:
    """Fetch a workflow file and return its text (truncated to ``max_bytes``)."""
    url = (
        f"{GITHUB_API}/repos/{urllib.parse.quote(owner)}/"
        f"{urllib.parse.quote(repo)}/contents/{urllib.parse.quote(path)}"
    )
    payload = _http_get_json(url, token, opener=opener)
    if not isinstance(payload, dict) or payload.get("type") != "file":
        return None
    encoding = payload.get("encoding")
    content = payload.get("content")
    if encoding == "base64" and isinstance(content, str):
        try:
            data = b64decode(content)
        except (ValueError, TypeError):
            return None
    elif isinstance(content, str):
        data = content.encode("utf-8", errors="replace")
    else:
        return None
    if len(data) > max_bytes:
        data = data[:max_bytes]
    if b"\x00" in data:
        return None  # binary — won't yield meaningful edges
    return data.decode("utf-8", errors="replace")


# --------------------------------------------------------------------------- #
# Per-repo classification + edge extraction
# --------------------------------------------------------------------------- #
def classify_paths(paths: Iterable[str]) -> dict[str, list[dict]]:
    """Bucket ``paths`` into the three artifact categories (sorted)."""
    buckets: dict[str, list[dict]] = {
        CAT_BRIDGE: [],
        CAT_RAG: [],
        CAT_WORKER: [],
    }
    for p in paths:
        result = classify_path(p)
        if result is None:
            continue
        kind, category = result
        buckets[category].append({"path": p, "kind": kind})
    for cat in buckets:
        buckets[cat].sort(key=lambda e: (e["path"], e["kind"]))
    return buckets


def _extract_repo_references(
    text: str, owner: str, candidates: set[str], self_name: str
) -> set[str]:
    """Return the subset of ``candidates`` referenced by ``text``.

    A reference is either an explicit ``owner/repo`` substring (case
    insensitive) or a standalone repo-name token (``\\b<name>\\b``,
    case sensitive — these names are typically PascalCase or
    hyphenated and unlikely to collide with normal English words).
    """
    refs: set[str] = set()
    lowered = text.lower()
    owner_prefix = f"{owner.lower()}/"
    for cand in candidates:
        if cand == self_name:
            continue
        if owner_prefix + cand.lower() in lowered:
            refs.add(cand)
            continue
        # Standalone token match (avoid substring false positives).
        if re.search(rf"\b{re.escape(cand)}\b", text):
            refs.add(cand)
    return refs


def extract_workflow_edges(
    owner: str,
    repo_name: str,
    workflow_paths: list[str],
    sibling_names: set[str],
    token: str,
    opener: Any = None,
    max_workflows: int = MAX_WORKFLOWS_PER_REPO,
    max_bytes: int = MAX_WORKFLOW_BYTES,
) -> list[dict]:
    """For each workflow, return edges referencing other sibling repos."""
    edges: list[dict] = []
    seen: set[tuple[str, str, str]] = set()
    # Cap how many workflow files we read per repo.
    for path in sorted(workflow_paths)[:max_workflows]:
        text = fetch_workflow_text(
            owner, repo_name, path, token, opener=opener, max_bytes=max_bytes
        )
        if not text:
            continue
        refs = _extract_repo_references(text, owner, sibling_names, repo_name)
        for target in refs:
            key = (repo_name, target, path)
            if key in seen:
                continue
            seen.add(key)
            edges.append({
                "from": repo_name,
                "to": target,
                "via": "github_workflow",
                "evidence": path,
            })
    return edges


# --------------------------------------------------------------------------- #
# Topology assembly
# --------------------------------------------------------------------------- #
def build_topology(
    owner: str,
    token: str,
    opener: Any = None,
    max_workflows: int = MAX_WORKFLOWS_PER_REPO,
    max_bytes: int = MAX_WORKFLOW_BYTES,
) -> dict:
    """Crawl every owner repo and assemble the topology document."""
    repos = list_owner_repos(owner, token, opener=opener)
    sibling_names = {r.get("name") for r in repos if r.get("name")}
    sibling_names.discard(None)
    sibling_names_str: set[str] = {n for n in sibling_names if isinstance(n, str)}

    nodes: list[dict] = []
    all_edges: list[dict] = []
    for repo_meta in repos:
        name = repo_meta.get("name")
        if not isinstance(name, str) or not name:
            continue
        if repo_meta.get("archived"):
            status = "archived"
        else:
            status = "active"
        default_branch = repo_meta.get("default_branch") or "main"

        try:
            paths, truncated = fetch_tree(
                owner, name, default_branch, token, opener=opener
            )
        except TopologyError:
            paths, truncated = [], False

        artifacts = classify_paths(paths)
        workflow_paths = [
            a["path"] for a in artifacts[CAT_WORKER]
            if a["kind"] == "github_workflow"
        ]
        edges = extract_workflow_edges(
            owner,
            name,
            workflow_paths,
            sibling_names_str,
            token,
            opener=opener,
            max_workflows=max_workflows,
            max_bytes=max_bytes,
        )
        all_edges.extend(edges)

        artifact_total = sum(len(v) for v in artifacts.values())
        node = {
            "repo": name,
            "github_url": repo_meta.get("html_url")
            or f"https://github.com/{owner}/{name}",
            "default_branch": default_branch,
            "status": status,
            "tree_truncated": truncated,
            "artifacts": {
                "bridges": artifacts[CAT_BRIDGE],
                "rags": artifacts[CAT_RAG],
                "workers": artifacts[CAT_WORKER],
            },
            "artifact_count": artifact_total,
            "is_orphan": artifact_total == 0,
        }
        nodes.append(node)

    nodes.sort(key=lambda n: n["repo"])
    all_edges.sort(key=lambda e: (e["from"], e["to"], e["evidence"]))
    orphans = sorted(n["repo"] for n in nodes if n["is_orphan"])

    summary = {
        "repos_scanned": len(nodes),
        "bridge_artifacts": sum(len(n["artifacts"]["bridges"]) for n in nodes),
        "rag_artifacts": sum(len(n["artifacts"]["rags"]) for n in nodes),
        "worker_artifacts": sum(len(n["artifacts"]["workers"]) for n in nodes),
        "edge_count": len(all_edges),
        "orphan_count": len(orphans),
    }

    return {
        "schema_version": "1.0.0",
        "generated_at": _dt.datetime.now(tz=_dt.timezone.utc).isoformat(),
        "generator": "scripts/topology_mapper.py",
        "owner": owner,
        "summary": summary,
        "nodes": nodes,
        "edges": all_edges,
        "orphans": orphans,
    }


# --------------------------------------------------------------------------- #
# Markdown companion
# --------------------------------------------------------------------------- #
def render_markdown(topology: dict) -> str:
    """Produce a short operator-readable summary of the topology."""
    s = topology["summary"]
    lines: list[str] = [
        "# Fleet topology",
        "",
        f"- **Owner:** `{topology['owner']}`",
        f"- **Generated at:** {topology['generated_at']}",
        f"- **Repos scanned:** {s['repos_scanned']}",
        f"- **Bridges/tunnels:** {s['bridge_artifacts']}",
        f"- **Existing RAGs:** {s['rag_artifacts']}",
        f"- **Automated workers:** {s['worker_artifacts']}",
        f"- **Cross-repo workflow edges:** {s['edge_count']}",
        f"- **Orphan nodes:** {s['orphan_count']}",
        "",
        "## Orphan nodes",
        "",
    ]
    if topology["orphans"]:
        lines.append(
            "These repositories have no detected bridges, RAGs, or "
            "workers — they are isolated nodes waiting for a bridge."
        )
        lines.append("")
        for name in topology["orphans"]:
            lines.append(f"- `{name}`")
    else:
        lines.append("_No orphans detected — every scanned repo carries "
                     "at least one infrastructure artifact._")
    lines.append("")
    lines.append("## Cross-repo edges")
    lines.append("")
    if topology["edges"]:
        for e in topology["edges"]:
            lines.append(
                f"- `{e['from']}` → `{e['to']}` via {e['via']} "
                f"(`{e['evidence']}`)"
            )
    else:
        lines.append("_No cross-repo workflow references detected._")
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--owner", default=DEFAULT_OWNER,
        help=f"GitHub user/org to map (default: {DEFAULT_OWNER})",
    )
    parser.add_argument(
        "--output", type=Path, default=None,
        help=f"Path to JSON topology (default: <repo>/{DEFAULT_OUTPUT_REL})",
    )
    parser.add_argument(
        "--report", type=Path, default=None,
        help=f"Path to Markdown companion (default: <repo>/{DEFAULT_REPORT_REL})",
    )
    parser.add_argument(
        "--root", type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root, used to resolve --output / --report defaults.",
    )
    parser.add_argument(
        "--max-workflows", type=int, default=MAX_WORKFLOWS_PER_REPO,
        help="Max workflow files inspected per repo (default: %(default)s).",
    )
    parser.add_argument(
        "--max-workflow-bytes", type=int, default=MAX_WORKFLOW_BYTES,
        help="Per-workflow byte cap (default: %(default)s).",
    )
    args = parser.parse_args(argv)

    token = _resolve_token()
    if not token:
        print(
            "topology_mapper: GH_TOKEN (or GITHUB_TOKEN) not set; nothing to do.\n"
            "  This tool is opt-in. Set a token and re-run to populate "
            f"{DEFAULT_OUTPUT_REL}.",
            file=sys.stderr,
        )
        return 0

    if args.max_workflows <= 0 or args.max_workflow_bytes <= 0:
        print(
            "topology_mapper: --max-workflows and --max-workflow-bytes "
            "must be positive.",
            file=sys.stderr,
        )
        return 2

    output: Path = args.output or (args.root.resolve() / DEFAULT_OUTPUT_REL)
    report: Path = args.report or (args.root.resolve() / DEFAULT_REPORT_REL)

    try:
        topology = build_topology(
            args.owner,
            token,
            max_workflows=args.max_workflows,
            max_bytes=args.max_workflow_bytes,
        )
    except TopologyError as exc:
        print(f"topology_mapper: {exc}", file=sys.stderr)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(topology, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_markdown(topology), encoding="utf-8")
    print(json.dumps({
        "owner": topology["owner"],
        "summary": topology["summary"],
        "output": str(output),
        "report": str(report),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
