#!/usr/bin/env python3
"""
TIA INTEGRATION COORDINATOR
Manages TIA-ARCHITECT-CORE integration with Mapping-and-Inventory
Handles space repair, model/dataset sync, and L4 GPU operations

Usage:
    python tia_coordinator.py --check-space
    python tia_coordinator.py --sync-models
    python tia_coordinator.py --sync-personas
    python tia_coordinator.py --full-sync
"""

import json
import argparse
from pathlib import Path
from datetime import datetime


class TIAIntegrationCoordinator:
    """Coordinates TIA-ARCHITECT-CORE integration"""
    
    def __init__(self):
        self.mapping_root = Path(".")
        self.tia_sync_manifest = Path("TIA_SYNC_STATUS.json")
    
    def check_space_status(self):
        """Check TIA Space status"""
        print("\n🤖 CHECKING TIA-ARCHITECT-CORE SPACE STATUS")
        print("=" * 60)
        
        status = {
            "check_timestamp": datetime.utcnow().isoformat() + "Z",
            "space_id": "DJ-Goanna-Coding/TIA-ARCHITECT-CORE",
            "components": {}
        }
        
        # Check if models manifest exists
        models_file = Path("data/models/models_manifest.json")
        if models_file.exists():
            with open(models_file, 'r') as f:
                models_data = json.load(f)
            
            status["components"]["models"] = {
                "available": True,
                "total": models_data.get("total_models", 0),
                "categories": list(models_data.get("categories", {}).keys())
            }
            print(f"✅ Models: {models_data.get('total_models', 0)} available")
        else:
            status["components"]["models"] = {"available": False}
            print("⚠️  Models: Not found")
        
        # Check workers
        workers_file = Path("data/workers/workers_manifest.json")
        if workers_file.exists():
            with open(workers_file, 'r') as f:
                workers_data = json.load(f)
            
            status["components"]["workers"] = {
                "available": True,
                "total": workers_data.get("total_workers", 0)
            }
            print(f"✅ Workers: {workers_data.get('total_workers', 0)} available")
        else:
            status["components"]["workers"] = {"available": False}
            print("⚠️  Workers: Not found")
        
        # Check intelligence map
        intel_map = Path("master_intelligence_map.txt")
        if intel_map.exists():
            size_kb = intel_map.stat().st_size / 1024
            status["components"]["intelligence_map"] = {
                "available": True,
                "size_kb": size_kb
            }
            print(f"✅ Intelligence Map: {size_kb:.1f} KB")
        else:
            status["components"]["intelligence_map"] = {"available": False}
            print("⚠️  Intelligence Map: Not found")
        
        # Save status
        with open(self.tia_sync_manifest, 'w') as f:
            json.dump(status, f, indent=2)
        
        print(f"\n✅ Status saved: {self.tia_sync_manifest}")
        return status
    
    def sync_models(self):
        """Prepare models for TIA sync"""
        print("\n📦 PREPARING MODELS FOR TIA SYNC")
        print("=" * 60)
        
        models_file = Path("data/models/models_manifest.json")
        if not models_file.exists():
            print("❌ Models manifest not found")
            return False
        
        with open(models_file, 'r') as f:
            models_manifest = json.load(f)
        
        # Create TIA-optimized model list
        tia_models = {
            "for_tia": True,
            "sync_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_models": models_manifest.get("total_models", 0),
            "recommended_for_l4": []
        }
        
        # Select models suitable for L4 GPU
        for category, cat_data in models_manifest.get("categories", {}).items():
            for model in cat_data.get("models", []):
                size_mb = model.get("size_bytes", 0) / (1024 * 1024)
                
                # Recommend models under 5GB for L4
                if size_mb < 5000:
                    tia_models["recommended_for_l4"].append({
                        "name": Path(model.get("path", "")).name,
                        "category": category,
                        "size_mb": round(size_mb, 2),
                        "path": model.get("path", "")
                    })
        
        # Save TIA model recommendations
        output_file = Path("data/models/tia_model_recommendations.json")
        with open(output_file, 'w') as f:
            json.dump(tia_models, f, indent=2)
        
        print(f"✅ {len(tia_models['recommended_for_l4'])} models suitable for L4 GPU")
        print(f"   Saved to: {output_file}")
        
        return True
    
    def sync_personas(self):
        """Create personas dataset for TIA"""
        print("\n🎭 CREATING PERSONAS DATASET FOR TIA")
        print("=" * 60)
        
        personas = {
            "dataset_version": "1.0.0",
            "created_for": "TIA-ARCHITECT-CORE",
            "created": datetime.utcnow().isoformat() + "Z",
            "personas": [
                {
                    "id": "wizard_mafia",
                    "name": "Wizard Mafia",
                    "role": "Centralized Power & Oversight",
                    "pillar": "LORE",
                    "capabilities": ["system_oversight", "authority_enforcement", "strategic_planning"],
                    "personality": "Authoritative, strategic, decisive",
                    "status": "active"
                },
                {
                    "id": "tiny_mystic",
                    "name": "The Tiny Mystic",
                    "role": "Pattern Recognition",
                    "pillar": "LORE",
                    "capabilities": ["pattern_analysis", "anomaly_detection", "insight_generation"],
                    "personality": "Observant, analytical, intuitive",
                    "status": "active"
                },
                {
                    "id": "curious_magpie",
                    "name": "Curious Magpie",
                    "role": "Evidence Gathering",
                    "pillar": "LORE",
                    "capabilities": ["data_collection", "artifact_discovery", "investigation"],
                    "personality": "Inquisitive, thorough, persistent",
                    "status": "active"
                },
                {
                    "id": "spiritua_hanson",
                    "name": "Spiritua Hanson",
                    "role": "Integrity Verification",
                    "pillar": "LORE",
                    "capabilities": ["validation", "authentication", "compliance_checking"],
                    "personality": "Precise, trustworthy, meticulous",
                    "status": "active"
                },
                {
                    "id": "the_surveyor",
                    "name": "The Surveyor",
                    "role": "Mapping Hub Harvester",
                    "pillar": "HARVESTER",
                    "capabilities": ["district_scanning", "artifact_extraction", "inventory_building"],
                    "personality": "Methodical, comprehensive, organized",
                    "status": "active"
                },
                {
                    "id": "the_oracle",
                    "name": "The Oracle",
                    "role": "TIA Reasoning Engine",
                    "pillar": "REASONING",
                    "capabilities": ["rag_processing", "embedding_generation", "intelligence_synthesis"],
                    "personality": "Wise, analytical, synthesizing",
                    "status": "active"
                },
                {
                    "id": "the_bridge",
                    "name": "The Bridge",
                    "role": "Mobile Scout",
                    "pillar": "BRIDGE",
                    "capabilities": ["filesystem_scanning", "telemetry", "remote_sync"],
                    "personality": "Adaptive, mobile, communicative",
                    "status": "active"
                },
                {
                    "id": "the_architect",
                    "name": "The Architect",
                    "role": "Citadel Systems Overseer",
                    "pillar": "ARCHITECT",
                    "capabilities": ["workflow_generation", "protocol_enforcement", "mesh_coordination"],
                    "personality": "Strategic, systematic, commanding",
                    "status": "active"
                }
            ]
        }
        
        personas["total_personas"] = len(personas["personas"])
        
        # Save personas dataset
        personas_file = Path("data/personas/ai_personas_for_tia.json")
        personas_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(personas_file, 'w') as f:
            json.dump(personas, f, indent=2)
        
        print(f"✅ Created {personas['total_personas']} AI personas")
        for persona in personas["personas"]:
            print(f"   🎭 {persona['name']} - {persona['role']}")
        
        print(f"\n   Saved to: {personas_file}")
        return True
    
    def full_sync(self):
        """Run complete TIA sync"""
        print("\n" + "=" * 60)
        print("🔄 FULL TIA INTEGRATION SYNC")
        print("=" * 60)
        
        results = {
            "space_check": False,
            "models_sync": False,
            "personas_sync": False
        }
        
        # Run all sync operations
        status = self.check_space_status()
        results["space_check"] = True
        
        if self.sync_models():
            results["models_sync"] = True
        
        if self.sync_personas():
            results["personas_sync"] = True
        
        # Summary
        print("\n" + "=" * 60)
        print("✅ FULL SYNC COMPLETE")
        print("=" * 60)
        
        for operation, success in results.items():
            status_icon = "✅" if success else "❌"
            print(f"{status_icon} {operation.replace('_', ' ').title()}")
        
        print("\nNext: Run tia_space_repair_sync.yml workflow to push to TIA Space")
        print("=" * 60)
        
        return all(results.values())


def main():
    parser = argparse.ArgumentParser(description="TIA Integration Coordinator")
    parser.add_argument("--check-space", action="store_true",
                       help="Check TIA Space status")
    parser.add_argument("--sync-models", action="store_true",
                       help="Prepare models for TIA")
    parser.add_argument("--sync-personas", action="store_true",
                       help="Create personas dataset")
    parser.add_argument("--full-sync", action="store_true",
                       help="Run complete sync")
    
    args = parser.parse_args()
    
    coordinator = TIAIntegrationCoordinator()
    
    if args.check_space:
        coordinator.check_space_status()
    
    if args.sync_models:
        coordinator.sync_models()
    
    if args.sync_personas:
        coordinator.sync_personas()
    
    if args.full_sync:
        coordinator.full_sync()
    
    if not any([args.check_space, args.sync_models, args.sync_personas, args.full_sync]):
        parser.print_help()


if __name__ == "__main__":
    main()
