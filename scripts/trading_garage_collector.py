#!/usr/bin/env python3
"""
CITADEL ARCHITECT - TRADING GARAGE COLLECTOR
Discovers and aggregates all trading bots, scripts, and strategies into organized garages
"""
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Garage configurations
GARAGES = {
    "Trading_Garage_Alpha": {
        "description": "Active trading bots and automation scripts",
        "filters": ["bot", "trader", "trading", "automation", "strategy"]
    },
    "Trading_Garage_Beta": {
        "description": "Backtesting engines and analysis tools",
        "filters": ["backtest", "analysis", "research", "monte-carlo", "simulation"]
    },
    "Trading_Garage_Omega": {
        "description": "Exchange connectors and API interfaces",
        "filters": ["exchange", "api", "connector", "binance", "coinbase", "kraken"]
    },
    "Trading_Garage_SpareParts": {
        "description": "Templates, components, notebooks, sandboxes for experimentation",
        "filters": ["template", "example", "notebook", "colab", "sandbox", "demo", "test", "experiment"]
    }
}

GARAGE_BASE = Path("Trading_Garages")


def load_repo_registry() -> Dict[str, Any]:
    """Load the repo bridge registry."""
    registry_path = Path("repo_bridge_registry.json")
    if not registry_path.exists():
        print("❌ Registry not found. Run scripts/discover_all_repos.py first")
        sys.exit(1)
    
    with open(registry_path, "r") as f:
        return json.load(f)


def classify_as_trading_repo(repo: Dict[str, Any]) -> str:
    """
    Classify a repository as trading-related and assign to garage.
    
    Returns:
        Garage name or empty string if not trading-related
    """
    name = repo.get("name", "").lower()
    description = repo.get("description", "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    pillar = repo.get("pillar", "")
    
    # Check if trading-related
    trading_keywords = [
        "trad", "bot", "strategy", "exchange", "market", "price",
        "backtest", "signal", "algo", "arbitrage", "portfolio",
        "vortex", "pioneer", "omega"
    ]
    
    is_trading = (
        pillar == "TRADING" or
        any(kw in name for kw in trading_keywords) or
        any(kw in description for kw in trading_keywords) or
        any(kw in topics for kw in trading_keywords)
    )
    
    if not is_trading:
        return ""
    
    # Assign to garage
    for garage_name, garage_config in GARAGES.items():
        filters = garage_config["filters"]
        if any(f in name or f in description for f in filters):
            return garage_name
    
    # Default garage for unclassified trading repos
    return "Trading_Garage_Alpha"


def create_garage_structure():
    """Create the garage directory structure."""
    print(f"🏗️  Creating garage structure in {GARAGE_BASE}/")
    
    GARAGE_BASE.mkdir(exist_ok=True)
    
    for garage_name, garage_config in GARAGES.items():
        garage_path = GARAGE_BASE / garage_name
        garage_path.mkdir(exist_ok=True)
        
        # Create README
        readme_path = garage_path / "README.md"
        readme_content = f"""# {garage_name}

**Description:** {garage_config['description']}

**Filters:** {', '.join(garage_config['filters'])}

## Contents

This garage contains clones and links to trading-related repositories.

**Structure:**
```
{garage_name}/
├── README.md          # This file
├── MANIFEST.json      # Garage manifest
├── repos/             # Cloned repositories
└── links/             # Symbolic links to original locations
```

## Usage

Repositories in this garage are synchronized copies. Original repos remain in their source locations.

**Authority:** Citadel Architect v25.0.OMNI+
"""
        readme_path.write_text(readme_content)
        
        # Create subdirectories
        (garage_path / "repos").mkdir(exist_ok=True)
        (garage_path / "links").mkdir(exist_ok=True)
        
        print(f"  ✅ {garage_name}")
    
    print("✅ Garage structure created")


def clone_repo_to_garage(repo: Dict[str, Any], garage_name: str):
    """
    Clone a repository into the specified garage.
    
    Args:
        repo: Repository metadata
        garage_name: Target garage name
    """
    repo_name = repo["name"]
    clone_url = repo["clone_url"]
    garage_path = GARAGE_BASE / garage_name / "repos" / repo_name
    
    if garage_path.exists():
        print(f"  ⚠️  {repo_name} already exists in {garage_name}")
        return False
    
    print(f"  📥 Cloning {repo_name} to {garage_name}...")
    
    try:
        # Clone with depth 1 for space efficiency
        subprocess.run(
            ["git", "clone", "--depth", "1", clone_url, str(garage_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300
        )
        print(f"    ✅ Cloned {repo_name}")
        return True
    except subprocess.TimeoutExpired:
        print(f"    ⚠️  Timeout cloning {repo_name}")
        return False
    except subprocess.CalledProcessError as e:
        print(f"    ❌ Failed to clone {repo_name}: {e.stderr.decode()}")
        return False


def create_garage_manifest(garage_name: str, repos: List[Dict[str, Any]]):
    """
    Create a manifest for the garage.
    
    Args:
        garage_name: Garage name
        repos: List of repositories in this garage
    """
    manifest_path = GARAGE_BASE / garage_name / "MANIFEST.json"
    
    manifest = {
        "garage_name": garage_name,
        "description": GARAGES[garage_name]["description"],
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_repos": len(repos),
        "repositories": repos,
        "statistics": {
            "by_language": {},
            "private_count": sum(1 for r in repos if r.get("is_private", False)),
            "public_count": sum(1 for r in repos if not r.get("is_private", False)),
            "total_size_kb": sum(r.get("size", 0) for r in repos)
        }
    }
    
    # Calculate language stats
    for repo in repos:
        lang = repo.get("language", "Unknown")
        manifest["statistics"]["by_language"][lang] = \
            manifest["statistics"]["by_language"].get(lang, 0) + 1
    
    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"    📋 Created manifest: {manifest_path}")


def generate_master_garage_index():
    """Generate master index of all garages."""
    index = {
        "version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_garages": len(GARAGES),
        "garages": {}
    }
    
    for garage_name in GARAGES.keys():
        manifest_path = GARAGE_BASE / garage_name / "MANIFEST.json"
        if manifest_path.exists():
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                index["garages"][garage_name] = {
                    "description": manifest["description"],
                    "total_repos": manifest["total_repos"],
                    "path": f"Trading_Garages/{garage_name}"
                }
    
    index_path = GARAGE_BASE / "GARAGE_INDEX.json"
    with open(index_path, "w") as f:
        json.dump(index, f, indent=2)
    
    print(f"✅ Master index created: {index_path}")


def generate_garage_guide():
    """Generate comprehensive garage guide."""
    guide_content = f"""# 🚗 Trading Garages - Complete Guide

**Generated:** {datetime.utcnow().isoformat()}Z  
**Authority:** Citadel Architect v25.0.OMNI+

## Overview

The Trading Garages system aggregates all trading bots, scripts, and strategies from across the DJ-Goana-Coding organization into organized collections.

## Garage Architecture

```
Trading_Garages/
├── GARAGE_INDEX.json                    # Master index of all garages
├── TRADING_GARAGE_GUIDE.md             # This guide
│
├── Trading_Garage_Alpha/               # Active bots & automation
│   ├── README.md
│   ├── MANIFEST.json
│   ├── repos/                          # Cloned repositories
│   └── links/                          # Links to originals
│
├── Trading_Garage_Beta/                # Backtesting & analysis
│   ├── README.md
│   ├── MANIFEST.json
│   ├── repos/
│   └── links/
│
└── Trading_Garage_Omega/               # Exchange connectors
    ├── README.md
    ├── MANIFEST.json
    ├── repos/
    └── links/
```

## Garage Descriptions

"""
    
    for garage_name, garage_config in GARAGES.items():
        guide_content += f"""### {garage_name}

**Description:** {garage_config['description']}

**Classification Filters:**
- {', '.join(garage_config['filters'])}

**Location:** `Trading_Garages/{garage_name}/`

"""
    
    guide_content += """
## Philosophy

**Dual Location Strategy:**
- Original repositories remain in their source locations
- Copies are aggregated in garages for centralized access
- Links maintain connection to originals
- Synchronization via bridge workflows

**Genesis Garage Analogy:**
Just as the Genesis Garage (likely in GDrive or a partition) stores foundational assets, 
these Trading Garages store trading-specific assets in an organized, accessible manner.

## Usage

### View All Garages

```bash
cat Trading_Garages/GARAGE_INDEX.json | jq .
```

### Explore a Garage

```bash
# View garage manifest
cat Trading_Garages/Trading_Garage_Alpha/MANIFEST.json | jq .

# List cloned repos
ls Trading_Garages/Trading_Garage_Alpha/repos/

# View garage README
cat Trading_Garages/Trading_Garage_Alpha/README.md
```

### Run Collection

```bash
# Collect all trading repos into garages
python scripts/trading_garage_collector.py

# Update garages (re-run collection)
python scripts/trading_garage_collector.py --update
```

### Individual Garage Access

Each garage is a self-contained unit:

```bash
cd Trading_Garages/Trading_Garage_Alpha/repos/
ls -la                    # View all cloned trading bots
cd tias-pioneer-trader    # Work with individual bot
```

## Integration with Bridge System

The Trading Garages work alongside the Repository Bridge:

1. **Bridge Discovery** → Finds all repos
2. **Garage Collector** → Filters trading repos
3. **Garage Organization** → Clones into appropriate garages
4. **Manifest Generation** → Creates garage metadata
5. **Index Generation** → Master garage index

## Synchronization

Garages are updated:
- Manually via `trading_garage_collector.py`
- Automatically via bridge workflows (optional)
- On-demand when new trading repos are added

## Statistics

View garage statistics:

```bash
# Master index stats
cat Trading_Garages/GARAGE_INDEX.json | jq '.garages'

# Individual garage stats
cat Trading_Garages/Trading_Garage_Alpha/MANIFEST.json | jq '.statistics'
```

## Maintenance

### Update All Garages

```bash
python scripts/trading_garage_collector.py --update
```

### Clean Garages

```bash
# Remove all cloned repos (preserves structure)
rm -rf Trading_Garages/*/repos/*

# Rebuild
python scripts/trading_garage_collector.py
```

### Add New Garage

Edit `scripts/trading_garage_collector.py` and add to `GARAGES` dict:

```python
"Trading_Garage_Delta": {{
    "description": "Your description",
    "filters": ["keyword1", "keyword2"]
}}
```

## Troubleshooting

### Garage Collection Fails
- Ensure `repo_bridge_registry.json` exists
- Run `python scripts/discover_all_repos.py` first
- Check network connectivity for cloning

### Clone Timeouts
- Increase timeout in `clone_repo_to_garage()`
- Clone manually and place in garage
- Use shallow clones (already default)

### Missing Repos in Garage
- Review classification logic in `classify_as_trading_repo()`
- Adjust filters in `GARAGES` configuration
- Re-run collection after updates

## Related Documentation

- [REPO_BRIDGE_GUIDE.md](../REPO_BRIDGE_GUIDE.md) - Repository bridge system
- [GLOBAL_WELD_GUIDE.md](../GLOBAL_WELD_GUIDE.md) - Multi-repo sync
- Individual garage READMEs in each garage directory

---

**Status:** Trading Garages Operational  
**Authority:** Citadel Architect v25.0.OMNI+  
**Version:** 1.0.0

**Collect. Organize. Trade.**
"""
    
    guide_path = GARAGE_BASE / "TRADING_GARAGE_GUIDE.md"
    guide_path.write_text(guide_content)
    print(f"✅ Garage guide created: {guide_path}")


def main():
    """Main execution function."""
    print("=" * 80)
    print("🚗 CITADEL ARCHITECT - TRADING GARAGE COLLECTOR")
    print("=" * 80)
    print()
    
    # Load registry
    print("📋 Loading repository registry...")
    registry = load_repo_registry()
    repos = registry.get("repositories", [])
    print(f"✅ Loaded {len(repos)} repositories")
    print()
    
    # Create garage structure
    create_garage_structure()
    print()
    
    # Classify and collect trading repos
    print("🔍 Classifying trading repositories...")
    garage_collections = {name: [] for name in GARAGES.keys()}
    
    for repo in repos:
        if repo.get("is_archived", False):
            continue  # Skip archived repos
        
        garage_name = classify_as_trading_repo(repo)
        if garage_name:
            garage_collections[garage_name].append(repo)
            print(f"  ✅ {repo['name']} → {garage_name}")
    
    print()
    
    # Clone repos to garages
    print("📥 Cloning repositories to garages...")
    for garage_name, repos_in_garage in garage_collections.items():
        if not repos_in_garage:
            print(f"  ℹ️  No repos for {garage_name}")
            continue
        
        print(f"\n🚗 {garage_name} ({len(repos_in_garage)} repos)")
        
        cloned_count = 0
        for repo in repos_in_garage:
            if clone_repo_to_garage(repo, garage_name):
                cloned_count += 1
        
        print(f"  ✅ Cloned {cloned_count}/{len(repos_in_garage)} repos")
        
        # Create manifest
        create_garage_manifest(garage_name, repos_in_garage)
    
    print()
    
    # Generate master index
    print("📊 Generating master garage index...")
    generate_master_garage_index()
    print()
    
    # Generate guide
    print("📚 Generating garage guide...")
    generate_garage_guide()
    print()
    
    # Summary
    print("=" * 80)
    print("🏁 COLLECTION COMPLETE")
    print("=" * 80)
    total_trading_repos = sum(len(repos) for repos in garage_collections.values())
    print(f"Total Trading Repos: {total_trading_repos}")
    print()
    print("Garage Summary:")
    for garage_name, repos_in_garage in garage_collections.items():
        print(f"  {garage_name}: {len(repos_in_garage)} repos")
    print()
    print("Generated Files:")
    print(f"  - Trading_Garages/GARAGE_INDEX.json")
    print(f"  - Trading_Garages/TRADING_GARAGE_GUIDE.md")
    for garage_name in GARAGES.keys():
        print(f"  - Trading_Garages/{garage_name}/MANIFEST.json")
    print()
    print("=" * 80)
    print("✅ Trading garages are ready!")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
