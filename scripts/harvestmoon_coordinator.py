#!/usr/bin/env python3
"""
HARVESTMOON PIPELINE COORDINATOR
Coordinates harvestmoon workers with Citadel automation
Creates unified pipelines for file pulling and harvesting

Usage:
    python harvestmoon_coordinator.py --discover
    python harvestmoon_coordinator.py --create-pipeline gdrive-pull
    python harvestmoon_coordinator.py --status
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import subprocess


class HarvestmoonCoordinator:
    """Coordinates harvestmoon workers with Citadel infrastructure"""
    
    def __init__(self):
        self.workers_dir = Path("data/workers/harvestmoon")
        self.manifest_file = Path("data/workers/workers_manifest.json")
        self.pipelines_dir = Path("data/pipelines")
        self.pipelines_dir.mkdir(parents=True, exist_ok=True)
    
    def discover_harvestmoon_workers(self):
        """Discover available harvestmoon workers"""
        print("\n🌙 Discovering Harvestmoon Workers...")
        print("=" * 60)
        
        if not self.workers_dir.exists():
            print("❌ Harvestmoon workers directory not found")
            print("   Run harvestmoon_integration.yml workflow first")
            return []
        
        workers = []
        for worker_file in self.workers_dir.glob("*.py"):
            workers.append({
                "name": worker_file.stem,
                "path": str(worker_file),
                "type": self._classify_worker(worker_file)
            })
            print(f"  ✅ {worker_file.name} ({self._classify_worker(worker_file)})")
        
        print(f"\n✅ Found {len(workers)} harvestmoon workers")
        return workers
    
    def _classify_worker(self, worker_file):
        """Classify worker based on filename and content"""
        name_lower = worker_file.name.lower()
        
        if 'harvest' in name_lower:
            return "harvester"
        elif 'pull' in name_lower or 'fetch' in name_lower:
            return "file_puller"
        elif 'pipeline' in name_lower:
            return "pipeline"
        elif 'automat' in name_lower:
            return "automation"
        else:
            return "utility"
    
    def create_pipeline(self, pipeline_type):
        """Create integration pipeline"""
        print(f"\n🔨 Creating {pipeline_type} pipeline...")
        print("=" * 60)
        
        pipelines = {
            "gdrive-pull": self._create_gdrive_pull_pipeline,
            "laptop-sync": self._create_laptop_sync_pipeline,
            "full-harvest": self._create_full_harvest_pipeline
        }
        
        if pipeline_type in pipelines:
            pipelines[pipeline_type]()
        else:
            print(f"❌ Unknown pipeline type: {pipeline_type}")
            print(f"   Available: {', '.join(pipelines.keys())}")
    
    def _create_gdrive_pull_pipeline(self):
        """Create GDrive pull pipeline using harvestmoon workers"""
        pipeline = {
            "pipeline_id": "gdrive-pull-harvestmoon",
            "created": datetime.utcnow().isoformat() + "Z",
            "description": "Pull files from GDrive using harvestmoon workers",
            "steps": [
                {
                    "step": 1,
                    "name": "Partition Scan",
                    "workflow": "gdrive_partition_harvester.yml",
                    "output": "data/gdrive_manifests/*.json"
                },
                {
                    "step": 2,
                    "name": "Harvestmoon Discovery",
                    "worker": "harvestmoon/harvest_worker.py",
                    "input": "data/gdrive_manifests/*.json",
                    "output": "data/harvestmoon_pulls/*.json"
                },
                {
                    "step": 3,
                    "name": "File Pull",
                    "worker": "harvestmoon/file_puller.py",
                    "input": "data/harvestmoon_pulls/*.json",
                    "output": "data/pulled_files/*"
                },
                {
                    "step": 4,
                    "name": "Indexing",
                    "workflow": "gdrive_document_indexer.yml",
                    "input": "data/pulled_files/*"
                },
                {
                    "step": 5,
                    "name": "Consolidation",
                    "script": "scripts/librarian_consolidator.py",
                    "output": "master_inventory.json"
                }
            ],
            "schedule": "0 */6 * * *",
            "status": "ready"
        }
        
        pipeline_file = self.pipelines_dir / "gdrive_pull_harvestmoon.json"
        with open(pipeline_file, 'w') as f:
            json.dump(pipeline, f, indent=2)
        
        print(f"✅ Pipeline created: {pipeline_file}")
        print(f"   Steps: {len(pipeline['steps'])}")
    
    def _create_laptop_sync_pipeline(self):
        """Create laptop sync pipeline using harvestmoon"""
        pipeline = {
            "pipeline_id": "laptop-sync-harvestmoon",
            "created": datetime.utcnow().isoformat() + "Z",
            "description": "Sync laptop files using harvestmoon automation",
            "steps": [
                {
                    "step": 1,
                    "name": "Desktop Scan",
                    "script": "scripts/laptop_desktop_scanner.py",
                    "args": ["--scan", "~/Desktop", "--ingest-map"],
                    "output": "data/laptop_inventory/*.json"
                },
                {
                    "step": 2,
                    "name": "Harvestmoon Processing",
                    "worker": "harvestmoon/laptop_processor.py",
                    "input": "data/laptop_inventory/*.json"
                },
                {
                    "step": 3,
                    "name": "Push to Hub",
                    "workflow": "laptop_push_workflow.yml"
                },
                {
                    "step": 4,
                    "name": "MASTER_MERGE_2 Ingestion",
                    "workflow": "laptop_master_merge_ingestion.yml",
                    "trigger": "data/laptop_inventory/master_system_map_2.json"
                }
            ],
            "trigger": "manual",
            "status": "ready"
        }
        
        pipeline_file = self.pipelines_dir / "laptop_sync_harvestmoon.json"
        with open(pipeline_file, 'w') as f:
            json.dump(pipeline, f, indent=2)
        
        print(f"✅ Pipeline created: {pipeline_file}")
    
    def _create_full_harvest_pipeline(self):
        """Create full harvest pipeline orchestrating all systems"""
        pipeline = {
            "pipeline_id": "full-harvest-harvestmoon",
            "created": datetime.utcnow().isoformat() + "Z",
            "description": "Full harvest cycle with harvestmoon coordination",
            "steps": [
                {
                    "step": 1,
                    "name": "GDrive Partition Harvest",
                    "workflow": "gdrive_partition_harvester.yml"
                },
                {
                    "step": 2,
                    "name": "Model Ingestion",
                    "workflow": "gdrive_model_ingester.yml"
                },
                {
                    "step": 3,
                    "name": "Worker Harvesting",
                    "workflow": "gdrive_worker_harvester.yml"
                },
                {
                    "step": 4,
                    "name": "Document Indexing",
                    "workflow": "gdrive_document_indexer.yml"
                },
                {
                    "step": 5,
                    "name": "Harvestmoon Orchestration",
                    "workflow": "harvestmoon_integration.yml"
                },
                {
                    "step": 6,
                    "name": "Master Harvest",
                    "workflow": "master_harvester.yml"
                },
                {
                    "step": 7,
                    "name": "Librarian Consolidation",
                    "script": "scripts/librarian_consolidator.py"
                },
                {
                    "step": 8,
                    "name": "Vacuum Cleanup",
                    "script": "scripts/vacuum_cleaner.py",
                    "args": ["--full-clean"]
                },
                {
                    "step": 9,
                    "name": "RAG Update",
                    "workflow": "oracle_sync.yml"
                }
            ],
            "schedule": "0 0 * * *",
            "status": "ready"
        }
        
        pipeline_file = self.pipelines_dir / "full_harvest_harvestmoon.json"
        with open(pipeline_file, 'w') as f:
            json.dump(pipeline, f, indent=2)
        
        print(f"✅ Pipeline created: {pipeline_file}")
        print(f"   Steps: {len(pipeline['steps'])}")
    
    def show_status(self):
        """Show harvestmoon coordinator status"""
        print("\n" + "=" * 60)
        print("🌙 HARVESTMOON COORDINATOR STATUS")
        print("=" * 60)
        
        # Check workers
        if self.workers_dir.exists():
            worker_count = len(list(self.workers_dir.glob("*.py")))
            print(f"\n✅ Harvestmoon Workers: {worker_count}")
        else:
            print("\n⚠️  Harvestmoon workers not found")
        
        # Check pipelines
        if self.pipelines_dir.exists():
            pipeline_count = len(list(self.pipelines_dir.glob("*harvestmoon*.json")))
            print(f"✅ Harvestmoon Pipelines: {pipeline_count}")
            
            for pipeline_file in self.pipelines_dir.glob("*harvestmoon*.json"):
                with open(pipeline_file, 'r') as f:
                    pipeline = json.load(f)
                print(f"\n  Pipeline: {pipeline['pipeline_id']}")
                print(f"    Steps: {len(pipeline['steps'])}")
                print(f"    Status: {pipeline['status']}")
        else:
            print("⚠️  No pipelines created")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Harvestmoon Pipeline Coordinator")
    parser.add_argument("--discover", action="store_true",
                       help="Discover harvestmoon workers")
    parser.add_argument("--create-pipeline", 
                       choices=["gdrive-pull", "laptop-sync", "full-harvest"],
                       help="Create integration pipeline")
    parser.add_argument("--status", action="store_true",
                       help="Show coordinator status")
    
    args = parser.parse_args()
    
    coordinator = HarvestmoonCoordinator()
    
    if args.discover:
        coordinator.discover_harvestmoon_workers()
    
    if args.create_pipeline:
        coordinator.create_pipeline(args.create_pipeline)
    
    if args.status:
        coordinator.show_status()
    
    if not any([args.discover, args.create_pipeline, args.status]):
        parser.print_help()


if __name__ == "__main__":
    main()
