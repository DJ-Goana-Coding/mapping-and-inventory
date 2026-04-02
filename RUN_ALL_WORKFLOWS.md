# HOW TO RUN ALL WORKFLOWS - Step by Step Instructions

## ⚡ Quick Method: GitHub Actions Web Interface

Since the GitHub API is sometimes restricted, the most reliable way to run all workflows is through the GitHub Actions web interface.

### Step 1: Navigate to GitHub Actions
1. Go to: **https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions**
2. You should see a list of workflows on the left sidebar

### Step 2: Run TIA_CITADEL_DEEP_SCAN
1. Click on **"TIA_CITADEL_DEEP_SCAN"** in the left sidebar
2. Click the **"Run workflow"** button (top right, above the workflow runs list)
3. A dropdown will appear:
   - Ensure branch is set to **"main"**
   - Click the green **"Run workflow"** button
4. ✅ The workflow will start running

**What this does:**
- Scans 321GB of data from Google Drive
- Generates `master_intelligence_map.txt`
- Takes approximately 10-15 minutes

### Step 3: Run S10_PUSH_TO_VAULT
1. Click on **"S10_PUSH_TO_VAULT"** in the left sidebar
2. Click the **"Run workflow"** button
3. A dropdown will appear with options:
   - Branch: **"main"**
   - sync_intel: **✓ true** (leave checked)
   - sync_cargo: **✓ true** (leave checked)
   - Click the green **"Run workflow"** button
4. ✅ The workflow will start running

**What this does:**
- Syncs S10 device data to Google Drive vault
- Updates worker status
- Takes approximately 2-5 minutes

### Step 4: Run Sync to HuggingFace Space
1. Click on **"Sync to HuggingFace Space"** in the left sidebar
2. Click the **"Run workflow"** button
3. A dropdown will appear:
   - Ensure branch is set to **"main"**
   - Click the green **"Run workflow"** button
4. ✅ The workflow will start running

**What this does:**
- Deploys the dashboard to HuggingFace Spaces
- Updates https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory
- Takes approximately 1-2 minutes for GitHub action + 3-5 minutes for HuggingFace rebuild

---

## 📊 Monitoring Workflow Progress

### View Running Workflows
1. Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. You'll see all recent workflow runs with their status:
   - 🟡 Yellow dot = In Progress
   - 🟢 Green checkmark = Success
   - 🔴 Red X = Failed

### View Detailed Logs
1. Click on any workflow run to see details
2. Click on the job name (e.g., "heavy_lift", "sync-to-hub", "s10_uplink")
3. Click on any step to see its logs
4. You can download logs using the gear icon ⚙️ in the top right

### Using GitHub CLI (Alternative)
If you have `gh` CLI installed and authenticated:

```bash
# List recent runs
gh run list --limit 10

# Watch a specific run
gh run watch <run-id>

# View logs for a run
gh run view <run-id> --log
```

---

## 🔧 Troubleshooting

### "Workflow run failed immediately"
**Likely cause:** Missing secrets (RCLONE_CONFIG_DATA or HF_TOKEN)

**Solution:**
1. Go to: Settings → Secrets and variables → Actions
2. Verify these secrets exist:
   - `RCLONE_CONFIG_DATA` (for TIA_CITADEL_DEEP_SCAN and S10_PUSH_TO_VAULT)
   - `HF_TOKEN` (for Sync to HuggingFace Space)
3. See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for instructions on creating secrets

### "No workflows appear in the Actions tab"
**Solution:** Workflows are only visible from the main branch. Make sure you're viewing:
https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions

### "Run workflow button is greyed out"
**Likely cause:** You don't have write permissions to the repository

**Solution:** Contact the repository owner to grant you write access, or ask them to run the workflows for you

### "TIA_CITADEL_DEEP_SCAN validation fails"
**Error message:** "RCLONE_CONFIG_DATA secret is empty or missing"

**Solution:**
1. Generate rclone config locally: `rclone config`
2. Configure a Google Drive remote named `gdrive`
3. Copy the config: `cat ~/.config/rclone/rclone.conf`
4. Add it as a GitHub secret:
   - Go to: Settings → Secrets and variables → Actions → New repository secret
   - Name: `RCLONE_CONFIG_DATA`
   - Value: Paste your entire rclone.conf content

---

## ✅ Success Indicators

### TIA_CITADEL_DEEP_SCAN Success
- ✅ Green checkmark in Actions tab
- ✅ New commit with message: "🔭 TIA Deep Scan (Section 142): Update intelligence map [automated]"
- ✅ `master_intelligence_map.txt` updated in the repository
- ✅ Artifact `intelligence-map` available for download

### S10_PUSH_TO_VAULT Success
- ✅ Green checkmark in Actions tab
- ✅ New commit with message: "📱 S10 Push: Update sync status [automated]"
- ✅ `worker_status.json` updated with latest sync timestamp
- ✅ Artifact `s10-push-report` available for download

### Sync to HuggingFace Space Success
- ✅ Green checkmark in Actions tab
- ✅ Message: "✅ Successfully pushed to HuggingFace"
- ✅ HuggingFace Space rebuilds and deploys
- ✅ Dashboard accessible at: https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory

---

## 📝 Summary

To bring everything up to date, you need to:

1. ✅ Run **TIA_CITADEL_DEEP_SCAN** → Updates intelligence map
2. ✅ Run **S10_PUSH_TO_VAULT** → Syncs device data
3. ✅ Run **Sync to HuggingFace Space** → Deploys dashboard

All workflows can be triggered from:
**https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions**

Total time: ~15-20 minutes for all workflows to complete

---

**For more detailed information, see:**
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete workflow documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Full deployment process
- [README.md](README.md) - Project overview

---

**Last Updated:** 2026-04-02
