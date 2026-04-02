"""
THE HIVE MASTER WORKER
Jurisdiction: V41_Hive_Master
Primary Task: Coordinating the Co-pilot agents and Hugging Face syncs

This worker manages synchronization with Hugging Face spaces and coordinates
the deployment of co-pilot agents across the ARK_CORE ecosystem.
"""

import os
import sys
import json
import datetime
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent
WORKER_STATUS_PATH = REPO_ROOT / "worker_status.json"


class HiveMasterWorker:
    """The Hive Master - Coordinating Co-pilot agents and HuggingFace syncs"""
    
    def __init__(self):
        self.worker_id = "hive_master"
        self.syncs_completed = 0
        self.errors = []
        self.hf_token = os.environ.get("HF_TOKEN")
    
    def check_hf_token(self) -> bool:
        """Check if HuggingFace token is available"""
        if not self.hf_token:
            self.errors.append("HF_TOKEN not set in environment")
            print("⚠️  HF_TOKEN not found - Hive Master will run in limited mode")
            return False
        return True
    
    def sync_to_huggingface(self, space_id: str = "DJ-Goana-Coding/mapping-and-inventory") -> bool:
        """
        Sync repository to HuggingFace Space
        
        Args:
            space_id: HuggingFace space ID
        
        Returns:
            True if successful, False otherwise
        """
        print(f"🤗 Syncing to HuggingFace Space: {space_id}")
        
        if not self.check_hf_token():
            print("   Skipping HuggingFace sync (no token)")
            return False
        
        try:
            # Check if huggingface_hub is installed
            try:
                from huggingface_hub import HfApi
            except ImportError:
                self.errors.append("huggingface_hub not installed")
                print("❌ huggingface_hub not installed - run: pip install huggingface_hub")
                return False
            
            # Initialize HuggingFace API
            api = HfApi(token=self.hf_token)
            
            # Get repository info
            try:
                space_info = api.space_info(space_id)
                print(f"   Connected to space: {space_info.id}")
            except Exception as e:
                self.errors.append(f"Failed to connect to HF space: {e}")
                print(f"❌ Failed to connect to HuggingFace space: {e}")
                return False
            
            # Upload key files to HuggingFace
            files_to_sync = [
                "app.py",
                "requirements.txt",
                "Dockerfile",
                "README.md",
                "master_inventory.json",
                "worker_status.json",
                "system_manifest.json",
            ]
            
            synced_files = []
            for file_name in files_to_sync:
                file_path = REPO_ROOT / file_name
                if file_path.exists():
                    try:
                        api.upload_file(
                            path_or_fileobj=str(file_path),
                            path_in_repo=file_name,
                            repo_id=space_id,
                            repo_type="space",
                            token=self.hf_token,
                        )
                        synced_files.append(file_name)
                        print(f"   ✅ Uploaded: {file_name}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to upload {file_name}: {e}")
                else:
                    print(f"   ⚠️  File not found: {file_name}")
            
            # Upload services directory
            services_dir = REPO_ROOT / "services"
            if services_dir.exists():
                for service_file in services_dir.glob("*.py"):
                    try:
                        api.upload_file(
                            path_or_fileobj=str(service_file),
                            path_in_repo=f"services/{service_file.name}",
                            repo_id=space_id,
                            repo_type="space",
                            token=self.hf_token,
                        )
                        synced_files.append(f"services/{service_file.name}")
                        print(f"   ✅ Uploaded: services/{service_file.name}")
                    except Exception as e:
                        print(f"   ⚠️  Failed to upload services/{service_file.name}: {e}")
            
            self.syncs_completed += 1
            print(f"✅ HuggingFace sync complete - {len(synced_files)} files uploaded")
            return True
            
        except Exception as e:
            error_msg = f"HuggingFace sync failed: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return False
    
    def coordinate_copilot_agents(self) -> Dict[str, str]:
        """
        Coordinate Co-pilot agents across the system
        
        Returns:
            Dictionary of agent statuses
        """
        print("🤖 Coordinating Co-pilot agents...")
        
        agents = {
            "librarian": "ACTIVE",
            "mapper": "ACTIVE",
            "tia_oracle": "ACTIVE",
            "dataset_connector": "ACTIVE",
        }
        
        # Check if key services are available
        services_dir = REPO_ROOT / "services"
        
        service_files = {
            "repo_mapper.py": "mapper",
            "dataset_connector.py": "dataset_connector",
            "tia_connector.py": "tia_oracle",
            "gdrive_connector.py": "librarian",
        }
        
        for service_file, agent_name in service_files.items():
            service_path = services_dir / service_file
            if not service_path.exists():
                agents[agent_name] = "MISSING"
                print(f"   ⚠️  {agent_name}: MISSING ({service_file})")
            else:
                print(f"   ✅ {agent_name}: ACTIVE")
        
        return agents
    
    def check_github_sync_status(self) -> Dict[str, str]:
        """
        Check GitHub synchronization status
        
        Returns:
            Dictionary with sync status information
        """
        print("🐙 Checking GitHub sync status...")
        
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            current_branch = result.stdout.strip()
            
            # Check if there are uncommitted changes
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            has_changes = bool(result.stdout.strip())
            
            # Get last commit info
            result = subprocess.run(
                ["git", "log", "-1", "--oneline"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
            last_commit = result.stdout.strip()
            
            status = {
                "branch": current_branch,
                "has_uncommitted_changes": has_changes,
                "last_commit": last_commit,
                "status": "SYNCED" if not has_changes else "CHANGES_PENDING"
            }
            
            print(f"   Branch: {current_branch}")
            print(f"   Last commit: {last_commit}")
            print(f"   Status: {status['status']}")
            
            return status
            
        except Exception as e:
            error_msg = f"Failed to check GitHub status: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return {"status": "ERROR", "error": str(e)}
    
    def run(self, sync_to_hf: bool = True):
        """
        Run the Hive Master worker
        
        Args:
            sync_to_hf: Whether to sync to HuggingFace
        """
        print("🐝 THE HIVE MASTER WORKER — Starting...")
        print("=" * 60)
        
        start_time = datetime.datetime.utcnow()
        
        # Coordinate Co-pilot agents
        agent_status = self.coordinate_copilot_agents()
        
        # Check GitHub sync status
        github_status = self.check_github_sync_status()
        
        # Sync to HuggingFace if requested
        hf_synced = False
        if sync_to_hf:
            hf_synced = self.sync_to_huggingface()
        else:
            print("⏭️  Skipping HuggingFace sync (disabled)")
        
        # Update worker status
        self._update_worker_status(start_time, {
            "agents": agent_status,
            "github": github_status,
            "hf_synced": hf_synced,
        })
        
        # Print summary
        print("=" * 60)
        print(f"✅ THE HIVE MASTER WORKER — Complete")
        print(f"   Active Agents: {sum(1 for s in agent_status.values() if s == 'ACTIVE')}/{len(agent_status)}")
        print(f"   GitHub Status: {github_status.get('status', 'UNKNOWN')}")
        print(f"   HuggingFace Sync: {'✅' if hf_synced else '❌'}")
        print(f"   Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:10]:
                print(f"   - {error}")
    
    def _update_worker_status(self, start_time: datetime.datetime, results: Dict):
        """Update worker_status.json with run results"""
        try:
            if WORKER_STATUS_PATH.exists():
                with open(WORKER_STATUS_PATH, 'r') as f:
                    status = json.load(f)
            else:
                status = {"workers": {}}
            
            end_time = datetime.datetime.utcnow()
            success = len(self.errors) == 0
            
            if "hive_master" not in status["workers"]:
                status["workers"]["hive_master"] = {}
            
            status["workers"]["hive_master"].update({
                "status": "OPERATIONAL" if success else "ERROR",
                "last_run": end_time.isoformat(),
                "last_success": end_time.isoformat() if success else status["workers"]["hive_master"].get("last_success"),
                "total_runs": status["workers"]["hive_master"].get("total_runs", 0) + 1,
                "total_syncs": status["workers"]["hive_master"].get("total_syncs", 0) + self.syncs_completed,
                "agent_status": results.get("agents", {}),
                "github_status": results.get("github", {}),
                "errors": self.errors[-10:] if self.errors else []
            })
            
            status["last_updated"] = end_time.isoformat()
            
            # Update sync_status section
            if "sync_status" not in status:
                status["sync_status"] = {}
            
            if results.get("hf_synced"):
                status["sync_status"]["hf_last_push"] = end_time.isoformat()
            
            with open(WORKER_STATUS_PATH, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to update worker_status.json: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="The Hive Master Worker - Co-pilot coordination and HF syncs")
    parser.add_argument("--no-hf-sync", action="store_true", help="Skip HuggingFace sync")
    
    args = parser.parse_args()
    
    worker = HiveMasterWorker()
    worker.run(sync_to_hf=not args.no_hf_sync)


if __name__ == "__main__":
    main()
