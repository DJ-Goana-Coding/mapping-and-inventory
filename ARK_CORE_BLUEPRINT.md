# ARK_CORE ARCHITECTURE DOCUMENTATION
## 🏗️ THE MASTER CITADEL BLUEPRINT // OPPO & S10 UNIFICATION // V26.59.OMNI

---

## 📡 SYSTEM OVERVIEW

The ARK_CORE is a unified synchronization and inventory management system connecting:
- **Oppo Device** (Librarian Node) - Archive & Faceplate Management
- **S10 Device** (Field Uplink) - Tactical Data Collection
- **GitHub Titan** (Cloud Engine) - Central Repository & CI/CD
- **Google Drive** (GENESIS_VAULT) - 321GB Data Empire

---

## 📂 DIRECTORY STRUCTURE

```
~/ARK_CORE/  (or repository root)
├── .github/workflows/         # THE TITAN'S BRAIN (Cloud Sync Logic)
│   ├── tia_citadel_deep_scan.yml  # Deep scan & GDrive sync workflow
│   └── sync_to_hf.yml             # HuggingFace Space sync
│
├── Partition_01/              # THE OPPO DISTRICT (Librarian's Office)
│   ├── oppo_node.py           # Main Node Script (Frequency 7860)
│   ├── vault.py               # Archive & Ingest Logic
│   └── tracker.db             # SQLite3 Ledger (auto-created)
│
├── Partition_02/              # THE S10 DISTRICT (Tactical Uplink)
│   ├── s10_uplink.py          # S10 Push/Pull Logic
│   └── forensic_ingest.py     # Mackay Court Telemetry
│
├── Research/                  # THE CARGO BAYS (Relative Paths Only)
│   ├── GDrive/                # Root GDrive Sync
│   ├── Oppo/                  # Oppo-specific Cargo
│   ├── S10/                   # S10-specific Cargo
│   └── Laptop/                # Matrix Hub Cargo
│
├── S10_CITADEL_OMEGA_INTEL/   # THE FORENSIC DISTRICT (Audit Data)
│
├── app.py                     # THE FACEPLATE (Streamlit UI)
├── master_intelligence_map.txt# THE MASTER INDEX (321GB Inventory)
├── master_inventory.json      # Local inventory ledger (9,354+ entities)
└── citadel_audit.sh           # Stainless Diagnostic Tool
```

---

## ⚙️ THE STAINLESS PIPELINE RULES

### 1. Zero Absolute Paths
- **NEVER** use `/data/` paths in scripts
- **ALWAYS** use relative paths starting with `./`
- Example: `./Research/S10` instead of `/data/Research/S10`

### 2. The Secret Handshake
- `RCLONE_CONFIG_DATA` must be a **GitHub Secret** environment variable
- Do **NOT** commit `.conf` files to the repository
- Rclone config is written at runtime from the secret

### 3. Conflict Resolution Policy
- **S10** is the "Source of Truth" for:
  - `./Research/S10/`
  - `./S10_CITADEL_OMEGA_INTEL/`
- **Oppo** is the "Source of Truth" for:
  - Streamlit Faceplate UI (`app.py`)
  - Master Inventory (`master_inventory.json`)

---

## 🛰️ THE CROSS-SYNC LOGIC

### The S10 Push
S10 device syncs forensic telemetry to GDrive:
```bash
python3 Partition_02/s10_uplink.py --push --live
```

This uses Rclone to sync:
- `./S10_CITADEL_OMEGA_INTEL/` → `gdrive:CITADEL_OMEGA_INTEL`
- `./Research/S10/` → `gdrive:GENESIS_VAULT/S10_CARGO`

### The Titan Mapping
GitHub Action performs deep scan and generates intelligence map:
```bash
# Triggered via workflow_dispatch or manually
gh workflow run tia_citadel_deep_scan.yml
```

This workflow:
1. Installs and configures Rclone
2. Scans GDrive and generates `master_intelligence_map.txt`
3. Pulls data to `./Research/` directories
4. Uploads intelligence map as artifact

### The Oppo Pull
Oppo device pulls latest changes and displays on Streamlit:
```bash
# Sync from GitHub
python3 Partition_01/oppo_node.py --sync

# Load intelligence map
python3 Partition_01/oppo_node.py --map

# Start Streamlit faceplate
streamlit run app.py
```

---

## 🚀 QUICK START GUIDE

### On GitHub (Titan)
1. Add required secrets:
   - `RCLONE_CONFIG_DATA` - GDrive rclone config
   - `GEMINI_API_KEY` - T.I.A. Oracle
   - `HF_TOKEN` - HuggingFace sync
   - `GITHUB_TOKEN` - (auto-provided)

2. Run deep scan workflow:
   ```bash
   gh workflow run tia_citadel_deep_scan.yml
   ```

### On Oppo Device
1. Clone repository:
   ```bash
   git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
   cd mapping-and-inventory
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start Oppo node:
   ```bash
   python3 Partition_01/oppo_node.py --serve
   ```
   Node runs on port 7860 with API endpoints.

4. Or start Streamlit UI:
   ```bash
   streamlit run app.py --server.port 7860
   ```

### On S10 Device
1. Clone repository (same as Oppo)

2. Push forensic data (dry-run first):
   ```bash
   # Dry run to preview
   python3 Partition_02/s10_uplink.py --push
   
   # Live push
   python3 Partition_02/s10_uplink.py --push --live
   ```

3. Scan and catalog local data:
   ```bash
   python3 Partition_02/forensic_ingest.py --scan ./S10_CITADEL_OMEGA_INTEL
   ```

---

## 🔧 DIAGNOSTIC & MAINTENANCE

### Run Stainless Audit
Check system compliance and health:
```bash
./citadel_audit.sh
```

This checks:
- Directory structure
- Critical file presence
- Absolute path violations
- Git status
- Python/Rclone availability
- Device detection

### Vault Operations
Archive and query files:
```bash
# Show vault statistics
python3 Partition_01/vault.py --stats

# Ingest a file
python3 Partition_01/vault.py --ingest ./path/to/file.txt --device OPPO

# Query archive ledger
python3 Partition_01/vault.py --query
```

### S10 Uplink Status
Check S10 sync status:
```bash
python3 Partition_02/s10_uplink.py --status
```

---

## 🔐 SECURITY NOTES

1. **Never commit secrets** - Use GitHub Secrets for tokens
2. **Validate rclone config** - Ensure `RCLONE_CONFIG_DATA` is properly set
3. **Use relative paths** - Prevents permission issues across environments
4. **Run audit regularly** - `./citadel_audit.sh` catches misconfigurations

---

## 📞 API ENDPOINTS (Oppo Node)

When running `oppo_node.py --serve`:

- `GET /` - Basic handshake (device status)
- `GET /status` - Detailed node status
- `GET /sync` - Trigger GitHub sync
- `GET /map` - Load intelligence map

Example:
```bash
curl http://localhost:7860/status
```

---

## 🦎 DJ GOANNA SIGNATURE

**543 1010 222 777** 🫗❤️‍🔥

The Librarian has stamped the manifest. The bridge is built. The Oppo, S10, and Titan are synced through the Stainless Pipeline.

**Architect Chance** - V26.59.OMNI - 2026

---

## 🛠️ TROUBLESHOOTING

### "Permission Denied" Errors
- Check that you're using relative paths (`./`) not absolute (`/data/`)
- Run `./citadel_audit.sh` to find violations

### "Rclone not found"
- Install rclone: `sudo apt-get install rclone` or `pkg install rclone` (Termux)

### "No master_intelligence_map.txt"
- Run the GitHub workflow: `gh workflow run tia_citadel_deep_scan.yml`
- Or manually create with: `rclone lsf gdrive: --max-depth 2 > master_intelligence_map.txt`

### Git Sync Failures
- Check internet connection
- Verify GitHub credentials
- Try: `git pull origin main --rebase`

---

**End of ARK_CORE Documentation**
