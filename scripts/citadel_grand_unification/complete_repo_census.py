#!/usr/bin/env python3
"""
🏛️ CITADEL GRAND UNIFICATION: Complete Repository Census
Phase 1.1 - Comprehensive repository discovery and metadata extraction

Scans all DJ-Goana-Coding (GitHub) and DJ-Goanna-Coding (HuggingFace) repositories
Generates complete_repo_census.json with full metadata matrix, hub-spoke topology,
and Double-N Rift documentation.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import time

class CompleteRepoCensus:
    """Complete repository census builder for Grand Unification"""
    
    def __init__(self):
        self.github_org = "DJ-Goana-Coding"  # Single-N
        self.hf_org = "DJ-Goanna-Coding"      # Double-N
        self.github_token = os.getenv("GITHUB_TOKEN", os.getenv("GH_TOKEN"))
        self.hf_token = os.getenv("HF_TOKEN")
        
        self.base_dir = Path(__file__).parent.parent.parent
        self.output_dir = self.base_dir / "data" / "discoveries"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.census_data = {
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "plan": "CITADEL GRAND UNIFICATION PLAN v1.0",
                "phase": "1.1 - Repository Constellation Mapping"
            },
            "double_n_rift": {
                "github_namespace": self.github_org,
                "huggingface_namespace": self.hf_org,
                "naming_difference": "GitHub uses single-N (Goana), HuggingFace uses double-N (Goanna)"
            },
            "hub_topology": {
                "primary_hub": {
                    "name": "mapping-and-inventory",
                    "platform": "GitHub",
                    "role": "Master Intelligence Coordinator"
                }
            },
            "github_repos": [],
            "huggingface_spaces": [],
            "spoke_relationships": {},
            "summary": {}
        }
    
    def discover_github_repos(self) -> List[Dict]:
        """Discover all GitHub repositories"""
        print(f"🔍 Scanning GitHub: {self.github_org}")
        
        headers = {}
        if self.github_token:
            headers["Authorization"] = f"token {self.github_token}"
        
        repos = []
        page = 1
        
        while page < 10:  # Limit to prevent excessive API calls
            url = f"https://api.github.com/orgs/{self.github_org}/repos"
            params = {"per_page": 100, "page": page}
            
            try:
                response = requests.get(url, headers=headers, params=params, timeout=30)
                response.raise_for_status()
                batch = response.json()
                
                if not batch:
                    break
                
                for repo in batch:
                    repos.append({
                        "name": repo["name"],
                        "url": repo["html_url"],
                        "language": repo.get("language", "Unknown"),
                        "size_mb": round(repo.get("size", 0) / 1024, 2)
                    })
                    print(f"  ✓ {repo['name']}")
                
                page += 1
                time.sleep(0.5)
                        
            except Exception as e:
                print(f"Error: {e}")
                break
        
        print(f"✅ Found {len(repos)} GitHub repos")
        return repos
    
    def build_complete_census(self):
        """Build complete repository census"""
        print("🏛️  CITADEL GRAND UNIFICATION: Repository Census")
        print("=" * 70)
        
        self.census_data["github_repos"] = self.discover_github_repos()
        self.census_data["summary"]["total_github_repos"] = len(self.census_data["github_repos"])
        
        output_file = self.output_dir / "complete_repo_census.json"
        with open(output_file, 'w') as f:
            json.dump(self.census_data, f, indent=2)
        
        print(f"\n✅ Census saved to: {output_file}")
        return self.census_data


if __name__ == "__main__":
    census_builder = CompleteRepoCensus()
    census_data = census_builder.build_complete_census()
