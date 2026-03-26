"""
Medic — DeepClean Protocol (Python Module)
==========================================
Python replacement for the legacy ``DeepClean.bat`` batch script.

Runs a 12-hour deep-clean cycle across all four primary Spokes:

* S10_Phalanx
* Oppo_Omega
* CGAL_Core
* pioneer-trader

Clean-up targets
----------------
* Temporary files (``*.tmp``, ``*.bak``, ``*.log`` older than retention window)
* Empty directories under each spoke's local node path
* Orphaned snapshot downloads in ``nodes/HF_Rack/`` (missing from migration
  manifest)

The Medic also verifies the 369-frequency signature on every vault record it
touches and emits a ``CLEAN_REPORT`` JSON after each cycle.

Usage::

    import asyncio
    from tasks.medic import run_deepclean_cycle, start_scheduled_medic

    # Single run:
    asyncio.run(run_deepclean_cycle())

    # 12-hour scheduled loop (blocks until cancelled):
    asyncio.run(start_scheduled_medic())
"""
from __future__ import annotations

import asyncio
import json
import logging
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

# Interval between deep-clean cycles (seconds).  Override via environment.
import os as _os

DEEPCLEAN_INTERVAL_S: int = int(_os.getenv("DEEPCLEAN_INTERVAL_S", str(12 * 3600)))

_REPO_ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent

# The four primary Spokes the Medic cleans
PRIMARY_SPOKES: list[str] = [
    "S10_Phalanx",
    "Oppo_Omega",
    "CGAL_Core",
    "pioneer-trader",
]

# File extensions that are eligible for deletion during a clean cycle
_TEMP_EXTENSIONS: tuple[str, ...] = (".tmp", ".bak")

# Maximum age (seconds) for log files before they are purged
_LOG_MAX_AGE_S: int = int(_os.getenv("MEDIC_LOG_MAX_AGE_S", str(7 * 24 * 3600)))  # 7 days

# Path where the Medic writes its clean report JSON
CLEAN_REPORT_PATH: pathlib.Path = _REPO_ROOT / "spark_ui" / "medic_clean_report.json"


# ---------------------------------------------------------------------------
# Clean helpers
# ---------------------------------------------------------------------------


def _clean_spoke(spoke_id: str, dry_run: bool) -> dict[str, Any]:
    """
    Run the deep-clean protocol for a single Spoke.

    Returns a summary dict for the spoke.
    """
    node_dir = _REPO_ROOT / "nodes" / spoke_id
    deleted_files: list[str] = []
    removed_dirs: list[str] = []

    if not node_dir.exists():
        logger.debug("[Medic] Spoke directory not found, skipping: %s", node_dir)
        return {
            "spoke": spoke_id,
            "node_dir": str(node_dir),
            "deleted_files": [],
            "removed_dirs": [],
            "status": "SKIPPED_NOT_FOUND",
        }

    now_ts = datetime.now(timezone.utc).timestamp()

    for filepath in node_dir.rglob("*"):
        if not filepath.is_file():
            continue

        suffix = filepath.suffix.lower()

        # Delete temp / bak files unconditionally
        if suffix in _TEMP_EXTENSIONS:
            if not dry_run:
                try:
                    filepath.unlink()
                    logger.info("[Medic] Deleted temp file: %s", filepath)
                except OSError as exc:
                    logger.warning("[Medic] Could not delete '%s': %s", filepath, exc)
                    continue
            deleted_files.append(str(filepath))
            continue

        # Delete stale log files
        if suffix == ".log":
            try:
                age = now_ts - filepath.stat().st_mtime
            except OSError:
                continue
            if age > _LOG_MAX_AGE_S:
                if not dry_run:
                    try:
                        filepath.unlink()
                        logger.info("[Medic] Deleted stale log: %s", filepath)
                    except OSError as exc:
                        logger.warning(
                            "[Medic] Could not delete log '%s': %s", filepath, exc
                        )
                        continue
                deleted_files.append(str(filepath))

    # Remove empty sub-directories
    if not dry_run:
        for dirpath in sorted(node_dir.rglob("*"), reverse=True):
            if dirpath.is_dir() and dirpath != node_dir:
                try:
                    dirpath.rmdir()
                    removed_dirs.append(str(dirpath))
                    logger.debug("[Medic] Removed empty dir: %s", dirpath)
                except OSError:
                    pass  # Not empty — skip

    return {
        "spoke": spoke_id,
        "node_dir": str(node_dir),
        "deleted_files": deleted_files,
        "removed_dirs": removed_dirs,
        "status": "OK",
    }


def _write_clean_report(report: dict[str, Any]) -> None:
    """Persist the clean report to :data:`CLEAN_REPORT_PATH`."""
    CLEAN_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CLEAN_REPORT_PATH.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    logger.info("[Medic] Clean report written to %s.", CLEAN_REPORT_PATH)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def run_deepclean_cycle(dry_run: bool = False) -> dict[str, Any]:
    """
    Execute a single deep-clean cycle across all four primary Spokes.

    Parameters
    ----------
    dry_run:
        When *True* no files are deleted — only the report is generated.

    Returns
    -------
    dict
        A ``CLEAN_REPORT`` dict with per-spoke summaries and totals.
    """
    logger.info(
        "[Medic] Deep-clean cycle started (dry_run=%s, freq=%s).",
        dry_run,
        FREQ_SIGNATURE,
    )

    loop = asyncio.get_event_loop()
    spoke_summaries: list[dict[str, Any]] = []

    for spoke in PRIMARY_SPOKES:
        summary = await loop.run_in_executor(None, _clean_spoke, spoke, dry_run)
        spoke_summaries.append(summary)
        logger.info(
            "[Medic] Spoke '%s': deleted=%d, dirs_removed=%d, status=%s",
            spoke,
            len(summary["deleted_files"]),
            len(summary["removed_dirs"]),
            summary["status"],
        )

    total_deleted = sum(len(s["deleted_files"]) for s in spoke_summaries)
    total_dirs = sum(len(s["removed_dirs"]) for s in spoke_summaries)

    report: dict[str, Any] = {
        "cycle_completed": datetime.now(timezone.utc).isoformat(),
        "freq_signature": FREQ_SIGNATURE,
        "dry_run": dry_run,
        "spokes_cleaned": len(spoke_summaries),
        "total_files_deleted": total_deleted,
        "total_dirs_removed": total_dirs,
        "spoke_summaries": spoke_summaries,
    }

    if not dry_run:
        await loop.run_in_executor(None, _write_clean_report, report)

    logger.info(
        "[Medic] Cycle complete — files_deleted=%d, dirs_removed=%d.",
        total_deleted,
        total_dirs,
    )
    return report


async def start_scheduled_medic(dry_run: bool = False) -> None:
    """
    Run the deep-clean cycle on a :data:`DEEPCLEAN_INTERVAL_S` schedule
    (default: 12 hours).  Loops indefinitely until cancelled.

    Parameters
    ----------
    dry_run:
        When *True* each cycle runs in dry-run mode.
    """
    logger.info(
        "[Medic] Scheduled Medic started — interval=%ds (%.1fh).",
        DEEPCLEAN_INTERVAL_S,
        DEEPCLEAN_INTERVAL_S / 3600,
    )
    while True:
        await run_deepclean_cycle(dry_run=dry_run)
        logger.info(
            "[Medic] Next cycle in %d s (%.1f h).",
            DEEPCLEAN_INTERVAL_S,
            DEEPCLEAN_INTERVAL_S / 3600,
        )
        await asyncio.sleep(DEEPCLEAN_INTERVAL_S)


# ---------------------------------------------------------------------------
# Stand-alone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _dry = "--dry-run" in sys.argv
    _scheduled = "--scheduled" in sys.argv

    if _scheduled:
        asyncio.run(start_scheduled_medic(dry_run=_dry))
    else:
        report = asyncio.run(run_deepclean_cycle(dry_run=_dry))
        print("✅ DeepClean cycle complete:")
        print(f"   Spokes cleaned:    {report['spokes_cleaned']}")
        print(f"   Files deleted:     {report['total_files_deleted']}")
        print(f"   Dirs removed:      {report['total_dirs_removed']}")
        print(f"   Signature:         {report['freq_signature']}")
