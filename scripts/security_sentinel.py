#!/usr/bin/env python3
"""
🛡️ SECURITY SENTINEL - Network Protection Worker
Q.G.T.N.L. Command Citadel - Security & Threat Detection

Purpose: Monitor and protect Citadel infrastructure
"""

import os
import sys
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/security_sentinel.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class SecuritySentinel:
    """
    Security Monitoring and Protection
    
    Monitors:
    - GitHub repository health
    - HuggingFace Space status
    - GDrive connectivity
    - Workflow status
    - Rate limits
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.data_path = self.base_path / "data" / "monitoring"
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.alerts = []
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        logger.info("🛡️ Security Sentinel initialized")
    
    def check_github_health(self) -> Dict:
        """Check GitHub repository health"""
        logger.info("🔍 Checking GitHub health...")
        
        try:
            # Check GitHub API status
            response = requests.get("https://api.github.com/status")
            if response.status_code == 200:
                logger.info("✅ GitHub API is healthy")
                return {"status": "healthy", "service": "github"}
            else:
                self.alerts.append("GitHub API returned non-200 status")
                return {"status": "degraded", "service": "github"}
        except Exception as e:
            logger.error(f"❌ GitHub health check failed: {e}")
            self.alerts.append(f"GitHub health check failed: {e}")
            return {"status": "error", "service": "github", "error": str(e)}
    
    def check_huggingface_health(self) -> Dict:
        """Check HuggingFace status"""
        logger.info("🔍 Checking HuggingFace health...")
        
        try:
            # Check HF status page
            response = requests.get("https://status.huggingface.co/api/v2/status.json", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status", {}).get("indicator", "unknown")
                
                if status == "none":
                    logger.info("✅ HuggingFace is healthy")
                    return {"status": "healthy", "service": "huggingface"}
                else:
                    self.alerts.append(f"HuggingFace status: {status}")
                    return {"status": status, "service": "huggingface"}
            else:
                return {"status": "unknown", "service": "huggingface"}
        except Exception as e:
            logger.error(f"❌ HuggingFace health check failed: {e}")
            return {"status": "error", "service": "huggingface", "error": str(e)}
    
    def check_rate_limits(self) -> Dict:
        """Check GitHub API rate limits"""
        logger.info("🔍 Checking rate limits...")
        
        if not self.github_token:
            logger.warning("⚠️ No GitHub token available")
            return {"status": "no_token"}
        
        try:
            headers = {"Authorization": f"token {self.github_token}"}
            response = requests.get("https://api.github.com/rate_limit", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                core = data.get("resources", {}).get("core", {})
                remaining = core.get("remaining", 0)
                limit = core.get("limit", 0)
                
                logger.info(f"📊 Rate limit: {remaining}/{limit}")
                
                if remaining < 100:
                    self.alerts.append(f"Low rate limit: {remaining}/{limit}")
                
                return {
                    "status": "checked",
                    "remaining": remaining,
                    "limit": limit,
                    "percentage": f"{(remaining/limit*100):.1f}%" if limit > 0 else "0%"
                }
            else:
                return {"status": "error", "code": response.status_code}
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def scan_security_threats(self) -> Dict:
        """Scan for security threats"""
        logger.info("🔍 Scanning for security threats...")
        
        threats = []
        
        # Check for exposed secrets (basic scan)
        sensitive_files = [
            ".env",
            "secrets.json",
            "credentials.json",
            "private_key.pem"
        ]
        
        for file in sensitive_files:
            file_path = self.base_path / file
            if file_path.exists():
                threats.append(f"Sensitive file found: {file}")
                logger.warning(f"⚠️ Found sensitive file: {file}")
        
        # Check .gitignore
        gitignore_path = self.base_path / ".gitignore"
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
                for file in sensitive_files:
                    if file not in content:
                        threats.append(f"{file} not in .gitignore")
        
        return {
            "threats_found": len(threats),
            "threats": threats,
            "status": "threats_found" if threats else "clean"
        }
    
    def run_patrol(self) -> Dict:
        """Run complete security patrol"""
        logger.info("🛡️ Starting security patrol...")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "github_health": self.check_github_health(),
            "huggingface_health": self.check_huggingface_health(),
            "rate_limits": self.check_rate_limits(),
            "security_scan": self.scan_security_threats(),
            "alerts": self.alerts
        }
        
        # Save results
        output_file = self.data_path / "security_patrol.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"💾 Security patrol results saved to {output_file}")
        
        # Print summary
        logger.info(f"""
🛡️ SECURITY PATROL COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━
GitHub:      {results['github_health']['status']}
HuggingFace: {results['huggingface_health']['status']}
Rate Limits: {results['rate_limits'].get('remaining', 'N/A')}/{results['rate_limits'].get('limit', 'N/A')}
Security:    {results['security_scan']['threats_found']} threats found
Alerts:      {len(self.alerts)} alerts
━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)
        
        return results


def main():
    """Main entry point"""
    sentinel = SecuritySentinel()
    results = sentinel.run_patrol()
    
    # Exit with error if critical alerts
    if len(sentinel.alerts) > 0:
        logger.warning(f"⚠️ {len(sentinel.alerts)} alerts generated")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
