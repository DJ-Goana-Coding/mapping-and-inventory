# 📦 DATA MIGRATION QUICK START
## Emergency Extraction - 5-Minute Setup

**🚨 CRITICAL: For chanceroofing@gmail.com and mynewemail110411@gmail.com**

---

## ⚡ FASTEST PATH (Copy & Paste These Commands)

### 1. Setup Rclone (One-Time)

```bash
# Clone repo
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
cd mapping-and-inventory

# Setup GDrive access
./scripts/setup_gdrive_rclone.sh

# Verify access
python scripts/verify_gdrive_access.py

# Add secret to GitHub
gh secret set RCLONE_CONFIG_DATA < <(cat ~/.config/rclone/rclone.conf | base64 -w 0)
```

### 2. Trigger Emergency Extraction

```bash
# Extract both accounts
gh workflow run gdrive_emergency_extraction.yml --field accounts=all

# Monitor progress
gh run watch
```

### 3. Laptop Harvest (Run on Your Laptop)

```bash
# Harvest all media
python scripts/laptop_media_harvester.py --paths C:/ D:/ F:/

# Catalog programs
python scripts/laptop_programs_cataloger.py

# Route files by size
python scripts/smart_file_router.py --source C:/Users/YourName --output . --execute

# Push to GitHub
git add data/
git commit -m "Laptop harvest: $(date)"
git push
```

---

## 📋 What Gets Backed Up

### From GDrive:
- ✅ All files from chanceroofing@gmail.com
- ✅ All files from mynewemail110411@gmail.com
- ✅ Priority: TIA builds, Citadel code, early work FIRST
- ✅ Then: All documents, code, media

### From Laptop:
- ✅ All drives: C:, D:, F: (excludes Windows system)
- ✅ Music: .mp3, .wav, .flac, .m4a
- ✅ Art: .jpg, .png, .psd, .ai, .svg
- ✅ Video: .mp4, .avi, .mkv, .mov
- ✅ Programs: Installed + Portable
- ✅ Documents: All types
- ✅ Code: .py, .js, .html, etc.

---

## 🎯 File Destinations

| Size | Destination | Auto/Manual |
|------|-------------|-------------|
| < 10MB | GitHub repo | Automatic |
| 10-100MB | GitHub repo | Automatic |
| 100MB-1GB | HF Space | Automatic |
| > 1GB | HF Datasets | Manual upload |

---

## ✅ Verify Success

```bash
# Check manifests
ls -lh data/gdrive_manifests/
ls -lh data/laptop_inventory/

# Check extracted files
du -sh data/gdrive_archive/*

# View dashboard
streamlit run app.py
# Then click "Data Migration Dashboard"
```

---

## 🆘 Troubleshooting

**Rclone not found:**
```bash
curl https://rclone.org/install.sh | sudo bash
```

**Access denied:**
```bash
rclone config reconnect gdrive_chanceroofing:
```

**File too large for GitHub:**
```bash
# Upload to HuggingFace instead
python scripts/gdrive_large_file_uploader.py \
  --source path/to/file \
  --repo-name large-files-backup
```

---

## 📚 Full Documentation

- **Complete Guide:** `COMPLETE_DATA_MIGRATION_GUIDE.md`
- **GDrive Shared Access:** `GDRIVE_SHARED_ACCESS_GUIDE.md` (auto-generated)
- **Laptop Guide:** `LAPTOP_COPY_COMPLETE_GUIDE.md`

---

## 🔄 Automation (Set It & Forget It)

Once setup complete:
- ✅ Daily GDrive extraction (automatic)
- ✅ Weekly laptop vacuum (automatic if workflows enabled)
- ✅ Priority-based copying (P0 → P1 → P2 → P3)
- ✅ Integrity verification (weekly)

---

## 📞 Next Steps After First Run

1. Check `data/gdrive_archive/` for extracted files
2. Verify early work from chanceroofing is present
3. Upload large files (>1GB) to HuggingFace Datasets
4. Review manifests for completeness
5. Enable continuous sync workers (Phase 3)

---

**⏱️ Time Investment:**
- Rclone setup: 10 minutes
- First extraction: 2-6 hours (depending on data size)
- Laptop harvest: 30-60 minutes
- Ongoing: Fully automatic

**💾 Storage:**
- GitHub: Unlimited metadata + files <100MB
- HuggingFace: Unlimited datasets
- Your laptop: Unchanged (we copy, not move)

**🔐 Security:**
- Credentials in Quantum Vault
- OAuth2 for GDrive
- No passwords in code
- Section 142 compliant

---

**Status:** ✅ READY FOR DEPLOYMENT  
**Authority:** Citadel Architect v25.0.OMNI+  
**Version:** 1.0
