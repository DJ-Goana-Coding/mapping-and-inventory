#!/usr/bin/env python3
"""
WORKERS CONSTELLATION SETUP
Discovers and orchestrates all workers from /data/workers
Sets up execution schedules and Google Sheets/Docs connectors

Usage:
    python workers_constellation_setup.py --discover
    python workers_constellation_setup.py --status
"""

import json
import os
from pathlib import Path
from datetime import datetime
import argparse


class WorkersConstellation:
    """Orchestrator for CITADEL worker constellation"""
    
    def __init__(self):
        self.data_dir = Path("data/workers")
        self.manifest_file = self.data_dir / "workers_manifest.json"
        self.local_workers_dir = Path("services")
    
    def discover_workers(self):
        """Discover all workers from data/workers and services/"""
        print("🔍 Discovering workers...")
        
        workers = {
            "discovery_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_workers": 0,
            "categories": {
                "Vacuums": {"count": 0, "workers": []},
                "Harvesters": {"count": 0, "workers": []},
                "Librarians": {"count": 0, "workers": []},
                "Reporters": {"count": 0, "workers": []},
                "Archivists": {"count": 0, "workers": []},
                "Utility": {"count": 0, "workers": []}
            }
        }
        
        # Discover local workers (services/ directory)
        if self.local_workers_dir.exists():
            for worker_file in self.local_workers_dir.glob("worker_*.py"):
                worker_info = self._analyze_worker(worker_file, "local")
                category = worker_info["category"]
                workers["categories"][category]["workers"].append(worker_info)
                workers["categories"][category]["count"] += 1
                workers["total_workers"] += 1
        
        # Discover GDrive workers (data/workers/)
        if self.data_dir.exists():
            for worker_file in self.data_dir.glob("*"):
                if worker_file.suffix in ['.gs', '.js', '.py']:
                    worker_info = self._analyze_worker(worker_file, "gdrive")
                    category = worker_info["category"]
                    workers["categories"][category]["workers"].append(worker_info)
                    workers["categories"][category]["count"] += 1
                    workers["total_workers"] += 1
        
        # Save manifest
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with open(self.manifest_file, 'w') as f:
            json.dump(workers, f, indent=2)
        
        print(f"✅ Discovered {workers['total_workers']} workers")
        print("\nCategory Breakdown:")
        for category, data in workers["categories"].items():
            if data["count"] > 0:
                print(f"  {category}: {data['count']}")
        
        return workers
    
    def _analyze_worker(self, worker_file, source):
        """Analyze worker file and extract metadata"""
        category = self._categorize_worker(worker_file.name)
        
        worker_info = {
            "name": worker_file.stem,
            "filename": worker_file.name,
            "path": str(worker_file),
            "source": source,
            "category": category,
            "status": "discovered",
            "schedule": self._get_default_schedule(category),
            "dependencies": self._detect_dependencies(worker_file),
            "size_bytes": worker_file.stat().st_size if worker_file.exists() else 0
        }
        
        return worker_info
    
    def _categorize_worker(self, filename):
        """Categorize worker based on filename"""
        filename_lower = filename.lower()
        
        categories = {
            "Vacuums": ["vacuum", "clean", "purge"],
            "Harvesters": ["harvest", "collect", "gather", "fetch"],
            "Librarians": ["librarian", "catalog", "index", "archivist"],
            "Reporters": ["reporter", "report", "notify"],
            "Archivists": ["archivist", "archive", "store"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in filename_lower for keyword in keywords):
                return category
        
        return "Utility"
    
    def _get_default_schedule(self, category):
        """Get default execution schedule for category"""
        schedules = {
            "Vacuums": "0 0 * * 0",  # Weekly on Sunday
            "Harvesters": "0 */6 * * *",  # Every 6 hours
            "Librarians": "0 */6 * * *",  # Every 6 hours
            "Reporters": "0 */12 * * *",  # Every 12 hours
            "Archivists": "0 1 * * *",  # Daily at 1 AM
            "Utility": "manual"
        }
        return schedules.get(category, "manual")
    
    def _detect_dependencies(self, worker_file):
        """Detect worker dependencies from file content"""
        dependencies = []
        
        if not worker_file.exists():
            return dependencies
        
        try:
            with open(worker_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Detect common dependencies
            if 'GOOGLE_SHEETS_CREDENTIALS' in content or 'gspread' in content:
                dependencies.append("google_sheets_api")
            if 'RCLONE_CONFIG' in content or 'rclone' in content:
                dependencies.append("rclone")
            if 'HF_TOKEN' in content or 'huggingface' in content:
                dependencies.append("huggingface_hub")
            if 'GITHUB_TOKEN' in content or 'PyGithub' in content:
                dependencies.append("github_api")
        
        except Exception:
            pass
        
        return dependencies
    
    def print_status(self):
        """Print current worker constellation status"""
        if not self.manifest_file.exists():
            print("❌ Workers manifest not found. Run --discover first.")
            return
        
        with open(self.manifest_file, 'r') as f:
            manifest = json.load(f)
        
        print("\n" + "=" * 60)
        print("🛠️  WORKERS CONSTELLATION STATUS")
        print("=" * 60)
        print(f"\nLast Discovery: {manifest['discovery_timestamp']}")
        print(f"Total Workers: {manifest['total_workers']}\n")
        
        for category, data in manifest["categories"].items():
            if data["count"] > 0:
                print(f"\n{category} ({data['count']} workers):")
                for worker in data["workers"]:
                    print(f"  • {worker['name']}")
                    print(f"    Source: {worker['source']}")
                    print(f"    Status: {worker['status']}")
                    print(f"    Schedule: {worker['schedule']}")
                    if worker.get("dependencies"):
                        print(f"    Dependencies: {', '.join(worker['dependencies'])}")
        
        print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Workers Constellation Setup")
    parser.add_argument("--discover", action="store_true",
                       help="Discover all workers and create manifest")
    parser.add_argument("--status", action="store_true",
                       help="Show current constellation status")
    
    args = parser.parse_args()
    
    constellation = WorkersConstellation()
    
    if args.discover:
        constellation.discover_workers()
    
    if args.status:
        constellation.print_status()
    
    if not args.discover and not args.status:
        parser.print_help()


if __name__ == "__main__":
    main()
