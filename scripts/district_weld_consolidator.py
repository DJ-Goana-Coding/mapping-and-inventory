#!/usr/bin/env python3
"""
DISTRICT WELD CONSOLIDATOR
Citadel Architect — District Artifact Aggregation

Consolidates TREE.md and INVENTORY.json from all Districts into unified manifests.
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Repository root
repo_root = Path(__file__).parent.parent
os.chdir(repo_root)


class DistrictWeldConsolidator:
    """Consolidates District artifacts into unified manifests."""
    
    def __init__(self):
        self.timestamp = datetime.utcnow()
        self.districts_dir = repo_root / "Districts"
        self.output_dir = repo_root / "data" / "weld_manifests"
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.districts = []
        self.consolidated_inventory = {}
        self.consolidated_tree = {}
    
    def discover_districts(self) -> List[str]:
        """Discover all Districts."""
        if not self.districts_dir.exists():
            print(f"❌ Districts directory not found: {self.districts_dir}")
            return []
        
        districts = []
        for item in sorted(self.districts_dir.iterdir()):
            if item.is_dir() and item.name.startswith('D'):
                districts.append(item.name)
        
        print(f"📊 Discovered {len(districts)} Districts")
        return districts
    
    def load_inventory(self, district_name: str) -> Dict[str, Any]:
        """Load INVENTORY.json from a District."""
        inventory_path = self.districts_dir / district_name / "INVENTORY.json"
        
        if not inventory_path.exists():
            print(f"⚠️  {district_name}: INVENTORY.json not found")
            return {}
        
        try:
            with open(inventory_path, 'r') as f:
                inventory = json.load(f)
            print(f"✅ {district_name}: INVENTORY.json loaded")
            return inventory
        except Exception as e:
            print(f"❌ {district_name}: Failed to load INVENTORY.json: {e}")
            return {}
    
    def load_tree(self, district_name: str) -> str:
        """Load TREE.md from a District."""
        tree_path = self.districts_dir / district_name / "TREE.md"
        
        if not tree_path.exists():
            print(f"⚠️  {district_name}: TREE.md not found")
            return ""
        
        try:
            with open(tree_path, 'r') as f:
                tree_content = f.read()
            print(f"✅ {district_name}: TREE.md loaded")
            return tree_content
        except Exception as e:
            print(f"❌ {district_name}: Failed to load TREE.md: {e}")
            return ""
    
    def consolidate_inventories(self):
        """Consolidate all District inventories."""
        print("\n🔗 Consolidating District Inventories...")
        
        for district in self.districts:
            inventory = self.load_inventory(district)
            if inventory:
                self.consolidated_inventory[district] = inventory
        
        # Add metadata
        weld_manifest = {
            "timestamp": self.timestamp.isoformat() + 'Z',
            "weld_type": "district_inventory",
            "total_districts": len(self.districts),
            "consolidated_districts": len(self.consolidated_inventory),
            "districts": self.consolidated_inventory
        }
        
        # Save consolidated inventory
        output_path = self.output_dir / "consolidated_district_inventory.json"
        with open(output_path, 'w') as f:
            json.dump(weld_manifest, f, indent=2)
        
        print(f"✅ Consolidated inventory saved: {output_path}")
        return weld_manifest
    
    def consolidate_trees(self):
        """Consolidate all District trees."""
        print("\n🌲 Consolidating District Trees...")
        
        for district in self.districts:
            tree = self.load_tree(district)
            if tree:
                self.consolidated_tree[district] = tree
        
        # Create consolidated tree document
        consolidated_content = f"""# 🌲 CONSOLIDATED DISTRICT TREES
## TITAN 392 — Unified District Structure

**Timestamp:** {self.timestamp.isoformat()}Z  
**Total Districts:** {len(self.districts)}  
**Consolidated Districts:** {len(self.consolidated_tree)}

---

"""
        
        for district, tree_content in sorted(self.consolidated_tree.items()):
            consolidated_content += f"""## {district}

{tree_content}

---

"""
        
        # Save consolidated tree
        output_path = self.output_dir / "consolidated_district_trees.md"
        with open(output_path, 'w') as f:
            f.write(consolidated_content)
        
        print(f"✅ Consolidated trees saved: {output_path}")
        return consolidated_content
    
    def generate_weld_report(self):
        """Generate weld operation report."""
        print("\n📊 Generating Weld Report...")
        
        report = {
            "timestamp": self.timestamp.isoformat() + 'Z',
            "weld_operation": "district_consolidation",
            "status": "COMPLETE",
            "districts": {
                "total": len(self.districts),
                "inventories_consolidated": len(self.consolidated_inventory),
                "trees_consolidated": len(self.consolidated_tree)
            },
            "outputs": {
                "consolidated_inventory": str(self.output_dir / "consolidated_district_inventory.json"),
                "consolidated_trees": str(self.output_dir / "consolidated_district_trees.md"),
                "weld_report": str(self.output_dir / "district_weld_report.json")
            }
        }
        
        # Save report
        report_path = self.output_dir / "district_weld_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Weld report saved: {report_path}")
        return report
    
    def execute_weld(self):
        """Execute complete District weld operation."""
        print("\n🔥 DISTRICT WELD CONSOLIDATOR")
        print("=" * 60)
        
        # Discover Districts
        self.districts = self.discover_districts()
        
        if not self.districts:
            print("❌ No Districts found - aborting weld")
            return False
        
        # Consolidate inventories
        self.consolidate_inventories()
        
        # Consolidate trees
        self.consolidate_trees()
        
        # Generate report
        report = self.generate_weld_report()
        
        print("\n✅ DISTRICT WELD COMPLETE")
        print(f"   • Districts processed: {report['districts']['total']}")
        print(f"   • Inventories consolidated: {report['districts']['inventories_consolidated']}")
        print(f"   • Trees consolidated: {report['districts']['trees_consolidated']}")
        print(f"   • Output directory: {self.output_dir}")
        
        return True


def main():
    """Main execution."""
    consolidator = DistrictWeldConsolidator()
    success = consolidator.execute_weld()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
