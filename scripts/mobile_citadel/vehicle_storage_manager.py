#!/usr/bin/env python3
"""
🚗 VEHICLE STORAGE PARTITION MANAGER
Mobile Citadel Command Center - Off-Grid Storage Management

Manages vehicle-based storage partitions for offline operations.
Implements the `/vehicle-storage/` partition layout for mobile Citadel nodes.
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class VehicleStorageManager:
    """Manages vehicle storage partitions for off-grid operations"""
    
    def __init__(self, base_path: str = "/vehicle-storage"):
        self.base_path = Path(base_path)
        self.partitions = {
            "repos-cache": "All GitHub repos cloned for offline work",
            "models-offline": "ML models for offline inference",
            "datasets-local": "Trading data, research datasets",
            "workers-archive": "Apps Script workers backup",
            "gdrive-manifests": "Partition metadata snapshots",
            "discovery-logs": "Scouting data queued for upload",
            "sync-queue": "Pending commits/artifacts"
        }
        self.manifest_file = self.base_path / "vehicle_manifest.json"
        
    def initialize_storage(self):
        """Initialize all storage partitions"""
        print("🚗 Initializing Vehicle Storage Partitions...")
        
        for partition, description in self.partitions.items():
            partition_path = self.base_path / partition
            partition_path.mkdir(parents=True, exist_ok=True)
            
            # Create README in each partition
            readme_path = partition_path / "README.md"
            if not readme_path.exists():
                with open(readme_path, 'w') as f:
                    f.write(f"# {partition}\n\n")
                    f.write(f"{description}\n\n")
                    f.write(f"Created: {datetime.utcnow().isoformat()}\n")
            
            print(f"  ✅ {partition}/")
        
        # Generate initial manifest
        self.generate_manifest()
        print(f"\n✅ Vehicle storage initialized at {self.base_path}")
    
    def generate_manifest(self) -> Dict:
        """Generate storage manifest with usage statistics"""
        manifest = {
            "generated_at": datetime.utcnow().isoformat(),
            "base_path": str(self.base_path),
            "partitions": {},
            "total_size_mb": 0,
            "total_files": 0
        }
        
        for partition in self.partitions.keys():
            partition_path = self.base_path / partition
            
            if partition_path.exists():
                # Calculate partition statistics
                total_size = 0
                file_count = 0
                
                for item in partition_path.rglob("*"):
                    if item.is_file():
                        file_count += 1
                        try:
                            total_size += item.stat().st_size
                        except (OSError, PermissionError):
                            pass
                
                manifest["partitions"][partition] = {
                    "path": str(partition_path),
                    "size_mb": round(total_size / (1024 * 1024), 2),
                    "file_count": file_count,
                    "description": self.partitions[partition]
                }
                
                manifest["total_size_mb"] += manifest["partitions"][partition]["size_mb"]
                manifest["total_files"] += file_count
        
        # Save manifest
        self.manifest_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest
    
    def get_partition_path(self, partition: str) -> Path:
        """Get path to specific partition"""
        if partition not in self.partitions:
            raise ValueError(f"Unknown partition: {partition}")
        return self.base_path / partition
    
    def clone_repo_to_cache(self, repo_url: str, repo_name: str) -> bool:
        """Clone a repository to repos-cache partition"""
        cache_path = self.get_partition_path("repos-cache")
        repo_path = cache_path / repo_name
        
        if repo_path.exists():
            print(f"  ℹ️  {repo_name} already cached")
            return True
        
        print(f"  📥 Cloning {repo_name}...")
        try:
            import subprocess
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=300
            )
            if result.returncode == 0:
                print(f"  ✅ {repo_name} cached")
                return True
            else:
                print(f"  ❌ Failed to clone {repo_name}: {result.stderr}")
                return False
        except (subprocess.SubprocessError, subprocess.TimeoutExpired) as e:
            print(f"  ❌ Error cloning {repo_name}: {e}")
            return False
    
    def save_gdrive_manifest(self, manifest_name: str, manifest_data: Dict):
        """Save GDrive partition manifest"""
        manifests_path = self.get_partition_path("gdrive-manifests")
        manifest_file = manifests_path / f"{manifest_name}.json"
        
        with open(manifest_file, 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        print(f"  ✅ GDrive manifest saved: {manifest_name}")
    
    def queue_discovery(self, discovery_type: str, data: Dict):
        """Queue discovery data for upload when online"""
        discovery_path = self.get_partition_path("discovery-logs")
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        discovery_file = discovery_path / f"{discovery_type}_{timestamp}.json"
        
        with open(discovery_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"  ✅ Discovery queued: {discovery_type}")
    
    def get_storage_report(self) -> str:
        """Generate human-readable storage report"""
        manifest = self.generate_manifest()
        
        report = []
        report.append("=" * 60)
        report.append("🚗 VEHICLE STORAGE REPORT")
        report.append("=" * 60)
        report.append(f"Generated: {manifest['generated_at']}")
        report.append(f"Base Path: {manifest['base_path']}")
        report.append(f"\nTotal Storage: {manifest['total_size_mb']:.2f} MB")
        report.append(f"Total Files: {manifest['total_files']:,}")
        
        report.append(f"\nPartitions:")
        for partition, info in manifest['partitions'].items():
            report.append(f"\n  📁 {partition}/")
            report.append(f"     Size: {info['size_mb']:.2f} MB")
            report.append(f"     Files: {info['file_count']:,}")
            report.append(f"     {info['description']}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def check_storage_health(self) -> Dict:
        """Check storage health and available space"""
        health = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "healthy",
            "warnings": [],
            "errors": []
        }
        
        # Check if base path exists
        if not self.base_path.exists():
            health["status"] = "error"
            health["errors"].append(f"Base path does not exist: {self.base_path}")
            return health
        
        # Check available disk space
        try:
            stat = shutil.disk_usage(self.base_path)
            available_gb = stat.free / (1024**3)
            used_percent = (stat.used / stat.total) * 100
            
            health["disk_space"] = {
                "total_gb": round(stat.total / (1024**3), 2),
                "used_gb": round(stat.used / (1024**3), 2),
                "free_gb": round(available_gb, 2),
                "used_percent": round(used_percent, 1)
            }
            
            if available_gb < 5:
                health["status"] = "warning"
                health["warnings"].append(f"Low disk space: {available_gb:.1f} GB available")
            
            if used_percent > 90:
                health["status"] = "warning"
                health["warnings"].append(f"Disk usage high: {used_percent:.1f}%")
        
        except OSError as e:
            health["errors"].append(f"Cannot check disk space: {e}")
        
        # Check partition accessibility
        for partition in self.partitions.keys():
            partition_path = self.get_partition_path(partition)
            if not partition_path.exists():
                health["warnings"].append(f"Partition missing: {partition}")
        
        return health


def main():
    """Main execution - manage vehicle storage"""
    import sys
    
    # Use default path or override from env/args
    base_path = os.environ.get("VEHICLE_STORAGE_PATH", "/tmp/vehicle-storage")
    manager = VehicleStorageManager(base_path=base_path)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "init":
            manager.initialize_storage()
        
        elif command == "report":
            print(manager.get_storage_report())
        
        elif command == "health":
            health = manager.check_storage_health()
            print(json.dumps(health, indent=2))
        
        elif command == "manifest":
            manifest = manager.generate_manifest()
            print(json.dumps(manifest, indent=2))
        
        else:
            print(f"Unknown command: {command}")
            print("\nUsage: vehicle_storage_manager.py [init|report|health|manifest]")
    else:
        # Default: initialize and show report
        if not manager.base_path.exists():
            manager.initialize_storage()
        print(manager.get_storage_report())


if __name__ == "__main__":
    main()
