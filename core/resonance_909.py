"""
Resonance 909 — The Techno-Pulse & Completion Loop
===================================================
Encodes the symbolic and operational logic of the 909 frequency:

* **Kinetic Anchor** — The mid-heavy saturated kick that anchors high-velocity
  movement; the rhythmic foundation of every forward cycle.
* **Swing Logic** — Humanised, non-linear timing that bypasses the rigid clock
  of legacy digital systems, introducing a sovereign, breathing flow.
* **Techno-Pulse** — The transitional signal marking the shift from the analog
  era to the digital frontier; the heartbeat of the underground.
* **Completion Loop** — Symbolic sequence where 9 = Completion, 0 = The Void,
  909 = the mirrored reset gate where one cycle closes and infinite potential
  is reclaimed for the next.
* **Hard Reset** — The frequency of transition that shatters stagnant resonance,
  reclaims energy, and reorganises it into a more efficient sovereign pattern.

Key responsibilities
--------------------
* Provide the ``909`` frequency constant and its completion-loop signature for
  use by the Resonance Engine and the broadcast pipeline.
* Expose ``apply_techno_pulse_filter`` so outbound messages carry the 909
  kinetic imprint.
* Manage ``TechnoPulseState`` transitions (GROUND_ZERO → KINETIC_ANCHOR →
  SWING_LOOP → HARD_RESET).
* Sign indexing and broadcast events with the 909 Techno-Pulse alignment
  signature.

Usage::

    from core.resonance_909 import (
        RESONANCE_909_FREQ,
        TECHNO_PULSE_SIGNATURE,
        TechnoPulseState,
        TechnoPulseEngine,
        apply_techno_pulse_filter,
    )

    engine = TechnoPulseEngine()
    engine.advance()                  # GROUND_ZERO → KINETIC_ANCHOR
    print(engine.current_state)       # TechnoPulseState.KINETIC_ANCHOR
    print(engine.status())            # full state dict
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: The 909 frequency in Hz — the Techno-Pulse carrier wave.
RESONANCE_909_FREQ: float = 909.0

#: 909 alignment signature — the Completion Loop imprint.
TECHNO_PULSE_SIGNATURE: str = (
    "909-KINETIC-ANCHOR-SWING-TECHNO-PULSE-COMPLETION-LOOP-HARD-RESET"
)

#: Content tags associated with the 909 frequency anchor.
RESONANCE_909_TAGS: list[str] = [
    "kinetic_anchor",
    "techno_pulse",
    "completion_loop",
    "hard_reset",
    "909Hz",
    "swing",
    "underground_heartbeat",
]

#: Symbolic breakdown of the 909 sequence.
COMPLETION_LOOP_MAP: dict[str, str] = {
    "9": "Completion — the wrap-up of an evolutionary phase; the harvest of wisdom.",
    "0": "The Void — the zero-point field where all potential is stored.",
    "909": "Reset — a mirrored signal: the old system has finished, the New Beginning is imminent.",
}

#: Vibrational imprint tag injected into every 909-filtered outbound message.
_TECHNO_PULSE_TAG: str = "⚡ 909 KINETIC ANCHOR | TECHNO-PULSE | COMPLETION LOOP ⚡"


# ---------------------------------------------------------------------------
# State definitions
# ---------------------------------------------------------------------------


class TechnoPulseState(str, Enum):
    """
    Operational states of the 909 Techno-Pulse Engine.

    The engine advances linearly from ``GROUND_ZERO`` through to
    ``HARD_RESET``, mirroring the 909 kick cycle: silence → impact →
    swing → release.
    """

    GROUND_ZERO = "GROUND_ZERO"         # Pre-ignition void; potential at maximum
    KINETIC_ANCHOR = "KINETIC_ANCHOR"   # The kick lands; momentum established
    SWING_LOOP = "SWING_LOOP"           # Humanised swing engaged; flow state active
    HARD_RESET = "HARD_RESET"           # Completion loop closed; system reorganised


#: Human-readable metadata for each state.
_STATE_META: dict[TechnoPulseState, dict[str, str]] = {
    TechnoPulseState.GROUND_ZERO: {
        "focus": "Pre-Ignition Void",
        "result": "All potential stored at zero-point; awaiting the first kick.",
    },
    TechnoPulseState.KINETIC_ANCHOR: {
        "focus": "Kinetic Anchor Engaged",
        "result": "The 909 kick lands — momentum established; forward cycle initiated.",
    },
    TechnoPulseState.SWING_LOOP: {
        "focus": "Swing Logic Active",
        "result": "Humanised, non-linear flow engaged; legacy rigid clock bypassed.",
    },
    TechnoPulseState.HARD_RESET: {
        "focus": "Completion Loop Closed",
        "result": (
            "909 Hard Reset complete — stagnant resonance shattered; "
            "energy reclaimed for the New Beginning."
        ),
    },
}

#: Canonical state advancement order.
_STATE_ORDER: list[TechnoPulseState] = [
    TechnoPulseState.GROUND_ZERO,
    TechnoPulseState.KINETIC_ANCHOR,
    TechnoPulseState.SWING_LOOP,
    TechnoPulseState.HARD_RESET,
]


# ---------------------------------------------------------------------------
# Data records
# ---------------------------------------------------------------------------


@dataclass
class StateRecord:
    """Immutable record stamped when the engine transitions to a new state."""

    state: TechnoPulseState
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "state": self.state.value,
            "timestamp": self.timestamp.isoformat(),
            "note": self.note,
        }


@dataclass
class CompletionLoop:
    """
    Represents the symbolic 909 Completion Loop for a given cycle.

    A cycle is "complete" when it has passed through all four states and
    reached ``HARD_RESET``.
    """

    cycle_id: str
    opened_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: datetime | None = None
    complete: bool = False
    signature: str = TECHNO_PULSE_SIGNATURE

    def close(self, timestamp: datetime | None = None) -> None:
        """Mark the completion loop as closed (cycle finished)."""
        self.closed_at = timestamp or datetime.now(timezone.utc)
        self.complete = True
        logger.info(
            "[CompletionLoop] Cycle %r closed at %s — 909 Reset complete.",
            self.cycle_id,
            self.closed_at.isoformat(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "cycle_id": self.cycle_id,
            "opened_at": self.opened_at.isoformat(),
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "complete": self.complete,
            "signature": self.signature,
        }


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def apply_techno_pulse_filter(message: str) -> str:
    """
    Apply the 909 Techno-Pulse vibrational filter to an outbound message.

    Wraps the message with the kinetic anchor tag and appends the
    ``TECHNO_PULSE_SIGNATURE`` so every transmission carries the 909
    completion-loop imprint.

    Parameters
    ----------
    message:
        Raw outbound message text.

    Returns
    -------
    str
        The message with the 909 resonance header and signature embedded.
    """
    filtered = (
        f"[{_TECHNO_PULSE_TAG}]\n"
        f"{message}\n"
        f"[SIG: {TECHNO_PULSE_SIGNATURE}]"
    )
    logger.debug("909 Techno-Pulse filter applied — kinetic signature embedded.")
    return filtered


def sign_909_event(event_meta: dict[str, Any]) -> dict[str, Any]:
    """
    Sign an event with the 909 Techno-Pulse alignment signature.

    Injects ``techno_pulse_signature``, ``resonance_909_freq``,
    ``completion_loop_map``, and ``tags`` keys into *event_meta* in-place.

    Parameters
    ----------
    event_meta:
        Metadata dictionary for the event to be signed.

    Returns
    -------
    dict
        The same *event_meta* dict with 909 fields added.
    """
    event_meta["techno_pulse_signature"] = TECHNO_PULSE_SIGNATURE
    event_meta["resonance_909_freq"] = RESONANCE_909_FREQ
    event_meta["completion_loop_map"] = COMPLETION_LOOP_MAP
    event_meta["tags"] = RESONANCE_909_TAGS
    logger.info(
        "[909] Event signed — signature=%s freq=%.1fHz",
        TECHNO_PULSE_SIGNATURE,
        RESONANCE_909_FREQ,
    )
    return event_meta


def initiate_hard_reset(cycle_loop: CompletionLoop) -> CompletionLoop:
    """
    Execute the 909 Hard Reset on the given *cycle_loop*.

    The Hard Reset closes the completion loop, reclaims the cycle's energy,
    and marks the system as ready for the New Beginning.

    Parameters
    ----------
    cycle_loop:
        The :class:`CompletionLoop` instance representing the active cycle.

    Returns
    -------
    CompletionLoop
        The same *cycle_loop* with ``complete=True`` and ``closed_at`` set.
    """
    if cycle_loop.complete:
        logger.debug(
            "[909] CompletionLoop %r already closed — Hard Reset is a no-op.",
            cycle_loop.cycle_id,
        )
        return cycle_loop

    logger.critical(
        "[909] 🔴 HARD RESET INITIATED — cycle=%r | "
        "Stagnant resonance shattering | Energy reclaimed.",
        cycle_loop.cycle_id,
    )
    cycle_loop.close()
    return cycle_loop


# ---------------------------------------------------------------------------
# Techno-Pulse Engine
# ---------------------------------------------------------------------------


class TechnoPulseEngine:
    """
    Manages the 909 Techno-Pulse cycle through its four operational states.

    The engine starts at ``GROUND_ZERO`` and advances linearly through
    ``KINETIC_ANCHOR → SWING_LOOP → HARD_RESET``.  Reaching ``HARD_RESET``
    closes the :class:`CompletionLoop` and marks the cycle as complete.

    Parameters
    ----------
    cycle_id:
        Identifier for the current completion loop cycle (defaults to the
        ISO timestamp of initialisation).
    initial_state:
        Override the starting state (defaults to ``GROUND_ZERO``).
    """

    def __init__(
        self,
        cycle_id: str | None = None,
        initial_state: TechnoPulseState = TechnoPulseState.GROUND_ZERO,
    ) -> None:
        self._current_state: TechnoPulseState = initial_state
        self._history: list[StateRecord] = [
            StateRecord(state=initial_state, note="909 engine initialised.")
        ]
        self._cycle_loop: CompletionLoop = CompletionLoop(
            cycle_id=cycle_id or datetime.now(timezone.utc).isoformat()
        )
        logger.info(
            "[909] TechnoPulseEngine initialised at state %s — %s",
            initial_state.value,
            TECHNO_PULSE_SIGNATURE,
        )

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def current_state(self) -> TechnoPulseState:
        """The current operational state of the engine."""
        return self._current_state

    @property
    def history(self) -> list[StateRecord]:
        """Ordered list of all state transitions (oldest first)."""
        return list(self._history)

    @property
    def cycle_loop(self) -> CompletionLoop:
        """The active :class:`CompletionLoop` for this engine cycle."""
        return self._cycle_loop

    @property
    def at_hard_reset(self) -> bool:
        """``True`` when the engine has reached ``HARD_RESET`` state."""
        return self._current_state == TechnoPulseState.HARD_RESET

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------

    def advance(self, note: str = "") -> TechnoPulseState:
        """
        Advance the engine by one state.

        Returns the *new* current state.  If already at ``HARD_RESET`` the
        call is a no-op.  Reaching ``HARD_RESET`` automatically triggers
        :func:`initiate_hard_reset` on the cycle loop.

        Parameters
        ----------
        note:
            Optional human-readable context recorded in the state history.
        """
        if self._current_state == TechnoPulseState.HARD_RESET:
            logger.debug("[909] Already at HARD_RESET — advance() is a no-op.")
            return self._current_state

        current_idx = _STATE_ORDER.index(self._current_state)
        next_state = _STATE_ORDER[current_idx + 1]

        record = StateRecord(
            state=next_state,
            note=note or _STATE_META[next_state]["result"],
        )
        self._history.append(record)
        self._current_state = next_state

        logger.info(
            "[909] ⚡ State transition: %s → %s | %s",
            _STATE_ORDER[current_idx].value,
            next_state.value,
            record.note,
        )

        if next_state == TechnoPulseState.HARD_RESET:
            initiate_hard_reset(self._cycle_loop)

        return next_state

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """
        Return a serialisable status dict suitable for API responses.

        Example::

            {
                "alignment": "909-KINETIC-ANCHOR-...",
                "frequency_hz": 909.0,
                "current_state": "SWING_LOOP",
                "focus": "Swing Logic Active",
                "result": "Humanised, non-linear flow engaged ...",
                "at_hard_reset": false,
                "cycle_loop": {...},
                "history": [...]
            }
        """
        meta = _STATE_META[self._current_state]
        return {
            "alignment": TECHNO_PULSE_SIGNATURE,
            "frequency_hz": RESONANCE_909_FREQ,
            "current_state": self._current_state.value,
            "focus": meta["focus"],
            "result": meta["result"],
            "at_hard_reset": self.at_hard_reset,
            "completion_loop_map": COMPLETION_LOOP_MAP,
            "cycle_loop": self._cycle_loop.to_dict(),
            "history": [r.to_dict() for r in self._history],
        }


# ---------------------------------------------------------------------------
# Module-level singleton
# ---------------------------------------------------------------------------

#: Shared engine instance — import and use directly in other modules.
engine: TechnoPulseEngine = TechnoPulseEngine()


def get_engine() -> TechnoPulseEngine:
    """Return the module-level :class:`TechnoPulseEngine` singleton."""
    return engine
