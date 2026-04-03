#!/usr/bin/env python3
"""
🤖 AUTONOMOUS SYNC ORCHESTRATOR
Sovereign Systems Overseer for Q.G.T.N.L. Command Citadel

Purpose: Autonomous synchronization orchestration across all nodes and spokes
Authority: Cloud-First Hierarchy (HF > GitHub > GDrive > Local)
Version: 25.0.OMNI+

This worker runs continuously and orchestrates all sync operations:
- Multi-repo GitHub sync (every 6 hours)
- HuggingFace Space sync (on GitHub push + every 6 hours)
- GDrive partition harvesting (every 12 hours)
- District artifact generation (every 24 hours)
- Health monitoring (every 1 hour)
"""

import os
import sys
import time
import json
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/autonomous_sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class AutonomousSyncOrchestrator:
    """
    Autonomous synchronization orchestrator
    
    Maintains continuous sync across all Citadel nodes following
    Cloud-First Authority hierarchy.
    """
    
    def __init__(self, config_path: str = "data/autonomous_sync_config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.last_run_times: Dict[str, datetime] = {}
        self.status_file = Path("data/autonomous_sync_status.json")
        
        # Create data directories if they don't exist
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        
        logger.info("🤖 Autonomous Sync Orchestrator initialized")
        logger.info(f"📋 Config loaded from: {config_path}")
    
    def load_config(self) -> Dict:
        """Load configuration file or create default"""
        default_config = {
            "sync_intervals": {
                "multi_repo_sync": 21600,      # 6 hours
                "hf_space_sync": 21600,        # 6 hours
                "gdrive_harvest": 43200,       # 12 hours
                "district_artifacts": 86400,   # 24 hours
                "health_check": 3600,          # 1 hour
                "master_inventory": 21600,     # 6 hours
                "rag_ingestion": 43200         # 12 hours
            },
            "workflows": {
                "multi_repo_sync": "multi_repo_sync.yml",
                "hf_space_sync": "sync_to_hf.yml",
                "gdrive_harvest": "gdrive_partition_harvester.yml",
                "district_artifacts": "bridge_push.yml",
                "health_check": "tia_core_monitor.yml",
                "master_inventory": "master_harvester.yml",
                "rag_ingestion": "oracle_sync.yml"
            },
            "enabled_tasks": {
                "multi_repo_sync": True,
                "hf_space_sync": True,
                "gdrive_harvest": True,
                "district_artifacts": True,
                "health_check": True,
                "master_inventory": True,
                "rag_ingestion": True
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                logger.info("✅ Configuration loaded successfully")
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}, using defaults")
                return default_config
        else:
            # Save default config
            Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(default_config, f, indent=2)
            logger.info("📝 Created default configuration file")
            return default_config
    
    def should_run_task(self, task_name: str) -> bool:
        """Check if a task should run based on interval"""
        if not self.config["enabled_tasks"].get(task_name, False):
            return False
        
        interval = self.config["sync_intervals"].get(task_name, 3600)
        last_run = self.last_run_times.get(task_name)
        
        if last_run is None:
            return True
        
        elapsed = (datetime.now() - last_run).total_seconds()
        return elapsed >= interval
    
    def trigger_workflow(self, workflow_name: str) -> bool:
        """Trigger a GitHub Actions workflow"""
        try:
            logger.info(f"🚀 Triggering workflow: {workflow_name}")
            
            cmd = [
                "gh", "workflow", "run", workflow_name,
                "--repo", "DJ-Goana-Coding/mapping-and-inventory"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Workflow triggered successfully: {workflow_name}")
                return True
            else:
                logger.error(f"❌ Workflow trigger failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ Workflow trigger timed out: {workflow_name}")
            return False
        except Exception as e:
            logger.error(f"💥 Workflow trigger error: {e}")
            return False
    
    def run_script(self, script_path: str, args: List[str] = None) -> bool:
        """Run a Python script"""
        try:
            logger.info(f"🐍 Running script: {script_path}")
            
            cmd = ["python3", script_path]
            if args:
                cmd.extend(args)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes
            )
            
            if result.returncode == 0:
                logger.info(f"✅ Script completed successfully: {script_path}")
                return True
            else:
                logger.error(f"❌ Script failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ Script timed out: {script_path}")
            return False
        except Exception as e:
            logger.error(f"💥 Script error: {e}")
            return False
    
    def execute_task(self, task_name: str) -> bool:
        """Execute a sync task"""
        workflow = self.config["workflows"].get(task_name)
        
        if not workflow:
            logger.warning(f"⚠️ No workflow configured for task: {task_name}")
            return False
        
        success = self.trigger_workflow(workflow)
        
        if success:
            self.last_run_times[task_name] = datetime.now()
        
        return success
    
    def save_status(self):
        """Save current status to file"""
        status = {
            "last_updated": datetime.now().isoformat(),
            "last_run_times": {
                task: time.isoformat()
                for task, time in self.last_run_times.items()
            },
            "enabled_tasks": self.config["enabled_tasks"],
            "sync_intervals": self.config["sync_intervals"]
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
    
    def orchestration_cycle(self):
        """Run one orchestration cycle"""
        logger.info("🔄 Starting orchestration cycle")
        
        tasks_run = 0
        tasks_succeeded = 0
        
        # Check each task
        for task_name in self.config["workflows"].keys():
            if self.should_run_task(task_name):
                logger.info(f"📋 Task due: {task_name}")
                success = self.execute_task(task_name)
                tasks_run += 1
                if success:
                    tasks_succeeded += 1
                
                # Small delay between tasks to avoid overwhelming GitHub API
                time.sleep(5)
        
        # Save status
        self.save_status()
        
        logger.info(f"✅ Cycle complete: {tasks_succeeded}/{tasks_run} tasks succeeded")
    
    def run_forever(self, check_interval: int = 300):
        """
        Run orchestrator continuously
        
        Args:
            check_interval: Seconds between orchestration cycles (default: 5 minutes)
        """
        logger.info(f"🚀 Starting autonomous orchestration (check every {check_interval}s)")
        
        try:
            while True:
                try:
                    self.orchestration_cycle()
                except Exception as e:
                    logger.error(f"💥 Orchestration cycle error: {e}")
                
                # Wait before next cycle
                logger.info(f"💤 Sleeping for {check_interval} seconds")
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info("🛑 Orchestrator stopped by user")
        except Exception as e:
            logger.error(f"💥 Fatal error: {e}")
            raise
    
    def run_once(self):
        """Run orchestration once and exit"""
        logger.info("🚀 Running single orchestration cycle")
        self.orchestration_cycle()
        logger.info("✅ Single cycle complete")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Autonomous Sync Orchestrator for Q.G.T.N.L. Command Citadel"
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run once and exit (instead of continuous)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=300,
        help="Check interval in seconds (default: 300 = 5 minutes)"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="data/autonomous_sync_config.json",
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    orchestrator = AutonomousSyncOrchestrator(config_path=args.config)
    
    if args.once:
        orchestrator.run_once()
    else:
        orchestrator.run_forever(check_interval=args.interval)


if __name__ == "__main__":
    main()
