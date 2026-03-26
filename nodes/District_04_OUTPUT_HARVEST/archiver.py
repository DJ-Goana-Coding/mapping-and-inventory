"""
nodes/District_04_OUTPUT_HARVEST/archiver.py — Permanent Memory Core
=====================================================================
Automates the Librarian's permanent memory core for District 04.

Whenever the D01→D04 bridge delivers a telemetry record, this module
formats the record and appends it to two sovereign log files kept in
this district:

* ``TOTAL_CITADEL_MAP.txt``  — human-readable append-only ledger
* ``MASTER_SYSTEM_MAP.csv``  — machine-readable telemetry archive

Constraint: This module is append-only.  It never overwrites existing
            log entries (Zero-Overwrite constraint).
"""
from __future__ import annotations

import csv
import io
import logging
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_D04_ROOT = pathlib.Path(__file__).parent

TOTAL_CITADEL_MAP: pathlib.Path = _D04_ROOT / "TOTAL_CITADEL_MAP.txt"
MASTER_SYSTEM_MAP: pathlib.Path = _D04_ROOT / "MASTER_SYSTEM_MAP.csv"

# ---------------------------------------------------------------------------
# CSV header (written once when the file is first created)
# ---------------------------------------------------------------------------
_CSV_HEADER: list[str] = [
    "timestamp",
    "sha256_hash",
    "command_type",
    "source_file",
    "meaning",
    "district_loop",
    "freq_signature",
]

_FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"
_DISTRICT_LOOP: str = "01_to_04"

# ---------------------------------------------------------------------------
# Telemetry record dataclass
# ---------------------------------------------------------------------------


class HarvestRecord:
    """
    A single telemetry record produced by the D01→D04 bridge.

    Parameters
    ----------
    sha256_hash:
        Hex digest of the originating command payload.
    timestamp:
        ISO-8601 UTC string at the moment of capture.
    meaning:
        Human-readable description of the action (e.g. trade symbol / model).
    command_type:
        ``"SIS"`` or ``"START_HARVEST"`` as classified by the D01 watcher.
    source_file:
        Filename of the originating command file in District 01.
    """

    __slots__ = ("sha256_hash", "timestamp", "meaning", "command_type", "source_file")

    def __init__(
        self,
        sha256_hash: str,
        timestamp: str,
        meaning: str,
        command_type: str = "SIS",
        source_file: str = "",
    ) -> None:
        self.sha256_hash = sha256_hash
        self.timestamp = timestamp
        self.meaning = meaning
        self.command_type = command_type
        self.source_file = source_file


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _ensure_csv_header() -> None:
    """Write the CSV header row if ``MASTER_SYSTEM_MAP.csv`` does not exist."""
    if MASTER_SYSTEM_MAP.exists():
        return
    with MASTER_SYSTEM_MAP.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(_CSV_HEADER)
    logger.info("[D04 Archiver] Created MASTER_SYSTEM_MAP.csv with header.")


def _format_txt_entry(record: HarvestRecord) -> str:
    """Return a formatted, human-readable log line for the TXT ledger."""
    return (
        f"[{record.timestamp}] "
        f"HASH={record.sha256_hash} | "
        f"TYPE={record.command_type} | "
        f"MEANING={record.meaning} | "
        f"SOURCE={record.source_file} | "
        f"LOOP={_DISTRICT_LOOP} | "
        f"FREQ={_FREQ_SIGNATURE}\n"
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def append_harvest(record: HarvestRecord) -> None:
    """
    Append *record* to both sovereign log files.

    This is a synchronous, atomic append operation.  Callers should call
    this from a thread-pool executor when used inside an async context so
    that file I/O does not block the event loop.

    Parameters
    ----------
    record:
        The :class:`HarvestRecord` to persist.
    """
    # --- 1. Human-readable ledger ---
    entry_txt = _format_txt_entry(record)
    try:
        with TOTAL_CITADEL_MAP.open("a", encoding="utf-8") as fh:
            fh.write(entry_txt)
        logger.info(
            "[D04 Archiver] 📝 Appended to TOTAL_CITADEL_MAP.txt | hash=%s",
            record.sha256_hash[:12],
        )
    except OSError as exc:
        logger.error("[D04 Archiver] Failed to write TOTAL_CITADEL_MAP.txt: %s", exc)

    # --- 2. Machine-readable CSV archive ---
    _ensure_csv_header()
    row: list[Any] = [
        record.timestamp,
        record.sha256_hash,
        record.command_type,
        record.source_file,
        record.meaning,
        _DISTRICT_LOOP,
        _FREQ_SIGNATURE,
    ]
    try:
        with MASTER_SYSTEM_MAP.open("a", newline="", encoding="utf-8") as fh:
            csv.writer(fh).writerow(row)
        logger.info(
            "[D04 Archiver] 📊 Appended to MASTER_SYSTEM_MAP.csv | hash=%s",
            record.sha256_hash[:12],
        )
    except OSError as exc:
        logger.error("[D04 Archiver] Failed to write MASTER_SYSTEM_MAP.csv: %s", exc)


def read_harvest_log(n: int = 50) -> list[str]:
    """
    Return the last *n* lines from ``TOTAL_CITADEL_MAP.txt``.

    Useful for health-check and telemetry endpoints.
    """
    if not TOTAL_CITADEL_MAP.exists():
        return []
    lines = TOTAL_CITADEL_MAP.read_text(encoding="utf-8").splitlines()
    return lines[-n:]


def harvest_count() -> int:
    """Return the total number of harvest records stored in the CSV archive."""
    if not MASTER_SYSTEM_MAP.exists():
        return 0
    # Subtract 1 for the header row
    line_count = sum(1 for _ in MASTER_SYSTEM_MAP.open(encoding="utf-8")) - 1
    return max(line_count, 0)
