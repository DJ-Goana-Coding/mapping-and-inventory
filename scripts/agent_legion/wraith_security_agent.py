#!/usr/bin/env python3
"""
👻 WRAITH SECURITY AGENT - Stealth Security Operator
Q.G.T.N.L. Agent Legion - Security Division

Purpose: Stealth detection and removal of security threats
Authority: Citadel Architect v26.0.LEGION+
"""

import os
import sys
import json
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WraithSecurityAgent:
    """
    Stealth security operator for silent threat detection and removal
    
    Capabilities:
    - Silent file system scanning
    - Hidden threat detection
    - Rootkit detection
    - Backdoor identification
    - Malware signature scanning
    """
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.threats_db = self.load_threat_signatures()
        self.scan_results = {
            "timestamp": datetime.now().isoformat(),
            "threats_found": [],
            "clean_files": 0,
            "suspicious_files": [],
            "quarantined": []
        }
        
        logger.info("👻 Wraith Security Agent initialized")
    
    def load_threat_signatures(self) -> Dict:
        """Load known threat signatures"""
        return {
            "malware_patterns": [
                r"eval\s*\(\s*base64_decode",
                r"system\s*\(\s*['\"]rm\s+-rf",
                r"exec\s*\(\s*['\"]curl.*\|\s*sh",
                r"__import__\s*\(\s*['\"]os['\"].*\.system",
                r"subprocess\.call\s*\(.*shell\s*=\s*True",
            ],
            "backdoor_patterns": [
                r"nc\s+-l\s+-p\s+\d+",
                r"\/bin\/bash\s+-i",
                r"socket\.socket.*SOCK_STREAM.*connect",
                r"reverse_shell",
                r"bind_shell",
            ],
            "tracker_patterns": [
                r"tracking\.js",
                r"analytics\.track",
                r"gtag\s*\(",
                r"facebook\.pixel",
                r"google-analytics\.com",
            ],
            "suspicious_extensions": [
                ".exe", ".dll", ".scr", ".vbs", ".bat", ".cmd",
                ".ps1", ".jar", ".class", ".so", ".dylib"
            ]
        }
    
    def scan_file(self, filepath: Path) -> Dict:
        """Scan individual file for threats"""
        result = {
            "path": str(filepath),
            "threats": [],
            "suspicious": False,
            "hash": ""
        }
        
        try:
            # Check extension
            if filepath.suffix.lower() in self.threats_db["suspicious_extensions"]:
                result["suspicious"] = True
                result["threats"].append(f"Suspicious extension: {filepath.suffix}")
            
            # Read file content
            if filepath.is_file() and filepath.stat().st_size < 10 * 1024 * 1024:  # Max 10MB
                try:
                    content = filepath.read_text(encoding='utf-8', errors='ignore')
                    
                    # Calculate hash
                    result["hash"] = hashlib.sha256(content.encode()).hexdigest()
                    
                    # Scan for malware patterns
                    for pattern in self.threats_db["malware_patterns"]:
                        if re.search(pattern, content, re.IGNORECASE):
                            result["threats"].append(f"Malware pattern: {pattern}")
                            result["suspicious"] = True
                    
                    # Scan for backdoors
                    for pattern in self.threats_db["backdoor_patterns"]:
                        if re.search(pattern, content, re.IGNORECASE):
                            result["threats"].append(f"Backdoor pattern: {pattern}")
                            result["suspicious"] = True
                    
                    # Scan for trackers
                    for pattern in self.threats_db["tracker_patterns"]:
                        if re.search(pattern, content, re.IGNORECASE):
                            result["threats"].append(f"Tracker pattern: {pattern}")
                            result["suspicious"] = True
                    
                except Exception as e:
                    logger.debug(f"Cannot read {filepath}: {e}")
        
        except Exception as e:
            logger.error(f"Error scanning {filepath}: {e}")
        
        return result
    
    def scan_directory(self, directory: Path, recursive: bool = True) -> None:
        """Scan directory for threats"""
        logger.info(f"👻 Scanning: {directory}")
        
        try:
            if recursive:
                files = directory.rglob("*")
            else:
                files = directory.glob("*")
            
            for filepath in files:
                if filepath.is_file():
                    result = self.scan_file(filepath)
                    
                    if result["threats"]:
                        self.scan_results["threats_found"].append(result)
                        logger.warning(f"⚠️  Threat detected: {filepath}")
                        for threat in result["threats"]:
                            logger.warning(f"    {threat}")
                    elif result["suspicious"]:
                        self.scan_results["suspicious_files"].append(result)
                    else:
                        self.scan_results["clean_files"] += 1
        
        except Exception as e:
            logger.error(f"Error scanning directory {directory}: {e}")
    
    def quarantine_threat(self, filepath: Path) -> bool:
        """Move threat to quarantine"""
        try:
            quarantine_dir = Path("data/security/quarantine")
            quarantine_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"{timestamp}_{filepath.name}"
            quarantine_path = quarantine_dir / new_name
            
            filepath.rename(quarantine_path)
            
            self.scan_results["quarantined"].append({
                "original": str(filepath),
                "quarantine": str(quarantine_path),
                "timestamp": timestamp
            })
            
            logger.info(f"🔒 Quarantined: {filepath} -> {quarantine_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to quarantine {filepath}: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generate security report"""
        report = {
            "agent": "Wraith Security Agent",
            "timestamp": self.scan_results["timestamp"],
            "summary": {
                "threats_found": len(self.scan_results["threats_found"]),
                "suspicious_files": len(self.scan_results["suspicious_files"]),
                "clean_files": self.scan_results["clean_files"],
                "quarantined": len(self.scan_results["quarantined"])
            },
            "threats": self.scan_results["threats_found"],
            "suspicious": self.scan_results["suspicious_files"],
            "quarantined": self.scan_results["quarantined"]
        }
        
        # Save report
        report_dir = Path("data/security/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"wraith_scan_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_file}")
        
        return report
    
    def deploy(self, target_path: Optional[str] = None, auto_quarantine: bool = False):
        """Deploy wraith agent"""
        logger.info("👻 Wraith Security Agent deploying...")
        
        target = Path(target_path) if target_path else Path.cwd()
        
        # Scan target
        self.scan_directory(target, recursive=True)
        
        # Auto-quarantine if enabled
        if auto_quarantine and self.scan_results["threats_found"]:
            logger.info("🔒 Auto-quarantine enabled")
            for threat in self.scan_results["threats_found"]:
                self.quarantine_threat(Path(threat["path"]))
        
        # Generate report
        report = self.generate_report()
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"👻 WRAITH SECURITY SCAN COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Threats Found: {report['summary']['threats_found']}")
        logger.info(f"  Suspicious Files: {report['summary']['suspicious_files']}")
        logger.info(f"  Clean Files: {report['summary']['clean_files']}")
        logger.info(f"  Quarantined: {report['summary']['quarantined']}")
        logger.info(f"{'='*60}")
        
        return report

def main():
    """Main entry point"""
    wraith = WraithSecurityAgent()
    
    # Deploy agent
    report = wraith.deploy(
        target_path=".",
        auto_quarantine=False  # Set True for automatic quarantine
    )
    
    return report

if __name__ == "__main__":
    main()
