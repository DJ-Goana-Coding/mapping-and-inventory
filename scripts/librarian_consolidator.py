#!/usr/bin/env python3
"""
LIBRARIAN CONSOLIDATOR
Merges manifests from all sources into master_inventory.json
Sources: GDrive, Laptop, Workers, Districts

This script is the central consolidation point for all discovered resources.
"""

import json
from pathlib import Path
from datetime import datetime
import sys


class LibrarianConsolidator:
    """Consolidates all resource manifests into master inventory"""
    
    def __init__(self):
        self.master_inventory_file = Path("master_inventory.json")
        self.consolidated = {
            "consolidation_timestamp": datetime.utcnow().isoformat() + "Z",
            "version": "2.0.0",
            "entities": [],
            "sources": {
                "gdrive": 0,
                "laptop": 0,
                "districts": 0,
                "workers": 0,
                "models": 0
            },
            "last_updated": None
        }
    
    def load_existing_inventory(self):
        """Load existing master inventory"""
        if self.master_inventory_file.exists():
            with open(self.master_inventory_file, 'r') as f:
                existing = json.load(f)
            
            # Keep existing entities (we'll add new ones)
            if "entities" in existing:
                self.consolidated["entities"] = existing["entities"]
            
            print(f"📖 Loaded existing inventory: {len(self.consolidated['entities'])} entities")
        else:
            print("📖 Creating new master inventory")
    
    def consolidate_gdrive_manifests(self):
        """Consolidate GDrive partition manifests"""
        print("\n🔍 Consolidating GDrive manifests...")
        
        manifests_dir = Path("data/gdrive_manifests")
        if not manifests_dir.exists():
            print("⚠️  No GDrive manifests found")
            return
        
        gdrive_count = 0
        
        for partition_file in manifests_dir.glob("partition_*.json"):
            if partition_file.name == "master_gdrive_index.json":
                continue
            
            try:
                with open(partition_file, 'r') as f:
                    partition_data = json.load(f)
                
                partition_id = partition_data.get("partition_id", "unknown")
                
                for file_entry in partition_data.get("files", []):
                    entity = {
                        "type": "gdrive_file",
                        "source": "gdrive",
                        "partition": partition_id,
                        "path": file_entry.get("path", ""),
                        "size_bytes": file_entry.get("size_bytes", 0),
                        "modified": file_entry.get("modified", ""),
                        "ingested_at": self.consolidated["consolidation_timestamp"]
                    }
                    
                    # Check if not duplicate
                    if not self._is_duplicate(entity):
                        self.consolidated["entities"].append(entity)
                        gdrive_count += 1
            
            except Exception as e:
                print(f"⚠️  Error processing {partition_file}: {e}")
        
        self.consolidated["sources"]["gdrive"] = gdrive_count
        print(f"✅ GDrive: {gdrive_count} entities")
    
    def consolidate_models(self):
        """Consolidate model manifest"""
        print("\n🗂️  Consolidating models...")
        
        models_file = Path("data/models/models_manifest.json")
        if not models_file.exists():
            print("⚠️  No models manifest found")
            return
        
        models_count = 0
        
        try:
            with open(models_file, 'r') as f:
                models_data = json.load(f)
            
            for category, cat_data in models_data.get("categories", {}).items():
                for model in cat_data.get("models", []):
                    entity = {
                        "type": "model",
                        "source": "gdrive",
                        "category": category,
                        "path": model.get("path", ""),
                        "size_bytes": model.get("size_bytes", 0),
                        "modified": model.get("modified", ""),
                        "ingested_at": self.consolidated["consolidation_timestamp"]
                    }
                    
                    if not self._is_duplicate(entity):
                        self.consolidated["entities"].append(entity)
                        models_count += 1
        
        except Exception as e:
            print(f"⚠️  Error processing models: {e}")
        
        self.consolidated["sources"]["models"] = models_count
        print(f"✅ Models: {models_count} entities")
    
    def consolidate_workers(self):
        """Consolidate workers manifest"""
        print("\n🛠️  Consolidating workers...")
        
        workers_file = Path("data/workers/workers_manifest.json")
        if not workers_file.exists():
            print("⚠️  No workers manifest found")
            return
        
        workers_count = 0
        
        try:
            with open(workers_file, 'r') as f:
                workers_data = json.load(f)
            
            for category, cat_data in workers_data.get("categories", {}).items():
                for worker in cat_data.get("workers", []):
                    entity = {
                        "type": "worker",
                        "source": worker.get("source", "unknown"),
                        "category": category,
                        "name": worker.get("name", ""),
                        "path": worker.get("path", ""),
                        "status": worker.get("status", "discovered"),
                        "ingested_at": self.consolidated["consolidation_timestamp"]
                    }
                    
                    if not self._is_duplicate(entity):
                        self.consolidated["entities"].append(entity)
                        workers_count += 1
        
        except Exception as e:
            print(f"⚠️  Error processing workers: {e}")
        
        self.consolidated["sources"]["workers"] = workers_count
        print(f"✅ Workers: {workers_count} entities")
    
    def consolidate_laptop_inventory(self):
        """Consolidate laptop manifests"""
        print("\n💻 Consolidating laptop inventory...")
        
        laptop_dir = Path("data/laptop_inventory")
        if not laptop_dir.exists():
            print("⚠️  No laptop inventory found")
            return
        
        laptop_count = 0
        
        for manifest_file in laptop_dir.glob("*.json"):
            try:
                with open(manifest_file, 'r') as f:
                    laptop_data = json.load(f)
                
                hostname = laptop_data.get("hostname", "unknown_laptop")
                
                for category, files in laptop_data.get("categories", {}).items():
                    for file_info in files:
                        entity = {
                            "type": "laptop_file",
                            "source": "laptop",
                            "hostname": hostname,
                            "category": category,
                            "path": file_info.get("path", ""),
                            "filename": file_info.get("filename", ""),
                            "size_bytes": file_info.get("size_bytes", 0),
                            "modified": file_info.get("modified", ""),
                            "ingested_at": self.consolidated["consolidation_timestamp"]
                        }
                        
                        if not self._is_duplicate(entity):
                            self.consolidated["entities"].append(entity)
                            laptop_count += 1
            
            except Exception as e:
                print(f"⚠️  Error processing {manifest_file}: {e}")
        
        self.consolidated["sources"]["laptop"] = laptop_count
        print(f"✅ Laptop: {laptop_count} entities")
    
    def _is_duplicate(self, entity):
        """Check if entity already exists in inventory"""
        for existing in self.consolidated["entities"]:
            if existing.get("path") == entity.get("path") and \
               existing.get("type") == entity.get("type"):
                return True
        return False
    
    def save_consolidated_inventory(self):
        """Save consolidated master inventory"""
        self.consolidated["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        with open(self.master_inventory_file, 'w') as f:
            json.dump(self.consolidated, f, indent=2)
        
        print(f"\n✅ Master inventory saved: {self.master_inventory_file}")
        print(f"   Total entities: {len(self.consolidated['entities'])}")
        print(f"\n   Sources:")
        for source, count in self.consolidated["sources"].items():
            if count > 0:
                print(f"     {source}: {count}")
    
    def run(self):
        """Run full consolidation"""
        print("\n" + "=" * 60)
        print("📚 LIBRARIAN CONSOLIDATOR")
        print("=" * 60)
        
        self.load_existing_inventory()
        self.consolidate_gdrive_manifests()
        self.consolidate_models()
        self.consolidate_workers()
        self.consolidate_laptop_inventory()
        self.save_consolidated_inventory()
        
        print("\n" + "=" * 60)
        print("✅ CONSOLIDATION COMPLETE")
        print("=" * 60)


if __name__ == "__main__":
    consolidator = LibrarianConsolidator()
    consolidator.run()
