#!/usr/bin/env python3
"""Build the repo-local ``global_manifest.json`` (Sovereign Fleet Reconstruction).

This script performs a safe, deterministic inventory of the repository and
produces two artifacts:

* ``inventory/file_index.json`` — every non-ignored file with relative path,
  extension, size and a truncated SHA-256. Files matching secret-like
  patterns are recorded with ``"redacted": true`` and **no content hash**.
* ``global_manifest.json`` (repo root) — a single source of truth that
  references the existing manifests rather than duplicating them, declares
  RAG dependency presence, partition liveness, and external reference
  placeholders. No credentials, tokens, or "bypass" data are embedded.

The script is idempotent: re-running on an unchanged tree produces
byte-identical output (timestamps are pinned to the latest mtime in the
inventory rather than wall-clock time).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

SCHEMA_VERSION = "1.0.0"

# Directories never walked into.
EXCLUDED_DIRS = {
    ".git",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    "node_modules",
    ".venv",
    "venv",
}

# Filename / glob patterns whose CONTENTS must never be hashed or read.
# Matches are tested against both the basename and the relative path.
SECRET_PATTERNS = (
    "*.env",
    ".env",
    ".env.*",
    "*.pem",
    "*.key",
    "credentials*.json",
    "token*.json",
    "token.json",
    "*.token",
    "service_account*.json",
    "client_secret*.json",
    "rclone.conf",
    "*.vault",
    "*.vault.json",
    "*_vault.json",
)

# Existing manifests to be referenced (not duplicated) by the global manifest.
KNOWN_MANIFESTS = (
    "system_manifest.json",
    "master_inventory.json",
    "districts.json",
    "district_status_report.json",
    "worker_status.json",
    "FOUNDATION_MANIFEST.md",
)

# Live partitions per operator directive. Anything else under Partition_NN is
# treated as Remote/Archived.
LIVE_PARTITIONS = {1, 2, 3, 4, 46}
TOTAL_PARTITIONS = 46

# Presence-only detection of bypass / tunnel-setup scripts. We record only
# whether the file exists; we never inline its contents.
BYPASS_SCRIPT_CANDIDATES = (
    "scripts/setup_gdrive_rclone.sh",
    "scripts/initialize_credential_vault.py",
    "scripts/verify_gdrive_access.py",
    "scripts/harvest_gdrive_accounts.py",
    "scripts/harvest_email_accounts.py",
    "scripts/clone_citadel_omega_libs.sh",
)

# RAG dependencies whose presence in requirements.txt we surface.
RAG_DEPS = ("faiss-cpu", "sentence-transformers", "huggingface-hub")


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _matches_secret(rel_path: str) -> bool:
    name = os.path.basename(rel_path)
    for pat in SECRET_PATTERNS:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def _sha256_truncated(path: Path, length: int = 16) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:length]


def _sha256_full(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _walk_repo(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune excluded directories in place for os.walk efficiency.
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDED_DIRS)
        for fname in sorted(filenames):
            yield Path(dirpath) / fname


def build_file_index(root: Path) -> list[dict]:
    """Return a deterministic, redacted inventory of every file in the repo."""
    # Exclude our own generated artifacts; they're not source-of-truth
    # inputs and including them would make the index non-convergent across
    # runs (each run would alter what the next run sees).
    self_outputs = {
        (root / "global_manifest.json").resolve(),
        (root / "inventory" / "file_index.json").resolve(),
    }
    index: list[dict] = []
    for fpath in _walk_repo(root):
        try:
            if fpath.resolve() in self_outputs:
                continue
        except OSError:
            pass
        try:
            rel = fpath.relative_to(root).as_posix()
        except ValueError:
            continue
        try:
            size = fpath.stat().st_size
        except OSError:
            continue
        ext = fpath.suffix.lower()
        if _matches_secret(rel):
            index.append(
                {
                    "path": rel,
                    "extension": ext,
                    "size": size,
                    "redacted": True,
                }
            )
            continue
        try:
            digest = _sha256_truncated(fpath)
        except OSError:
            digest = None
        index.append(
            {
                "path": rel,
                "extension": ext,
                "size": size,
                "sha256_16": digest,
                "redacted": False,
            }
        )
    return index


def summarise_assets(index: list[dict], root: Path) -> dict:
    ext_counts: dict[str, int] = {}
    redacted_count = 0
    total_size = 0
    for entry in index:
        ext = entry["extension"] or "<none>"
        ext_counts[ext] = ext_counts.get(ext, 0) + 1
        total_size += entry["size"]
        if entry.get("redacted"):
            redacted_count += 1

    top_level = sorted(
        p.name
        for p in root.iterdir()
        if p.is_dir() and p.name not in EXCLUDED_DIRS
    )

    partition_re = re.compile(r"^Partition_(\d{2})$")
    found_partitions = sorted(
        int(m.group(1))
        for m in (partition_re.match(p.name) for p in root.iterdir() if p.is_dir())
        if m
    )

    partitions = {
        "total_declared": TOTAL_PARTITIONS,
        "live_ids": sorted(LIVE_PARTITIONS),
        "live_present": sorted(n for n in found_partitions if n in LIVE_PARTITIONS),
        "live_missing": sorted(n for n in LIVE_PARTITIONS if n not in found_partitions),
        "remote_archived_ids": sorted(
            n for n in range(1, TOTAL_PARTITIONS + 1) if n not in LIVE_PARTITIONS
        ),
        "directories_found": [f"Partition_{n:02d}" for n in found_partitions],
    }

    return {
        "file_count": len(index),
        "redacted_count": redacted_count,
        "total_size_bytes": total_size,
        "extension_counts": dict(sorted(ext_counts.items())),
        "top_level_directories": top_level,
        "partitions": partitions,
    }


def reconcile_manifests(root: Path) -> dict:
    """Reference (don't duplicate) the existing manifest files."""
    out: dict[str, dict] = {}
    for name in KNOWN_MANIFESTS:
        path = root / name
        entry: dict = {"path": name, "exists": path.exists()}
        if not path.exists():
            out[name] = entry
            continue
        entry["size"] = path.stat().st_size
        entry["sha256"] = _sha256_full(path)
        if name.endswith(".json"):
            try:
                with path.open("r", encoding="utf-8") as fh:
                    data = json.load(fh)
                if isinstance(data, dict):
                    entry["top_level_keys"] = sorted(data.keys())
                    entry["kind"] = "object"
                elif isinstance(data, list):
                    entry["top_level_keys"] = []
                    entry["kind"] = "array"
                    entry["length"] = len(data)
                else:
                    entry["kind"] = type(data).__name__
            except (OSError, json.JSONDecodeError) as exc:
                entry["parse_error"] = str(exc)
        else:
            entry["kind"] = "markdown"
        out[name] = entry
    return out


def detect_rag_dependencies(root: Path) -> dict:
    req = root / "requirements.txt"
    presence = {dep: False for dep in RAG_DEPS}
    pinned: dict[str, str] = {}
    if req.exists():
        for raw in req.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            for dep in RAG_DEPS:
                if line.lower().startswith(dep.lower()):
                    presence[dep] = True
                    pinned[dep] = line
    return {
        "source": "requirements.txt",
        "present": presence,
        "specifiers": pinned,
    }


def detect_bypass_scripts(root: Path) -> dict:
    """Record presence-only flags for tunnel/credential setup scripts."""
    return {
        rel: (root / rel).exists() for rel in BYPASS_SCRIPT_CANDIDATES
    }


def _latest_mtime(root: Path) -> float:
    # Exclude our own generated artifacts so re-runs don't chase their own
    # mtimes (which would break determinism).
    excluded = {
        (root / "global_manifest.json").resolve(),
        (root / "inventory" / "file_index.json").resolve(),
    }
    latest = 0.0
    for fpath in _walk_repo(root):
        try:
            if fpath.resolve() in excluded:
                continue
        except OSError:
            pass
        try:
            m = fpath.stat().st_mtime
        except OSError:
            continue
        if m > latest:
            latest = m
    return latest


def build_global_manifest(
    root: Path, file_index: list[dict], mtime: float | None = None
) -> dict:
    if mtime is None:
        mtime = _latest_mtime(root)
    generated_at = (
        _dt.datetime.fromtimestamp(mtime, tz=_dt.timezone.utc).isoformat()
        if mtime
        else "1970-01-01T00:00:00+00:00"
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "generator": "scripts/build_global_manifest.py",
        "repo_assets": summarise_assets(file_index, root),
        "manifests": reconcile_manifests(root),
        "rag_dependencies": detect_rag_dependencies(root),
        "external_references": {
            "gdrive_archive_id": "CITADEL-BOT-INDEX",
            "gdrive_archive_env_var": "GDRIVE_ARCHIVE_ID",
            "hf_dataset_storage": "DJ-Goana-Coding/CITADEL_OMEGA_Inventory",
            "hf_dataset_env_var": "HF_DATASET_REPO",
            "hf_datasets": [],
            "notes": (
                "Identifiers only. Authentication must be supplied at runtime "
                "via environment variables; never embed secrets in this manifest."
            ),
        },
        "bypass_scripts_present": detect_bypass_scripts(root),
        "out_of_scope": [
            "credential mapping or relocation",
            "creation of Partition_05..45 directories",
            "live network calls to Google Drive or Hugging Face",
            "addition of CCXT or other trading dependencies",
        ],
    }


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False) + "\n"
    path.write_text(text, encoding="utf-8")


# --------------------------------------------------------------------------- #
# Entry point
# --------------------------------------------------------------------------- #
def generate(root: Path) -> tuple[Path, Path]:
    """Generate both artifacts. Returns (file_index_path, global_manifest_path)."""
    file_index = build_file_index(root)
    # Pin generated_at to the source-tree mtime BEFORE we write our own
    # outputs, otherwise re-running would chase its own tail.
    source_mtime = _latest_mtime(root)
    file_index_path = root / "inventory" / "file_index.json"
    write_json(
        file_index_path,
        {
            "schema_version": SCHEMA_VERSION,
            "root": ".",
            "file_count": len(file_index),
            "files": file_index,
        },
    )
    manifest = build_global_manifest(root, file_index, mtime=source_mtime)
    manifest_path = root / "global_manifest.json"
    write_json(manifest_path, manifest)
    return file_index_path, manifest_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root (defaults to parent of this script's directory).",
    )
    args = parser.parse_args(argv)
    root: Path = args.root.resolve()
    if not root.is_dir():
        print(f"error: root {root} is not a directory", file=sys.stderr)
        return 2
    file_index_path, manifest_path = generate(root)
    print(f"Wrote {file_index_path.relative_to(root)}")
    print(f"Wrote {manifest_path.relative_to(root)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
