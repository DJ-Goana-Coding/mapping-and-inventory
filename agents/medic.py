"""
Medic — DeepClean Protocol
===========================
Python replacement for the legacy ``DeepClean.bat`` batch script.

Sweeps one or more target directories and removes low-value ephemeral files
(temporary files, compiled Python byte-code, download caches, log files, etc.)
to free disk space and keep storage nodes healthy.

Scheduling
----------
The :func:`schedule_deep_clean` coroutine runs the protocol on a recurring
interval (default 12 hours) across all configured primary spokes
(S10_Phalanx, Oppo_Omega, CGAL_Core, Pioneer).

Authentication / paths
----------------------
All target paths are supplied via the ``MEDIC_TARGETS`` environment variable
(path-separator-delimited list of absolute paths — ``:`` on Unix, ``;`` on
Windows, i.e. ``os.pathsep``) or passed directly to :func:`deep_clean`.
**No local Windows paths are hard-coded.**

Usage::

    import asyncio
    from agents.medic import schedule_deep_clean

    # Run the 12-hour recurring clean on all configured spokes.
    asyncio.run(schedule_deep_clean())
"""
from __future__ import annotations

import asyncio
import logging
import os
import pathlib
import shutil
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Files / directories that are always safe to remove
# ---------------------------------------------------------------------------

_EPHEMERAL_EXTENSIONS: frozenset[str] = frozenset(
    {".tmp", ".temp", ".log", ".bak", ".old", ".pyc", ".pyo"}
)

_EPHEMERAL_DIR_NAMES: frozenset[str] = frozenset(
    {"__pycache__", ".cache", "tmp", "temp", "Temp", ".pytest_cache", ".mypy_cache"}
)

# Default interval between deep-clean cycles (seconds)
DEFAULT_INTERVAL_S: int = 12 * 60 * 60  # 12 hours

# ---------------------------------------------------------------------------
# Primary spoke identifiers — paths are resolved from the environment
# ---------------------------------------------------------------------------

PRIMARY_SPOKES: list[str] = ["S10_Phalanx", "Oppo_Omega", "CGAL_Core", "Pioneer"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_targets() -> list[pathlib.Path]:
    """
    Resolve the list of target directories from the ``MEDIC_TARGETS``
    environment variable (colon-separated absolute paths).

    Falls back to an empty list if the variable is not set, so the caller
    must supply paths explicitly or the clean run is a no-op.
    """
    raw = os.environ.get("MEDIC_TARGETS", "")
    targets: list[pathlib.Path] = []
    for part in raw.split(os.pathsep):  # os.pathsep: ':' on Unix, ';' on Windows
        part = part.strip()
        if part:
            target_path = pathlib.Path(part)
            if target_path.exists():
                targets.append(target_path)
            else:
                logger.warning("[Medic] Target path not found, skipping: %s", target_path)
    return targets


def _sweep(target: pathlib.Path, dry_run: bool) -> dict[str, Any]:
    """
    Sweep *target* and remove ephemeral files / directories.

    Returns a summary dict with ``removed_files``, ``removed_dirs``,
    and ``freed_bytes``.
    """
    removed_files: list[str] = []
    removed_dirs: list[str] = []
    freed_bytes: int = 0

    for dirpath, dirnames, filenames in os.walk(target, topdown=False):
        dp = pathlib.Path(dirpath)

        # Remove ephemeral directory trees (e.g. __pycache__)
        for dname in list(dirnames):
            if dname in _EPHEMERAL_DIR_NAMES:
                full_dir = dp / dname
                try:
                    size = sum(
                        f.stat().st_size
                        for f in full_dir.rglob("*")
                        if f.is_file()
                    )
                    if not dry_run:
                        shutil.rmtree(full_dir, ignore_errors=True)
                    removed_dirs.append(str(full_dir))
                    freed_bytes += size
                    logger.info("[Medic] Removed dir: %s (%d bytes)", full_dir, size)
                except OSError as exc:
                    logger.warning("[Medic] Could not remove dir '%s': %s", full_dir, exc)

        # Remove ephemeral files
        for fname in filenames:
            fpath = dp / fname
            if fpath.suffix.lower() in _EPHEMERAL_EXTENSIONS:
                try:
                    size = fpath.stat().st_size
                    if not dry_run:
                        fpath.unlink()
                    removed_files.append(str(fpath))
                    freed_bytes += size
                    logger.info("[Medic] Removed file: %s (%d bytes)", fpath, size)
                except OSError as exc:
                    logger.warning(
                        "[Medic] Could not remove file '%s': %s", fpath, exc
                    )

    return {
        "removed_files": removed_files,
        "removed_dirs": removed_dirs,
        "freed_bytes": freed_bytes,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def deep_clean(
    targets: list[str | pathlib.Path] | None = None,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Run the DeepClean protocol against *targets*.

    Parameters
    ----------
    targets:
        List of directories to sweep.  When ``None``, the list is resolved
        from the ``MEDIC_TARGETS`` environment variable.
    dry_run:
        When ``True``, log what *would* be removed without deleting anything.

    Returns
    -------
    dict
        Aggregated summary with ``targets_swept``, ``total_removed_files``,
        ``total_removed_dirs``, and ``total_freed_bytes``.
    """
    if targets is None:
        resolved = _resolve_targets()
    else:
        resolved = [pathlib.Path(t) for t in targets]

    if not resolved:
        logger.info("[Medic] No targets configured — deep_clean is a no-op.")
        return {
            "targets_swept": 0,
            "total_removed_files": 0,
            "total_removed_dirs": 0,
            "total_freed_bytes": 0,
        }

    logger.info(
        "[Medic] DeepClean starting on %d target(s) (dry_run=%s).",
        len(resolved),
        dry_run,
    )

    loop = asyncio.get_event_loop()
    all_removed_files: list[str] = []
    all_removed_dirs: list[str] = []
    total_freed = 0

    for target in resolved:
        summary = await loop.run_in_executor(None, _sweep, target, dry_run)
        all_removed_files.extend(summary["removed_files"])
        all_removed_dirs.extend(summary["removed_dirs"])
        total_freed += summary["freed_bytes"]

    result: dict[str, Any] = {
        "targets_swept": len(resolved),
        "total_removed_files": len(all_removed_files),
        "total_removed_dirs": len(all_removed_dirs),
        "total_freed_bytes": total_freed,
    }
    logger.info(
        "[Medic] DeepClean complete — files=%d, dirs=%d, freed=%d bytes.",
        result["total_removed_files"],
        result["total_removed_dirs"],
        result["total_freed_bytes"],
    )
    return result


async def schedule_deep_clean(
    targets: list[str | pathlib.Path] | None = None,
    interval_s: int = DEFAULT_INTERVAL_S,
    *,
    dry_run: bool = False,
) -> None:
    """
    Run :func:`deep_clean` on a recurring *interval_s* schedule.

    Runs immediately on first invocation, then sleeps for *interval_s*
    seconds before repeating.  The loop runs indefinitely until cancelled.

    Parameters
    ----------
    targets:
        Directories to sweep.  Defaults to ``MEDIC_TARGETS`` env-var list.
    interval_s:
        Seconds between clean cycles.  Defaults to 43 200 (12 hours).
    dry_run:
        Forward to :func:`deep_clean`.
    """
    spoke_count = len(PRIMARY_SPOKES)
    logger.info(
        "[Medic] Scheduler started — interval=%ds, spokes=%d (%s).",
        interval_s,
        spoke_count,
        ", ".join(PRIMARY_SPOKES),
    )
    while True:
        try:
            await deep_clean(targets=targets, dry_run=dry_run)
        except Exception as exc:
            logger.error("[Medic] DeepClean cycle failed: %s", exc)
        await asyncio.sleep(interval_s)


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _dry = "--dry-run" in sys.argv
    _targets = [a for a in sys.argv[1:] if not a.startswith("--")] or None
    asyncio.run(deep_clean(targets=_targets, dry_run=_dry))
