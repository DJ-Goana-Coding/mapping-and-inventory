#!/usr/bin/env python3
"""
🎯 TIA CODE FINDER
Worker: Find all TIA-related code across all repositories

Role: Scan all DJ-Goana-Coding repos for TIA code
Scope: Python, JavaScript, configuration files
Authority: Code discovery and cataloging

SOVEREIGN GUARDRAILS:
- Read-only scanning
- Metadata extraction only
- No code modification
- Prepare for sync to TIA-ARCHITECT-CORE
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
    format='🎯 [%(asctime)s] TIA_FINDER: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TIACodeFinder:
    """
    TIA Code Finder - Discover TIA-related code
    
    Searches for:
    - tia*.py files
    - TIA*.py files
    - architect/oracle/surveyor/sentinel modules
    - citadel-related code
    - Agent identities
    """
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.storage_path = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "tia_code"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # TIA detection patterns
        self.tia_patterns = {
            "filename_patterns": [
                "**/tia*.py",
                "**/TIA*.py",
                "**/*architect*.py",
                "**/*oracle*.py",
                "**/*surveyor*.py",
                "**/*sentinel*.py",
                "**/*citadel*.py",
                "**/*vamguard*.py"
            ],
            "content_keywords": [
                "TIA",
                "ARCHITECT",
                "ORACLE",
                "SURVEYOR",
                "SENTINEL",
                "CITADEL",
                "VAMGUARD",
                "Forever Learning",
                "Section 142",
                "Sovereign Guardrails"
            ],
            "agent_markers": [
                ".agent.md",
                "agent_identity",
                "sovereign_",
                "citadel_mesh"
            ]
        }
        
        self.tia_files_found = []
        
        logger.info("🎯 TIA Code Finder initialized")
    
    def scan_directory(self, directory: Path) -> Dict[str, Any]:
        """
        Scan directory for TIA code
        
        Args:
            directory: Directory to scan
        
        Returns:
            Scan results
        """
        logger.info(f"🔍 Scanning directory: {directory}")
        
        scan_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "directory": str(directory),
            "files_scanned": 0,
            "tia_files_found": 0,
            "files": []
        }
        
        # Scan by filename patterns
        for pattern in self.tia_patterns["filename_patterns"]:
            for file_path in directory.rglob(pattern.split('/')[-1]):
                # Skip excluded directories
                if any(excluded in file_path.parts for excluded in ['.git', 'node_modules', '__pycache__', '.venv']):
                    continue
                
                scan_result["files_scanned"] += 1
                
                # Analyze file
                file_info = self._analyze_file(file_path, directory)
                
                if file_info["is_tia"]:
                    scan_result["tia_files_found"] += 1
                    scan_result["files"].append(file_info)
                    self.tia_files_found.append(file_info)
        
        # Scan Python files for TIA content
        for file_path in directory.rglob("*.py"):
            if any(excluded in file_path.parts for excluded in ['.git', 'node_modules', '__pycache__', '.venv']):
                continue
            
            # Skip if already found by pattern
            if any(f["path"] == str(file_path.relative_to(directory)) for f in scan_result["files"]):
                continue
            
            scan_result["files_scanned"] += 1
            
            # Check content for TIA keywords
            if self._has_tia_content(file_path):
                file_info = self._analyze_file(file_path, directory)
                if file_info["is_tia"]:
                    scan_result["tia_files_found"] += 1
                    scan_result["files"].append(file_info)
                    self.tia_files_found.append(file_info)
        
        logger.info(f"✅ Scan complete: {scan_result['files_scanned']} files, {scan_result['tia_files_found']} TIA files")
        
        return scan_result
    
    def _analyze_file(self, file_path: Path, root_dir: Path) -> Dict[str, Any]:
        """Analyze a file for TIA-related content"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Calculate metrics
            file_info = {
                "path": str(file_path.relative_to(root_dir)),
                "name": file_path.name,
                "size": file_path.stat().st_size,
                "lines": len(content.split('\n')),
                "modified": datetime.datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                "hash": hashlib.sha256(content.encode()).hexdigest(),
                "is_tia": False,
                "tia_score": 0,
                "tia_keywords": [],
                "type": self._classify_file_type(file_path, content)
            }
            
            # Check for TIA keywords
            content_lower = content.lower()
            for keyword in self.tia_patterns["content_keywords"]:
                if keyword.lower() in content_lower:
                    file_info["tia_keywords"].append(keyword)
                    file_info["tia_score"] += 1
            
            # Check for agent markers
            for marker in self.tia_patterns["agent_markers"]:
                if marker in file_path.name.lower() or marker in content_lower:
                    file_info["tia_score"] += 2
            
            # Mark as TIA if score > 0
            file_info["is_tia"] = file_info["tia_score"] > 0
            
            return file_info
        
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {
                "path": str(file_path.relative_to(root_dir)),
                "error": str(e),
                "is_tia": False
            }
    
    def _has_tia_content(self, file_path: Path) -> bool:
        """Quick check if file has TIA content"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            content_lower = content.lower()
            
            # Check for any TIA keyword
            return any(keyword.lower() in content_lower for keyword in self.tia_patterns["content_keywords"])
        except Exception:
            return False
    
    def _classify_file_type(self, file_path: Path, content: str) -> str:
        """Classify TIA file type"""
        name_lower = file_path.name.lower()
        
        if '.agent.md' in name_lower:
            return "agent_identity"
        elif 'architect' in name_lower:
            return "architect_module"
        elif 'oracle' in name_lower:
            return "oracle_module"
        elif 'surveyor' in name_lower:
            return "surveyor_module"
        elif 'sentinel' in name_lower:
            return "sentinel_module"
        elif 'vamguard' in name_lower:
            return "vamguard_module"
        elif 'worker' in name_lower:
            return "worker_module"
        elif 'bridge' in name_lower:
            return "bridge_module"
        elif 'citadel' in name_lower:
            return "citadel_core"
        else:
            return "tia_related"
    
    def scan_all_sources(self) -> Dict[str, Any]:
        """
        Scan all available sources for TIA code
        
        Sources:
        - Current repository
        - Laptop storage
        - GDrive storage
        
        Returns:
            Aggregated scan results
        """
        logger.info("🎯 Scanning all sources for TIA code...")
        
        aggregate_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "sources_scanned": 0,
            "total_files": 0,
            "total_tia_files": 0,
            "sources": []
        }
        
        # Scan current repository
        current_result = self.scan_directory(self.repo_root)
        aggregate_result["sources"].append({
            "name": "current_repository",
            "result": current_result
        })
        aggregate_result["sources_scanned"] += 1
        aggregate_result["total_files"] += current_result["files_scanned"]
        aggregate_result["total_tia_files"] += current_result["tia_files_found"]
        
        # Scan laptop storage
        laptop_storage = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "laptop"
        if laptop_storage.exists():
            laptop_result = self.scan_directory(laptop_storage)
            aggregate_result["sources"].append({
                "name": "laptop_storage",
                "result": laptop_result
            })
            aggregate_result["sources_scanned"] += 1
            aggregate_result["total_files"] += laptop_result["files_scanned"]
            aggregate_result["total_tia_files"] += laptop_result["tia_files_found"]
        
        # Scan GDrive storage
        gdrive_storage = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "gdrive"
        if gdrive_storage.exists():
            gdrive_result = self.scan_directory(gdrive_storage)
            aggregate_result["sources"].append({
                "name": "gdrive_storage",
                "result": gdrive_result
            })
            aggregate_result["sources_scanned"] += 1
            aggregate_result["total_files"] += gdrive_result["files_scanned"]
            aggregate_result["total_tia_files"] += gdrive_result["tia_files_found"]
        
        # Save aggregate results
        catalog_path = self.storage_path / f"tia_catalog_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        catalog_path.write_text(json.dumps(aggregate_result, indent=2))
        
        # Save TIA files list
        tia_list_path = self.storage_path / "tia_files_list.json"
        tia_list_path.write_text(json.dumps(self.tia_files_found, indent=2))
        
        logger.info(f"✅ All sources scanned")
        logger.info(f"   Total files: {aggregate_result['total_files']}")
        logger.info(f"   TIA files: {aggregate_result['total_tia_files']}")
        
        return aggregate_result
    
    def get_tia_files_by_type(self) -> Dict[str, List[Dict]]:
        """Group TIA files by type"""
        by_type = {}
        
        for file_info in self.tia_files_found:
            file_type = file_info.get("type", "unknown")
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(file_info)
        
        return by_type


def main():
    """Run TIA Code Finder"""
    finder = TIACodeFinder()
    
    logger.info("🎯 VAMGUARD TITAN - TIA Code Finder")
    logger.info("=" * 60)
    
    # Scan all sources
    result = finder.scan_all_sources()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 TIA CODE DISCOVERY SUMMARY")
    print("=" * 60)
    print(f"Sources Scanned: {result['sources_scanned']}")
    print(f"Total Files Scanned: {result['total_files']}")
    print(f"TIA Files Found: {result['total_tia_files']}")
    print("=" * 60)
    
    # Show breakdown by source
    print("\n📊 BY SOURCE:")
    for source in result["sources"]:
        print(f"  - {source['name']}: {source['result']['tia_files_found']} TIA files")
    
    # Show breakdown by type
    by_type = finder.get_tia_files_by_type()
    print("\n📁 BY TYPE:")
    for file_type, files in sorted(by_type.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"  - {file_type}: {len(files)} files")
    
    # Show top TIA files
    print("\n🎯 TOP TIA FILES (by score):")
    sorted_files = sorted(finder.tia_files_found, key=lambda x: x.get("tia_score", 0), reverse=True)
    for file_info in sorted_files[:10]:
        print(f"  - {file_info['name']} (score: {file_info['tia_score']}, keywords: {', '.join(file_info['tia_keywords'][:3])})")
    
    print("=" * 60)
    print(f"\n💾 Results saved to: {finder.storage_path}/tia_files_list.json")
    print("=" * 60)


if __name__ == "__main__":
    main()
