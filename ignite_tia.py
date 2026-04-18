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
    fleet = manifest.get("fleet_map", {}) or {}
    hf_datasets = refs.get("hf_datasets", []) or []
    verified_hf = sum(
        1 for d in hf_datasets if isinstance(d, dict) and d.get("verified") is True
    )
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
        f"hf_datasets       : {len(hf_datasets)} known, {verified_hf} verified",
        f"fleet_map_entries : {fleet.get('entry_count', 0)}",
        f"bypass_scripts    : {sorted(k for k, v in bypass.items() if v)}",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Network-status (no I/O — reports recorded gates only)
# --------------------------------------------------------------------------- #
NEXUS_RECEIPTS_REL = "fleet/nexus_receipts.json"


def _load_nexus_receipts(path: Path) -> dict:
    """Load operator-signed coherence receipts.

    Schema (all keys optional)::

        {
          "csharp_nexus_reachable": {"verified_at": "<iso8601>"},
          "gdrive_tunnel_open":    {"verified_at": "<iso8601>"},
          "adobe_vts_query_ok":    {"verified_at": "<iso8601>"}
        }

    Missing/malformed file → ``{}`` (every gate stays unverified).
    """
    if not path.is_file():
        return {}
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def network_status(manifest: dict, repo_root: Path | None = None) -> dict:
    """Compute a structured network-status report from a loaded manifest.

    Performs **zero** network I/O. Every flag is derived from data that's
    already on disk (the manifest itself, plus an optional operator-signed
    ``fleet/nexus_receipts.json``). ``citadel_visible`` is ``true`` only
    when *every* gate is satisfied; otherwise the ``reasons`` list explains
    which spoke or tunnel needs attention.
    """
    if repo_root is None:
        repo_root = REPO_ROOT
    receipts = _load_nexus_receipts(repo_root / NEXUS_RECEIPTS_REL)

    refs = manifest.get("external_references", {}) or {}
    fleet = manifest.get("fleet_map", {}) or {}
    sources = fleet.get("sources", {}) or {}
    aggregate = fleet.get("aggregate", {}) or {}
    hf_datasets = refs.get("hf_datasets", []) or []

    registry_src = sources.get("registry", {}) or {}
    discovery_src = sources.get("discovery", {}) or {}

    gates: list[dict] = []
    reasons: list[str] = []

    # Gate 1: registry populated.
    reg_count = int(registry_src.get("entry_count", 0) or 0)
    g1 = {
        "name": "fleet_registry_populated",
        "ok": reg_count > 0,
        "detail": f"{reg_count} registry entries",
    }
    gates.append(g1)
    if not g1["ok"]:
        reasons.append("fleet/fleet_registry.json has no entries (operator must curate)")

    # Gate 2: crawler discovery file present.
    disc_exists = bool(discovery_src.get("exists"))
    g2 = {
        "name": "fleet_discovery_present",
        "ok": disc_exists,
        "detail": (
            f"{discovery_src.get('entry_count', 0)} discovery entries"
            if disc_exists
            else "fleet/fleet_discovery.json absent"
        ),
    }
    gates.append(g2)
    if not g2["ok"]:
        reasons.append(
            "fleet/fleet_discovery.json absent — run scripts/total_fleet_crawler.py "
            "with GH_TOKEN set"
        )

    # Gate 3: at least one HF dataset verified.
    hf_total = len(hf_datasets)
    hf_verified = sum(
        1 for d in hf_datasets if isinstance(d, dict) and d.get("verified") is True
    )
    g3 = {
        "name": "hf_datasets_verified",
        "ok": hf_total > 0 and hf_verified == hf_total,
        "detail": f"{hf_verified}/{hf_total} HF datasets verified",
    }
    gates.append(g3)
    if not g3["ok"]:
        reasons.append(
            f"{hf_total - hf_verified}/{hf_total} HF datasets unverified — "
            "operator must add receipts to fleet/hf_receipts.json"
        )

    # Gates 4-6: external coherence receipts (operator-signed). We cannot
    # observe these from this process; they default to unknown/false.
    for key, label in (
        ("csharp_nexus_reachable", "C# Private Nexus reachable"),
        ("gdrive_tunnel_open", "GDrive CITADEL-BOT tunnel open"),
        ("adobe_vts_query_ok", "Adobe/VTS logic query succeeded"),
    ):
        receipt = receipts.get(key) if isinstance(receipts.get(key), dict) else None
        ok = isinstance(receipt, dict) and isinstance(receipt.get("verified_at"), str)
        gates.append(
            {
                "name": key,
                "ok": ok,
                "detail": (
                    f"verified_at={receipt['verified_at']}"
                    if ok and receipt is not None
                    else "no operator receipt"
                ),
            }
        )
        if not ok:
            reasons.append(
                f"{label}: no entry in fleet/nexus_receipts.json — "
                "operator must add a verified_at timestamp after personally confirming"
            )

    citadel_visible = all(g["ok"] for g in gates)

    return {
        "citadel_visible": citadel_visible,
        "gates": gates,
        "reasons": reasons,
        "fleet_map_entry_count": fleet.get("entry_count", 0),
        "discovery_aggregate": aggregate,
        "receipts_path": str((repo_root / NEXUS_RECEIPTS_REL).as_posix()),
        "receipts_present": (repo_root / NEXUS_RECEIPTS_REL).is_file(),
    }


def format_network_status(report: dict) -> str:
    lines: list[str] = []
    visible = report.get("citadel_visible", False)
    lines.append(f"CITADEL VISIBLE   : {'true' if visible else 'false'}")
    lines.append(f"fleet_map entries : {report.get('fleet_map_entry_count', 0)}")
    agg = report.get("discovery_aggregate", {}) or {}
    lines.append(
        f"discovery totals  : repos={agg.get('total_repos', 0)} "
        f"sysmf={agg.get('repos_with_system_manifest', 0)} "
        f"fileidx={agg.get('repos_with_file_index', 0)} "
        f"modules={agg.get('total_modules', 0)} "
        f"hf_urls={agg.get('repos_with_hf_space_url', 0)}"
    )
    lines.append(
        f"receipts          : {report.get('receipts_path')} "
        f"(present={report.get('receipts_present')})"
    )
    lines.append("gates:")
    for g in report.get("gates", []):
        mark = "PASS" if g.get("ok") else "FAIL"
        lines.append(f"  [{mark}] {g.get('name')}: {g.get('detail')}")
    reasons = report.get("reasons", [])
    if reasons:
        lines.append("reasons (fix in this order):")
        for r in reasons:
            lines.append(f"  - {r}")
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
    parser.add_argument(
        "--network-status",
        action="store_true",
        help=(
            "Print a structured network-status report (CITADEL VISIBLE flag, "
            "per-gate detail, and a reason list). Performs no network I/O."
        ),
    )
    args = parser.parse_args(argv)
    try:
        manifest = load_manifest(args.manifest)
    except ManifestError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if args.network_status:
        report = network_status(manifest)
        if args.json:
            json.dump(report, sys.stdout, indent=2)
            sys.stdout.write("\n")
        else:
            print(format_network_status(report))
        return 0 if report.get("citadel_visible") else 2
    if args.json:
        json.dump(manifest, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(summarise(manifest))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
