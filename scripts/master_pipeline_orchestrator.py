#!/usr/bin/env python3
"""
⚡ MASTER PIPELINE ORCHESTRATOR
Citadel Mesh Data Flow & Pipeline Management

Purpose: Orchestrate all data pipelines across the Citadel Mesh
Version: 25.0.OMNI+

Manages data flows:
- GitHub → HuggingFace Spaces
- GDrive → GitHub → HuggingFace
- Local Nodes → GitHub
- District Artifacts → Master Inventory
- RAG Ingestion Pipeline
- Model Registry Pipeline
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logs/pipeline_orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class PipelineStatus(Enum):
    """Pipeline execution status"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PAUSED = "paused"

class Pipeline:
    """Represents a single data pipeline"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.status = PipelineStatus.PENDING
        self.last_run = None
        self.last_success = None
        self.error_count = 0
        self.execution_count = 0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "name": self.name,
            "status": self.status.value,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "error_count": self.error_count,
            "execution_count": self.execution_count,
            "config": self.config
        }

class MasterPipelineOrchestrator:
    """
    Master Pipeline Orchestrator
    
    Coordinates all data pipelines across the Citadel Mesh
    following Cloud-First Authority hierarchy.
    """
    
    def __init__(self, config_path: str = "data/pipelines/pipeline_config.json"):
        self.config_path = config_path
        self.pipelines: Dict[str, Pipeline] = {}
        self.status_file = Path("data/pipelines/pipeline_status.json")
        
        # Create directories
        Path("data/logs").mkdir(parents=True, exist_ok=True)
        Path("data/pipelines").mkdir(parents=True, exist_ok=True)
        
        # Load configuration
        self.load_config()
        
        logger.info("⚡ Master Pipeline Orchestrator initialized")
        logger.info(f"📋 Loaded {len(self.pipelines)} pipelines")
    
    def load_config(self):
        """Load pipeline configuration"""
        default_pipelines = {
            "github_to_hf": {
                "description": "Sync GitHub repositories to HuggingFace Spaces",
                "source": "GitHub (DJ-Goana-Coding)",
                "destination": "HuggingFace Spaces (DJ-Goanna-Coding)",
                "workflow": "sync_to_hf.yml",
                "frequency": "on_push",
                "enabled": True,
                "stages": [
                    "checkout_github",
                    "configure_hf_remote",
                    "push_to_hf"
                ]
            },
            "gdrive_to_github": {
                "description": "Harvest GDrive metadata to GitHub",
                "source": "Google Drive (GENESIS_VAULT 321GB)",
                "destination": "GitHub (mapping-and-inventory)",
                "workflow": "tia_citadel_deep_scan.yml",
                "frequency": "daily",
                "enabled": True,
                "stages": [
                    "validate_rclone",
                    "scan_partitions",
                    "generate_manifests",
                    "commit_to_github"
                ]
            },
            "local_to_github": {
                "description": "Sync local nodes to GitHub",
                "source": "Local Nodes (S10, Oppo, Laptop)",
                "destination": "GitHub",
                "workflow": "bridge_push.yml",
                "frequency": "on_demand",
                "enabled": True,
                "stages": [
                    "scan_local_filesystem",
                    "generate_artifacts",
                    "push_to_github"
                ]
            },
            "district_aggregation": {
                "description": "Aggregate District artifacts to master inventory",
                "source": "District INVENTORY.json files",
                "destination": "master_inventory.json",
                "workflow": "master_harvester.yml",
                "frequency": "every_6_hours",
                "enabled": True,
                "stages": [
                    "discover_districts",
                    "collect_inventories",
                    "merge_and_dedupe",
                    "write_master_inventory"
                ]
            },
            "rag_ingestion": {
                "description": "Ingest master intelligence map into RAG store",
                "source": "master_intelligence_map.txt",
                "destination": "rag_store/ (FAISS vectors)",
                "workflow": "oracle_sync.yml",
                "frequency": "every_12_hours",
                "enabled": True,
                "stages": [
                    "diff_analysis",
                    "load_intelligence_map",
                    "generate_embeddings",
                    "update_faiss_index",
                    "save_metadata"
                ]
            },
            "model_registry": {
                "description": "Update model registry from multiple sources",
                "source": "HuggingFace Hub, Local models, CITADEL_OMEGA",
                "destination": "data/models/models_manifest.json",
                "workflow": "frontier_models_download.yml",
                "frequency": "weekly",
                "enabled": True,
                "stages": [
                    "scan_hf_hub",
                    "scan_local_models",
                    "update_registry",
                    "download_new_models"
                ]
            },
            "worker_constellation": {
                "description": "Manage worker constellation status",
                "source": "Worker services",
                "destination": "worker_status.json",
                "workflow": "workers_constellation_setup.py",
                "frequency": "hourly",
                "enabled": True,
                "stages": [
                    "health_check_workers",
                    "restart_failed_workers",
                    "update_status_file"
                ]
            },
            "trading_garage_sync": {
                "description": "Aggregate trading bots into garages",
                "source": "Multiple bot repositories",
                "destination": "Trading_Garages/",
                "workflow": "trading_garage_collector.py",
                "frequency": "daily",
                "enabled": True,
                "stages": [
                    "discover_bot_repos",
                    "classify_by_strategy",
                    "aggregate_to_garages",
                    "generate_garage_inventory"
                ]
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    pipelines_config = {**default_pipelines, **loaded_config.get("pipelines", {})}
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}, using defaults")
                pipelines_config = default_pipelines
        else:
            pipelines_config = default_pipelines
            # Save default config
            self.save_config({"pipelines": pipelines_config})
        
        # Initialize Pipeline objects
        for name, config in pipelines_config.items():
            self.pipelines[name] = Pipeline(name, config)
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
        logger.info("💾 Configuration saved")
    
    def get_pipeline_dag(self) -> Dict[str, List[str]]:
        """
        Get pipeline DAG (Directed Acyclic Graph)
        
        Returns dependencies between pipelines
        """
        dag = {
            "github_to_hf": [],  # No deps, triggered by GitHub push
            "gdrive_to_github": [],  # No deps, scheduled
            "local_to_github": [],  # No deps, on-demand
            "district_aggregation": ["local_to_github"],  # Depends on districts being updated
            "rag_ingestion": ["gdrive_to_github", "district_aggregation"],  # Needs intelligence map
            "model_registry": [],  # Independent
            "worker_constellation": [],  # Independent health check
            "trading_garage_sync": []  # Independent
        }
        return dag
    
    def get_execution_order(self) -> List[str]:
        """
        Get optimal pipeline execution order based on DAG
        
        Returns topologically sorted pipeline list
        """
        dag = self.get_pipeline_dag()
        
        # Simple topological sort
        in_degree = {pipeline: 0 for pipeline in dag}
        for deps in dag.values():
            for dep in deps:
                in_degree[dep] += 1
        
        queue = [p for p in dag if in_degree[p] == 0]
        result = []
        
        while queue:
            pipeline = queue.pop(0)
            result.append(pipeline)
            
            for other_pipeline, deps in dag.items():
                if pipeline in deps:
                    in_degree[other_pipeline] -= 1
                    if in_degree[other_pipeline] == 0:
                        queue.append(other_pipeline)
        
        return result
    
    def visualize_pipelines(self) -> str:
        """Generate visual representation of pipelines"""
        viz = [
            "# ⚡ CITADEL MESH DATA PIPELINES",
            f"**Generated:** {datetime.now().isoformat()}",
            "",
            "```",
            "┌─────────────────────────────────────────────────────────────┐",
            "│                    DATA FLOW TOPOLOGY                       │",
            "└─────────────────────────────────────────────────────────────┘",
            "",
            "┌──────────────┐",
            "│ Local Nodes  │ (S10, Oppo, Laptop)",
            "└──────┬───────┘",
            "       │ local_to_github",
            "       ↓",
            "┌──────────────┐      ┌─────────────┐",
            "│ Google Drive │      │   GitHub    │ (DJ-Goana-Coding/*)",
            "│ GENESIS_VAULT│----->│ Repositories│",
            "└──────────────┘      └──────┬──────┘",
            "  gdrive_to_github           │ github_to_hf",
            "                             ↓",
            "                      ┌─────────────┐",
            "                      │ HuggingFace │ (DJ-Goanna-Coding/*)",
            "                      │   Spaces    │",
            "                      └─────────────┘",
            "",
            "┌──────────────────────────────────────┐",
            "│        AGGREGATION PIPELINES         │",
            "└──────────────────────────────────────┘",
            "",
            "District INVENTORY.json ──→ master_inventory.json",
            "  (district_aggregation)",
            "",
            "master_intelligence_map.txt ──→ RAG Store (FAISS)",
            "  (rag_ingestion)",
            "",
            "Bot Repos ──→ Trading_Garages/",
            "  (trading_garage_sync)",
            "",
            "HF Hub + Local ──→ models_manifest.json",
            "  (model_registry)",
            "",
            "```",
            "",
            "## PIPELINE STATUS",
            ""
        ]
        
        for name, pipeline in self.pipelines.items():
            status_emoji = {
                PipelineStatus.PENDING: "⏸️",
                PipelineStatus.RUNNING: "🔄",
                PipelineStatus.SUCCEEDED: "✅",
                PipelineStatus.FAILED: "❌",
                PipelineStatus.PAUSED: "⏸️"
            }
            
            emoji = status_emoji.get(pipeline.status, "❓")
            enabled = "🟢" if pipeline.config.get("enabled") else "🔴"
            
            viz.append(f"### {emoji} {enabled} {pipeline.name}")
            viz.append(f"- **Description:** {pipeline.config.get('description')}")
            viz.append(f"- **Source:** {pipeline.config.get('source')}")
            viz.append(f"- **Destination:** {pipeline.config.get('destination')}")
            viz.append(f"- **Frequency:** {pipeline.config.get('frequency')}")
            viz.append(f"- **Executions:** {pipeline.execution_count}")
            viz.append(f"- **Errors:** {pipeline.error_count}")
            viz.append("")
        
        return "\n".join(viz)
    
    def save_status(self):
        """Save pipeline status to file"""
        status = {
            "last_updated": datetime.now().isoformat(),
            "pipelines": {
                name: pipeline.to_dict()
                for name, pipeline in self.pipelines.items()
            }
        }
        
        with open(self.status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        logger.info("💾 Pipeline status saved")
    
    def generate_pipeline_viz_file(self):
        """Generate pipeline visualization markdown file"""
        viz = self.visualize_pipelines()
        
        viz_path = Path("data/pipelines/PIPELINE_TOPOLOGY.md")
        with open(viz_path, 'w') as f:
            f.write(viz)
        
        logger.info(f"📊 Pipeline visualization saved to {viz_path}")


def main():
    """Main entry point"""
    orchestrator = MasterPipelineOrchestrator()
    
    # Generate visualization
    orchestrator.generate_pipeline_viz_file()
    
    # Save status
    orchestrator.save_status()
    
    # Print execution order
    execution_order = orchestrator.get_execution_order()
    logger.info("📋 Optimal pipeline execution order:")
    for i, pipeline in enumerate(execution_order, 1):
        logger.info(f"  {i}. {pipeline}")


if __name__ == "__main__":
    main()
