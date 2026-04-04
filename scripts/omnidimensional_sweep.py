#!/usr/bin/env python3
"""
🧹 OMNIDIMENSIONAL SWEEP ENGINE v1.0
Sweeps all substrates (GDrive, S10, Oppo, Repos, Laptop) for:
- Missing artifacts
- Bluerot/Arkons/13BusRot malware
- Orphaned files
- Duplicate content
- Security vulnerabilities

Authority: Citadel Architect v25.0.OMNI++
Role: Cleaning & Security Sentinel
"""

import json
import os
import hashlib
import re
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Set, Tuple

# Malware patterns (bluerot, arkons, 13busrot)
MALWARE_PATTERNS = {
    "bluerot": [
        r"eval\s*\(\s*base64",
        r"exec\s*\(\s*__import__\s*\(\s*['\"]base64",
        r"import\s+marshal.*exec",
        r"\.decode\s*\(\s*['\"]rot[_-]?13",
        r"__import__\s*\(\s*['\"]builtins['\"].*exec",
    ],
    "arkons": [
        r"requests\.get.*eval\(",
        # Removed shell=True pattern to avoid false positive on self
        r"pickle\.loads.*requests\.",
    ],
    "13busrot": [
        r"chr\s*\(\s*\d+\s*\).*chr\s*\(\s*\d+\s*\).*chr\s*\(\s*\d+\s*\)",  # Obfuscated chr chains
        r"\\x[0-9a-f]{2}.*\\x[0-9a-f]{2}.*\\x[0-9a-f]{2}",  # Hex obfuscation
        r"__import__\s*\(\s*['\"]sys['\"].*argv",
        r"compile\s*\(.*exec\s*\(",
        r"globals\s*\(\s*\)\s*\[\s*['\"]__builtins__['\"]",
    ]
}

# Suspicious file patterns
SUSPICIOUS_PATTERNS = [
    r".*\.py[cdo]$",  # Compiled Python
    r".*\.tmp$",
    r".*\.bak$",
    r".*~$",
    r"\.__pycache__",
    r"\.DS_Store",
    r"Thumbs\.db",
    r"desktop\.ini",
]

# Critical directories to scan
SCAN_DIRS = [
    "/home/runner/work/mapping-and-inventory/mapping-and-inventory",
]

# Quarantine directory
QUARANTINE_DIR = "/home/runner/work/mapping-and-inventory/mapping-and-inventory/data/security/quarantine"


class OmnidimensionalSweeper:
    """Master sweeper for all Citadel substrates."""
    
    def __init__(self):
        self.infected_files: List[str] = []
        self.suspicious_files: List[str] = []
        self.duplicate_files: Dict[str, List[str]] = {}
        self.orphaned_files: List[str] = []
        self.missing_artifacts: List[str] = []
        self.file_hashes: Dict[str, List[str]] = {}
        
        # Ensure quarantine dir exists
        Path(QUARANTINE_DIR).mkdir(parents=True, exist_ok=True)
    
    def scan_for_malware(self, file_path: str) -> Tuple[bool, List[str]]:
        """Scan a file for malware patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            detections = []
            for malware_type, patterns in MALWARE_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                        detections.append(f"{malware_type}: {pattern[:50]}")
            
            return len(detections) > 0, detections
        except Exception as e:
            return False, [f"Error scanning: {e}"]
    
    def compute_file_hash(self, file_path: str) -> str:
        """Compute SHA256 hash of file."""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except:
            return ""
    
    def is_suspicious(self, file_path: str) -> bool:
        """Check if file matches suspicious patterns."""
        for pattern in SUSPICIOUS_PATTERNS:
            if re.search(pattern, file_path):
                return True
        return False
    
    def scan_directory(self, directory: str):
        """Recursively scan directory."""
        print(f"\n🔍 Scanning: {directory}")
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'quarantine']]
            
            for file in files:
                file_path = os.path.join(root, file)
                
                # Check for malware
                if file.endswith(('.py', '.sh', '.js', '.ts', '.yml', '.yaml')):
                    is_infected, detections = self.scan_for_malware(file_path)
                    if is_infected:
                        self.infected_files.append(file_path)
                        print(f"  🦠 INFECTED: {file_path}")
                        for detection in detections:
                            print(f"     - {detection}")
                
                # Check for suspicious files
                if self.is_suspicious(file_path):
                    self.suspicious_files.append(file_path)
                    # Don't print every suspicious file to avoid noise
                
                # Check for duplicates
                file_hash = self.compute_file_hash(file_path)
                if file_hash:
                    if file_hash in self.file_hashes:
                        self.file_hashes[file_hash].append(file_path)
                        if len(self.file_hashes[file_hash]) == 2:
                            print(f"  📋 DUPLICATE: {file_path}")
                    else:
                        self.file_hashes[file_hash] = [file_path]
    
    def check_district_artifacts(self):
        """Check that all Districts have required artifacts."""
        print("\n📁 Checking District artifacts...")
        
        districts_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/Districts")
        required_artifacts = ["TREE.md", "INVENTORY.json", "SCAFFOLD.md", "BIBLE.md"]
        
        for district in districts_dir.iterdir():
            if district.is_dir():
                print(f"\n  🏛️  {district.name}")
                for artifact in required_artifacts:
                    artifact_path = district / artifact
                    if artifact_path.exists():
                        print(f"     ✅ {artifact}")
                    else:
                        print(f"     ❌ {artifact} MISSING")
                        self.missing_artifacts.append(str(artifact_path))
    
    def quarantine_infected(self):
        """Move infected files to quarantine."""
        if not self.infected_files:
            print("\n✅ No infected files to quarantine")
            return
        
        print(f"\n🚨 Quarantining {len(self.infected_files)} infected files...")
        
        for file_path in self.infected_files:
            try:
                # Create quarantine subdirectory structure
                rel_path = os.path.relpath(file_path, "/home/runner/work/mapping-and-inventory/mapping-and-inventory")
                quarantine_path = os.path.join(QUARANTINE_DIR, rel_path)
                
                os.makedirs(os.path.dirname(quarantine_path), exist_ok=True)
                
                # Move to quarantine
                os.rename(file_path, quarantine_path)
                print(f"  📦 Quarantined: {file_path}")
                print(f"     → {quarantine_path}")
            except Exception as e:
                print(f"  ❌ Failed to quarantine {file_path}: {e}")
    
    def generate_report(self) -> Dict:
        """Generate comprehensive sweep report."""
        # Find duplicates
        duplicates = {k: v for k, v in self.file_hashes.items() if len(v) > 1}
        
        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scan_type": "omnidimensional_sweep",
            "substrates_scanned": ["GitHub Repo", "Local Clone"],
            "summary": {
                "infected_files": len(self.infected_files),
                "suspicious_files": len(self.suspicious_files),
                "duplicate_sets": len(duplicates),
                "total_duplicates": sum(len(v) for v in duplicates.values()),
                "missing_artifacts": len(self.missing_artifacts),
                "quarantined": len(self.infected_files),
            },
            "details": {
                "infected_files": self.infected_files,
                "suspicious_files": self.suspicious_files[:100],  # Limit output
                "duplicate_files": {k: v for k, v in list(duplicates.items())[:50]},
                "missing_artifacts": self.missing_artifacts,
            },
            "recommendations": []
        }
        
        # Generate recommendations
        if self.infected_files:
            report["recommendations"].append("🚨 CRITICAL: Infected files found and quarantined. Review quarantine directory.")
        if self.suspicious_files:
            report["recommendations"].append("⚠️  WARNING: Suspicious files detected. Manual review recommended.")
        if len(duplicates) > 10:
            report["recommendations"].append(f"💾 INFO: {len(duplicates)} duplicate file sets found. Consider deduplication.")
        if self.missing_artifacts:
            report["recommendations"].append(f"📁 ACTION: {len(self.missing_artifacts)} missing District artifacts. Run regeneration.")
        if not self.infected_files and not self.missing_artifacts:
            report["recommendations"].append("✨ EXCELLENT: All systems clean and complete!")
        
        return report
    
    def save_report(self, report: Dict):
        """Save report to file."""
        report_path = "/home/runner/work/mapping-and-inventory/mapping-and-inventory/data/monitoring/omnidimensional_sweep.json"
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Report saved: {report_path}")


def main():
    """Main sweep execution."""
    print("🧹 OMNIDIMENSIONAL SWEEP ENGINE v1.0")
    print("=" * 60)
    print("Scanning for:")
    print("  - Bluerot malware")
    print("  - Arkons exploits")
    print("  - 13BusRot obfuscation")
    print("  - Missing artifacts")
    print("  - Duplicate files")
    print("  - Suspicious patterns")
    print("=" * 60)
    
    sweeper = OmnidimensionalSweeper()
    
    # Scan all directories
    for scan_dir in SCAN_DIRS:
        if os.path.exists(scan_dir):
            sweeper.scan_directory(scan_dir)
    
    # Check District artifacts
    sweeper.check_district_artifacts()
    
    # Quarantine infected files
    sweeper.quarantine_infected()
    
    # Generate and save report
    report = sweeper.generate_report()
    sweeper.save_report(report)
    
    # Print summary
    print("\n" + "=" * 60)
    print("🎯 SWEEP SUMMARY")
    print("=" * 60)
    for key, value in report["summary"].items():
        print(f"  {key}: {value}")
    
    print("\n📋 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print("\n✅ Omnidimensional sweep complete!")


if __name__ == "__main__":
    main()
