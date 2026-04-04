#!/usr/bin/env python3
"""
🌐 CITADEL SPOKE WORKFLOW DEPLOYER

This script deploys the Citadel Hub-Spoke synchronization workflows
to any repository that wants to connect to the mapping-and-inventory hub
and sync to HuggingFace.

Usage:
    python deploy_spoke_workflows.py [--repo-path /path/to/repo]

Author: Citadel Architect v25.0.OMNI++
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime
import argparse


class SpokeWorkflowDeployer:
    """Deploys Citadel Hub-Spoke synchronization workflows"""
    
    def __init__(self, repo_path=None):
        self.repo_path = Path(repo_path or os.getcwd())
        self.hub_path = Path(__file__).parent.parent
        self.workflows_dir = self.repo_path / ".github" / "workflows"
        
    def deploy_workflows(self):
        """Deploy all spoke workflows to target repository"""
        
        print("━" * 60)
        print("🌐 CITADEL SPOKE WORKFLOW DEPLOYER")
        print("━" * 60)
        print(f"📦 Target Repository: {self.repo_path}")
        print(f"🏠 Hub Repository: {self.hub_path}")
        print()
        
        # Ensure workflows directory exists
        self.workflows_dir.mkdir(parents=True, exist_ok=True)
        
        # Deploy workflows
        workflows_deployed = []
        
        # 1. Deploy HF Sync workflow
        if self._deploy_hf_sync():
            workflows_deployed.append("spoke_sync_to_hf.yml")
        
        # 2. Deploy Hub Registration workflow
        if self._deploy_hub_registration():
            workflows_deployed.append("spoke_hub_registration.yml")
        
        # 3. Create README for workflows
        self._create_workflows_readme()
        
        print()
        print("━" * 60)
        print("✅ DEPLOYMENT COMPLETE")
        print("━" * 60)
        print(f"📁 Workflows deployed: {len(workflows_deployed)}")
        for wf in workflows_deployed:
            print(f"   • {wf}")
        print()
        print("Next steps:")
        print("  1. Add HF_TOKEN to repository secrets")
        print("  2. Commit and push these workflows")
        print("  3. Workflows will auto-trigger on push to main")
        print()
        print("🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors")
        print("━" * 60)
        
    def _deploy_hf_sync(self):
        """Deploy HuggingFace sync workflow"""
        
        source = self.hub_path / ".github" / "workflows" / "spoke_sync_to_hf.yml"
        target = self.workflows_dir / "spoke_sync_to_hf.yml"
        
        if not source.exists():
            print(f"⚠️  Source workflow not found: {source}")
            return False
        
        try:
            shutil.copy2(source, target)
            print(f"✅ Deployed: spoke_sync_to_hf.yml")
            return True
        except Exception as e:
            print(f"❌ Failed to deploy spoke_sync_to_hf.yml: {e}")
            return False
    
    def _deploy_hub_registration(self):
        """Deploy hub registration workflow"""
        
        source = self.hub_path / ".github" / "workflows" / "spoke_hub_registration.yml"
        target = self.workflows_dir / "spoke_hub_registration.yml"
        
        if not source.exists():
            print(f"⚠️  Source workflow not found: {source}")
            return False
        
        try:
            shutil.copy2(source, target)
            print(f"✅ Deployed: spoke_hub_registration.yml")
            return True
        except Exception as e:
            print(f"❌ Failed to deploy spoke_hub_registration.yml: {e}")
            return False
    
    def _create_workflows_readme(self):
        """Create README for workflows directory"""
        
        readme_path = self.workflows_dir / "README.md"
        
        readme_content = f"""# Citadel Hub-Spoke Workflows

**Deployed:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

This directory contains workflows that connect this repository to the Citadel Mesh:

## Workflows

### 🔄 spoke_sync_to_hf.yml
Automatically syncs this repository to HuggingFace.

- **Triggers:** Push to main, every 6 hours, manual dispatch
- **Requires:** `HF_TOKEN` secret
- **Action:** Pushes code from GitHub → HuggingFace

### 📡 spoke_hub_registration.yml
Registers this repository with the mapping-and-inventory hub.

- **Triggers:** Push to main, every 12 hours, manual dispatch
- **Action:** Sends metadata, TREE, and INVENTORY to hub
- **Output:** Registration artifacts

## Setup Instructions

### 1. Add HF_TOKEN Secret

Go to repository Settings → Secrets and variables → Actions → New repository secret:

- **Name:** `HF_TOKEN`
- **Value:** Your HuggingFace token (get from https://huggingface.co/settings/tokens)

### 2. Verify Configuration

The workflows auto-detect your repository configuration:
- Repository name and owner
- Repository type (Space, Model, Dataset)
- HuggingFace destination URL

### 3. Trigger Workflows

Workflows trigger automatically on push to main, or manually via:

```bash
gh workflow run spoke_sync_to_hf.yml
gh workflow run spoke_hub_registration.yml
```

## Architecture

```
┌─────────────────────┐
│   GitHub Repo       │
│  (Your Spoke)       │
└──────┬──────────────┘
       │
       ├─────────────────────────┐
       │                         │
       v                         v
┌──────────────┐        ┌────────────────┐
│ HuggingFace  │        │ Hub Registry   │
│   (L4 Compute)│        │ (Mapping Hub)  │
└──────────────┘        └────────────────┘
```

## Authority Hierarchy

Per Citadel Architect Directive #1:

1. **HuggingFace Spaces (L4)** - Highest authority
2. **GitHub Repositories** - Source of truth
3. **GDrive Metadata** - Backup reference
4. **Local Nodes** - Never override cloud

## Sync Policy

- **GitHub → HF:** Always pull from GitHub (never push to GitHub from HF)
- **Spoke → Hub:** Send metadata only (TREE, INVENTORY, registration)
- **Hub → Spoke:** Never (spokes are autonomous)

## Support

For issues or questions, see:
- Main hub: https://github.com/DJ-Goana-Coding/mapping-and-inventory
- Workflow docs: `.github/workflows/` in hub repo

---

🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors
"""
        
        try:
            with open(readme_path, 'w') as f:
                f.write(readme_content)
            print(f"✅ Created: workflows/README.md")
        except Exception as e:
            print(f"⚠️  Failed to create README: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy Citadel Hub-Spoke workflows to a repository"
    )
    parser.add_argument(
        '--repo-path',
        type=str,
        default=None,
        help='Path to target repository (default: current directory)'
    )
    
    args = parser.parse_args()
    
    deployer = SpokeWorkflowDeployer(repo_path=args.repo_path)
    deployer.deploy_workflows()


if __name__ == "__main__":
    main()
