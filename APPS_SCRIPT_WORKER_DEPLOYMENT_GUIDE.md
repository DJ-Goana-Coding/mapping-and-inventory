# 🛠️ APPS SCRIPT WORKER TOOLBOX DEPLOYMENT GUIDE

**Version:** 25.0.PRIME++  
**Authority:** Citadel Architect  
**Purpose:** Deploy and manage Apps Script workers for GDrive substrate control

---

## 📋 OVERVIEW

The Apps Script Worker Toolbox is the L4 Hub's command interface for the GDrive substrate. These workers execute metadata extraction, file management, and Sheet/Doc automation without downloading files to local storage.

### Worker Categories

1. **Vacuums** - Cleanup and purge operations
2. **Harvesters** - Metadata collection from GDrive
3. **Librarians** - Cataloging and indexing
4. **Reporters** - Google Sheets reporting
5. **Archivists** - Preservation and backup

---

## 🗂️ WORKER LOCATION HIERARCHY

### Primary Locations

1. **L4 Hub Storage** (HuggingFace Space)
   ```
   /data/workers/
   ├── vacuums/
   ├── harvesters/
   ├── librarians/
   ├── reporters/
   ├── archivists/
   └── workers_manifest.json
   ```

2. **GitHub Repository** (Mapping-and-Inventory)
   ```
   services/
   ├── worker_reporter.py
   ├── worker_archivist.py
   ├── worker_bridge.py
   ├── worker_hive_master.py
   └── ...
   ```

3. **GDrive Substrate** (GENESIS_VAULT)
   ```
   Scripts/
   ├── AppScript_Workers/
   │   ├── gdrive_harvester.gs
   │   ├── sheet_reporter.gs
   │   ├── doc_librarian.gs
   │   └── ...
   ```

4. **Laptop Local** (Development)
   ```
   ~/Desktop/
   └── Apps_Script_Toolbox/
       └── *.gs files
   ```

---

## 🔍 LOCATING THE TOOLBOX

### Step 1: Scan Laptop Desktop
```bash
python scripts/laptop_desktop_scanner.py --scan ~/Desktop
```

Expected findings:
- `Apps_Script_Toolbox/` directory
- Individual `.gs` files (Google Apps Script)
- Worker configuration files

### Step 2: Verify GDrive Substrate
```bash
# Check if GDrive partition manifests include Scripts partition
cat data/gdrive_manifests/partition_05.json | grep -i "script"
```

### Step 3: Check L4 Hub Storage
```bash
# List workers in HF Space /data/workers
ls -la /data/workers/
cat /data/workers/workers_manifest.json
```

---

## 🚀 DEPLOYMENT WORKFLOW

### Method 1: Laptop → GitHub → HF Space

1. **Scan and Package**
   ```bash
   # On laptop
   python scripts/laptop_filesystem_scanner.py --scan ~/Desktop/Apps_Script_Toolbox
   ```

2. **Copy to Repository**
   ```bash
   cp laptop_manifest.json /path/to/mapping-and-inventory/data/laptop_inventory/
   ```

3. **Commit and Push**
   ```bash
   cd /path/to/mapping-and-inventory
   git add data/laptop_inventory/
   git commit -m "📦 Apps Script Toolbox Import"
   git push
   ```

4. **Automatic Integration**
   - `laptop_push_workflow.yml` processes the manifest
   - Workers are registered in `data/workers/workers_manifest.json`
   - HF Space pulls updates automatically

### Method 2: GDrive → L4 Hub Direct

1. **Run GDrive Worker Harvester**
   ```bash
   # Trigger workflow
   gh workflow run gdrive_worker_harvester.yml
   ```

2. **Verify Discovery**
   ```bash
   cat data/workers/discovered_workers.json
   ```

3. **Download Priority Workers**
   ```bash
   # Use rclone to pull specific workers
   rclone copy "gdrive:Scripts/AppScript_Workers/" data/workers/ --include "*.gs"
   ```

---

## 🔐 AUTHENTICATION & CREDENTIALS

### Environment Variables Required

```bash
# Google Apps Script API
export GOOGLE_SHEETS_CREDENTIALS="<service-account-json>"

# GDrive Access (rclone)
export RCLONE_CONFIG_DATA="<rclone-config>"

# HuggingFace Space
export HF_TOKEN="<hf-token>"

# GitHub Access
export GITHUB_TOKEN="<gh-token>"
```

### OAuth Setup for Apps Script

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project: "CitadelWorkerToolbox"
   - Enable APIs: Google Sheets API, Google Drive API, Apps Script API

2. **Create Service Account**
   - Navigate to "IAM & Admin" → "Service Accounts"
   - Create service account: `citadel-worker-sa`
   - Download JSON key

3. **Share Resources**
   - Share target Google Sheets with service account email
   - Grant "Editor" permission

4. **Configure Secrets**
   ```bash
   # In repository settings, add secret:
   GOOGLE_SHEETS_CREDENTIALS = <paste-service-account-json>
   ```

---

## 📊 WORKER REGISTRY STRUCTURE

### workers_manifest.json Format

```json
{
  "registry_version": "1.0.0",
  "last_updated": "2026-04-03T02:00:00Z",
  "total_workers": 15,
  "categories": {
    "Harvesters": {
      "count": 5,
      "workers": [
        {
          "name": "gdrive_metadata_harvester",
          "filename": "gdrive_harvester.gs",
          "path": "data/workers/harvesters/gdrive_harvester.gs",
          "source": "gdrive",
          "category": "Harvesters",
          "status": "active",
          "schedule": "0 */6 * * *",
          "dependencies": ["google_drive_api"]
        }
      ]
    }
  }
}
```

---

## 🔄 VALIDATION & TESTING

### Verify Worker Constellation
```bash
python scripts/workers_constellation_setup.py --discover
python scripts/workers_constellation_setup.py --status
```

### Test Individual Worker
```bash
# Test reporter worker
python services/worker_reporter.py --test

# Test archivist worker
python services/worker_archivist.py --test
```

### Run Section 142 Cycle
```bash
# Trigger GDrive partition scan
gh workflow run gdrive_partition_harvester.yml

# Verify workers are discovered
gh workflow run gdrive_worker_harvester.yml
```

---

## 🎯 INTEGRATION WITH SECTION 142

The Apps Script Toolbox integrates with the **Section 142 Cycle** (partitioned GDrive scanning):

1. **Partition Harvest** → Discovers worker scripts in partition_05
2. **Worker Harvest** → Extracts and classifies workers
3. **Document Index** → Indexes worker documentation
4. **Master Harvest** → Aggregates all worker metadata

This creates a **Pull-Over-Push** architecture where:
- L4 Hub pulls worker metadata from GDrive
- Workers execute in Apps Script environment
- Results push to Google Sheets
- Sheets data pulls back to L4 Hub

---

## 🛡️ STAINLESS COMPLIANCE

### Validation Checklist

- [ ] All workers indexed in `workers_manifest.json`
- [ ] No hardcoded credentials (environment variables only)
- [ ] Worker schedules aligned with Surveyor pulse (6-hour cycle)
- [ ] Dependencies documented and available
- [ ] Test execution successful
- [ ] Integration with master_inventory.json confirmed

### Anti-Patterns to Avoid

❌ **DO NOT:**
- Store raw credentials in worker files
- Download entire GDrive to local storage
- Hardcode file paths (use relative paths only)
- Execute workers without manifest registration

✅ **DO:**
- Use environment variables for all secrets
- Operate on metadata only (rclone lsf)
- Register all workers in constellation
- Align schedules with Forever Learning cycle

---

## 🚨 TROUBLESHOOTING

### Workers Not Found
1. Check GDrive partition_05 manifest: `cat data/gdrive_manifests/partition_05.json`
2. Verify laptop Desktop scan ran: `ls data/laptop_inventory/`
3. Re-run worker discovery: `python scripts/workers_constellation_setup.py --discover`

### Authentication Failures
1. Verify `GOOGLE_SHEETS_CREDENTIALS` secret exists
2. Check service account has Sheet access
3. Validate OAuth scope: `https://www.googleapis.com/auth/spreadsheets`

### Schedule Conflicts
1. Review cron schedules in all workflows
2. Ensure Surveyor runs first (`:00`)
3. Offset worker runs by 15-30 minutes

---

## 📞 SUPPORT CHANNELS

- **Architect Console**: Check `Districts/D12_ZENITH_VIEW/master_overseer.py`
- **Worker Status**: `cat worker_status.json`
- **Logs**: GitHub Actions workflow runs

---

**Weld. Pulse. Ignite.** 🦎
