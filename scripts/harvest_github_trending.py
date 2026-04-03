#!/usr/bin/env python3
"""
🛰️ AETHER HARVEST PROTOCOL - GitHub Trending Harvester
Clones AI agent frameworks, mesh networks, and distributed systems
Author: Citadel Architect v25.0.OMNI++
Date: April 2026
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

print("=" * 80)
print("🛰️ AETHER HARVEST PROTOCOL - GitHub Trending Harvester (April 2026)")
print("=" * 80)
print()

# Setup paths
BASE_DIR = Path(__file__).parent.parent
TOOLS_DIR = BASE_DIR / "data" / "tools"
TOOLS_DIR.mkdir(parents=True, exist_ok=True)

# GitHub repositories to harvest (April 2026 discoveries)
GITHUB_HARVEST = {
    "agents": {
        "description": "AI Agent Frameworks and Multi-Agent Systems",
        "repos": [
            {
                "name": "AutoGPT",
                "url": "https://github.com/Significant-Gravitas/AutoGPT.git",
                "description": "Autonomous GPT-4 agent framework",
                "priority": "CRITICAL",
                "stars": "160K+",
                "use_case": "Autonomous task execution"
            },
            {
                "name": "LangChain",
                "url": "https://github.com/langchain-ai/langchain.git",
                "description": "Framework for LLM applications",
                "priority": "CRITICAL",
                "stars": "80K+",
                "use_case": "LLM orchestration and chains"
            },
            {
                "name": "MetaGPT",
                "url": "https://github.com/geekan/MetaGPT.git",
                "description": "Multi-agent framework for software development",
                "priority": "HIGH",
                "stars": "40K+",
                "use_case": "Multi-agent collaboration"
            },
            {
                "name": "Deer-Flow",
                "url": "https://github.com/bytedance/deer-flow.git",
                "description": "ByteDance SuperAgents framework",
                "priority": "HIGH",
                "stars": "5K+",
                "use_case": "Modular task-based subagents",
                "note": "May not exist - placeholder for ByteDance agent framework"
            }
        ]
    },
    "mesh-networks": {
        "description": "Mesh Networking and Distributed Communication",
        "repos": [
            {
                "name": "Meshtastic",
                "url": "https://github.com/meshtastic/firmware.git",
                "description": "LoRa mesh networking firmware",
                "priority": "HIGH",
                "stars": "3K+",
                "use_case": "Off-grid mesh communication"
            },
            {
                "name": "NetBird",
                "url": "https://github.com/netbirdio/netbird.git",
                "description": "WireGuard-based mesh VPN",
                "priority": "HIGH",
                "stars": "9K+",
                "use_case": "Secure mesh VPN"
            },
            {
                "name": "OpenThread",
                "url": "https://github.com/openthread/openthread.git",
                "description": "Google's IoT mesh protocol",
                "priority": "MEDIUM",
                "stars": "3K+",
                "use_case": "IoT mesh networking"
            },
            {
                "name": "CJDNS",
                "url": "https://github.com/cjdelisle/cjdns.git",
                "description": "Encrypted mesh networking",
                "priority": "MEDIUM",
                "stars": "5K+",
                "use_case": "Encrypted P2P mesh"
            },
            {
                "name": "Reticulum",
                "url": "https://github.com/markqvist/Reticulum.git",
                "description": "Censorship-resistant mesh stack",
                "priority": "MEDIUM",
                "stars": "2K+",
                "use_case": "Resilient mesh communication"
            }
        ]
    },
    "distributed": {
        "description": "Distributed Systems and Frameworks",
        "repos": [
            {
                "name": "HuggingFace-Accelerate",
                "url": "https://github.com/huggingface/accelerate.git",
                "description": "Easy distributed training framework",
                "priority": "CRITICAL",
                "stars": "6K+",
                "use_case": "Heterogeneous GPU clusters"
            },
            {
                "name": "Ray",
                "url": "https://github.com/ray-project/ray.git",
                "description": "Distributed computing framework",
                "priority": "HIGH",
                "stars": "30K+",
                "use_case": "Distributed ML and applications"
            },
            {
                "name": "Dask",
                "url": "https://github.com/dask/dask.git",
                "description": "Parallel computing library",
                "priority": "MEDIUM",
                "stars": "12K+",
                "use_case": "Distributed data processing"
            }
        ]
    },
    "vector-db": {
        "description": "Vector Databases for RAG Systems",
        "repos": [
            {
                "name": "Qdrant",
                "url": "https://github.com/qdrant/qdrant.git",
                "description": "Rust-based vector database (RECOMMENDED)",
                "priority": "CRITICAL",
                "stars": "18K+",
                "use_case": "High-performance RAG backend"
            },
            {
                "name": "Weaviate",
                "url": "https://github.com/weaviate/weaviate.git",
                "description": "Vector database with hybrid search",
                "priority": "HIGH",
                "stars": "9K+",
                "use_case": "Hybrid text+vector search"
            },
            {
                "name": "Milvus",
                "url": "https://github.com/milvus-io/milvus.git",
                "description": "Billion-scale vector database",
                "priority": "MEDIUM",
                "stars": "27K+",
                "use_case": "Large-scale vector search"
            },
            {
                "name": "ChromaDB",
                "url": "https://github.com/chroma-core/chroma.git",
                "description": "Lightweight embedding database",
                "priority": "MEDIUM",
                "stars": "12K+",
                "use_case": "Development and prototyping"
            }
        ]
    }
}


def clone_repository(url: str, target_dir: Path, shallow: bool = True) -> bool:
    """Clone a Git repository with error handling"""
    
    if target_dir.exists() and (target_dir / ".git").exists():
        print(f"⏭️  Repository already exists, skipping...")
        return True
    
    try:
        print(f"📥 Cloning repository...")
        print(f"   URL: {url}")
        print(f"   Target: {target_dir}")
        
        # Create parent directory
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        
        # Clone with or without full history
        cmd = ["git", "clone"]
        if shallow:
            cmd.extend(["--depth", "1"])
        cmd.extend([url, str(target_dir)])
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"✅ Repository cloned successfully!")
            
            # Get basic repo info
            try:
                # Count files
                file_count = sum(1 for _ in target_dir.rglob("*") if _.is_file())
                print(f"   Files: {file_count}")
                
                # Get repo size
                size = sum(f.stat().st_size for f in target_dir.rglob("*") if f.is_file())
                size_mb = size / (1024 * 1024)
                print(f"   Size: {size_mb:.2f} MB")
            except:
                pass
            
            print()
            return True
        else:
            print(f"❌ Clone failed: {result.stderr}")
            print()
            return False
            
    except subprocess.TimeoutExpired:
        print(f"❌ Clone timed out after 5 minutes")
        print()
        return False
    except Exception as e:
        print(f"❌ Error cloning repository: {e}")
        print()
        return False


def create_tools_registry(cloned_repos: List[Dict]) -> Dict:
    """Create comprehensive tools registry"""
    
    registry = {
        "version": "1.0.0",
        "protocol": "AETHER_HARVEST",
        "generated": datetime.now().isoformat(),
        "discovery_date": "2026-04-03",
        "categories": {
            "agents": "AI Agent Frameworks and Multi-Agent Systems",
            "mesh-networks": "Mesh Networking and Distributed Communication",
            "distributed": "Distributed Systems and Computing Frameworks",
            "vector-db": "Vector Databases for RAG Systems"
        },
        "cloned_repositories": cloned_repos,
        "statistics": {
            "total_cloned": len(cloned_repos),
            "by_category": {},
            "by_priority": {}
        }
    }
    
    # Calculate statistics
    for repo in cloned_repos:
        cat = repo["category"]
        pri = repo["priority"]
        
        registry["statistics"]["by_category"][cat] = \
            registry["statistics"]["by_category"].get(cat, 0) + 1
        registry["statistics"]["by_priority"][pri] = \
            registry["statistics"]["by_priority"].get(pri, 0) + 1
    
    return registry


def main():
    """Main orchestration for GitHub repository harvesting"""
    
    print(f"📁 Tools base directory: {TOOLS_DIR}")
    print()
    
    # Track results
    cloned_repos = []
    total_attempted = 0
    successful = 0
    failed = 0
    
    # Clone repositories by category
    for category, config in GITHUB_HARVEST.items():
        print("=" * 80)
        print(f"📦 CATEGORY: {category}")
        print(f"   {config['description']}")
        print("=" * 80)
        print()
        
        category_dir = TOOLS_DIR / category
        category_dir.mkdir(parents=True, exist_ok=True)
        
        for repo in config["repos"]:
            total_attempted += 1
            
            # Extract repo name from URL
            repo_name = repo["url"].split("/")[-1].replace(".git", "")
            target_dir = category_dir / repo_name
            
            print(f"🗂️  {repo['name']}")
            print(f"   Priority: {repo['priority']}")
            print(f"   Stars: {repo['stars']}")
            print(f"   Description: {repo['description']}")
            print(f"   Use Case: {repo['use_case']}")
            
            if "note" in repo:
                print(f"   ℹ️  NOTE: {repo['note']}")
            
            success = clone_repository(repo["url"], target_dir, shallow=True)
            
            if success:
                successful += 1
                cloned_repos.append({
                    "name": repo["name"],
                    "category": category,
                    "url": repo["url"],
                    "local_path": str(target_dir),
                    "description": repo["description"],
                    "priority": repo["priority"],
                    "stars": repo["stars"],
                    "use_case": repo["use_case"],
                    "clone_date": datetime.now().isoformat()
                })
            else:
                failed += 1
    
    # Create tools registry
    print("=" * 80)
    print("📋 CREATING TOOLS REGISTRY")
    print("=" * 80)
    print()
    
    registry = create_tools_registry(cloned_repos)
    
    # Save registry
    registry_path = TOOLS_DIR / "tools_registry.json"
    with open(registry_path, 'w') as f:
        json.dump(registry, f, indent=2)
    
    print(f"✅ Registry saved: {registry_path}")
    print()
    
    # Final summary
    print("=" * 80)
    print("✅ AETHER HARVEST PROTOCOL - HARVEST COMPLETE")
    print("=" * 80)
    print()
    print(f"📊 Summary:")
    print(f"   Total attempted: {total_attempted}")
    print(f"   Successfully cloned: {successful}")
    print(f"   Failed: {failed}")
    print()
    print(f"📁 Tools location: {TOOLS_DIR}")
    print(f"📋 Registry: {registry_path}")
    print()
    
    if successful > 0:
        print("🎯 Cloned Repositories by Category:")
        for repo in cloned_repos:
            print(f"   ✓ {repo['name']} ({repo['category']})")
        print()
    
    if failed > 0:
        print("⚠️  Some repositories failed to clone. This may be due to:")
        print("   - Repository doesn't exist")
        print("   - Network issues")
        print("   - Access restrictions")
        print()
    
    print("🚀 Next Steps:")
    print("   1. Explore cloned repositories")
    print("   2. Install dependencies for frameworks you want to use")
    print("   3. Integrate agents into TIA-ARCHITECT-CORE")
    print("   4. Evaluate vector databases for RAG migration")
    print("   5. Test mesh networking tools")
    print()
    
    return successful > 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
