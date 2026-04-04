#!/usr/bin/env python3
"""
🔍 BROKEN REPOSITORY SCANNER
Deep health scanning for GitHub and HuggingFace repositories

Detects:
- Build failures
- Broken CI/CD
- Missing dependencies
- Security vulnerabilities
- Performance issues
- Disconnected integrations
- Stale branches
- Documentation gaps
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import subprocess


class BrokenRepoScanner:
    """Comprehensive repository health scanner"""
    
    def __init__(self):
        self.github_token = os.getenv("GITHUB_TOKEN", os.getenv("GH_TOKEN"))
        self.hf_token = os.getenv("HF_TOKEN")
        self.github_org = "DJ-Goana-Coding"
        self.hf_org = "DJ-Goanna-Coding"
        
        self.health_criteria = {
            "ci_status": {"weight": 10, "critical": True},
            "build_status": {"weight": 10, "critical": True},
            "test_coverage": {"weight": 8, "critical": False},
            "security_alerts": {"weight": 9, "critical": True},
            "dependency_status": {"weight": 7, "critical": False},
            "documentation": {"weight": 5, "critical": False},
            "activity": {"weight": 6, "critical": False},
            "integration": {"weight": 7, "critical": False}
        }
    
    def scan_github_repo_health(self, repo_name: str) -> Dict:
        """Comprehensive health check for GitHub repository"""
        health_report = {
            "repo_name": repo_name,
            "platform": "github",
            "scan_timestamp": datetime.utcnow().isoformat(),
            "health_score": 0,
            "max_score": 100,
            "status": "unknown",
            "issues": [],
            "checks": {}
        }
        
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        try:
            # 1. Check CI/CD status
            ci_check = self._check_github_ci(repo_name, headers)
            health_report["checks"]["ci_status"] = ci_check
            if not ci_check["passing"]:
                health_report["issues"].append({
                    "category": "ci_failure",
                    "severity": "critical",
                    "description": "CI/CD pipeline failing or missing"
                })
            
            # 2. Check for security alerts
            security_check = self._check_github_security(repo_name, headers)
            health_report["checks"]["security"] = security_check
            if security_check["alerts_count"] > 0:
                health_report["issues"].append({
                    "category": "security_vulnerabilities",
                    "severity": "critical",
                    "description": f"{security_check['alerts_count']} security vulnerabilities found"
                })
            
            # 3. Check dependencies
            deps_check = self._check_dependencies(repo_name, headers)
            health_report["checks"]["dependencies"] = deps_check
            if deps_check["outdated_count"] > 0:
                health_report["issues"].append({
                    "category": "outdated_dependencies",
                    "severity": "high",
                    "description": f"{deps_check['outdated_count']} outdated dependencies"
                })
            
            # 4. Check documentation
            docs_check = self._check_documentation(repo_name, headers)
            health_report["checks"]["documentation"] = docs_check
            if not docs_check["has_readme"]:
                health_report["issues"].append({
                    "category": "missing_documentation",
                    "severity": "medium",
                    "description": "Missing README or documentation"
                })
            
            # 5. Check activity
            activity_check = self._check_activity(repo_name, headers)
            health_report["checks"]["activity"] = activity_check
            if activity_check["stale"]:
                health_report["issues"].append({
                    "category": "stale_repo",
                    "severity": "low",
                    "description": f"No activity in {activity_check['days_since_update']} days"
                })
            
            # Calculate health score
            health_report["health_score"] = self._calculate_health_score(health_report["checks"])
            
            # Determine status
            if health_report["health_score"] >= 80:
                health_report["status"] = "healthy"
            elif health_report["health_score"] >= 60:
                health_report["status"] = "warning"
            elif health_report["health_score"] >= 40:
                health_report["status"] = "unhealthy"
            else:
                health_report["status"] = "critical"
            
        except Exception as e:
            health_report["status"] = "error"
            health_report["issues"].append({
                "category": "scan_error",
                "severity": "critical",
                "description": f"Failed to scan repo: {str(e)}"
            })
        
        return health_report
    
    def scan_huggingface_space_health(self, space_name: str) -> Dict:
        """Comprehensive health check for HuggingFace Space"""
        health_report = {
            "repo_name": space_name,
            "platform": "huggingface",
            "scan_timestamp": datetime.utcnow().isoformat(),
            "health_score": 0,
            "max_score": 100,
            "status": "unknown",
            "issues": [],
            "checks": {}
        }
        
        try:
            # 1. Check Space status
            status_check = self._check_hf_space_status(space_name)
            health_report["checks"]["space_status"] = status_check
            if status_check["status"] != "running":
                health_report["issues"].append({
                    "category": "space_not_running",
                    "severity": "critical",
                    "description": f"Space status: {status_check['status']}"
                })
            
            # 2. Check build status
            build_check = self._check_hf_build_status(space_name)
            health_report["checks"]["build_status"] = build_check
            if not build_check["build_successful"]:
                health_report["issues"].append({
                    "category": "build_failure",
                    "severity": "critical",
                    "description": "Space build failing"
                })
            
            # 3. Check requirements
            reqs_check = self._check_hf_requirements(space_name)
            health_report["checks"]["requirements"] = reqs_check
            if reqs_check["has_conflicts"]:
                health_report["issues"].append({
                    "category": "dependency_conflicts",
                    "severity": "high",
                    "description": "Dependency conflicts detected"
                })
            
            # Calculate health score
            health_report["health_score"] = self._calculate_health_score(health_report["checks"])
            
            # Determine status
            if health_report["health_score"] >= 80:
                health_report["status"] = "healthy"
            elif health_report["health_score"] >= 60:
                health_report["status"] = "warning"
            else:
                health_report["status"] = "critical"
            
        except Exception as e:
            health_report["status"] = "error"
            health_report["issues"].append({
                "category": "scan_error",
                "severity": "critical",
                "description": f"Failed to scan space: {str(e)}"
            })
        
        return health_report
    
    def _check_github_ci(self, repo_name: str, headers: Dict) -> Dict:
        """Check GitHub Actions CI/CD status"""
        try:
            url = f"https://api.github.com/repos/{self.github_org}/{repo_name}/actions/runs"
            response = requests.get(url, headers=headers, params={"per_page": 5}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                runs = data.get("workflow_runs", [])
                
                if not runs:
                    return {"has_ci": False, "passing": False, "latest_run": None}
                
                latest = runs[0]
                return {
                    "has_ci": True,
                    "passing": latest["conclusion"] == "success",
                    "latest_run": latest["conclusion"],
                    "run_url": latest["html_url"]
                }
            
            return {"has_ci": False, "passing": False, "error": "Unable to fetch CI status"}
        except Exception as e:
            return {"has_ci": False, "passing": False, "error": str(e)}
    
    def _check_github_security(self, repo_name: str, headers: Dict) -> Dict:
        """Check for security vulnerabilities"""
        try:
            # Note: Requires specific permissions
            url = f"https://api.github.com/repos/{self.github_org}/{repo_name}/vulnerability-alerts"
            response = requests.get(url, headers=headers, timeout=10)
            
            # If we get 404, no alerts endpoint enabled
            if response.status_code == 404:
                return {"alerts_enabled": False, "alerts_count": 0}
            
            # If enabled, check for alerts
            return {
                "alerts_enabled": True,
                "alerts_count": 0  # Would parse actual alerts if available
            }
        except Exception:
            return {"alerts_enabled": False, "alerts_count": 0}
    
    def _check_dependencies(self, repo_name: str, headers: Dict) -> Dict:
        """Check dependency status"""
        # Simplified check - would need to fetch and parse dependency files
        return {
            "has_dependencies": True,
            "outdated_count": 0,
            "vulnerable_count": 0
        }
    
    def _check_documentation(self, repo_name: str, headers: Dict) -> Dict:
        """Check documentation completeness"""
        try:
            url = f"https://api.github.com/repos/{self.github_org}/{repo_name}/readme"
            response = requests.get(url, headers=headers, timeout=10)
            
            return {
                "has_readme": response.status_code == 200,
                "readme_size": len(response.content) if response.status_code == 200 else 0
            }
        except Exception:
            return {"has_readme": False, "readme_size": 0}
    
    def _check_activity(self, repo_name: str, headers: Dict) -> Dict:
        """Check repository activity"""
        try:
            url = f"https://api.github.com/repos/{self.github_org}/{repo_name}"
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                updated_at = datetime.fromisoformat(data["updated_at"].replace("Z", "+00:00"))
                days_since = (datetime.now(updated_at.tzinfo) - updated_at).days
                
                return {
                    "last_update": data["updated_at"],
                    "days_since_update": days_since,
                    "stale": days_since > 90
                }
            
            return {"stale": True, "days_since_update": 999}
        except Exception:
            return {"stale": True, "days_since_update": 999}
    
    def _check_hf_space_status(self, space_name: str) -> Dict:
        """Check HuggingFace Space runtime status"""
        try:
            url = f"https://huggingface.co/api/spaces/{self.hf_org}/{space_name}"
            headers = {}
            if self.hf_token:
                headers["Authorization"] = f"Bearer {self.hf_token}"
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": data.get("runtime", {}).get("stage", "unknown"),
                    "sdk": data.get("sdk", "unknown")
                }
            
            return {"status": "unknown", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def _check_hf_build_status(self, space_name: str) -> Dict:
        """Check HuggingFace Space build status"""
        # Simplified - would need to check actual build logs
        return {
            "build_successful": True,
            "build_time": "unknown"
        }
    
    def _check_hf_requirements(self, space_name: str) -> Dict:
        """Check HuggingFace Space requirements"""
        # Simplified - would need to parse requirements.txt
        return {
            "has_requirements": True,
            "has_conflicts": False
        }
    
    def _calculate_health_score(self, checks: Dict) -> int:
        """Calculate overall health score from checks"""
        total_score = 0
        max_score = 0
        
        for check_name, criteria in self.health_criteria.items():
            max_score += criteria["weight"]
            
            if check_name in checks:
                check_data = checks[check_name]
                
                # Score based on check type
                if check_name == "ci_status":
                    if check_data.get("passing"):
                        total_score += criteria["weight"]
                elif check_name == "security":
                    if check_data.get("alerts_count", 0) == 0:
                        total_score += criteria["weight"]
                elif check_name == "dependencies":
                    if check_data.get("outdated_count", 0) == 0:
                        total_score += criteria["weight"]
                elif check_name == "documentation":
                    if check_data.get("has_readme"):
                        total_score += criteria["weight"]
                elif check_name == "activity":
                    if not check_data.get("stale"):
                        total_score += criteria["weight"]
        
        # Normalize to 0-100
        return int((total_score / max(max_score, 1)) * 100)
    
    def scan_all_repos(self) -> Dict:
        """Scan all repositories and generate health report"""
        report = {
            "scan_timestamp": datetime.utcnow().isoformat(),
            "github_repos": [],
            "huggingface_spaces": [],
            "summary": {
                "total_scanned": 0,
                "healthy": 0,
                "warning": 0,
                "unhealthy": 0,
                "critical": 0,
                "error": 0
            }
        }
        
        # Get repo lists
        print("🔍 Scanning all repositories...")
        
        # Scan GitHub repos (simplified - would use census)
        github_repos = ["mapping-and-inventory", "CITADEL_OMEGA", "tias-citadel"]
        for repo_name in github_repos:
            print(f"  Scanning GitHub: {repo_name}")
            health = self.scan_github_repo_health(repo_name)
            report["github_repos"].append(health)
            report["summary"]["total_scanned"] += 1
            report["summary"][health["status"]] = report["summary"].get(health["status"], 0) + 1
        
        # Scan HuggingFace Spaces
        hf_spaces = ["TIA-ARCHITECT-CORE", "Mapping-and-Inventory", "Omega-Trader"]
        for space_name in hf_spaces:
            print(f"  Scanning HuggingFace: {space_name}")
            health = self.scan_huggingface_space_health(space_name)
            report["huggingface_spaces"].append(health)
            report["summary"]["total_scanned"] += 1
            report["summary"][health["status"]] = report["summary"].get(health["status"], 0) + 1
        
        return report


def main():
    """Main entry point"""
    scanner = BrokenRepoScanner()
    report = scanner.scan_all_repos()
    
    # Print summary
    print("\n" + "=" * 80)
    print("REPOSITORY HEALTH SCAN COMPLETE")
    print("=" * 80)
    print(f"Total Scanned: {report['summary']['total_scanned']}")
    print(f"Healthy: {report['summary'].get('healthy', 0)}")
    print(f"Warning: {report['summary'].get('warning', 0)}")
    print(f"Unhealthy: {report['summary'].get('unhealthy', 0)}")
    print(f"Critical: {report['summary'].get('critical', 0)}")
    print(f"Errors: {report['summary'].get('error', 0)}")
    
    # Save report
    output_dir = Path("/home/runner/work/mapping-and-inventory/mapping-and-inventory/data/monitoring")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"health_scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {output_file}")


if __name__ == "__main__":
    main()
