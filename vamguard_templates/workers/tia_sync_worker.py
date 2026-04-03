#!/usr/bin/env python3
"""
🚀 TIA SYNC WORKER
Worker: Sync TIA code to DJ-Goanna-Coding/TIA-ARCHITECT-CORE

Role: Push discovered TIA code to TIA-ARCHITECT-CORE repository
Scope: Code synchronization, RAG updates, model syncing
Authority: TIA-ARCHITECT-CORE write access

SOVEREIGN GUARDRAILS:
- Only sync validated TIA code
- Never expose credentials
- Log all sync operations
- Double-N Rift aware (GitHub: DJ-Goana-Coding, HF: DJ-Goanna-Coding)
"""

import os
import json
import datetime
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='🚀 [%(asctime)s] TIA_SYNC: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class TIASyncWorker:
    """
    TIA Sync Worker - Push TIA code to TIA-ARCHITECT-CORE
    
    Syncs:
    - Agent identities
    - Core modules
    - Worker scripts
    - Configuration files
    - Documentation
    """
    
    def __init__(self, repo_root: Path = None):
        self.repo_root = repo_root or Path.cwd()
        self.tia_storage = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "tia_code"
        self.sync_log_path = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "sync_logs"
        self.sync_log_path.mkdir(parents=True, exist_ok=True)
        
        # TIA-ARCHITECT-CORE configuration
        self.tia_core_repo = "https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git"
        self.tia_core_hf = "https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE"
        self.tia_core_path = self.repo_root / ".tia_core_clone"
        
        logger.info("🚀 TIA Sync Worker initialized")
    
    def clone_tia_core(self) -> bool:
        """Clone TIA-ARCHITECT-CORE repository"""
        if self.tia_core_path.exists():
            logger.info("♻️  TIA-ARCHITECT-CORE already cloned")
            return self._update_tia_core()
        
        logger.info(f"📥 Cloning TIA-ARCHITECT-CORE...")
        
        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", self.tia_core_repo, str(self.tia_core_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info("✅ TIA-ARCHITECT-CORE cloned")
                return True
            else:
                logger.error(f"❌ Clone failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"❌ Clone error: {e}")
            return False
    
    def _update_tia_core(self) -> bool:
        """Update existing TIA-ARCHITECT-CORE clone"""
        logger.info("🔄 Updating TIA-ARCHITECT-CORE...")
        
        try:
            result = subprocess.run(
                ["git", "-C", str(self.tia_core_path), "pull"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info("✅ TIA-ARCHITECT-CORE updated")
                return True
            else:
                logger.warning(f"⚠️  Update warning: {result.stderr}")
                return True  # Continue even if pull fails
        
        except Exception as e:
            logger.error(f"❌ Update error: {e}")
            return False
    
    def sync_tia_files(self) -> Dict[str, Any]:
        """
        Sync TIA files to TIA-ARCHITECT-CORE
        
        Returns:
            Sync results
        """
        # Load TIA files list
        tia_list_path = self.tia_storage / "tia_files_list.json"
        if not tia_list_path.exists():
            logger.error("❌ TIA files list not found - run tia_code_finder.py first")
            return {"success": False, "error": "TIA files list not found"}
        
        tia_files = json.loads(tia_list_path.read_text())
        
        logger.info(f"🚀 Syncing {len(tia_files)} TIA files to TIA-ARCHITECT-CORE...")
        
        # Clone/update TIA-ARCHITECT-CORE
        if not self.clone_tia_core():
            return {"success": False, "error": "Failed to clone TIA-ARCHITECT-CORE"}
        
        sync_result = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "files_synced": 0,
            "files_skipped": 0,
            "files_failed": 0,
            "synced_files": []
        }
        
        # Organize files by type
        for file_info in tia_files:
            try:
                source_path = self.repo_root / file_info["path"]
                
                # Skip if source doesn't exist
                if not source_path.exists():
                    sync_result["files_skipped"] += 1
                    continue
                
                # Determine destination based on file type
                dest_rel_path = self._get_destination_path(file_info)
                dest_path = self.tia_core_path / dest_rel_path
                
                # Create destination directory
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                shutil.copy2(source_path, dest_path)
                
                sync_result["files_synced"] += 1
                sync_result["synced_files"].append({
                    "source": file_info["path"],
                    "destination": dest_rel_path,
                    "type": file_info.get("type", "unknown")
                })
                
                logger.info(f"✅ Synced: {file_info['name']} → {dest_rel_path}")
            
            except Exception as e:
                logger.error(f"❌ Sync failed for {file_info.get('name', 'unknown')}: {e}")
                sync_result["files_failed"] += 1
        
        # Save sync log
        log_path = self.sync_log_path / f"tia_sync_{datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        log_path.write_text(json.dumps(sync_result, indent=2))
        
        logger.info(f"✅ Sync complete: {sync_result['files_synced']} files synced")
        
        return sync_result
    
    def _get_destination_path(self, file_info: Dict) -> str:
        """Determine destination path based on file type"""
        file_type = file_info.get("type", "unknown")
        filename = Path(file_info["path"]).name
        
        if file_type == "agent_identity":
            return f".github/agents/{filename}"
        elif file_type in ["architect_module", "oracle_module", "surveyor_module"]:
            return f"core/{filename}"
        elif file_type in ["sentinel_module", "vamguard_module"]:
            return f"security/{filename}"
        elif file_type == "worker_module":
            return f"workers/{filename}"
        elif file_type == "bridge_module":
            return f"bridges/{filename}"
        elif file_type == "citadel_core":
            return f"citadel/{filename}"
        else:
            return f"modules/{filename}"
    
    def commit_and_push(self, message: str = None) -> bool:
        """
        Commit and push changes to TIA-ARCHITECT-CORE
        
        Args:
            message: Commit message
        
        Returns:
            True if successful
        """
        if message is None:
            message = f"🚀 TIA Sync: Auto-sync from Mapping Hub @ {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
        
        logger.info("📤 Committing and pushing to TIA-ARCHITECT-CORE...")
        
        try:
            # Configure git
            subprocess.run(
                ["git", "-C", str(self.tia_core_path), "config", "user.name", "VAMGUARD TIA Sync"],
                capture_output=True
            )
            subprocess.run(
                ["git", "-C", str(self.tia_core_path), "config", "user.email", "tia-sync@citadel.mesh"],
                capture_output=True
            )
            
            # Add all changes
            subprocess.run(
                ["git", "-C", str(self.tia_core_path), "add", "."],
                capture_output=True
            )
            
            # Commit
            result = subprocess.run(
                ["git", "-C", str(self.tia_core_path), "commit", "-m", message],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0 and "nothing to commit" not in result.stdout:
                logger.warning(f"⚠️  Commit warning: {result.stderr}")
            
            # Push to GitHub
            push_result = subprocess.run(
                ["git", "-C", str(self.tia_core_path), "push", "origin", "main"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if push_result.returncode == 0:
                logger.info("✅ Pushed to GitHub: DJ-Goana-Coding/TIA-ARCHITECT-CORE")
            else:
                logger.error(f"❌ GitHub push failed: {push_result.stderr}")
                return False
            
            # Push to HuggingFace (if HF remote exists)
            self._push_to_huggingface()
            
            return True
        
        except Exception as e:
            logger.error(f"❌ Commit/push error: {e}")
            return False
    
    def _push_to_huggingface(self):
        """Push to HuggingFace Space"""
        try:
            # Check if HF remote exists
            result = subprocess.run(
                ["git", "-C", str(self.tia_core_path), "remote", "get-url", "hf"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                # Add HF remote
                subprocess.run(
                    ["git", "-C", str(self.tia_core_path), "remote", "add", "hf", self.tia_core_hf],
                    capture_output=True
                )
            
            # Push to HF
            hf_result = subprocess.run(
                ["git", "-C", str(self.tia_core_path), "push", "--force", "hf", "main"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if hf_result.returncode == 0:
                logger.info("✅ Pushed to HuggingFace: DJ-Goanna-Coding/TIA-ARCHITECT-CORE")
            else:
                logger.warning(f"⚠️  HF push warning: {hf_result.stderr}")
        
        except Exception as e:
            logger.warning(f"⚠️  HF push error: {e}")
    
    def full_sync(self) -> Dict[str, Any]:
        """
        Perform full TIA sync cycle
        
        Returns:
            Complete sync results
        """
        logger.info("🎯 Starting full TIA sync cycle...")
        
        # Sync files
        sync_result = self.sync_tia_files()
        
        if sync_result.get("files_synced", 0) > 0:
            # Commit and push
            success = self.commit_and_push()
            sync_result["pushed"] = success
        else:
            logger.info("ℹ️  No files to sync")
            sync_result["pushed"] = False
        
        return sync_result


def main():
    """Run TIA Sync Worker"""
    worker = TIASyncWorker()
    
    logger.info("🚀 VAMGUARD TITAN - TIA Sync Worker")
    logger.info("=" * 60)
    
    # Perform full sync
    result = worker.full_sync()
    
    # Print summary
    print("\n" + "=" * 60)
    print("🚀 TIA SYNC SUMMARY")
    print("=" * 60)
    print(f"Files Synced: {result.get('files_synced', 0)}")
    print(f"Files Skipped: {result.get('files_skipped', 0)}")
    print(f"Files Failed: {result.get('files_failed', 0)}")
    print(f"Pushed to TIA-ARCHITECT-CORE: {'✅ Yes' if result.get('pushed') else '❌ No'}")
    print("=" * 60)
    
    if result.get("synced_files"):
        print("\n📁 SYNCED FILES BY TYPE:")
        by_type = {}
        for file_info in result["synced_files"]:
            file_type = file_info["type"]
            if file_type not in by_type:
                by_type[file_type] = []
            by_type[file_type].append(file_info)
        
        for file_type, files in sorted(by_type.items()):
            print(f"  - {file_type}: {len(files)} files")
    
    print("=" * 60)


if __name__ == "__main__":
    main()
