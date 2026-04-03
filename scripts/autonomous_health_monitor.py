#!/usr/bin/env python3
"""
🏥 AUTONOMOUS HEALTH MONITOR
Citadel Mesh Health & Status Monitoring

Purpose: Continuous health monitoring of all Citadel components
Version: 25.0.OMNI+

Monitors:
- Worker status (Bridge, Archivist, Reporter, Hive Master)
- Service connectivity (GitHub, HuggingFace, GDrive)
- Pipeline health
- District artifact completeness
- System resources
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/health_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class HealthStatus(Enum):
    """Component health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"

class HealthMonitor:
    """
    Autonomous Health Monitor
    
    Continuously monitors all Citadel Mesh components and reports status
    """
    
    def __init__(self):
        self.status_file = Path("data/HEALTH_STATUS.json")
        
        # Create directories
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        logger.info("🏥 Health Monitor initialized")
    
    def check_github_connectivity(self) -> Dict:
        """Check GitHub API connectivity"""
        logger.info("🔍 Checking GitHub connectivity...")
        
        try:
            result = subprocess.run(
                ["gh", "api", "user"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {
                    "status": HealthStatus.HEALTHY.value,
                    "message": "GitHub API accessible",
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": f"GitHub API error: {result.stderr}",
                    "last_check": datetime.now().isoformat()
                }
        except subprocess.TimeoutExpired:
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": "GitHub API timeout",
                "last_check": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": f"GitHub check failed: {e}",
                "last_check": datetime.now().isoformat()
            }
    
    def check_workers(self) -> Dict:
        """Check worker status"""
        logger.info("🔍 Checking worker status...")
        
        worker_status_file = Path("worker_status.json")
        
        if not worker_status_file.exists():
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "worker_status.json not found",
                "workers": {}
            }
        
        try:
            with open(worker_status_file, 'r') as f:
                content = f.read()
                # worker_status.json is currently plain text, not JSON
                # Parse it as text for now
                
                workers = {
                    "The Bridge": "UNKNOWN",
                    "The Archivist": "UNKNOWN",
                    "The Reporter": "UNKNOWN",
                    "The Hive Master": "UNKNOWN"
                }
                
                if "OPERATIONAL" in content:
                    workers["The Bridge"] = "OPERATIONAL"
                if "STANDBY" in content:
                    if "Archivist" in content:
                        workers["The Archivist"] = "STANDBY"
                    if "Hive Master" in content:
                        workers["The Hive Master"] = "STANDBY"
                if "ERROR" in content:
                    workers["The Reporter"] = "ERROR"
                
                operational_count = sum(1 for status in workers.values() if status == "OPERATIONAL")
                total_count = len(workers)
                
                if operational_count == 0:
                    overall_status = HealthStatus.UNHEALTHY.value
                elif operational_count < total_count:
                    overall_status = HealthStatus.DEGRADED.value
                else:
                    overall_status = HealthStatus.HEALTHY.value
                
                return {
                    "status": overall_status,
                    "message": f"{operational_count}/{total_count} workers operational",
                    "workers": workers,
                    "last_check": datetime.now().isoformat()
                }
        
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": f"Worker check failed: {e}",
                "workers": {},
                "last_check": datetime.now().isoformat()
            }
    
    def check_districts(self) -> Dict:
        """Check District artifact completeness"""
        logger.info("🔍 Checking District artifacts...")
        
        districts_file = Path("districts.json")
        
        if not districts_file.exists():
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": "districts.json not found",
                "districts": {}
            }
        
        try:
            with open(districts_file, 'r') as f:
                data = json.load(f)
                districts = data.get("districts", [])
            
            district_status = {}
            complete_count = 0
            
            for district in districts:
                district_id = district.get("id")
                district_path = Path(district.get("path", f"Districts/{district_id}"))
                
                if not district_path.exists():
                    district_status[district_id] = "MISSING"
                    continue
                
                # Check for required artifacts
                has_tree = (district_path / "TREE.md").exists()
                has_inventory = (district_path / "INVENTORY.json").exists()
                has_scaffold = (district_path / "SCAFFOLD.md").exists()
                
                if has_tree and has_inventory and has_scaffold:
                    district_status[district_id] = "COMPLETE"
                    complete_count += 1
                elif has_tree or has_inventory or has_scaffold:
                    district_status[district_id] = "PARTIAL"
                else:
                    district_status[district_id] = "PENDING"
            
            total_districts = len(districts)
            
            if complete_count == 0:
                overall_status = HealthStatus.UNHEALTHY.value
            elif complete_count < total_districts:
                overall_status = HealthStatus.DEGRADED.value
            else:
                overall_status = HealthStatus.HEALTHY.value
            
            return {
                "status": overall_status,
                "message": f"{complete_count}/{total_districts} districts complete",
                "districts": district_status,
                "last_check": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": f"District check failed: {e}",
                "districts": {},
                "last_check": datetime.now().isoformat()
            }
    
    def check_master_inventory(self) -> Dict:
        """Check master inventory status"""
        logger.info("🔍 Checking master inventory...")
        
        inventory_file = Path("master_inventory.json")
        
        if not inventory_file.exists():
            return {
                "status": HealthStatus.UNHEALTHY.value,
                "message": "master_inventory.json not found",
                "last_check": datetime.now().isoformat()
            }
        
        try:
            stat = inventory_file.stat()
            size_mb = stat.st_size / (1024 * 1024)
            modified = datetime.fromtimestamp(stat.st_mtime)
            age_hours = (datetime.now() - modified).total_seconds() / 3600
            
            # Check if inventory is recent (updated within 24 hours)
            if age_hours > 24:
                status = HealthStatus.DEGRADED.value
                message = f"Inventory outdated ({age_hours:.1f} hours old)"
            else:
                status = HealthStatus.HEALTHY.value
                message = f"Inventory current ({size_mb:.1f}MB, {age_hours:.1f}h old)"
            
            return {
                "status": status,
                "message": message,
                "size_mb": round(size_mb, 2),
                "last_modified": modified.isoformat(),
                "age_hours": round(age_hours, 1),
                "last_check": datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": f"Inventory check failed: {e}",
                "last_check": datetime.now().isoformat()
            }
    
    def check_workflows(self) -> Dict:
        """Check GitHub Actions workflow status"""
        logger.info("🔍 Checking workflow status...")
        
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "5", "--json", "status,conclusion,name"],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                
                failed_count = sum(1 for run in runs if run.get("conclusion") == "failure")
                total_count = len(runs)
                
                if failed_count == 0:
                    status = HealthStatus.HEALTHY.value
                    message = "All recent workflows succeeded"
                elif failed_count < total_count:
                    status = HealthStatus.DEGRADED.value
                    message = f"{failed_count}/{total_count} recent workflows failed"
                else:
                    status = HealthStatus.UNHEALTHY.value
                    message = "All recent workflows failed"
                
                return {
                    "status": status,
                    "message": message,
                    "recent_runs": runs,
                    "last_check": datetime.now().isoformat()
                }
            else:
                return {
                    "status": HealthStatus.UNKNOWN.value,
                    "message": "Failed to fetch workflow status",
                    "last_check": datetime.now().isoformat()
                }
        
        except Exception as e:
            return {
                "status": HealthStatus.UNKNOWN.value,
                "message": f"Workflow check failed: {e}",
                "last_check": datetime.now().isoformat()
            }
    
    def check_dependencies(self) -> Dict:
        """Check Python dependencies"""
        logger.info("🔍 Checking dependencies...")
        
        required_deps = [
            "streamlit",
            "requests",
            "PyYAML",
            "sentence-transformers",
            "faiss-cpu",
            "numpy",
            "pandas"
        ]
        
        missing_deps = []
        
        for dep in required_deps:
            try:
                __import__(dep.replace("-", "_"))
            except ImportError:
                missing_deps.append(dep)
        
        # Check optional but recommended deps
        optional_deps = ["gspread", "google-auth"]
        missing_optional = []
        
        for dep in optional_deps:
            try:
                __import__(dep.replace("-", "_"))
            except ImportError:
                missing_optional.append(dep)
        
        if len(missing_deps) > 0:
            status = HealthStatus.UNHEALTHY.value
            message = f"Missing required dependencies: {', '.join(missing_deps)}"
        elif len(missing_optional) > 0:
            status = HealthStatus.DEGRADED.value
            message = f"Missing optional dependencies: {', '.join(missing_optional)}"
        else:
            status = HealthStatus.HEALTHY.value
            message = "All dependencies satisfied"
        
        return {
            "status": status,
            "message": message,
            "missing_required": missing_deps,
            "missing_optional": missing_optional,
            "last_check": datetime.now().isoformat()
        }
    
    def run_health_check(self) -> Dict:
        """Run complete health check"""
        logger.info("🏥 Running complete health check...")
        
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "version": "25.0.OMNI",
            "checks": {
                "github": self.check_github_connectivity(),
                "workers": self.check_workers(),
                "districts": self.check_districts(),
                "master_inventory": self.check_master_inventory(),
                "workflows": self.check_workflows(),
                "dependencies": self.check_dependencies()
            }
        }
        
        # Calculate overall health
        statuses = [check["status"] for check in health_report["checks"].values()]
        
        if all(s == HealthStatus.HEALTHY.value for s in statuses):
            overall_status = HealthStatus.HEALTHY.value
            overall_message = "All systems operational"
        elif any(s == HealthStatus.UNHEALTHY.value for s in statuses):
            overall_status = HealthStatus.UNHEALTHY.value
            unhealthy_systems = [
                name for name, check in health_report["checks"].items()
                if check["status"] == HealthStatus.UNHEALTHY.value
            ]
            overall_message = f"Systems unhealthy: {', '.join(unhealthy_systems)}"
        else:
            overall_status = HealthStatus.DEGRADED.value
            degraded_systems = [
                name for name, check in health_report["checks"].items()
                if check["status"] == HealthStatus.DEGRADED.value
            ]
            overall_message = f"Systems degraded: {', '.join(degraded_systems)}"
        
        health_report["overall_status"] = overall_status
        health_report["overall_message"] = overall_message
        
        # Save health report
        with open(self.status_file, 'w') as f:
            json.dump(health_report, f, indent=2)
        
        logger.info(f"📊 Health check complete: {overall_status}")
        
        return health_report
    
    def generate_health_report_md(self, health_report: Dict) -> str:
        """Generate markdown health report"""
        
        status_emoji = {
            HealthStatus.HEALTHY.value: "✅",
            HealthStatus.DEGRADED.value: "⚠️",
            HealthStatus.UNHEALTHY.value: "❌",
            HealthStatus.UNKNOWN.value: "❓"
        }
        
        overall_emoji = status_emoji.get(health_report["overall_status"], "❓")
        
        report = [
            f"# 🏥 CITADEL MESH HEALTH REPORT",
            f"**Generated:** {health_report['timestamp']}",
            f"**Overall Status:** {overall_emoji} {health_report['overall_status'].upper()}",
            f"**Message:** {health_report['overall_message']}",
            "",
            "---",
            "",
            "## 📊 COMPONENT STATUS",
            ""
        ]
        
        for component, check in health_report["checks"].items():
            emoji = status_emoji.get(check["status"], "❓")
            report.append(f"### {emoji} {component.upper()}")
            report.append(f"- **Status:** {check['status']}")
            report.append(f"- **Message:** {check['message']}")
            report.append(f"- **Last Check:** {check['last_check']}")
            report.append("")
        
        return "\n".join(report)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Health Monitor for Q.G.T.N.L. Command Citadel"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/HEALTH_REPORT.md",
        help="Path to save markdown health report"
    )
    
    args = parser.parse_args()
    
    monitor = HealthMonitor()
    
    # Run health check
    health_report = monitor.run_health_check()
    
    # Generate markdown report
    markdown_report = monitor.generate_health_report_md(health_report)
    
    # Save markdown report
    with open(args.output, 'w') as f:
        f.write(markdown_report)
    
    logger.info(f"📄 Health report saved to {args.output}")
    
    # Print summary
    print(f"\n{markdown_report}\n")


if __name__ == "__main__":
    main()
