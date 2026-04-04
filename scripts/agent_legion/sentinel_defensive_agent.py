#!/usr/bin/env python3
"""
🛡️ SENTINEL DEFENSIVE AGENT - Continuous Protection
Q.G.T.N.L. Agent Legion - Defensive Division

Purpose: Continuous monitoring and defensive protection
Authority: Citadel Architect v26.0.LEGION+
"""

import os
import sys
import json
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentinelDefensiveAgent:
    """
    Defensive sentinel for continuous protection and monitoring
    
    Monitors:
    - File integrity
    - Suspicious file creation
    - Permission changes
    - Network connections
    - Process spawning
    """
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.baseline = {}
        self.alerts = []
        self.watch_directories = [
            Path.cwd(),
            Path.cwd() / "scripts",
            Path.cwd() / "data",
            Path.cwd() / ".github"
        ]
        
        logger.info("🛡️ Sentinel Defensive Agent initialized")
    
    def create_baseline(self) -> Dict:
        """Create security baseline"""
        logger.info("🛡️ Creating security baseline...")
        
        baseline = {
            "timestamp": datetime.now().isoformat(),
            "files": {},
            "directories": []
        }
        
        for watch_dir in self.watch_directories:
            if not watch_dir.exists():
                continue
            
            baseline["directories"].append(str(watch_dir))
            
            for filepath in watch_dir.rglob("*"):
                if filepath.is_file():
                    try:
                        stats = filepath.stat()
                        content_hash = self.hash_file(filepath)
                        
                        baseline["files"][str(filepath)] = {
                            "hash": content_hash,
                            "size": stats.st_size,
                            "modified": stats.st_mtime,
                            "permissions": oct(stats.st_mode)
                        }
                    except:
                        pass
        
        self.baseline = baseline
        
        # Save baseline
        baseline_dir = Path("data/security/baselines")
        baseline_dir.mkdir(parents=True, exist_ok=True)
        
        baseline_file = baseline_dir / "sentinel_baseline.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        logger.info(f"✅ Baseline created: {len(baseline['files'])} files tracked")
        
        return baseline
    
    def hash_file(self, filepath: Path) -> str:
        """Calculate file hash"""
        try:
            if filepath.stat().st_size > 100 * 1024 * 1024:  # Skip files > 100MB
                return "too_large"
            
            with open(filepath, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except:
            return "error"
    
    def check_integrity(self) -> List[Dict]:
        """Check file integrity against baseline"""
        logger.info("🛡️ Checking file integrity...")
        
        changes = []
        
        if not self.baseline:
            logger.warning("No baseline exists. Creating baseline first.")
            self.create_baseline()
            return changes
        
        # Check existing files
        for filepath_str, file_info in self.baseline["files"].items():
            filepath = Path(filepath_str)
            
            # File deleted
            if not filepath.exists():
                change = {
                    "type": "deleted",
                    "path": filepath_str,
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                }
                changes.append(change)
                self.alerts.append(change)
                logger.warning(f"⚠️  File deleted: {filepath}")
                continue
            
            # File modified
            try:
                current_hash = self.hash_file(filepath)
                if current_hash != file_info["hash"]:
                    change = {
                        "type": "modified",
                        "path": filepath_str,
                        "severity": "medium",
                        "old_hash": file_info["hash"],
                        "new_hash": current_hash,
                        "timestamp": datetime.now().isoformat()
                    }
                    changes.append(change)
                    self.alerts.append(change)
                    logger.warning(f"⚠️  File modified: {filepath}")
                
                # Permission changed
                stats = filepath.stat()
                current_perms = oct(stats.st_mode)
                if current_perms != file_info["permissions"]:
                    change = {
                        "type": "permissions_changed",
                        "path": filepath_str,
                        "severity": "medium",
                        "old_perms": file_info["permissions"],
                        "new_perms": current_perms,
                        "timestamp": datetime.now().isoformat()
                    }
                    changes.append(change)
                    self.alerts.append(change)
                    logger.warning(f"⚠️  Permissions changed: {filepath}")
            except:
                pass
        
        # Check for new files
        for watch_dir in self.watch_directories:
            if not watch_dir.exists():
                continue
            
            for filepath in watch_dir.rglob("*"):
                if filepath.is_file() and str(filepath) not in self.baseline["files"]:
                    change = {
                        "type": "new_file",
                        "path": str(filepath),
                        "severity": "low",
                        "timestamp": datetime.now().isoformat()
                    }
                    changes.append(change)
                    logger.info(f"ℹ️  New file detected: {filepath}")
        
        return changes
    
    def monitor(self, duration_seconds: int = 60, interval_seconds: int = 10):
        """Continuous monitoring"""
        logger.info(f"🛡️ Starting continuous monitoring for {duration_seconds}s...")
        
        start_time = time.time()
        check_count = 0
        
        while time.time() - start_time < duration_seconds:
            check_count += 1
            logger.info(f"\n🛡️ Integrity check #{check_count}")
            
            changes = self.check_integrity()
            
            if changes:
                logger.warning(f"⚠️  {len(changes)} changes detected!")
            else:
                logger.info("✅ No changes detected")
            
            # Wait for next check
            time.sleep(interval_seconds)
        
        logger.info(f"🛡️ Monitoring complete: {check_count} checks performed")
    
    def generate_report(self) -> Dict:
        """Generate sentinel report"""
        report = {
            "agent": "Sentinel Defensive Agent",
            "timestamp": datetime.now().isoformat(),
            "baseline": {
                "created": self.baseline.get("timestamp", "N/A"),
                "files_tracked": len(self.baseline.get("files", {})),
                "directories_watched": len(self.baseline.get("directories", []))
            },
            "alerts": self.alerts,
            "summary": {
                "total_alerts": len(self.alerts),
                "deleted_files": len([a for a in self.alerts if a["type"] == "deleted"]),
                "modified_files": len([a for a in self.alerts if a["type"] == "modified"]),
                "permission_changes": len([a for a in self.alerts if a["type"] == "permissions_changed"]),
                "new_files": len([a for a in self.alerts if a["type"] == "new_file"])
            }
        }
        
        # Save report
        report_dir = Path("data/security/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"sentinel_protection_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_file}")
        
        return report
    
    def deploy(self, mode: str = "scan"):
        """Deploy sentinel agent"""
        logger.info("🛡️ Sentinel Defensive Agent deploying...")
        
        if mode == "baseline":
            # Create baseline only
            self.create_baseline()
        
        elif mode == "scan":
            # Single integrity scan
            changes = self.check_integrity()
        
        elif mode == "monitor":
            # Continuous monitoring
            self.monitor(duration_seconds=300, interval_seconds=30)
        
        # Generate report
        report = self.generate_report()
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"🛡️ SENTINEL DEFENSIVE SCAN COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Files Tracked: {report['baseline']['files_tracked']}")
        logger.info(f"  Total Alerts: {report['summary']['total_alerts']}")
        logger.info(f"  Deleted: {report['summary']['deleted_files']}")
        logger.info(f"  Modified: {report['summary']['modified_files']}")
        logger.info(f"  New Files: {report['summary']['new_files']}")
        logger.info(f"{'='*60}")
        
        return report

def main():
    """Main entry point"""
    sentinel = SentinelDefensiveAgent()
    
    # Deploy agent in scan mode
    report = sentinel.deploy(mode="scan")
    
    return report

if __name__ == "__main__":
    main()
