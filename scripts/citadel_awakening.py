#!/usr/bin/env python3
"""
🏰 CITADEL AWAKENING - Master Orchestrator
Q.G.T.N.L. Command Citadel - Full Network Activation

Purpose: Deploy and coordinate all autonomous workers across the Citadel Mesh
Authority: Citadel Architect v26.0.AWAKENING+
"""

import os
import sys
import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import concurrent.futures

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/citadel_awakening.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CitadelAwakening:
    """
    Master Orchestrator for Citadel Network Activation
    
    Coordinates:
    - Discovery workers (scouts, hounds)
    - Security workers (sentinels, wraiths)
    - Processing workers (catalogers, ingestors)
    - Monitoring workers (watchers, reporters)
    """
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent
        self.scripts_path = self.base_path / "scripts"
        self.data_path = self.base_path / "data"
        self.logs_path = self.data_path / "logs"
        self.status_file = self.data_path / "worker_status.json"
        
        # Create directories
        self.logs_path.mkdir(parents=True, exist_ok=True)
        (self.data_path / "discoveries").mkdir(parents=True, exist_ok=True)
        (self.data_path / "monitoring").mkdir(parents=True, exist_ok=True)
        
        # Worker registry
        self.workers = self.load_worker_registry()
        
        logger.info("🏰 Citadel Awakening Orchestrator initialized")
    
    def load_worker_registry(self) -> Dict:
        """Load worker registry with all available workers"""
        return {
            "scouts": [
                {
                    "name": "Domain Scout",
                    "script": "domain_scout.py",
                    "type": "discovery",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "Spiritual Network Mapper",
                    "script": "spiritual_network_mapper.py",
                    "type": "discovery",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "Repo Scout",
                    "script": "discover_all_repos.py",
                    "type": "discovery",
                    "status": "ready",
                    "priority": 2
                },
                {
                    "name": "Trending Scout",
                    "script": "harvest_github_trending.py",
                    "type": "discovery",
                    "status": "ready",
                    "priority": 3
                }
            ],
            "hounds": [
                {
                    "name": "District Harvester",
                    "script": "autonomous_district_harvester.py",
                    "type": "collection",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "Laptop Scanner",
                    "script": "laptop_filesystem_scanner.py",
                    "type": "collection",
                    "status": "ready",
                    "priority": 2
                },
                {
                    "name": "Trading Garage Collector",
                    "script": "trading_garage_collector.py",
                    "type": "collection",
                    "status": "ready",
                    "priority": 2
                }
            ],
            "sentinels": [
                {
                    "name": "Health Monitor",
                    "script": "autonomous_health_monitor.py",
                    "type": "monitoring",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "Sentinel Coordinator",
                    "script": "sentinel_coordinator.py",
                    "type": "security",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "TIA Coordinator",
                    "script": "tia_coordinator.py",
                    "type": "monitoring",
                    "status": "ready",
                    "priority": 2
                }
            ],
            "wraiths": [
                {
                    "name": "Vacuum Cleaner",
                    "script": "vacuum_cleaner.py",
                    "type": "maintenance",
                    "status": "ready",
                    "priority": 3
                }
            ],
            "coordinators": [
                {
                    "name": "Master Pipeline Orchestrator",
                    "script": "master_pipeline_orchestrator.py",
                    "type": "orchestration",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "Sync Orchestrator",
                    "script": "autonomous_sync_orchestrator.py",
                    "type": "orchestration",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "HarvestMoon Coordinator",
                    "script": "harvestmoon_coordinator.py",
                    "type": "orchestration",
                    "status": "ready",
                    "priority": 2
                },
                {
                    "name": "Librarian Consolidator",
                    "script": "librarian_consolidator.py",
                    "type": "processing",
                    "status": "ready",
                    "priority": 2
                }
            ],
            "ingestors": [
                {
                    "name": "RAG Ingest",
                    "script": "rag_ingest.py",
                    "type": "processing",
                    "status": "ready",
                    "priority": 1
                },
                {
                    "name": "Wake Up TIA",
                    "script": "wake_up_tia.py",
                    "type": "activation",
                    "status": "ready",
                    "priority": 1
                }
            ]
        }
    
    def deploy_worker(self, worker: Dict) -> Dict:
        """Deploy a single worker"""
        script_path = self.scripts_path / worker["script"]
        
        if not script_path.exists():
            logger.warning(f"⚠️ Worker script not found: {worker['name']}")
            return {
                "worker": worker["name"],
                "status": "not_found",
                "error": f"Script not found: {worker['script']}"
            }
        
        try:
            logger.info(f"🚀 Deploying {worker['name']}...")
            
            # Run the worker script
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=str(self.base_path),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                logger.info(f"✅ {worker['name']} deployed successfully")
                return {
                    "worker": worker["name"],
                    "status": "success",
                    "output": result.stdout[-500:] if result.stdout else ""
                }
            else:
                logger.error(f"❌ {worker['name']} failed: {result.stderr}")
                return {
                    "worker": worker["name"],
                    "status": "failed",
                    "error": result.stderr[-500:] if result.stderr else ""
                }
        
        except subprocess.TimeoutExpired:
            logger.warning(f"⏱️ {worker['name']} timed out (still running)")
            return {
                "worker": worker["name"],
                "status": "timeout",
                "note": "Worker may still be running in background"
            }
        except Exception as e:
            logger.error(f"❌ {worker['name']} error: {e}")
            return {
                "worker": worker["name"],
                "status": "error",
                "error": str(e)
            }
    
    def deploy_worker_group(self, group_name: str, workers: List[Dict], parallel: bool = False) -> List[Dict]:
        """Deploy a group of workers"""
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 Deploying {group_name.upper()} ({len(workers)} workers)")
        logger.info(f"{'='*60}\n")
        
        results = []
        
        if parallel and len(workers) > 1:
            # Deploy workers in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
                future_to_worker = {
                    executor.submit(self.deploy_worker, worker): worker
                    for worker in workers
                }
                
                for future in concurrent.futures.as_completed(future_to_worker):
                    result = future.result()
                    results.append(result)
        else:
            # Deploy workers sequentially (by priority)
            sorted_workers = sorted(workers, key=lambda w: w.get("priority", 999))
            for worker in sorted_workers:
                result = self.deploy_worker(worker)
                results.append(result)
        
        return results
    
    def wake_citadel(self):
        """Wake up the entire Citadel network"""
        logger.info("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║               🏰 CITADEL AWAKENING PROTOCOL 🏰                     ║
║                                                                    ║
║           "Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"  ║
║                   Let's wake the citadel up!                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
        """)
        
        all_results = {}
        
        # Phase 1: Sentinels (monitoring & security first)
        logger.info("\n🛡️ PHASE 1: Deploying Sentinels (Security & Monitoring)")
        all_results["sentinels"] = self.deploy_worker_group(
            "sentinels",
            self.workers["sentinels"],
            parallel=True
        )
        
        # Phase 2: Scouts (discovery)
        logger.info("\n🔍 PHASE 2: Deploying Scouts (Discovery)")
        all_results["scouts"] = self.deploy_worker_group(
            "scouts",
            self.workers["scouts"],
            parallel=True
        )
        
        # Phase 3: Hounds (collection)
        logger.info("\n🐕 PHASE 3: Deploying Hounds (Collection)")
        all_results["hounds"] = self.deploy_worker_group(
            "hounds",
            self.workers["hounds"],
            parallel=False  # Sequential for safety
        )
        
        # Phase 4: Coordinators (orchestration)
        logger.info("\n🎯 PHASE 4: Deploying Coordinators (Orchestration)")
        all_results["coordinators"] = self.deploy_worker_group(
            "coordinators",
            self.workers["coordinators"],
            parallel=False
        )
        
        # Phase 5: Ingestors (processing)
        logger.info("\n🔄 PHASE 5: Deploying Ingestors (Processing)")
        all_results["ingestors"] = self.deploy_worker_group(
            "ingestors",
            self.workers["ingestors"],
            parallel=False
        )
        
        # Phase 6: Wraiths (cleanup)
        logger.info("\n👻 PHASE 6: Deploying Wraiths (Cleanup)")
        all_results["wraiths"] = self.deploy_worker_group(
            "wraiths",
            self.workers["wraiths"],
            parallel=False
        )
        
        # Save results
        self.save_deployment_results(all_results)
        
        # Print summary
        self.print_summary(all_results)
        
        return all_results
    
    def save_deployment_results(self, results: Dict):
        """Save deployment results to file"""
        output_file = self.data_path / "monitoring" / "deployment_results.json"
        
        deployment_data = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "summary": self.calculate_summary(results)
        }
        
        with open(output_file, 'w') as f:
            json.dump(deployment_data, f, indent=2)
        
        logger.info(f"\n💾 Results saved to {output_file}")
    
    def calculate_summary(self, results: Dict) -> Dict:
        """Calculate deployment summary statistics"""
        total = 0
        success = 0
        failed = 0
        timeout = 0
        not_found = 0
        
        for group_results in results.values():
            for result in group_results:
                total += 1
                status = result.get("status", "unknown")
                if status == "success":
                    success += 1
                elif status == "failed" or status == "error":
                    failed += 1
                elif status == "timeout":
                    timeout += 1
                elif status == "not_found":
                    not_found += 1
        
        return {
            "total_workers": total,
            "successful": success,
            "failed": failed,
            "timeout": timeout,
            "not_found": not_found,
            "success_rate": f"{(success/total*100):.1f}%" if total > 0 else "0%"
        }
    
    def print_summary(self, results: Dict):
        """Print deployment summary"""
        summary = self.calculate_summary(results)
        
        logger.info(f"""
╔════════════════════════════════════════════════════════════════════╗
║                    DEPLOYMENT SUMMARY                               ║
╠════════════════════════════════════════════════════════════════════╣
║  Total Workers:     {summary['total_workers']:<47} ║
║  ✅ Successful:     {summary['successful']:<47} ║
║  ❌ Failed:         {summary['failed']:<47} ║
║  ⏱️  Timeout:        {summary['timeout']:<47} ║
║  ⚠️  Not Found:     {summary['not_found']:<47} ║
║  📊 Success Rate:   {summary['success_rate']:<47} ║
╚════════════════════════════════════════════════════════════════════╝

🎉 CITADEL AWAKENING COMPLETE! The network is ALIVE! 🎉
        """)


def main():
    """Main entry point"""
    try:
        orchestrator = CitadelAwakening()
        results = orchestrator.wake_citadel()
        
        # Exit with appropriate code
        summary = orchestrator.calculate_summary(results)
        if summary["failed"] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    
    except KeyboardInterrupt:
        logger.info("\n⚠️ Awakening interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Fatal error during awakening: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
