# ✅ ACTION CHECKLIST: Bring Everything Up to Date

## 🎯 Your Mission
Run all 3 workflows to update the entire CITADEL OMEGA system.

---

## 📋 Step-by-Step Checklist

### ☑️ Step 1: Navigate to GitHub Actions
- [ ] Open browser and go to: **https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions**

### ☑️ Step 2: Run TIA_CITADEL_DEEP_SCAN (First)
- [ ] Click **"TIA_CITADEL_DEEP_SCAN"** in left sidebar
- [ ] Click **"Run workflow"** button (top right)
- [ ] Select branch: **main**
- [ ] Click green **"Run workflow"** button
- [ ] ⏱️ Wait ~10-15 minutes for completion

### ☑️ Step 3: Run S10_PUSH_TO_VAULT (Second)
- [ ] Click **"S10_PUSH_TO_VAULT"** in left sidebar
- [ ] Click **"Run workflow"** button
- [ ] Select branch: **main**
- [ ] Keep both checkboxes checked (sync_intel ✓, sync_cargo ✓)
- [ ] Click green **"Run workflow"** button
- [ ] ⏱️ Wait ~2-5 minutes for completion

### ☑️ Step 4: Run Sync to HuggingFace Space (Third)
- [ ] Click **"Sync to HuggingFace Space"** in left sidebar
- [ ] Click **"Run workflow"** button
- [ ] Select branch: **main**
- [ ] Click green **"Run workflow"** button
- [ ] ⏱️ Wait ~1-2 minutes for completion
- [ ] ⏱️ Wait additional ~3-5 minutes for HuggingFace rebuild

### ☑️ Step 5: Verify Success
- [ ] All 3 workflows show green checkmark ✅ in Actions tab
- [ ] New commits appear in repository for TIA_CITADEL_DEEP_SCAN and S10_PUSH_TO_VAULT
- [ ] Visit https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory to confirm dashboard is live

---

## 🚨 Quick Troubleshooting

**If a workflow fails:**
1. Click on the failed workflow run
2. Read the error message in the logs
3. Common issues:
   - ❌ **Missing RCLONE_CONFIG_DATA secret** → See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for setup
   - ❌ **Missing HF_TOKEN secret** → Add token with Write permissions in Settings → Secrets
   - ❌ **Permission denied** → Ask repository owner for write access

---

## ✅ Done!

Once all checkboxes are completed:
- ✅ Intelligence map is updated (master_intelligence_map.txt)
- ✅ S10 data is synced to vault (worker_status.json updated)
- ✅ Dashboard is deployed to HuggingFace
- ✅ **CITADEL OMEGA is fully up to date!**

---

**Need help?** See [RUN_ALL_WORKFLOWS.md](RUN_ALL_WORKFLOWS.md) for detailed instructions.
