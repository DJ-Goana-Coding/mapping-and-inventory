#!/usr/bin/env python3
"""
TITAN 392 HEALTH MONITOR
Citadel Architect — Health & Status Monitoring

Monitors all 392 integration points and reports system health.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any

# Repository root
repo_root = Path(__file__).parent.parent
os.chdir(repo_root)


class TitanHealthMonitor:
    """Monitors health of TITAN 392 infrastructure."""
    
    def __init__(self):
        self.timestamp = datetime.utcnow()
        self.registry_path = repo_root / "data" / "titan_392_registry.json"
        self.health_report_path = repo_root / "data" / "monitoring" / "titan_health.json"
        self.alerts = []
        
        # Ensure monitoring directory exists
        self.health_report_path.parent.mkdir(parents=True, exist_ok=True)
    
    def load_registry(self) -> Dict[str, Any]:
        """Load Titan 392 registry."""
        if not self.registry_path.exists():
            self.add_alert("CRITICAL", "Titan 392 registry not found")
            return {}
        
        try:
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.add_alert("CRITICAL", f"Failed to load registry: {e}")
            return {}
    
    def add_alert(self, severity: str, message: str):
        """Add an alert to the report."""
        self.alerts.append({
            "severity": severity,
            "message": message,
            "timestamp": self.timestamp.isoformat() + 'Z'
        })
        print(f"[{severity}] {message}")
    
    def check_github_api(self) -> Dict[str, Any]:
        """Check GitHub API health."""
        status = {
            "service": "GitHub API",
            "status": "UNKNOWN",
            "rate_limit": None,
            "rate_remaining": None
        }
        
        try:
            import requests
            token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_PAT')
            
            if not token:
                status["status"] = "UNCONFIGURED"
                self.add_alert("WARNING", "GitHub token not configured")
                return status
            
            headers = {"Authorization": f"token {token}"}
            response = requests.get("https://api.github.com/rate_limit", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                rate_info = data.get('rate', {})
                status["rate_limit"] = rate_info.get('limit', 0)
                status["rate_remaining"] = rate_info.get('remaining', 0)
                
                if status["rate_remaining"] < 100:
                    status["status"] = "DEGRADED"
                    self.add_alert("WARNING", f"GitHub rate limit low: {status['rate_remaining']}/{status['rate_limit']}")
                else:
                    status["status"] = "HEALTHY"
                    print(f"✅ GitHub API healthy: {status['rate_remaining']}/{status['rate_limit']} requests")
            else:
                status["status"] = "ERROR"
                self.add_alert("ERROR", f"GitHub API returned HTTP {response.status_code}")
        
        except Exception as e:
            status["status"] = "ERROR"
            self.add_alert("ERROR", f"GitHub API check failed: {e}")
        
        return status
    
    def check_huggingface_api(self) -> Dict[str, Any]:
        """Check HuggingFace API health."""
        status = {
            "service": "HuggingFace API",
            "status": "UNKNOWN"
        }
        
        try:
            import requests
            token = os.environ.get('HF_TOKEN')
            
            if not token:
                status["status"] = "UNCONFIGURED"
                self.add_alert("WARNING", "HuggingFace token not configured")
                return status
            
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get("https://huggingface.co/api/whoami", headers=headers)
            
            if response.status_code == 200:
                status["status"] = "HEALTHY"
                print("✅ HuggingFace API healthy")
            else:
                status["status"] = "DEGRADED"
                self.add_alert("WARNING", f"HuggingFace API returned HTTP {response.status_code}")
        
        except Exception as e:
            status["status"] = "ERROR"
            self.add_alert("ERROR", f"HuggingFace API check failed: {e}")
        
        return status
    
    def check_districts(self) -> Dict[str, Any]:
        """Check District integrity."""
        districts_dir = repo_root / "Districts"
        
        status = {
            "service": "Districts",
            "status": "UNKNOWN",
            "total_districts": 0,
            "healthy_districts": 0,
            "missing_artifacts": []
        }
        
        if not districts_dir.exists():
            status["status"] = "CRITICAL"
            self.add_alert("CRITICAL", "Districts directory not found")
            return status
        
        required_files = ["TREE.md", "INVENTORY.json", "SCAFFOLD.md"]
        
        for district_path in sorted(districts_dir.iterdir()):
            if not district_path.is_dir():
                continue
            
            status["total_districts"] += 1
            district_name = district_path.name
            district_healthy = True
            
            for required_file in required_files:
                file_path = district_path / required_file
                if not file_path.exists():
                    status["missing_artifacts"].append(f"{district_name}/{required_file}")
                    district_healthy = False
            
            if district_healthy:
                status["healthy_districts"] += 1
        
        if status["missing_artifacts"]:
            status["status"] = "DEGRADED"
            self.add_alert("ERROR", f"Missing District artifacts: {', '.join(status['missing_artifacts'])}")
        else:
            status["status"] = "HEALTHY"
            print(f"✅ All {status['total_districts']} Districts healthy")
        
        return status
    
    def check_workflows(self) -> Dict[str, Any]:
        """Check GitHub workflows."""
        workflows_dir = repo_root / ".github" / "workflows"
        
        status = {
            "service": "GitHub Workflows",
            "status": "UNKNOWN",
            "total_workflows": 0,
            "critical_workflows": []
        }
        
        if not workflows_dir.exists():
            status["status"] = "CRITICAL"
            self.add_alert("CRITICAL", "Workflows directory not found")
            return status
        
        # Count total workflows
        workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
        status["total_workflows"] = len(workflow_files)
        
        # Check critical workflows
        critical_workflows = [
            "pulse_sync_master.yml",
            "mesh_heartbeat.yml",
            "forever_learning_orchestrator.yml"
        ]
        
        for workflow in critical_workflows:
            if (workflows_dir / workflow).exists():
                status["critical_workflows"].append(workflow)
        
        if len(status["critical_workflows"]) == len(critical_workflows):
            status["status"] = "HEALTHY"
            print(f"✅ All {len(critical_workflows)} critical workflows present ({status['total_workflows']} total)")
        else:
            status["status"] = "DEGRADED"
            missing = set(critical_workflows) - set(status["critical_workflows"])
            self.add_alert("WARNING", f"Missing critical workflows: {', '.join(missing)}")
        
        return status
    
    def check_data_structure(self) -> Dict[str, Any]:
        """Check data directory structure."""
        data_dir = repo_root / "data"
        
        status = {
            "service": "Data Structure",
            "status": "UNKNOWN",
            "required_directories": [],
            "missing_directories": []
        }
        
        required_dirs = [
            "monitoring",
            "discoveries",
            "models",
            "workers",
            "datasets",
            "forever_learning"
        ]
        
        for dir_name in required_dirs:
            dir_path = data_dir / dir_name
            if dir_path.exists():
                status["required_directories"].append(dir_name)
            else:
                status["missing_directories"].append(dir_name)
        
        if status["missing_directories"]:
            status["status"] = "DEGRADED"
            self.add_alert("WARNING", f"Missing data directories: {', '.join(status['missing_directories'])}")
        else:
            status["status"] = "HEALTHY"
            print(f"✅ All {len(required_dirs)} required data directories present")
        
        return status
    
    def check_integration_points(self, registry: Dict[str, Any]) -> Dict[str, Any]:
        """Check integration point counts."""
        status = {
            "service": "Integration Points",
            "status": "UNKNOWN",
            "total_points": 0,
            "node_counts": {}
        }
        
        if not registry:
            status["status"] = "ERROR"
            self.add_alert("ERROR", "Cannot check integration points without registry")
            return status
        
        nodes = registry.get("nodes", {})
        total = 0
        
        for node_type, node_data in nodes.items():
            count = node_data.get("count", 0) if isinstance(node_data, dict) else 0
            status["node_counts"][node_type] = count
            total += count
        
        status["total_points"] = total
        
        expected_total = registry.get("total_integration_points", 392)
        
        if total >= expected_total * 0.9:  # Within 10% of expected
            status["status"] = "HEALTHY"
            print(f"✅ Integration points: {total}/{expected_total}")
        else:
            status["status"] = "DEGRADED"
            self.add_alert("WARNING", f"Integration point count low: {total}/{expected_total}")
        
        return status
    
    def generate_health_report(self) -> Dict[str, Any]:
        """Generate complete health report."""
        print("\n🏥 TITAN 392 HEALTH CHECK")
        print("=" * 60)
        
        # Load registry
        registry = self.load_registry()
        
        # Run all health checks
        checks = {
            "github_api": self.check_github_api(),
            "huggingface_api": self.check_huggingface_api(),
            "districts": self.check_districts(),
            "workflows": self.check_workflows(),
            "data_structure": self.check_data_structure(),
            "integration_points": self.check_integration_points(registry)
        }
        
        # Determine overall status
        statuses = [check["status"] for check in checks.values()]
        
        if "CRITICAL" in statuses:
            overall_status = "CRITICAL"
        elif "ERROR" in statuses:
            overall_status = "ERROR"
        elif "DEGRADED" in statuses:
            overall_status = "DEGRADED"
        elif "UNKNOWN" in statuses:
            overall_status = "UNKNOWN"
        else:
            overall_status = "HEALTHY"
        
        # Build report
        report = {
            "timestamp": self.timestamp.isoformat() + 'Z',
            "version": registry.get("version", "unknown"),
            "titan_id": registry.get("titan_id", "TITAN-392-OMNI"),
            "overall_status": overall_status,
            "checks": checks,
            "alerts": self.alerts,
            "next_check": (self.timestamp + timedelta(hours=6)).isoformat() + 'Z'
        }
        
        # Save report
        with open(self.health_report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 Health Report saved to: {self.health_report_path}")
        print(f"🏥 Overall Status: {overall_status}")
        print(f"⚠️ Total Alerts: {len(self.alerts)}")
        
        return report


def main():
    """Main execution."""
    monitor = TitanHealthMonitor()
    report = monitor.generate_health_report()
    
    # Exit with error code if not healthy
    if report["overall_status"] in ["CRITICAL", "ERROR"]:
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
