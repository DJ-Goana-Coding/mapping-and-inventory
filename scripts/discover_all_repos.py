#!/usr/bin/env python3
"""
CITADEL ARCHITECT - REPOSITORY DISCOVERY ENGINE
Discovers all DJ-Goana-Coding GitHub repositories and generates complete registry
"""
import os
import sys
import json
import requests
from datetime import datetime
from typing import List, Dict, Any

GITHUB_ORG = "DJ-Goana-Coding"
GITHUB_API = "https://api.github.com"


def discover_github_repos(org: str, token: str = None) -> List[Dict[str, Any]]:
    """
    Discover all repositories in the GitHub organization.
    
    Args:
        org: GitHub organization name
        token: Optional GitHub token for authentication
        
    Returns:
        List of repository metadata dictionaries
    """
    repos = []
    page = 1
    per_page = 100
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    print(f"🔍 Discovering repositories in {org}...")
    
    while True:
        url = f"{GITHUB_API}/orgs/{org}/repos"
        params = {"page": page, "per_page": per_page, "type": "all"}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            
            batch = response.json()
            if not batch:
                break
                
            repos.extend(batch)
            print(f"  📦 Found {len(batch)} repos on page {page} (total: {len(repos)})")
            
            # Check if there are more pages
            if len(batch) < per_page:
                break
                
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching repos: {e}")
            break
    
    print(f"✅ Discovery complete: {len(repos)} repositories found")
    return repos


def classify_repo(repo: Dict[str, Any]) -> Dict[str, Any]:
    """
    Classify and extract metadata from a GitHub repository.
    
    Args:
        repo: Raw GitHub API repository object
        
    Returns:
        Classified repository metadata
    """
    name = repo.get("name", "unknown")
    description = repo.get("description", "")
    topics = repo.get("topics", [])
    language = repo.get("language", "Unknown")
    is_private = repo.get("private", False)
    is_archived = repo.get("archived", False)
    default_branch = repo.get("default_branch", "main")
    
    # Determine role/type based on name and topics
    role = "Unknown"
    repo_type = "GitHub Repo"
    pillar = "UNCLASSIFIED"
    
    # Classification logic
    if "architect" in name.lower() or "tia" in name.lower():
        role = "Reasoning Hub / Oracle"
        pillar = "LORE"
        repo_type = "Reasoning Hub"
    elif "mapping" in name.lower() or "inventory" in name.lower():
        role = "Librarian / Central Hub"
        pillar = "MEMORY"
        repo_type = "Command Core"
    elif "ark" in name.lower():
        role = "Sovereign Intelligence Engine"
        pillar = "LORE"
        repo_type = "Core System"
    elif "trader" in name.lower() or "trading" in name.lower():
        role = "Trading System"
        pillar = "TRADING"
    elif "vortex" in name.lower() or "engine" in name.lower():
        role = "Compute Engine"
        pillar = "WEB3"
    elif "vault" in name.lower() or "storage" in name.lower():
        role = "Data Vault"
        pillar = "MEMORY"
    elif "soul" in name.lower() or "genetics" in name.lower():
        role = "Cognitive Reservoir"
        pillar = "LORE"
    
    return {
        "name": name,
        "full_name": repo.get("full_name", f"{GITHUB_ORG}/{name}"),
        "description": description,
        "type": repo_type,
        "role": role,
        "pillar": pillar,
        "url": repo.get("html_url", ""),
        "clone_url": repo.get("clone_url", ""),
        "ssh_url": repo.get("ssh_url", ""),
        "language": language,
        "topics": topics,
        "is_private": is_private,
        "is_archived": is_archived,
        "default_branch": default_branch,
        "created_at": repo.get("created_at", ""),
        "updated_at": repo.get("updated_at", ""),
        "pushed_at": repo.get("pushed_at", ""),
        "size": repo.get("size", 0),
        "stargazers_count": repo.get("stargazers_count", 0),
        "watchers_count": repo.get("watchers_count", 0),
        "has_issues": repo.get("has_issues", False),
        "has_projects": repo.get("has_projects", False),
        "has_wiki": repo.get("has_wiki", False),
    }


def generate_bridge_config(repos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate bridge configuration for repo syncing.
    
    Args:
        repos: List of classified repositories
        
    Returns:
        Bridge configuration dictionary
    """
    config = {
        "version": "1.0.0",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "organization": GITHUB_ORG,
        "total_repos": len(repos),
        "repositories": repos,
        "bridge_config": {
            "sync_target": "mapping-and-inventory",
            "sync_method": "artifact_extraction",
            "artifact_types": ["TREE.md", "INVENTORY.json", "SCAFFOLD.md"],
            "hf_space": {
                "org": "DJ-Goanna-Coding",
                "space": "Mapping-and-Inventory",
                "url": "https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory"
            }
        },
        "statistics": {
            "by_pillar": {},
            "by_language": {},
            "by_type": {},
            "private_count": sum(1 for r in repos if r["is_private"]),
            "public_count": sum(1 for r in repos if not r["is_private"]),
            "archived_count": sum(1 for r in repos if r["is_archived"]),
            "active_count": sum(1 for r in repos if not r["is_archived"])
        }
    }
    
    # Calculate statistics
    for repo in repos:
        # By pillar
        pillar = repo.get("pillar", "UNCLASSIFIED")
        config["statistics"]["by_pillar"][pillar] = \
            config["statistics"]["by_pillar"].get(pillar, 0) + 1
        
        # By language
        lang = repo.get("language", "Unknown")
        config["statistics"]["by_language"][lang] = \
            config["statistics"]["by_language"].get(lang, 0) + 1
        
        # By type
        repo_type = repo.get("type", "Unknown")
        config["statistics"]["by_type"][repo_type] = \
            config["statistics"]["by_type"].get(repo_type, 0) + 1
    
    return config


def main():
    """Main execution function."""
    print("=" * 80)
    print("🏛️  CITADEL ARCHITECT - REPOSITORY DISCOVERY ENGINE")
    print("=" * 80)
    print()
    
    # Get GitHub token from environment
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("⚠️  No GITHUB_TOKEN found - API rate limits will apply")
        print("   Set GITHUB_TOKEN environment variable for higher limits")
        print()
    
    # Discover repositories
    repos_raw = discover_github_repos(GITHUB_ORG, github_token)
    
    if not repos_raw:
        print("❌ No repositories found or discovery failed")
        sys.exit(1)
    
    print()
    print("📊 Classifying repositories...")
    
    # Classify repositories
    repos_classified = [classify_repo(repo) for repo in repos_raw]
    
    # Generate bridge configuration
    bridge_config = generate_bridge_config(repos_classified)
    
    # Save to file
    output_file = "repo_bridge_registry.json"
    with open(output_file, "w") as f:
        json.dump(bridge_config, f, indent=2)
    
    print(f"✅ Registry saved to: {output_file}")
    print()
    print("📊 DISCOVERY SUMMARY")
    print("=" * 80)
    print(f"Total Repositories: {bridge_config['total_repos']}")
    print(f"Active: {bridge_config['statistics']['active_count']}")
    print(f"Archived: {bridge_config['statistics']['archived_count']}")
    print(f"Public: {bridge_config['statistics']['public_count']}")
    print(f"Private: {bridge_config['statistics']['private_count']}")
    print()
    print("By Pillar:")
    for pillar, count in sorted(bridge_config['statistics']['by_pillar'].items()):
        print(f"  {pillar}: {count}")
    print()
    print("By Language:")
    for lang, count in sorted(bridge_config['statistics']['by_language'].items(), 
                             key=lambda x: x[1], reverse=True):
        print(f"  {lang}: {count}")
    print()
    print("=" * 80)
    print(f"✅ Discovery complete! Found {len(repos_classified)} repositories")
    print("=" * 80)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
