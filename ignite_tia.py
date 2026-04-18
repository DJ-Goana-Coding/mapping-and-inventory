#!/usr/bin/env python3
"""Thin loader for ``global_manifest.json`` (the T.I.A. ignition bridge).

This module is intentionally minimal. It exists so that external clients —
including the .NET *Private Nexus* — have a single, stable Python entry
point for querying the repository's manifest of manifests. It deliberately
does not open tunnels, contact Google Drive, or call Hugging Face. Any
external integration is the responsibility of the caller and must supply
its own credentials via environment variables.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_MANIFEST = REPO_ROOT / "global_manifest.json"

REQUIRED_TOP_LEVEL_KEYS = (
    "schema_version",
    "generated_at",
    "repo_assets",
    "manifests",
    "rag_dependencies",
    "external_references",
)

SUPPORTED_SCHEMA_MAJOR = 1


class ManifestError(RuntimeError):
    """Raised when the global manifest cannot be loaded or validated."""


def _validate(manifest: Any, source: Path) -> dict:
    if not isinstance(manifest, dict):
        raise ManifestError(f"{source}: top-level JSON must be an object")
    missing = [k for k in REQUIRED_TOP_LEVEL_KEYS if k not in manifest]
    if missing:
        raise ManifestError(f"{source}: missing required keys: {missing}")
    schema = str(manifest.get("schema_version", ""))
    try:
        major = int(schema.split(".", 1)[0])
    except ValueError as exc:
        raise ManifestError(f"{source}: invalid schema_version '{schema}'") from exc
    if major != SUPPORTED_SCHEMA_MAJOR:
        raise ManifestError(
            f"{source}: unsupported schema_version major {major} "
            f"(expected {SUPPORTED_SCHEMA_MAJOR})"
        )
    return manifest


def load_manifest(path: Path | str | None = None) -> dict:
    """Load and validate the global manifest.

    Resolution order:
    1. Explicit ``path`` argument.
    2. ``GLOBAL_MANIFEST_PATH`` environment variable.
    3. ``global_manifest.json`` next to this file.
    """
    if path is None:
        env = os.environ.get("GLOBAL_MANIFEST_PATH")
        path = Path(env) if env else DEFAULT_MANIFEST
    path = Path(path)
    if not path.is_file():
        raise ManifestError(f"manifest not found: {path}")
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ManifestError(f"{path}: invalid JSON: {exc}") from exc
    return _validate(data, path)


def summarise(manifest: dict) -> str:
    assets = manifest.get("repo_assets", {})
    parts = manifest.get("partitions") or assets.get("partitions", {})
    deps = manifest.get("rag_dependencies", {}).get("present", {})
    refs = manifest.get("external_references", {})
    bypass = manifest.get("bypass_scripts_present", {})
    lines = [
        f"schema_version    : {manifest.get('schema_version')}",
        f"generated_at      : {manifest.get('generated_at')}",
        f"file_count        : {assets.get('file_count')}",
        f"redacted_count    : {assets.get('redacted_count')}",
        f"total_size_bytes  : {assets.get('total_size_bytes')}",
        f"top_level_dirs    : {len(assets.get('top_level_directories', []))}",
        f"partitions_live   : {parts.get('live_present')}",
        f"partitions_remote : {len(parts.get('remote_archived_ids', []))}",
        f"rag_deps_present  : {sorted(k for k, v in deps.items() if v)}",
        f"gdrive_archive_id : {refs.get('gdrive_archive_id')}",
        f"hf_dataset_storage: {refs.get('hf_dataset_storage')}",
        f"bypass_scripts    : {sorted(k for k, v in bypass.items() if v)}",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Path to global_manifest.json (overrides GLOBAL_MANIFEST_PATH).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the validated manifest as JSON instead of a summary.",
    )
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.json:
        json.dump(manifest, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(summarise(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
