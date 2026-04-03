#!/usr/bin/env python3
"""
SENTINEL SWARM COORDINATOR
Coordinates tias-sentinel-scout-swarm operations
Manages monitoring, scanning, and distributed sentinel operations

Usage:
    python sentinel_coordinator.py --deploy
    python sentinel_coordinator.py --monitor
    python sentinel_coordinator.py --status
    python sentinel_coordinator.py --alert-check
"""

import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import hashlib


class SentinelSwarmCoordinator:
    """Coordinates sentinel-scout-swarm operations across Citadel Mesh"""
    
    def __init__(self):
        self.sentinels_dir = Path("data/sentinels")
        self.registry_file = self.sentinels_dir / "sentinel_swarm_registry.json"
        self.config_file = self.sentinels_dir / "sentinel_operations_config.json"
        self.alerts_file = self.sentinels_dir / "sentinel_alerts.json"
    
    def deploy_swarm(self):
        """Deploy sentinel swarm with coordination"""
        print("\n🛡️ DEPLOYING SENTINEL SWARM")
        print("=" * 60)
        
        if not self.registry_file.exists():
            print("❌ Sentinel registry not found")
            print("   Run sentinel_swarm_integration.yml workflow first")
            return False
        
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        print(f"Deploying swarm components:")
        print(f"  🛡️ Sentinels: {len(registry['swarm']['sentinels'])}")
        print(f"  🔍 Scouts: {len(registry['swarm']['scouts'])}")
        print(f"  🐝 Coordinators: {len(registry['swarm']['coordinators'])}")
        print(f"  👁️ Monitors: {len(registry['swarm']['monitors'])}")
        
        # Mark all as active
        for category in registry['swarm'].values():
            for component in category:
                component['status'] = 'active'
                component['last_activation'] = datetime.utcnow().isoformat() + "Z"
        
        registry['deployment_status'] = 'active'
        registry['last_updated'] = datetime.utcnow().isoformat() + "Z"
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print("\n✅ Sentinel swarm deployed and active")
        return True
    
    def monitor_resources(self):
        """Run monitoring sweep across Citadel resources"""
        print("\n👁️ SENTINEL MONITORING SWEEP")
        print("=" * 60)
        
        if not self.config_file.exists():
            print("❌ Sentinel config not found")
            return False
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        monitoring_config = config['operations']['monitoring']
        
        if not monitoring_config['enabled']:
            print("⚠️  Monitoring is disabled")
            return False
        
        monitoring_results = {
            "sweep_timestamp": datetime.utcnow().isoformat() + "Z",
            "targets_checked": 0,
            "targets_healthy": 0,
            "targets_missing": 0,
            "alerts_generated": 0,
            "details": []
        }
        
        print("Monitoring targets:")
        for target in monitoring_config['targets']:
            target_path = Path(target)
            
            if target_path.exists():
                status = "✅ HEALTHY"
                monitoring_results["targets_healthy"] += 1
                
                # Calculate checksum for files
                if target_path.is_file():
                    with open(target_path, 'rb') as f:
                        checksum = hashlib.md5(f.read()).hexdigest()[:8]
                    size = target_path.stat().st_size
                    detail = f"{target} - {size} bytes - checksum: {checksum}"
                else:
                    file_count = len(list(target_path.rglob("*")))
                    detail = f"{target} - {file_count} items"
            else:
                status = "❌ MISSING"
                monitoring_results["targets_missing"] += 1
                monitoring_results["alerts_generated"] += 1
                detail = f"{target} - NOT FOUND"
            
            monitoring_results["targets_checked"] += 1
            monitoring_results["details"].append(detail)
            print(f"  {status}: {target}")
        
        # Save monitoring results
        results_file = self.sentinels_dir / "monitoring_results.json"
        with open(results_file, 'w') as f:
            json.dump(monitoring_results, f, indent=2)
        
        print(f"\n📊 Monitoring Summary:")
        print(f"   Checked: {monitoring_results['targets_checked']}")
        print(f"   Healthy: {monitoring_results['targets_healthy']}")
        print(f"   Missing: {monitoring_results['targets_missing']}")
        
        if monitoring_results['alerts_generated'] > 0:
            self._generate_alert("MISSING_RESOURCES", monitoring_results)
        
        return True
    
    def check_alerts(self):
        """Check for active alerts"""
        print("\n🚨 CHECKING SENTINEL ALERTS")
        print("=" * 60)
        
        if not self.alerts_file.exists():
            print("✅ No alerts active")
            return []
        
        with open(self.alerts_file, 'r') as f:
            alerts_data = json.load(f)
        
        active_alerts = [a for a in alerts_data.get('alerts', []) if a['status'] == 'active']
        
        if len(active_alerts) == 0:
            print("✅ No active alerts")
            return []
        
        print(f"⚠️  {len(active_alerts)} active alert(s):\n")
        
        for alert in active_alerts:
            severity_icon = {"critical": "🔴", "warning": "⚠️", "info": "ℹ️"}.get(alert['severity'], "•")
            print(f"{severity_icon} [{alert['severity'].upper()}] {alert['type']}")
            print(f"   Timestamp: {alert['timestamp']}")
            print(f"   Message: {alert['message']}")
            print()
        
        return active_alerts
    
    def _generate_alert(self, alert_type, data):
        """Generate alert and save to alerts file"""
        alert = {
            "type": alert_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "severity": self._determine_severity(alert_type, data),
            "message": self._format_alert_message(alert_type, data),
            "status": "active",
            "data": data
        }
        
        # Load existing alerts
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r') as f:
                alerts_data = json.load(f)
        else:
            alerts_data = {"alerts": []}
        
        alerts_data["alerts"].append(alert)
        alerts_data["last_updated"] = datetime.utcnow().isoformat() + "Z"
        
        # Save alerts
        self.sentinels_dir.mkdir(parents=True, exist_ok=True)
        with open(self.alerts_file, 'w') as f:
            json.dump(alerts_data, f, indent=2)
        
        print(f"\n🚨 ALERT GENERATED: {alert_type}")
        print(f"   Severity: {alert['severity']}")
        print(f"   {alert['message']}")
    
    def _determine_severity(self, alert_type, data):
        """Determine alert severity"""
        if alert_type == "MISSING_RESOURCES":
            missing_count = data.get("targets_missing", 0)
            if missing_count >= 3:
                return "critical"
            elif missing_count >= 1:
                return "warning"
        return "info"
    
    def _format_alert_message(self, alert_type, data):
        """Format alert message"""
        if alert_type == "MISSING_RESOURCES":
            return f"{data['targets_missing']} critical resources missing from monitoring targets"
        return f"Alert: {alert_type}"
    
    def show_status(self):
        """Show comprehensive sentinel swarm status"""
        print("\n" + "=" * 60)
        print("🛡️ SENTINEL SWARM STATUS")
        print("=" * 60)
        
        # Registry status
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                registry = json.load(f)
            
            print(f"\n📋 Registry:")
            print(f"   Deployment Status: {registry.get('deployment_status', 'unknown')}")
            print(f"   Last Updated: {registry.get('last_updated', 'unknown')}")
            
            print(f"\n🐝 Swarm Composition:")
            for component_type, components in registry['swarm'].items():
                active_count = sum(1 for c in components if c.get('status') == 'active')
                print(f"   {component_type.capitalize()}: {active_count}/{len(components)} active")
        else:
            print("\n⚠️  Registry not found")
        
        # Configuration status
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            print(f"\n⚙️ Operations:")
            for op_name, op_config in config['operations'].items():
                if op_name == 'alerts':
                    continue
                status = "✅ Enabled" if op_config.get('enabled') else "❌ Disabled"
                print(f"   {op_name.replace('_', ' ').title()}: {status}")
        
        # Recent monitoring
        monitoring_file = self.sentinels_dir / "monitoring_results.json"
        if monitoring_file.exists():
            with open(monitoring_file, 'r') as f:
                monitoring = json.load(f)
            
            print(f"\n👁️ Last Monitoring Sweep:")
            print(f"   Timestamp: {monitoring['sweep_timestamp']}")
            print(f"   Healthy: {monitoring['targets_healthy']}/{monitoring['targets_checked']}")
            if monitoring['targets_missing'] > 0:
                print(f"   ⚠️  Missing: {monitoring['targets_missing']}")
        
        # Active alerts
        active_alerts = []
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r') as f:
                alerts_data = json.load(f)
            active_alerts = [a for a in alerts_data.get('alerts', []) if a['status'] == 'active']
        
        print(f"\n🚨 Alerts: {len(active_alerts)} active")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Sentinel Swarm Coordinator")
    parser.add_argument("--deploy", action="store_true",
                       help="Deploy sentinel swarm")
    parser.add_argument("--monitor", action="store_true",
                       help="Run monitoring sweep")
    parser.add_argument("--alert-check", action="store_true",
                       help="Check for active alerts")
    parser.add_argument("--status", action="store_true",
                       help="Show swarm status")
    
    args = parser.parse_args()
    
    coordinator = SentinelSwarmCoordinator()
    
    if args.deploy:
        coordinator.deploy_swarm()
    
    if args.monitor:
        coordinator.monitor_resources()
    
    if args.alert_check:
        coordinator.check_alerts()
    
    if args.status:
        coordinator.show_status()
    
    if not any([args.deploy, args.monitor, args.alert_check, args.status]):
        parser.print_help()


if __name__ == "__main__":
    main()
