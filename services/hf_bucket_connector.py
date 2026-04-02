#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
SERVICES — HF BUCKET CONNECTOR
═══════════════════════════════════════════════════════════════════════════════

HuggingFace Storage Bucket Integration

PURPOSE:
  Provides connectivity to the HuggingFace Space Storage Bucket, enabling the
  storage and retrieval of the 321GB Research/ cargo without Git LFS limits.
  This bypasses the "Wizard Mafia's" 404 errors by using persistent storage.

FUNCTIONALITY:
  - Detect bucket mount points (/data/ or /mnt/storage/)
  - Prioritize bucket-stored master_inventory.json over repo version
  - Provide health monitoring for bucket sync operations
  - Enable Research/ cargo access without Git limitations

INTEGRATION:
  - Used by Librarian tab for inventory search priority
  - Used by D12 Master Overseer for health monitoring
  - Integrated with tia_citadel_deep_scan.yml workflow

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Any


# Possible bucket mount points
BUCKET_MOUNT_POINTS = [
    "/data",
    "/mnt/storage",
    "/persistent-storage",
    "/storage"
]


class HFBucketConnector:
    """
    HuggingFace Storage Bucket connector
    
    Manages connection to HF Space Storage Bucket for persistent 321GB cargo.
    """
    
    def __init__(self):
        self.connector_id = "hf_bucket_primary"
        self.bucket_path = None
        self.bucket_available = False
        self.detect_bucket()
    
    def detect_bucket(self) -> bool:
        """
        Detect if HF Storage Bucket is mounted
        
        Returns:
            True if bucket is available, False otherwise
        """
        for mount_point in BUCKET_MOUNT_POINTS:
            if os.path.exists(mount_point) and os.path.isdir(mount_point):
                # Verify it's writable
                try:
                    test_file = Path(mount_point) / ".bucket_test"
                    test_file.touch()
                    test_file.unlink()
                    self.bucket_path = mount_point
                    self.bucket_available = True
                    print(f"✅ HF Storage Bucket detected at: {mount_point}")
                    return True
                except (PermissionError, OSError):
                    continue
        
        print("⚠️  HF Storage Bucket not detected - using local storage only")
        return False
    
    def get_bucket_inventory_path(self) -> Optional[Path]:
        """
        Get path to master_inventory.json in bucket (priority location)
        
        Returns:
            Path to bucket inventory or None if not available
        """
        if not self.bucket_available or not self.bucket_path:
            return None
        
        inventory_path = Path(self.bucket_path) / "master_inventory.json"
        if inventory_path.exists():
            return inventory_path
        
        return None
    
    def get_research_cargo_path(self) -> Optional[Path]:
        """
        Get path to Research/ directory in bucket (321GB cargo)
        
        Returns:
            Path to bucket Research/ directory or None if not available
        """
        if not self.bucket_available or not self.bucket_path:
            return None
        
        research_path = Path(self.bucket_path) / "Research"
        if research_path.exists() and research_path.is_dir():
            return research_path
        
        return None
    
    def load_bucket_inventory(self) -> Optional[List[Dict[str, Any]]]:
        """
        Load master_inventory.json from bucket (priority source)
        
        Returns:
            Inventory data or None if not available
        """
        inventory_path = self.get_bucket_inventory_path()
        if not inventory_path:
            return None
        
        try:
            with open(inventory_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                print(f"✅ Loaded {len(data)} entities from bucket inventory")
                return data
            elif isinstance(data, dict):
                # Flatten if nested
                items = []
                for k, v in data.items():
                    if isinstance(v, list):
                        items.extend(v)
                    else:
                        items.append({"key": k, **v} if isinstance(v, dict) else {"key": k, "value": v})
                print(f"✅ Loaded {len(items)} entities from bucket inventory (flattened)")
                return items
            
            return []
        except Exception as e:
            print(f"⚠️  Failed to load bucket inventory: {e}")
            return None
    
    def get_bucket_status(self) -> Dict[str, Any]:
        """
        Get comprehensive bucket status
        
        Returns:
            Dictionary with bucket health and availability info
        """
        status = {
            "available": self.bucket_available,
            "mount_point": self.bucket_path,
            "inventory_available": False,
            "research_cargo_available": False,
            "inventory_count": 0,
            "research_size_gb": 0
        }
        
        if not self.bucket_available:
            return status
        
        # Check inventory
        inventory_path = self.get_bucket_inventory_path()
        if inventory_path:
            status["inventory_available"] = True
            try:
                inventory = self.load_bucket_inventory()
                if inventory:
                    status["inventory_count"] = len(inventory)
            except Exception:
                pass
        
        # Check Research/ cargo
        research_path = self.get_research_cargo_path()
        if research_path:
            status["research_cargo_available"] = True
            try:
                # Calculate size
                total_size = 0
                for root, dirs, files in os.walk(research_path):
                    for file in files:
                        filepath = os.path.join(root, file)
                        if os.path.exists(filepath):
                            total_size += os.path.getsize(filepath)
                status["research_size_gb"] = round(total_size / (1024**3), 2)
            except Exception:
                pass
        
        return status
    
    def sync_inventory_to_repo(self, repo_root: Path) -> bool:
        """
        Sync bucket inventory back to repo root (for Git commits)
        
        Args:
            repo_root: Path to repository root
        
        Returns:
            True if sync successful, False otherwise
        """
        inventory_path = self.get_bucket_inventory_path()
        if not inventory_path:
            return False
        
        try:
            repo_inventory = repo_root / "master_inventory.json"
            with open(inventory_path, 'r') as src:
                data = json.load(src)
            with open(repo_inventory, 'w') as dst:
                json.dump(data, dst, indent=2)
            print(f"✅ Synced bucket inventory to repo: {repo_inventory}")
            return True
        except Exception as e:
            print(f"❌ Failed to sync bucket inventory to repo: {e}")
            return False


def get_bucket_connector() -> HFBucketConnector:
    """
    Get singleton instance of HFBucketConnector
    
    Returns:
        HFBucketConnector instance
    """
    if not hasattr(get_bucket_connector, "_instance"):
        get_bucket_connector._instance = HFBucketConnector()
    return get_bucket_connector._instance


if __name__ == "__main__":
    print("═" * 70)
    print("HF BUCKET CONNECTOR — Diagnostics")
    print("═" * 70)
    
    connector = HFBucketConnector()
    status = connector.get_bucket_status()
    
    print("\nBucket Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n" + "═" * 70)
