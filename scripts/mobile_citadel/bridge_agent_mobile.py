#!/usr/bin/env python3
"""
📱 BRIDGE AGENT MOBILE
Mobile Citadel Command Center - Enhanced Bridge Agent for Vehicle Operations

Enhanced Bridge Agent with offline queue management, sync prioritization,
local metadata generation, and power/storage monitoring for mobile nodes.
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Import mobile citadel components
import sys
sys.path.insert(0, str(Path(__file__).parent))
from connectivity_detector import ConnectivityDetector
from sync_queue_manager import SyncQueueManager, SyncOperation, SyncPriority
from vehicle_storage_manager import VehicleStorageManager


class BridgeAgentMobile:
    """Enhanced Bridge Agent for mobile/vehicle operations"""
    
    def __init__(self, node_name: str = "oppo-bridge"):
        self.node_name = node_name
        self.connectivity = ConnectivityDetector()
        self.sync_queue = SyncQueueManager()
        self.storage = VehicleStorageManager(
            base_path=os.environ.get("VEHICLE_STORAGE_PATH", "/tmp/vehicle-storage")
        )
        self.state_file = Path("/tmp/mobile_bridge_state.json")
        
    def check_system_status(self) -> Dict:
        """Comprehensive system status check"""
        status = {
            "timestamp": datetime.utcnow().isoformat(),
            "node_name": self.node_name,
            "connectivity": {},
            "sync_queue": {},
            "storage": {},
            "power": {},
            "mode": "unknown"
        }
        
        # Connectivity status
        conn_state = self.connectivity.get_connectivity_state()
        status["connectivity"] = {
            "is_online": conn_state["is_online"],
            "connection_type": conn_state.get("connection_type"),
            "github_available": conn_state["services"].get("github", False),
            "hf_available": conn_state["services"].get("huggingface", False),
            "bandwidth_quality": conn_state["bandwidth"].get("quality", "unknown")
        }
        
        # Sync queue status
        queue_stats = self.sync_queue.get_queue_stats()
        status["sync_queue"] = {
            "queued": queue_stats["total_queued"],
            "in_progress": queue_stats["in_progress"],
            "failed": queue_stats["failed"]
        }
        
        # Storage status
        storage_health = self.storage.check_storage_health()
        status["storage"] = {
            "status": storage_health["status"],
            "warnings": storage_health.get("warnings", []),
            "disk_space_gb": storage_health.get("disk_space", {}).get("free_gb", 0)
        }
        
        # Determine operating mode
        if status["connectivity"]["is_online"]:
            if status["sync_queue"]["queued"] > 0:
                status["mode"] = "ONLINE_SYNCING"
            else:
                status["mode"] = "ONLINE_READY"
        else:
            status["mode"] = "OFFLINE_QUEUE"
        
        return status
    
    def execute_sync_window(self, max_operations: int = 20, max_size_mb: float = 200.0):
        """Execute a sync window when connectivity is available"""
        print("=" * 60)
        print("🔄 EXECUTING SYNC WINDOW")
        print("=" * 60)
        
        # Check connectivity first
        conn_state = self.connectivity.monitor_and_report()
        if not conn_state["is_online"]:
            print("❌ Cannot sync - currently offline")
            return
        
        print(f"✅ Online via {conn_state['connection_type']}")
        print(f"   Bandwidth: {conn_state['bandwidth']['quality']}")
        
        # Adjust batch size based on bandwidth
        if conn_state['bandwidth']['quality'] == 'poor':
            max_operations = min(5, max_operations)
            max_size_mb = min(50, max_size_mb)
            print(f"   ⚠️  Reduced batch size due to poor bandwidth")
        
        # Get next batch
        batch = self.sync_queue.get_next_batch(
            max_operations=max_operations,
            max_size_mb=max_size_mb
        )
        
        if not batch:
            print("\n✅ Sync queue is empty")
            return
        
        print(f"\n📦 Processing {len(batch)} operations...")
        
        for op in batch:
            print(f"\n  Processing: [{op.priority}] {op.operation}")
            if op.repo:
                print(f"    Repo: {op.repo}")
            
            # Mark as in progress
            self.sync_queue.update_status(op.id, "in_progress")
            
            # Execute operation (simplified - would call actual sync logic)
            success = self._execute_operation(op)
            
            if success:
                self.sync_queue.mark_completed(op.id)
                print(f"    ✅ Completed")
            else:
                self.sync_queue.mark_failed(op.id, "Execution failed")
                print(f"    ❌ Failed")
        
        # Cleanup completed
        self.sync_queue.clear_completed()
        
        print("\n" + "=" * 60)
        print("✅ Sync window completed")
    
    def _execute_operation(self, op) -> bool:
        """Execute a single sync operation (placeholder)"""
        # This would contain actual git/hf/gdrive sync logic
        # For now, just simulate success
        return True
    
    def queue_commit(self, repo: str, branch: str, files: List[str], message: str):
        """Queue a commit for later push"""
        self.sync_queue.add_operation(
            operation=SyncOperation.GIT_PUSH,
            priority=SyncPriority.HIGH,
            repo=repo,
            branch=branch,
            files=files,
            metadata={"commit_message": message}
        )
        print(f"✅ Commit queued: {repo}/{branch}")
    
    def generate_daily_report(self) -> str:
        """Generate daily status report"""
        status = self.check_system_status()
        
        report = []
        report.append("=" * 60)
        report.append(f"📱 BRIDGE AGENT MOBILE REPORT - {self.node_name}")
        report.append("=" * 60)
        report.append(f"Timestamp: {status['timestamp']}")
        report.append(f"Mode: {status['mode']}")
        
        report.append(f"\n🌐 Connectivity:")
        report.append(f"  Status: {'🟢 ONLINE' if status['connectivity']['is_online'] else '🔴 OFFLINE'}")
        if status['connectivity']['is_online']:
            report.append(f"  Connection: {status['connectivity']['connection_type']}")
            report.append(f"  GitHub: {'✅' if status['connectivity']['github_available'] else '❌'}")
            report.append(f"  HuggingFace: {'✅' if status['connectivity']['hf_available'] else '❌'}")
            report.append(f"  Bandwidth: {status['connectivity']['bandwidth_quality']}")
        
        report.append(f"\n📦 Sync Queue:")
        report.append(f"  Queued: {status['sync_queue']['queued']}")
        report.append(f"  In Progress: {status['sync_queue']['in_progress']}")
        report.append(f"  Failed: {status['sync_queue']['failed']}")
        
        report.append(f"\n💾 Storage:")
        report.append(f"  Status: {status['storage']['status']}")
        report.append(f"  Free Space: {status['storage']['disk_space_gb']:.1f} GB")
        if status['storage']['warnings']:
            report.append(f"  Warnings:")
            for warning in status['storage']['warnings']:
                report.append(f"    ⚠️  {warning}")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def run_daily_routine(self):
        """Execute daily mobile citadel routine"""
        print("\n🌅 MOBILE CITADEL DAILY ROUTINE")
        print("=" * 60)
        
        # 1. Check connectivity
        print("\n1️⃣  Checking connectivity...")
        conn_state = self.connectivity.monitor_and_report()
        
        # 2. Generate storage report
        print("\n2️⃣  Generating storage report...")
        storage_report = self.storage.get_storage_report()
        print(storage_report)
        
        # 3. Check sync queue
        print("\n3️⃣  Checking sync queue...")
        queue_report = self.sync_queue.generate_sync_report()
        print(queue_report)
        
        # 4. Execute sync if online
        if conn_state["is_online"]:
            print("\n4️⃣  Executing sync window...")
            self.execute_sync_window()
        else:
            print("\n4️⃣  Offline - sync window skipped")
        
        # 5. Generate final report
        print("\n5️⃣  Final status report...")
        print(self.generate_daily_report())
        
        print("\n✅ Daily routine completed\n")


def main():
    """Main execution"""
    import sys
    
    node_name = os.environ.get("BRIDGE_NODE_NAME", "oppo-bridge")
    bridge = BridgeAgentMobile(node_name=node_name)
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "status":
            status = bridge.check_system_status()
            print(json.dumps(status, indent=2))
        
        elif command == "sync":
            bridge.execute_sync_window()
        
        elif command == "daily":
            bridge.run_daily_routine()
        
        elif command == "report":
            print(bridge.generate_daily_report())
        
        else:
            print(f"Unknown command: {command}")
            print("\nUsage: bridge_agent_mobile.py [status|sync|daily|report]")
    else:
        # Default: run daily routine
        bridge.run_daily_routine()


if __name__ == "__main__":
    main()
