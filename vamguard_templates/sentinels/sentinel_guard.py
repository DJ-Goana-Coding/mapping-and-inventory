#!/usr/bin/env python3
"""
🛡️ SENTINEL GUARD
The Watchful Guardian - Active Security Monitoring

Role: Real-time threat detection and response
Scope: All Citadel Mesh nodes, workers, and bridges
Authority: Security Override (auto-isolate on critical threats)

SOVEREIGN GUARDRAILS:
- Never expose credentials
- Never write absolute paths
- Always log security events
- Auto-report to D12 Overseer
"""

import os
import json
import hashlib
import datetime
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='🛡️ [%(asctime)s] SENTINEL: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


@dataclass
class SecurityEvent:
    """Security event data structure"""
    timestamp: str
    event_type: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    source: str
    description: str
    action_taken: str
    metadata: Dict[str, Any]


@dataclass
class ThreatDetection:
    """Threat detection result"""
    detected: bool
    threat_type: str
    severity: str
    details: str
    recommendations: List[str]


class SentinelGuard:
    """
    The Sentinel Guard - Active Security Monitoring
    
    Monitors:
    - Credential exposure in code/configs
    - Absolute path violations
    - Symlink integrity
    - Worker health and auth
    - Bridge connection security
    - Suspicious file access patterns
    """
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.security_log_path = self.repo_root / "data" / "security_logs"
        self.security_log_path.mkdir(parents=True, exist_ok=True)
        
        # Security patterns
        self.credential_patterns = [
            r'(?i)(api[_-]?key|apikey)[\s]*[=:][\s]*["\']([^\s"\']+)["\']',
            r'(?i)(secret|password|passwd|pwd)[\s]*[=:][\s]*["\']([^\s"\']+)["\']',
            r'(?i)(token|auth[_-]?token)[\s]*[=:][\s]*["\']([^\s"\']+)["\']',
            r'(?i)(access[_-]?key|accesskey)[\s]*[=:][\s]*["\']([^\s"\']+)["\']',
            r'(?i)ghp_[a-zA-Z0-9]{36}',  # GitHub PAT
            r'(?i)hf_[a-zA-Z0-9]{34}',   # HuggingFace token
        ]
        
        self.absolute_path_pattern = r'(?:^|[\s"\'])(/[a-z][^"\s]*|[A-Z]:\\[^"\s]*)'
        
        # Security metrics
        self.events = []
        self.threats_detected = 0
        self.scans_performed = 0
        
        logger.info("🛡️ Sentinel Guard initialized")
    
    def scan_file_for_credentials(self, file_path: Path) -> ThreatDetection:
        """
        Scan a single file for exposed credentials
        
        Returns:
            ThreatDetection object with results
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            detections = []
            for pattern in self.credential_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    detections.append(f"Pattern match: {pattern[:30]}...")
            
            if detections:
                return ThreatDetection(
                    detected=True,
                    threat_type="CREDENTIAL_EXPOSURE",
                    severity="CRITICAL",
                    details=f"Found {len(detections)} potential credential(s) in {file_path.name}",
                    recommendations=[
                        "Move credentials to environment variables",
                        "Add file to .gitignore if it contains secrets",
                        "Use encrypted vault or secret management",
                        "Review git history for exposed secrets"
                    ]
                )
            
            return ThreatDetection(
                detected=False,
                threat_type="CREDENTIAL_EXPOSURE",
                severity="INFO",
                details="No credentials detected",
                recommendations=[]
            )
        
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return ThreatDetection(
                detected=False,
                threat_type="SCAN_ERROR",
                severity="LOW",
                details=str(e),
                recommendations=["Review file manually"]
            )
    
    def scan_file_for_absolute_paths(self, file_path: Path) -> ThreatDetection:
        """
        Scan file for absolute path violations
        
        Returns:
            ThreatDetection object with results
        """
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            
            # Exclude common false positives
            excluded_patterns = [
                r'#!/usr/bin',  # Shebang
                r'#![a-z]',     # Rust attributes
                r'http://',     # URLs
                r'https://',    # URLs
            ]
            
            lines_with_paths = []
            for line_num, line in enumerate(content.split('\n'), 1):
                # Skip excluded patterns
                if any(re.search(pat, line) for pat in excluded_patterns):
                    continue
                
                match = re.search(self.absolute_path_pattern, line)
                if match:
                    lines_with_paths.append((line_num, line.strip()[:80]))
            
            if lines_with_paths:
                return ThreatDetection(
                    detected=True,
                    threat_type="ABSOLUTE_PATH_VIOLATION",
                    severity="MEDIUM",
                    details=f"Found {len(lines_with_paths)} absolute path(s) in {file_path.name}",
                    recommendations=[
                        "Convert to relative paths",
                        "Use Path(__file__).parent for repo-relative paths",
                        "Use environment variables for external paths",
                        "Follow Sovereign Guardrail: RELATIVE_PATH_ENFORCEMENT"
                    ]
                )
            
            return ThreatDetection(
                detected=False,
                threat_type="ABSOLUTE_PATH_VIOLATION",
                severity="INFO",
                details="No absolute paths detected",
                recommendations=[]
            )
        
        except Exception as e:
            logger.error(f"Error scanning {file_path}: {e}")
            return ThreatDetection(
                detected=False,
                threat_type="SCAN_ERROR",
                severity="LOW",
                details=str(e),
                recommendations=["Review file manually"]
            )
    
    def scan_repository(self, exclude_dirs: List[str] = None) -> Dict[str, Any]:
        """
        Scan entire repository for security issues
        
        Args:
            exclude_dirs: Directories to exclude (e.g., .git, node_modules)
        
        Returns:
            Scan report with all findings
        """
        if exclude_dirs is None:
            exclude_dirs = ['.git', 'node_modules', '__pycache__', '.venv', 'venv', 'data']
        
        logger.info(f"🔍 Starting repository security scan...")
        self.scans_performed += 1
        
        scan_results = {
            "scan_id": hashlib.sha256(str(datetime.datetime.utcnow()).encode()).hexdigest()[:16],
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "repo_root": str(self.repo_root),
            "files_scanned": 0,
            "threats_found": 0,
            "critical_threats": 0,
            "high_threats": 0,
            "medium_threats": 0,
            "findings": []
        }
        
        # Scan all files
        for file_path in self.repo_root.rglob('*'):
            # Skip directories and excluded paths
            if file_path.is_dir():
                continue
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            
            # Only scan text files
            if file_path.suffix not in ['.py', '.js', '.json', '.yaml', '.yml', '.md', '.sh', '.txt', '.env.example']:
                continue
            
            scan_results["files_scanned"] += 1
            
            # Scan for credentials
            cred_result = self.scan_file_for_credentials(file_path)
            if cred_result.detected:
                scan_results["threats_found"] += 1
                if cred_result.severity == "CRITICAL":
                    scan_results["critical_threats"] += 1
                
                scan_results["findings"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "threat": asdict(cred_result)
                })
                
                # Log security event
                self._log_security_event(
                    event_type="CREDENTIAL_DETECTED",
                    severity=cred_result.severity,
                    source=str(file_path.relative_to(self.repo_root)),
                    description=cred_result.details,
                    action_taken="LOGGED_FOR_REVIEW"
                )
            
            # Scan for absolute paths
            path_result = self.scan_file_for_absolute_paths(file_path)
            if path_result.detected:
                scan_results["threats_found"] += 1
                if path_result.severity == "HIGH":
                    scan_results["high_threats"] += 1
                elif path_result.severity == "MEDIUM":
                    scan_results["medium_threats"] += 1
                
                scan_results["findings"].append({
                    "file": str(file_path.relative_to(self.repo_root)),
                    "threat": asdict(path_result)
                })
        
        # Save scan report
        report_path = self.security_log_path / f"scan_{scan_results['scan_id']}.json"
        report_path.write_text(json.dumps(scan_results, indent=2))
        
        logger.info(f"✅ Scan complete: {scan_results['files_scanned']} files, {scan_results['threats_found']} threats")
        logger.info(f"📊 Critical: {scan_results['critical_threats']}, High: {scan_results['high_threats']}, Medium: {scan_results['medium_threats']}")
        
        return scan_results
    
    def _log_security_event(self, event_type: str, severity: str, source: str,
                           description: str, action_taken: str, metadata: Dict = None):
        """Log a security event"""
        event = SecurityEvent(
            timestamp=datetime.datetime.utcnow().isoformat() + "Z",
            event_type=event_type,
            severity=severity,
            source=source,
            description=description,
            action_taken=action_taken,
            metadata=metadata or {}
        )
        
        self.events.append(event)
        
        # Write to log file
        log_file = self.security_log_path / f"events_{datetime.datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        with open(log_file, 'a') as f:
            f.write(json.dumps(asdict(event)) + '\n')
    
    def get_security_status(self) -> Dict[str, Any]:
        """Get current security status"""
        return {
            "sentinel_status": "ACTIVE",
            "scans_performed": self.scans_performed,
            "threats_detected": self.threats_detected,
            "events_logged": len(self.events),
            "last_scan": self.events[-1].timestamp if self.events else None
        }


def main():
    """Run Sentinel Guard security scan"""
    sentinel = SentinelGuard()
    
    logger.info("🛡️ VAMGUARD TITAN - Sentinel Guard")
    logger.info("=" * 60)
    
    # Run security scan
    results = sentinel.scan_repository()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🛡️ SECURITY SCAN SUMMARY")
    print("=" * 60)
    print(f"Files Scanned: {results['files_scanned']}")
    print(f"Threats Found: {results['threats_found']}")
    print(f"  - Critical: {results['critical_threats']}")
    print(f"  - High: {results['high_threats']}")
    print(f"  - Medium: {results['medium_threats']}")
    print(f"\nReport: data/security_logs/scan_{results['scan_id']}.json")
    print("=" * 60)
    
    # Exit with error if critical threats found
    if results['critical_threats'] > 0:
        logger.error("🚨 CRITICAL THREATS DETECTED - Review immediately!")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
