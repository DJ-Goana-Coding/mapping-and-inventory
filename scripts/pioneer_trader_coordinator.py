#!/usr/bin/env python3
"""
PIONEER TRADER COORDINATOR
Coordinates tias-pioneer-trader operations
Manages trading, market monitoring, and pioneer exploration

Usage:
    python pioneer_trader_coordinator.py --deploy
    python pioneer_trader_coordinator.py --scan-markets
    python pioneer_trader_coordinator.py --explore
    python pioneer_trader_coordinator.py --status
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


class PioneerTraderCoordinator:
    """Coordinates pioneer-trader operations for market intelligence"""
    
    def __init__(self):
        self.pioneer_dir = Path("data/pioneer_trader")
        self.registry_file = self.pioneer_dir / "pioneer_trader_registry.json"
        self.config_file = self.pioneer_dir / "trading_operations_config.json"
        self.market_data_file = self.pioneer_dir / "market_data.json"
    
    def deploy_components(self):
        """Deploy pioneer-trader components"""
        print("\n🚀 DEPLOYING PIONEER TRADER COMPONENTS")
        print("=" * 60)
        
        if not self.registry_file.exists():
            print("❌ Pioneer trader registry not found")
            print("   Run pioneer_trader_integration.yml workflow first")
            return False
        
        with open(self.registry_file, 'r') as f:
            registry = json.load(f)
        
        print("Deploying components:")
        for comp_type, components in registry["components"].items():
            if len(components) > 0:
                print(f"  📊 {comp_type.replace('_', ' ').title()}: {len(components)}")
                
                # Mark as active
                for component in components:
                    component['status'] = 'active'
                    component['last_activation'] = datetime.utcnow().isoformat() + "Z"
        
        registry['deployment_status'] = 'active'
        registry['last_updated'] = datetime.utcnow().isoformat() + "Z"
        
        with open(self.registry_file, 'w') as f:
            json.dump(registry, f, indent=2)
        
        print(f"\n✅ {registry['total_components']} components deployed")
        return True
    
    def scan_markets(self):
        """Scan markets for opportunities"""
        print("\n📊 SCANNING MARKETS")
        print("=" * 60)
        
        if not self.config_file.exists():
            print("❌ Trading operations config not found")
            return False
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        market_config = config['operations']['market_monitoring']
        
        if not market_config['enabled']:
            print("⚠️  Market monitoring is disabled")
            return False
        
        print("Scanning markets:")
        for market in market_config['markets']:
            print(f"  📈 {market.upper()}")
        
        # Create market scan result
        scan_result = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "markets_scanned": market_config['markets'],
            "opportunities": [],
            "alerts": [],
            "status": "completed"
        }
        
        # Simulated market data (replace with actual API calls)
        for market in market_config['markets']:
            scan_result["opportunities"].append({
                "market": market,
                "type": "trend_analysis",
                "confidence": "moderate",
                "description": f"Market scan completed for {market}"
            })
        
        # Save scan results
        self.pioneer_dir.mkdir(parents=True, exist_ok=True)
        scan_file = self.pioneer_dir / f"market_scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(scan_file, 'w') as f:
            json.dump(scan_result, f, indent=2)
        
        print(f"\n✅ Market scan completed")
        print(f"   Markets: {len(market_config['markets'])}")
        print(f"   Opportunities: {len(scan_result['opportunities'])}")
        print(f"   Results: {scan_file.name}")
        
        return True
    
    def pioneer_exploration(self):
        """Run pioneer exploration for new opportunities"""
        print("\n🔍 PIONEER EXPLORATION")
        print("=" * 60)
        
        if not self.config_file.exists():
            print("❌ Trading operations config not found")
            return False
        
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        pioneer_config = config['operations']['pioneer_exploration']
        
        if not pioneer_config['enabled']:
            print("⚠️  Pioneer exploration is disabled")
            return False
        
        print("Exploration targets:")
        for target in pioneer_config['targets']:
            print(f"  🚀 {target.replace('_', ' ').title()}")
        
        # Create exploration result
        exploration_result = {
            "exploration_timestamp": datetime.utcnow().isoformat() + "Z",
            "targets_explored": pioneer_config['targets'],
            "discoveries": [],
            "status": "completed"
        }
        
        # Simulated discoveries (replace with actual exploration logic)
        for target in pioneer_config['targets']:
            exploration_result["discoveries"].append({
                "target": target,
                "type": "opportunity",
                "status": "identified",
                "description": f"Exploration completed for {target.replace('_', ' ')}"
            })
        
        # Save exploration results
        exploration_file = self.pioneer_dir / f"exploration_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(exploration_file, 'w') as f:
            json.dump(exploration_result, f, indent=2)
        
        print(f"\n✅ Pioneer exploration completed")
        print(f"   Targets: {len(pioneer_config['targets'])}")
        print(f"   Discoveries: {len(exploration_result['discoveries'])}")
        print(f"   Results: {exploration_file.name}")
        
        return True
    
    def show_status(self):
        """Show comprehensive pioneer-trader status"""
        print("\n" + "=" * 60)
        print("🚀 PIONEER TRADER STATUS")
        print("=" * 60)
        
        # Registry status
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                registry = json.load(f)
            
            print(f"\n📋 Registry:")
            print(f"   Total Components: {registry.get('total_components', 0)}")
            print(f"   Deployment Status: {registry.get('deployment_status', 'unknown')}")
            print(f"   Last Updated: {registry.get('last_updated', 'unknown')}")
            
            print(f"\n📊 Component Breakdown:")
            for comp_type, components in registry['components'].items():
                if len(components) > 0:
                    active_count = sum(1 for c in components if c.get('status') == 'active')
                    print(f"   {comp_type.replace('_', ' ').title()}: {active_count}/{len(components)} active")
        else:
            print("\n⚠️  Registry not found")
        
        # Configuration status
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = json.load(f)
            
            print(f"\n⚙️ Operations:")
            for op_name, op_config in config['operations'].items():
                if isinstance(op_config, dict) and 'enabled' in op_config:
                    status = "✅ Enabled" if op_config.get('enabled') else "❌ Disabled"
                    print(f"   {op_name.replace('_', ' ').title()}: {status}")
            
            # Safety settings
            trading_config = config['operations'].get('trading', {})
            print(f"\n🛡️ Safety Settings:")
            print(f"   Mode: {trading_config.get('mode', 'unknown')}")
            print(f"   Risk Level: {trading_config.get('risk_level', 'unknown')}")
            print(f"   Auto-Execute: {'❌ Disabled' if not trading_config.get('auto_execute') else '⚠️ Enabled'}")
        
        # Recent scans
        if self.pioneer_dir.exists():
            scan_files = list(self.pioneer_dir.glob("market_scan_*.json"))
            exploration_files = list(self.pioneer_dir.glob("exploration_*.json"))
            
            print(f"\n📈 Activity:")
            print(f"   Market Scans: {len(scan_files)}")
            print(f"   Explorations: {len(exploration_files)}")
            
            if scan_files:
                latest_scan = max(scan_files, key=lambda p: p.stat().st_mtime)
                print(f"   Latest Scan: {latest_scan.name}")
            
            if exploration_files:
                latest_exploration = max(exploration_files, key=lambda p: p.stat().st_mtime)
                print(f"   Latest Exploration: {latest_exploration.name}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Pioneer Trader Coordinator")
    parser.add_argument("--deploy", action="store_true",
                       help="Deploy pioneer-trader components")
    parser.add_argument("--scan-markets", action="store_true",
                       help="Scan markets for opportunities")
    parser.add_argument("--explore", action="store_true",
                       help="Run pioneer exploration")
    parser.add_argument("--status", action="store_true",
                       help="Show coordinator status")
    
    args = parser.parse_args()
    
    coordinator = PioneerTraderCoordinator()
    
    if args.deploy:
        coordinator.deploy_components()
    
    if args.scan_markets:
        coordinator.scan_markets()
    
    if args.explore:
        coordinator.pioneer_exploration()
    
    if args.status:
        coordinator.show_status()
    
    if not any([args.deploy, args.scan_markets, args.explore, args.status]):
        parser.print_help()


if __name__ == "__main__":
    main()
