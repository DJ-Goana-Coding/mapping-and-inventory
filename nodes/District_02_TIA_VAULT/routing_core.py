"""
T.I.A. Routing Core — District 02: Intelligence Layer
======================================================
Core routing logic for the Tactical Intelligence Architect (T.I.A.) persona.

Routes incoming signals from sovereign nodes to the appropriate downstream
targets: Brain Vault, Staging Queue, Persona Broadcast, or the ORACLE Council.

Constraint: This module does NOT modify V23 trading engines or RAG Indexer
logic. It strictly routes — it never overwrites existing vault records above
the Guardian's 85% semantic similarity threshold.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

FREQ_SIGNATURE = "69-333-222-92-93-999-777-88-29-369"

# ---------------------------------------------------------------------------
# Signal Priority
# ---------------------------------------------------------------------------


class Priority(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ---------------------------------------------------------------------------
# Signal dataclass
# ---------------------------------------------------------------------------


@dataclass
class Signal:
    """Represents an incoming intelligence signal to be routed by T.I.A."""

    source: str
    payload: dict[str, Any]
    signal_type: str
    priority: Priority = Priority.MEDIUM
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Routing table
# ---------------------------------------------------------------------------

#: Maps signal_type strings to (destination, priority) pairs.
ROUTING_TABLE: dict[str, tuple[str, Priority]] = {
    "fleet_topology_update": ("brain_vault+broadcast", Priority.HIGH),
    "acquisition_target_staged": ("staging_queue", Priority.MEDIUM),
    "persona_health_alert": ("oracle_council", Priority.HIGH),
    "guardian_rejection": ("audit_log_district_12", Priority.LOW),
    "phase_broadcast": ("all_personas", Priority.HIGH),
}

#: All active personas T.I.A. coordinates with.
ACTIVE_PERSONAS: list[str] = [
    "ORACLE",
    "DOOFY",
    "HIPPY",
    "AION",
    "GOANNA",
    "SNIPER",
    "SENTINEL",
    "WRAITH",
    "SCOUT",
]


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------


class TIARouter:
    """
    Routes incoming signals to the appropriate destination according to the
    static routing table defined above.

    Usage::

        router = TIARouter()
        result = router.route(signal)
    """

    def route(self, signal: Signal) -> dict[str, Any]:
        """
        Evaluate *signal* against the routing table and return a routing
        decision dict describing the destination and action taken.
        """
        destination, priority = ROUTING_TABLE.get(
            signal.signal_type,
            ("brain_vault", Priority.LOW),
        )

        logger.info(
            "[T.I.A. Router] signal_type=%s | source=%s | destination=%s | priority=%s",
            signal.signal_type,
            signal.source,
            destination,
            priority.value,
        )

        return {
            "signal_type": signal.signal_type,
            "source": signal.source,
            "destination": destination,
            "priority": priority.value,
            "freq_signature": FREQ_SIGNATURE,
            "payload_keys": list(signal.payload.keys()),
        }

    def broadcast(self, message: str, source: str = "T.I.A.") -> list[dict[str, Any]]:
        """
        Broadcast *message* to all active personas.

        Returns a list of routing decisions, one per persona.
        """
        results = []
        for persona in ACTIVE_PERSONAS:
            signal = Signal(
                source=source,
                payload={"message": message, "recipient": persona},
                signal_type="phase_broadcast",
                priority=Priority.HIGH,
            )
            results.append(self.route(signal))
            logger.info("[T.I.A. Router] Broadcast sent to %s.", persona)
        return results
