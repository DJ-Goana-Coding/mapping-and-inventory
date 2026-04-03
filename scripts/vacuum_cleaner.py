#!/usr/bin/env python3
"""
VACUUM CLEANER
Cleanup and deduplication worker
Removes duplicate entries, identifies stale resources, compresses old manifests

Usage:
    python vacuum_cleaner.py --deduplicate
    python vacuum_cleaner.py --compress-old
    python vacuum_cleaner.py --full-clean
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import shutil


class VacuumCleaner:
    """Cleanup and deduplication worker"""
    
    def __init__(self):
        self.master_inventory_file = Path("master_inventory.json")
        self.archive_dir = Path("Archive_Vault/vacuum_archive")
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def deduplicate_inventory(self):
        """Remove duplicate entries from master inventory"""
        print("\n🧹 Deduplicating master inventory...")
        
        if not self.master_inventory_file.exists():
            print("❌ Master inventory not found")
            return
        
        with open(self.master_inventory_file, 'r') as f:
            inventory = json.load(f)
        
        original_count = len(inventory.get("entities", []))
        
        # Deduplicate based on type and path
        seen = set()
        deduplicated = []
        
        for entity in inventory.get("entities", []):
            key = (entity.get("type"), entity.get("path"))
            
            if key not in seen:
                seen.add(key)
                deduplicated.append(entity)
        
        removed_count = original_count - len(deduplicated)
        
        if removed_count > 0:
            # Backup original
            backup_file = self.archive_dir / f"master_inventory_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
            shutil.copy(self.master_inventory_file, backup_file)
            print(f"📦 Backup saved: {backup_file}")
            
            # Save deduplicated
            inventory["entities"] = deduplicated
            inventory["last_updated"] = datetime.utcnow().isoformat() + "Z"
            
            with open(self.master_inventory_file, 'w') as f:
                json.dump(inventory, f, indent=2)
            
            print(f"✅ Removed {removed_count} duplicates")
            print(f"   Original: {original_count} entities")
            print(f"   Deduplicated: {len(deduplicated)} entities")
        else:
            print("✅ No duplicates found")
    
    def identify_stale_resources(self):
        """Identify resources that haven't been modified in 90+ days"""
        print("\n🔍 Identifying stale resources...")
        
        if not self.master_inventory_file.exists():
            print("❌ Master inventory not found")
            return
        
        with open(self.master_inventory_file, 'r') as f:
            inventory = json.load(f)
        
        stale_threshold = datetime.utcnow() - timedelta(days=90)
        stale_resources = []
        
        for entity in inventory.get("entities", []):
            modified_str = entity.get("modified", "")
            if modified_str:
                try:
                    # Parse ISO timestamp
                    modified_date = datetime.fromisoformat(modified_str.replace('Z', '+00:00'))
                    
                    if modified_date < stale_threshold:
                        stale_resources.append({
                            "path": entity.get("path", "unknown"),
                            "type": entity.get("type", "unknown"),
                            "modified": modified_str,
                            "days_old": (datetime.utcnow() - modified_date.replace(tzinfo=None)).days
                        })
                except Exception:
                    pass
        
        if stale_resources:
            # Save stale resources report
            report_file = self.archive_dir / f"stale_resources_{datetime.utcnow().strftime('%Y%m%d')}.json"
            with open(report_file, 'w') as f:
                json.dump({
                    "scan_date": datetime.utcnow().isoformat() + "Z",
                    "threshold_days": 90,
                    "total_stale": len(stale_resources),
                    "resources": stale_resources
                }, f, indent=2)
            
            print(f"⚠️  Found {len(stale_resources)} stale resources")
            print(f"   Report saved: {report_file}")
        else:
            print("✅ No stale resources found")
    
    def compress_old_manifests(self):
        """Archive manifests older than 30 days"""
        print("\n📦 Compressing old manifests...")
        
        manifests_dir = Path("data/gdrive_manifests")
        if not manifests_dir.exists():
            print("⚠️  No manifests directory found")
            return
        
        archive_threshold = datetime.utcnow() - timedelta(days=30)
        archived_count = 0
        
        for manifest_file in manifests_dir.glob("*.json"):
            if manifest_file.name in ["master_gdrive_index.json", "discovered_docs.json"]:
                continue  # Keep these
            
            try:
                # Check file age
                mtime = datetime.fromtimestamp(manifest_file.stat().st_mtime)
                
                if mtime < archive_threshold:
                    # Move to archive
                    archive_subdir = self.archive_dir / "old_manifests"
                    archive_subdir.mkdir(parents=True, exist_ok=True)
                    
                    archive_path = archive_subdir / manifest_file.name
                    shutil.move(str(manifest_file), str(archive_path))
                    
                    archived_count += 1
                    print(f"  📦 Archived: {manifest_file.name}")
            
            except Exception as e:
                print(f"⚠️  Error archiving {manifest_file}: {e}")
        
        if archived_count > 0:
            print(f"✅ Archived {archived_count} old manifest(s)")
        else:
            print("✅ No old manifests to archive")
    
    def full_clean(self):
        """Run all cleanup operations"""
        print("\n" + "=" * 60)
        print("🧹 VACUUM CLEANER - FULL CLEAN")
        print("=" * 60)
        
        self.deduplicate_inventory()
        self.identify_stale_resources()
        self.compress_old_manifests()
        
        print("\n" + "=" * 60)
        print("✅ FULL CLEAN COMPLETE")
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Vacuum Cleaner - Cleanup Worker")
    parser.add_argument("--deduplicate", action="store_true",
                       help="Deduplicate master inventory")
    parser.add_argument("--stale", action="store_true",
                       help="Identify stale resources")
    parser.add_argument("--compress-old", action="store_true",
                       help="Compress old manifests")
    parser.add_argument("--full-clean", action="store_true",
                       help="Run all cleanup operations")
    
    args = parser.parse_args()
    
    vacuum = VacuumCleaner()
    
    if args.full_clean:
        vacuum.full_clean()
    else:
        if args.deduplicate:
            vacuum.deduplicate_inventory()
        
        if args.stale:
            vacuum.identify_stale_resources()
        
        if args.compress_old:
            vacuum.compress_old_manifests()
        
        if not any([args.deduplicate, args.stale, args.compress_old]):
            parser.print_help()


if __name__ == "__main__":
    main()
