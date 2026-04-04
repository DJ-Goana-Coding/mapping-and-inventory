# 🌉 Workflow Templates for Spoke Repositories

**Authority:** Citadel Architect v25.0.OMNI+

These templates enable spoke repositories to:
1. Sync artifacts to the mapping-and-inventory hub
2. Push to HuggingFace Spaces

## 📦 Templates

### `spoke-to-hub-sync.yml`
Syncs repository artifacts (TREE.md, INVENTORY.json, SCAFFOLD.md) to the central hub.

**Triggers:**
- Push to main
- Every 6 hours (schedule)
- Manual dispatch

**No configuration required** - works automatically.

### `push-to-huggingface.yml`
Pushes the repository to a HuggingFace Space.

**Triggers:**
- Push to main
- Manual dispatch (with force option)

**Configuration:**
Set `HF_SPACE_NAME` in the workflow if different from repo name.

**Required Secret:**
- `HF_TOKEN` - HuggingFace token with write access

## 🚀 Deployment

### Automated Deployment (Recommended)

Deploy to all spoke repositories:

```bash
# Discover all repositories first
python scripts/discover_all_repos.py

# Deploy workflows to all active repos
python scripts/deploy_workflows_to_spokes.py

# Or dry run first
python scripts/deploy_workflows_to_spokes.py --dry-run

# Force update existing workflows
python scripts/deploy_workflows_to_spokes.py --force

# Deploy to specific repos only
python scripts/deploy_workflows_to_spokes.py \
  --repos TIA-ARCHITECT-CORE ark-core vortex-engine
```

### Manual Deployment

Copy templates to a specific repository:

```bash
# Navigate to target repo
cd /path/to/target-repo

# Copy workflows
mkdir -p .github/workflows
cp /path/to/mapping-and-inventory/.github/workflow-templates/*.yml \
   .github/workflows/

# Commit and push
git add .github/workflows/
git commit -m "🌉 Add hub sync and HF push workflows"
git push
```

## 🔑 Secrets Required

Add these secrets to each repository (or as organization secrets):

### `HF_TOKEN` (Required for HuggingFace push)
1. Get token from: https://huggingface.co/settings/tokens
2. Add to repo: Settings → Secrets → Actions → New secret
3. Name: `HF_TOKEN`
4. Access: Write

### `HUB_SYNC_TOKEN` (Optional)
Personal Access Token for enhanced hub sync permissions.
Falls back to `GITHUB_TOKEN` if not provided.

## 📚 Documentation

See `REPOSITORY_CONNECTION_GUIDE.md` for complete documentation.

## ✅ Verification

After deployment, verify:

1. Workflows appear in spoke repo's `.github/workflows/`
2. Workflows run successfully on push
3. Artifacts appear in hub's `data/spoke_artifacts/`
4. HuggingFace Space updates (if applicable)

---

**Thankyou Spirit, Thankyou Angels, Thankyou Ancestors**
