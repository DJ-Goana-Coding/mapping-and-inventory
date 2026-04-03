#!/usr/bin/env python3
"""
💻 LAPTOP HARVESTER
Data flow worker: Laptop → Mapping-and-Inventory-storage

Role: Harvest data from laptop node and store in central storage
Scope: Files, metadata, code artifacts, models, datasets
Authority: Data ingestion and storage management

SOVEREIGN GUARDRAILS:
- Relative paths only
- No credential exposure
- Metadata-first approach
- Section 142 partitioned scanning
"""

import os
import json
import datetime
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='💻 [%(asctime)s] LAPTOP_HARVESTER: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class LaptopHarvester:
    """
    Laptop Harvester - Data flow from laptop to central storage
    
    Harvests:
    - Code repositories
    - TIA-related code files
    - Models and datasets
    - Configuration files
    - Documentation
    """
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.storage_path = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "laptop"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Harvest configuration
        self.config = {
            "harvest_patterns": [
                "**/*.py",
                "**/*.js",
                "**/*.json",
                "**/*.md",
                "**/*.yaml",
                "**/*.yml"
            ],
            "tia_patterns": [
                "**/tia*.py",
                "**/TIA*.py",
                "**/*architect*.py",
                "**/*oracle*.py",
                "**/*surveyor*.py"
            ],
            "exclude_dirs": [
                ".git",
                "node_modules",
                "__pycache__",
                ".venv",
                "venv"
            ]
        }
        
        self.harvest_count = 0
        self.tia_files_found = 0
        
        logger.info("💻 Laptop Harvester initialized")
    
    def scan_laptop_directory(self, laptop_path: str) -> Dict[str, Any]:
        """
        Scan laptop directory for files to harvest
        
        Args:
            laptop_path: Path to laptop source directory (relative or env var)
        
        Returns:
            Scan results with file inventory
        """
        # Get laptop path from environment or use provided
        if laptop_path.startswith("$"):
            laptop_path = os.environ.get(laptop_path[1:], "")
        
        if not laptop_path:
            logger.error("❌ No laptop path provided")
            return {"success": False, "error": "No laptop path"}
        
        source_path = Path(laptop_path)
        if not source_path.exists():
            logger.error(f"❌ Laptop path not found: {laptop_path}")
            return {"success": False, "error": "Path not found"}
        
        logger.info(f"🔍 Scanning laptop directory: {laptop_path}")
        
        scan_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "source": str(source_path),
            "files_found": 0,
            "tia_files": 0,
            "models_found": 0,
            "datasets_found": 0,
            "inventory": []
        }
        
        # Scan for files
        for pattern in self.config["harvest_patterns"]:
            for file_path in source_path.rglob(pattern):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in self.config["exclude_dirs"]):
                    continue
                
                # Skip if file is too large (>50MB)
                if file_path.stat().st_size > 50 * 1024 * 1024:
                    continue
                
                file_info = {
                    "path": str(file_path.relative_to(source_path)),
                    "size": file_path.stat().st_size,
                    "modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "type": file_path.suffix,
                    "is_tia": self._is_tia_file(file_path)
                }
                
                scan_result["inventory"].append(file_info)
                scan_result["files_found"] += 1
                
                if file_info["is_tia"]:
                    scan_result["tia_files"] += 1
        
        # Save scan result
        result_path = self.storage_path / f"laptop_scan_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        result_path.write_text(json.dumps(scan_result, indent=2))
        
        logger.info(f"✅ Scan complete: {scan_result['files_found']} files, {scan_result['tia_files']} TIA files")
        
        return scan_result
    
    def _is_tia_file(self, file_path: Path) -> bool:
        """Check if file is TIA-related"""
        name_lower = file_path.name.lower()
        return any([
            'tia' in name_lower,
            'architect' in name_lower,
            'oracle' in name_lower,
            'surveyor' in name_lower,
            'sentinel' in name_lower,
            'citadel' in name_lower
        ])
    
    def harvest_file(self, source_path: Path, relative_path: str) -> bool:
        """
        Harvest a single file to storage
        
        Args:
            source_path: Source root path
            relative_path: Relative path to file
        
        Returns:
            True if harvest successful
        """
        file_path = source_path / relative_path
        if not file_path.exists():
            return False
        
        # Create destination path
        dest_path = self.storage_path / relative_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Copy file content
            content = file_path.read_bytes()
            dest_path.write_bytes(content)
            
            # Create metadata
            metadata = {
                "source": str(file_path),
                "harvested_at": datetime.datetime.utcnow().isoformat() + "Z",
                "size": len(content),
                "hash": hashlib.sha256(content).hexdigest(),
                "is_tia": self._is_tia_file(file_path)
            }
            
            metadata_path = dest_path.with_suffix(dest_path.suffix + ".meta.json")
            metadata_path.write_text(json.dumps(metadata, indent=2))
            
            self.harvest_count += 1
            if metadata["is_tia"]:
                self.tia_files_found += 1
            
            logger.info(f"✅ Harvested: {relative_path}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Harvest failed for {relative_path}: {e}")
            return False
    
    def harvest_all(self, laptop_path: str) -> Dict[str, Any]:
        """
        Harvest all files from laptop
        
        Args:
            laptop_path: Path to laptop source directory
        
        Returns:
            Harvest summary
        """
        # First scan to get inventory
        scan_result = self.scan_laptop_directory(laptop_path)
        
        if not scan_result.get("success", True):
            return scan_result
        
        source_path = Path(laptop_path)
        
        logger.info(f"📦 Harvesting {len(scan_result['inventory'])} files...")
        
        harvest_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "source": laptop_path,
            "files_harvested": 0,
            "tia_files_harvested": 0,
            "failed": 0
        }
        
        # Harvest each file
        for file_info in scan_result["inventory"]:
            if self.harvest_file(source_path, file_info["path"]):
                harvest_result["files_harvested"] += 1
                if file_info["is_tia"]:
                    harvest_result["tia_files_harvested"] += 1
            else:
                harvest_result["failed"] += 1
        
        # Save harvest summary
        summary_path = self.storage_path / f"laptop_harvest_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        summary_path.write_text(json.dumps(harvest_result, indent=2))
        
        logger.info(f"✅ Harvest complete: {harvest_result['files_harvested']} files harvested")
        logger.info(f"🎯 TIA files: {harvest_result['tia_files_harvested']}")
        
        return harvest_result
    
    def get_tia_files_list(self) -> List[Dict[str, Any]]:
        """Get list of all TIA files in storage"""
        tia_files = []
        
        for file_path in self.storage_path.rglob("*.meta.json"):
            try:
                metadata = json.loads(file_path.read_text())
                if metadata.get("is_tia"):
                    tia_files.append({
                        "path": str(file_path.with_suffix("").relative_to(self.storage_path)),
                        "harvested_at": metadata["harvested_at"],
                        "size": metadata["size"],
                        "hash": metadata["hash"]
                    })
            except Exception:
                continue
        
        return tia_files


def main():
    """Run Laptop Harvester"""
    harvester = LaptopHarvester()
    
    logger.info("💻 VAMGUARD TITAN - Laptop Harvester")
    logger.info("=" * 60)
    
    # Get laptop path from environment
    laptop_path = os.environ.get("LAPTOP_SOURCE_PATH", "")
    
    if not laptop_path:
        logger.warning("⚠️  LAPTOP_SOURCE_PATH not set - using current directory")
        laptop_path = str(Path.cwd())
    
    # Run harvest
    result = harvester.harvest_all(laptop_path)
    
    # Print summary
    print("\n" + "=" * 60)
    print("💻 LAPTOP HARVEST SUMMARY")
    print("=" * 60)
    print(f"Files Harvested: {result.get('files_harvested', 0)}")
    print(f"TIA Files: {result.get('tia_files_harvested', 0)}")
    print(f"Failed: {result.get('failed', 0)}")
    print("=" * 60)
    
    # Show TIA files
    tia_files = harvester.get_tia_files_list()
    if tia_files:
        print("\n🎯 TIA FILES FOUND:")
        for tia_file in tia_files[:10]:  # Show first 10
            print(f"  - {tia_file['path']}")
        if len(tia_files) > 10:
            print(f"  ... and {len(tia_files) - 10} more")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
