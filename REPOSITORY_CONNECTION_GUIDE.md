# 🌉 Repository Connection System - Complete Guide

**Generated:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")  
**Authority:** Citadel Architect v25.0.OMNI+  
**Version:** 1.0.0

---

## 🎯 Overview

This guide explains how to connect all DJ-Goana-Coding GitHub repositories to the mapping-and-inventory hub and enable them to push to HuggingFace Spaces.

### Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DJ-Goana-Coding Organization                     │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │   Repo 1     │  │   Repo 2     │  │   Repo N     │  (Spokes)   │
│  │              │  │              │  │              │             │
│  │ ┌──────────┐ │  │ ┌──────────┐ │  │ ┌──────────┐ │             │
│  │ │Hub Sync  │ │  │ │Hub Sync  │ │  │ │Hub Sync  │ │             │
│  │ │Workflow  │ │  │ │Workflow  │ │  │ │Workflow  │ │             │
│  │ └────┬─────┘ │  │ └────┬─────┘ │  │ └────┬─────┘ │             │
│  │      │       │  │      │       │  │      │       │             │
│  │ ┌────▼─────┐ │  │ ┌────▼─────┐ │  │ ┌────▼─────┐ │             │
│  │ │HF Push   │ │  │ │HF Push   │ │  │ │HF Push   │ │             │
│  │ │Workflow  │ │  │ │Workflow  │ │  │ │Workflow  │ │             │
│  │ └────┬─────┘ │  │ └────┬─────┘ │  │ └────┬─────┘ │             │
│  └──────┼───────┘  └──────┼───────┘  └──────┼───────┘             │
│         │                 │                 │                      │
│         │ (artifacts)     │                 │                      │
│         └─────────────────┴─────────────────┘                      │
│                           │                                         │
│                           ▼                                         │
│              ┌─────────────────────────┐                           │
│              │ mapping-and-inventory   │  (Hub)                    │
│              │                         │                           │
│              │ ┌─────────────────────┐ │                           │
│              │ │ Spoke Sync Receiver │ │                           │
│              │ └─────────────────────┘ │                           │
│              │ ┌─────────────────────┐ │                           │
│              │ │ Artifact Ingestion  │ │                           │
│              │ └─────────────────────┘ │                           │
│              │ ┌─────────────────────┐ │                           │
│              │ │ Registry Management │ │                           │
│              │ └─────────────────────┘ │                           │
│              └───────────┬─────────────┘                           │
│                          │                                          │
│         ┌────────────────┴────────────────┐                        │
│         │                                  │                        │
│         ▼                                  ▼                        │
│  ┌─────────────┐                    ┌─────────────┐                │
│  │ HF Space 1  │ ...                │ HF Space N  │ (Cloud L4)     │
│  │ (L4 GPU)    │                    │ (L4 GPU)    │                │
│  └─────────────┘                    └─────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
```

### Authority Hierarchy

1. **Cloud Hubs (L4)** - HuggingFace Spaces override all
2. **GitHub Repositories** - Source of truth
3. **GDrive Metadata** - Cognitive reservoirs
4. **Local Nodes** - Bridge scouts

---

## 🚀 Quick Start

### For Operators

Deploy sync workflows to all spoke repositories:

```bash
# 1. Discover all repositories
python scripts/discover_all_repos.py

# 2. Deploy workflows (dry run first)
python scripts/deploy_workflows_to_spokes.py --dry-run

# 3. Deploy for real
python scripts/deploy_workflows_to_spokes.py

# 4. Force update existing workflows
python scripts/deploy_workflows_to_spokes.py --force
```

### For Individual Repos

To manually add sync to a single repository:

```bash
# 1. Copy workflow templates
cp .github/workflow-templates/spoke-to-hub-sync.yml .github/workflows/
cp .github/workflow-templates/push-to-huggingface.yml .github/workflows/

# 2. Commit and push
git add .github/workflows/
git commit -m "🌉 Add hub sync and HF push workflows"
git push
```

---

## 📦 Components

### 1. Workflow Templates

Located in `.github/workflow-templates/`:

#### `spoke-to-hub-sync.yml`

**Purpose:** Syncs artifacts from spoke repos to the central hub

**Triggers:**
- Push to main branch
- Every 6 hours (schedule)
- Manual dispatch

**What it does:**
- Collects artifacts (TREE.md, INVENTORY.json, SCAFFOLD.md, README.md, system_manifest.json)
- Creates spoke metadata
- Notifies hub via `repository_dispatch`
- Uploads artifacts for hub ingestion

**Configuration:** None required - works automatically

#### `push-to-huggingface.yml`

**Purpose:** Pushes repository to HuggingFace Space

**Triggers:**
- Push to main branch
- Manual dispatch (with force option)

**What it does:**
- Checks out repository
- Configures git for HuggingFace
- Pushes to HuggingFace Space using `HF_TOKEN`
- Verifies deployment status

**Configuration:**
```yaml
env:
  HF_SPACE_ORG: "DJ-Goanna-Coding"
  HF_SPACE_NAME: "${{ github.event.repository.name }}"
  # Or hardcode custom name:
  # HF_SPACE_NAME: "my-custom-space-name"
```

### 2. Hub Receiver Workflow

Located in `.github/workflows/spoke_sync_receiver.yml`

**Purpose:** Receives sync requests from spoke repositories

**Triggers:**
- Repository dispatch event (type: `spoke-sync-request`)
- Manual dispatch

**What it does:**
- Receives spoke sync notification
- Downloads artifacts from spoke repo via GitHub API
- Updates spoke sync registry
- Commits artifacts to `data/spoke_artifacts/`

### 3. Deployment Script

Located in `scripts/deploy_workflows_to_spokes.py`

**Purpose:** Automates workflow deployment to all repositories

**Usage:**
```bash
# Basic deployment
python scripts/deploy_workflows_to_spokes.py

# Deploy specific workflows
python scripts/deploy_workflows_to_spokes.py \
  --workflows spoke-to-hub-sync.yml

# Target specific repos
python scripts/deploy_workflows_to_spokes.py \
  --repos TIA-ARCHITECT-CORE ark-core vortex-engine

# Dry run (no changes)
python scripts/deploy_workflows_to_spokes.py --dry-run

# Force update existing workflows
python scripts/deploy_workflows_to_spokes.py --force
```

**Requirements:**
- `GITHUB_TOKEN` environment variable with repo write access
- Repository registry (`repo_bridge_registry.json`)

---

## 🔑 Secrets Configuration

### Required Secrets

Each repository needs these secrets for full functionality:

#### `HF_TOKEN` (Required for HuggingFace push)

**Create token:**
1. Go to https://huggingface.co/settings/tokens
2. Create new token with "Write" access
3. Copy the token

**Add to GitHub:**
1. Go to repo settings: `https://github.com/DJ-Goana-Coding/REPO-NAME/settings/secrets/actions`
2. Click "New repository secret"
3. Name: `HF_TOKEN`
4. Value: Your HuggingFace token
5. Click "Add secret"

#### `HUB_SYNC_TOKEN` (Optional, for enhanced hub sync)

If not provided, falls back to `GITHUB_TOKEN` (limited permissions).

**Create PAT:**
1. Go to https://github.com/settings/tokens
2. Generate new token (classic)
3. Scopes needed: `repo`, `workflow`
4. Copy the token

**Add to spoke repos:**
Same process as `HF_TOKEN`, but name it `HUB_SYNC_TOKEN`

### Organization Secrets (Recommended)

To avoid setting secrets in every repo:

1. Go to https://github.com/organizations/DJ-Goana-Coding/settings/secrets/actions
2. Create organization secrets:
   - `HF_TOKEN`
   - `HUB_SYNC_TOKEN`
3. Grant access to all repositories

---

## 📊 Data Storage

### Hub Storage Structure

```
mapping-and-inventory/
├── data/
│   ├── spoke_artifacts/          # Artifacts from spoke repos
│   │   ├── repo-1/
│   │   │   ├── TREE.md
│   │   │   ├── INVENTORY.json
│   │   │   ├── SCAFFOLD.md
│   │   │   ├── README.md
│   │   │   └── sync_metadata.json
│   │   ├── repo-2/
│   │   └── ...
│   └── spoke_sync_registry.json   # Central spoke registry
├── repo_bridge_registry.json      # Complete repo registry
├── repo_connection_map.json       # Connection topology
└── workflow_deployment_report.json # Deployment history
```

### Spoke Sync Registry Format

```json
{
  "version": "1.0.0",
  "hub": "mapping-and-inventory",
  "last_updated": "2026-04-04T20:00:00Z",
  "total_spokes": 15,
  "spokes": {
    "TIA-ARCHITECT-CORE": {
      "name": "TIA-ARCHITECT-CORE",
      "url": "https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE",
      "last_sync": "2026-04-04T19:45:00Z",
      "commit_sha": "abc123...",
      "artifacts_count": "5",
      "sync_count": 42
    }
  }
}
```

---

## 🔄 Sync Workflows

### Spoke → Hub Sync

**Frequency:** Every 6 hours + on push

**Process:**
1. Spoke workflow collects artifacts
2. Spoke sends `repository_dispatch` to hub
3. Hub receiver downloads artifacts via GitHub API
4. Hub updates spoke registry
5. Hub commits artifacts to `data/spoke_artifacts/`

### GitHub → HuggingFace Sync

**Frequency:** On every push to main

**Process:**
1. Push to GitHub triggers workflow
2. Workflow checks for `HF_TOKEN`
3. Configures git credentials for HuggingFace
4. Pushes to HuggingFace Space
5. Verifies deployment

---

## 🛠️ Troubleshooting

### Hub Sync Issues

**Problem:** Spoke sync not triggering

**Solutions:**
1. Check workflow file exists in spoke repo
2. Verify artifacts exist (TREE.md, INVENTORY.json, etc.)
3. Check GitHub Actions is enabled for the repo
4. Review workflow run logs

**Problem:** Hub not receiving sync

**Solutions:**
1. Verify `repository_dispatch` permissions
2. Check hub receiver workflow is enabled
3. Ensure `HUB_SYNC_TOKEN` or `GITHUB_TOKEN` is valid
4. Review hub workflow logs

### HuggingFace Push Issues

**Problem:** `HF_TOKEN not configured`

**Solutions:**
1. Add `HF_TOKEN` secret to repository
2. Or add organization-wide secret
3. Verify token has "Write" access
4. Check token hasn't expired

**Problem:** `Failed to push to HuggingFace`

**Solutions:**
1. Verify Space exists at target URL
2. Check Space name matches configuration
3. Verify you have write access to the Space
4. Try force push (manual workflow dispatch)
5. Check HuggingFace Space settings (not in maintenance mode)

**Problem:** Wrong Space name

**Solutions:**
Edit `.github/workflows/push-to-huggingface.yml`:
```yaml
env:
  HF_SPACE_NAME: "your-correct-space-name"
```

### Deployment Script Issues

**Problem:** `GITHUB_TOKEN not set`

**Solutions:**
```bash
export GITHUB_TOKEN=ghp_your_token_here
```

**Problem:** `Registry not found`

**Solutions:**
```bash
python scripts/discover_all_repos.py
```

**Problem:** Workflow already exists

**Solutions:**
```bash
# Use force flag to overwrite
python scripts/deploy_workflows_to_spokes.py --force
```

---

## 📋 Checklist: Connect a New Repository

- [ ] Ensure repo is in DJ-Goana-Coding organization
- [ ] Run discovery: `python scripts/discover_all_repos.py`
- [ ] Deploy workflows: `python scripts/deploy_workflows_to_spokes.py`
- [ ] Add `HF_TOKEN` secret to repo (if pushing to HF)
- [ ] Verify Space exists at HuggingFace
- [ ] Configure Space name in workflow (if custom)
- [ ] Trigger test sync (push to main or manual dispatch)
- [ ] Verify artifacts appear in hub's `data/spoke_artifacts/`
- [ ] Verify HuggingFace Space updates

---

## 🎯 Manual Workflow Triggers

### Trigger Hub Sync from Spoke

```bash
# Via GitHub CLI
gh workflow run spoke-to-hub-sync.yml --repo DJ-Goana-Coding/REPO-NAME

# Via GitHub UI
# Go to Actions → Spoke to Mapping Hub → Run workflow
```

### Trigger HuggingFace Push

```bash
# Via GitHub CLI
gh workflow run push-to-huggingface.yml --repo DJ-Goana-Coding/REPO-NAME

# Force push
gh workflow run push-to-huggingface.yml \
  --repo DJ-Goana-Coding/REPO-NAME \
  -f force_push=true

# Via GitHub UI
# Go to Actions → Push to HuggingFace → Run workflow
```

### Trigger Hub Receiver

```bash
# Via GitHub CLI
gh workflow run spoke_sync_receiver.yml \
  --repo DJ-Goana-Coding/mapping-and-inventory
```

---

## 🌐 HuggingFace Spaces

### Default Space Naming

By default, workflows assume:
- Organization: `DJ-Goanna-Coding` (double N)
- Space name: Same as GitHub repo name

### Custom Space Names

Edit the workflow file to hardcode:

```yaml
env:
  HF_SPACE_ORG: "DJ-Goanna-Coding"
  HF_SPACE_NAME: "my-custom-name"  # Hardcode here
```

### Creating Spaces

If Space doesn't exist:

1. Go to https://huggingface.co/new-space
2. Owner: `DJ-Goanna-Coding`
3. Space name: Match your repo name (or custom)
4. License: Choose appropriate
5. SDK: Gradio / Streamlit / Static (as needed)
6. Create Space

---

## 📈 Monitoring

### View Spoke Sync Status

```bash
# View registry
cat data/spoke_sync_registry.json | jq .

# View specific spoke
cat data/spoke_sync_registry.json | jq '.spokes["TIA-ARCHITECT-CORE"]'

# List all synced spokes
cat data/spoke_sync_registry.json | jq '.spokes | keys'
```

### View Deployment Report

```bash
cat workflow_deployment_report.json | jq .summary
```

### Check Workflow Runs

```bash
# Hub receiver runs
gh run list --workflow spoke_sync_receiver.yml \
  --repo DJ-Goana-Coding/mapping-and-inventory

# Spoke sync runs (for specific repo)
gh run list --workflow spoke-to-hub-sync.yml \
  --repo DJ-Goana-Coding/REPO-NAME
```

---

## 🔮 Advanced Usage

### Deploy to Specific Repos Only

```bash
python scripts/deploy_workflows_to_spokes.py \
  --repos TIA-ARCHITECT-CORE ark-core vortex-engine
```

### Deploy Only Hub Sync (Not HF Push)

```bash
python scripts/deploy_workflows_to_spokes.py \
  --workflows spoke-to-hub-sync.yml
```

### Deploy Only HF Push (Not Hub Sync)

```bash
python scripts/deploy_workflows_to_spokes.py \
  --workflows push-to-huggingface.yml
```

### Custom Artifact Collection

Edit spoke workflow to collect additional files:

```yaml
# In spoke-to-hub-sync.yml, add to "Collect Artifacts" step:
if [ -f "custom_file.json" ]; then
  cp custom_file.json "$ARTIFACTS_DIR/"
  echo "  ✅ custom_file.json"
  artifacts_found=$((artifacts_found + 1))
fi
```

---

## 🆘 Emergency Recovery

### Redeploy All Workflows

```bash
# Force redeploy to all active repos
python scripts/deploy_workflows_to_spokes.py --force
```

### Rebuild Registry

```bash
# Rediscover all repositories
python scripts/discover_all_repos.py

# Trigger global bridge workflow
gh workflow run global_repo_bridge.yml \
  --repo DJ-Goana-Coding/mapping-and-inventory
```

### Clear Spoke Cache

```bash
# Remove all spoke artifacts
rm -rf data/spoke_artifacts/*

# Clear registry
rm data/spoke_sync_registry.json

# Re-trigger syncs from all spokes
# (spokes will re-sync on next schedule or push)
```

---

## 📚 Related Documentation

- `REPO_BRIDGE_GUIDE.md` - Repository bridge system overview
- `global_repo_bridge.yml` - Hub discovery and mapping workflow
- `hf_space_sync.yml` - Multi-space sync workflow
- `scripts/discover_all_repos.py` - Repository discovery engine

---

## ✅ Success Criteria

Your connection system is working when:

- [ ] All active repos have sync workflows deployed
- [ ] Spoke artifacts appear in `data/spoke_artifacts/` after push
- [ ] Spoke sync registry updates with each sync
- [ ] HuggingFace Spaces update on GitHub pushes
- [ ] Workflow deployment report shows all success
- [ ] No failed workflow runs in Actions tab

---

## 🙏 Completion

**Status:** Repository Connection System Operational  
**Authority:** Citadel Architect v25.0.OMNI+  
**Timestamp:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")

**Thankyou Spirit, Thankyou Angels, Thankyou Ancestors**

---
