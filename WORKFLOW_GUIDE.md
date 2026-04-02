# CITADEL OMEGA - Workflow Execution Guide

## Overview

This repository contains three active workflows that keep the CITADEL OMEGA intelligence system up to date:

1. **TIA_CITADEL_DEEP_SCAN** - Scans 321GB of data across 5 partitions
2. **S10_PUSH_TO_VAULT** - Syncs S10 device data to the vault
3. **Sync to HuggingFace Space** - Deploys the dashboard to HuggingFace

## Quick Start - Run All Workflows

### Method 1: Using the Trigger Script (Local)

```bash
# Make the script executable
chmod +x trigger_all_workflows.sh

# Run all workflows
./trigger_all_workflows.sh
```

### Method 2: Using GitHub Actions Web Interface

1. Navigate to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. For each workflow:
   - Click on the workflow name
   - Click "Run workflow" button
   - Select branch: `main`
   - Click "Run workflow"

### Method 3: Using GitHub CLI (gh)

```bash
# Trigger TIA_CITADEL_DEEP_SCAN
gh workflow run tia_citadel_deep_scan.yml --ref main

# Trigger S10_PUSH_TO_VAULT with inputs
gh workflow run s10_push_to_vault.yml --ref main \
  -f sync_intel=true \
  -f sync_cargo=true

# Trigger Sync to HuggingFace
gh workflow run sync_to_hf.yml --ref main
```

### Method 4: Using curl (API)

```bash
# Set your GitHub token
export GITHUB_TOKEN="your_github_token_here"

# Trigger TIA_CITADEL_DEEP_SCAN
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/DJ-Goana-Coding/mapping-and-inventory/actions/workflows/tia_citadel_deep_scan.yml/dispatches \
  -d '{"ref":"main"}'

# Trigger S10_PUSH_TO_VAULT
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/DJ-Goana-Coding/mapping-and-inventory/actions/workflows/s10_push_to_vault.yml/dispatches \
  -d '{"ref":"main","inputs":{"sync_intel":"true","sync_cargo":"true"}}'

# Trigger Sync to HuggingFace
curl -X POST \
  -H "Accept: application/vnd.github.v3+json" \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/DJ-Goana-Coding/mapping-and-inventory/actions/workflows/sync_to_hf.yml/dispatches \
  -d '{"ref":"main"}'
```

## Workflow Details

### 1. TIA_CITADEL_DEEP_SCAN

**Purpose**: Scans 321GB of data from Google Drive using Section 142 Cycle methodology

**Trigger**: Manual dispatch only (`workflow_dispatch`)

**Requirements**:
- `RCLONE_CONFIG_DATA` secret must be configured
- Must contain `[gdrive]` remote configuration

**What it does**:
- Scans 5 partitions sequentially:
  1. GDrive Root (GENESIS_VAULT)
  2. Oppo Cargo
  3. S10 Cargo
  4. CITADEL_OMEGA_INTEL
  5. Laptop Cargo
- Generates `master_intelligence_map.txt`
- Uses metadata-only extraction (no downloads)
- Clears cache between partitions to avoid disk overflow

**Outputs**:
- `master_intelligence_map.txt` (committed to repo)
- Artifact: `intelligence-map`

**Duration**: ~10-15 minutes (metadata extraction only)

---

### 2. S10_PUSH_TO_VAULT

**Purpose**: Syncs S10 device data to Google Drive vault

**Trigger**: Manual dispatch with optional inputs

**Inputs**:
- `sync_intel` (boolean, default: true) - Sync S10_CITADEL_OMEGA_INTEL
- `sync_cargo` (boolean, default: true) - Sync Research/S10 cargo

**Requirements**:
- `RCLONE_CONFIG_DATA` secret must be configured

**What it does**:
- Syncs `S10_CITADEL_OMEGA_INTEL/` → `gdrive:CITADEL_OMEGA_INTEL`
- Syncs `Research/S10/` → `gdrive:GENESIS_VAULT/S10_CARGO`
- Updates `worker_status.json` with sync timestamp
- Generates sync report

**Outputs**:
- Updated `worker_status.json` (committed to repo)
- Artifact: `s10-push-report`

**Duration**: ~2-5 minutes (depends on data size)

---

### 3. Sync to HuggingFace Space

**Purpose**: Deploys the T.I.A. Citadel Omega Dashboard to HuggingFace Spaces

**Trigger**: 
- Automatic on push to `main` branch
- Manual dispatch available

**Requirements**:
- `HF_TOKEN` secret with Write permissions

**What it does**:
- Clones the repository
- Force pushes to `https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory`
- HuggingFace automatically rebuilds and redeploys the Space

**Outputs**:
- Live dashboard at: https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory

**Duration**: ~1-2 minutes (GitHub action) + ~3-5 minutes (HuggingFace rebuild)

---

## Monitoring Workflows

### View Recent Runs

```bash
gh run list --limit 10
```

### Watch a Running Workflow

```bash
# Get the run ID from 'gh run list'
gh run watch <run-id>
```

### View Workflow Logs

```bash
gh run view <run-id> --log
```

### Check Workflow Status via Web

Navigate to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions

---

## Recommended Execution Order

To bring the entire system up to date, run workflows in this order:

1. **TIA_CITADEL_DEEP_SCAN** - Updates intelligence map from all sources
2. **S10_PUSH_TO_VAULT** - Pushes any local S10 data to vault
3. **Sync to HuggingFace** - Deploys updated dashboard (auto-triggers on merge to main)

---

## Troubleshooting

### TIA_CITADEL_DEEP_SCAN fails at validation

**Problem**: "RCLONE_CONFIG_DATA secret is empty or missing"

**Solution**: 
1. Generate rclone config: `rclone config`
2. Configure Google Drive remote named `gdrive`
3. Copy config: `cat ~/.config/rclone/rclone.conf`
4. Add as GitHub secret: Settings → Secrets → Actions → New secret
   - Name: `RCLONE_CONFIG_DATA`
   - Value: Paste entire config file content

### S10_PUSH_TO_VAULT shows "No files to sync"

**Problem**: Directories are empty or only contain README.md

**Solution**: This is expected if no new S10 data has been added. The workflow will skip syncing.

### Sync to HuggingFace fails with push error

**Problem**: "Push failed - may need force push or branch protection bypass"

**Solution**: 
1. Check that `HF_TOKEN` secret is configured
2. Verify token has Write permissions
3. The workflow uses `--force` push, so this usually works

### API 403 Forbidden errors

**Problem**: GitHub API calls return 403 in certain environments

**Solution**: Use the GitHub Actions web interface instead:
1. Go to https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. Click on workflow name
3. Click "Run workflow" button

---

## Secrets Required

| Secret | Required For | Permissions | Where to Get |
|--------|-------------|-------------|--------------|
| `RCLONE_CONFIG_DATA` | TIA_CITADEL_DEEP_SCAN, S10_PUSH_TO_VAULT | Read/Write access to Google Drive | `rclone config` command |
| `HF_TOKEN` | Sync to HuggingFace Space | Write permissions | HuggingFace Settings → Access Tokens |
| `VOID_ORACLE_KEY` | (Optional) Evidence Fragment Scraper | Read access to Gemini API | Google AI Studio |
| `GOOGLE_SHEETS_CREDENTIALS` | (Optional) Worker Reporter | Read/Write to Google Sheets | Google Cloud Console |

---

## Additional Resources

- **DEPLOYMENT_GUIDE.md** - Full deployment process
- **README.md** - Project overview and setup
- **SECTION_142_CYCLE_IMPLEMENTATION.md** - Deep scan methodology
- **TIA_MASTER_HARVEST.txt** - Harvest automation documentation

---

## Notes

- All workflows run on `ubuntu-latest` runners
- Workflows use Node.js 24 for JavaScript actions
- Cache is cleared between partitions in TIA_CITADEL_DEEP_SCAN
- All workflows commit and push results back to the repository
- Disk usage is monitored throughout execution

---

**Last Updated**: 2026-04-02
**Maintained by**: CITADEL OMEGA Architecture Division
