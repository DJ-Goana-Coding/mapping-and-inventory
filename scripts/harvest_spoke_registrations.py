#!/usr/bin/env python3
"""
🌐 CITADEL HUB SPOKE HARVESTER

This script runs on the mapping-and-inventory hub to harvest
registration data from spoke repositories.

It collects TREE, INVENTORY, and metadata from all spokes and
maintains the central repository registry.

Author: Citadel Architect v25.0.OMNI++
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SpokeHarvester:
    """Harvests registration data from spoke repositories"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.registry_path = self.repo_root / "data" / "citadel_mesh" / "repository_registry.json"
        self.spokes_data_dir = self.repo_root / "data" / "citadel_mesh" / "spokes"
        self.spokes_data_dir.mkdir(parents=True, exist_ok=True)
        
        self.gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.gh_token:
            self.headers["Authorization"] = f"token {self.gh_token}"
        
    def load_registry(self) -> Dict:
        """Load the central repository registry"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r') as f:
                return json.load(f)
        return {"spokes": []}
    
    def save_registry(self, registry: Dict):
        """Save the central repository registry"""
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
    
    def harvest_all_spokes(self):
        """Harvest data from all registered spokes"""
        
        print("━" * 60)
        print("🌐 CITADEL HUB SPOKE HARVESTER")
        print("━" * 60)
        print()
        
        registry = self.load_registry()
        spokes = [s for s in registry.get("spokes", []) if s.get("enabled", False)]
        
        print(f"📊 Total spokes: {len(registry.get('spokes', []))}")
        print(f"✅ Enabled spokes: {len(spokes)}")
        print()
        
        harvested = 0
        failed = 0
        
        for spoke in spokes:
            print(f"📡 Harvesting: {spoke['name']}")
            try:
                if self.harvest_spoke(spoke):
                    harvested += 1
                    print(f"   ✅ Success")
                else:
                    failed += 1
                    print(f"   ⚠️  Partial/Failed")
            except Exception as e:
                failed += 1
                print(f"   ❌ Error: {e}")
            print()
        
        print("━" * 60)
        print("📊 HARVEST SUMMARY")
        print("━" * 60)
        print(f"✅ Harvested: {harvested}")
        print(f"⚠️  Failed: {failed}")
        print(f"📁 Data stored: {self.spokes_data_dir}")
        print()
        print("🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors")
        print("━" * 60)
    
    def harvest_spoke(self, spoke: Dict) -> bool:
        """Harvest data from a single spoke"""
        
        spoke_name = spoke['name']
        spoke_owner = spoke['owner']
        
        # Create spoke data directory
        spoke_dir = self.spokes_data_dir / spoke_name
        spoke_dir.mkdir(exist_ok=True)
        
        success = True
        
        # 1. Harvest TREE.md
        if self._harvest_file(spoke_owner, spoke_name, "TREE.md", spoke_dir):
            print(f"   📄 TREE.md harvested")
        else:
            success = False
        
        # 2. Harvest INVENTORY.json
        if self._harvest_file(spoke_owner, spoke_name, "INVENTORY.json", spoke_dir):
            print(f"   📄 INVENTORY.json harvested")
        else:
            success = False
        
        # 3. Harvest README.md
        if self._harvest_file(spoke_owner, spoke_name, "README.md", spoke_dir):
            print(f"   📄 README.md harvested")
        
        # 4. Harvest workflow artifacts (if available)
        self._harvest_workflow_artifacts(spoke_owner, spoke_name, spoke_dir)
        
        # 5. Create spoke metadata
        metadata = {
            "spoke": spoke_name,
            "owner": spoke_owner,
            "harvested_at": datetime.utcnow().isoformat() + "Z",
            "github_url": spoke.get("github_url"),
            "hf_space": spoke.get("hf_space"),
            "pillar": spoke.get("pillar"),
            "district": spoke.get("district"),
            "role": spoke.get("role")
        }
        
        with open(spoke_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"   💾 Metadata saved")
        
        return success
    
    def _harvest_file(self, owner: str, repo: str, filepath: str, output_dir: Path) -> bool:
        """Harvest a specific file from a repository"""
        
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{filepath}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Decode content (GitHub API returns base64)
                import base64
                content = base64.b64decode(data['content']).decode('utf-8')
                
                # Save file
                output_path = output_dir / filepath
                with open(output_path, 'w') as f:
                    f.write(content)
                
                return True
            else:
                return False
        except Exception as e:
            print(f"      ⚠️  Error harvesting {filepath}: {e}")
            return False
    
    def _harvest_workflow_artifacts(self, owner: str, repo: str, output_dir: Path):
        """Harvest workflow artifacts from spoke registration runs"""
        
        # This would require GitHub Actions API access to download artifacts
        # For now, we'll skip this and rely on file harvesting
        pass
    
    def update_spoke_status(self, spoke_name: str, status: Dict):
        """Update spoke status in registry"""
        
        registry = self.load_registry()
        
        for spoke in registry.get("spokes", []):
            if spoke['name'] == spoke_name:
                spoke['last_seen'] = datetime.utcnow().isoformat() + "Z"
                spoke['status'] = status
                break
        
        self.save_registry(registry)


def main():
    """Main entry point"""
    
    harvester = SpokeHarvester()
    harvester.harvest_all_spokes()


if __name__ == "__main__":
    main()
