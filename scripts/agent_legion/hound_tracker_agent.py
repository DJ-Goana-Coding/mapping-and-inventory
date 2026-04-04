#!/usr/bin/env python3
"""
🐕 HOUND TRACKER DETECTION AGENT - Tracker Hunter
Q.G.T.N.L. Agent Legion - Detection Division

Purpose: Deep tracker detection and profiling
Authority: Citadel Architect v26.0.LEGION+
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import re
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HoundTrackerAgent:
    """
    Tracker detection specialist for identifying all forms of tracking
    
    Detects:
    - Web trackers (Google Analytics, Facebook Pixel, etc.)
    - Browser fingerprinting
    - Cookie trackers
    - Telemetry beacons
    - Hidden tracking pixels
    - Device fingerprinting
    """
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.tracker_db = self.load_tracker_database()
        self.detection_log = {
            "timestamp": datetime.now().isoformat(),
            "trackers_found": [],
            "tracker_types": {},
            "high_risk": [],
            "medium_risk": [],
            "low_risk": []
        }
        
        logger.info("🐕 Hound Tracker Detection Agent initialized")
    
    def load_tracker_database(self) -> Dict:
        """Load comprehensive tracker database"""
        return {
            "analytics": {
                "risk": "high",
                "patterns": [
                    r"google-analytics\.com",
                    r"ga\s*\(\s*['\"]send",
                    r"gtag\s*\(\s*['\"]config",
                    r"analytics\.js",
                    r"_gat\._anonymizeIp",
                    r"mixpanel\.track",
                    r"amplitude\.getInstance",
                    r"segment\.track",
                    r"heap\.track"
                ],
                "domains": [
                    "google-analytics.com",
                    "mixpanel.com",
                    "amplitude.com",
                    "segment.com",
                    "heap.io"
                ]
            },
            "social_trackers": {
                "risk": "high",
                "patterns": [
                    r"facebook\.com/tr",
                    r"fbq\s*\(\s*['\"]track",
                    r"connect\.facebook\.net",
                    r"twitter\.com/i/adsct",
                    r"linkedin\.com/px",
                    r"snap\.licdn\.com",
                    r"pinterest\.com/ct"
                ],
                "domains": [
                    "connect.facebook.net",
                    "facebook.com",
                    "twitter.com",
                    "linkedin.com",
                    "pinterest.com"
                ]
            },
            "fingerprinting": {
                "risk": "critical",
                "patterns": [
                    r"navigator\.userAgent",
                    r"navigator\.platform",
                    r"screen\.width.*screen\.height",
                    r"getTimezoneOffset",
                    r"canvas\.toDataURL",
                    r"audioContext.*fingerprint",
                    r"webgl.*fingerprint",
                    r"font.*detection",
                    r"battery.*level"
                ]
            },
            "ad_trackers": {
                "risk": "high",
                "patterns": [
                    r"doubleclick\.net",
                    r"googlesyndication\.com",
                    r"adservice\.google",
                    r"facebook\.com/tr",
                    r"ads-twitter\.com",
                    r"advertising\.com",
                    r"criteo\.com",
                    r"taboola\.com"
                ],
                "domains": [
                    "doubleclick.net",
                    "googlesyndication.com",
                    "criteo.com",
                    "taboola.com",
                    "outbrain.com"
                ]
            },
            "telemetry": {
                "risk": "medium",
                "patterns": [
                    r"telemetry\.send",
                    r"beacon\.send",
                    r"sendBeacon",
                    r"crash\.report",
                    r"error\.tracking",
                    r"sentry\.io",
                    r"bugsnag\.notify"
                ]
            },
            "session_replay": {
                "risk": "critical",
                "patterns": [
                    r"hotjar\.com",
                    r"fullstory\.com",
                    r"logrocket\.com",
                    r"mouseflow\.com",
                    r"smartlook\.com",
                    r"session.*replay",
                    r"record.*session"
                ]
            },
            "cookies": {
                "risk": "medium",
                "patterns": [
                    r"document\.cookie\s*=",
                    r"setCookie",
                    r"_ga=",
                    r"_gid=",
                    r"_fbp=",
                    r"third.*party.*cookie"
                ]
            }
        }
    
    def analyze_file(self, filepath: Path) -> List[Dict]:
        """Analyze file for trackers"""
        trackers = []
        
        if not filepath.is_file() or filepath.stat().st_size > 10 * 1024 * 1024:
            return trackers
        
        try:
            content = filepath.read_text(encoding='utf-8', errors='ignore')
            
            # Scan for each tracker type
            for tracker_type, tracker_info in self.tracker_db.items():
                patterns = tracker_info.get("patterns", [])
                risk = tracker_info.get("risk", "medium")
                
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        tracker = {
                            "file": str(filepath),
                            "type": tracker_type,
                            "risk": risk,
                            "pattern": pattern,
                            "match": match.group(0),
                            "line": content[:match.start()].count('\n') + 1,
                            "context": content[max(0, match.start()-50):match.end()+50]
                        }
                        trackers.append(tracker)
                        
                        # Log by risk level
                        if risk == "critical":
                            self.detection_log["high_risk"].append(tracker)
                        elif risk == "high":
                            self.detection_log["high_risk"].append(tracker)
                        elif risk == "medium":
                            self.detection_log["medium_risk"].append(tracker)
                        else:
                            self.detection_log["low_risk"].append(tracker)
                        
                        # Count by type
                        if tracker_type not in self.detection_log["tracker_types"]:
                            self.detection_log["tracker_types"][tracker_type] = 0
                        self.detection_log["tracker_types"][tracker_type] += 1
        
        except Exception as e:
            logger.debug(f"Cannot analyze {filepath}: {e}")
        
        return trackers
    
    def scan_directory(self, directory: Path) -> None:
        """Scan directory for trackers"""
        logger.info(f"🐕 Hunting trackers in: {directory}")
        
        # Target file extensions
        tracker_extensions = [
            '.js', '.html', '.htm', '.php', '.py', '.java',
            '.cs', '.rb', '.go', '.ts', '.jsx', '.tsx'
        ]
        
        try:
            for filepath in directory.rglob("*"):
                if filepath.suffix.lower() in tracker_extensions:
                    trackers = self.analyze_file(filepath)
                    
                    if trackers:
                        self.detection_log["trackers_found"].extend(trackers)
                        logger.warning(f"⚠️  Trackers found in: {filepath}")
                        for tracker in trackers:
                            logger.warning(f"    [{tracker['risk'].upper()}] {tracker['type']}: {tracker['match'][:50]}")
        
        except Exception as e:
            logger.error(f"Error scanning directory: {e}")
    
    def generate_tracker_profile(self) -> Dict:
        """Generate comprehensive tracker profile"""
        profile = {
            "total_trackers": len(self.detection_log["trackers_found"]),
            "by_risk": {
                "critical": len([t for t in self.detection_log["trackers_found"] if t.get("risk") == "critical"]),
                "high": len([t for t in self.detection_log["trackers_found"] if t.get("risk") == "high"]),
                "medium": len([t for t in self.detection_log["trackers_found"] if t.get("risk") == "medium"]),
                "low": len([t for t in self.detection_log["trackers_found"] if t.get("risk") == "low"])
            },
            "by_type": self.detection_log["tracker_types"],
            "affected_files": list(set([t["file"] for t in self.detection_log["trackers_found"]])),
            "recommendations": []
        }
        
        # Generate recommendations
        if profile["by_risk"]["critical"] > 0:
            profile["recommendations"].append("CRITICAL: Remove session replay and fingerprinting trackers immediately")
        
        if profile["by_risk"]["high"] > 0:
            profile["recommendations"].append("HIGH: Review and remove analytics and ad trackers")
        
        if "analytics" in self.detection_log["tracker_types"]:
            profile["recommendations"].append("Consider privacy-friendly analytics alternatives (Plausible, Fathom)")
        
        if "fingerprinting" in self.detection_log["tracker_types"]:
            profile["recommendations"].append("Remove device fingerprinting code - major privacy violation")
        
        return profile
    
    def generate_report(self) -> Dict:
        """Generate detection report"""
        profile = self.generate_tracker_profile()
        
        report = {
            "agent": "Hound Tracker Detection Agent",
            "timestamp": self.detection_log["timestamp"],
            "profile": profile,
            "trackers_found": self.detection_log["trackers_found"],
            "high_risk_trackers": self.detection_log["high_risk"],
            "medium_risk_trackers": self.detection_log["medium_risk"],
            "low_risk_trackers": self.detection_log["low_risk"]
        }
        
        # Save report
        report_dir = Path("data/security/reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = report_dir / f"hound_tracker_detection_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📄 Report saved: {report_file}")
        
        return report
    
    def deploy(self):
        """Deploy hound agent"""
        logger.info("🐕 Hound Tracker Detection Agent deploying...")
        
        # Scan for trackers
        self.scan_directory(Path.cwd())
        
        # Generate report
        report = self.generate_report()
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"🐕 HOUND TRACKER DETECTION COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"  Total Trackers: {report['profile']['total_trackers']}")
        logger.info(f"  Critical Risk: {report['profile']['by_risk']['critical']}")
        logger.info(f"  High Risk: {report['profile']['by_risk']['high']}")
        logger.info(f"  Medium Risk: {report['profile']['by_risk']['medium']}")
        logger.info(f"  Affected Files: {len(report['profile']['affected_files'])}")
        logger.info(f"{'='*60}")
        
        if report['profile']['recommendations']:
            logger.info("\n📋 RECOMMENDATIONS:")
            for rec in report['profile']['recommendations']:
                logger.info(f"  • {rec}")
        
        return report

def main():
    """Main entry point"""
    hound = HoundTrackerAgent()
    report = hound.deploy()
    return report

if __name__ == "__main__":
    main()
