"""
AION Probe — Trans-Dimensional Sector Mapper (District 12 / ORACLE_ETHICS)
==========================================================================
The AION Probe scans target data directories for 'Quantum Lords' and
'TransDimensional Entities' lore, mathematical frameworks, and quantum
theory documents, then ingests them into the District 12 (ORACLE_ETHICS)
library as the 'Universal Knowledge' baseline for the AI fleet.

Target source path
------------------
``E:\\RECOVERY_STAGING\\...\\BIG DOOFY LAND STORY MAIN FOLDER\\``
(and all sub-directories containing lore, math, or quantum theory data.)

Destination
-----------
District 12 brain-vault partition: ``12_ORACLE_ETHICS``

Usage::

    import asyncio
    from brain.aion_probe import run_probe

    asyncio.run(run_probe(source_dir="E:/RECOVERY_STAGING"))
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
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"
TARGET_DISTRICT: str = "12_ORACLE_ETHICS"

_REPO_ROOT: pathlib.Path = pathlib.Path(__file__).parent.parent

# Supported lore / knowledge file extensions the probe will ingest
_LORE_EXTENSIONS: tuple[str, ...] = (
    ".txt", ".md", ".json", ".pdf", ".docx", ".doc", ".rtf", ".csv"
)

# Keywords that identify Quantum Lords / TransDimensional lore folders
_LORE_KEYWORDS: tuple[str, ...] = (
    "quantum",
    "lords",
    "transdimensional",
    "trans-dimensional",
    "trans_dimensional",
    "aion",
    "lore",
    "story",
    "big doofy",
    "universal knowledge",
    "entities",
)

# Knowledge saturation state file — written to the repo so the HUD can read it
SATURATION_STATE_PATH: pathlib.Path = (
    _REPO_ROOT / "spark_ui" / "knowledge_saturation.json"
)


# ---------------------------------------------------------------------------
# Lore discovery helpers
# ---------------------------------------------------------------------------


def _is_lore_path(path: pathlib.Path) -> bool:
    """Return True if *path* name/parent contains any lore keyword."""
    check = (path.name + " " + str(path)).lower()
    return any(kw in check for kw in _LORE_KEYWORDS)


def _discover_lore_files(source_dir: pathlib.Path) -> list[pathlib.Path]:
    """
    Recursively walk *source_dir* and return all files whose path contains a
    lore keyword and whose extension is in :data:`_LORE_EXTENSIONS`.
    """
    found: list[pathlib.Path] = []
    try:
        for candidate in source_dir.rglob("*"):
            if (
                candidate.is_file()
                and candidate.suffix.lower() in _LORE_EXTENSIONS
                and _is_lore_path(candidate)
            ):
                found.append(candidate)
    except PermissionError as exc:
        logger.warning("[AION] Permission denied scanning %s: %s", source_dir, exc)
    return found


# ---------------------------------------------------------------------------
# Saturation state helpers
# ---------------------------------------------------------------------------


def _load_saturation_state() -> dict[str, Any]:
    """Load the current knowledge saturation state, or return an empty scaffold."""
    if SATURATION_STATE_PATH.exists():
        try:
            with SATURATION_STATE_PATH.open(encoding="utf-8") as fh:
                return json.load(fh)
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "district": TARGET_DISTRICT,
        "total_lore_files_discovered": 0,
        "total_chunks_indexed": 0,
        "saturation_pct": 0.0,
        "last_probe_run": None,
        "freq_signature": FREQ_SIGNATURE,
    }


def _save_saturation_state(state: dict[str, Any]) -> None:
    """Persist the saturation state to :data:`SATURATION_STATE_PATH`."""
    SATURATION_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with SATURATION_STATE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, indent=2)
    logger.info("[AION] Saturation state saved to %s.", SATURATION_STATE_PATH)


# ---------------------------------------------------------------------------
# Brain-vault ingestion helper
# ---------------------------------------------------------------------------


def _ingest_file_to_vault(filepath: pathlib.Path) -> int:
    """
    Attempt to index *filepath* into the brain vault under the
    ``12_ORACLE_ETHICS`` district label.

    Returns the number of chunks indexed (0 if ingestion was skipped or
    failed).
    """
    try:
        from brain.indexer import get_collection, index_directory  # type: ignore

        col = get_collection()
        chunks = index_directory(col, filepath.parent)
        return chunks
    except Exception as exc:
        logger.debug(
            "[AION] Could not index '%s' into vault: %s", filepath.name, exc
        )
        return 0


# ---------------------------------------------------------------------------
# Main probe coroutine
# ---------------------------------------------------------------------------


async def run_probe(
    source_dir: str | pathlib.Path = "E:/RECOVERY_STAGING",
    dry_run: bool = False,
) -> dict[str, Any]:
    """
    Run the AION Probe over *source_dir*.

    The probe:

    1. Discovers all lore / quantum-theory files in *source_dir*.
    2. Ingests each file into the District 12 brain-vault partition.
    3. Updates the knowledge saturation state JSON for the HUD.

    Parameters
    ----------
    source_dir:
        Root directory to scan — typically ``E:/RECOVERY_STAGING`` or the
        'BIG DOOFY LAND STORY MAIN FOLDER' path.
    dry_run:
        When *True* discovery runs but no files are indexed and no state is
        written.

    Returns
    -------
    dict
        A summary with keys ``files_discovered``, ``chunks_indexed``,
        ``saturation_pct``, and ``freq_signature``.
    """
    source = pathlib.Path(source_dir)
    logger.info(
        "[AION] Probe initiated — source=%s, district=%s, dry_run=%s",
        source,
        TARGET_DISTRICT,
        dry_run,
    )

    # Discovery phase (run in executor to stay non-blocking)
    loop = asyncio.get_event_loop()
    lore_files: list[pathlib.Path] = await loop.run_in_executor(
        None, _discover_lore_files, source
    )

    logger.info("[AION] Discovered %d lore file(s).", len(lore_files))

    total_chunks = 0
    if not dry_run:
        for lf in lore_files:
            chunks = await loop.run_in_executor(None, _ingest_file_to_vault, lf)
            total_chunks += chunks

    # Update saturation state
    state = _load_saturation_state()
    state["total_lore_files_discovered"] = len(lore_files)
    state["total_chunks_indexed"] = (
        state.get("total_chunks_indexed", 0) + total_chunks
    )
    # Saturation percentage is a rough gauge: 1 % per 10 indexed chunks, capped at 100 %
    state["saturation_pct"] = min(
        100.0, round(state["total_chunks_indexed"] / 10.0, 2)
    )
    state["last_probe_run"] = datetime.now(timezone.utc).isoformat()
    state["freq_signature"] = FREQ_SIGNATURE

    if not dry_run:
        await loop.run_in_executor(None, _save_saturation_state, state)

    summary: dict[str, Any] = {
        "files_discovered": len(lore_files),
        "chunks_indexed": total_chunks,
        "saturation_pct": state["saturation_pct"],
        "freq_signature": FREQ_SIGNATURE,
    }

    logger.info(
        "[AION] Probe complete — files=%d, chunks=%d, saturation=%.1f%%",
        summary["files_discovered"],
        summary["chunks_indexed"],
        summary["saturation_pct"],
    )
    return summary


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

    _source = sys.argv[1] if len(sys.argv) > 1 else "E:/RECOVERY_STAGING"
    _dry = "--dry-run" in sys.argv

    result = asyncio.run(run_probe(source_dir=_source, dry_run=_dry))
    print("✅ AION Probe complete:")
    print(f"   Files discovered:  {result['files_discovered']}")
    print(f"   Chunks indexed:    {result['chunks_indexed']}")
    print(f"   Saturation:        {result['saturation_pct']:.1f}%")
    print(f"   Signature:         {result['freq_signature']}")
