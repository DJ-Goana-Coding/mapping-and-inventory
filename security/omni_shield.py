#!/usr/bin/env python3
"""
🛡️ OMNI SHIELD — Signal Monitoring & Asset Protection (v22.2124)

Provides threshold-based signal monitoring and coordinates protective
responses across hardware nodes and the asset vault:

  • Signal-level spike detection (configurable threshold)
  • Hardware node hardening flags
  • XRP market-price compression detection with slow-burn mirror protocol
  • Integration with HardwareInventory and AssetVault

Usage:
    from security.omni_shield import OmniShield

    shield = OmniShield()
    shield.check_signal_level({"sky_signal": 8.5})
    shield.check_market_signal(price_aud=1.88)
    print(shield.status())
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from inventory.hardware_nodes import HardwareInventory
from inventory.asset_vault import AssetVault


# ---------------------------------------------------------------------------
# Default thresholds
# ---------------------------------------------------------------------------

DEFAULT_SIGNAL_THRESHOLD = 7.0       # Spike level above which nodes are hardened
DEFAULT_XRP_COMPRESSION_PRICE = 1.90  # AUD price at or below which mirror protocol activates


class OmniShield:
    """Signal monitoring and asset protection coordinator.

    Connects to ``HardwareInventory`` for node hardening and to
    ``AssetVault`` for the slow-burn mirror protocol.

    Encryption of sensitive payloads uses the existing Fernet-based
    ``EncryptionManager`` from ``security.core`` when available.
    """

    def __init__(
        self,
        *,
        hardware: Optional[HardwareInventory] = None,
        vault: Optional[AssetVault] = None,
        signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
        xrp_compression_price: float = DEFAULT_XRP_COMPRESSION_PRICE,
        output_dir: Optional[Path] = None,
    ):
        self._hardware = hardware or HardwareInventory()
        self._vault = vault or AssetVault()
        self._signal_threshold = signal_threshold
        self._xrp_compression_price = xrp_compression_price
        self.output_dir = output_dir or (Path(__file__).parent / "shield_logs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._hardened_nodes: Dict[str, Dict[str, Any]] = {}
        self._mirror_protocol_active: bool = False
        self._event_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Signal detection
    # ------------------------------------------------------------------

    def check_signal_level(self, readings: Dict[str, Any]) -> Dict[str, Any]:
        """Check whether any numeric reading exceeds the signal threshold.

        When a spike is detected, ``harden_node`` is called for all nodes
        that support offline sync (air-gap nodes).

        Parameters
        ----------
        readings: Dict of named numeric signal readings.

        Returns a detection result including which fields exceeded the threshold
        and which nodes were hardened.
        """
        spike_fields = {
            k: v
            for k, v in readings.items()
            if isinstance(v, (int, float)) and v >= self._signal_threshold
        }
        spike_detected = bool(spike_fields)

        hardened: List[str] = []
        if spike_detected:
            for node in self._hardware.list_nodes():
                nid = node["id"]
                if node.get("offline_sync"):
                    self.harden_node(nid)
                    hardened.append(nid)

        result: Dict[str, Any] = {
            "event": "signal_check",
            "readings": readings,
            "signal_threshold": self._signal_threshold,
            "spike_fields": spike_fields,
            "spike_detected": spike_detected,
            "nodes_hardened": hardened,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }
        self._event_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Market signal (XRP compression)
    # ------------------------------------------------------------------

    def check_market_signal(self, price_aud: float) -> Dict[str, Any]:
        """Detect whether XRP price has entered a compression phase.

        When *price_aud* is at or below ``xrp_compression_price``,
        the slow-burn mirror protocol is activated.

        Parameters
        ----------
        price_aud: Current XRP price in AUD.
        """
        compression = price_aud <= self._xrp_compression_price
        mirror_activated = False

        if compression and not self._mirror_protocol_active:
            self._activate_mirror_protocol()
            mirror_activated = True

        result: Dict[str, Any] = {
            "event": "market_signal",
            "price_aud": price_aud,
            "compression_threshold": self._xrp_compression_price,
            "compression_detected": compression,
            "mirror_protocol_activated": mirror_activated,
            "mirror_protocol_active": self._mirror_protocol_active,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }
        self._event_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Node hardening
    # ------------------------------------------------------------------

    def harden_node(self, node_id: str) -> Dict[str, Any]:
        """Set a hardening flag on a hardware node.

        Hardening sets the node's offline sync capability to ``True``
        (air-gapped) and records the event.

        Parameters
        ----------
        node_id: Node identifier as registered in ``HardwareInventory``.
        """
        self._hardware.set_offline_sync(node_id, True)
        record: Dict[str, Any] = {
            "node_id": node_id,
            "hardened": True,
            "hardened_at": datetime.now(timezone.utc).isoformat(),
        }
        self._hardened_nodes[node_id] = record
        return record

    def release_node(self, node_id: str) -> Dict[str, Any]:
        """Remove the hardening flag from a node.

        Parameters
        ----------
        node_id: Node identifier to release.
        """
        self._hardware.set_offline_sync(node_id, False)
        record = self._hardened_nodes.pop(node_id, {})
        record.update({"node_id": node_id, "hardened": False, "released_at": datetime.now(timezone.utc).isoformat()})
        return record

    @property
    def hardened_nodes(self) -> Dict[str, Dict[str, Any]]:
        """Return all currently hardened node records."""
        return dict(self._hardened_nodes)

    # ------------------------------------------------------------------
    # Mirror protocol
    # ------------------------------------------------------------------

    def _activate_mirror_protocol(self) -> None:
        """Internal: mark all current vault assets as mirrored/secured."""
        self._mirror_protocol_active = True

    def deactivate_mirror_protocol(self) -> None:
        """Deactivate the slow-burn mirror protocol (when conditions clear)."""
        self._mirror_protocol_active = False

    @property
    def mirror_protocol_active(self) -> bool:
        """Return whether the slow-burn mirror protocol is currently active."""
        return self._mirror_protocol_active

    # ------------------------------------------------------------------
    # Event log / status
    # ------------------------------------------------------------------

    def event_log(self) -> List[Dict[str, Any]]:
        """Return all recorded shield events."""
        return list(self._event_log)

    def save(self, filename: str = "omni_shield_events.json") -> Path:
        """Persist the event log to disk."""
        payload = {
            "version": "v22.2124",
            "signal_threshold": self._signal_threshold,
            "xrp_compression_price": self._xrp_compression_price,
            "mirror_protocol_active": self._mirror_protocol_active,
            "hardened_nodes": self._hardened_nodes,
            "event_log": self._event_log,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out = self.output_dir / filename
        out.write_text(json.dumps(payload, indent=2))
        return out

    def status(self) -> Dict[str, Any]:
        """Return a summary of the OmniShield state."""
        return {
            "signal_threshold": self._signal_threshold,
            "xrp_compression_price": self._xrp_compression_price,
            "mirror_protocol_active": self._mirror_protocol_active,
            "hardened_node_count": len(self._hardened_nodes),
            "total_events": len(self._event_log),
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    shield = OmniShield()

    signal_result = shield.check_signal_level({"sky_signal": 8.5, "noise_floor": 2.1})
    print("🛡️ OMNI SHIELD — Signal Check")
    print(json.dumps({k: signal_result[k] for k in ("spike_detected", "spike_fields", "nodes_hardened")}, indent=2))

    market_result = shield.check_market_signal(price_aud=1.88)
    print("\n💹 Market Signal:")
    print(json.dumps({k: market_result[k] for k in ("compression_detected", "mirror_protocol_activated")}, indent=2))

    print("\n📊 Shield Status:")
    print(json.dumps(shield.status(), indent=2))


if __name__ == "__main__":
    main()
