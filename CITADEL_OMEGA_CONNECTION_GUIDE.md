# 🌉 CITADEL_OMEGA Connection Guide

**Generated:** 2026-04-05T04:40:00Z  
**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Ready for Connection

---

## 🎯 Overview

This guide provides step-by-step instructions for connecting the CITADEL_OMEGA repository to the mapping-and-inventory hub.

---

## 🚀 Quick Start (Recommended)

### Option 1: Automated Deployment from mapping-and-inventory

**Prerequisites:**
- GitHub token with `repo` and `workflow` permissions
- Access to both DJ-Goana-Coding/CITADEL_OMEGA and DJ-Goana-Coding/mapping-and-inventory

**Steps:**

```bash
# 1. Set GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# 2. Navigate to mapping-and-inventory repository
cd /path/to/mapping-and-inventory

# 3. Run discovery (if registry doesn't exist)
python scripts/discover_all_repos.py

# 4. Deploy workflows to CITADEL_OMEGA specifically
python scripts/deploy_workflows_to_spokes.py --repos CITADEL_OMEGA

# 5. Verify deployment
cat workflow_deployment_report.json | jq '.deployments[] | select(.repo == "CITADEL_OMEGA")'
```

**What this does:**
- Automatically creates `.github/workflows/spoke-to-hub-sync.yml` in CITADEL_OMEGA
- Automatically creates `.github/workflows/push-to-huggingface.yml` in CITADEL_OMEGA
- Commits the workflows to CITADEL_OMEGA via GitHub API
- Updates the repository registry

---

## 📋 Option 2: Manual Workflow Setup

If you prefer to manually set up the connection:

### Step 1: Add Workflows to CITADEL_OMEGA

**In the CITADEL_OMEGA repository:**

```bash
# Create workflows directory
mkdir -p .github/workflows

# Download spoke-to-hub-sync workflow
curl https://raw.githubusercontent.com/DJ-Goana-Coding/mapping-and-inventory/main/.github/workflow-templates/spoke-to-hub-sync.yml \
  -o .github/workflows/spoke-to-hub-sync.yml

# Download HuggingFace push workflow (optional)
curl https://raw.githubusercontent.com/DJ-Goana-Coding/mapping-and-inventory/main/.github/workflow-templates/push-to-huggingface.yml \
  -o .github/workflows/push-to-huggingface.yml

# Commit and push
git add .github/workflows/
git commit -m "🌉 Connect to mapping-and-inventory hub"
git push
```

### Step 2: Verify Required Artifacts Exist

CITADEL_OMEGA should have these files (create if missing):

```bash
# In CITADEL_OMEGA repository

# 1. TREE.md - Directory structure
# Generate if missing:
tree -L 3 > TREE.md

# 2. INVENTORY.json - Entity registry
# Create basic structure if missing:
cat > INVENTORY.json << 'EOF'
{
  "version": "1.0.0",
  "repository": "CITADEL_OMEGA",
  "components": {
    "omega_trader": "Trading operations hub",
    "omega_bots": "AI trading agents",
    "omega_scout": "API connectors and security",
    "omega_archive": "Strategy library and RAG",
    "models": "ML models directory",
    "datasets": "Trading datasets",
    "libraries": "Trading libraries",
    "tools": "Utilities",
    "genesis": "Foundation"
  },
  "last_updated": "2026-04-05T04:40:00Z"
}
EOF

# 3. SCAFFOLD.md - Architecture blueprint
# Copy from documentation:
cp CITADEL_OMEGA_ARCHITECTURE.md SCAFFOLD.md

# 4. system_manifest.json - System metadata
cat > system_manifest.json << 'EOF'
{
  "name": "CITADEL_OMEGA",
  "version": "1.0.0",
  "type": "trading_hub",
  "status": "active",
  "components": 9,
  "last_updated": "2026-04-05T04:40:00Z"
}
EOF

# 5. Commit artifacts
git add TREE.md INVENTORY.json SCAFFOLD.md system_manifest.json
git commit -m "📦 Add hub sync artifacts"
git push
```

---

## 🔑 Secrets Configuration

### For HuggingFace Push (Optional)

If you want CITADEL_OMEGA to automatically push to HuggingFace Spaces:

**Add to CITADEL_OMEGA repository secrets:**

1. Go to: `https://github.com/DJ-Goana-Coding/CITADEL_OMEGA/settings/secrets/actions`
2. Click "New repository secret"
3. Name: `HF_TOKEN`
4. Value: Get from https://huggingface.co/settings/tokens (needs "Write" access)
5. Click "Add secret"

**Or use Organization Secret (recommended):**

1. Go to: `https://github.com/organizations/DJ-Goana-Coding/settings/secrets/actions`
2. Create `HF_TOKEN` organization secret
3. Grant access to CITADEL_OMEGA

### For Enhanced Hub Sync (Optional)

Add `HUB_SYNC_TOKEN` with `repo` + `workflow` scopes if you need enhanced permissions beyond the default `GITHUB_TOKEN`.

---

## ✅ Verification Steps

### 1. Confirm Workflows Deployed

Check CITADEL_OMEGA Actions page:
```
https://github.com/DJ-Goana-Coding/CITADEL_OMEGA/actions
```

You should see:
- ✅ "Spoke to Mapping Hub" workflow
- ✅ "Push to HuggingFace" workflow (if added)

### 2. Trigger Test Sync

**Option A: Push to CITADEL_OMEGA**
```bash
# In CITADEL_OMEGA repository
git commit --allow-empty -m "Test hub sync"
git push
```

**Option B: Manual Workflow Dispatch**
1. Go to: `https://github.com/DJ-Goana-Coding/CITADEL_OMEGA/actions`
2. Select "Spoke to Mapping Hub"
3. Click "Run workflow"
4. Click "Run workflow" button

### 3. Verify in mapping-and-inventory

**Check artifacts directory:**
```bash
# In mapping-and-inventory repository
ls -la data/spoke_artifacts/CITADEL_OMEGA/
```

Should contain:
- `TREE.md`
- `INVENTORY.json`
- `SCAFFOLD.md`
- `system_manifest.json`
- `README.md`
- `sync_metadata.json`

**Check spoke registry:**
```bash
cat data/spoke_sync_registry.json | jq '.spokes["CITADEL_OMEGA"]'
```

Should show:
```json
{
  "name": "CITADEL_OMEGA",
  "url": "https://github.com/DJ-Goana-Coding/CITADEL_OMEGA",
  "last_sync": "2026-04-05T04:40:00Z",
  "commit_sha": "abc123...",
  "artifacts_count": "5",
  "sync_count": 1
}
```

### 4. Verify Agent Configuration

**In mapping-and-inventory:**
```bash
cat .github/agents/citadel-omega.agent.md
```

Should contain CITADEL_OMEGA agent identity and operational directives.

---

## 🔄 Sync Behavior

### Automatic Triggers

The spoke-to-hub-sync workflow runs:
- ✅ On every push to main branch
- ✅ Every 6 hours (scheduled: 0 */6 * * *)
- ✅ Manual dispatch available

### What Gets Synced

Each sync collects and sends:
1. **TREE.md** - Directory structure
2. **INVENTORY.json** - Component registry
3. **SCAFFOLD.md** - Architecture blueprint
4. **system_manifest.json** - System metadata
5. **README.md** - Documentation

### Sync Process

```
1. CITADEL_OMEGA workflow collects artifacts
2. Workflow sends repository_dispatch to mapping-and-inventory
3. mapping-and-inventory spoke_sync_receiver.yml receives event
4. Hub downloads artifacts via GitHub API
5. Hub updates data/spoke_sync_registry.json
6. Hub commits artifacts to data/spoke_artifacts/CITADEL_OMEGA/
```

---

## 🌐 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│           DJ-Goana-Coding/CITADEL_OMEGA (Spoke)              │
│                                                              │
│  Push to main → .github/workflows/spoke-to-hub-sync.yml     │
│                           │                                  │
│                           ├─ Collect artifacts              │
│                           ├─ Create metadata                │
│                           └─ Send repository_dispatch       │
│                                                              │
│  .github/agents/citadel-omega.agent.md (exists in hub)      │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           │ repository_dispatch event
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│      DJ-Goana-Coding/mapping-and-inventory (Hub)            │
│                                                              │
│  .github/workflows/spoke_sync_receiver.yml                  │
│                           │                                  │
│                           ├─ Receive dispatch               │
│                           ├─ Download artifacts             │
│                           ├─ Update registry                │
│                           └─ Commit to repo                 │
│                                                              │
│  data/spoke_artifacts/CITADEL_OMEGA/                        │
│  ├── TREE.md                                                │
│  ├── INVENTORY.json                                         │
│  ├── SCAFFOLD.md                                            │
│  ├── system_manifest.json                                   │
│  ├── README.md                                              │
│  └── sync_metadata.json                                     │
│                                                              │
│  data/spoke_sync_registry.json                              │
│  └── spokes["CITADEL_OMEGA"] = {...}                        │
│                                                              │
│  .github/agents/citadel-omega.agent.md                      │
│  └── Agent identity and directives                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Troubleshooting

### Problem: Workflow not triggering

**Solutions:**
1. Verify workflow file exists in `.github/workflows/`
2. Check GitHub Actions is enabled for CITADEL_OMEGA
3. Verify branch name is `main` (not `master`)
4. Check workflow syntax with: `gh workflow view spoke-to-hub-sync.yml`

### Problem: Hub not receiving sync

**Solutions:**
1. Check spoke workflow logs in CITADEL_OMEGA Actions
2. Verify `repository_dispatch` event was sent
3. Check hub receiver workflow logs in mapping-and-inventory
4. Ensure `GITHUB_TOKEN` or `HUB_SYNC_TOKEN` has permissions

### Problem: Artifacts not found

**Solutions:**
1. Ensure required files exist in CITADEL_OMEGA
2. Check file names match exactly (case-sensitive)
3. Verify files are in repository root (not subdirectories)
4. Check workflow logs for collection errors

### Problem: HuggingFace push fails

**Solutions:**
1. Verify `HF_TOKEN` secret is configured
2. Check token has "Write" permissions
3. Verify HuggingFace Space exists at target URL
4. Check Space name configuration in workflow
5. Remember: GitHub = DJ-Goana-Coding, HuggingFace = DJ-Goanna-Coding (double 'n')

---

## 📊 Monitoring

### View Sync Status

```bash
# In mapping-and-inventory
cat data/spoke_sync_registry.json | jq '.spokes["CITADEL_OMEGA"]'
```

### View Sync History

```bash
# In mapping-and-inventory
git log --oneline -- data/spoke_artifacts/CITADEL_OMEGA/
```

### Check Workflow Runs

```bash
# CITADEL_OMEGA spoke syncs
gh run list --workflow spoke-to-hub-sync.yml --repo DJ-Goana-Coding/CITADEL_OMEGA

# Hub receiver runs
gh run list --workflow spoke_sync_receiver.yml --repo DJ-Goana-Coding/mapping-and-inventory
```

---

## 🎯 Success Criteria

Connection is successful when:

- ✅ Workflows deployed to CITADEL_OMEGA
- ✅ Required artifacts exist in CITADEL_OMEGA
- ✅ Test sync triggers successfully
- ✅ Artifacts appear in mapping-and-inventory `data/spoke_artifacts/CITADEL_OMEGA/`
- ✅ Registry updated in `data/spoke_sync_registry.json`
- ✅ Agent configuration exists at `.github/agents/citadel-omega.agent.md`
- ✅ No failed workflow runs

---

## 📚 Related Documentation

- `REPOSITORY_CONNECTION_GUIDE.md` - Complete hub sync system guide
- `CITADEL_OMEGA_ARCHITECTURE.md` - CITADEL_OMEGA architecture details
- `.github/agents/citadel-omega.agent.md` - Agent identity file
- `.github/workflow-templates/spoke-to-hub-sync.yml` - Spoke sync template
- `.github/workflow-templates/push-to-huggingface.yml` - HF push template

---

## 🆘 Emergency Commands

### Force Re-sync

```bash
# In CITADEL_OMEGA
gh workflow run spoke-to-hub-sync.yml
```

### Reset Connection

```bash
# In mapping-and-inventory - remove and re-add
rm -rf data/spoke_artifacts/CITADEL_OMEGA/
# Then trigger sync from CITADEL_OMEGA
```

### Verify Connection Infrastructure

```bash
# In mapping-and-inventory
./verify_citadel_omega_connection.sh
```

---

## ✨ Next Steps

After successful connection:

1. **Monitor Initial Syncs**
   - Watch Actions tab in both repositories
   - Verify artifacts update regularly
   - Check for any errors

2. **Configure HuggingFace Push** (Optional)
   - Add `HF_TOKEN` secret
   - Create HuggingFace Spaces if needed
   - Test push workflow

3. **Integrate with Other Systems**
   - TIA-ARCHITECT-CORE for orchestration
   - ARK_CORE for physical node integration
   - HuggingFace Spaces for dashboards

4. **Establish Monitoring**
   - Set up alerts for failed syncs
   - Monitor sync frequency
   - Track artifact changes

---

## 🙏 Completion

**Status:** Connection Guide Complete  
**Authority:** Citadel Architect v25.0.OMNI+  
**Timestamp:** 2026-04-05T04:40:00Z

**Thankyou Spirit, Thankyou Angels, Thankyou Ancestors**

---
