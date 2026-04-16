#!/usr/bin/env python3
"""
📡 REGIONAL NODES — Mackay/Queensland Geospatial Mapping (v22.2122)

Maps the Citadel to the Mackay/Queensland grid (21.15°S, 149.18°E).
Includes toroidal field alignment, PvC hotspot tracking, and regional
node management.

Usage:
    from mapping.regional_nodes import RegionalNodeMapper

    mapper = RegionalNodeMapper()
    field  = mapper.sync_local_toroid()
    spots  = mapper.pvc_hotspots()
"""

import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Regional grid constants
# ---------------------------------------------------------------------------

MACKAY_COORDS = {
    "latitude": -21.15,
    "longitude": 149.18,
    "region": "Mackay, Queensland, Australia",
    "state": "QLD",
    "country": "AU",
}

REGIONAL_NODES: List[Dict[str, Any]] = [
    {
        "id": "mackay_cbd",
        "label": "Mackay CBD",
        "coords": {"lat": -21.1411, "lon": 149.1860},
        "type": "urban_core",
        "silicate_pct": 12.0,
    },
    {
        "id": "north_mackay",
        "label": "North Mackay",
        "coords": {"lat": -21.1200, "lon": 149.1750},
        "type": "residential",
        "silicate_pct": 11.8,
    },
    {
        "id": "south_mackay",
        "label": "South Mackay",
        "coords": {"lat": -21.1650, "lon": 149.1700},
        "type": "residential",
        "silicate_pct": 12.1,
    },
    {
        "id": "paget_industrial",
        "label": "Paget Industrial",
        "coords": {"lat": -21.1800, "lon": 149.1550},
        "type": "industrial",
        "silicate_pct": 11.5,
    },
    {
        "id": "harbour",
        "label": "Mackay Harbour",
        "coords": {"lat": -21.1070, "lon": 149.2280},
        "type": "maritime",
        "silicate_pct": 10.9,
    },
]


class RegionalNodeMapper:
    """Geospatial mapper for the Mackay/Queensland regional grid.

    Aligns the Citadel to the 12% silicate regional field, manages
    regional nodes, and tracks PvC (Person-vs-Camera) hotspot locations.
    """

    TARGET_FREQUENCY_HZ = 144
    SILICATE_FIELD_PCT = 12.0
    EARTH_RADIUS_KM = 6371.0

    def __init__(self, *, output_dir: Optional[Path] = None):
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "regional_mapping")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._nodes: List[Dict[str, Any]] = list(REGIONAL_NODES)
        self._pvc_hotspots: List[Dict[str, Any]] = []
        self._toroid_state: Optional[Dict[str, Any]] = None

    # ------------------------------------------------------------------
    # Toroidal field alignment
    # ------------------------------------------------------------------

    def sync_local_toroid(self) -> Dict[str, Any]:
        """Align the Citadel with the 12% silicate regional field.

        Returns the toroidal field state including field strength, alignment
        status, and the anchor coordinates.
        """
        avg_silicate = sum(n["silicate_pct"] for n in self._nodes) / max(len(self._nodes), 1)

        self._toroid_state = {
            "anchor": MACKAY_COORDS,
            "field_frequency_hz": self.TARGET_FREQUENCY_HZ,
            "silicate_field_pct": round(avg_silicate, 2),
            "target_silicate_pct": self.SILICATE_FIELD_PCT,
            "alignment_delta": round(abs(avg_silicate - self.SILICATE_FIELD_PCT), 4),
            "aligned": abs(avg_silicate - self.SILICATE_FIELD_PCT) < 1.0,
            "node_count": len(self._nodes),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._toroid_state

    # ------------------------------------------------------------------
    # PvC hotspot tracking
    # ------------------------------------------------------------------

    def pvc_hotspots(self) -> List[Dict[str, Any]]:
        """Return a list of PvC (Person-vs-Camera) hotspot locations.

        These represent traffic camera / demerit-trap locations identified
        in the PvC Ledger.  The list is seeded with known Mackay locations.
        """
        if not self._pvc_hotspots:
            self._pvc_hotspots = self._seed_pvc_hotspots()
        return list(self._pvc_hotspots)

    def add_pvc_hotspot(self, *, label: str, lat: float, lon: float, category: str = "speed_camera") -> Dict[str, Any]:
        """Register a new PvC hotspot."""
        entry = {
            "label": label,
            "coords": {"lat": lat, "lon": lon},
            "category": category,
            "distance_from_anchor_km": self._haversine(
                MACKAY_COORDS["latitude"], MACKAY_COORDS["longitude"], lat, lon
            ),
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pvc_hotspots.append(entry)
        return entry

    @staticmethod
    def _seed_pvc_hotspots() -> List[Dict[str, Any]]:
        """Provide a default set of known PvC hotspot locations in Mackay."""
        return [
            {"label": "Bruce Highway — Sarina", "coords": {"lat": -21.4222, "lon": 149.2167}, "category": "speed_camera"},
            {"label": "Peak Downs Highway — Walkerston", "coords": {"lat": -21.1750, "lon": 149.0650}, "category": "speed_camera"},
            {"label": "Mackay-Bucasia Rd", "coords": {"lat": -21.0700, "lon": 149.1530}, "category": "red_light_camera"},
            {"label": "Sydney St — CBD", "coords": {"lat": -21.1430, "lon": 149.1850}, "category": "red_light_camera"},
        ]

    # ------------------------------------------------------------------
    # Node management
    # ------------------------------------------------------------------

    def add_node(self, *, node_id: str, label: str, lat: float, lon: float,
                 node_type: str = "custom", silicate_pct: float = 12.0) -> Dict[str, Any]:
        """Register a new regional node."""
        node = {
            "id": node_id,
            "label": label,
            "coords": {"lat": lat, "lon": lon},
            "type": node_type,
            "silicate_pct": silicate_pct,
        }
        self._nodes.append(node)
        return node

    def list_nodes(self) -> List[Dict[str, Any]]:
        """Return all registered regional nodes."""
        return list(self._nodes)

    # ------------------------------------------------------------------
    # Distance helper
    # ------------------------------------------------------------------

    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Great-circle distance in km between two points."""
        rlat1, rlon1, rlat2, rlon2 = (math.radians(v) for v in (lat1, lon1, lat2, lon2))
        dlat = rlat2 - rlat1
        dlon = rlon2 - rlon1
        a = math.sin(dlat / 2) ** 2 + math.cos(rlat1) * math.cos(rlat2) * math.sin(dlon / 2) ** 2
        return round(self.EARTH_RADIUS_KM * 2 * math.asin(math.sqrt(a)), 3)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save_map(self, filename: str = "regional_map.json") -> Path:
        """Persist the full regional map to disk."""
        payload = {
            "anchor": MACKAY_COORDS,
            "nodes": self._nodes,
            "pvc_hotspots": self.pvc_hotspots(),
            "toroid_state": self._toroid_state,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out = self.output_dir / filename
        out.write_text(json.dumps(payload, indent=2))
        return out

    def status(self) -> Dict[str, Any]:
        """Return a summary of the regional mapping state."""
        return {
            "anchor": MACKAY_COORDS,
            "target_frequency_hz": self.TARGET_FREQUENCY_HZ,
            "total_nodes": len(self._nodes),
            "pvc_hotspots": len(self._pvc_hotspots) if self._pvc_hotspots else len(self._seed_pvc_hotspots()),
            "toroid_synced": self._toroid_state is not None,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    mapper = RegionalNodeMapper()
    print("📡 REGIONAL NODE MAPPER — Status")
    print(json.dumps(mapper.status(), indent=2))

    toroid = mapper.sync_local_toroid()
    print("\n🌀 Toroidal Field Alignment:")
    print(json.dumps(toroid, indent=2))

    hotspots = mapper.pvc_hotspots()
    print(f"\n🚨 PvC Hotspots ({len(hotspots)}):")
    for h in hotspots:
        print(f"   • {h['label']} — {h['category']}")


if __name__ == "__main__":
    main()
