"""
Harvester — Drive Scanner Module (Python Module)
================================================
Python replacement for the legacy ``Harvester_Drive_Scanner.bat`` batch script.

Scans all configured drive paths for new assets (models, datasets, code,
lore) and feeds discovered file metadata into the fleet's brain vault for
continuous 'Forever Learning'.

Scan targets
------------
* ``C:\\Citadel\\`` — primary Citadel directory (code + models)
* ``C:\\tools\\``   — tooling binaries
* ``E:\\``          — 2.5 TB lore archive (RECOVERY_STAGING)

Output
------
Each scan cycle produces a structured JSON harvest report and appends any
newly discovered file records to ``Master_Harvest_Log.json`` in the repo
root.  Paths containing local Windows usernames are automatically scrubbed by
:mod:`utils.sanitizer` (No-Lemon protocol) before any cloud mirroring.

Usage::

    import asyncio
    from tasks.harvester import run_harvest_cycle, start_scheduled_harvester

    # Single run:
    asyncio.run(run_harvest_cycle())
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

HARVEST_INTERVAL_S: int = int(os.getenv("HARVEST_INTERVAL_S", str(6 * 3600)))  # 6 h

_REPO_ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent

# Harvest log path
HARVEST_LOG_PATH: pathlib.Path = _REPO_ROOT / "Master_Harvest_Log.json"

# File extensions to harvest (excluding binary model files to stay bandwidth-safe)
_HARVEST_EXTENSIONS: tuple[str, ...] = (
    ".py", ".json", ".md", ".txt", ".yaml", ".yml", ".csv",
    ".gguf", ".onnx", ".bin", ".safetensors",
)

# Scan root directories — these are Windows paths; adjust for the local machine
# environment.  On non-Windows systems the scanner skips paths that do not exist.
SCAN_ROOTS: list[str] = [
    os.getenv("HARVEST_ROOT_CITADEL", r"C:\Citadel"),
    os.getenv("HARVEST_ROOT_TOOLS", r"C:\tools"),
    os.getenv("HARVEST_ROOT_LORE", r"E:\RECOVERY_STAGING"),
]

# Keyword patterns that flag a file as a model asset
_MODEL_KEYWORDS: tuple[str, ...] = (
    "model", "quant", "gguf", "onnx", "safetensors", "llama",
    "mistral", "deepseek", "nomic", "embed",
)


# ---------------------------------------------------------------------------
# Scan helpers
# ---------------------------------------------------------------------------


def _classify_file(filepath: pathlib.Path) -> str:
    """Return a coarse asset-type label for *filepath*."""
    name_lower = filepath.name.lower()
    if any(kw in name_lower for kw in _MODEL_KEYWORDS):
        return "model"
    suffix = filepath.suffix.lower()
    if suffix in (".py",):
        return "code"
    if suffix in (".json", ".yaml", ".yml"):
        return "config"
    if suffix in (".md", ".txt", ".csv"):
        return "lore"
    return "asset"


def _scan_root(root: str) -> list[dict[str, Any]]:
    """
    Walk *root* and return a list of file-record dicts for all matching files.

    Paths are scrubbed via :func:`utils.sanitizer.sanitize_path` before being
    stored in any record.
    """
    from utils.sanitizer import sanitize_path  # type: ignore

    root_path = pathlib.Path(root)
    if not root_path.exists():
        logger.debug("[Harvester] Scan root does not exist, skipping: %s", root)
        return []

    records: list[dict[str, Any]] = []
    try:
        for filepath in root_path.rglob("*"):
            if not filepath.is_file():
                continue
            if filepath.suffix.lower() not in _HARVEST_EXTENSIONS:
                continue
            try:
                stat = filepath.stat()
                records.append(
                    {
                        "FullName": sanitize_path(str(filepath)),
                        "Length": stat.st_size,
                        "LastWriteTime": datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat(),
                        "asset_type": _classify_file(filepath),
                        "scan_root": sanitize_path(root),
                        "freq_signature": FREQ_SIGNATURE,
                    }
                )
            except OSError as exc:
                logger.debug("[Harvester] Stat error for '%s': %s", filepath, exc)
    except PermissionError as exc:
        logger.warning("[Harvester] Permission denied at '%s': %s", root, exc)

    return records


def _load_harvest_log() -> dict[str, Any]:
    """Load the existing harvest log JSON, or return an empty scaffold."""
    if HARVEST_LOG_PATH.exists():
        try:
            with HARVEST_LOG_PATH.open(encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {"records": [], "total_harvested": 0, "last_harvest": None}


def _save_harvest_log(log: dict[str, Any]) -> None:
    """Persist the harvest log to :data:`HARVEST_LOG_PATH`."""
    HARVEST_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with HARVEST_LOG_PATH.open("w", encoding="utf-8") as fh:
        json.dump(log, fh, indent=2, default=str)
    logger.info("[Harvester] Harvest log saved — total records: %d.", log["total_harvested"])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def run_harvest_cycle(
    scan_roots: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Execute a single harvest cycle across all configured scan roots.

    Parameters
    ----------
    scan_roots:
        Override the default :data:`SCAN_ROOTS`.  Useful for testing.
    dry_run:
        When *True* the harvest log is not written to disk.

    Returns
    -------
    dict
        A harvest summary with ``new_records``, ``total_records``,
        ``last_harvest``, and ``freq_signature``.
    """
    roots = scan_roots if scan_roots is not None else SCAN_ROOTS
    logger.info(
        "[Harvester] Harvest cycle started — roots=%d, dry_run=%s, freq=%s",
        len(roots),
        dry_run,
        FREQ_SIGNATURE,
    )

    loop = asyncio.get_event_loop()
    all_new_records: list[dict[str, Any]] = []

    for root in roots:
        records = await loop.run_in_executor(None, _scan_root, root)
        all_new_records.extend(records)
        logger.info("[Harvester] Root '%s' → %d file(s) found.", root, len(records))

    log = _load_harvest_log()
    existing_paths: set[str] = {r.get("FullName", "") for r in log["records"]}

    new_entries = [r for r in all_new_records if r["FullName"] not in existing_paths]
    log["records"].extend(new_entries)
    log["total_harvested"] = len(log["records"])
    log["last_harvest"] = datetime.now(timezone.utc).isoformat()

    if not dry_run and new_entries:
        await loop.run_in_executor(None, _save_harvest_log, log)

    summary: dict[str, Any] = {
        "new_records": len(new_entries),
        "total_records": log["total_harvested"],
        "last_harvest": log["last_harvest"],
        "freq_signature": FREQ_SIGNATURE,
    }

    logger.info(
        "[Harvester] Cycle complete — new=%d, total=%d.",
        summary["new_records"],
        summary["total_records"],
    )
    return summary


async def start_scheduled_harvester(
    scan_roots: list[str] | None = None,
    dry_run: bool = False,
) -> None:
    """
    Run harvest cycles on a :data:`HARVEST_INTERVAL_S` schedule (default: 6 h).
    Loops indefinitely until cancelled.
    """
    logger.info(
        "[Harvester] Scheduled Harvester started — interval=%ds (%.1fh).",
        HARVEST_INTERVAL_S,
        HARVEST_INTERVAL_S / 3600,
    )
    while True:
        await run_harvest_cycle(scan_roots=scan_roots, dry_run=dry_run)
        logger.info(
            "[Harvester] Next cycle in %d s (%.1f h).",
            HARVEST_INTERVAL_S,
            HARVEST_INTERVAL_S / 3600,
        )
        await asyncio.sleep(HARVEST_INTERVAL_S)


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
        asyncio.run(start_scheduled_harvester(dry_run=_dry))
    else:
        result = asyncio.run(run_harvest_cycle(dry_run=_dry))
        print("✅ Harvest cycle complete:")
        print(f"   New records:   {result['new_records']}")
        print(f"   Total records: {result['total_records']}")
        print(f"   Signature:     {result['freq_signature']}")
