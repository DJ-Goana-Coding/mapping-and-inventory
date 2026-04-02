"""
THE BRIDGE WORKER
Jurisdiction: Trinity_Master_Cloud
Primary Task: Maintaining tunnels between the Oppo, S10, and Cloud

This worker monitors the connection status between all device nodes
(Oppo Librarian, S10 Field Uplink, Cloud GitHub, HuggingFace) and
ensures data flows correctly across the system.
"""

import os
import sys
import json
import datetime
import socket
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Repository root
REPO_ROOT = Path(__file__).parent.parent
WORKER_STATUS_PATH = REPO_ROOT / "worker_status.json"


class BridgeWorker:
    """The Bridge - Maintaining tunnels between nodes"""
    
    def __init__(self):
        self.worker_id = "bridge"
        self.tunnels_maintained = 0
        self.errors = []
        
        # Node endpoints
        self.nodes = {
            "oppo_librarian": {
                "name": "Oppo Librarian Node",
                "type": "device",
                "endpoint": None,  # Local device, no remote endpoint
                "status": "UNKNOWN"
            },
            "s10_uplink": {
                "name": "S10 Field Uplink",
                "type": "device",
                "endpoint": None,  # Local device, no remote endpoint
                "status": "UNKNOWN"
            },
            "github_titan": {
                "name": "GitHub Titan (Cloud Engine)",
                "type": "cloud",
                "endpoint": "github.com",
                "status": "UNKNOWN"
            },
            "huggingface_rack": {
                "name": "HuggingFace 1TB Rack",
                "type": "cloud",
                "endpoint": "huggingface.co",
                "status": "UNKNOWN"
            },
            "gdrive_vault": {
                "name": "Google Drive Vault",
                "type": "cloud",
                "endpoint": "drive.google.com",
                "status": "UNKNOWN"
            }
        }
    
    def check_network_connectivity(self, host: str, port: int = 443, timeout: int = 5) -> bool:
        """
        Check if a host is reachable via TCP
        
        Args:
            host: Hostname or IP address
            port: Port number (default: 443 for HTTPS)
            timeout: Connection timeout in seconds
        
        Returns:
            True if reachable, False otherwise
        """
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host, port))
            sock.close()
            return result == 0
        except Exception as e:
            return False
    
    def check_github_connection(self) -> Tuple[bool, str]:
        """
        Check GitHub connection status
        
        Returns:
            Tuple of (success, message)
        """
        print("🐙 Checking GitHub Titan connection...")
        
        # Check network connectivity
        if not self.check_network_connectivity("github.com"):
            return False, "Network unreachable"
        
        # Check git remote
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "github.com" in result.stdout:
                print("   ✅ GitHub remote configured")
                
                # Try to fetch (lightweight check)
                result = subprocess.run(
                    ["git", "ls-remote", "--heads", "origin"],
                    cwd=REPO_ROOT,
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                
                if result.returncode == 0:
                    return True, "Connected and authenticated"
                else:
                    return False, "Authentication failed"
            else:
                return False, "No GitHub remote configured"
                
        except subprocess.TimeoutExpired:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Error: {e}"
    
    def check_huggingface_connection(self) -> Tuple[bool, str]:
        """
        Check HuggingFace connection status
        
        Returns:
            Tuple of (success, message)
        """
        print("🤗 Checking HuggingFace Rack connection...")
        
        # Check network connectivity
        if not self.check_network_connectivity("huggingface.co"):
            return False, "Network unreachable"
        
        # Check HF token
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            return False, "HF_TOKEN not set"
        
        # Try to connect to HuggingFace API
        try:
            from huggingface_hub import HfApi
            api = HfApi(token=hf_token)
            
            # Try to get user info
            user_info = api.whoami()
            username = user_info.get("name", "Unknown")
            
            print(f"   ✅ Authenticated as: {username}")
            return True, f"Connected as {username}"
            
        except ImportError:
            return False, "huggingface_hub not installed"
        except Exception as e:
            return False, f"Authentication failed: {e}"
    
    def check_gdrive_connection(self) -> Tuple[bool, str]:
        """
        Check Google Drive connection status
        
        Returns:
            Tuple of (success, message)
        """
        print("☁️  Checking Google Drive Vault connection...")
        
        # Check network connectivity
        if not self.check_network_connectivity("drive.google.com"):
            return False, "Network unreachable"
        
        # Check rclone
        try:
            result = subprocess.run(
                ["which", "rclone"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return False, "rclone not installed"
            
            # Check if gdrive remote exists
            result = subprocess.run(
                ["rclone", "listremotes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "gdrive:" in result.stdout:
                print("   ✅ rclone gdrive remote configured")
                
                # Try a lightweight test (lsd with timeout)
                try:
                    result = subprocess.run(
                        ["rclone", "lsd", "gdrive:", "--max-depth", "1"],
                        capture_output=True,
                        text=True,
                        timeout=20
                    )
                    
                    if result.returncode == 0:
                        return True, "Connected and accessible"
                    else:
                        return False, "Connection test failed"
                except subprocess.TimeoutExpired:
                    return False, "Connection timeout"
            else:
                return False, "gdrive remote not configured"
                
        except Exception as e:
            return False, f"Error: {e}"
    
    def check_device_nodes(self) -> Dict[str, str]:
        """
        Check status of local device nodes (Oppo, S10)
        
        Returns:
            Dictionary with device statuses
        """
        print("📱 Checking device nodes...")
        
        statuses = {}
        
        # Check for device-specific indicators
        # In a real implementation, these would check actual device connectivity
        # For now, we check if the scripts exist
        
        # Oppo Librarian Node
        oppo_script = REPO_ROOT / "Partition_01" / "oppo_node.py"
        if oppo_script.exists():
            statuses["oppo_librarian"] = "SCRIPT_AVAILABLE"
            print("   ✅ Oppo Librarian: Script available")
        else:
            statuses["oppo_librarian"] = "SCRIPT_MISSING"
            print("   ⚠️  Oppo Librarian: Script missing")
        
        # S10 Field Uplink
        # Check if S10 cargo directory exists
        s10_dir = REPO_ROOT / "Research" / "S10"
        if s10_dir.exists():
            statuses["s10_uplink"] = "DIRECTORY_AVAILABLE"
            print("   ✅ S10 Uplink: Directory available")
        else:
            statuses["s10_uplink"] = "DIRECTORY_MISSING"
            print("   ⚠️  S10 Uplink: Directory missing")
        
        return statuses
    
    def monitor_tunnels(self) -> Dict[str, Dict]:
        """
        Monitor all tunnels/connections in the system
        
        Returns:
            Dictionary with status of all tunnels
        """
        print("🌉 Monitoring all tunnels...")
        print("=" * 60)
        
        tunnel_status = {}
        
        # Check GitHub
        success, message = self.check_github_connection()
        self.nodes["github_titan"]["status"] = "CONNECTED" if success else "DISCONNECTED"
        self.nodes["github_titan"]["message"] = message
        tunnel_status["github_titan"] = {
            "connected": success,
            "message": message
        }
        if success:
            self.tunnels_maintained += 1
        
        # Check HuggingFace
        success, message = self.check_huggingface_connection()
        self.nodes["huggingface_rack"]["status"] = "CONNECTED" if success else "DISCONNECTED"
        self.nodes["huggingface_rack"]["message"] = message
        tunnel_status["huggingface_rack"] = {
            "connected": success,
            "message": message
        }
        if success:
            self.tunnels_maintained += 1
        
        # Check Google Drive
        success, message = self.check_gdrive_connection()
        self.nodes["gdrive_vault"]["status"] = "CONNECTED" if success else "DISCONNECTED"
        self.nodes["gdrive_vault"]["message"] = message
        tunnel_status["gdrive_vault"] = {
            "connected": success,
            "message": message
        }
        if success:
            self.tunnels_maintained += 1
        
        # Check device nodes
        device_statuses = self.check_device_nodes()
        for device, status in device_statuses.items():
            self.nodes[device]["status"] = status
            tunnel_status[device] = {
                "status": status
            }
        
        return tunnel_status
    
    def run(self):
        """Run the Bridge worker"""
        print("🌉 THE BRIDGE WORKER — Starting...")
        print("=" * 60)
        
        start_time = datetime.datetime.utcnow()
        
        # Monitor all tunnels
        tunnel_status = self.monitor_tunnels()
        
        # Update worker status
        self._update_worker_status(start_time, tunnel_status)
        
        # Print summary
        print("=" * 60)
        print(f"✅ THE BRIDGE WORKER — Complete")
        print(f"   Active Tunnels: {self.tunnels_maintained}")
        print(f"   Total Nodes: {len(self.nodes)}")
        print(f"   Errors: {len(self.errors)}")
        
        print("\n🌉 Tunnel Status Summary:")
        for node_id, node_info in self.nodes.items():
            status = node_info["status"]
            icon = "✅" if "CONNECTED" in status or "AVAILABLE" in status else "❌"
            message = node_info.get("message", status)
            print(f"   {icon} {node_info['name']}: {message}")
        
        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:10]:
                print(f"   - {error}")
    
    def _update_worker_status(self, start_time: datetime.datetime, tunnel_status: Dict):
        """Update worker_status.json with run results"""
        try:
            if WORKER_STATUS_PATH.exists():
                with open(WORKER_STATUS_PATH, 'r') as f:
                    status = json.load(f)
            else:
                status = {"workers": {}}
            
            end_time = datetime.datetime.utcnow()
            success = len(self.errors) == 0
            
            if "bridge" not in status["workers"]:
                status["workers"]["bridge"] = {}
            
            status["workers"]["bridge"].update({
                "status": "OPERATIONAL" if success else "ERROR",
                "last_run": end_time.isoformat(),
                "last_success": end_time.isoformat() if success else status["workers"]["bridge"].get("last_success"),
                "total_runs": status["workers"]["bridge"].get("total_runs", 0) + 1,
                "total_tunnels_maintained": status["workers"]["bridge"].get("total_tunnels_maintained", 0) + self.tunnels_maintained,
                "tunnel_status": tunnel_status,
                "errors": self.errors[-10:] if self.errors else []
            })
            
            status["last_updated"] = end_time.isoformat()
            
            with open(WORKER_STATUS_PATH, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to update worker_status.json: {e}")


def main():
    """Main entry point"""
    worker = BridgeWorker()
    worker.run()


if __name__ == "__main__":
    main()
