#!/usr/bin/env python3
"""
📋 EQUIPMENT CHECKLIST TRACKER
Mobile Citadel Command Center - Equipment & Budget Tracker

Tracks equipment acquisition, budget, and readiness for mobile operations.
Implements the complete equipment checklist from the Mobile Citadel plan.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from enum import Enum


class EquipmentCategory(Enum):
    """Equipment categories"""
    COMPUTING = "computing"
    POWER = "power"
    CONNECTIVITY = "connectivity"
    VEHICLE = "vehicle"
    COMMUNITY = "community"
    LICENSE = "license"


class EquipmentStatus(Enum):
    """Equipment acquisition status"""
    NOT_STARTED = "not_started"
    RESEARCHING = "researching"
    QUOTED = "quoted"
    ORDERED = "ordered"
    ACQUIRED = "acquired"
    INSTALLED = "installed"


class EquipmentTracker:
    """Tracks equipment checklist and budget"""
    
    def __init__(self, data_file: str = "/tmp/mobile_citadel/equipment_tracker.json"):
        self.data_file = Path(data_file)
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        self.equipment = self._initialize_equipment()
        self.load_data()
    
    def _initialize_equipment(self) -> Dict:
        """Initialize complete equipment checklist"""
        return {
            "computing": [
                {"name": "Primary laptop (high-spec, rugged case)", "priority": "P0", "cost_estimate": 3000, "status": "not_started"},
                {"name": "Backup laptop #1", "priority": "P1", "cost_estimate": 1500, "status": "not_started"},
                {"name": "Backup laptop #2", "priority": "P1", "cost_estimate": 1500, "status": "not_started"},
                {"name": "Backup laptop #3", "priority": "P2", "cost_estimate": 1500, "status": "not_started"},
                {"name": "Oppo smartphone (Bridge Agent)", "priority": "P0", "cost_estimate": 0, "status": "acquired", "notes": "Already operational"},
                {"name": "Backup smartphone #1", "priority": "P1", "cost_estimate": 500, "status": "not_started"},
                {"name": "Backup smartphone #2", "priority": "P1", "cost_estimate": 500, "status": "not_started"},
                {"name": "Tablet for monitoring", "priority": "P1", "cost_estimate": 800, "status": "not_started"},
                {"name": "Portable monitor #1", "priority": "P2", "cost_estimate": 300, "status": "not_started"},
                {"name": "Portable monitor #2", "priority": "P2", "cost_estimate": 300, "status": "not_started"},
                {"name": "Keyboards, mice, cables", "priority": "P1", "cost_estimate": 200, "status": "not_started"},
                {"name": "USB hubs, power adapters", "priority": "P1", "cost_estimate": 150, "status": "not_started"},
                {"name": "External SSD 4TB", "priority": "P0", "cost_estimate": 400, "status": "not_started"},
                {"name": "NAS unit (RAID 1, 8TB+)", "priority": "P0", "cost_estimate": 600, "status": "not_started"},
                {"name": "Offline backup drives (4TB x2)", "priority": "P1", "cost_estimate": 300, "status": "not_started"},
                {"name": "Network router", "priority": "P0", "cost_estimate": 200, "status": "not_started"},
                {"name": "Mesh network nodes (3x)", "priority": "P1", "cost_estimate": 450, "status": "not_started"}
            ],
            "power": [
                {"name": "6x 300W flexible solar panels", "priority": "P0", "cost_estimate": 2400, "status": "not_started"},
                {"name": "4x 200W portable panels", "priority": "P1", "cost_estimate": 800, "status": "not_started"},
                {"name": "15kWh LiFePO4 battery bank", "priority": "P0", "cost_estimate": 8000, "status": "not_started"},
                {"name": "MPPT charge controllers", "priority": "P0", "cost_estimate": 500, "status": "not_started"},
                {"name": "3000W inverter (pure sine)", "priority": "P0", "cost_estimate": 600, "status": "not_started"},
                {"name": "5kW diesel generator", "priority": "P0", "cost_estimate": 2000, "status": "not_started"},
                {"name": "Cables, connectors, fuses", "priority": "P1", "cost_estimate": 300, "status": "not_started"},
                {"name": "Battery monitor + BMS", "priority": "P0", "cost_estimate": 400, "status": "not_started"}
            ],
            "connectivity": [
                {"name": "Starlink dish + router + mounting", "priority": "P0", "cost_estimate": 600, "status": "not_started", "monthly": 120},
                {"name": "4G/5G router with external antenna", "priority": "P0", "cost_estimate": 400, "status": "not_started"},
                {"name": "40dB signal booster", "priority": "P1", "cost_estimate": 300, "status": "not_started"},
                {"name": "SIM cards (3+ carriers)", "priority": "P0", "cost_estimate": 50, "status": "not_started", "monthly": 150},
                {"name": "LoRa modules (long-range)", "priority": "P2", "cost_estimate": 200, "status": "not_started"},
                {"name": "Ethernet switches", "priority": "P1", "cost_estimate": 100, "status": "not_started"},
                {"name": "Coaxial cables, adapters", "priority": "P1", "cost_estimate": 100, "status": "not_started"}
            ],
            "vehicle": [
                {"name": "All-terrain vehicle (7+ pass, 4WD)", "priority": "P0", "cost_estimate": 100000, "status": "not_started", "notes": "Mercedes Sprinter 4x4 / Unimog / MAN TGE"},
                {"name": "Trailer/caravan (all-terrain)", "priority": "P0", "cost_estimate": 30000, "status": "not_started"},
                {"name": "Roof rack for solar panels", "priority": "P0", "cost_estimate": 1500, "status": "not_started"},
                {"name": "Water storage (200L+)", "priority": "P0", "cost_estimate": 500, "status": "not_started"},
                {"name": "Kitchen setup (gas stove, utensils)", "priority": "P0", "cost_estimate": 1000, "status": "not_started"},
                {"name": "Fridge/freezer (12V/240V)", "priority": "P0", "cost_estimate": 1500, "status": "not_started"},
                {"name": "Rooftop tents (7+ capacity)", "priority": "P0", "cost_estimate": 3000, "status": "not_started"},
                {"name": "Motorbike #1", "priority": "P1", "cost_estimate": 5000, "status": "not_started"},
                {"name": "Motorbike #2", "priority": "P1", "cost_estimate": 5000, "status": "not_started"},
                {"name": "Motorbike mounting gear", "priority": "P1", "cost_estimate": 500, "status": "not_started"},
                {"name": "Tool kit (mechanical + electrical)", "priority": "P0", "cost_estimate": 1000, "status": "not_started"}
            ],
            "community": [
                {"name": "Portable solar setups (10x 100W kits)", "priority": "P1", "cost_estimate": 2000, "status": "not_started"},
                {"name": "Battery banks (portable, 500Wh+ each x10)", "priority": "P1", "cost_estimate": 3000, "status": "not_started"},
                {"name": "LED lighting systems", "priority": "P1", "cost_estimate": 500, "status": "not_started"},
                {"name": "Tents (10+ person capacity)", "priority": "P1", "cost_estimate": 2000, "status": "not_started"},
                {"name": "Canned food storage (3+ months)", "priority": "P0", "cost_estimate": 2000, "status": "not_started"},
                {"name": "Seeds (heirloom, diverse)", "priority": "P1", "cost_estimate": 300, "status": "not_started"},
                {"name": "Water purification (filters, tablets, UV)", "priority": "P0", "cost_estimate": 500, "status": "not_started"},
                {"name": "Medical supplies (comprehensive)", "priority": "P0", "cost_estimate": 1500, "status": "not_started"},
                {"name": "Organic/medicinal supplies", "priority": "P1", "cost_estimate": 800, "status": "not_started"},
                {"name": "Backup generators (2x)", "priority": "P1", "cost_estimate": 2000, "status": "not_started"},
                {"name": "Communications gear (radios, LoRa)", "priority": "P1", "cost_estimate": 1000, "status": "not_started"}
            ],
            "license": [
                {"name": "Driving license renewal", "priority": "P0", "cost_estimate": 100, "status": "not_started", "notes": "PRIORITY #1"},
                {"name": "Heavy vehicle license (if needed)", "priority": "P0", "cost_estimate": 500, "status": "not_started"},
                {"name": "Trailer license/endorsement", "priority": "P0", "cost_estimate": 200, "status": "not_started"},
                {"name": "Vehicle insurance", "priority": "P0", "cost_estimate": 3000, "status": "not_started", "yearly": 3000},
                {"name": "Trailer insurance", "priority": "P0", "cost_estimate": 800, "status": "not_started", "yearly": 800},
                {"name": "Equipment insurance", "priority": "P1", "cost_estimate": 1000, "status": "not_started", "yearly": 1000},
                {"name": "Vehicle registration", "priority": "P0", "cost_estimate": 500, "status": "not_started", "yearly": 500}
            ]
        }
    
    def load_data(self):
        """Load tracker data from disk"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r') as f:
                    saved_data = json.load(f)
                    # Merge saved status into equipment
                    for category, items in saved_data.get("equipment", {}).items():
                        if category in self.equipment:
                            for i, item in enumerate(items):
                                if i < len(self.equipment[category]):
                                    self.equipment[category][i].update({
                                        "status": item.get("status", "not_started"),
                                        "notes": item.get("notes", ""),
                                        "acquired_date": item.get("acquired_date"),
                                        "actual_cost": item.get("actual_cost")
                                    })
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_data(self):
        """Save tracker data to disk"""
        data = {
            "last_updated": datetime.utcnow().isoformat(),
            "equipment": self.equipment
        }
        with open(self.data_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def update_item_status(self, category: str, item_name: str, status: str, 
                          actual_cost: Optional[float] = None, notes: Optional[str] = None):
        """Update equipment item status"""
        if category not in self.equipment:
            print(f"❌ Unknown category: {category}")
            return
        
        for item in self.equipment[category]:
            if item_name.lower() in item["name"].lower():
                item["status"] = status
                if actual_cost is not None:
                    item["actual_cost"] = actual_cost
                if notes:
                    item["notes"] = notes
                if status == "acquired":
                    item["acquired_date"] = datetime.utcnow().isoformat()
                
                self.save_data()
                print(f"✅ Updated: {item['name']} → {status}")
                return
        
        print(f"❌ Item not found: {item_name}")
    
    def get_budget_summary(self) -> Dict:
        """Calculate budget summary"""
        summary = {
            "total_estimate": 0,
            "total_actual": 0,
            "total_monthly": 0,
            "total_yearly": 0,
            "by_category": {},
            "by_status": {},
            "by_priority": {}
        }
        
        for category, items in self.equipment.items():
            cat_estimate = 0
            cat_actual = 0
            
            for item in items:
                estimate = item.get("cost_estimate", 0)
                actual = item.get("actual_cost", estimate)
                status = item.get("status", "not_started")
                priority = item.get("priority", "P3")
                
                summary["total_estimate"] += estimate
                
                if status in ["acquired", "installed"]:
                    summary["total_actual"] += actual
                    cat_actual += actual
                
                cat_estimate += estimate
                
                # Monthly/yearly costs
                if "monthly" in item:
                    summary["total_monthly"] += item["monthly"]
                if "yearly" in item:
                    summary["total_yearly"] += item["yearly"]
                
                # By status
                summary["by_status"][status] = summary["by_status"].get(status, 0) + 1
                
                # By priority
                summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
            
            summary["by_category"][category] = {
                "estimate": cat_estimate,
                "actual": cat_actual,
                "items": len(items)
            }
        
        return summary
    
    def generate_checklist_report(self) -> str:
        """Generate human-readable checklist report"""
        summary = self.get_budget_summary()
        
        report = []
        report.append("=" * 70)
        report.append("📋 MOBILE CITADEL EQUIPMENT CHECKLIST")
        report.append("=" * 70)
        
        # Budget overview
        report.append(f"\n💰 Budget Overview:")
        report.append(f"  Total Estimated: ${summary['total_estimate']:,}")
        report.append(f"  Total Spent: ${summary['total_actual']:,}")
        report.append(f"  Remaining: ${summary['total_estimate'] - summary['total_actual']:,}")
        if summary['total_monthly']:
            report.append(f"  Monthly Costs: ${summary['total_monthly']:,}/month")
        if summary['total_yearly']:
            report.append(f"  Yearly Costs: ${summary['total_yearly']:,}/year")
        
        # Progress by status
        report.append(f"\n📊 Progress:")
        for status, count in sorted(summary['by_status'].items()):
            status_emoji = {
                "not_started": "⬜",
                "researching": "🔍",
                "quoted": "💬",
                "ordered": "📦",
                "acquired": "✅",
                "installed": "🔧"
            }.get(status, "❓")
            report.append(f"  {status_emoji} {status.replace('_', ' ').title()}: {count}")
        
        # By category
        report.append(f"\n📦 By Category:")
        for category, data in summary['by_category'].items():
            percent = (data['actual'] / data['estimate'] * 100) if data['estimate'] > 0 else 0
            report.append(f"\n  {category.upper()}:")
            report.append(f"    Estimate: ${data['estimate']:,}")
            report.append(f"    Spent: ${data['actual']:,} ({percent:.1f}%)")
            report.append(f"    Items: {data['items']}")
        
        # P0 items not acquired
        report.append(f"\n🎯 Priority P0 Items Not Acquired:")
        p0_missing = []
        for category, items in self.equipment.items():
            for item in items:
                if item.get("priority") == "P0" and item.get("status") not in ["acquired", "installed"]:
                    p0_missing.append(f"  ⚠️  [{category.upper()}] {item['name']} (${item.get('cost_estimate', 0):,})")
        
        if p0_missing:
            report.extend(p0_missing)
        else:
            report.append("  ✅ All P0 items acquired!")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def main():
    """Main execution"""
    import sys
    
    tracker = EquipmentTracker()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "report":
            print(tracker.generate_checklist_report())
        
        elif command == "budget":
            summary = tracker.get_budget_summary()
            print(json.dumps(summary, indent=2))
        
        elif command == "update":
            # update <category> "<item_name>" <status> [actual_cost]
            if len(sys.argv) >= 5:
                category = sys.argv[2]
                item_name = sys.argv[3]
                status = sys.argv[4]
                actual_cost = float(sys.argv[5]) if len(sys.argv) > 5 else None
                tracker.update_item_status(category, item_name, status, actual_cost)
            else:
                print("Usage: equipment_tracker.py update <category> '<item_name>' <status> [actual_cost]")
        
        else:
            print(f"Unknown command: {command}")
            print("\nUsage: equipment_tracker.py [report|budget|update]")
    else:
        # Default: show report
        print(tracker.generate_checklist_report())


if __name__ == "__main__":
    main()
