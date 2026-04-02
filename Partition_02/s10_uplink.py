"""
ARK_CORE // PARTITION_02 // S10_UPLINK.PY
S10 Push/Pull Logic for Tactical Uplink
Handles sync between S10 device and GitHub/GDrive.
"""
import os
import subprocess
import json
from datetime import datetime


class S10Uplink:
    """S10 device uplink manager for cloud synchronization."""
    
    def __init__(self, device_id="S10_CITADEL"):
        """Initialize S10 uplink."""
        self.device_id = device_id
        self.local_intel_path = "./S10_CITADEL_OMEGA_INTEL"
        self.local_research_path = "./Research/S10"
        self.remote_intel = "gdrive:CITADEL_OMEGA_INTEL"
        self.remote_research = "gdrive:GENESIS_VAULT/S10_CARGO"
    
    def push_to_cloud(self, source_path=None, dry_run=True):
        """
        Push S10 data to GDrive.
        
        Args:
            source_path: Path to push (defaults to S10 intel directory)
            dry_run: If True, only simulate the push
        """
        if source_path is None:
            source_path = self.local_intel_path
        
        # Ensure local directory exists
        os.makedirs(source_path, exist_ok=True)
        
        # Determine remote target
        if "INTEL" in source_path:
            remote = self.remote_intel
        else:
            remote = self.remote_research
        
        cmd = ["rclone", "sync", source_path, remote, "--progress", "--stats-one-line"]
        if dry_run:
            cmd.append("--dry-run")
        
        print(f"🚀 S10 UPLINK: Pushing {source_path} → {remote}")
        if dry_run:
            print("   [DRY RUN MODE - No actual transfer]")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Push successful!")
                return {"status": "success", "output": result.stdout}
            else:
                print(f"❌ Push failed: {result.stderr}")
                return {"status": "error", "output": result.stderr}
        
        except subprocess.TimeoutExpired:
            print("⏱️ Push timed out after 5 minutes")
            return {"status": "timeout"}
        except FileNotFoundError:
            print("❌ rclone not found. Please install rclone.")
            return {"status": "error", "message": "rclone not installed"}
    
    def pull_from_cloud(self, target_path=None, dry_run=True):
        """
        Pull S10 data from GDrive.
        
        Args:
            target_path: Local path to pull to (defaults to S10 intel directory)
            dry_run: If True, only simulate the pull
        """
        if target_path is None:
            target_path = self.local_intel_path
        
        # Ensure local directory exists
        os.makedirs(target_path, exist_ok=True)
        
        # Determine remote source
        if "INTEL" in target_path:
            remote = self.remote_intel
        else:
            remote = self.remote_research
        
        cmd = ["rclone", "sync", remote, target_path, "--progress", "--stats-one-line"]
        if dry_run:
            cmd.append("--dry-run")
        
        print(f"📥 S10 UPLINK: Pulling {remote} → {target_path}")
        if dry_run:
            print("   [DRY RUN MODE - No actual transfer]")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print("✅ Pull successful!")
                return {"status": "success", "output": result.stdout}
            else:
                print(f"❌ Pull failed: {result.stderr}")
                return {"status": "error", "output": result.stderr}
        
        except subprocess.TimeoutExpired:
            print("⏱️ Pull timed out after 5 minutes")
            return {"status": "timeout"}
        except FileNotFoundError:
            print("❌ rclone not found. Please install rclone.")
            return {"status": "error", "message": "rclone not installed"}
    
    def sync_status(self):
        """Get sync status and statistics."""
        status = {
            "device_id": self.device_id,
            "timestamp": datetime.now().isoformat(),
            "local_paths": {
                "intel": self.local_intel_path,
                "research": self.local_research_path
            },
            "rclone_available": self._check_rclone()
        }
        
        # Check local directories
        for name, path in status["local_paths"].items():
            if os.path.exists(path):
                file_count = sum(len(files) for _, _, files in os.walk(path))
                status[f"{name}_files"] = file_count
            else:
                status[f"{name}_files"] = 0
        
        return status
    
    def _check_rclone(self):
        """Check if rclone is available."""
        try:
            subprocess.run(["rclone", "version"], capture_output=True, check=True)
            return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            return False


def main():
    """Main S10 uplink CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="S10 Tactical Uplink Manager")
    parser.add_argument("--push", action="store_true", help="Push S10 data to cloud")
    parser.add_argument("--pull", action="store_true", help="Pull S10 data from cloud")
    parser.add_argument("--status", action="store_true", help="Show sync status")
    parser.add_argument("--path", help="Custom path for push/pull")
    parser.add_argument("--live", action="store_true", help="Execute live (default is dry-run)")
    
    args = parser.parse_args()
    
    uplink = S10Uplink()
    dry_run = not args.live
    
    if args.status:
        status = uplink.sync_status()
        print("\n📡 S10 UPLINK STATUS")
        print(f"Device: {status['device_id']}")
        print(f"Timestamp: {status['timestamp']}")
        print(f"Rclone Available: {'✅' if status['rclone_available'] else '❌'}")
        print(f"\nLocal Files:")
        print(f"  Intel: {status.get('intel_files', 0)} files")
        print(f"  Research: {status.get('research_files', 0)} files")
    
    elif args.push:
        result = uplink.push_to_cloud(source_path=args.path, dry_run=dry_run)
        if result["status"] != "success":
            exit(1)
    
    elif args.pull:
        result = uplink.pull_from_cloud(target_path=args.path, dry_run=dry_run)
        if result["status"] != "success":
            exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
