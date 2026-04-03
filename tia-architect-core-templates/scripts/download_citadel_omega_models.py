#!/usr/bin/env python3
"""
CITADEL_OMEGA - Model Downloader
Download ML models from HuggingFace for trading operations
Author: Citadel Architect v25.0.OMNI+
"""

import os
import sys
from pathlib import Path
from huggingface_hub import snapshot_download, hf_hub_download
import json

print("=" * 60)
print("🤖 CITADEL_OMEGA - ML Model Downloader")
print("=" * 60)
print()

# Setup paths
BASE_DIR = Path(__file__).parent.parent / "CITADEL_OMEGA"
MODELS_DIR = BASE_DIR / "models" / "pretrained"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Model registry
MODELS = {
    "sentiment_analysis": [
        {
            "name": "FinBERT",
            "repo_id": "ProsusAI/finbert",
            "local_dir": "finbert",
            "description": "Financial sentiment analysis (positive/negative/neutral)"
        },
        {
            "name": "CryptoBERT",
            "repo_id": "ElKulako/cryptobert",
            "local_dir": "cryptobert",
            "description": "Cryptocurrency-specific sentiment analysis"
        },
        {
            "name": "Twitter RoBERTa",
            "repo_id": "cardiffnlp/twitter-roberta-base-sentiment-latest",
            "local_dir": "twitter-roberta-sentiment",
            "description": "Twitter sentiment analysis"
        }
    ],
    "embeddings": [
        {
            "name": "Sentence Transformers (MiniLM)",
            "repo_id": "sentence-transformers/all-MiniLM-L6-v2",
            "local_dir": "sentence-transformers-minilm",
            "description": "Fast sentence embeddings for RAG"
        },
        {
            "name": "Sentence Transformers (MPNet)",
            "repo_id": "sentence-transformers/all-mpnet-base-v2",
            "local_dir": "sentence-transformers-mpnet",
            "description": "High-quality sentence embeddings"
        }
    ],
    "language_models": [
        {
            "name": "DistilGPT2",
            "repo_id": "distilgpt2",
            "local_dir": "distilgpt2",
            "description": "Lightweight GPT-2 for text generation"
        },
        {
            "name": "FLAN-T5 Small",
            "repo_id": "google/flan-t5-small",
            "local_dir": "flan-t5-small",
            "description": "Instruction-tuned T5 for Q&A"
        }
    ],
    "timeseries": [
        {
            "name": "TimeGPT",
            "repo_id": "nixtla/timegpt-1",
            "local_dir": "timegpt",
            "description": "Time series forecasting",
            "skip": True  # Requires authentication
        }
    ]
}


def download_model(repo_id: str, local_dir: str, description: str):
    """Download a model from HuggingFace"""
    target_path = MODELS_DIR / local_dir
    
    if target_path.exists():
        print(f"⏭️  {local_dir} already exists, skipping...")
        return True
    
    try:
        print(f"📥 Downloading {local_dir}...")
        print(f"   Repo: {repo_id}")
        print(f"   Description: {description}")
        
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(target_path),
            local_dir_use_symlinks=False
        )
        
        print(f"✅ {local_dir} downloaded successfully!")
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error downloading {local_dir}: {e}")
        print()
        return False


def main():
    """Main download orchestration"""
    
    # Check for HF token (optional)
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        print("🔑 HuggingFace token detected")
    else:
        print("⚠️  No HF_TOKEN found - some models may require authentication")
    print()
    
    # Create models directory
    print(f"📁 Models directory: {MODELS_DIR}")
    print()
    
    # Track results
    total_models = 0
    downloaded = 0
    failed = 0
    skipped = 0
    
    # Download each category
    for category, models_list in MODELS.items():
        print("-" * 60)
        print(f"📦 Category: {category.upper()}")
        print("-" * 60)
        print()
        
        for model in models_list:
            total_models += 1
            
            if model.get("skip", False):
                print(f"⏭️  Skipping {model['name']} (requires special auth)")
                skipped += 1
                print()
                continue
            
            success = download_model(
                repo_id=model["repo_id"],
                local_dir=model["local_dir"],
                description=model["description"]
            )
            
            if success:
                downloaded += 1
            else:
                failed += 1
    
    # Create model registry
    registry = {
        "version": "1.0.0",
        "downloaded_models": [],
        "categories": MODELS
    }
    
    # List downloaded models
    for category, models_list in MODELS.items():
        for model in models_list:
            target_path = MODELS_DIR / model["local_dir"]
            if target_path.exists():
                registry["downloaded_models"].append({
                    "name": model["name"],
                    "category": category,
                    "repo_id": model["repo_id"],
                    "local_path": str(target_path),
                    "description": model["description"]
                })
    
    # Save registry
    registry_path = MODELS_DIR.parent / "model_registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print("=" * 60)
    print("✅ Model Download Complete!")
    print("=" * 60)
    print()
    print(f"📊 Summary:")
    print(f"   Total models: {total_models}")
    print(f"   Downloaded: {downloaded}")
    print(f"   Failed: {failed}")
    print(f"   Skipped: {skipped}")
    print()
    print(f"📁 Models location: {MODELS_DIR}")
    print(f"📋 Registry saved: {registry_path}")
    print()
    print("🎯 Next Steps:")
    print("  1. Test models: python scripts/test_models.py")
    print("  2. Setup RAG: python omega_archive/rag_system/rag_engine.py")
    print("  3. Train custom models: python tools/model_trainers/lstm_trainer.py")
    print()


if __name__ == "__main__":
    # Check for huggingface_hub
    try:
        import huggingface_hub
    except ImportError:
        print("❌ Error: huggingface_hub not installed")
        print("   Install with: pip install huggingface-hub")
        sys.exit(1)
    
    main()
