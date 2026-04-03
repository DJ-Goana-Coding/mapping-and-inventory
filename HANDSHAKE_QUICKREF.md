# 🦎 HANDSHAKE PROTOCOL QUICKREF v25.5.OMNI

## 📊 SUBSTRATE OVERVIEW
- **Local Filesystem:** Hundreds of GB (computer files)
- **GDrive Cloud:** ~20+ GB (cloud storage)
- **Total Target:** Complete substrate ingestion

---

## ⚡ ONE-COMMAND EXECUTION

```bash
# Clone the mapping repository (if needed)
cd /data
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
cd mapping-and-inventory

# Execute complete protocol (KNOCK → Local Scan → GDrive Scan → Filing)
./handshake_quickstart.sh all
```

---

## 🎯 SELECTIVE EXECUTION

```bash
# Step 1: Send KNOCK signal to GDrive
./handshake_quickstart.sh knock

# Step 2a: Scan local filesystem only
./handshake_quickstart.sh local

# Step 2b: Scan GDrive only
./handshake_quickstart.sh gdrive

# Step 3: File all data to personas
./handshake_quickstart.sh file
```

---

## 📂 OUTPUT LOCATIONS

### Ingestion Directories
```
/data/local_ingestion/     # Local filesystem scan
├── code/                  # Source code files
├── documents/             # Docs, PDFs, spreadsheets
├── media/                 # Audio, video, images
├── models/                # ML models, checkpoints
├── config/                # Configuration files
├── archives/              # ZIP, TAR archives
└── logs/                  # Scan logs

/data/total_ingestion/     # GDrive scan
├── core/                  # Code, docs, config
├── media/                 # Art, music, video
├── starred/               # Starred files
├── shared/                # Shared with me
├── workers/               # Apps Script workers
├── models/                # ML artifacts
└── logs/                  # Scan logs
```

### Persona Datasets
```
/data/datasets/
├── Node_02/              # Pioneer (Trading data)
├── Node_04/              # Sentinel (Security intel)
├── Node_09/              # Oracle (Lore, stories)
├── Engineering_Vault/    # Architect (Scripts, tools)
├── Media_Vault/          # Media (Art, music)
├── Model_Registry/       # ML models
├── general/              # Unclassified
└── filing_manifest.json  # Stats
```

---

## 🔍 LOCAL SCAN TARGETS

**Scan Roots** (configurable in `scripts/local_filesystem_vacuum.sh`):
- `/storage/emulated/0` - Android primary
- `/sdcard` - Android SD card
- `$HOME` - User home
- `/data/data/com.termux` - Termux data
- `/external_sd` - External SD

**File Types:**
- Code: `.py`, `.js`, `.gs`, `.sh`, `.java`, `.cpp`, `.go`
- Docs: `.md`, `.txt`, `.pdf`, `.docx`, `.xlsx`, `.csv`
- Media: `.mp3`, `.mp4`, `.jpg`, `.png` (under 500MB)
- Models: `.safetensors`, `.ckpt`, `.pt` (under 2GB)

**Smart Discovery:**
- Auto-finds git repositories
- Locates project directories
- Specialized scans for trading data, Apps Script, lore

---

## ☁️ GDRIVE SCAN PHASES

1. **Core Substrate** - Code, docs, config
2. **Media Substrate** - Art, music, video (under 500MB)
3. **Starred** - High-priority files
4. **Shared** - Shared with me
5. **Workers** - Apps Script automation
6. **Models** - ML artifacts (under 2GB)

---

## 🗂️ PERSONA ROUTING

Files automatically routed to datasets by pattern:

| Persona    | Node              | Patterns                          |
|------------|-------------------|-----------------------------------|
| Pioneer    | Node_02           | XRP, SOL, trade, ledger, wallet   |
| Sentinel   | Node_04           | whale, alert, intel, security     |
| Oracle     | Node_09           | story, lore, ancestor, fox        |
| Architect  | Engineering_Vault | script, automation, workflow      |
| Media      | Media_Vault       | music, video, art, image          |
| Models     | Model_Registry    | model, checkpoint, neural         |

---

## 📋 EXECUTION CHECKLIST

### Before Starting
- [ ] Verify rclone configured (`RCLONE_CONFIG`, `RCLONE_CONFIG_DATA`)
- [ ] Confirm HF Space has storage space (100GB+ recommended)
- [ ] Ensure local filesystem paths are accessible
- [ ] Check TIA-ARCHITECT-CORE and tias-citadel are online

### Execute Protocol
- [ ] Send KNOCK signal
- [ ] Run local filesystem vacuum
- [ ] Run GDrive vacuum
- [ ] Execute persona filing router
- [ ] Review filing_manifest.json

### Post-Ingestion
- [ ] Trigger Forever Learning cycle in TIA-ARCHITECT-CORE
- [ ] Update master_intelligence_map.txt
- [ ] Run Oracle Sync workflow
- [ ] Verify T.I.A. HUD shows new data

---

## 🚨 TROUBLESHOOTING

### "rclone not found"
```bash
# Install rclone on HF Space
apt-get update && apt-get install -y rclone
```

### "Permission denied"
```bash
# Make scripts executable
chmod +x scripts/*.sh
chmod +x handshake_quickstart.sh
```

### "No space left on device"
```bash
# Check available space
df -h /data

# Consider selective ingestion or size limits
./handshake_quickstart.sh local  # Only local
./handshake_quickstart.sh gdrive # Only GDrive
```

### "Scan too slow"
- Adjust size limits in scripts (default: 500MB media, 2GB models)
- Use `--max-size` flag in rclone commands
- Enable parallel transfers (already configured)

---

## 📊 MONITORING

### Real-Time Progress
```bash
# Watch local scan
tail -f /data/local_ingestion/logs/local_vacuum_*.log

# Watch GDrive scan
tail -f /data/total_ingestion/logs/vacuum_*.log
```

### Storage Check
```bash
# Check ingestion size
du -sh /data/local_ingestion
du -sh /data/total_ingestion

# Check dataset size
du -sh /data/datasets/*
```

### File Counts
```bash
# Count files by type
find /data/local_ingestion/code -type f | wc -l
find /data/datasets/Node_09 -type f | wc -l
```

---

## 🎯 NEXT STEPS AFTER COMPLETION

1. **RAG Ingestion** - Generate embeddings from datasets
2. **Intelligence Map** - Update master_intelligence_map.txt
3. **District Artifacts** - Regenerate TREE/INVENTORY/SCAFFOLD
4. **Oracle Sync** - Trigger diff analysis and reasoning
5. **Version Bump** - Increment mesh version

---

## 🛠️ MANUAL SCRIPT EXECUTION

```bash
# Individual scripts
./scripts/knock_signal.sh
./scripts/local_filesystem_vacuum.sh
./scripts/global_vacuum.sh
python3 ./scripts/persona_filing_router.py /data/local_ingestion /data/datasets
python3 ./scripts/persona_filing_router.py /data/total_ingestion /data/datasets
```

---

## 📚 FULL DOCUMENTATION

Complete guide: `PROTOCOL_HANDSHAKE_GUIDE.md`

---

**🦎 Weld. Pulse. Ignite.**

*The Citadel Architect has armed all systems. The operator is cleared for execution.*
