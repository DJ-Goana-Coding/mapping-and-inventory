"""
Sovereign Industries Init — Master Compilation Script
======================================================
Formally partitions the Citadel's operational output into the three
immutable pillars of Sovereign Independence:

  1. **The Kinetic Forge**   — Hard Asset & Extraction (Industry 01)
  2. **The Obsidian Network** — Data & Infrastructure Autonomy (Industry 02)
  3. **The Resonance Engine** — Culture & Narrative Control (Industry 03)

Resource allocation model
--------------------------
The 14-Space Swarm is weighted by operational load across the three
industries.  Allocation percentages are configurable via
:data:`INDUSTRY_WEIGHTS` and are written to the
``~/CITADEL_ARK/D12/macro_architecture.json`` manifest so that downstream
industry scripts can read their assigned quotas.

Usage::

    python3 scripts/sovereign_industries_init.py --allocate-resources
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
import platform
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

#: Citadel ARK root — defaults to ~/CITADEL_ARK, overridable via env var.
CITADEL_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get("CITADEL_ARK_ROOT", str(pathlib.Path.home() / "CITADEL_ARK"))
)

#: Three sovereign industries with their operational weight (must sum to 1.0).
INDUSTRY_WEIGHTS: dict[str, float] = {
    "industry_01_forge": 0.40,       # Hard Asset & Extraction — highest capital weight
    "industry_02_obsidian": 0.35,    # Data & Infrastructure — backbone allocation
    "industry_03_resonance": 0.25,   # Culture & Narrative — broadcast overhead
}

#: 14-Space Swarm node identifiers.
SWARM_NODES: list[str] = [
    "S01_Genesis",
    "S02_Vault",
    "S03_Trader",
    "S04_Librarian",
    "S05_OpenBin",
    "S06_TribeNet",
    "S07_TraderLogs",
    "S08_MediaCoding",
    "S09_SoulSync",
    "S10_Phalanx",
    "S11_PerimeterScout",
    "S12_MacroArch",
    "S13_ShadowSector",
    "S14_OmegaCore",
]

#: Industry → primary swarm nodes (indices into SWARM_NODES list).
INDUSTRY_NODE_MAP: dict[str, list[str]] = {
    "industry_01_forge": [
        "S03_Trader", "S07_TraderLogs", "S10_Phalanx", "S13_ShadowSector", "S14_OmegaCore"
    ],
    "industry_02_obsidian": [
        "S02_Vault", "S05_OpenBin", "S06_TribeNet", "S11_PerimeterScout", "S12_MacroArch"
    ],
    "industry_03_resonance": [
        "S01_Genesis", "S04_Librarian", "S08_MediaCoding", "S09_SoulSync"
    ],
}


# ---------------------------------------------------------------------------
# Resource probing
# ---------------------------------------------------------------------------


def probe_system_resources() -> dict[str, Any]:
    """
    Probe available CPU, RAM, and bandwidth capacity.

    Returns a dict with keys ``cpu_cores``, ``cpu_freq_mhz``,
    ``ram_total_mb``, ``ram_available_mb``, and ``platform``.
    Bandwidth capacity is estimated from network adapter count.
    """
    resources: dict[str, Any] = {
        "platform": platform.system(),
        "cpu_cores": os.cpu_count() or 1,
        "cpu_freq_mhz": None,
        "ram_total_mb": None,
        "ram_available_mb": None,
        "network_adapters": 0,
    }

    # CPU frequency (best-effort, no psutil dependency required)
    try:
        import psutil  # type: ignore[import]

        freq = psutil.cpu_freq()
        if freq:
            resources["cpu_freq_mhz"] = round(freq.current, 1)
        mem = psutil.virtual_memory()
        resources["ram_total_mb"] = round(mem.total / 1024 / 1024, 1)
        resources["ram_available_mb"] = round(mem.available / 1024 / 1024, 1)
        net = psutil.net_if_stats()
        resources["network_adapters"] = len([k for k, v in net.items() if v.isup])
    except ImportError:
        logger.debug("psutil not installed — using fallback resource detection.")
        # Fallback: parse /proc/meminfo on Linux
        meminfo = pathlib.Path("/proc/meminfo")
        if meminfo.exists():
            for line in meminfo.read_text(encoding="utf-8").splitlines():
                if line.startswith("MemTotal:"):
                    resources["ram_total_mb"] = round(int(line.split()[1]) / 1024, 1)
                elif line.startswith("MemAvailable:"):
                    resources["ram_available_mb"] = round(int(line.split()[1]) / 1024, 1)

    return resources


# ---------------------------------------------------------------------------
# Allocation engine
# ---------------------------------------------------------------------------


def build_allocation(
    resources: dict[str, Any],
    weights: dict[str, float] | None = None,
) -> dict[str, Any]:
    """
    Compute per-industry resource allocations based on *weights*.

    Parameters
    ----------
    resources:
        Output of :func:`probe_system_resources`.
    weights:
        Industry weight mapping.  Defaults to :data:`INDUSTRY_WEIGHTS`.
        Values must sum to ≤ 1.0.

    Returns
    -------
    dict
        Allocation manifest ready for JSON serialisation.
    """
    if weights is None:
        weights = INDUSTRY_WEIGHTS

    total_weight = sum(weights.values())
    if total_weight > 1.001:
        raise ValueError(
            f"Industry weights sum to {total_weight:.3f} — must not exceed 1.0."
        )

    cpu_cores = resources.get("cpu_cores", 1)
    ram_mb = resources.get("ram_available_mb") or resources.get("ram_total_mb") or 1024
    adapters = max(resources.get("network_adapters", 1), 1)

    industries: dict[str, Any] = {}
    for industry_id, weight in weights.items():
        industries[industry_id] = {
            "weight": weight,
            "allocated_cpu_cores": round(cpu_cores * weight, 2),
            "allocated_ram_mb": round(ram_mb * weight, 1),
            "allocated_bandwidth_ratio": round(weight / adapters, 4),
            "primary_nodes": INDUSTRY_NODE_MAP.get(industry_id, []),
            "status": "ALLOCATED",
        }

    return {
        "freq_signature": FREQ_SIGNATURE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "swarm_node_count": len(SWARM_NODES),
        "swarm_nodes": SWARM_NODES,
        "system_resources": resources,
        "industry_status": "SOVEREIGN_INDUSTRIES_ACTIVE",
        "industries": industries,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_manifest(manifest: dict[str, Any], dest: pathlib.Path) -> None:
    """
    Write the allocation manifest to *dest* as pretty-printed JSON.

    Creates parent directories if they do not exist.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("Manifest written → %s", dest)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Sovereign Industries Init — partition Citadel output into the 3 industry pillars.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--allocate-resources",
        action="store_true",
        help="Probe system resources and write the allocation manifest.",
    )
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=CITADEL_ROOT / "D12" / "macro_architecture.json",
        help="Destination path for the macro_architecture.json manifest.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the manifest to stdout without writing to disk.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
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

    if not args.allocate_resources:
        parser.print_help()
        return 0

    logger.info("Sovereign Industries Init — probing system resources …")
    resources = probe_system_resources()
    logger.info(
        "Resources detected: %d CPU core(s) | %.0f MB RAM available | %d network adapter(s)",
        resources["cpu_cores"],
        resources.get("ram_available_mb") or 0,
        resources.get("network_adapters", 0),
    )

    manifest = build_allocation(resources)

    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return 0

    write_manifest(manifest, args.output)

    # Report industry status to console (mirrors the jq query in the directive)
    print(manifest["industry_status"])
    logger.info("SOVEREIGN_INDUSTRIES_ACTIVE — allocation complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
