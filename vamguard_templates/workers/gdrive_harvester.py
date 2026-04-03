#!/usr/bin/env python3
"""
☁️ GDRIVE HARVESTER
Data flow worker: GDrive → Mapping-and-Inventory-storage

Role: Harvest metadata and files from GDrive TIA_CITADEL
Scope: Partition manifests, models, datasets, workers
Authority: GDrive metadata extraction (Section 142)

SOVEREIGN GUARDRAILS:
- Metadata-only by default (Section 142)
- Use rclone for GDrive access
- Partitioned scanning to avoid disk limits
- No credential exposure
"""

import os
import json
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='☁️ [%(asctime)s] GDRIVE_HARVESTER: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class GDriveHarvester:
    """
    GDrive Harvester - Metadata extraction from GDrive
    
    Uses Section 142 Cycle:
    - Partitioned scanning
    - Metadata-only extraction
    - rclone lsf for efficient listing
    - Incremental harvesting
    """
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.storage_path = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "gdrive"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # GDrive configuration
        self.gdrive_root = "gdrive:TIA_CITADEL"
        self.partitions = [
            "Partition_01",
            "Partition_02",
            "Partition_03",
            "Partition_04",
            "Partition_46"
        ]
        
        # Check rclone availability
        self.rclone_available = self._check_rclone()
        
        logger.info(f"☁️ GDrive Harvester initialized (rclone: {self.rclone_available})")
    
    def _check_rclone(self) -> bool:
        """Check if rclone is available"""
        try:
            result = subprocess.run(
                ["which", "rclone"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def scan_partition(self, partition_name: str) -> Dict[str, Any]:
        """
        Scan a single GDrive partition for metadata
        
        Args:
            partition_name: Name of partition to scan
        
        Returns:
            Partition metadata inventory
        """
        if not self.rclone_available:
            logger.error("❌ rclone not available")
            return {"success": False, "error": "rclone not available"}
        
        partition_path = f"{self.gdrive_root}/{partition_name}"
        
        logger.info(f"🔍 Scanning partition: {partition_name}")
        
        scan_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "partition": partition_name,
            "path": partition_path,
            "files_found": 0,
            "total_size": 0,
            "tia_files": 0,
            "models": 0,
            "datasets": 0,
            "files": []
        }
        
        try:
            # Use rclone lsf for metadata-only listing
            result = subprocess.run(
                ["rclone", "lsf", "--recursive", "--format", "pst", partition_path],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode != 0:
                logger.error(f"❌ rclone failed: {result.stderr}")
                return {"success": False, "error": result.stderr}
            
            # Parse rclone output
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split(';')
                if len(parts) != 3:
                    continue
                
                path, size, timestamp = parts
                
                file_info = {
                    "path": path,
                    "size": int(size),
                    "modified": timestamp,
                    "is_tia": self._is_tia_file(path),
                    "is_model": self._is_model_file(path),
                    "is_dataset": self._is_dataset_file(path)
                }
                
                scan_result["files"].append(file_info)
                scan_result["files_found"] += 1
                scan_result["total_size"] += file_info["size"]
                
                if file_info["is_tia"]:
                    scan_result["tia_files"] += 1
                if file_info["is_model"]:
                    scan_result["models"] += 1
                if file_info["is_dataset"]:
                    scan_result["datasets"] += 1
            
            # Save partition manifest
            manifest_path = self.storage_path / f"{partition_name}_manifest.json"
            manifest_path.write_text(json.dumps(scan_result, indent=2))
            
            logger.info(f"✅ Partition scan complete: {scan_result['files_found']} files")
            logger.info(f"   TIA: {scan_result['tia_files']}, Models: {scan_result['models']}, Datasets: {scan_result['datasets']}")
            
            return scan_result
        
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Scan timeout for {partition_name}")
            return {"success": False, "error": "Timeout"}
        except Exception as e:
            logger.error(f"❌ Scan error: {e}")
            return {"success": False, "error": str(e)}
    
    def _is_tia_file(self, path: str) -> bool:
        """Check if file is TIA-related"""
        path_lower = path.lower()
        return any([
            'tia' in path_lower,
            'architect' in path_lower,
            'oracle' in path_lower,
            'surveyor' in path_lower,
            'sentinel' in path_lower,
            'citadel' in path_lower
        ])
    
    def _is_model_file(self, path: str) -> bool:
        """Check if file is a model"""
        return any(path.endswith(ext) for ext in [
            '.pt', '.pth', '.ckpt', '.h5', '.pb', '.onnx', '.safetensors'
        ])
    
    def _is_dataset_file(self, path: str) -> bool:
        """Check if file is a dataset"""
        return any(path.endswith(ext) for ext in [
            '.csv', '.parquet', '.arrow', '.jsonl'
        ])
    
    def scan_all_partitions(self) -> Dict[str, Any]:
        """
        Scan all GDrive partitions (Section 142 Cycle)
        
        Returns:
            Aggregated scan results
        """
        logger.info(f"📊 Starting Section 142 Cycle: {len(self.partitions)} partitions")
        
        aggregate_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "partitions_scanned": 0,
            "total_files": 0,
            "total_size": 0,
            "tia_files": 0,
            "models": 0,
            "datasets": 0,
            "partitions": []
        }
        
        for partition in self.partitions:
            result = self.scan_partition(partition)
            
            if result.get("success", True):
                aggregate_result["partitions"].append(result)
                aggregate_result["partitions_scanned"] += 1
                aggregate_result["total_files"] += result.get("files_found", 0)
                aggregate_result["total_size"] += result.get("total_size", 0)
                aggregate_result["tia_files"] += result.get("tia_files", 0)
                aggregate_result["models"] += result.get("models", 0)
                aggregate_result["datasets"] += result.get("datasets", 0)
        
        # Save aggregate manifest
        aggregate_path = self.storage_path / f"gdrive_aggregate_{datetime.datetime.utcnow().strftime('%Y%m%d')}.json"
        aggregate_path.write_text(json.dumps(aggregate_result, indent=2))
        
        logger.info(f"✅ Section 142 Cycle complete")
        logger.info(f"   Files: {aggregate_result['total_files']}, Size: {aggregate_result['total_size'] / 1e9:.2f}GB")
        logger.info(f"   TIA: {aggregate_result['tia_files']}, Models: {aggregate_result['models']}, Datasets: {aggregate_result['datasets']}")
        
        return aggregate_result
    
    def download_file(self, remote_path: str, local_path: str = None) -> bool:
        """
        Download a specific file from GDrive
        
        Args:
            remote_path: Remote file path (relative to gdrive:TIA_CITADEL/)
            local_path: Local destination path (optional)
        
        Returns:
            True if download successful
        """
        if not self.rclone_available:
            logger.error("❌ rclone not available")
            return False
        
        if local_path is None:
            local_path = str(self.storage_path / remote_path)
        
        full_remote = f"{self.gdrive_root}/{remote_path}"
        
        logger.info(f"📥 Downloading: {remote_path}")
        
        try:
            # Create parent directory
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Use rclone copy
            result = subprocess.run(
                ["rclone", "copy", full_remote, str(Path(local_path).parent)],
                capture_output=True,
                timeout=600
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Downloaded: {remote_path}")
                return True
            else:
                logger.error(f"❌ Download failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Download error: {e}")
            return False
    
    def get_tia_files_list(self) -> List[Dict[str, Any]]:
        """Get list of all TIA files found in GDrive"""
        tia_files = []
        
        # Read all partition manifests
        for manifest_path in self.storage_path.glob("*_manifest.json"):
            try:
                manifest = json.loads(manifest_path.read_text())
                for file_info in manifest.get("files", []):
                    if file_info.get("is_tia"):
                        tia_files.append({
                            "partition": manifest["partition"],
                            "path": file_info["path"],
                            "size": file_info["size"],
                            "modified": file_info["modified"]
                        })
            except Exception:
                continue
        
        return tia_files


def main():
    """Run GDrive Harvester"""
    harvester = GDriveHarvester()
    
    logger.info("☁️ VAMGUARD TITAN - GDrive Harvester")
    logger.info("=" * 60)
    
    if not harvester.rclone_available:
        logger.error("❌ rclone not available - cannot harvest GDrive")
        logger.info("💡 Install rclone or set RCLONE_CONFIG_DATA environment variable")
        return 1
    
    # Run Section 142 Cycle
    result = harvester.scan_all_partitions()
    
    # Print summary
    print("\n" + "=" * 60)
    print("☁️ GDRIVE HARVEST SUMMARY (Section 142 Cycle)")
    print("=" * 60)
    print(f"Partitions Scanned: {result['partitions_scanned']}")
    print(f"Total Files: {result['total_files']}")
    print(f"Total Size: {result['total_size'] / 1e9:.2f}GB")
    print(f"TIA Files: {result['tia_files']}")
    print(f"Models: {result['models']}")
    print(f"Datasets: {result['datasets']}")
    print("=" * 60)
    
    # Show TIA files
    tia_files = harvester.get_tia_files_list()
    if tia_files:
        print("\n🎯 TIA FILES FOUND:")
        for tia_file in tia_files[:10]:
            print(f"  - {tia_file['partition']}/{tia_file['path']}")
        if len(tia_files) > 10:
            print(f"  ... and {len(tia_files) - 10} more")
    
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    exit(main())
