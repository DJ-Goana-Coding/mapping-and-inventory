# 🏰 ARK_CORE MANIFESTO - System Documentation

**Version:** 26.57.OMNI  
**Status:** STAINLESS ✅  
**Architect:** DJ Goanna (543 1010 222 777 ❤️‍🔥)

---

## 📡 1. THE SYSTEM TOPOLOGY (THE ROOTS)

The ARK_CORE is a decentralized intelligence hub spanning three primary "Districts":

1. **The Local Node (Oppo/S10)**: Termux environment running Python 3.11+, hosting the Librarian
2. **The Cloud Engine (GitHub Titan)**: GitHub Actions (Ubuntu-Latest) running Node 24 and Rclone
3. **The Cargo Vault (GDrive)**: A 321GB repository of forensic and cultural data

---

## 📂 2. THE DIRECTORY SCAFFOLD (THE TRUNK)

The following structure is maintained strictly to avoid `[Errno 2]` pathing errors:

```
~/ARK_CORE/
├── .github/workflows/         # THE TITAN'S BRAIN
│   └── tia_citadel_deep_scan.yml  # The Heavy-Lift Blueprint
├── Partition_01/              # THE LIBRARIAN'S OFFICE
│   ├── oppo_node.py           # Main Node Script (Frequency 7860)
│   ├── vault.py               # Archive & Ingest Logic
│   └── tracker.db             # SQLite3 Ledger of the 321GB
├── Research/                  # THE CARGO BAYS (Relative Paths)
│   ├── GDrive/                # Root GDrive Sync
│   ├── Oppo/                  # Oppo-specific Cargo
│   ├── S10/                   # S10-specific Cargo
│   └── Laptop/                # Matrix Hub Cargo
├── S10_CITADEL_OMEGA_INTEL/   # THE FORENSIC DISTRICT (High-Level Audit)
├── app.py                     # THE FACEPLATE (Streamlit UI)
├── master_intelligence_map.txt# THE MASTER INDEX (321GB Inventory)
└── citadel_audit.sh           # The Stainless Diagnostic Tool
```

---

## ⚙️ 3. THE LOGIC WELDS (THE BRANCHES)

### A. The Pathing Protocol

**Rule:** NO absolute paths (e.g., `/data/Research`).  
**Fix:** ALWAYS use relative paths (e.g., `./Research/`) to ensure the GitHub Runner and the Oppo Termux environment can both write to the folders without "Permission Denied" errors.

### B. The Sync Frequency

- **Tool:** Rclone
- **Direction:** GDrive → GitHub Titan → master_intelligence_map.txt → Oppo Node
- **Secrets:** `RCLONE_CONFIG_DATA` must be injected as an environment variable, not a hardcoded file

---

## 🛰️ 4. THE HANDSHAKE (THE LEAVES)

When the Architect "jumps on" to view the Faceplate, the following must be true:

1. GitHub Action must have pushed a fresh `master_intelligence_map.txt` to the main branch
2. Oppo Node must run `git pull` to ingest the new map
3. Streamlit (`app.py`) must read the local `Research/` directory and match it against the Map

---

## 🔧 5. KEY COMPONENTS

### Partition_01/vault.py

Archive & Ingest Logic for the 321GB vault.

**Usage:**
```bash
# Initialize and show statistics
python3 Partition_01/vault.py stats

# Ingest a directory
python3 Partition_01/vault.py ingest ./Research/GDrive GDrive

# Archive to JSON
python3 Partition_01/vault.py archive vault_archive.json
```

### Partition_01/oppo_node.py

Main Node Script listening on port 7860 for S10+ handshakes.

**Usage:**
```bash
# Run the Oppo Node (Termux or local)
python3 Partition_01/oppo_node.py
```

### citadel_audit.sh

The Stainless Diagnostic Tool - performs comprehensive health checks.

**Usage:**
```bash
# Run full system audit
./citadel_audit.sh
```

**Checks:**
- ✅ Directory structure
- ✅ Critical files
- ✅ Python environment
- ✅ Git status
- ✅ Port availability (7860)
- ✅ Disk space
- ✅ Vault tracker database
- ✅ Environment variables

---

## 🚀 6. GITHUB ACTIONS WORKFLOW

### TIA_CITADEL_DEEP_SCAN

Located at `.github/workflows/tia_citadel_deep_scan.yml`

**Purpose:** Heavy-lift sync from GDrive to generate master intelligence map

**Manual Trigger:**
```bash
# Using GitHub CLI
gh workflow run tia_citadel_deep_scan.yml

# Or via GitHub UI: Actions → TIA_CITADEL_DEEP_SCAN → Run workflow
```

**What it does:**
1. Installs and configures Rclone with `RCLONE_CONFIG_DATA` secret
2. Tests connection to GDrive
3. Generates `master_intelligence_map.txt` (321GB inventory)
4. Pulls GDrive vault to `./Research/GDrive`
5. Pulls Oppo cargo to `./Research/Oppo`
6. Pulls S10 cargo to `./Research/S10`
7. Pulls S10 CITADEL_OMEGA_INTEL to `./S10_CITADEL_OMEGA_INTEL`
8. Pulls Laptop cargo to `./Research/Laptop`
9. Commits and pushes `master_intelligence_map.txt` back to repository

---

## 🔐 7. REQUIRED SECRETS

Configure these in GitHub repository settings (Settings → Secrets and variables → Actions):

- `RCLONE_CONFIG_DATA`: Rclone configuration for GDrive access
- `HF_TOKEN`: HuggingFace token for Space deployment

---

## 🧪 8. TESTING THE SYSTEM

### Run System Audit
```bash
./citadel_audit.sh
```

Expected output: `✅ SYSTEM STATUS: STAINLESS`

### Initialize Vault Tracker
```bash
python3 Partition_01/vault.py
```

### Test Oppo Node
```bash
# Terminal 1: Start the node
python3 Partition_01/oppo_node.py

# Terminal 2: Test handshake
curl http://localhost:7860
# Expected: {"status": "online", "role": "OPPO Recon", "vote": "HOLDING_FLOOR"}
```

### Run Streamlit Faceplate
```bash
streamlit run app.py --server.port=7860
```

---

## 🦎 9. DJ GOANNA'S WISDOM

> "Architect! Chance, brother! 🫀❤️‍🔥 543 1010 222 777... there it is. The 'Roots-to-Leaves' Manifesto. 🦎 This document is the 'Stainless' code for the Agent. It tells the machine exactly where to put the LEGO blocks so the Librarian doesn't trip in the dark. We've mapped the 321GB, we've indexed the 'Pointy Crown' corruption, and we've built the Faceplate. Now the ARK is Stainless. The 1264+ files are gonna flow like water."

---

## 📝 10. QUICK REFERENCE

| Component | Location | Purpose |
|-----------|----------|---------|
| Vault Logic | `Partition_01/vault.py` | Archive & track 321GB data |
| Oppo Node | `Partition_01/oppo_node.py` | Port 7860 handshake server |
| Diagnostic Tool | `citadel_audit.sh` | System health checks |
| Intelligence Map | `master_intelligence_map.txt` | 321GB GDrive inventory |
| Streamlit UI | `app.py` | Main dashboard/faceplate |
| GitHub Workflow | `.github/workflows/tia_citadel_deep_scan.yml` | Heavy-lift sync |

---

## 🎯 11. MAINTENANCE CHECKLIST

- [ ] Run `./citadel_audit.sh` weekly
- [ ] Trigger `TIA_CITADEL_DEEP_SCAN` workflow monthly
- [ ] Review `master_intelligence_map.txt` for changes
- [ ] Run `git pull` on Oppo Node after workflow completes
- [ ] Check `Partition_01/tracker.db` size and integrity
- [ ] Monitor port 7860 availability

---

**Ready to send the command!** 🚀
