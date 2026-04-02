# 🚀 MASTER BRIDGE DEPLOYMENT GUIDE

**Finalizing mapping-and-inventory as the Faceplate for the 321GB Empire**

---

## 📡 THE RELAY LOGIC

This repository serves as the **Master Bridge** connecting:
- **Local Hardware** (S10, Oppo, Laptop)
- **Google Drive** (321GB GENESIS_VAULT)
- **HuggingFace Space** (Public UI/Faceplate)
- **Other Repositories** (ARK, district repos)

By pushing from this repo, you're turning on the lights across the entire system.

---

## ✅ FINALIZATION CHECKLIST

### 1. ✅ LOCK THE SYNC TARGET
**Status:** COMPLETE

The sync_to_hf.yml workflow is configured with the correct case-sensitive URL:
```yaml
https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory
```

**Verification:**
```bash
grep -A2 "git remote add hf" .github/workflows/sync_to_hf.yml
```

---

### 2. ✅ CONNECT THE DISCONNECTED
**Status:** COMPLETE

The tia_citadel_deep_scan.yml workflow:
- Pulls latest 321GB index from GDrive
- Runs Archivist and Bridge workers
- Commits master_intelligence_map.txt automatically
- Updates worker_status.json

**Key Steps in Workflow:**
```yaml
- name: Deep Scan
  run: rclone lsf gdrive: --max-depth 2 > master_intelligence_map.txt

- name: Commit Intelligence Map to Repository
  run: |
    git add master_intelligence_map.txt
    git commit -m "🗺️ Update master intelligence map"
```

**Manual Trigger:**
```bash
gh workflow run tia_citadel_deep_scan.yml
```

---

### 3. ✅ REBOOT THE FACEPLATE
**Status:** COMPLETE

Slimmed down requirements.txt with pinned versions:
- No GPU bloat (e.g., torch, tensorflow)
- Lightweight dependencies only
- Compatible with HuggingFace Spaces CPU environment

**Before (unpinned, potential bloat):**
```
streamlit>=1.36.0
pandas
huggingface_hub
```

**After (pinned, optimized):**
```
streamlit==1.36.0
pandas==2.0.3
huggingface_hub==0.23.4
```

**This fixes the HuggingFace Runtime Error** by ensuring consistent, lightweight dependencies.

---

### 4. ✅ HIRE THE WORKERS
**Status:** COMPLETE

Workers deployed to Partition_01:
- `citadel_reporter.py` - Google Sheets automation
- `citadel_archivist.py` - MD5 hashing and file organization
- `apps_script_toolbox.py` - Command center for worker operations

**Verification:**
```bash
ls -la Partition_01/citadel_*.py
```

---

### 5. ✅ LINK WORKERS TO APPS SCRIPT
**Status:** COMPLETE

Created `apps_script_toolbox.py` with four main functions:
1. `--identity-strike` - Section 44 audit to Google Sheets
2. `--full-audit` - Complete archive processing
3. `--worker-status` - Health dashboard updates
4. `--verify` - Connection validation

**Test Run:**
```bash
python Partition_01/apps_script_toolbox.py --verify
```

---

## 🔧 DEPLOYMENT STEPS

### Step 1: Verify Local Setup
```bash
# Check we're in the right repo
pwd
# Should show: /path/to/mapping-and-inventory

# Check branch
git branch
# Should show: copilot/push-mapping-inventory-to-huggingface

# Run audit
SKIP_REMOTE_TEST=1 ./citadel_audit.sh
```

### Step 2: Merge to Main Branch
```bash
# Create pull request (if not already created)
gh pr create --title "🏰 Finalize Master Bridge - Connect All Systems" \
  --body "Complete deployment of Master Bridge infrastructure"

# Or merge directly (if you have permissions)
git checkout main
git merge copilot/push-mapping-inventory-to-huggingface
git push origin main
```

### Step 3: Push to HuggingFace
When you push to `main` branch, the `sync_to_hf.yml` workflow automatically:
1. Triggers on push to main
2. Syncs entire repo to HuggingFace Space
3. Deploys updated requirements.txt
4. Restarts the Streamlit app

**Watch the deployment:**
```bash
# View workflow status
gh run watch

# Or check HuggingFace Space directly
# https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory
```

### Step 4: Trigger Data Sync
After deployment, pull the latest 321GB data:
```bash
# Manually trigger the deep scan workflow
gh workflow run tia_citadel_deep_scan.yml

# Watch progress
gh run watch
```

This will:
- Connect to GDrive via rclone
- Pull latest data from all cargo bays
- Generate master_intelligence_map.txt
- Update worker_status.json
- Commit changes back to repo

### Step 5: Verify HuggingFace Space
1. Visit: https://huggingface.co/spaces/DJ-Goana-Coding/Mapping-and-Inventory
2. Check status changes from "Runtime Error" → "Running"
3. Verify the UI displays:
   - File count (1264+)
   - Cargo bay data (S10, Oppo, Laptop)
   - Forensic audit tab with S10_CITADEL_OMEGA_INTEL data

---

## 📊 VISUAL CHECK - "STAINLESS" INDICATORS

### ✅ Success Indicators

**1. HuggingFace Space Status:**
```
Status: Running (green)
Build: Successful
Logs: No errors
```

**2. UI Display:**
```
CITADEL OMEGA — Mapping & Inventory
┌─────────────────────────────────┐
│ Total Files: 1264+              │
│ GDrive Status: Connected        │
│ Last Sync: 2026-04-02 05:54 UTC │
└─────────────────────────────────┘
```

**3. Forensic Audit Tab:**
Shows data from:
- S10_CITADEL_OMEGA_INTEL dataset
- Research/S10 cargo
- Research/Oppo cargo
- Research/Laptop cargo

**4. Repository Files Updated:**
```bash
# These files should have recent timestamps
ls -lt master_intelligence_map.txt
ls -lt worker_status.json
ls -lt archive_index.json
```

---

## 🔥 TROUBLESHOOTING

### Issue: HuggingFace Shows "Runtime Error"
**Solution:**
1. Check Build logs on HuggingFace
2. Verify requirements.txt is optimized (no GPU deps)
3. Check Dockerfile configuration
4. Ensure port 7860 is configured in Streamlit

### Issue: Data Not Showing in UI
**Solution:**
1. Run `gh workflow run tia_citadel_deep_scan.yml`
2. Check workflow logs for errors
3. Verify RCLONE_CONFIG_DATA secret is set
4. Confirm master_intelligence_map.txt was committed

### Issue: Google Sheets Not Updating
**Solution:**
1. Verify GOOGLE_SHEETS_CREDENTIALS secret
2. Share Google Sheets with service account
3. Run `python Partition_01/apps_script_toolbox.py --verify`
4. Check worker_status.json for errors

---

## 🎯 NEXT STEPS AFTER DEPLOYMENT

### 1. Identity Strike Report (Optional)
Generate Section 44 audit in Google Sheets:
```bash
# Run via GitHub Actions or locally
python Partition_01/apps_script_toolbox.py --identity-strike
```

### 2. Monitor Worker Status
Check automated sync operations:
```bash
# View worker status
cat worker_status.json | python -m json.tool
```

### 3. Verify Dataset Links
Ensure S10_CITADEL_OMEGA_INTEL dataset is accessible:
- Check HuggingFace dataset exists
- Verify access permissions
- Test data loading in UI

---

## 🏰 SYSTEM ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────┐
│             HUGGINGFACE SPACE (FACEPLATE)                   │
│         DJ-Goana-Coding/Mapping-and-Inventory               │
│                                                             │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Streamlit   │  │ File Browser │  │ Forensic     │      │
│  │ Dashboard   │  │              │  │ Audit        │      │
│  └─────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────────▲────────────────────────────────────┘
                         │
                    [sync_to_hf.yml]
                         │
┌────────────────────────▼────────────────────────────────────┐
│             GITHUB REPO (MASTER BRIDGE)                     │
│         DJ-Goana-Coding/mapping-and-inventory               │
│                                                             │
│  ┌──────────────────┐  ┌────────────────────────────┐     │
│  │ Workers          │  │ Workflows                  │     │
│  │ - Archivist      │  │ - tia_citadel_deep_scan    │     │
│  │ - Reporter       │  │ - sync_to_hf               │     │
│  │ - Bridge         │  │ - s10_push_to_vault        │     │
│  │ - Hive Master    │  └────────────────────────────┘     │
│  └──────────────────┘                                      │
└────────────────────────▲────────────────────────────────────┘
                         │
                  [tia_citadel_deep_scan.yml]
                         │
┌────────────────────────▼────────────────────────────────────┐
│                 GOOGLE DRIVE (VAULT)                        │
│                   GENESIS_VAULT (321GB)                     │
│                                                             │
│  ┌────────────┐  ┌─────────────┐  ┌──────────────┐        │
│  │ S10_CARGO  │  │ OPPO_CARGO  │  │ LAPTOP_CARGO │        │
│  └────────────┘  └─────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

---

## 📝 COMMAND REFERENCE

### GitHub CLI Commands
```bash
# View workflow runs
gh run list --workflow=sync_to_hf.yml

# Trigger workflow
gh workflow run tia_citadel_deep_scan.yml

# Watch workflow in real-time
gh run watch

# View workflow logs
gh run view <run-id> --log
```

### Worker Commands
```bash
# Verify connections
python Partition_01/apps_script_toolbox.py --verify

# Identity Strike report
python Partition_01/apps_script_toolbox.py --identity-strike

# Full audit
python Partition_01/apps_script_toolbox.py --full-audit

# Update worker status
python Partition_01/apps_script_toolbox.py --worker-status
```

### Audit Commands
```bash
# Full system audit (skip remote tests)
SKIP_REMOTE_TEST=1 ./citadel_audit.sh

# Check for absolute paths
grep -r "/data/" --include="*.py" --include="*.sh" . | grep -v ".git"

# Verify relative paths
grep -r "\./Research" --include="*.py" | wc -l
```

---

## 🎊 COMPLETION CRITERIA

The Master Bridge is fully deployed when:

✅ HuggingFace Space status: **Running**  
✅ UI displays 321GB data summary  
✅ Forensic Audit tab shows S10/Oppo/Laptop data  
✅ master_intelligence_map.txt updates automatically  
✅ worker_status.json shows recent sync times  
✅ Apps Script Toolbox verifies 4/4 connections  
✅ Requirements.txt has no GPU bloat  

---

## 🦎 DJ GOANNA'S FINAL CHECKLIST

**Before you push to main:**
- [ ] Run `SKIP_REMOTE_TEST=1 ./citadel_audit.sh`
- [ ] Verify sync_to_hf.yml has correct URL
- [ ] Check requirements.txt is optimized
- [ ] Ensure workers are in Partition_01
- [ ] Review master_intelligence_map.txt exists

**After pushing to main:**
- [ ] Watch sync_to_hf.yml workflow complete
- [ ] Check HuggingFace Space goes "Running"
- [ ] Trigger tia_citadel_deep_scan.yml
- [ ] Verify data appears in UI
- [ ] Run Identity Strike report (optional)

**543 1010 222 777 ❤️‍🔥**

---

*Ready to hit the master switch? Push to main and watch the Citadel go live.*
