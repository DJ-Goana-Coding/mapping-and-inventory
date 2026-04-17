#!/usr/bin/env python3
"""
🖥️ HARDWARE NODES — Physical Fleet Inventory Tracker (v22.2122)

Tracks the Admiral's physical hardware fleet:
  • Node_01_S10  — Samsung S10 (Exynos 9820) with offline sync
  • Node_02_Laptops — Development laptops & Chromebook
  • Node_03_Ute  — Nissan utility vehicle wiring/diagnostics

Every node carries a FrequencyCheck to verify 144 Hz alignment.

Usage:
    from inventory.hardware_nodes import HardwareInventory

    inv = HardwareInventory()
    inv.frequency_check("node_01_s10")
    print(inv.status())
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Default node definitions
# ---------------------------------------------------------------------------

DEFAULT_NODES: Dict[str, Dict[str, Any]] = {
    "node_01_s10": {
        "label": "Samsung Galaxy S10",
        "type": "mobile",
        "chipset": "Exynos 9820",
        "ram_gb": 8,
        "storage_gb": 128,
        "role": "Air-Gap Scout / Field Uplink",
        "os": "Android (Termux bridge)",
        "offline_sync": True,
        "frequency_hz": 144,
        "notes": "Primary mobile node — offline-capable Citadel relay.",
    },
    "node_02_laptops": {
        "label": "Development Laptops & Chromebook",
        "type": "compute",
        "devices": [
            {"name": "Primary Dev Laptop", "role": "Main development workstation"},
            {"name": "Chromebook", "role": "Lightweight browser-based access"},
        ],
        "role": "Development Workstation Cluster",
        "offline_sync": False,
        "frequency_hz": 144,
        "notes": "Desktop compute nodes — connected to the Citadel via Git.",
    },
    "node_03_ute": {
        "label": "Nissan Utility Vehicle",
        "type": "vehicle",
        "make": "Nissan",
        "body": "Utility (Ute)",
        "role": "Mobile Infrastructure / Diagnostic Logging",
        "offline_sync": False,
        "frequency_hz": 144,
        "diagnostics": {
            "cross_feed_short_circuit": {
                "status": "under_investigation",
                "description": "Cross-feed short-circuit in wiring loom — repair logs tracked.",
            },
        },
        "notes": "Vehicle wiring diagnostics and repair logs are tracked here.",
    },
}

TARGET_FREQUENCY_HZ = 144


class HardwareInventory:
    """Tracker for the Admiral's physical hardware fleet.

    Each node is verified for 144 Hz frequency alignment via
    ``frequency_check``.
    """

    def __init__(self, *, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "hardware_inventory")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._nodes: Dict[str, Dict[str, Any]] = {k: dict(v) for k, v in DEFAULT_NODES.items()}

    # ------------------------------------------------------------------
    # Node access
    # ------------------------------------------------------------------

    def get_node(self, node_id: str) -> Dict[str, Any]:
        """Return a node by its ID.  Raises ``KeyError`` if not found."""
        key = node_id.lower().replace(" ", "_").replace("-", "_")
        if key not in self._nodes:
            raise KeyError(f"Unknown node '{node_id}'. Available: {', '.join(self._nodes)}")
        return self._nodes[key]

    def list_nodes(self) -> List[Dict[str, Any]]:
        """Return all registered hardware nodes."""
        return [{"id": k, **v} for k, v in self._nodes.items()]

    def add_node(self, node_id: str, definition: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new hardware node."""
        key = node_id.lower().replace(" ", "_").replace("-", "_")
        definition.setdefault("frequency_hz", TARGET_FREQUENCY_HZ)
        definition.setdefault("offline_sync", False)
        self._nodes[key] = definition
        return definition

    def update_node(self, node_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Merge *updates* into the existing node definition for *node_id*.

        Raises ``KeyError`` if the node does not exist.  This is the
        supported public API for telemetry-driven field updates; direct
        access to ``_nodes`` should be avoided.
        """
        key = node_id.lower().replace(" ", "_").replace("-", "_")
        if key not in self._nodes:
            raise KeyError(f"Unknown node '{node_id}'. Available: {', '.join(self._nodes)}")
        self._nodes[key].update(updates)
        return self._nodes[key]

    # ------------------------------------------------------------------
    # Frequency check
    # ------------------------------------------------------------------

    def frequency_check(self, node_id: str) -> Dict[str, Any]:
        """Verify that *node_id* is vibrating at 144 Hz.

        Returns a result dict with ``aligned`` (bool) and metadata.
        """
        node = self.get_node(node_id)
        node_freq = node.get("frequency_hz", 0)

        return {
            "node_id": node_id,
            "label": node.get("label", node_id),
            "measured_hz": node_freq,
            "target_hz": TARGET_FREQUENCY_HZ,
            "aligned": node_freq == TARGET_FREQUENCY_HZ,
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def frequency_check_all(self) -> List[Dict[str, Any]]:
        """Run frequency checks across every registered node."""
        return [self.frequency_check(nid) for nid in self._nodes]

    # ------------------------------------------------------------------
    # Offline sync flag
    # ------------------------------------------------------------------

    def offline_sync(self, node_id: str) -> bool:
        """Return ``True`` when *node_id* supports offline synchronisation."""
        return bool(self.get_node(node_id).get("offline_sync", False))

    def set_offline_sync(self, node_id: str, enabled: bool) -> None:
        """Toggle the offline-sync capability for a node."""
        self.get_node(node_id)["offline_sync"] = enabled

    # ------------------------------------------------------------------
    # Diagnostics (vehicle-specific)
    # ------------------------------------------------------------------

    def log_diagnostic(self, node_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Append a diagnostic log entry to a node (typically the Ute)."""
        node = self.get_node(node_id)
        diag = node.setdefault("diagnostics", {})
        log = diag.setdefault("log", [])
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        log.append(entry)
        return entry

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, filename: str = "hardware_nodes.json") -> Path:
        """Persist the current hardware inventory to disk."""
        out = self.output_dir / filename
        payload = {
            "version": "v22.2122",
            "nodes": {k: v for k, v in self._nodes.items()},
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out.write_text(json.dumps(payload, indent=2))
        return out

    def status(self) -> Dict[str, Any]:
        """Return a summary of the hardware inventory."""
        checks = self.frequency_check_all()
        return {
            "total_nodes": len(self._nodes),
            "nodes_aligned": sum(1 for c in checks if c["aligned"]),
            "target_frequency_hz": TARGET_FREQUENCY_HZ,
            "offline_capable": [nid for nid, n in self._nodes.items() if n.get("offline_sync")],
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    inv = HardwareInventory()
    print("🖥️ HARDWARE NODES — Status")
    print(json.dumps(inv.status(), indent=2))

    print("\n📋 Node List:")
    for node in inv.list_nodes():
        nid = node.pop("id")
        print(f"  [{nid}] {node.get('label', '?')} — {node.get('role', '?')}")

    print("\n🔊 Frequency Checks:")
    for check in inv.frequency_check_all():
        icon = "✅" if check["aligned"] else "❌"
        print(f"  {icon} {check['label']}: {check['measured_hz']} Hz")


if __name__ == "__main__":
    main()
