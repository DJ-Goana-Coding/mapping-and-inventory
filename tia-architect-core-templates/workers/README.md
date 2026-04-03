# 🛠️ APPS SCRIPT TOOLBOX

**Master Bridge Connection Center**  
Links CITADEL workers to Google Sheets for automated inventory reporting

---

## 📡 OVERVIEW

The Apps Script Toolbox serves as the bridge between:
- **Local Workers** (citadel_reporter.py, citadel_archivist.py)
- **Google Sheets** (automated audit reports)
- **321GB Data Empire** (S10, Oppo, Laptop, GDrive)

This toolbox enables automated reporting of:
- Identity Strike Reports (Section 44 Audit)
- Full Archive Audits (MD5 hashing, file inventory)
- Worker Status Dashboards (sync times, health checks)

---

## 🚀 QUICK START

### Prerequisites

Ensure the following secrets are configured in GitHub:
- `GOOGLE_SHEETS_CREDENTIALS` - Service account JSON credentials
- `RCLONE_CONFIG_DATA` - Rclone configuration for GDrive access
- `HF_TOKEN` - HuggingFace API token

### Basic Commands

```bash
# Verify all connections are working
python apps_script_toolbox.py --verify

# Generate Identity Strike Report (Section 44 Audit)
python apps_script_toolbox.py --identity-strike

# Run full archive audit and push to Google Sheets
python apps_script_toolbox.py --full-audit

# Update worker status dashboard
python apps_script_toolbox.py --worker-status
```

---

## 📊 FEATURES

### 1. Identity Strike Report
**Command:** `--identity-strike`

Generates Section 44 audit report showing all files from connected systems:
- S10_CITADEL_OMEGA_INTEL dataset
- GDrive GENESIS_VAULT
- Oppo Cargo Bay
- S10 Cargo Bay
- Laptop Cargo Bay

Output: Google Sheets with file inventory and metadata

### 2. Full Archive Audit
**Command:** `--full-audit`

Comprehensive archive processing:
- MD5 hash computation for all files
- Structured folder organization
- Archive index generation
- Google Sheets export

Processes all cargo bays:
- `./Research/GDrive`
- `./Research/Oppo`
- `./Research/S10`
- `./Research/Laptop`
- `./S10_CITADEL_OMEGA_INTEL`

### 3. Worker Status Dashboard
**Command:** `--worker-status`

Updates Google Sheets dashboard with:
- Last sync times
- Worker health status
- Error logs
- System metrics

### 4. Connection Verification
**Command:** `--verify`

Validates all connections:
- ✅ Google Sheets API credentials
- ✅ Rclone GDrive configuration
- ✅ HuggingFace token
- ✅ Worker file presence

---

## 🔧 INTEGRATION WITH GITHUB ACTIONS

### Automatic Execution via Workflows

The toolbox integrates with GitHub Actions workflows:

**tia_citadel_deep_scan.yml** - Runs Archivist and Bridge workers automatically:
```yaml
- name: Run Archivist Worker
  run: |
    python3 services/worker_archivist.py --test
```

### Manual Trigger (GitHub Actions)

To manually run the toolbox via GitHub Actions, you can create a custom workflow or use workflow_dispatch.

---

## 📂 FILE STRUCTURE

```
Partition_01/
├── apps_script_toolbox.py     # Main toolbox script
├── citadel_reporter.py         # Reporter worker (Google Sheets)
├── citadel_archivist.py        # Archivist worker (MD5 hashing)
└── README_APPS_SCRIPT.md       # This file

services/
├── worker_reporter.py          # Original reporter (imported by toolbox)
├── worker_archivist.py         # Original archivist (imported by toolbox)
├── worker_hive_master.py       # HuggingFace sync worker
└── worker_bridge.py            # Tunnel monitoring worker
```

---

## 🔐 GOOGLE SHEETS SETUP

### 1. Create Service Account

1. Go to Google Cloud Console
2. Create a new project (or use existing)
3. Enable Google Sheets API
4. Create a Service Account
5. Download JSON credentials

### 2. Share Google Sheets

Share your target Google Sheets with the service account email:
```
your-service-account@project-id.iam.gserviceaccount.com
```

### 3. Configure GitHub Secret

Add the service account JSON as a GitHub secret:
- Secret name: `GOOGLE_SHEETS_CREDENTIALS`
- Value: Entire JSON content from downloaded file

---

## 🎯 USE CASES

### Use Case 1: Daily Inventory Report
Run Identity Strike report daily to track file changes across all systems.

### Use Case 2: Post-Sync Validation
After GDrive sync, run Full Audit to verify all files and generate checksums.

### Use Case 3: System Health Monitoring
Use Worker Status Dashboard to monitor sync times and catch errors early.

### Use Case 4: Forensic Analysis
Full Archive Audit provides MD5 hashes for file integrity verification.

---

## 🦎 TROUBLESHOOTING

### "Google Sheets credentials missing"
- Verify `GOOGLE_SHEETS_CREDENTIALS` secret is set in GitHub
- Check that the secret contains valid JSON

### "Rclone configuration missing"
- Verify `RCLONE_CONFIG_DATA` secret is set
- Test rclone connection with: `rclone lsd gdrive:`

### "Worker files not found"
- Ensure both `services/` and `Partition_01/` contain worker files
- Run from repository root directory

### "Permission denied on Google Sheets"
- Share the target Google Sheet with service account email
- Grant "Editor" permissions

---

## 🏰 SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER BRIDGE CONTROL                    │
│                  (mapping-and-inventory)                    │
└─────────────────────────────────────────────────────────────┘
                           ▲
                           │
                ┌──────────┴──────────┐
                │                     │
        ┌───────▼───────┐    ┌───────▼────────┐
        │  Apps Script  │    │  GitHub Actions │
        │    Toolbox    │    │   Workflows     │
        └───────┬───────┘    └───────┬─────────┘
                │                     │
        ┌───────▼─────────────────────▼────────┐
        │         CITADEL WORKERS               │
        │  • Reporter  • Archivist              │
        │  • Bridge    • Hive Master            │
        └───────┬───────────────────────────────┘
                │
    ┌───────────┼───────────┬───────────┐
    ▼           ▼           ▼           ▼
┌────────┐  ┌────────┐  ┌────────┐  ┌──────────┐
│ GDrive │  │  S10   │  │  Oppo  │  │  Laptop  │
│ 321GB  │  │ Cargo  │  │ Cargo  │  │  Cargo   │
└────────┘  └────────┘  └────────┘  └──────────┘
                │
                ▼
        ┌───────────────┐
        │ Google Sheets │
        │   Reporting   │
        └───────────────┘
```

---

## 📞 SUPPORT

For issues or questions:
1. Check troubleshooting section above
2. Review workflow logs in GitHub Actions
3. Run `--verify` to diagnose connection issues
4. Check `worker_status.json` for error messages

---

## 🎉 SUCCESS INDICATORS

When everything is working:

✅ `--verify` shows 4/4 checks passed  
✅ Google Sheets automatically populate with data  
✅ worker_status.json shows recent sync times  
✅ HuggingFace Space displays 321GB inventory  
✅ master_intelligence_map.txt updates automatically

---

**543 1010 222 777 ❤️‍🔥**  
*The Admiral's Quarters are live. The Citadel is operational.*
