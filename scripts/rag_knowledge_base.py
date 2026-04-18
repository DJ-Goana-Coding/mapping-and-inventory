#!/usr/bin/env python3
"""Build the ``rag_knowledge_base`` section of ``global_manifest.json``.

This module performs a deterministic, read-only scan of the local
repository to produce a "Master Map" that downstream tools (e.g. T.I.A.)
can use to locate libraries, manifests, and modals spread across the
fleet. It deliberately does **not**:

* read or embed file contents into the manifest (only path/size/hash
  metadata is recorded);
* contact the network or sibling repositories (cross-repo ingestion is
  delegated to the opt-in operator tool ``scripts/total_fleet_crawler.py``
  and is reported here as ``status: not_available_in_sandbox`` when no
  crawler output is on disk);
* invent semantic labels — anything that does not match an explicit rule
  is recorded as ``"unclassified"``.

The Semantic Purpose classifier is a flat, ordered table of
``(rule, label)`` pairs. The first matching rule wins. Rules are
intentionally narrow and based on filesystem evidence (path prefixes,
basename keywords) rather than file contents.
"""

from __future__ import annotations

import datetime as _dt
import fnmatch
import hashlib
import os
import re
from pathlib import Path
from typing import Callable, Iterable

# --------------------------------------------------------------------------- #
# Scope
# --------------------------------------------------------------------------- #

# Partitions we scan recursively. The build script trusts this list; if a
# directory is missing it is reported as ``present: false`` rather than
# silently skipped.
PARTITION_DIRS = (
    "Partition_01",
    "Partition_02",
    "Partition_03",
    "Partition_04",
    "Partition_46",
)

# Extensions we record per file inside each partition.
PARTITION_FILE_EXTENSIONS = frozenset({".json", ".md", ".txt", ".py"})

# Documents we deep-read everywhere in the local tree (path index only —
# we still do not embed contents).
DEEP_READ_BASENAMES = ("README.md", "system_manifest.json", "architecture.md")

# Directories never walked into. Mirrors ``EXCLUDED_DIRS`` in the build
# script so the two stay consistent.
EXCLUDED_DIRS = frozenset({
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
})

# Optional crawler artifact (produced by scripts/total_fleet_crawler.py).
CROSS_REPO_DISCOVERY_REL = "fleet/fleet_discovery.json"


# --------------------------------------------------------------------------- #
# Semantic Purpose classifier
# --------------------------------------------------------------------------- #
#
# Each rule is a callable ``(rel_path: str) -> bool``. The first rule that
# returns ``True`` assigns its label; otherwise the label is
# ``"unclassified"``. Path comparisons are POSIX, case-insensitive on the
# basename only (paths use the on-disk casing).

UNCLASSIFIED = "unclassified"


def _starts_with(prefix: str) -> Callable[[str], bool]:
    p = prefix.rstrip("/") + "/"
    return lambda rel: rel == prefix.rstrip("/") or rel.startswith(p)


def _name_in(*names: str) -> Callable[[str], bool]:
    lowered = {n.lower() for n in names}
    return lambda rel: os.path.basename(rel).lower() in lowered


def _name_glob(*patterns: str) -> Callable[[str], bool]:
    return lambda rel: any(
        fnmatch.fnmatchcase(os.path.basename(rel).lower(), pat.lower())
        for pat in patterns
    )


def _contains(*needles: str) -> Callable[[str], bool]:
    lowered = tuple(n.lower() for n in needles)
    return lambda rel: any(n in rel.lower() for n in lowered)


# Order matters: more specific rules come first. Documentation overrides
# only when the basename is exactly README/architecture/system_manifest;
# everything else falls through to topic-based rules.
SEMANTIC_RULES: tuple[tuple[Callable[[str], bool], str], ...] = (
    # --- Exact, well-known artifacts --------------------------------------
    (_name_in("system_manifest.json"), "System Manifest"),
    (_name_in("architecture.md"), "Architecture Doc"),
    (_name_in("readme.md"), "Documentation"),

    # --- Top-level functional areas (path-based) --------------------------
    (_starts_with("Trading_Garages"), "Trading Logic"),
    (_starts_with("trading"), "Trading Logic"),
    (_starts_with("Districts"), "District Manifest"),
    (_starts_with("Forever_Learning"), "Forever Learning"),
    (_starts_with("Archive_Vault"), "Archive Vault"),
    (_starts_with("workers"), "Worker Config"),
    (_starts_with("sentinel-scout-templates"), "Worker Config"),
    (_starts_with("vamguard_templates"), "Vamguard Asset"),
    (_starts_with("VAMGUARD_TITAN"), "Vamguard Asset"),
    (_starts_with("tia-architect-core-templates"), "TIA Core"),
    (_starts_with("tia-citadel-templates"), "TIA Core"),
    (_starts_with("TIA_MASTER_BUILD"), "TIA Core"),
    (_starts_with("S10_CITADEL_OMEGA_INTEL"), "Citadel Intel"),
    (_starts_with("ingestion"), "Ingestion Pipeline"),
    (_starts_with("inventory"), "Manifest/Inventory"),
    (_starts_with("mapping"), "Manifest/Inventory"),
    (_starts_with("fleet"), "Fleet Map"),
    (_starts_with("security"), "Security"),
    (_starts_with("legal"), "Legal Doc"),
    (_starts_with("tests"), "Test"),
    (_starts_with("scripts"), "Operator Script"),
    (_starts_with("services"), "Service Module"),
    (_starts_with("core"), "Core Module"),
    (_starts_with("frontend"), "Frontend Asset"),
    (_starts_with("pages"), "Frontend Asset"),
    (_starts_with("templates"), "Template"),
    (_starts_with("website_templates"), "Template"),
    (_starts_with("docs"), "Documentation"),
    (_starts_with("PERSONA_SHOPPING"), "Persona Asset"),
    (_starts_with("Research"), "Research"),
    (_starts_with("data"), "Data Asset"),
    (_starts_with("deploy"), "Deployment"),
    (_starts_with("bridge"), "Bridge Module"),
    (_starts_with("src"), "Core Module"),

    # --- Topic-based fallbacks (basename / path keyword) ------------------
    (_contains("adobe", "vts"), "Adobe Plugin"),
    (_contains("multimedia", "audio", "video", "/media/"), "Multimedia Config"),
    (_contains("trader", "trading", "ccxt", "mexc", "binance"), "Trading Logic"),
    (_contains("citadel"), "Citadel Doc"),
    (_contains("tia"), "TIA Core"),
    (_contains("vamguard"), "Vamguard Asset"),
    (_contains("rag", "vector", "embedding"), "RAG Component"),
    (_contains("manifest", "inventory", "registry"), "Manifest/Inventory"),
    (_contains("workflow", "deploy", "ignite"), "Deployment"),
    (_name_glob("test_*.py", "*_test.py"), "Test"),
)


def classify(rel_path: str) -> str:
    """Return the Semantic Purpose label for a repo-relative POSIX path."""
    for rule, label in SEMANTIC_RULES:
        if rule(rel_path):
            return label
    return UNCLASSIFIED


# Public, machine-readable description of the rules. Useful for tests
# and for letting downstream tools display "why" a label was chosen.
def describe_rules() -> list[dict]:
    return [
        {"order": i, "label": label}
        for i, (_, label) in enumerate(SEMANTIC_RULES)
    ]


# --------------------------------------------------------------------------- #
# Filesystem helpers (kept local to avoid import cycles with the build
# script, and to make this module independently testable).
# --------------------------------------------------------------------------- #
def _walk(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        for fname in sorted(filenames):
            yield Path(dirpath) / fname


def _sha256_truncated(path: Path, length: int = 16) -> str | None:
    h = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                h.update(chunk)
    except OSError:
        return None
    return h.hexdigest()[:length]


def _iso(mtime: float) -> str:
    return _dt.datetime.fromtimestamp(mtime, tz=_dt.timezone.utc).isoformat()


# --------------------------------------------------------------------------- #
# Partition scan
# --------------------------------------------------------------------------- #
def scan_partition(
    repo_root: Path,
    partition: str,
    is_secret: Callable[[str], bool],
) -> dict:
    """Return a deterministic record for one partition directory.

    ``is_secret`` is supplied by the caller (the build script) so we share
    a single source of truth for redaction patterns. Secret files are
    listed by path only — no hash, no size beyond what stat() reveals on
    the directory entry.
    """
    pdir = repo_root / partition
    if not pdir.is_dir():
        return {
            "partition": partition,
            "present": False,
            "file_count": 0,
            "files": [],
        }

    files: list[dict] = []
    for fpath in _walk(pdir):
        ext = fpath.suffix.lower()
        if ext not in PARTITION_FILE_EXTENSIONS:
            continue
        try:
            rel = fpath.relative_to(repo_root).as_posix()
        except ValueError:
            continue
        try:
            st = fpath.stat()
        except OSError:
            continue
        entry: dict = {
            "path": rel,
            "extension": ext,
            "size": st.st_size,
            "mtime": _iso(st.st_mtime),
            "semantic_purpose": classify(rel),
        }
        if is_secret(rel):
            entry["redacted"] = True
        else:
            digest = _sha256_truncated(fpath)
            if digest is not None:
                entry["sha256_16"] = digest
        files.append(entry)

    return {
        "partition": partition,
        "present": True,
        "file_count": len(files),
        "files": files,
    }


# --------------------------------------------------------------------------- #
# Deep-read index (README / system_manifest / architecture)
# --------------------------------------------------------------------------- #
def deep_read_index(
    repo_root: Path,
    is_secret: Callable[[str], bool],
) -> list[dict]:
    """Locate every deep-read document in the local tree.

    Records path, size, full SHA-256, mtime, and Semantic Purpose. Does
    not include file contents; the manifest is metadata-only.
    """
    targets = {n.lower() for n in DEEP_READ_BASENAMES}
    out: list[dict] = []
    for fpath in _walk(repo_root):
        if fpath.name.lower() not in targets:
            continue
        try:
            rel = fpath.relative_to(repo_root).as_posix()
        except ValueError:
            continue
        try:
            st = fpath.stat()
        except OSError:
            continue
        entry: dict = {
            "path": rel,
            "basename": fpath.name,
            "size": st.st_size,
            "mtime": _iso(st.st_mtime),
            "semantic_purpose": classify(rel),
        }
        if is_secret(rel):
            entry["redacted"] = True
        else:
            h = hashlib.sha256()
            try:
                with fpath.open("rb") as fh:
                    for chunk in iter(lambda: fh.read(65536), b""):
                        h.update(chunk)
                entry["sha256"] = h.hexdigest()
            except OSError:
                pass
        out.append(entry)
    out.sort(key=lambda e: e["path"])
    return out


# --------------------------------------------------------------------------- #
# Cross-repo ingestion status (delegated to total_fleet_crawler.py)
# --------------------------------------------------------------------------- #
def cross_repo_status(repo_root: Path) -> dict:
    """Report whether sibling-repo discovery output is available.

    We never invent sibling data here. If the operator has run
    ``scripts/total_fleet_crawler.py`` (which requires a GitHub token and
    is opt-in), its output file will exist and we surface its top-level
    counts. Otherwise we emit ``not_available_in_sandbox`` with an
    actionable hint.
    """
    discovery = repo_root / CROSS_REPO_DISCOVERY_REL
    if not discovery.is_file():
        return {
            "status": "not_available_in_sandbox",
            "discovery_path": CROSS_REPO_DISCOVERY_REL,
            "discovery_exists": False,
            "hint": (
                "Run 'python scripts/total_fleet_crawler.py' on a workstation "
                "with GH_TOKEN (or GITHUB_TOKEN) set to populate "
                f"{CROSS_REPO_DISCOVERY_REL}. The build script will then "
                "merge its output into 'fleet_map' on the next run."
            ),
        }
    try:
        st = discovery.stat()
    except OSError:
        return {
            "status": "discovery_unreadable",
            "discovery_path": CROSS_REPO_DISCOVERY_REL,
            "discovery_exists": True,
        }
    return {
        "status": "discovery_present",
        "discovery_path": CROSS_REPO_DISCOVERY_REL,
        "discovery_exists": True,
        "discovery_size": st.st_size,
        "discovery_mtime": _iso(st.st_mtime),
        "note": (
            "See 'fleet_map' for the merged registry+discovery view. "
            "This section reports presence only."
        ),
    }


# --------------------------------------------------------------------------- #
# Top-level builder
# --------------------------------------------------------------------------- #
def _summarise_purpose_counts(records: Iterable[dict]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in records:
        for f in r.get("files", []):
            label = f.get("semantic_purpose", UNCLASSIFIED)
            counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


def build_rag_knowledge_base(
    repo_root: Path,
    is_secret: Callable[[str], bool],
) -> dict:
    """Assemble the ``rag_knowledge_base`` section.

    ``is_secret`` is passed in so this module shares the build script's
    redaction policy without re-importing it (which would create a cycle).
    """
    partition_records = [
        scan_partition(repo_root, p, is_secret) for p in PARTITION_DIRS
    ]
    deep_docs = deep_read_index(repo_root, is_secret)

    deep_purpose_counts: dict[str, int] = {}
    for d in deep_docs:
        label = d.get("semantic_purpose", UNCLASSIFIED)
        deep_purpose_counts[label] = deep_purpose_counts.get(label, 0) + 1

    partitions_present = [r["partition"] for r in partition_records if r["present"]]
    partitions_missing = [r["partition"] for r in partition_records if not r["present"]]

    return {
        "schema_version": "1.0.0",
        "scope": {
            "partitions_scanned": list(PARTITION_DIRS),
            "partitions_present": partitions_present,
            "partitions_missing": partitions_missing,
            "partition_file_extensions": sorted(PARTITION_FILE_EXTENSIONS),
            "deep_read_basenames": list(DEEP_READ_BASENAMES),
        },
        "classifier": {
            "rule_count": len(SEMANTIC_RULES),
            "labels": sorted({label for _, label in SEMANTIC_RULES} | {UNCLASSIFIED}),
            "default_label": UNCLASSIFIED,
            "rules": describe_rules(),
        },
        "partitions": partition_records,
        "deep_read_documents": {
            "document_count": len(deep_docs),
            "purpose_counts": dict(sorted(deep_purpose_counts.items())),
            "documents": deep_docs,
        },
        "semantic_purpose_summary": {
            "total_files_classified": sum(
                r["file_count"] for r in partition_records
            ),
            "purpose_counts": _summarise_purpose_counts(partition_records),
        },
        "cross_repo_ingestion": cross_repo_status(repo_root),
    }
