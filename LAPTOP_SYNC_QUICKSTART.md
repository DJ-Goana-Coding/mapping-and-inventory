# 💻 LAPTOP SYNC QUICK START

**One command to copy all laptop data to Citadel Mesh**

---

## ⚡ INSTANT START

### Quick Scan (Metadata Only - 2 minutes)
```bash
cd /path/to/mapping-and-inventory
./laptop_sync_orchestrator.sh
```

### Full Harvest (Metadata + Files - 10-15 minutes)
```bash
cd /path/to/mapping-and-inventory
./laptop_sync_orchestrator.sh --full
```

---

## 📋 WHAT IT DOES

### Quick Scan Mode (Default)
1. ✅ Scans your entire filesystem (Documents, Downloads, Desktop, Projects, Code, models)
2. ✅ Searches Desktop for MASTER_MERGE_2.ps1 and MASTER_SYSTEM_MAP_2.csv
3. ✅ Generates JSON manifests with metadata (no file contents)
4. ✅ Commits and pushes to GitHub
5. ✅ Triggers cloud sync workflows

**Output:**
- `data/laptop_inventory/laptop_manifest_latest.json` - Complete file inventory
- `data/laptop_inventory/laptop_desktop_scan_latest.json` - Desktop artifacts
- `data/laptop_inventory/laptop_sync_summary_latest.json` - Sync summary

### Full Harvest Mode (`--full`)
Everything in Quick Scan, PLUS:
1. ✅ Harvests actual file contents (*.py, *.js, *.json, *.md, *.yaml)
2. ✅ Identifies TIA-related files (architect, oracle, surveyor, citadel)
3. ✅ Stores in `data/Mapping-and-Inventory-storage/laptop/`
4. ✅ Creates metadata for each file (hash, size, timestamp)

**Additional Output:**
- `data/Mapping-and-Inventory-storage/laptop/` - All harvested files
- Individual `*.meta.json` files for each harvested file

---

## 🚀 FIRST TIME SETUP

1. **Clone the repository to your laptop:**
   ```bash
   git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
   cd mapping-and-inventory
   ```

2. **Verify scripts exist:**
   ```bash
   ls -la scripts/laptop_filesystem_scanner.py
   ls -la scripts/laptop_desktop_scanner.py
   ls -la vamguard_templates/workers/laptop_harvester.py
   ```

3. **Run the orchestrator:**
   ```bash
   ./laptop_sync_orchestrator.sh
   ```

---

## 📊 WHAT GETS SCANNED

### Directories Scanned
- `~/Documents`
- `~/Downloads`
- `~/Desktop`
- `~/Projects`
- `~/Code`
- `~/models`

### File Categories
- **Models:** `.h5`, `.pkl`, `.pt`, `.pth`, `.safetensors`, `.gguf`, `.bin`, `.model`, `.weights`
- **Libraries:** `.py`, `.js`, `.ts`, `.go`, `.java`, `.cpp`, `.c`, `.rs`
- **Scripts:** `.sh`, `.bash`, `.zsh`, `.ps1`, `.bat`
- **Documents:** `.md`, `.txt`, `.pdf`, `.docx`, `.doc`, `.odt`
- **Datasets:** `.csv`, `.json`, `.jsonl`, `.parquet`, `.arrow`, `.feather`

### Exclusions
- Hidden files/directories (starting with `.`)
- `node_modules`, `__pycache__`, `venv`, `env`
- Files larger than 1GB (scan) or 50MB (harvest)

---

## 🔄 AUTOMATIC SYNC FLOW

After you push, these workflows auto-trigger:

```
Laptop Push
    ↓
GitHub: laptop_sync_processor.yml
    ↓ (generates intelligence report)
    ↓ (triggers multi-repo sync)
    ↓
GitHub: multi_repo_sync.yml
    ↓ (updates master_intelligence_map.txt)
    ↓ (updates master_inventory.json)
    ↓
GitHub: hf_space_sync.yml
    ↓ (pushes to HuggingFace)
    ↓
HuggingFace Space: DJ-Goanna-Coding/Mapping-and-Inventory
    ↓
Oracle: oracle_sync.yml (every 6 hours)
    ↓ (RAG ingestion)
    ↓
TIA-ARCHITECT-CORE RAG Store
```

---

## 🛡️ PRIVACY & SECURITY

### What's Included
✅ File paths and names  
✅ File sizes and timestamps  
✅ File types and categories  
✅ File contents (only in `--full` mode, and only specific file types)

### What's NOT Included
❌ No credentials or secrets  
❌ No `.git` directories  
❌ No `node_modules` or other build artifacts  
❌ No files larger than 1GB (scan) or 50MB (harvest)  
❌ No hidden files or system files

### Sovereign Guardrails
- **Relative Paths Only:** No absolute path exposure
- **Metadata-First:** Scan before harvest
- **Section 142 Compliant:** Partition-aware scanning
- **Cloud-First Authority:** GitHub → HuggingFace → GDrive

---

## 📖 EXAMPLE OUTPUT

### Quick Scan Output
```
╔════════════════════════════════════════════════════════════════╗
║           💻 LAPTOP SYNC ORCHESTRATOR v1.0                    ║
║           Citadel Mesh Data Copy Protocol                     ║
╚════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════╗
║ PHASE 1: Filesystem Scan                                      ║
╚════════════════════════════════════════════════════════════════╝

🔍 Scanning filesystem...
✅ Filesystem scan complete

╔════════════════════════════════════════════════════════════════╗
║ PHASE 2: Desktop Forensic Scan (MASTER_MERGE_2)               ║
╚════════════════════════════════════════════════════════════════╝

🔎 Scanning Desktop for MASTER_MERGE_2 artifacts...
✅ Desktop scan complete

╔════════════════════════════════════════════════════════════════╗
║ PHASE 4: Generate Summary Report                              ║
╚════════════════════════════════════════════════════════════════╝

✅ Summary generated

╔════════════════════════════════════════════════════════════════╗
║ PHASE 5: Commit & Push to GitHub                              ║
╚════════════════════════════════════════════════════════════════╝

📝 Staging files...
💾 Committing: 💻 Laptop Sync: Quick Scan @ 2026-04-04T03:30:00Z
📤 Pushing to GitHub...
✅ Successfully pushed to GitHub

╔════════════════════════════════════════════════════════════════╗
║                    ✅ SYNC COMPLETE                            ║
╚════════════════════════════════════════════════════════════════╝

🎯 Laptop data successfully copied to Citadel Mesh!
```

---

## 🔧 TROUBLESHOOTING

### "laptop_filesystem_scanner.py not found"
**Solution:** Make sure you're in the root of the mapping-and-inventory repository:
```bash
cd /path/to/mapping-and-inventory
pwd  # Should show .../mapping-and-inventory
```

### "Permission denied"
**Solution:** Make script executable:
```bash
chmod +x laptop_sync_orchestrator.sh
```

### "Desktop directory not found"
**Solution:** This is normal if your Desktop is in a different location. The script will skip Desktop scan and continue.

### "Push failed"
**Solution:** Ensure you have push access to the repository:
```bash
git remote -v  # Check remote URL
git config --list | grep user  # Check git user
```

### Python dependencies missing
**Solution:** Install required packages:
```bash
pip install pathlib typing-extensions
```

---

## 📞 MANUAL MODE

If you prefer to run each phase separately:

```bash
# Phase 1: Filesystem Scan
python scripts/laptop_filesystem_scanner.py --full-scan --output laptop_manifest.json

# Phase 2: Desktop Scan
python scripts/laptop_desktop_scanner.py --scan ~/Desktop --ingest-map

# Phase 3: Harvest (optional)
export LAPTOP_SOURCE_PATH="$HOME"
python vamguard_templates/workers/laptop_harvester.py

# Phase 4: Commit & Push
git add data/laptop_inventory/
git commit -m "💻 Laptop data sync"
git push
```

---

## 🎯 NEXT STEPS AFTER PUSH

1. **Monitor GitHub Actions:**
   - Visit: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
   - Watch for `laptop_sync_processor.yml` to complete

2. **Check Intelligence Report:**
   - File: `data/laptop_inventory/laptop_intelligence_report.md`
   - Generated automatically after push

3. **Verify HuggingFace Sync:**
   - Visit: https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
   - Check for updated data

4. **Oracle RAG Ingestion:**
   - Runs automatically within 6 hours
   - Check: `.github/workflows/oracle_sync.yml` status

---

## 📚 RELATED DOCUMENTATION

- `scripts/laptop_filesystem_scanner.py` - Filesystem scanner implementation
- `scripts/laptop_desktop_scanner.py` - Desktop forensic scanner
- `vamguard_templates/workers/laptop_harvester.py` - File harvester
- `.github/workflows/laptop_sync_processor.yml` - GitHub workflow
- `BRIDGE_RAG_ARCHITECTURE.md` - Overall architecture

---

**Status:** ✅ READY TO USE  
**Authority:** Cloud-First (GitHub → HuggingFace → GDrive)  
**Version:** 1.0  
**Last Updated:** 2026-04-04
