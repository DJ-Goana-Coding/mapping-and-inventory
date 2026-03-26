"""
nodes/District_01_COMMAND_INPUT/watcher.py — Live Ingestion Watcher
====================================================================
Monitors District 01 for incoming Symbolic Instruction Sets (SIS) and
``!: START_HARVEST`` trigger files originating from the S10 Phalanx or
Gemini Live bridges.

Zero-Trust Lock
---------------
Every execution command must carry a valid HMAC-SHA256 signature produced
by the Commander (``AEGIS_COMMANDER_TOKEN``) or T.I.A. (``TIA_AUTH_TOKEN``).
Commands that fail signature verification are silently dropped and logged to
``SECURITY_ALERTS.log`` — they are never executed.

Constraint: This module does NOT modify VortexBerserker logic.  It strictly
            watches and routes — it never executes trade logic directly.
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import logging
import os
import pathlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
_D01_ROOT = pathlib.Path(__file__).parent
_REPO_ROOT = _D01_ROOT.parent.parent
_SECURITY_LOG: pathlib.Path = _REPO_ROOT / "SECURITY_ALERTS.log"

# ---------------------------------------------------------------------------
# Recognised trigger / instruction-set patterns
# ---------------------------------------------------------------------------
#: File suffix patterns that identify a Symbolic Instruction Set.
_SIS_SUFFIXES: tuple[str, ...] = (".sis", ".json", ".txt", ".yml", ".yaml")

#: Stem / content keyword that marks an emergency harvest trigger.
_HARVEST_TRIGGER_STEM: str = "START_HARVEST"
_HARVEST_TRIGGER_CONTENT: str = "!: START_HARVEST"

# Poll interval when the asyncio filesystem event loop is used as a fallback.
_POLL_INTERVAL_SECONDS: float = float(os.environ.get("D01_POLL_INTERVAL", "2.0"))


# ---------------------------------------------------------------------------
# Signature verification — Zero-Trust Lock
# ---------------------------------------------------------------------------


def _verify_signature(payload: dict[str, Any]) -> bool:
    """
    Return *True* if *payload* carries a valid SHA-256 signature produced
    by the Commander or T.I.A.

    A payload must include both ``"timestamp"`` (Unix epoch float/int) and
    ``"signature"`` (hex string) fields.  The expected signature is computed
    as::

        SHA256(token + str(timestamp))

    where *token* is either ``AEGIS_COMMANDER_TOKEN`` or ``TIA_AUTH_TOKEN``.
    This matches the existing sovereign-sync signature scheme used in
    ``bridge_protocol.py`` and ``check_panic_signal()``.
    """
    timestamp = payload.get("timestamp")
    signature = payload.get("signature")
    if timestamp is None or not signature:
        return False

    for env_key in ("AEGIS_COMMANDER_TOKEN", "TIA_AUTH_TOKEN"):
        token = os.environ.get(env_key)
        if not token:
            continue
        expected = hashlib.sha256(
            f"{token}{timestamp}".encode()
        ).hexdigest()
        if signature == expected:
            return True
    return False


def _log_zero_trust_rejection(path: pathlib.Path, reason: str) -> None:
    """Append a zero-trust rejection event to the security audit log."""
    entry = (
        f"[{datetime.now(timezone.utc).isoformat()}] "
        f"ZERO_TRUST_REJECTION | file={path.name} | reason={reason}\n"
    )
    try:
        with _SECURITY_LOG.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        logger.error("Could not write to SECURITY_ALERTS.log: %s", exc)
    logger.warning("Zero-Trust Lock rejected command from '%s': %s", path.name, reason)


# ---------------------------------------------------------------------------
# Payload loading
# ---------------------------------------------------------------------------


def _load_payload(path: pathlib.Path) -> dict[str, Any] | None:
    """
    Attempt to parse *path* as a JSON payload.

    For plain-text trigger files (containing ``!: START_HARVEST``) a minimal
    synthetic payload dict is returned so the standard verification flow still
    applies.

    Returns ``None`` when the file cannot be parsed or the content does not
    match any recognised pattern.
    """
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.debug("D01 Watcher: could not read '%s': %s", path, exc)
        return None

    # JSON-based SIS or trigger file
    if path.suffix in (".json",):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.debug("D01 Watcher: '%s' is not valid JSON.", path.name)
            return None

    # Plain-text harvest trigger
    if _HARVEST_TRIGGER_CONTENT in raw or _HARVEST_TRIGGER_STEM in path.stem.upper():
        # Expect at least timestamp + signature fields somewhere in the file.
        # Try line-by-line JSON extraction as a convenience format:
        #   {"timestamp": 1234567890, "signature": "abc..."}
        for line in raw.splitlines():
            stripped = line.strip()
            if stripped.startswith("{") and stripped.endswith("}"):
                try:
                    return json.loads(stripped)
                except json.JSONDecodeError:
                    continue
        # No parseable auth line found — treat entire file as unsigned.
        return None

    # Unrecognised plain-text file
    return None


# ---------------------------------------------------------------------------
# Command dataclass
# ---------------------------------------------------------------------------


@dataclass
class Command:
    """A validated, signed command sourced from District 01."""

    source_file: str
    payload: dict[str, Any]
    command_type: str  # "SIS" | "START_HARVEST"
    received_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Watcher
# ---------------------------------------------------------------------------


class D01Watcher:
    """
    Live-ingestion watcher for District 01 (COMMAND_INPUT).

    Monitors *watch_dir* for new files.  Valid, signed commands are dispatched
    to all registered handlers via :meth:`add_handler`.  Invalid or unsigned
    commands are rejected and logged.

    Usage::

        watcher = D01Watcher()
        watcher.add_handler(my_async_handler)
        await watcher.run()
    """

    def __init__(self, watch_dir: str | pathlib.Path | None = None) -> None:
        self._watch_dir: pathlib.Path = (
            pathlib.Path(watch_dir) if watch_dir else _D01_ROOT
        )
        self._handlers: list[Any] = []
        self._seen: set[str] = set()
        self._running: bool = False

    # ------------------------------------------------------------------
    # Handler registration
    # ------------------------------------------------------------------

    def add_handler(self, handler: Any) -> None:
        """Register an async callable ``handler(command: Command) -> None``."""
        self._handlers.append(handler)

    # ------------------------------------------------------------------
    # Core logic
    # ------------------------------------------------------------------

    def _classify(self, path: pathlib.Path) -> str:
        """Return ``"START_HARVEST"`` or ``"SIS"`` based on *path*."""
        if (
            _HARVEST_TRIGGER_STEM in path.stem.upper()
            or path.stem.startswith("!")
        ):
            return "START_HARVEST"
        return "SIS"

    async def _process_file(self, path: pathlib.Path) -> None:
        """Validate and dispatch a single candidate file."""
        if path.suffix not in _SIS_SUFFIXES:
            return

        payload = _load_payload(path)
        if payload is None:
            _log_zero_trust_rejection(path, "unrecognised or unparseable format")
            return

        if not _verify_signature(payload):
            _log_zero_trust_rejection(path, "missing or invalid cryptographic signature")
            return

        command = Command(
            source_file=str(path),
            payload=payload,
            command_type=self._classify(path),
        )
        logger.info(
            "[D01 Watcher] ✅ Valid command accepted: type=%s | file=%s",
            command.command_type,
            path.name,
        )

        for handler in self._handlers:
            try:
                await handler(command)
            except Exception as exc:  # pragma: no cover
                logger.error(
                    "[D01 Watcher] Handler error for '%s': %s", path.name, exc
                )

    async def _scan(self) -> None:
        """Scan watch_dir for new files and process any not yet seen."""
        try:
            entries = list(self._watch_dir.iterdir())
        except OSError:
            return
        for entry in entries:
            if not entry.is_file():
                continue
            key = f"{entry.name}::{entry.stat().st_mtime}::{entry.stat().st_size}"
            if key in self._seen:
                continue
            self._seen.add(key)
            await self._process_file(entry)

    async def run(self) -> None:
        """
        Start the polling loop.

        Runs indefinitely until :meth:`stop` is called.  Polls
        *watch_dir* every :data:`_POLL_INTERVAL_SECONDS` seconds.
        """
        self._running = True
        logger.info(
            "[D01 Watcher] 🟢 Live ingestion watcher armed — monitoring '%s'",
            self._watch_dir,
        )
        while self._running:
            await self._scan()
            await asyncio.sleep(_POLL_INTERVAL_SECONDS)

    def stop(self) -> None:
        """Signal the watcher loop to terminate after its current iteration."""
        self._running = False
        logger.info("[D01 Watcher] 🔴 Watcher stopped.")


# ---------------------------------------------------------------------------
# Bridge-connected factory
# ---------------------------------------------------------------------------


def create_watcher_with_bridge(
    watch_dir: str | pathlib.Path | None = None,
) -> "D01Watcher":
    """
    Create a :class:`D01Watcher` pre-wired to the D01→D04 bridge.

    Any valid command received by the watcher is automatically dispatched
    to :func:`core.district_1_4_bridge.dispatch` so the event is hashed,
    timestamped, and archived in District 04 without any additional setup.

    Parameters
    ----------
    watch_dir:
        Directory to monitor.  Defaults to the ``District_01_COMMAND_INPUT``
        folder.

    Returns
    -------
    D01Watcher
        A watcher with the bridge handler already registered.
    """
    from core.district_1_4_bridge import dispatch as bridge_dispatch  # local import to avoid circular dep

    async def _bridge_handler(command: Command) -> None:
        await bridge_dispatch(
            payload=command.payload,
            command_type=command.command_type,
            source_file=command.source_file,
        )

    watcher = D01Watcher(watch_dir=watch_dir)
    watcher.add_handler(_bridge_handler)
    return watcher
