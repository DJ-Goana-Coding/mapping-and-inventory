#!/usr/bin/env python3
"""
LAPTOP DESKTOP FORENSIC SCANNER
Sovereign Directive: Locate MASTER_MERGE_2.ps1 and MASTER_SYSTEM_MAP_2.csv
Target: Laptop Desktop spoke

Usage:
    python laptop_desktop_scanner.py --scan ~/Desktop
    python laptop_desktop_scanner.py --scan ~/Desktop --ingest-map
"""

import os
import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
import sys


class DesktopForensicScanner:
    """Forensic scanner for Laptop Desktop - locates MASTER_MERGE_2 artifacts"""
    
    def __init__(self):
        self.artifacts = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "target": "Laptop Desktop Spoke",
            "artifacts_found": [],
            "master_merge_script": None,
            "master_system_map": None
        }
    
    def scan_desktop(self, desktop_path):
        """Scan Desktop directory for MASTER_MERGE_2 artifacts"""
        print(f"\n🔍 FORENSIC SCAN: {desktop_path}")
        print("=" * 60)
        
        desktop = Path(desktop_path).expanduser()
        
        if not desktop.exists():
            print(f"❌ Desktop path not found: {desktop}")
            return False
        
        print("🎯 Target Artifacts:")
        print("  • MASTER_MERGE_2.ps1 - PowerShell merge script")
        print("  • MASTER_SYSTEM_MAP_2.csv - Unified system map")
        print()
        
        # Search for artifacts
        for item in desktop.rglob("*"):
            if item.is_file():
                filename_lower = item.name.lower()
                
                # Check for MASTER_MERGE_2.ps1
                if "master_merge" in filename_lower and item.suffix == ".ps1":
                    self.artifacts["master_merge_script"] = {
                        "path": str(item),
                        "size_bytes": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat() + "Z"
                    }
                    self.artifacts["artifacts_found"].append("MASTER_MERGE_2.ps1")
                    print(f"✅ FOUND: {item.name}")
                    print(f"   Path: {item}")
                    print(f"   Size: {item.stat().st_size} bytes")
                
                # Check for MASTER_SYSTEM_MAP_2.csv
                if "master_system_map" in filename_lower and item.suffix == ".csv":
                    self.artifacts["master_system_map"] = {
                        "path": str(item),
                        "size_bytes": item.stat().st_size,
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat() + "Z"
                    }
                    self.artifacts["artifacts_found"].append("MASTER_SYSTEM_MAP_2.csv")
                    print(f"✅ FOUND: {item.name}")
                    print(f"   Path: {item}")
                    print(f"   Size: {item.stat().st_size} bytes")
        
        if len(self.artifacts["artifacts_found"]) == 0:
            print("⚠️  No MASTER_MERGE_2 artifacts found on Desktop")
            return False
        
        print(f"\n✅ Located {len(self.artifacts['artifacts_found'])} artifact(s)")
        return True
    
    def ingest_master_system_map(self):
        """Ingest MASTER_SYSTEM_MAP_2.csv into Citadel format"""
        if not self.artifacts["master_system_map"]:
            print("\n❌ MASTER_SYSTEM_MAP_2.csv not found. Run scan first.")
            return False
        
        print("\n📥 INGESTING MASTER_SYSTEM_MAP_2.csv")
        print("=" * 60)
        
        map_path = Path(self.artifacts["master_system_map"]["path"])
        
        try:
            # Read CSV
            entities = []
            with open(map_path, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    # Convert CSV row to Citadel entity format
                    entity = {
                        "type": "laptop_desktop_entity",
                        "source": "MASTER_MERGE_2",
                        "full_name": row.get("FullName", ""),
                        "keyword": row.get("Keyword", ""),
                        "directory": row.get("Directory", ""),
                        "extension": row.get("Extension", ""),
                        "size_bytes": int(row.get("Length", 0)) if row.get("Length", "").isdigit() else 0,
                        "modified": row.get("LastWriteTime", ""),
                        "ingested_at": self.artifacts["scan_timestamp"]
                    }
                    entities.append(entity)
            
            print(f"✅ Parsed {len(entities)} entities from CSV")
            
            # Deduplicate by FullName and Keyword (as per PowerShell logic)
            seen = set()
            deduplicated = []
            
            for entity in entities:
                key = (entity["full_name"], entity["keyword"])
                if key not in seen:
                    seen.add(key)
                    deduplicated.append(entity)
            
            removed = len(entities) - len(deduplicated)
            if removed > 0:
                print(f"🧹 Removed {removed} duplicates")
            
            # Save to laptop_inventory
            output_dir = Path("data/laptop_inventory")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            output_file = output_dir / "master_system_map_2.json"
            manifest = {
                "import_timestamp": self.artifacts["scan_timestamp"],
                "source": "MASTER_MERGE_2.ps1",
                "hostname": "laptop_desktop",
                "total_entities": len(deduplicated),
                "entities": deduplicated
            }
            
            with open(output_file, 'w') as f:
                json.dump(manifest, f, indent=2)
            
            print(f"✅ Manifest saved: {output_file}")
            print(f"   Entities: {len(deduplicated)}")
            
            # Generate summary report
            extensions = {}
            for entity in deduplicated:
                ext = entity.get("extension", "unknown")
                extensions[ext] = extensions.get(ext, 0) + 1
            
            print("\n📊 Entity Breakdown:")
            for ext, count in sorted(extensions.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {ext}: {count}")
            
            return True
        
        except Exception as e:
            print(f"❌ Error ingesting CSV: {e}")
            return False
    
    def save_scan_report(self, output_path):
        """Save scan report"""
        with open(output_path, 'w') as f:
            json.dump(self.artifacts, f, indent=2)
        
        print(f"\n✅ Scan report saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Laptop Desktop Forensic Scanner")
    parser.add_argument("--scan", required=True, help="Desktop directory to scan")
    parser.add_argument("--ingest-map", action="store_true",
                       help="Ingest MASTER_SYSTEM_MAP_2.csv after finding it")
    parser.add_argument("--output", default="laptop_desktop_scan.json",
                       help="Output scan report file")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🛡️ LAPTOP DESKTOP FORENSIC SCANNER")
    print("   Sovereign Directive: Locate MASTER_MERGE_2 Artifacts")
    print("=" * 60)
    
    scanner = DesktopForensicScanner()
    
    # Scan Desktop
    found = scanner.scan_desktop(args.scan)
    
    # Optionally ingest the map
    if found and args.ingest_map and scanner.artifacts["master_system_map"]:
        scanner.ingest_master_system_map()
    
    # Save scan report
    scanner.save_scan_report(args.output)
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    
    if found:
        print("1. Review the ingested manifest in data/laptop_inventory/")
        print("2. Commit and push to trigger laptop_push_workflow")
        print("3. The Surveyor will merge into global inventory")
        print("4. The Librarian will validate Apps Script toolbox connection")
    else:
        print("1. Verify the Desktop path is correct")
        print("2. Check if MASTER_MERGE_2.ps1 has been run")
        print("3. Look for MASTER_SYSTEM_MAP_2.csv in alternate locations")
    
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
