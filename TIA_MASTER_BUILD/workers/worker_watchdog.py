#!/usr/bin/env python3
"""
👁️ WORKER WATCHDOG - Continuous Monitoring & Auto-Healing
Q.G.T.N.L. Command Citadel - Worker Constellation Guardian

Purpose: Continuously watch workers and scripts, trigger self-healing when issues detected
Version: 26.0.WATCHDOG+
Authority: Citadel Architect

Monitors:
- Script health (syntax, imports, executability)
- Worker execution failures
- Template changes (auto-update scripts)
- File system changes (detect new/modified scripts)
- Workflow failures
"""

import os
import sys
import time
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime
import hashlib
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/watchdog.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class WorkerWatchdog:
    """
    Continuous Worker Monitoring & Auto-Healing
    
    Watches for:
    - Broken scripts
    - Failed worker executions
    - Template changes
    - New scripts
    """
    
    def __init__(self, check_interval: int = 300):
        self.base_path = Path(__file__).parent.parent
        self.scripts_path = self.base_path / "scripts"
        self.templates_path = self.base_path / "tia-architect-core-templates"
        self.data_path = self.base_path / "data"
        self.monitoring_path = self.data_path / "monitoring"
        self.watchdog_state_file = self.monitoring_path / "watchdog_state.json"
        
        self.check_interval = check_interval  # seconds between checks
        self.running = False
        
        # Track file hashes to detect changes
        self.file_hashes: Dict[str, str] = {}
        self.template_hashes: Dict[str, str] = {}
        
        # Statistics
        self.stats = {
            "total_checks": 0,
            "issues_detected": 0,
            "auto_repairs_triggered": 0,
            "successful_repairs": 0,
            "start_time": None,
            "last_check": None
        }
        
        # Create directories
        self.monitoring_path.mkdir(parents=True, exist_ok=True)
        (self.data_path / "logs").mkdir(parents=True, exist_ok=True)
        
        logger.info("👁️ Worker Watchdog initialized")
        logger.info(f"   Check interval: {check_interval}s")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.sha256(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""
    
    def scan_file_hashes(self, directory: Path, pattern: str = "*.py") -> Dict[str, str]:
        """Scan directory and calculate hashes for all files matching pattern"""
        hashes = {}
        for file_path in directory.rglob(pattern):
            if file_path.is_file() and not file_path.name.startswith('.'):
                rel_path = str(file_path.relative_to(self.base_path))
                hashes[rel_path] = self.calculate_file_hash(file_path)
        return hashes
    
    def detect_changes(self) -> Dict[str, List[str]]:
        """Detect file changes since last check"""
        changes = {
            "new_files": [],
            "modified_files": [],
            "deleted_files": [],
            "template_changes": []
        }
        
        # Scan current state
        current_hashes = self.scan_file_hashes(self.scripts_path, "*.py")
        current_hashes.update(self.scan_file_hashes(self.scripts_path, "*.sh"))
        current_hashes.update(self.scan_file_hashes(self.base_path / "services", "*.py"))
        
        # Detect changes
        for file_path, file_hash in current_hashes.items():
            if file_path not in self.file_hashes:
                changes["new_files"].append(file_path)
                logger.info(f"📝 New file detected: {file_path}")
            elif self.file_hashes[file_path] != file_hash:
                changes["modified_files"].append(file_path)
                logger.info(f"✏️  Modified file detected: {file_path}")
        
        # Detect deletions
        for file_path in self.file_hashes:
            if file_path not in current_hashes:
                changes["deleted_files"].append(file_path)
                logger.info(f"🗑️  Deleted file detected: {file_path}")
        
        # Update hash cache
        self.file_hashes = current_hashes
        
        # Check template changes
        if self.templates_path.exists():
            template_hashes = self.scan_file_hashes(self.templates_path, "*")
            for file_path, file_hash in template_hashes.items():
                if file_path not in self.template_hashes:
                    changes["template_changes"].append(file_path)
                    logger.info(f"📋 New template detected: {file_path}")
                elif self.template_hashes[file_path] != file_hash:
                    changes["template_changes"].append(file_path)
                    logger.info(f"📋 Template updated: {file_path}")
            self.template_hashes = template_hashes
        
        return changes
    
    def trigger_self_healing(self) -> bool:
        """Trigger the self-healing worker"""
        logger.info("🔮 Triggering self-healing worker...")
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.scripts_path / "self_healing_worker.py")],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Self-healing completed successfully")
                self.stats["successful_repairs"] += 1
                return True
            else:
                logger.warning(f"⚠️  Self-healing finished with warnings")
                logger.debug(f"Output: {result.stdout}")
                logger.debug(f"Errors: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Self-healing timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to run self-healing: {e}")
            return False
    
    def check_workflow_health(self) -> bool:
        """Check GitHub Actions workflow health"""
        logger.info("🔍 Checking workflow health...")
        
        try:
            # Check if gh CLI is available
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "5", "--json", "conclusion,status,name"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                runs = json.loads(result.stdout)
                failed_runs = [r for r in runs if r.get("conclusion") == "failure"]
                
                if failed_runs:
                    logger.warning(f"⚠️  {len(failed_runs)} workflow runs failed recently")
                    for run in failed_runs:
                        logger.warning(f"   - {run.get('name', 'Unknown')}: {run.get('conclusion')}")
                    return False
                else:
                    logger.info("✅ All recent workflows healthy")
                    return True
            else:
                logger.debug("GitHub CLI not available or not authenticated")
                return True  # Don't fail if gh CLI not available
                
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Workflow health check timed out")
            return True
        except Exception as e:
            logger.debug(f"Workflow health check error: {e}")
            return True  # Don't fail on errors
    
    def perform_health_check(self):
        """Perform a complete health check cycle"""
        logger.info("🏥 Performing health check...")
        self.stats["total_checks"] += 1
        self.stats["last_check"] = datetime.now().isoformat()
        
        issues_found = False
        
        # 1. Detect file changes
        changes = self.detect_changes()
        if any(changes.values()):
            logger.info(f"📊 Changes detected: {sum(len(v) for v in changes.values())} files")
            issues_found = True
            self.stats["issues_detected"] += 1
        
        # 2. Check workflow health
        workflows_healthy = self.check_workflow_health()
        if not workflows_healthy:
            issues_found = True
            self.stats["issues_detected"] += 1
        
        # 3. Trigger healing if issues found or on first check
        if issues_found or self.stats["total_checks"] == 1:
            logger.info("🔧 Issues detected or initial check, triggering self-healing...")
            self.stats["auto_repairs_triggered"] += 1
            self.trigger_self_healing()
        else:
            logger.info("✅ No issues detected, system healthy")
        
        # Save state
        self.save_state()
    
    def save_state(self):
        """Save watchdog state to file"""
        try:
            state = {
                "stats": self.stats,
                "file_count": len(self.file_hashes),
                "template_count": len(self.template_hashes),
                "last_update": datetime.now().isoformat()
            }
            
            with open(self.watchdog_state_file, 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save watchdog state: {e}")
    
    def load_state(self):
        """Load previous watchdog state"""
        try:
            if self.watchdog_state_file.exists():
                with open(self.watchdog_state_file, 'r') as f:
                    state = json.load(f)
                    self.stats.update(state.get("stats", {}))
                    logger.info(f"📊 Loaded previous state: {state.get('file_count', 0)} files tracked")
        except Exception as e:
            logger.warning(f"Could not load previous state: {e}")
    
    def run_continuous(self):
        """Run continuous monitoring loop"""
        logger.info("🚀 Starting continuous monitoring...")
        self.running = True
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Load previous state
        self.load_state()
        
        # Initial hash scan
        logger.info("📸 Taking initial snapshot...")
        self.file_hashes = self.scan_file_hashes(self.scripts_path, "*.py")
        self.file_hashes.update(self.scan_file_hashes(self.scripts_path, "*.sh"))
        if self.templates_path.exists():
            self.template_hashes = self.scan_file_hashes(self.templates_path, "*")
        
        logger.info(f"📊 Tracking {len(self.file_hashes)} scripts, {len(self.template_hashes)} templates")
        
        try:
            while self.running:
                try:
                    self.perform_health_check()
                except Exception as e:
                    logger.error(f"❌ Health check failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Wait for next check
                logger.info(f"😴 Sleeping for {self.check_interval}s until next check...")
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("⏹️  Watchdog stopped by user")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Fatal error in watchdog: {e}")
            raise
        finally:
            self.save_state()
            logger.info("👁️ Worker Watchdog shutdown complete")
    
    def run_once(self):
        """Run a single health check"""
        logger.info("🎯 Running single health check...")
        self.stats["start_time"] = datetime.now().isoformat()
        
        # Initial snapshot
        self.file_hashes = self.scan_file_hashes(self.scripts_path, "*.py")
        self.file_hashes.update(self.scan_file_hashes(self.scripts_path, "*.sh"))
        if self.templates_path.exists():
            self.template_hashes = self.scan_file_hashes(self.templates_path, "*")
        
        # Perform check
        self.perform_health_check()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print watchdog statistics"""
        print("\n" + "═" * 70)
        print("👁️ WORKER WATCHDOG - SESSION SUMMARY")
        print("═" * 70)
        print(f"Total Checks:          {self.stats['total_checks']}")
        print(f"Issues Detected:       {self.stats['issues_detected']}")
        print(f"Auto-Repairs Triggered: {self.stats['auto_repairs_triggered']}")
        print(f"Successful Repairs:    {self.stats['successful_repairs']}")
        print(f"Files Tracked:         {len(self.file_hashes)}")
        print(f"Templates Tracked:     {len(self.template_hashes)}")
        print("═" * 70 + "\n")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Worker Watchdog - Continuous Monitoring")
    parser.add_argument('--interval', type=int, default=300, help='Check interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create watchdog
    watchdog = WorkerWatchdog(check_interval=args.interval)
    
    if args.once:
        watchdog.run_once()
    else:
        watchdog.run_continuous()


if __name__ == "__main__":
    main()
