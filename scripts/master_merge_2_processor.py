#!/usr/bin/env python3
"""
🎯 MASTER_MERGE_2 PRIORITY PROCESSOR
Locates and processes MASTER_MERGE_2 artifacts FIRST
Uses it as a guide to discover additional laptop data locations

Usage:
    python scripts/master_merge_2_processor.py
    python scripts/master_merge_2_processor.py --desktop ~/Desktop
"""

import os
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
import sys


class MasterMerge2Processor:
    """Priority processor for MASTER_MERGE_2 artifacts"""
    
    def __init__(self, desktop_path=None):
        self.desktop_path = Path(desktop_path or Path.home() / "Desktop").expanduser()
        self.repo_root = Path(__file__).parent.parent
        self.output_dir = self.repo_root / "data" / "laptop_inventory"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.artifacts = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "desktop_path": str(self.desktop_path),
            "master_merge_script": None,
            "master_system_map": None,
            "discovered_paths": [],
            "total_entities": 0
        }
    
    def find_master_merge_2(self):
        """Find MASTER_MERGE_2.ps1 and MASTER_SYSTEM_MAP_2.csv"""
        print("\n" + "=" * 70)
        print("🎯 PRIORITY: Locating MASTER_MERGE_2 Artifacts")
        print("=" * 70)
        print(f"\n🔍 Searching Desktop: {self.desktop_path}")
        
        if not self.desktop_path.exists():
            print(f"❌ Desktop not found: {self.desktop_path}")
            print("\n💡 TIP: Specify desktop path with --desktop flag")
            return False
        
        # Search for PowerShell script
        print("\n📜 Searching for MASTER_MERGE_2.ps1...")
        for item in self.desktop_path.rglob("*.ps1"):
            if "master_merge" in item.name.lower():
                self.artifacts["master_merge_script"] = {
                    "path": str(item),
                    "size_bytes": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat() + "Z"
                }
                print(f"✅ FOUND: {item.name}")
                print(f"   Location: {item}")
                print(f"   Size: {item.stat().st_size:,} bytes")
                print(f"   Modified: {datetime.fromtimestamp(item.stat().st_mtime)}")
                break
        
        # Search for CSV map
        print("\n🗺️  Searching for MASTER_SYSTEM_MAP_2.csv...")
        for item in self.desktop_path.rglob("*.csv"):
            if "master_system_map" in item.name.lower():
                self.artifacts["master_system_map"] = {
                    "path": str(item),
                    "size_bytes": item.stat().st_size,
                    "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat() + "Z"
                }
                print(f"✅ FOUND: {item.name}")
                print(f"   Location: {item}")
                print(f"   Size: {item.stat().st_size:,} bytes")
                print(f"   Modified: {datetime.fromtimestamp(item.stat().st_mtime)}")
                break
        
        if not self.artifacts["master_merge_script"] and not self.artifacts["master_system_map"]:
            print("\n⚠️  MASTER_MERGE_2 artifacts not found on Desktop")
            print("\n💡 NEXT STEPS:")
            print("   1. Check if MASTER_MERGE_2.ps1 has been run")
            print("   2. Look for these files in alternate locations")
            print("   3. Verify Desktop path is correct")
            return False
        
        return True
    
    def extract_powershell_paths(self):
        """Extract file paths from PowerShell script"""
        if not self.artifacts["master_merge_script"]:
            return []
        
        print("\n" + "=" * 70)
        print("📜 Extracting Paths from PowerShell Script")
        print("=" * 70)
        
        script_path = Path(self.artifacts["master_merge_script"]["path"])
        paths = []
        
        try:
            content = script_path.read_text(encoding='utf-8', errors='ignore')
            
            # Look for common PowerShell path patterns
            import re
            
            # Pattern 1: Get-ChildItem paths
            get_childitem_pattern = r'Get-ChildItem\s+(?:-Path\s+)?["\']?([^"\']+)["\']?'
            matches = re.findall(get_childitem_pattern, content, re.IGNORECASE)
            paths.extend(matches)
            
            # Pattern 2: Direct path assignments
            path_assignment_pattern = r'\$\w+\s*=\s*["\']([^"\']+)["\']'
            matches = re.findall(path_assignment_pattern, content)
            paths.extend(matches)
            
            # Pattern 3: Export-Csv paths
            export_csv_pattern = r'Export-Csv\s+(?:-Path\s+)?["\']?([^"\']+)["\']?'
            matches = re.findall(export_csv_pattern, content, re.IGNORECASE)
            paths.extend(matches)
            
            # Clean and deduplicate paths
            unique_paths = list(set([p.strip() for p in paths if p.strip()]))
            
            print(f"\n✅ Extracted {len(unique_paths)} unique paths from PowerShell script:")
            for path in unique_paths[:10]:  # Show first 10
                print(f"   📂 {path}")
            if len(unique_paths) > 10:
                print(f"   ... and {len(unique_paths) - 10} more")
            
            self.artifacts["discovered_paths"] = unique_paths
            return unique_paths
        
        except Exception as e:
            print(f"❌ Error reading PowerShell script: {e}")
            return []
    
    def process_master_system_map(self):
        """Process MASTER_SYSTEM_MAP_2.csv and extract intelligence"""
        if not self.artifacts["master_system_map"]:
            print("\n⚠️  MASTER_SYSTEM_MAP_2.csv not found")
            return None
        
        print("\n" + "=" * 70)
        print("🗺️  Processing MASTER_SYSTEM_MAP_2.csv")
        print("=" * 70)
        
        map_path = Path(self.artifacts["master_system_map"]["path"])
        
        try:
            entities = []
            directories_found = set()
            extensions_found = {}
            keywords_found = {}
            
            with open(map_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                
                print("\n📊 Analyzing CSV structure...")
                fieldnames = reader.fieldnames
                print(f"   Columns: {', '.join(fieldnames)}")
                
                for row in reader:
                    # Extract entity data
                    entity = {
                        "full_name": row.get("FullName", ""),
                        "keyword": row.get("Keyword", ""),
                        "directory": row.get("Directory", ""),
                        "extension": row.get("Extension", ""),
                        "size_bytes": int(row.get("Length", 0)) if row.get("Length", "").isdigit() else 0,
                        "modified": row.get("LastWriteTime", "")
                    }
                    
                    entities.append(entity)
                    
                    # Track directories
                    if entity["directory"]:
                        directories_found.add(entity["directory"])
                    
                    # Track extensions
                    ext = entity["extension"]
                    extensions_found[ext] = extensions_found.get(ext, 0) + 1
                    
                    # Track keywords
                    kw = entity["keyword"]
                    if kw:
                        keywords_found[kw] = keywords_found.get(kw, 0) + 1
            
            self.artifacts["total_entities"] = len(entities)
            
            print(f"\n✅ Processed {len(entities):,} entities from CSV")
            
            # Show top directories
            print(f"\n📂 Unique Directories Found: {len(directories_found)}")
            for directory in sorted(list(directories_found))[:10]:
                print(f"   • {directory}")
            if len(directories_found) > 10:
                print(f"   ... and {len(directories_found) - 10} more")
            
            # Show top extensions
            print(f"\n📄 Top File Types:")
            sorted_extensions = sorted(extensions_found.items(), key=lambda x: x[1], reverse=True)
            for ext, count in sorted_extensions[:10]:
                print(f"   • {ext}: {count:,} files")
            
            # Show top keywords
            if keywords_found:
                print(f"\n🏷️  Top Keywords:")
                sorted_keywords = sorted(keywords_found.items(), key=lambda x: x[1], reverse=True)
                for kw, count in sorted_keywords[:10]:
                    print(f"   • {kw}: {count:,} occurrences")
            
            # Save processed data
            output = {
                "import_timestamp": self.artifacts["scan_timestamp"],
                "source": "MASTER_MERGE_2.ps1",
                "total_entities": len(entities),
                "unique_directories": len(directories_found),
                "unique_extensions": len(extensions_found),
                "directories": sorted(list(directories_found)),
                "extensions": extensions_found,
                "keywords": keywords_found,
                "entities": entities
            }
            
            output_file = self.output_dir / "master_system_map_2.json"
            with open(output_file, 'w') as f:
                json.dump(output, f, indent=2)
            
            print(f"\n✅ Saved to: {output_file}")
            
            return output
        
        except Exception as e:
            print(f"❌ Error processing CSV: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_scan_guide(self, map_data):
        """Generate a guide for what to scan based on MASTER_MERGE_2 data"""
        print("\n" + "=" * 70)
        print("🎯 Generating Scan Guide from MASTER_MERGE_2 Intelligence")
        print("=" * 70)
        
        guide = {
            "generated": datetime.utcnow().isoformat() + "Z",
            "source": "MASTER_MERGE_2 Analysis",
            "priority_directories": [],
            "priority_extensions": [],
            "priority_keywords": [],
            "recommended_actions": []
        }
        
        if map_data:
            # Priority directories (top 20)
            directories = map_data.get("directories", [])
            guide["priority_directories"] = directories[:20]
            
            # Priority extensions (top 10)
            extensions = map_data.get("extensions", {})
            sorted_ext = sorted(extensions.items(), key=lambda x: x[1], reverse=True)
            guide["priority_extensions"] = [ext for ext, _ in sorted_ext[:10]]
            
            # Priority keywords (top 10)
            keywords = map_data.get("keywords", {})
            sorted_kw = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
            guide["priority_keywords"] = [kw for kw, _ in sorted_kw[:10]]
        
        # Add PowerShell discovered paths
        if self.artifacts["discovered_paths"]:
            guide["powershell_paths"] = self.artifacts["discovered_paths"]
        
        # Recommended actions
        guide["recommended_actions"] = [
            "Scan priority directories for additional files",
            "Focus on priority file extensions",
            "Search for files containing priority keywords",
            "Use MASTER_SYSTEM_MAP_2 as ground truth for inventory",
            "Cross-reference with current filesystem state"
        ]
        
        # Save guide
        guide_file = self.output_dir / "master_merge_2_scan_guide.json"
        with open(guide_file, 'w') as f:
            json.dump(guide, f, indent=2)
        
        print(f"\n✅ Scan Guide Generated: {guide_file}")
        
        print(f"\n📋 PRIORITY SCAN TARGETS:")
        print(f"\n   📂 Top Directories ({len(guide['priority_directories'])}):")
        for directory in guide["priority_directories"][:5]:
            print(f"      • {directory}")
        
        print(f"\n   📄 Top Extensions ({len(guide['priority_extensions'])}):")
        for ext in guide["priority_extensions"][:5]:
            print(f"      • {ext}")
        
        if guide.get("priority_keywords"):
            print(f"\n   🏷️  Top Keywords ({len(guide['priority_keywords'])}):")
            for kw in guide["priority_keywords"][:5]:
                print(f"      • {kw}")
        
        return guide
    
    def save_summary(self):
        """Save processing summary"""
        summary_file = self.output_dir / "master_merge_2_summary.json"
        
        with open(summary_file, 'w') as f:
            json.dump(self.artifacts, f, indent=2)
        
        print(f"\n✅ Summary saved: {summary_file}")


def main():
    parser = argparse.ArgumentParser(
        description="MASTER_MERGE_2 Priority Processor - Examine FIRST"
    )
    parser.add_argument(
        "--desktop",
        help="Desktop directory path (default: ~/Desktop)",
        default=None
    )
    
    args = parser.parse_args()
    
    print("\n" + "=" * 70)
    print("🎯 MASTER_MERGE_2 PRIORITY PROCESSOR")
    print("   Intelligence-First Laptop Data Discovery")
    print("=" * 70)
    
    processor = MasterMerge2Processor(args.desktop)
    
    # Step 1: Find MASTER_MERGE_2 artifacts
    found = processor.find_master_merge_2()
    
    if not found:
        print("\n" + "=" * 70)
        print("⚠️  MASTER_MERGE_2 artifacts not found")
        print("=" * 70)
        print("\nContinuing with standard scan...")
        sys.exit(1)
    
    # Step 2: Extract paths from PowerShell script
    processor.extract_powershell_paths()
    
    # Step 3: Process CSV map
    map_data = processor.process_master_system_map()
    
    # Step 4: Generate scan guide
    if map_data:
        processor.generate_scan_guide(map_data)
    
    # Step 5: Save summary
    processor.save_summary()
    
    # Final output
    print("\n" + "=" * 70)
    print("✅ MASTER_MERGE_2 PROCESSING COMPLETE")
    print("=" * 70)
    
    print(f"\n📊 DISCOVERY SUMMARY:")
    print(f"   • PowerShell Script: {'✅ Found' if processor.artifacts['master_merge_script'] else '❌ Not Found'}")
    print(f"   • System Map CSV: {'✅ Found' if processor.artifacts['master_system_map'] else '❌ Not Found'}")
    print(f"   • Paths Discovered: {len(processor.artifacts['discovered_paths'])}")
    print(f"   • Total Entities: {processor.artifacts['total_entities']:,}")
    
    print(f"\n📁 OUTPUT FILES:")
    print(f"   • data/laptop_inventory/master_system_map_2.json")
    print(f"   • data/laptop_inventory/master_merge_2_scan_guide.json")
    print(f"   • data/laptop_inventory/master_merge_2_summary.json")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review the scan guide: data/laptop_inventory/master_merge_2_scan_guide.json")
    print(f"   2. Use discovered paths to guide additional scanning")
    print(f"   3. Run full laptop sync: ./laptop_sync_orchestrator.sh")
    print(f"   4. Commit and push: git add data/ && git commit -m '🎯 MASTER_MERGE_2 intelligence' && git push")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
