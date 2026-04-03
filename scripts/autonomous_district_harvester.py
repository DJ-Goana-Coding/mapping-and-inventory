#!/usr/bin/env python3
"""
📂 AUTONOMOUS DISTRICT HARVESTER
Sovereign District Artifact Generator for Q.G.T.N.L. Command Citadel

Purpose: Automatically generate and maintain District artifacts
Version: 25.0.OMNI+

This worker autonomously generates:
- TREE.md (hierarchical file structure)
- INVENTORY.json (complete artifact registry)
- SCAFFOLD.md (architectural overview)

For all Districts (D01-D12, RESEARCH) in the Citadel Mesh.
"""

import os
import sys
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/district_harvester.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DistrictHarvester:
    """
    Autonomous District Artifact Generator
    
    Scans District directories and generates standardized artifacts
    following Section 142 Cycle and Surveyor protocols.
    """
    
    def __init__(self, districts_file: str = "districts.json"):
        self.districts_file = districts_file
        self.districts = self.load_districts()
        self.repo_root = Path.cwd()
        
        # Create logs directory
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        logger.info("📂 District Harvester initialized")
        logger.info(f"📋 Loaded {len(self.districts)} districts")
    
    def load_districts(self) -> List[Dict]:
        """Load districts from registry"""
        try:
            with open(self.districts_file, 'r') as f:
                data = json.load(f)
                districts = data.get("districts", [])
                logger.info(f"✅ Loaded {len(districts)} districts from registry")
                return districts
        except FileNotFoundError:
            logger.error(f"❌ Districts file not found: {self.districts_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON in districts file: {e}")
            return []
    
    def generate_tree(self, district_path: Path) -> str:
        """
        Generate TREE.md for a district
        
        Returns hierarchical file structure in markdown format
        """
        logger.info(f"🌳 Generating TREE.md for {district_path}")
        
        def scan_directory(path: Path, prefix: str = "", is_last: bool = True) -> List[str]:
            """Recursively scan directory and build tree"""
            lines = []
            
            try:
                items = sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
                
                for i, item in enumerate(items):
                    is_last_item = (i == len(items) - 1)
                    connector = "└── " if is_last_item else "├── "
                    
                    # Skip hidden files and common excludes
                    if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', '.git']:
                        continue
                    
                    if item.is_dir():
                        lines.append(f"{prefix}{connector}📁 {item.name}/")
                        
                        # Recursively scan subdirectories
                        extension = "    " if is_last_item else "│   "
                        lines.extend(scan_directory(item, prefix + extension, is_last_item))
                    else:
                        # Determine file type emoji
                        emoji = self.get_file_emoji(item.suffix)
                        lines.append(f"{prefix}{connector}{emoji} {item.name}")
            
            except PermissionError:
                lines.append(f"{prefix}❌ [Permission Denied]")
            
            return lines
        
        # Build tree
        tree_lines = [
            f"# 🌳 TREE - {district_path.name}",
            f"**Generated:** {datetime.now().isoformat()}",
            f"**Authority:** Citadel Architect v25.0.OMNI",
            "",
            "```",
            f"📁 {district_path.name}/"
        ]
        
        tree_lines.extend(scan_directory(district_path))
        tree_lines.append("```")
        
        return "\n".join(tree_lines)
    
    def get_file_emoji(self, suffix: str) -> str:
        """Get appropriate emoji for file type"""
        emoji_map = {
            '.md': '📄',
            '.json': '📋',
            '.py': '🐍',
            '.sh': '🐚',
            '.yml': '⚙️',
            '.yaml': '⚙️',
            '.txt': '📝',
            '.csv': '📊',
            '.js': '📜',
            '.ts': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.jpg': '🖼️',
            '.png': '🖼️',
            '.pdf': '📕',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦'
        }
        return emoji_map.get(suffix.lower(), '📄')
    
    def generate_inventory(self, district_path: Path) -> Dict:
        """
        Generate INVENTORY.json for a district
        
        Returns complete artifact registry with metadata
        """
        logger.info(f"📋 Generating INVENTORY.json for {district_path}")
        
        inventory = {
            "district": district_path.name,
            "generated": datetime.now().isoformat(),
            "version": "25.0.OMNI",
            "artifacts": [],
            "statistics": {
                "total_files": 0,
                "total_directories": 0,
                "total_size_bytes": 0,
                "file_types": {}
            }
        }
        
        def scan_for_inventory(path: Path):
            """Recursively scan and build inventory"""
            try:
                for item in path.iterdir():
                    # Skip hidden and excluded items
                    if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', '.git']:
                        continue
                    
                    if item.is_dir():
                        inventory["statistics"]["total_directories"] += 1
                        scan_for_inventory(item)
                    else:
                        # Add file to inventory
                        try:
                            stat = item.stat()
                            file_size = stat.st_size
                            
                            # Calculate MD5 hash for small files (<10MB)
                            file_hash = None
                            if file_size < 10 * 1024 * 1024:
                                try:
                                    with open(item, 'rb') as f:
                                        file_hash = hashlib.md5(f.read()).hexdigest()
                                except Exception:
                                    pass
                            
                            artifact = {
                                "path": str(item.relative_to(district_path)),
                                "name": item.name,
                                "type": "file",
                                "extension": item.suffix,
                                "size_bytes": file_size,
                                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                                "md5": file_hash
                            }
                            
                            inventory["artifacts"].append(artifact)
                            inventory["statistics"]["total_files"] += 1
                            inventory["statistics"]["total_size_bytes"] += file_size
                            
                            # Track file types
                            ext = item.suffix or "no_extension"
                            inventory["statistics"]["file_types"][ext] = \
                                inventory["statistics"]["file_types"].get(ext, 0) + 1
                        
                        except Exception as e:
                            logger.warning(f"⚠️ Could not process file {item}: {e}")
            
            except PermissionError:
                logger.warning(f"⚠️ Permission denied: {path}")
        
        scan_for_inventory(district_path)
        
        return inventory
    
    def generate_scaffold(self, district_path: Path, district_info: Dict) -> str:
        """
        Generate SCAFFOLD.md for a district
        
        Returns high-level architectural overview
        """
        logger.info(f"🏗️ Generating SCAFFOLD.md for {district_path}")
        
        pillar = district_info.get("pillar", "UNKNOWN")
        description = district_info.get("description", "No description available")
        
        scaffold = f"""# 🏗️ SCAFFOLD - {district_path.name}

**Generated:** {datetime.now().isoformat()}  
**Authority:** Citadel Architect v25.0.OMNI  
**Pillar:** {pillar}

---

## 📋 DISTRICT OVERVIEW

{description}

---

## 🎯 CORE FUNCTIONS

1. **Primary Role:** {district_info.get("primary_role", "TBD")}
2. **Secondary Role:** {district_info.get("secondary_role", "TBD")}
3. **Integration:** {district_info.get("integration", "TBD")}

---

## 📊 CURRENT STATUS

- **Operational Status:** {district_info.get("status", "PENDING")}
- **Artifact Completeness:** Checking...
- **Last Harvest:** {datetime.now().isoformat()}

---

## 🔗 CONNECTIONS

**Upstream Dependencies:**
{self.format_list(district_info.get("upstream_deps", []))}

**Downstream Consumers:**
{self.format_list(district_info.get("downstream_consumers", []))}

---

## 📁 ARTIFACT REGISTRY

Required artifacts for this district:
- ✅ TREE.md (hierarchical structure)
- ✅ INVENTORY.json (complete registry)
- ✅ SCAFFOLD.md (this file)

---

## 🚀 AUTOMATION PROTOCOLS

**Harvesting:**
- Frequency: Every 24 hours
- Method: Autonomous District Harvester
- Workflow: `bridge_push.yml`

**Sync:**
- Target: master_inventory.json
- Aggregator: `librarian_consolidator.py`
- Workflow: `master_harvester.yml`

---

## 📞 SUPPORT

**Architect:** Citadel Architect v25.0.OMNI  
**Surveyor:** Mapping Hub Harvester  
**Oracle:** TIA-ARCHITECT-CORE

---

**Last Updated:** {datetime.now().isoformat()}
"""
        return scaffold
    
    def format_list(self, items: List[str]) -> str:
        """Format list for markdown"""
        if not items:
            return "- None"
        return "\n".join(f"- {item}" for item in items)
    
    def harvest_district(self, district_info: Dict) -> bool:
        """Harvest a single district and generate all artifacts"""
        district_id = district_info.get("id")
        district_path = self.repo_root / district_info.get("path", f"Districts/{district_id}")
        
        logger.info(f"🔍 Harvesting district: {district_id} at {district_path}")
        
        # Check if district exists
        if not district_path.exists():
            logger.warning(f"⚠️ District path does not exist: {district_path}")
            return False
        
        try:
            # Generate TREE.md
            tree_content = self.generate_tree(district_path)
            tree_path = district_path / "TREE.md"
            with open(tree_path, 'w') as f:
                f.write(tree_content)
            logger.info(f"✅ Generated TREE.md")
            
            # Generate INVENTORY.json
            inventory_data = self.generate_inventory(district_path)
            inventory_path = district_path / "INVENTORY.json"
            with open(inventory_path, 'w') as f:
                json.dump(inventory_data, f, indent=2)
            logger.info(f"✅ Generated INVENTORY.json")
            
            # Generate SCAFFOLD.md
            scaffold_content = self.generate_scaffold(district_path, district_info)
            scaffold_path = district_path / "SCAFFOLD.md"
            with open(scaffold_path, 'w') as f:
                f.write(scaffold_content)
            logger.info(f"✅ Generated SCAFFOLD.md")
            
            logger.info(f"🎉 Successfully harvested {district_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to harvest {district_id}: {e}")
            return False
    
    def harvest_all(self) -> Dict[str, bool]:
        """Harvest all districts"""
        logger.info("🚀 Starting harvest of all districts")
        
        results = {}
        
        for district_info in self.districts:
            district_id = district_info.get("id")
            success = self.harvest_district(district_info)
            results[district_id] = success
        
        # Summary
        total = len(results)
        succeeded = sum(1 for v in results.values() if v)
        
        logger.info(f"✅ Harvest complete: {succeeded}/{total} districts succeeded")
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous District Harvester for Q.G.T.N.L. Command Citadel"
    )
    parser.add_argument(
        "--district",
        type=str,
        help="Harvest a specific district by ID (e.g., D01)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Harvest all districts"
    )
    
    args = parser.parse_args()
    
    harvester = DistrictHarvester()
    
    if args.district:
        # Harvest specific district
        district_info = next(
            (d for d in harvester.districts if d.get("id") == args.district),
            None
        )
        if district_info:
            harvester.harvest_district(district_info)
        else:
            logger.error(f"❌ District not found: {args.district}")
    elif args.all:
        # Harvest all districts
        harvester.harvest_all()
    else:
        # Default: harvest all
        harvester.harvest_all()


if __name__ == "__main__":
    main()
