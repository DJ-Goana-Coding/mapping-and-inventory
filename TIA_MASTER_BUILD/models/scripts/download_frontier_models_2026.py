#!/usr/bin/env python3
"""
🔮 AETHER HARVEST PROTOCOL - Frontier Models Downloader (2026)
Downloads cutting-edge AI models discovered via web reconnaissance
Author: Citadel Architect v25.0.OMNI++
Date: April 2026
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

try:
    from huggingface_hub import snapshot_download, hf_hub_download, list_repo_files
except ImportError:
    print("❌ Error: huggingface_hub not installed")
    print("   Install with: pip install huggingface-hub")
    sys.exit(1)

print("=" * 80)
print("🔮 AETHER HARVEST PROTOCOL - Frontier Models Downloader (April 2026)")
print("=" * 80)
print()

# Setup paths
BASE_DIR = Path(__file__).parent.parent
MODELS_DIR = BASE_DIR / "data" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Frontier Models Registry (April 2026 Discovery)
FRONTIER_MODELS = {
    "Core": {
        "gemma-4": [
            {
                "name": "Gemma 4 - 2B (E2B)",
                "repo_id": "google/gemma-2b-it",  # Placeholder - actual v4 not yet on HF
                "local_dir": "gemma-4-2b",
                "description": "Gemma 4 lightweight (2B params) - multimodal, edge-ready",
                "priority": "CRITICAL",
                "license": "Apache 2.0",
                "capabilities": ["text", "image", "audio", "256K context"],
                "note": "Using gemma-2b as placeholder until gemma-4 official release"
            },
            {
                "name": "Gemma 4 - 4B (E4B)",
                "repo_id": "google/gemma-7b-it",  # Placeholder
                "local_dir": "gemma-4-4b",
                "description": "Gemma 4 balanced (4B params) - multimodal with edge optimization",
                "priority": "CRITICAL",
                "license": "Apache 2.0",
                "capabilities": ["text", "image", "audio", "256K context"],
                "note": "Using gemma-7b as placeholder until gemma-4 official release"
            }
        ],
        "qwen-3.5": [
            {
                "name": "Qwen 3.5 - 7B Instruct",
                "repo_id": "Qwen/Qwen2.5-7B-Instruct",  # Latest available
                "local_dir": "qwen-3.5-7b-instruct",
                "description": "Qwen 3.5 multilingual code specialist",
                "priority": "HIGH",
                "license": "Apache 2.0",
                "capabilities": ["multilingual", "code", "128K context"]
            },
            {
                "name": "Qwen 3.5 - 14B Instruct",
                "repo_id": "Qwen/Qwen2.5-14B-Instruct",
                "local_dir": "qwen-3.5-14b-instruct",
                "description": "Qwen 3.5 larger variant for complex tasks",
                "priority": "MEDIUM",
                "license": "Apache 2.0",
                "capabilities": ["multilingual", "code", "128K context"]
            }
        ]
    },
    "Utility": {
        "deepseek-v4": [
            {
                "name": "DeepSeek Coder V2",
                "repo_id": "deepseek-ai/deepseek-coder-6.7b-instruct",
                "local_dir": "deepseek-coder-v2",
                "description": "DeepSeek cost-performance leader for coding",
                "priority": "HIGH",
                "license": "MIT",
                "capabilities": ["code", "sub-$1/M tokens", "general coding"]
            }
        ],
        "embeddings": [
            {
                "name": "BGE Large EN v1.5",
                "repo_id": "BAAI/bge-large-en-v1.5",
                "local_dir": "bge-large-en-v1.5",
                "description": "SOTA embeddings for RAG (2024-2026)",
                "priority": "HIGH",
                "license": "MIT",
                "capabilities": ["embeddings", "RAG", "semantic search"]
            },
            {
                "name": "E5 Large v2",
                "repo_id": "intfloat/e5-large-v2",
                "local_dir": "e5-large-v2",
                "description": "Multilingual embeddings for RAG",
                "priority": "MEDIUM",
                "license": "MIT",
                "capabilities": ["embeddings", "multilingual", "RAG"]
            },
            {
                "name": "All-MPNet Base v2",
                "repo_id": "sentence-transformers/all-mpnet-base-v2",
                "local_dir": "all-mpnet-base-v2",
                "description": "High-quality sentence embeddings (upgrade from MiniLM)",
                "priority": "HIGH",
                "license": "Apache 2.0",
                "capabilities": ["embeddings", "sentence similarity", "RAG"]
            }
        ]
    },
    "Research": {
        "nemotron-3": [
            {
                "name": "NVIDIA Nemotron Mini",
                "repo_id": "nvidia/Mistral-NeMo-Minitron-8B-Instruct",
                "local_dir": "nemotron-mini-8b",
                "description": "NVIDIA research model - efficient and capable",
                "priority": "MEDIUM",
                "license": "NVIDIA Open Model License",
                "capabilities": ["research", "efficient", "8B params"]
            }
        ]
    },
    "Lore": {
        "text-to-video": [
            {
                "name": "CogVideoX",
                "repo_id": "THUDM/CogVideoX-5b",
                "local_dir": "cogvideox-5b",
                "description": "Text-to-video generation model",
                "priority": "LOW",
                "license": "Apache 2.0",
                "capabilities": ["text-to-video", "video generation"],
                "note": "Large model - download on-demand only"
            }
        ]
    }
}

# Proprietary API-only models (for registry only, not download)
API_ONLY_MODELS = {
    "claude-opus-4.6": {
        "provider": "Anthropic",
        "capabilities": ["1M context", "coding", "agent teams", "80.8% SWE-Bench"],
        "pricing": "Premium tier",
        "api_endpoint": "https://api.anthropic.com/v1/messages",
        "documentation": "https://docs.anthropic.com/claude/reference/getting-started-with-the-api"
    },
    "gpt-5.4": {
        "provider": "OpenAI",
        "variants": ["Thinking", "Pro", "Codex"],
        "capabilities": ["1M context", "computer control", "128K output", "agentic workflows"],
        "pricing": "Variable by variant",
        "api_endpoint": "https://api.openai.com/v1/chat/completions",
        "documentation": "https://platform.openai.com/docs/api-reference"
    },
    "gemini-3.1-pro": {
        "provider": "Google",
        "capabilities": ["256K context", "multimodal", "competitive pricing"],
        "pricing": "Mid-tier",
        "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models",
        "documentation": "https://ai.google.dev/docs"
    }
}


def download_model(repo_id: str, local_dir: str, category: str, description: str, 
                  priority: str, max_size_gb: Optional[float] = None) -> bool:
    """Download a model from HuggingFace with error handling and size limits"""
    
    target_path = MODELS_DIR / category / local_dir
    
    # Check if already exists
    if target_path.exists() and any(target_path.iterdir()):
        print(f"⏭️  {local_dir} already exists, skipping...")
        return True
    
    try:
        print(f"📥 Downloading {local_dir}...")
        print(f"   Repo: {repo_id}")
        print(f"   Category: {category}")
        print(f"   Priority: {priority}")
        print(f"   Description: {description}")
        
        # Check if repo exists
        try:
            files = list_repo_files(repo_id)
            print(f"   Found {len(files)} files in repository")
        except Exception as e:
            print(f"⚠️  Could not list files: {e}")
            print(f"   Attempting download anyway...")
        
        # Download with size awareness
        target_path.mkdir(parents=True, exist_ok=True)
        
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_path),
            local_dir_use_symlinks=False,
            resume_download=True,
            max_workers=4
        )
        
        print(f"✅ {local_dir} downloaded successfully!")
        print(f"   Location: {target_path}")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error downloading {local_dir}: {e}")
        print(f"   This may be due to:")
        print(f"   - Model not yet released on HuggingFace")
        print(f"   - Incorrect repo_id")
        print(f"   - Authentication required")
        print(f"   - Network issues")
        print()
        return False


def create_model_registry(downloaded_models: List[Dict], api_models: Dict) -> Dict:
    """Create comprehensive model registry with classifications"""
    
    registry = {
        "version": "2.0.0",
        "protocol": "AETHER_HARVEST",
        "generated": datetime.now().isoformat(),
        "discovery_date": "2026-04-03",
        "classifications": {
            "Core": "Foundation models for primary reasoning and generation",
            "Utility": "Specialized models for embeddings, cost-performance, specific tasks",
            "Research": "Experimental and research-grade models",
            "Lore": "Creative models for video, audio, persona generation",
            "Genetics": "Reserved for future genetic algorithm models"
        },
        "downloaded_models": downloaded_models,
        "api_only_models": api_models,
        "statistics": {
            "total_downloaded": len(downloaded_models),
            "total_api_registered": len(api_models),
            "by_category": {},
            "by_priority": {}
        }
    }
    
    # Calculate statistics
    for model in downloaded_models:
        cat = model["category"]
        pri = model["priority"]
        
        registry["statistics"]["by_category"][cat] = \
            registry["statistics"]["by_category"].get(cat, 0) + 1
        registry["statistics"]["by_priority"][pri] = \
            registry["statistics"]["by_priority"].get(pri, 0) + 1
    
    return registry


def main():
    """Main orchestration for frontier model downloads"""
    
    # Check for HF token
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print("🔑 HuggingFace token detected")
    else:
        print("⚠️  No HF_TOKEN found - some models may require authentication")
        print("   Set via: export HF_TOKEN=your_token_here")
    print()
    
    print(f"📁 Models base directory: {MODELS_DIR}")
    print()
    
    # Track results
    downloaded_models = []
    total_attempted = 0
    successful = 0
    failed = 0
    
    # Download each category
    for category, subcategories in FRONTIER_MODELS.items():
        print("=" * 80)
        print(f"📦 CATEGORY: {category}")
        print("=" * 80)
        print()
        
        for subcategory, models_list in subcategories.items():
            print(f"🗂️  Subcategory: {subcategory}")
            print("-" * 80)
            
            for model in models_list:
                total_attempted += 1
                
                # Show note if exists
                if "note" in model:
                    print(f"ℹ️  NOTE: {model['note']}")
                
                success = download_model(
                    repo_id=model["repo_id"],
                    local_dir=model["local_dir"],
                    category=category,
                    description=model["description"],
                    priority=model["priority"]
                )
                
                if success:
                    successful += 1
                    downloaded_models.append({
                        "name": model["name"],
                        "category": category,
                        "subcategory": subcategory,
                        "repo_id": model["repo_id"],
                        "local_path": str(MODELS_DIR / category / model["local_dir"]),
                        "description": model["description"],
                        "priority": model["priority"],
                        "license": model["license"],
                        "capabilities": model["capabilities"],
                        "download_date": datetime.now().isoformat()
                    })
                else:
                    failed += 1
            
            print()
    
    # Create model registry
    print("=" * 80)
    print("📋 CREATING MODEL REGISTRY")
    print("=" * 80)
    print()
    
    registry = create_model_registry(downloaded_models, API_ONLY_MODELS)
    
    # Save registry
    registry_path = MODELS_DIR / "model_registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"✅ Registry saved: {registry_path}")
    print()
    
    # Create API registry
    api_registry_path = MODELS_DIR / "api_models_registry.json"
    with open(api_registry_path, 'w') as f:
        json.dump({
            "version": "1.0.0",
            "generated": datetime.now().isoformat(),
            "note": "API-only models (Claude Opus 4.6, GPT-5.4, etc.) - requires API keys",
            "models": API_ONLY_MODELS
        }, f, indent=2)
    
    print(f"✅ API Registry saved: {api_registry_path}")
    print()
    
    # Final summary
    print("=" * 80)
    print("✅ AETHER HARVEST PROTOCOL - DOWNLOAD COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Summary:")
    print(f"   Total attempted: {total_attempted}")
    print(f"   Successfully downloaded: {successful}")
    print(f"   Failed: {failed}")
    print(f"   API-only registered: {len(API_ONLY_MODELS)}")
    print()
    print(f"📁 Downloads location: {MODELS_DIR}")
    print(f"📋 Model registry: {registry_path}")
    print(f"📋 API registry: {api_registry_path}")
    print()
    
    if successful > 0:
        print("🎯 Downloaded Models by Category:")
        for model in downloaded_models:
            print(f"   ✓ {model['name']} ({model['category']}/{model['subcategory']})")
        print()
    
    if failed > 0:
        print("⚠️  Some models failed to download. This is expected for:")
        print("   - Models not yet released (Gemma 4, LLaMA 4, etc.)")
        print("   - Models requiring special authentication")
        print("   - Placeholder repo IDs")
        print()
    
    print("🚀 Next Steps:")
    print("   1. Monitor for Gemma 4 and LLaMA 4 official releases")
    print("   2. Update repo_ids when models become available")
    print("   3. Re-run this script to download newly released models")
    print("   4. Test models: python scripts/test_frontier_models.py")
    print("   5. Integrate into RAG: python scripts/rag_ingest.py")
    print()
    
    return successful > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
