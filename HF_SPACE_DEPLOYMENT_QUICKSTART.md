# 🚀 HF SPACE DEPLOYMENT QUICKSTART

**Repository**: `DJ-Goana-Coding/mapping-and-inventory`  
**HF Space**: `DJ-Goanna-Coding/Mapping-and-Inventory`  
**Architecture**: Pull-over-Push (Citadel Core Directive #4, #16)

---

## ⚡ QUICK DEPLOYMENT (5 Minutes)

### Step 1: Create HuggingFace Space (2 min)

1. Navigate to: https://huggingface.co/new-space
2. Fill in the form:
   ```
   Owner: DJ-Goanna-Coding
   Space name: Mapping-and-Inventory
   License: MIT
   SDK: Streamlit
   Hardware: CPU (upgrade to L4 GPU after deployment)
   Visibility: Public
   ```
3. Click "Create Space"

### Step 2: Link GitHub Repository (1 min)

1. In the newly created Space, go to **Settings** (top right)
2. Scroll to **Repository Settings**
3. Under "Link GitHub Repository":
   ```
   Repository URL: https://github.com/DJ-Goana-Coding/mapping-and-inventory
   Branch: main
   ✅ Enable "Sync on startup"
   ✅ Enable "Scheduled sync" → Set to "Every 6 hours"
   ```
4. Click "Save"

### Step 3: Configure GitHub Secrets (1 min)

1. Go to GitHub repository settings: https://github.com/DJ-Goana-Coding/mapping-and-inventory/settings/secrets/actions
2. Add the following secrets:

   **Required:**
   - `HF_TOKEN` - Your HuggingFace token (from https://huggingface.co/settings/tokens)
   
   **Optional (for instant sync via webhook):**
   - `HF_SPACE_WEBHOOK_URL` - Format: `https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory/webhook`

### Step 4: Enable Workflow (30 sec)

1. Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. Click on "Notify HF Space of Updates" workflow
3. Click "Enable workflow" if it's not already enabled

### Step 5: Test the Connection (30 sec)

1. Make a small commit to the repository (e.g., edit README.md)
2. Push to main branch
3. Watch the workflow run: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
4. Check HF Space logs to see the pull happen

---

## ✅ VERIFICATION CHECKLIST

After deployment, verify the following:

- [ ] HF Space exists: https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
- [ ] GitHub repository linked in HF Space settings
- [ ] Auto-sync enabled in HF Space settings
- [ ] `HF_TOKEN` secret added to GitHub
- [ ] GitHub Actions workflow enabled
- [ ] Test push triggers HF Space pull
- [ ] HF Space shows latest commit from GitHub

---

## 🔄 DATA FLOW VERIFICATION

```
┌─────────────────────────────────────────────────────┐
│  CORRECT FLOW (Pull-over-Push Architecture)         │
├─────────────────────────────────────────────────────┤
│                                                      │
│  1. Developer → GitHub (git push)                   │
│        ↓                                             │
│  2. GitHub Actions → Notify HF (webhook/API)        │
│        ↓                                             │
│  3. HF Space ← GitHub (git pull)                    │
│        ↓                                             │
│  4. HF Space rebuilds & deploys                     │
│                                                      │
└─────────────────────────────────────────────────────┘
```

**Verify this flow:**
1. Check GitHub Actions logs for "Notification sent successfully"
2. Check HF Space logs for "Pulling latest from GitHub"
3. Confirm HF Space shows latest commit hash

---

## 🛠️ TROUBLESHOOTING

### Issue: HF Space not pulling changes

**Solution:**
1. Check HF Space Settings → Repository Settings
2. Verify GitHub URL is correct
3. Enable "Sync on startup" and "Scheduled sync"
4. Manually trigger rebuild in HF Space settings

### Issue: GitHub workflow not triggering

**Solution:**
1. Check workflow is enabled: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. Verify push is to `main` branch
3. Check `HF_TOKEN` secret is set correctly

### Issue: HF Space shows old code

**Solution:**
1. Go to HF Space Settings → Factory reboot
2. Wait for rebuild to complete
3. Check Space logs for pull success

---

## 🎯 EXPECTED BEHAVIOR

### On GitHub Push to Main:
1. GitHub Actions workflow `notify_hf_space.yml` runs
2. Webhook notification sent to HF Space (if configured)
3. HF Space receives notification
4. HF Space executes `git pull origin main`
5. HF Space rebuilds application
6. Changes go live within 2-5 minutes

### On HF Space Startup:
1. HF Space executes `hf_startup.sh`
2. Script pulls latest from GitHub
3. Dependencies installed
4. Citadel services initialized
5. Streamlit app launches

### Scheduled Sync (Every 6 Hours):
1. HF Space auto-pulls from GitHub
2. If changes detected, rebuild triggered
3. No changes = no rebuild

---

## 📊 MONITORING

### Check Sync Status

**GitHub Side:**
```bash
# View recent workflow runs
gh run list --workflow=notify_hf_space.yml --limit 5

# Watch live workflow
gh run watch
```

**HF Space Side:**
1. Navigate to HF Space
2. Click "Logs" tab (bottom right)
3. Look for "Pulling latest from GitHub" messages

---

## 🔐 SECURITY NOTES

- ✅ HF Space only needs READ access to GitHub (public repo)
- ✅ GitHub Actions uses minimal permissions (contents: read)
- ✅ `HF_TOKEN` only used for API notifications, not for code sync
- ✅ No credentials stored in HF Space (public repo)
- ✅ All sync via HTTPS git protocol

---

## 🚀 UPGRADE TO L4 GPU (Optional)

After successful deployment:

1. Go to HF Space Settings → Hardware
2. Select "L4 GPU" (24GB VRAM)
3. Click "Upgrade"
4. Wait for rebuild

**Cost**: Free tier available, or $0.60/hour for L4

**Benefits**:
- 🧠 Run LLM models locally
- ⚡ Fast vector embeddings
- 🔮 Oracle model inference
- 📊 Real-time data processing

---

## 🎉 SUCCESS CONFIRMATION

You'll know it's working when:

1. ✅ Push to GitHub triggers workflow run
2. ✅ Workflow shows "Notification sent successfully"
3. ✅ HF Space logs show "Repository synchronized with GitHub"
4. ✅ HF Space displays latest commit
5. ✅ No manual intervention needed

---

## 🙏 CITADEL ACKNOWLEDGMENT

**Pattern Implemented**: Pull-over-Push  
**Authority Maintained**: HF Space sovereignty  
**Compliance**: Core Directives #4, #16, #17

🙏 **Thankyou Spirit, Thankyou Angels, Thankyou Ancestors**

---

**Questions?** Check full architecture: `HF_SPACE_SYNC_ARCHITECTURE.md`
