"""
core/district_1_4_bridge.py — Asynchronous D01→D04 Routing Pipeline
=====================================================================
Connects the 'Muscle' (District 01 — COMMAND_INPUT) to the 'Memory'
(District 04 — OUTPUT_HARVEST).

When the Pioneer Vanguard engine executes a trade, pulls a model down,
or any other command fires in D01, this bridge:

1. Computes the SHA-256 hash of the command payload.
2. Captures the exact UTC timestamp of the event.
3. Derives the human-readable 'Meaning' of the action.
4. Dispatches a :class:`BridgeEvent` to the D04 archiver asynchronously,
   without blocking the trading-engine's event loop.
5. Optionally indexes the event into the brain vault with the
   ``district_loop: 01_to_04`` metadata tag.

Constraint: This module does NOT modify ``vortex_bible.py`` logic.  It is
            a pure routing and logging operation.

Performance: All D04 I/O is dispatched via ``asyncio.get_event_loop().
             run_in_executor(None, ...)`` so file writes never introduce
             latency on the hot path of the trading engine.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any

from nodes.District_04_OUTPUT_HARVEST.archiver import HarvestRecord, append_harvest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DISTRICT_LOOP_TAG: str = "01_to_04"
_FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

# Source label prefix used when events are indexed into the brain vault.
# The indexer detects this prefix to apply the district_loop tag automatically.
BRIDGE_SOURCE_PREFIX: str = "district_1_4_bridge::"


# ---------------------------------------------------------------------------
# Bridge event dataclass
# ---------------------------------------------------------------------------


class BridgeEvent:
    """
    A routed event flowing from District 01 to District 04.

    Parameters
    ----------
    payload:
        The raw command payload dict from D01.
    command_type:
        ``"SIS"`` or ``"START_HARVEST"`` as classified by the D01 watcher.
    source_file:
        Filename of the originating command file in District 01.
    meaning:
        Optional human-readable description supplied by the caller.
        When omitted the bridge derives a best-effort description from
        the payload keys.
    """

    __slots__ = (
        "payload",
        "command_type",
        "source_file",
        "meaning",
        "sha256_hash",
        "timestamp",
    )

    def __init__(
        self,
        payload: dict[str, Any],
        command_type: str = "SIS",
        source_file: str = "",
        meaning: str = "",
    ) -> None:
        self.payload = payload
        self.command_type = command_type
        self.source_file = source_file
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.sha256_hash = _hash_payload(payload)
        self.meaning = meaning or _derive_meaning(payload, command_type)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _hash_payload(payload: dict[str, Any]) -> str:
    """Return the SHA-256 hex digest of the canonical JSON representation of *payload*."""
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _derive_meaning(payload: dict[str, Any], command_type: str) -> str:
    """
    Best-effort extraction of a human-readable 'Meaning' from *payload*.

    Checks common payload keys used across the Pioneer Vanguard and
    Gemini Live bridges.
    """
    for key in ("meaning", "action", "command", "directive", "symbol", "model", "task"):
        val = payload.get(key)
        if val:
            return str(val)
    if command_type == "START_HARVEST":
        return "Harvest cycle triggered"
    return f"D01 command — keys: {', '.join(list(payload.keys())[:4])}"


def _to_harvest_record(event: BridgeEvent) -> HarvestRecord:
    """Convert a :class:`BridgeEvent` into a :class:`HarvestRecord` for D04."""
    return HarvestRecord(
        sha256_hash=event.sha256_hash,
        timestamp=event.timestamp,
        meaning=event.meaning,
        command_type=event.command_type,
        source_file=event.source_file,
    )


# ---------------------------------------------------------------------------
# Public async API
# ---------------------------------------------------------------------------


async def route_to_d04(event: BridgeEvent) -> None:
    """
    Asynchronously route *event* from D01 to D04.

    The D04 file I/O (append to TXT + CSV) is dispatched to a thread-pool
    executor so it does not block the event loop, preserving trading-engine
    latency guarantees.

    Parameters
    ----------
    event:
        The :class:`BridgeEvent` to log.
    """
    record = _to_harvest_record(event)
    loop = asyncio.get_running_loop()

    logger.info(
        "[D1→D4 Bridge] ⚡ Routing event | type=%s | hash=%s | meaning=%s",
        event.command_type,
        event.sha256_hash[:12],
        event.meaning,
    )

    # Offload blocking file I/O to thread pool — zero latency impact on caller.
    await loop.run_in_executor(None, append_harvest, record)

    logger.debug(
        "[D1→D4 Bridge] ✅ Event committed to D04 vault | hash=%s",
        event.sha256_hash[:12],
    )


async def dispatch(
    payload: dict[str, Any],
    *,
    command_type: str = "SIS",
    source_file: str = "",
    meaning: str = "",
) -> BridgeEvent:
    """
    Convenience wrapper: build a :class:`BridgeEvent` and route it to D04.

    This is the primary entry-point for the Pioneer Vanguard engine and
    any other D01 consumer.

    Parameters
    ----------
    payload:
        Raw command payload dict.
    command_type:
        ``"SIS"`` or ``"START_HARVEST"``.
    source_file:
        Filename of the originating command file.
    meaning:
        Human-readable description of the action.  If omitted the bridge
        derives it automatically from *payload*.

    Returns
    -------
    BridgeEvent
        The event that was created and dispatched, including its computed
        SHA-256 hash and timestamp.
    """
    event = BridgeEvent(
        payload=payload,
        command_type=command_type,
        source_file=source_file,
        meaning=meaning,
    )
    await route_to_d04(event)
    return event
