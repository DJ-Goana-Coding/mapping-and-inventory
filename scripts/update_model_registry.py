#!/usr/bin/env python3
"""
📋 AETHER HARVEST PROTOCOL - Model Registry Updater
Updates master model registry with new frontier model discoveries
Author: Citadel Architect v25.0.OMNI++
Date: April 2026
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

print("=" * 80)
print("📋 AETHER HARVEST PROTOCOL - Model Registry Updater")
print("=" * 80)
print()

BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "data" / "models"
DISCOVERY_MANIFEST = BASE_DIR / "data" / "AETHER_HARVEST_DISCOVERY_MANIFEST.json"

# Load discovery manifest
if DISCOVERY_MANIFEST.exists():
    with open(DISCOVERY_MANIFEST) as f:
        DISCOVERIES = json.load(f)
    print(f"✅ Loaded discovery manifest: {len(DISCOVERIES.get('discoveries', {}).get('frontier_models', {}).get('categories', {}))} categories")
else:
    print(f"⚠️  Discovery manifest not found: {DISCOVERY_MANIFEST}")
    DISCOVERIES = {}

def scan_downloaded_models() -> Dict:
    """Scan the models directory for actually downloaded models"""
    
    downloaded = {
        "Core": [],
        "Utility": [],
        "Research": [],
        "Lore": []
    }
    
    print(f"🔍 Scanning {MODELS_DIR} for downloaded models...")
    print()
    
    for category in ["Core", "Utility", "Research", "Lore"]:
        category_dir = MODELS_DIR / category
        if not category_dir.exists():
            continue
        
        for model_dir in category_dir.iterdir():
            if not model_dir.is_dir() or model_dir.name.startswith('.'):
                continue
            
            # Check if directory has actual model files
            has_content = False
            model_files = []
            
            # Look for model file types
            for pattern in ['*.bin', '*.safetensors', '*.pt', '*.pth', '*.onnx', 'config.json', 'pytorch_model.bin']:
                files = list(model_dir.rglob(pattern))
                if files:
                    has_content = True
                    model_files.extend([f.name for f in files[:3]])  # First 3 files
            
            if has_content or len(list(model_dir.rglob('*'))) > 5:  # Has content or significant files
                size = sum(f.stat().st_size for f in model_dir.rglob('*') if f.is_file())
                size_mb = size / (1024 * 1024)
                
                downloaded[category].append({
                    "local_dir": model_dir.name,
                    "full_path": str(model_dir),
                    "size_mb": round(size_mb, 2),
                    "file_count": len(list(model_dir.rglob('*'))),
                    "sample_files": model_files[:5],
                    "verified": has_content
                })
                
                print(f"   ✓ {category}/{model_dir.name} ({size_mb:.1f} MB, {len(list(model_dir.rglob('*')))} files)")
    
    return downloaded

def create_master_registry(downloaded_models: Dict) -> Dict:
    """Create comprehensive master model registry"""
    
    registry = {
        "version": "2.0.0",
        "protocol": "AETHER_HARVEST",
        "generated": datetime.now().isoformat(),
        "last_update": datetime.now().isoformat(),
        "source": "Aether Harvest Protocol - April 2026 Web Reconnaissance",
        
        "classifications": {
            "Core": {
                "description": "Foundation models for primary reasoning and generation",
                "priority": "CRITICAL",
                "examples": ["Gemma 4", "Qwen 3.5", "LLaMA 4"]
            },
            "Utility": {
                "description": "Specialized models for embeddings, cost-performance, specific tasks",
                "priority": "HIGH",
                "examples": ["DeepSeek V4", "BGE embeddings", "E5 embeddings"]
            },
            "Research": {
                "description": "Experimental and research-grade models",
                "priority": "MEDIUM",
                "examples": ["NVIDIA Nemotron 3", "MAGNET", "Academic models"]
            },
            "Lore": {
                "description": "Creative models for video, audio, persona generation",
                "priority": "MEDIUM",
                "examples": ["Text-to-Video", "Text-to-Speech", "Avatar generation"]
            },
            "Genetics": {
                "description": "Reserved for future genetic algorithm and evolutionary models",
                "priority": "LOW",
                "examples": ["Genetic algorithms", "Evolutionary strategies"]
            }
        },
        
        "discovered_models": {},
        "downloaded_models": {},
        "api_only_models": {},
        
        "statistics": {
            "total_discovered": 0,
            "total_downloaded": 0,
            "total_api_only": 0,
            "by_category": {
                "discovered": {},
                "downloaded": {}
            },
            "total_size_gb": 0
        },
        
        "citadel_omega_models": {
            "note": "Existing CITADEL_OMEGA trading models (already integrated)",
            "models": [
                "FinBERT (sentiment)",
                "CryptoBERT (crypto sentiment)",
                "Twitter RoBERTa (social sentiment)",
                "Sentence Transformers MiniLM (embeddings)",
                "Sentence Transformers MPNet (embeddings)",
                "DistilGPT2 (text generation)",
                "FLAN-T5 Small (Q&A)"
            ],
            "location": "CITADEL_OMEGA/models/pretrained/",
            "status": "Active in trading operations"
        }
    }
    
    # Add discovered models from manifest
    if DISCOVERIES:
        frontier_models = DISCOVERIES.get('discoveries', {}).get('frontier_models', {}).get('categories', {})
        
        for category, models_list in frontier_models.items():
            if category == "API_Only":
                registry["api_only_models"] = {
                    m["name"]: {
                        "provider": m["provider"],
                        "capabilities": m["capabilities"],
                        "priority": m["priority"],
                        "status": m["status"]
                    }
                    for m in models_list
                }
                registry["statistics"]["total_api_only"] = len(models_list)
            else:
                registry["discovered_models"][category] = models_list
                registry["statistics"]["total_discovered"] += len(models_list)
                registry["statistics"]["by_category"]["discovered"][category] = len(models_list)
    
    # Add downloaded models
    total_size_bytes = 0
    for category, models in downloaded_models.items():
        if models:
            registry["downloaded_models"][category] = models
            registry["statistics"]["by_category"]["downloaded"][category] = len(models)
            registry["statistics"]["total_downloaded"] += len(models)
            total_size_bytes += sum(m["size_mb"] * 1024 * 1024 for m in models)
    
    registry["statistics"]["total_size_gb"] = round(total_size_bytes / (1024**3), 2)
    
    return registry

def save_registry(registry: Dict):
    """Save registry to multiple locations"""
    
    # Main registry location
    main_registry = MODELS_DIR / "model_registry.json"
    with open(main_registry, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"✅ Main registry saved: {main_registry}")
    
    # Backup to root data directory
    backup_registry = BASE_DIR / "data" / "master_model_registry.json"
    with open(backup_registry, 'w') as f:
        json.dump(registry, f, indent=2)
    print(f"✅ Backup registry saved: {backup_registry}")
    
    # Create summary file
    summary = {
        "version": registry["version"],
        "generated": registry["generated"],
        "total_discovered": registry["statistics"]["total_discovered"],
        "total_downloaded": registry["statistics"]["total_downloaded"],
        "total_api_only": registry["statistics"]["total_api_only"],
        "total_size_gb": registry["statistics"]["total_size_gb"],
        "classifications": list(registry["classifications"].keys()),
        "registry_location": str(main_registry)
    }
    
    summary_file = MODELS_DIR / "registry_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    print(f"✅ Summary saved: {summary_file}")

def generate_readme():
    """Generate README for models directory"""
    
    readme_content = """# Frontier Models Registry (April 2026)

## Overview

This directory contains frontier AI models discovered via the Aether Harvest Protocol web reconnaissance mission (April 2026).

## Directory Structure

```
data/models/
├── Core/                    # Foundation models (Gemma 4, Qwen 3.5, LLaMA 4)
├── Utility/                 # Embeddings, cost-performance models
├── Research/                # Experimental models (Nemotron 3, MAGNET)
├── Lore/                    # Creative models (text-to-video, TTS)
├── model_registry.json      # Complete model registry
├── api_models_registry.json # API-only models (Claude, GPT-5, Gemini)
└── registry_summary.json    # Quick statistics

```

## Model Classifications

### Core (Foundation Models)
- **Gemma 4**: Google's multimodal edge-ready model (2B, 4B, 26B, 31B variants)
- **Qwen 3.5**: Alibaba's multilingual code specialist
- **LLaMA 4**: Meta's open-source foundation model (expected 2026)

### Utility (Specialized Models)
- **DeepSeek V4**: Cost-performance leader for coding
- **BGE Large EN v1.5**: SOTA embeddings for RAG
- **E5 Large v2**: Multilingual embeddings
- **All-MPNet Base v2**: High-quality sentence embeddings

### Research (Experimental)
- **NVIDIA Nemotron 3**: Research-grade efficient model
- **MAGNET**: Autonomous mesh network model system

### Lore (Creative)
- **Text-to-Video**: CogVideoX, HunyuanVideo
- **Text-to-Speech**: HumeAI Tada series

## Download Models

```bash
# Download all frontier models
python scripts/download_frontier_models_2026.py

# View registry
cat data/models/model_registry.json
```

## API-Only Models

These models are available via API only (not downloadable):
- **Claude Opus 4.6** (Anthropic)
- **GPT-5.4** (OpenAI)
- **Gemini 3.1 Pro** (Google)

See `api_models_registry.json` for API endpoints and documentation.

## Usage

### Load a Model
```python
from transformers import AutoModel, AutoTokenizer

# Example: Load Qwen 3.5
model = AutoModel.from_pretrained("data/models/Core/qwen-3.5-7b-instruct")
tokenizer = AutoTokenizer.from_pretrained("data/models/Core/qwen-3.5-7b-instruct")
```

### Use Embeddings
```python
from sentence_transformers import SentenceTransformer

# Load BGE embeddings
model = SentenceTransformer("data/models/Utility/embeddings/bge-large-en-v1.5")
embeddings = model.encode(["Hello world", "Frontier AI models"])
```

## Citadel Integration

### Districts
- **D03 (MEMORY)**: Embeddings, RAG infrastructure
- **TIA-ARCHITECT-CORE**: Gemma 4, Qwen 3.5 for reasoning
- **AETHER-NEXUS**: Model hosting and inference on HF Space

### Sync Targets
- **FLEET-WATCHER**: Model deployment monitoring
- **AETHER-NEXUS**: Inference and demo hosting

---

*Generated by Aether Harvest Protocol v25.0.OMNI++*
"""
    
    readme_file = MODELS_DIR / "README.md"
    with open(readme_file, 'w') as f:
        f.write(readme_content)
    print(f"✅ README generated: {readme_file}")

def main():
    """Main orchestration"""
    
    print(f"📁 Models directory: {MODELS_DIR}")
    print()
    
    # Scan for downloaded models
    downloaded = scan_downloaded_models()
    
    print()
    print("=" * 80)
    print("📊 DOWNLOADED MODELS SUMMARY")
    print("=" * 80)
    for category, models in downloaded.items():
        print(f"\n📦 {category}: {len(models)} models")
        for model in models:
            print(f"   ✓ {model['local_dir']} ({model['size_mb']} MB)")
    
    print()
    
    # Create master registry
    print("=" * 80)
    print("📋 CREATING MASTER REGISTRY")
    print("=" * 80)
    print()
    
    registry = create_master_registry(downloaded)
    
    # Save registry
    save_registry(registry)
    
    # Generate README
    print()
    generate_readme()
    
    # Final summary
    print()
    print("=" * 80)
    print("✅ MODEL REGISTRY UPDATE COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Statistics:")
    print(f"   Total discovered: {registry['statistics']['total_discovered']}")
    print(f"   Total downloaded: {registry['statistics']['total_downloaded']}")
    print(f"   Total API-only: {registry['statistics']['total_api_only']}")
    print(f"   Total size: {registry['statistics']['total_size_gb']} GB")
    print()
    print(f"📁 Registry Files:")
    print(f"   - data/models/model_registry.json")
    print(f"   - data/models/api_models_registry.json")
    print(f"   - data/models/registry_summary.json")
    print(f"   - data/models/README.md")
    print(f"   - data/master_model_registry.json (backup)")
    print()
    print("🚀 Next Steps:")
    print("   1. Review registry: cat data/models/model_registry.json")
    print("   2. Download missing models: python scripts/download_frontier_models_2026.py")
    print("   3. Integrate into RAG: python scripts/rag_ingest.py")
    print("   4. Deploy to AETHER-NEXUS HF Space")
    print()

if __name__ == "__main__":
    main()
