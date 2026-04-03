#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
PERSONA FILING ROUTER: Data-to-Dataset Bridge (v25.5.OMNI)
═══════════════════════════════════════════════════════════════════════════
Purpose: Route ingested data to appropriate T.I.A. Core Datasets by Persona
Authority: Follows the Constellation persona assignments
═══════════════════════════════════════════════════════════════════════════
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Set
import re

# ═══════════════════════════════════════════════════════════════════════════
# PERSONA CONSTELLATION MAPPING
# ═══════════════════════════════════════════════════════════════════════════

PERSONA_ROUTES = {
    "Pioneer": {
        "node": "Node_02",
        "patterns": [
            r"XRP", r"SOL", r"Solana", r"Ripple",
            r"ABN.*Trade", r"Trade.*Ledger",
            r"trading", r"exchange", r"wallet"
        ],
        "extensions": [".csv", ".json", ".xlsx", ".txt"],
        "keywords": ["trade", "transaction", "ledger", "wallet", "crypto"]
    },
    "Sentinel": {
        "node": "Node_04",
        "patterns": [
            r"Whale.*Alert", r"whale.*watch",
            r"fbi", r"cia", r"intelligence",
            r"security", r"threat", r"alert"
        ],
        "extensions": [".json", ".txt", ".md", ".csv"],
        "keywords": ["whale", "alert", "intel", "security", "monitor"]
    },
    "Oracle": {
        "node": "Node_09",
        "patterns": [
            r"3.*Stories", r"Ancestr", r"Fox.*Core",
            r"Hekate", r"lore", r"mythos",
            r"story", r"narrative", r"legend"
        ],
        "extensions": [".md", ".txt", ".pdf", ".json"],
        "keywords": ["story", "lore", "ancestor", "myth", "legend", "fox", "hekate"]
    },
    "Architect": {
        "node": "Engineering_Vault",
        "patterns": [
            r"Apps.*Script", r"MASTER.*MERGE",
            r"\.gs$", r"automation", r"workflow",
            r"pipeline", r"orchestrat"
        ],
        "extensions": [".gs", ".py", ".sh", ".ps1", ".yaml", ".yml"],
        "keywords": ["script", "automation", "workflow", "pipeline", "merge", "tool"]
    },
    "Media": {
        "node": "Media_Vault",
        "patterns": [
            r"music", r"video", r"art", r"image",
            r"audio", r"visual"
        ],
        "extensions": [".mp3", ".wav", ".mp4", ".jpg", ".png", ".gif", ".svg"],
        "keywords": ["music", "video", "art", "image", "audio", "photo"]
    },
    "Models": {
        "node": "Model_Registry",
        "patterns": [
            r"model", r"checkpoint", r"weights",
            r"neural", r"\.safetensors", r"\.ckpt"
        ],
        "extensions": [".safetensors", ".ckpt", ".pt", ".pth", ".bin", ".onnx"],
        "keywords": ["model", "checkpoint", "weights", "neural", "trained"]
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# FILING LOGIC
# ═══════════════════════════════════════════════════════════════════════════

class PersonaFilingRouter:
    def __init__(self, ingestion_root: str = "/data/total_ingestion", output_root: str = "/data/datasets"):
        self.ingestion_root = Path(ingestion_root)
        self.output_root = Path(output_root)
        self.stats = {
            "total_files": 0,
            "routed_files": 0,
            "unrouted_files": 0,
            "by_persona": {}
        }
        
        # Create output directories
        for persona, config in PERSONA_ROUTES.items():
            node_path = self.output_root / config["node"]
            node_path.mkdir(parents=True, exist_ok=True)
            self.stats["by_persona"][persona] = 0
    
    def classify_file(self, file_path: Path) -> Set[str]:
        """Classify file into one or more persona categories"""
        matches = set()
        file_name = file_path.name.lower()
        file_ext = file_path.suffix.lower()
        
        # Read first few lines if text file
        content_sample = ""
        if file_ext in [".txt", ".md", ".json", ".csv", ".py", ".js", ".gs"]:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content_sample = f.read(1000).lower()
            except Exception:
                pass
        
        # Match against persona patterns
        for persona, config in PERSONA_ROUTES.items():
            # Check extension
            if file_ext in config["extensions"]:
                # Check patterns
                for pattern in config["patterns"]:
                    if re.search(pattern, file_name, re.IGNORECASE):
                        matches.add(persona)
                        break
                
                # Check keywords in content
                if not matches and content_sample:
                    for keyword in config["keywords"]:
                        if keyword in content_sample or keyword in file_name:
                            matches.add(persona)
                            break
        
        return matches
    
    def route_file(self, file_path: Path):
        """Route file to appropriate persona datasets"""
        self.stats["total_files"] += 1
        
        # Classify the file
        personas = self.classify_file(file_path)
        
        if personas:
            self.stats["routed_files"] += 1
            
            # Copy to each matching persona directory
            for persona in personas:
                node = PERSONA_ROUTES[persona]["node"]
                dest_dir = self.output_root / node
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                # Preserve directory structure
                rel_path = file_path.relative_to(self.ingestion_root)
                dest_path = dest_dir / rel_path
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Copy file
                try:
                    shutil.copy2(file_path, dest_path)
                    self.stats["by_persona"][persona] += 1
                    print(f"✅ {persona}: {rel_path}")
                except Exception as e:
                    print(f"❌ Error routing {file_path}: {e}")
        else:
            self.stats["unrouted_files"] += 1
            # Copy to general storage
            general_dir = self.output_root / "general"
            general_dir.mkdir(parents=True, exist_ok=True)
            rel_path = file_path.relative_to(self.ingestion_root)
            dest_path = general_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(file_path, dest_path)
                print(f"📦 General: {rel_path}")
            except Exception as e:
                print(f"❌ Error routing {file_path}: {e}")
    
    def scan_and_route(self):
        """Scan ingestion directory and route all files"""
        print("═══════════════════════════════════════════════════════════════════════════")
        print("🗂️ PERSONA FILING ROUTER: Data-to-Dataset Bridge")
        print("═══════════════════════════════════════════════════════════════════════════")
        print(f"Source: {self.ingestion_root}")
        print(f"Target: {self.output_root}")
        print("")
        
        # Walk all files in ingestion directory
        for file_path in self.ingestion_root.rglob("*"):
            if file_path.is_file():
                self.route_file(file_path)
        
        # Print summary
        print("")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("📊 Filing Summary")
        print("═══════════════════════════════════════════════════════════════════════════")
        print(f"Total Files Processed: {self.stats['total_files']}")
        print(f"Routed to Personas: {self.stats['routed_files']}")
        print(f"General Storage: {self.stats['unrouted_files']}")
        print("")
        print("By Persona:")
        for persona, count in sorted(self.stats["by_persona"].items()):
            node = PERSONA_ROUTES[persona]["node"]
            print(f"  {persona:12} ({node:20}): {count:6} files")
        print("═══════════════════════════════════════════════════════════════════════════")
        
        # Save manifest
        manifest_path = self.output_root / "filing_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(self.stats, f, indent=2)
        print(f"✅ Manifest saved: {manifest_path}")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    
    ingestion_root = sys.argv[1] if len(sys.argv) > 1 else "/data/total_ingestion"
    output_root = sys.argv[2] if len(sys.argv) > 2 else "/data/datasets"
    
    router = PersonaFilingRouter(ingestion_root, output_root)
    router.scan_and_route()
    
    print("")
    print("🎯 Next Steps:")
    print("  1. Review filed datasets in /data/datasets/")
    print("  2. Trigger Forever Learning cycle in TIA-ARCHITECT-CORE")
    print("  3. Update RAG store with new embeddings")
    print("  4. Version bump the intelligence mesh")
    print("")
    print("🦎 Weld. Pulse. Ignite.")
