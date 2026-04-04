#!/usr/bin/env python3
"""
🎯 PERSONAL ARCHIVE OMNIVAC ORCHESTRATOR v1.0
Master coordinator for the complete personal data harvesting, RAG ingestion,
and website deployment pipeline

Coordinates:
1. Email harvesting (8+ accounts)
2. Browser history extraction
3. AI chat archiving
4. Device scanning
5. RAG ingestion
6. Tech stack procurement
7. Website generation
8. Infrastructure deployment

Usage:
    python personal_archive_orchestrator.py --phase all
    python personal_archive_orchestrator.py --phase harvest
    python personal_archive_orchestrator.py --phase rag
    python personal_archive_orchestrator.py --phase deploy
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PersonalArchiveOrchestrator:
    """Master orchestration for Personal Archive Omnivac Protocol"""
    
    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)
        self.scripts_dir = self.base_dir / "scripts"
        self.data_dir = self.base_dir / "data" / "personal_archive"
        
        self.stats = {
            "phases_completed": [],
            "phases_failed": [],
            "total_runtime_seconds": 0
        }
    
    def run_script(self, script_name: str, description: str) -> Dict:
        """Run a Python script and capture results"""
        logger.info(f"🚀 Running: {description}")
        logger.info(f"   Script: {script_name}")
        
        script_path = self.scripts_dir / script_name
        
        if not script_path.exists():
            logger.error(f"❌ Script not found: {script_path}")
            return {"status": "error", "message": "script not found"}
        
        try:
            start_time = datetime.now()
            
            result = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes max
            )
            
            end_time = datetime.now()
            runtime = (end_time - start_time).total_seconds()
            
            if result.returncode == 0:
                logger.info(f"✅ {description} completed in {runtime:.2f}s")
                return {
                    "status": "success",
                    "runtime_seconds": runtime,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            else:
                logger.error(f"❌ {description} failed")
                logger.error(f"   Error: {result.stderr}")
                return {
                    "status": "error",
                    "runtime_seconds": runtime,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
        
        except subprocess.TimeoutExpired:
            logger.error(f"⏱️ {description} timed out")
            return {"status": "timeout"}
        
        except Exception as e:
            logger.error(f"❌ {description} exception: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def phase_1_harvest(self) -> Dict:
        """Phase 1: Data Harvesting"""
        logger.info("=" * 80)
        logger.info("📦 PHASE 1: DATA HARVESTING")
        logger.info("=" * 80)
        
        results = {}
        
        # 1. Email harvesting
        results["email_harvester"] = self.run_script(
            "email_archive_harvester.py",
            "Email Archive Harvester"
        )
        
        # 2. Browser history
        results["browser_vacuum"] = self.run_script(
            "browser_history_vacuum.py",
            "Browser History Vacuum"
        )
        
        # 3. AI chats
        results["ai_chats"] = self.run_script(
            "ai_chat_extractor.py",
            "AI Chat Extractor"
        )
        
        # 4. Device scanning
        results["device_scanner"] = self.run_script(
            "device_account_scanner.py",
            "Device Account Scanner"
        )
        
        # Check if phase successful
        success_count = sum(1 for r in results.values() if r.get("status") == "success")
        
        if success_count == len(results):
            self.stats["phases_completed"].append("harvest")
            logger.info("✅ Phase 1: Data Harvesting - COMPLETE")
        else:
            self.stats["phases_failed"].append("harvest")
            logger.error(f"❌ Phase 1: Data Harvesting - PARTIAL ({success_count}/{len(results)} succeeded)")
        
        return {
            "phase": "harvest",
            "status": "success" if success_count == len(results) else "partial",
            "results": results
        }
    
    def phase_2_rag_ingestion(self) -> Dict:
        """Phase 2: RAG Ingestion"""
        logger.info("=" * 80)
        logger.info("🧠 PHASE 2: RAG INGESTION")
        logger.info("=" * 80)
        
        results = {}
        
        # RAG ingestion
        results["rag_ingest"] = self.run_script(
            "personal_archive_rag_ingest.py",
            "Personal Archive RAG Ingestion"
        )
        
        if results["rag_ingest"].get("status") == "success":
            self.stats["phases_completed"].append("rag")
            logger.info("✅ Phase 2: RAG Ingestion - COMPLETE")
        else:
            self.stats["phases_failed"].append("rag")
            logger.error("❌ Phase 2: RAG Ingestion - FAILED")
        
        return {
            "phase": "rag",
            "status": results["rag_ingest"].get("status"),
            "results": results
        }
    
    def phase_3_tech_shopping(self) -> Dict:
        """Phase 3: Technology Stack Research"""
        logger.info("=" * 80)
        logger.info("🛍️ PHASE 3: TECH STACK SHOPPING")
        logger.info("=" * 80)
        
        results = {}
        
        # Tech stack shopper
        results["tech_shopper"] = self.run_script(
            "tech_stack_shopper.py",
            "Tech Stack Shopper"
        )
        
        if results["tech_shopper"].get("status") == "success":
            self.stats["phases_completed"].append("tech_shopping")
            logger.info("✅ Phase 3: Tech Stack Shopping - COMPLETE")
        else:
            self.stats["phases_failed"].append("tech_shopping")
            logger.error("❌ Phase 3: Tech Stack Shopping - FAILED")
        
        return {
            "phase": "tech_shopping",
            "status": results["tech_shopper"].get("status"),
            "results": results
        }
    
    def phase_4_website_generation(self) -> Dict:
        """Phase 4: Website Generation"""
        logger.info("=" * 80)
        logger.info("🌐 PHASE 4: WEBSITE GENERATION")
        logger.info("=" * 80)
        
        logger.info("⚠️ Website generation requires manual setup:")
        logger.info("   1. Create Next.js 14 project")
        logger.info("   2. Install dependencies from BOM")
        logger.info("   3. Configure RAG search interface")
        logger.info("   4. Deploy to Vercel")
        logger.info("")
        logger.info("📝 See PERSONAL_ARCHIVE_OMNIVAC_PROTOCOL.md for full instructions")
        
        self.stats["phases_completed"].append("website_generation")
        
        return {
            "phase": "website_generation",
            "status": "manual",
            "message": "Requires manual setup - see protocol documentation"
        }
    
    def run_all_phases(self) -> Dict:
        """Execute all phases in sequence"""
        logger.info("=" * 80)
        logger.info("🎯 PERSONAL ARCHIVE OMNIVAC - FULL EXECUTION")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        results = {
            "execution_date": start_time.isoformat(),
            "phases": {}
        }
        
        # Phase 1: Harvest
        results["phases"]["harvest"] = self.phase_1_harvest()
        
        # Phase 2: RAG
        results["phases"]["rag"] = self.phase_2_rag_ingestion()
        
        # Phase 3: Tech Shopping
        results["phases"]["tech_shopping"] = self.phase_3_tech_shopping()
        
        # Phase 4: Website (manual)
        results["phases"]["website"] = self.phase_4_website_generation()
        
        end_time = datetime.now()
        runtime = (end_time - start_time).total_seconds()
        
        self.stats["total_runtime_seconds"] = runtime
        
        results["statistics"] = self.stats
        results["total_runtime_seconds"] = runtime
        results["total_runtime_minutes"] = runtime / 60
        
        # Save results
        results_path = self.data_dir / "orchestration_results.json"
        results_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(results_path, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 ORCHESTRATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total runtime: {runtime/60:.2f} minutes")
        logger.info(f"Phases completed: {len(self.stats['phases_completed'])}")
        logger.info(f"Phases failed: {len(self.stats['phases_failed'])}")
        logger.info(f"Results saved: {results_path}")
        logger.info("=" * 80)
        
        return results


def main():
    """Main execution with argument parsing"""
    parser = argparse.ArgumentParser(
        description="Personal Archive Omnivac Orchestrator v1.0"
    )
    parser.add_argument(
        "--phase",
        choices=["all", "harvest", "rag", "tech", "website"],
        default="all",
        help="Phase to execute (default: all)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("🎯 PERSONAL ARCHIVE OMNIVAC ORCHESTRATOR v1.0")
    print("=" * 80)
    print()
    
    orchestrator = PersonalArchiveOrchestrator()
    
    if args.phase == "all":
        results = orchestrator.run_all_phases()
    elif args.phase == "harvest":
        results = orchestrator.phase_1_harvest()
    elif args.phase == "rag":
        results = orchestrator.phase_2_rag_ingestion()
    elif args.phase == "tech":
        results = orchestrator.phase_3_tech_shopping()
    elif args.phase == "website":
        results = orchestrator.phase_4_website_generation()
    else:
        print(f"Unknown phase: {args.phase}")
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("✅ ORCHESTRATION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()
