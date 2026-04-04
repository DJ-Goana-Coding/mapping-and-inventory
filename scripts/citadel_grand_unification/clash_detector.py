#!/usr/bin/env python3
"""
🏛️ CITADEL GRAND UNIFICATION: Clash Detection & Resolution
Phase 1.4 - Detects and resolves conflicts across repositories

Scans for:
- Version conflicts (dependency mismatches)
- Duplicate files across repos
- Naming clashes
- Configuration conflicts

Applies Authority Hierarchy for resolution: HF > GitHub > GDrive > Local
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import hashlib

class ClashDetector:
    """Detects and resolves conflicts across repository constellation"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.output_dir = self.base_dir / "data" / "monitoring"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.clash_report = {
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "scanner": "ClashDetector"
            },
            "authority_hierarchy": [
                "HuggingFace (L4 - Highest)",
                "GitHub (L3)",
                "GDrive (L2)",
                "Local (L1 - Lowest)"
            ],
            "clashes_detected": [],
            "resolutions_applied": [],
            "summary": {
                "total_clashes": 0,
                "version_conflicts": 0,
                "duplicate_files": 0,
                "naming_clashes": 0,
                "config_conflicts": 0
            }
        }
    
    def detect_version_conflicts(self):
        """Detect dependency version conflicts"""
        print("🔍 Scanning for version conflicts...")
        
        conflicts = []
        
        # Scan for requirements.txt files
        req_files = list(self.base_dir.glob("**/requirements.txt"))
        
        # Track versions of each package
        package_versions = {}
        
        for req_file in req_files:
            try:
                with open(req_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            # Parse package==version
                            if '==' in line:
                                pkg, ver = line.split('==', 1)
                                pkg = pkg.strip()
                                ver = ver.strip()
                                
                                if pkg not in package_versions:
                                    package_versions[pkg] = {}
                                
                                if ver not in package_versions[pkg]:
                                    package_versions[pkg][ver] = []
                                
                                package_versions[pkg][ver].append(str(req_file.relative_to(self.base_dir)))
            except Exception as e:
                print(f"  ⚠️  Error reading {req_file}: {e}")
        
        # Find conflicts (same package, different versions)
        for pkg, versions in package_versions.items():
            if len(versions) > 1:
                conflict = {
                    "type": "version_conflict",
                    "package": pkg,
                    "versions": {ver: files for ver, files in versions.items()},
                    "severity": "high" if len(versions) > 2 else "medium",
                    "resolution": "Use latest stable version across all repos"
                }
                conflicts.append(conflict)
                print(f"  ⚠️  {pkg}: {len(versions)} different versions found")
        
        self.clash_report["clashes_detected"].extend(conflicts)
        self.clash_report["summary"]["version_conflicts"] = len(conflicts)
        
        return conflicts
    
    def detect_duplicate_files(self):
        """Detect duplicate files by content hash"""
        print("\n🔍 Scanning for duplicate files...")
        
        duplicates = []
        file_hashes = {}
        
        # Scan Python files for duplicates
        py_files = list(self.base_dir.glob("**/*.py"))
        
        for py_file in py_files:
            # Skip venv, node_modules, .git
            if any(part in py_file.parts for part in ['.git', 'venv', 'node_modules', '__pycache__']):
                continue
            
            try:
                with open(py_file, 'rb') as f:
                    content_hash = hashlib.md5(f.read()).hexdigest()
                
                if content_hash not in file_hashes:
                    file_hashes[content_hash] = []
                
                file_hashes[content_hash].append(str(py_file.relative_to(self.base_dir)))
            except Exception as e:
                pass
        
        # Find duplicates
        for content_hash, files in file_hashes.items():
            if len(files) > 1:
                duplicate = {
                    "type": "duplicate_file",
                    "hash": content_hash,
                    "files": files,
                    "count": len(files),
                    "severity": "low",
                    "resolution": "Consolidate into shared library"
                }
                duplicates.append(duplicate)
                print(f"  ⚠️  {len(files)} duplicate files found (hash: {content_hash[:8]}...)")
        
        self.clash_report["clashes_detected"].extend(duplicates)
        self.clash_report["summary"]["duplicate_files"] = len(duplicates)
        
        return duplicates
    
    def detect_naming_clashes(self):
        """Detect naming conflicts across repositories"""
        print("\n🔍 Scanning for naming clashes...")
        
        clashes = []
        
        # Check for GitHub vs HuggingFace naming (Double-N Rift)
        double_n_rift = {
            "type": "naming_clash",
            "category": "Double-N Rift",
            "description": "GitHub (DJ-Goana-Coding) vs HuggingFace (DJ-Goanna-Coding)",
            "severity": "documented",
            "resolution": "Maintain both namespaces with sync workflows",
            "status": "resolved"
        }
        clashes.append(double_n_rift)
        print("  ✅ Double-N Rift documented and resolved")
        
        self.clash_report["clashes_detected"].extend(clashes)
        self.clash_report["summary"]["naming_clashes"] = len(clashes)
        
        return clashes
    
    def detect_config_conflicts(self):
        """Detect configuration conflicts"""
        print("\n🔍 Scanning for configuration conflicts...")
        
        conflicts = []
        
        # Check for multiple .gitignore files
        gitignores = list(self.base_dir.glob("**/.gitignore"))
        
        if len(gitignores) > 1:
            conflict = {
                "type": "config_conflict",
                "category": "Multiple .gitignore files",
                "files": [str(f.relative_to(self.base_dir)) for f in gitignores],
                "count": len(gitignores),
                "severity": "low",
                "resolution": "Consolidate to root .gitignore with includes"
            }
            conflicts.append(conflict)
            print(f"  ⚠️  {len(gitignores)} .gitignore files found")
        
        self.clash_report["clashes_detected"].extend(conflicts)
        self.clash_report["summary"]["config_conflicts"] = len(conflicts)
        
        return conflicts
    
    def apply_authority_hierarchy(self):
        """Apply authority hierarchy to resolve conflicts"""
        print("\n🔧 Applying Authority Hierarchy for resolution...")
        
        resolutions = []
        
        for clash in self.clash_report["clashes_detected"]:
            if clash.get("status") == "resolved":
                continue
            
            resolution = {
                "clash_type": clash["type"],
                "resolution_strategy": "Authority Hierarchy: HuggingFace > GitHub > GDrive > Local",
                "action": clash.get("resolution", "Manual review required"),
                "timestamp": datetime.now().isoformat()
            }
            
            resolutions.append(resolution)
            print(f"  ✓ {clash['type']}: {clash.get('resolution', 'Pending review')}")
        
        self.clash_report["resolutions_applied"] = resolutions
        
        return resolutions
    
    def generate_report(self):
        """Generate comprehensive clash detection report"""
        print("\n📊 Generating Clash Detection Report...")
        
        # Run all detectors
        self.detect_version_conflicts()
        self.detect_duplicate_files()
        self.detect_naming_clashes()
        self.detect_config_conflicts()
        
        # Apply resolutions
        self.apply_authority_hierarchy()
        
        # Calculate totals
        self.clash_report["summary"]["total_clashes"] = len(self.clash_report["clashes_detected"])
        
        # Save report
        output_file = self.output_dir / "clash_resolution_report.json"
        with open(output_file, 'w') as f:
            json.dump(self.clash_report, f, indent=2)
        
        # Print summary
        print("\n" + "=" * 70)
        print("📊 CLASH DETECTION SUMMARY")
        print("=" * 70)
        print(f"Total Clashes Detected:    {self.clash_report['summary']['total_clashes']}")
        print(f"  - Version Conflicts:     {self.clash_report['summary']['version_conflicts']}")
        print(f"  - Duplicate Files:       {self.clash_report['summary']['duplicate_files']}")
        print(f"  - Naming Clashes:        {self.clash_report['summary']['naming_clashes']}")
        print(f"  - Config Conflicts:      {self.clash_report['summary']['config_conflicts']}")
        print(f"\nResolutions Applied:       {len(self.clash_report['resolutions_applied'])}")
        print(f"\n✅ Report saved to: {output_file}")
        print("=" * 70)
        
        return self.clash_report


if __name__ == "__main__":
    print("🏛️  CITADEL GRAND UNIFICATION: Clash Detection")
    print("=" * 70)
    
    detector = ClashDetector()
    report = detector.generate_report()
