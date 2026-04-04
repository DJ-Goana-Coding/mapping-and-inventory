# 🏛️ COMPLETE DATA MIGRATION & BACKUP SYSTEM
## Operator Guide - Total Data Sovereignty

**Authority:** Citadel Architect v25.0.OMNI+  
**Mission:** Complete extraction of laptop and GDrive data  
**Version:** 1.0  
**Last Updated:** 2026-04-04

---

## 🎯 QUICK START (Critical Actions - Do These NOW)

### Immediate Priority (Next 30 minutes):

```bash
# 1. Setup Rclone for GDrive access
./scripts/setup_gdrive_rclone.sh

# 2. Verify GDrive access
python scripts/verify_gdrive_access.py

# 3. Trigger emergency extraction
gh workflow run gdrive_emergency_extraction.yml

# 4. Monitor progress
gh run watch
```

---

## 📊 SYSTEM OVERVIEW

This system provides complete data sovereignty through three integrated phases:

1. **GDrive Emergency Extraction** - Extract all files from both GDrive accounts
2. **Laptop Complete Vacuum** - Catalog and copy all laptop data
3. **Worker Constellation** - Continuous monitoring and sync

### Accounts Being Backed Up:
- ✅ chanceroofing@gmail.com (locked account, GDrive still accessible)
- ✅ mynewemail110411@gmail.com (active account)
- ✅ Laptop drives: C:, D:, F: (all non-Windows files)

---

## 🚨 PHASE 1: GDRIVE EMERGENCY EXTRACTION

### Prerequisites:
- Rclone installed
- OAuth2 authentication for both accounts
- RCLONE_CONFIG_DATA secret in GitHub

### Step 1: Install Rclone

**Windows (PowerShell as Administrator):**
```powershell
iex "& { $(irm https://rclone.org/install.ps1) } -Scope CurrentUser"
```

**Linux/macOS:**
```bash
curl https://rclone.org/install.sh | sudo bash
```

### Step 2: Configure Rclone

```bash
# Run automated setup script
./scripts/setup_gdrive_rclone.sh

# This will guide you through:
# 1. OAuth2 authentication for chanceroofing@gmail.com
# 2. OAuth2 authentication for mynewemail110411@gmail.com
# 3. Testing access to both accounts
# 4. Generating GitHub Secret format
```

### Step 3: Add Secret to GitHub

```bash
# Option A: Using GitHub CLI
gh secret set RCLONE_CONFIG_DATA < <(cat ~/.config/rclone/rclone.conf | base64 -w 0)

# Option B: Manual
# 1. Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/settings/secrets/actions
# 2. Click "New repository secret"
# 3. Name: RCLONE_CONFIG_DATA
# 4. Value: Run `cat ~/.config/rclone/rclone.conf | base64 -w 0` and paste output
```

### Step 4: Verify Access

```bash
python scripts/verify_gdrive_access.py
```

**Expected Output:**
```
✅ chanceroofing@gmail.com accessible
✅ mynewemail110411@gmail.com accessible
📁 Root items: 123
```

### Step 5: Trigger Extraction

**Via GitHub Actions:**
```bash
gh workflow run gdrive_emergency_extraction.yml --field accounts=all
```

**Via Web:**
1. Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. Select "GDrive Emergency Extraction"
3. Click "Run workflow"
4. Choose accounts: "all"
5. Click "Run workflow"

### Step 6: Monitor Progress

```bash
# Watch latest run
gh run watch

# Or check web dashboard
# https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
```

### Priority Tiers:

**P0 (CRITICAL) - Extracted First:**
- TIA builds
- Citadel code
- AI agent implementations
- Early work documents

**P1 (HIGH) - Extracted Second:**
- All documents (.md, .txt, .json)
- All code files (.py, .js, .gs)
- Scripts and automation

**P2 (MEDIUM) - Extracted Third:**
- Media files (music, art, video)
- Models (.gguf, .pt)
- Datasets

**P3 (LOW) - Extracted Last:**
- Archives (.zip, .rar)
- Duplicates
- Temp files

### Extraction Destinations:

| File Size | Destination | Path |
|-----------|-------------|------|
| < 100MB | GitHub | `data/gdrive_archive/{account}/` |
| 100MB - 1GB | HF Space | Persistent storage |
| > 1GB | HF Datasets | Upload via API |

---

## 💻 PHASE 2: LAPTOP COMPLETE VACUUM

### Run on Your Laptop:

#### Step 1: Clone Repository

```bash
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
cd mapping-and-inventory
```

#### Step 2: System Profile

```bash
python scripts/system_librarian.py
```

This generates:
- Hardware specifications
- Installed programs list
- Disk usage analysis
- Capabilities assessment
- Upgrade recommendations

#### Step 3: Media Harvest

```bash
# Scan all drives for media
python scripts/laptop_media_harvester.py --paths C:/ D:/ F:/
```

This catalogs:
- **Music:** .mp3, .wav, .flac, .m4a
- **Art:** .jpg, .png, .psd, .ai
- **Video:** .mp4, .avi, .mkv, .mov

Output:
- `data/laptop_inventory/media_harvest_catalog.json`
- `data/laptop_inventory/media_harvest_report.md`

#### Step 4: Programs Catalog

```bash
python scripts/laptop_programs_cataloger.py
```

This catalogs:
- Installed programs (from Windows Registry)
- Portable applications
- Program versions and sizes

Output:
- `data/laptop_inventory/programs_catalog.json`
- `data/laptop_inventory/programs_catalog_report.md`

#### Step 5: Smart File Routing

```bash
# Route files by size
python scripts/smart_file_router.py \
  --source C:/Users/YourName \
  --output . \
  --execute \
  --tiers small medium
```

This:
- Scans all files
- Classifies by size tier
- Copies small/medium files to GitHub
- Generates upload plan for large files

#### Step 6: Commit and Push

```bash
git add data/
git commit -m "Laptop vacuum: $(date)"
git push
```

### Automated Weekly Vacuum:

The workflow `.github/workflows/laptop_vacuum_complete.yml` runs weekly.

**Trigger manually:**
```bash
gh workflow run laptop_vacuum_complete.yml --field scan_mode=full
```

---

## 👁️ CRITICAL: Accessing chanceroofing@gmail.com

### The Situation:
- Account locked out (June 2025)
- GDrive still accessible
- Google One still charging monthly
- Early work stored here (VERY IMPORTANT)

### Access Methods:

#### Method 1: Via mynewemail Account (Shared Access)

```bash
# List shared files
rclone lsf gdrive_mynewemail:shared_with_me --max-depth 1

# Copy all shared files
rclone copy gdrive_mynewemail:shared_with_me ./backup/shared -P
```

#### Method 2: Google Takeout (RECOMMENDED)

1. Go to: https://takeout.google.com
2. Try logging in with chanceroofing@gmail.com
3. Select "Google Drive"
4. Choose "All Drive data included"
5. File type: .zip
6. Max size: 50GB per file
7. Delivery: Email to mynewemail110411@gmail.com
8. Wait for download links (can take hours/days)
9. Download and extract all .zip files

**Why Google Takeout:**
- ✅ Gets ALL files (even non-shared)
- ✅ Preserves folder structure
- ✅ Works even if account locked
- ✅ Complete account backup

#### Method 3: Search for Early Work

```bash
# Search for early work patterns
rclone lsf gdrive_mynewemail: --recursive | grep -i "early\|2020\|2021\|2022"
```

---

## 📦 FILE SIZE STRATEGY

### Small Files (<100MB) → GitHub
**Location:** `data/Mapping-and-Inventory-storage/laptop/`

**What:**
- Documents
- Code files
- Small images
- Config files

**How:**
```bash
git add data/Mapping-and-Inventory-storage/
git commit -m "Add small files"
git push
```

### Medium Files (100MB-1GB) → HuggingFace Space
**Location:** HF Space persistent storage

**What:**
- Medium images
- Small models
- Processed datasets

**How:** Workflow handles automatically

### Large Files (>1GB) → HuggingFace Datasets
**Location:** HuggingFace Datasets repository

**What:**
- Music collections
- Art/photo collections
- Video files
- Large models (.gguf >4GB)

**How:**
```bash
python scripts/gdrive_large_file_uploader.py \
  --source ./large_files \
  --repo-name personal-music-archive \
  --min-size 100
```

**Datasets Created:**
- `DJ-Goanna-Coding/personal-music-archive`
- `DJ-Goanna-Coding/personal-art-collection`
- `DJ-Goanna-Coding/personal-video-archive`
- `DJ-Goanna-Coding/gdrive-chanceroofing-backup`
- `DJ-Goanna-Coding/laptop-programs-archive`

---

## 🔍 MONITORING & VERIFICATION

### Check Extraction Status:

```bash
# GDrive manifests
ls -lh data/gdrive_manifests/

# Laptop inventory
ls -lh data/laptop_inventory/

# Archived files
du -sh data/gdrive_archive/*
du -sh data/Mapping-and-Inventory-storage/laptop/
```

### Verify File Integrity:

```bash
# Check hashes in manifest
cat data/gdrive_archive/chanceroofing/copy_manifest.json | jq '.stats'
```

### View Progress Dashboard:

1. Go to: https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
2. Click "Data Migration Dashboard" tab
3. View real-time sync progress

---

## 🆘 TROUBLESHOOTING

### Rclone "Not Accessible" Error:

```bash
# Reconfigure remote
rclone config reconnect gdrive_chanceroofing:
```

### GitHub Push Fails (File Too Large):

```bash
# Remove large file from staging
git reset HEAD path/to/large/file

# Upload to HuggingFace instead
python scripts/gdrive_large_file_uploader.py \
  --source path/to/large/file \
  --repo-name large-files-archive
```

### Workflow Fails:

```bash
# View logs
gh run view --log

# Re-run failed jobs
gh run rerun
```

---

## ✅ SUCCESS CRITERIA

- [ ] Rclone configured for both GDrive accounts
- [ ] chanceroofing@gmail.com fully cataloged
- [ ] mynewemail110411@gmail.com fully cataloged
- [ ] P0/P1 files extracted within 24 hours
- [ ] Laptop system profile generated
- [ ] Laptop media catalog generated
- [ ] Laptop programs catalog generated
- [ ] Small files (<100MB) committed to GitHub
- [ ] Large files cataloged with upload manifests
- [ ] All manifests pushed to repository
- [ ] Integrity verification passing

---

## 📞 NEXT STEPS AFTER EXTRACTION

1. **Verify Critical Files:**
   - Check `data/gdrive_archive/chanceroofing/P0_CRITICAL/`
   - Verify early work is present
   - Test file integrity

2. **Upload Large Files:**
   - Run large file uploader for >1GB files
   - Monitor HuggingFace Datasets uploads
   - Verify upload manifests

3. **Enable Continuous Sync:**
   - Deploy GDrive monitor workers (Phase 3)
   - Setup laptop watch daemon
   - Configure weekly integrity checks

4. **Update Intelligence Map:**
   - Merge manifests into master intelligence map
   - Update TIA-ARCHITECT-CORE RAG
   - Rebuild knowledge graph

---

## 📚 DOCUMENTATION FILES

- `GDRIVE_SHARED_ACCESS_GUIDE.md` - Accessing chanceroofing via mynewemail
- `LAPTOP_COPY_COMPLETE_GUIDE.md` - Laptop vacuum detailed guide
- `PERSONAL_ARCHIVE_OMNIVAC_PROTOCOL.md` - Complete archive protocol
- `QUANTUM_VAULT_OPERATOR_GUIDE.md` - Credential management

---

**🔐 Security:** All credentials stored in Quantum Vault  
**☁️ Authority:** Cloud-First (GitHub → HuggingFace → GDrive)  
**♻️ Compliance:** Section 142, Pull-Over-Push, No Self-Execution

---

**For Support:** Check workflow logs, manifests, and reports in `data/` directory  
**For Updates:** Pull latest from main branch regularly

**Generated:** 2026-04-04  
**Authority:** Citadel Architect v25.0.OMNI+
