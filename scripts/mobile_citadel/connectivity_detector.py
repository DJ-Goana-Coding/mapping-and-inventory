#!/usr/bin/env python3
"""
🌐 CONNECTIVITY DETECTOR
Mobile Citadel Command Center - Network State Monitor

Detects and manages online/offline states for vehicle-based operations.
Supports multiple connectivity tiers: Starlink, 4G/5G, WiFi mesh.
"""

import os
import sys
import json
import socket
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class ConnectivityDetector:
    """Detects and manages connectivity state for mobile operations"""
    
    def __init__(self, state_file: str = "/tmp/connectivity_state.json"):
        self.state_file = Path(state_file)
        self.connectivity_tiers = {
            "starlink": {"priority": 1, "test_hosts": ["8.8.8.8", "1.1.1.1"]},
            "cellular": {"priority": 2, "test_hosts": ["8.8.8.8", "1.1.1.1"]},
            "wifi": {"priority": 3, "test_hosts": ["192.168.1.1", "8.8.8.8"]},
            "mesh": {"priority": 4, "test_hosts": ["192.168.100.1"]}
        }
        
    def check_internet_connectivity(self, timeout: int = 3) -> Tuple[bool, Optional[str]]:
        """
        Check internet connectivity by attempting to reach known hosts.
        Returns (is_online, connection_type)
        """
        for tier_name, tier_config in sorted(
            self.connectivity_tiers.items(), 
            key=lambda x: x[1]["priority"]
        ):
            for host in tier_config["test_hosts"]:
                try:
                    # Try to establish socket connection
                    socket.create_connection((host, 80), timeout=timeout)
                    return True, tier_name
                except (socket.timeout, socket.error, OSError):
                    continue
        
        return False, None
    
    def check_github_connectivity(self) -> bool:
        """Check if GitHub API is reachable"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "https://api.github.com", "--max-time", "5"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() == "200"
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return False
    
    def check_huggingface_connectivity(self) -> bool:
        """Check if HuggingFace is reachable"""
        try:
            result = subprocess.run(
                ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", 
                 "https://huggingface.co", "--max-time", "5"],
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.stdout.strip() == "200"
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            return False
    
    def get_bandwidth_estimate(self) -> Optional[float]:
        """Estimate available bandwidth (simplified check)"""
        try:
            # Simple ping test to estimate latency
            result = subprocess.run(
                ["ping", "-c", "3", "8.8.8.8"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "avg" in result.stdout:
                # Extract average ping time
                for line in result.stdout.split("\n"):
                    if "avg" in line or "min/avg/max" in line:
                        parts = line.split("=")
                        if len(parts) > 1:
                            avg = parts[1].split("/")[1].strip()
                            return float(avg)
        except (subprocess.SubprocessError, subprocess.TimeoutExpired, ValueError):
            pass
        return None
    
    def get_connectivity_state(self) -> Dict:
        """Get comprehensive connectivity state"""
        is_online, connection_type = self.check_internet_connectivity()
        
        state = {
            "timestamp": datetime.utcnow().isoformat(),
            "is_online": is_online,
            "connection_type": connection_type,
            "services": {
                "github": False,
                "huggingface": False
            },
            "bandwidth": {
                "latency_ms": None,
                "quality": "unknown"
            },
            "recommended_actions": []
        }
        
        if is_online:
            # Check specific services
            state["services"]["github"] = self.check_github_connectivity()
            state["services"]["huggingface"] = self.check_huggingface_connectivity()
            
            # Estimate bandwidth
            latency = self.get_bandwidth_estimate()
            if latency:
                state["bandwidth"]["latency_ms"] = latency
                if latency < 50:
                    state["bandwidth"]["quality"] = "excellent"
                    state["recommended_actions"].append("Full sync recommended")
                elif latency < 150:
                    state["bandwidth"]["quality"] = "good"
                    state["recommended_actions"].append("Normal sync operations OK")
                elif latency < 300:
                    state["bandwidth"]["quality"] = "moderate"
                    state["recommended_actions"].append("Prioritize critical updates only")
                else:
                    state["bandwidth"]["quality"] = "poor"
                    state["recommended_actions"].append("Queue operations for later")
        else:
            state["recommended_actions"].append("Offline mode - queue all operations")
        
        return state
    
    def save_state(self, state: Dict):
        """Save connectivity state to file"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self) -> Optional[Dict]:
        """Load last known connectivity state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return None
    
    def monitor_and_report(self) -> Dict:
        """Monitor connectivity and return comprehensive report"""
        current_state = self.get_connectivity_state()
        previous_state = self.load_state()
        
        # Detect state transitions
        if previous_state:
            if previous_state.get("is_online") != current_state["is_online"]:
                if current_state["is_online"]:
                    current_state["state_change"] = "OFFLINE_TO_ONLINE"
                    current_state["recommended_actions"].insert(0, 
                        "🟢 ONLINE - Execute sync queue")
                else:
                    current_state["state_change"] = "ONLINE_TO_OFFLINE"
                    current_state["recommended_actions"].insert(0, 
                        "🔴 OFFLINE - Queue mode activated")
            else:
                current_state["state_change"] = "NO_CHANGE"
        else:
            current_state["state_change"] = "INITIAL_CHECK"
        
        # Save current state
        self.save_state(current_state)
        
        return current_state


def main():
    """Main execution - check connectivity and report"""
    detector = ConnectivityDetector()
    state = detector.monitor_and_report()
    
    # Print report
    print("=" * 60)
    print("🌐 MOBILE CITADEL CONNECTIVITY REPORT")
    print("=" * 60)
    print(f"Timestamp: {state['timestamp']}")
    print(f"Status: {'🟢 ONLINE' if state['is_online'] else '🔴 OFFLINE'}")
    
    if state['is_online']:
        print(f"Connection: {state['connection_type'].upper()}")
        print(f"\nServices:")
        print(f"  GitHub: {'✅' if state['services']['github'] else '❌'}")
        print(f"  HuggingFace: {'✅' if state['services']['huggingface'] else '❌'}")
        
        if state['bandwidth']['latency_ms']:
            print(f"\nBandwidth:")
            print(f"  Latency: {state['bandwidth']['latency_ms']:.1f}ms")
            print(f"  Quality: {state['bandwidth']['quality'].upper()}")
    
    print(f"\nState Change: {state['state_change']}")
    
    if state['recommended_actions']:
        print(f"\nRecommended Actions:")
        for action in state['recommended_actions']:
            print(f"  • {action}")
    
    print("=" * 60)
    
    # Output JSON for script consumption
    json_output = {
        "is_online": state['is_online'],
        "connection_type": state.get('connection_type'),
        "github_available": state['services'].get('github', False),
        "hf_available": state['services'].get('huggingface', False),
        "bandwidth_quality": state['bandwidth'].get('quality', 'unknown'),
        "state_change": state['state_change']
    }
    
    output_file = Path("/tmp/connectivity_check.json")
    with open(output_file, 'w') as f:
        json.dump(json_output, f, indent=2)
    
    # Exit code: 0 if online, 1 if offline
    sys.exit(0 if state['is_online'] else 1)


if __name__ == "__main__":
    main()
