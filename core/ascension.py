"""
Ascension Protocol — Vertical Trajectory Manager
=================================================
Governs the four-phase operational ascent of the distributed system:

  0. **GROUND**  — Pre-launch standby; awaiting ignition command.
  1. **IGNITION** — Breaking initial inertia; establishing the upward drive.
  2. **CLIMB**    — Navigating the layers; bypassing the noise of lower levels.
  3. **APEX**     — Achieving the high point; total oversight of the landscape.

Phase transitions are triggered as the system reaches operational milestones:

* ``IGNITION`` — entered automatically on first system initialisation (HEART boot).
* ``CLIMB``    — entered once the full Trinity boot completes with OK or SKIPPED.
* ``APEX``     — entered when the VortexBerserker engine becomes active.

Usage::

    from core.ascension import AscensionProtocol

    protocol = AscensionProtocol()
    protocol.advance()                # GROUND → IGNITION
    print(protocol.current_phase)     # AscensionPhase.IGNITION
    print(protocol.status())          # full phase dict
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Phase definitions
# ---------------------------------------------------------------------------

#: Ascension alignment signature stamped on every phase transition.
ASCENSION_SIGNATURE: str = "ASCENSION-VERTICAL-TRAJECTORY-369"


class AscensionPhase(str, Enum):
    """Ordered operational phases of the Ascension Protocol."""

    GROUND = "GROUND"       # Pre-launch / uninitialised
    IGNITION = "IGNITION"   # Breaking initial inertia; upward drive established
    CLIMB = "CLIMB"         # Navigating the layers; noise bypassed
    APEX = "APEX"           # High point reached; total oversight achieved


# Human-readable descriptions from the Ascension Protocol table.
_PHASE_META: dict[AscensionPhase, dict[str, str]] = {
    AscensionPhase.GROUND: {
        "focus": "Pre-Launch Standby",
        "result": "Awaiting ignition command.",
    },
    AscensionPhase.IGNITION: {
        "focus": "Breaking Initial Inertia",
        "result": "Establishing the upward drive.",
    },
    AscensionPhase.CLIMB: {
        "focus": "Navigating the Layers",
        "result": "Bypassing the noise of the lower levels.",
    },
    AscensionPhase.APEX: {
        "focus": "Achieving the High Point",
        "result": "Total oversight of the landscape.",
    },
}

# Canonical phase order for advance() transitions
_PHASE_ORDER: list[AscensionPhase] = [
    AscensionPhase.GROUND,
    AscensionPhase.IGNITION,
    AscensionPhase.CLIMB,
    AscensionPhase.APEX,
]


# ---------------------------------------------------------------------------
# Data record
# ---------------------------------------------------------------------------


@dataclass
class PhaseRecord:
    """Immutable record stamped when the system enters a new phase."""

    phase: AscensionPhase
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "phase": self.phase.value,
            "timestamp": self.timestamp.isoformat(),
            "note": self.note,
        }


# ---------------------------------------------------------------------------
# Protocol manager
# ---------------------------------------------------------------------------


class AscensionProtocol:
    """
    Manages the vertical trajectory of the system through its three phases.

    The protocol starts at ``GROUND`` and advances linearly through
    ``IGNITION → CLIMB → APEX``.  Once at ``APEX`` the system has achieved
    full operational altitude; further ``advance()`` calls are no-ops.

    Parameters
    ----------
    initial_phase:
        Override the starting phase (defaults to ``GROUND``).
    """

    def __init__(self, initial_phase: AscensionPhase = AscensionPhase.GROUND) -> None:
        self._current_phase: AscensionPhase = initial_phase
        self._history: list[PhaseRecord] = [
            PhaseRecord(phase=initial_phase, note="Protocol initialised.")
        ]
        logger.info(
            "[Ascension] Protocol initialised at phase %s — %s",
            initial_phase.value,
            ASCENSION_SIGNATURE,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_phase(self) -> AscensionPhase:
        """The current operational phase."""
        return self._current_phase

    @property
    def history(self) -> list[PhaseRecord]:
        """Ordered list of all phase transitions (oldest first)."""
        return list(self._history)

    @property
    def at_apex(self) -> bool:
        """``True`` when the system has reached ``APEX`` — maximum altitude."""
        return self._current_phase == AscensionPhase.APEX

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------

    def advance(self, note: str = "") -> AscensionPhase:
        """
        Advance the protocol by one phase.

        Returns the *new* current phase.  If already at ``APEX`` the call
        is a no-op and ``APEX`` is returned without recording a duplicate
        entry in the history.

        Parameters
        ----------
        note:
            Optional human-readable context recorded in the phase history.
        """
        if self._current_phase == AscensionPhase.APEX:
            logger.debug("[Ascension] Already at APEX — advance() is a no-op.")
            return self._current_phase

        current_idx = _PHASE_ORDER.index(self._current_phase)
        next_phase = _PHASE_ORDER[current_idx + 1]

        record = PhaseRecord(phase=next_phase, note=note or _PHASE_META[next_phase]["result"])
        self._history.append(record)
        self._current_phase = next_phase

        logger.info(
            "[Ascension] 🚀 Phase transition: %s → %s | %s",
            _PHASE_ORDER[current_idx].value,
            next_phase.value,
            record.note,
        )
        return next_phase

    def set_phase(self, phase: AscensionPhase, note: str = "") -> None:
        """
        Directly set the phase (used for recovery / external override).

        Unlike ``advance()``, this method allows jumping to any phase.
        A warning is logged if the target phase is earlier than the current one.
        """
        if phase == self._current_phase:
            return

        current_idx = _PHASE_ORDER.index(self._current_phase)
        target_idx = _PHASE_ORDER.index(phase)
        if target_idx < current_idx:
            logger.warning(
                "[Ascension] Phase regression detected: %s → %s (override).",
                self._current_phase.value,
                phase.value,
            )

        record = PhaseRecord(phase=phase, note=note or f"Direct override to {phase.value}.")
        self._history.append(record)
        self._current_phase = phase
        logger.info("[Ascension] Phase set to %s — %s", phase.value, record.note)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """
        Return a serialisable status dict suitable for API responses.

        Example::

            {
                "alignment": "ASCENSION-VERTICAL-TRAJECTORY-369",
                "current_phase": "CLIMB",
                "focus": "Navigating the Layers",
                "result": "Bypassing the noise of the lower levels.",
                "at_apex": false,
                "history": [...]
            }
        """
        meta = _PHASE_META[self._current_phase]
        return {
            "alignment": ASCENSION_SIGNATURE,
            "current_phase": self._current_phase.value,
            "focus": meta["focus"],
            "result": meta["result"],
            "at_apex": self.at_apex,
            "history": [r.to_dict() for r in self._history],
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Shared protocol instance — import and use directly in other modules.
protocol: AscensionProtocol = AscensionProtocol()


def get_protocol() -> AscensionProtocol:
    """Return the module-level :class:`AscensionProtocol` singleton."""
    return protocol
