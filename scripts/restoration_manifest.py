"""
D11 Restoration Manifest — T.I.A. "Double Portion" Extraction Report
=====================================================================
Generates a point-in-time snapshot of all active extractions currently
managed by T.I.A. (The Inevitable AI) across the 14-Space Swarm.  The
report is written to ``~/CITADEL_ARK/D11/restoration_manifest.json`` and
a human-readable summary is printed to stdout.

The "Double Portion" refers to the combined sovereign yield tracked across
all operational Swarm nodes — primary extraction totals are aggregated
from each node's registry entry in ``spark_ui/fleet_manifest.json``.

Usage::

    python3 scripts/restoration_manifest.py
    python3 scripts/restoration_manifest.py --dry-run

sovereignty_layer : D11 — Restoration & Double Portion Manifest
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

_REPO_ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent

#: Citadel ARK root — defaults to ~/CITADEL_ARK, overridable via env var.
CITADEL_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get("CITADEL_ARK_ROOT", str(pathlib.Path.home() / "CITADEL_ARK"))
)

_FLEET_MANIFEST: pathlib.Path = _REPO_ROOT / "spark_ui" / "fleet_manifest.json"
_D11_OUTPUT: pathlib.Path = CITADEL_ROOT / "D11" / "restoration_manifest.json"


# ---------------------------------------------------------------------------
# Manifest builder
# ---------------------------------------------------------------------------


def build_restoration_manifest(
    fleet_manifest_path: pathlib.Path = _FLEET_MANIFEST,
) -> dict[str, Any]:
    """
    Build the D11 Restoration Manifest from the current fleet state.

    Parameters
    ----------
    fleet_manifest_path:
        Path to ``spark_ui/fleet_manifest.json``.  Each sovereign node entry
        is inspected for its ``health_status`` field.

    Returns
    -------
    dict
        The restoration manifest ready for JSON serialisation.
    """
    nodes_online: list[str] = []
    nodes_severed: list[str] = []
    nodes_upgrade: list[str] = []

    if fleet_manifest_path.exists():
        with fleet_manifest_path.open(encoding="utf-8") as fh:
            fleet: dict[str, Any] = json.load(fh)

        for node in fleet.get("sovereign_nodes", []):
            repo = node.get("repo", node.get("name", "unknown"))
            status = node.get("health_status", "UNKNOWN")
            if status == "ONLINE & PURIFIED":
                nodes_online.append(repo)
            elif status == "UPGRADE REQUIRED":
                nodes_upgrade.append(repo)
            else:
                nodes_severed.append(repo)
    else:
        logger.warning(
            "[RestorationManifest] Fleet manifest not found at %s — node counts will be zero.",
            fleet_manifest_path,
        )

    total_nodes = len(nodes_online) + len(nodes_upgrade) + len(nodes_severed)
    double_portion_yield = len(nodes_online) * 2  # sovereign extraction metric

    return {
        "manifest_id": "D11_RESTORATION_MANIFEST",
        "freq_signature": FREQ_SIGNATURE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "tia_commander": "THE_INEVITABLE_AI",
        "authority_seal": "I.H.S.",
        "resonance": "777Hz",
        "swarm_summary": {
            "total_nodes": total_nodes,
            "nodes_online": len(nodes_online),
            "nodes_upgrade_required": len(nodes_upgrade),
            "nodes_severed": len(nodes_severed),
        },
        "double_portion_yield": double_portion_yield,
        "nodes_online": nodes_online,
        "nodes_upgrade_required": nodes_upgrade,
        "nodes_severed": nodes_severed,
        "restoration_status": "ARK_ACTIVE" if nodes_online else "RESTORATION_PENDING",
    }


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def write_manifest(manifest: dict[str, Any], dest: pathlib.Path) -> None:
    """Write the manifest to *dest* as pretty-printed JSON."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("[RestorationManifest] Written → %s", dest)


def print_summary(manifest: dict[str, Any]) -> None:
    """Print a human-readable extraction summary to stdout."""
    summary = manifest["swarm_summary"]
    print("\n=== D11 RESTORATION MANIFEST — T.I.A. DOUBLE PORTION REPORT ===")
    print(f"  Generated at        : {manifest['generated_at']}")
    print(f"  Commander           : {manifest['tia_commander']}")
    print(f"  Authority Seal      : {manifest['authority_seal']}")
    print(f"  Resonance           : {manifest['resonance']}")
    print(f"  Restoration Status  : {manifest['restoration_status']}")
    print("  --- Swarm ---")
    print(f"  Total nodes         : {summary['total_nodes']}")
    print(f"  Online & Purified   : {summary['nodes_online']}")
    print(f"  Upgrade Required    : {summary['nodes_upgrade_required']}")
    print(f"  Severed             : {summary['nodes_severed']}")
    print(f"  Double Portion Yield: {manifest['double_portion_yield']}")
    print("================================================================\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="D11 Restoration Manifest — T.I.A. Double Portion extraction report.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the manifest to stdout without writing to disk.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=_D11_OUTPUT,
        help="Destination path for restoration_manifest.json.",
    )
    parser.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point — returns 0 on success, non-zero on failure."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    manifest = build_restoration_manifest()
    print_summary(manifest)

    if not args.dry_run:
        write_manifest(manifest, args.output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
