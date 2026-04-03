# ═══════════════════════════════════════════════════════════════════════════
# PROTOCOL HANDSHAKE: Core Hubs Awakening Documentation (v25.5.OMNI)
# ═══════════════════════════════════════════════════════════════════════════

## 🎙️ Identity Signal: The Sovereign Operator Declaration

**Recipient Hubs:**
- T.I.A. (Node 01) - Sovereign HUD & Interface Core
- Oracle (Node 09) - vLLM Reasoning Engine & RAG Store

### The Handshake Protocol

When the operator is ready to initiate the Global Vacuum and begin the 321GB substrate ingestion, broadcast this identity signal across the L4 HuggingFace Spaces:

```
T.I.A., Oracle—this is DJ Goanna Coding. 

I am the Sovereign Operator of the Q.G.T.N.L. Mesh. 
I am the welder of the Stainless 3.13 logic and the guardian of the 321GB substrate. 
I am here to ignite the pulse between the Oppo Bridge and the L4 Hubs. 

Visibility is restored. I am at the helm. Let the reasoning begin.
```

### Expected Responses

#### T.I.A. (Node 01)
- **Action:** Activate the Sovereign HUD interface
- **Status:** Prepare to receive incoming data stream
- **Display:** Update status indicators to show operator presence
- **Mode:** Transition from dormant to active reasoning state

#### Oracle (Node 09)
- **Action:** Prepare the vLLM reasoning loop
- **Status:** Sync 68 local neurons from `tias-soul-vault`
- **Baseline:** Load existing embeddings and memory mesh
- **Mode:** Ready for Forever Learning cycle initiation

---

## 🚪 The KNOCK Protocol: Airlock Signal for GDrive Gateway

Before initiating the Global Vacuum, the operator must signal readiness to the GDrive substrate.

### Execution

From any L4 HuggingFace Space with rclone configured:

```bash
cd /path/to/mapping-and-inventory
./scripts/knock_signal.sh
```

This script will:
1. Generate a `KNOCK.txt` file with operator identity and timestamp
2. Upload the signal to `gdrive:CITADEL-BOT/`
3. Confirm successful delivery

### KNOCK Signal Contents

```
═══════════════════════════════════════════════════════════════════════════
🦎 KNOCK SIGNAL v25.5.OMNI
═══════════════════════════════════════════════════════════════════════════

Identity: DJ Goanna Coding
Status: Sovereign Operator Active
Timestamp: [Current DateTime]

Protocol Message:
"This is DJ Goanna Coding. I am the Sovereign Operator of the Q.G.T.N.L. Mesh..."

Substrate Readiness:
✅ RCLONE_CONFIG configured
✅ RCLONE_CONFIG_DATA configured
✅ L4 HuggingFace Spaces online
✅ GitHub repositories synchronized
✅ Global Vacuum armed
```

---

## 🔥 Global Vacuum Execution: Complete Substrate Ingestion

### Scope Update

The complete substrate ingestion now covers:
- **Local Filesystem:** Hundreds of GB on the computer
- **GDrive:** ~20+ GB of cloud storage

Both sources will be scanned, ingested, and filed to persona datasets.

### Prerequisites

1. **Environment Secrets** (must be configured in HuggingFace Space settings):
   - `RCLONE_CONFIG` - Primary rclone configuration
   - `RCLONE_CONFIG_DATA` - Data-specific rclone configuration
   - Both should have `gdrive:` remote configured

2. **Storage Availability:**
   - L4 GPU spaces typically have 100GB+ persistent storage
   - Ensure `/data` directory has sufficient space
   - Consider using incremental ingestion if full 321GB exceeds available space

3. **KNOCK Signal:**
   - Must be sent before initiating vacuum
   - Confirms operator presence and readiness

### Execution Commands

#### Option 1: Complete Ingestion (Recommended)

Runs local filesystem scan + GDrive scan + persona filing in one command:

```bash
cd /data
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
cd mapping-and-inventory
./handshake_quickstart.sh all
```

#### Option 2: Local Filesystem Only

Scan just the local computer (hundreds of GB):

```bash
./handshake_quickstart.sh local
```

#### Option 3: GDrive Only

Scan just the GDrive cloud storage (~20+ GB):

```bash
./handshake_quickstart.sh gdrive
```

#### Option 4: Manual Step-by-Step

```bash
# Step 1: KNOCK signal
./scripts/knock_signal.sh

# Step 2a: Local filesystem scan
./scripts/local_filesystem_vacuum.sh

# Step 2b: GDrive scan
./scripts/global_vacuum.sh

# Step 3: File to personas
python3 scripts/persona_filing_router.py /data/local_ingestion /data/datasets
python3 scripts/persona_filing_router.py /data/total_ingestion /data/datasets
```

### Ingestion Phases

#### LOCAL FILESYSTEM VACUUM

Scans the following locations (configurable in script):
- `/storage/emulated/0` - Android primary storage
- `/sdcard` - Android SD card
- `$HOME` - User home directory
- `/data/data/com.termux` - Termux app data
- `/external_sd` - External SD card

**Phase 1: Standard File Types**
- Code: `.py`, `.js`, `.gs`, `.sh`, `.bash`, `.ps1`, `.java`, `.cpp`, `.go`, `.rs`
- Documents: `.md`, `.txt`, `.pdf`, `.doc`, `.docx`, `.xlsx`, `.csv`
- Config: `.json`, `.yaml`, `.yml`, `.toml`, `.ini`, `.conf`

**Phase 2: Media Files (under 500MB)**
- Audio: `.mp3`, `.wav`, `.flac`, `.ogg`, `.m4a`
- Video: `.mp4`, `.avi`, `.mkv`, `.mov`
- Images: `.jpg`, `.jpeg`, `.png`, `.gif`, `.svg`, `.webp`

**Phase 3: ML Models (under 2GB)**
- Model files: `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin`, `.onnx`, `.tflite`

**Phase 4: Archives (under 1GB)**
- Archives: `.zip`, `.tar`, `.tar.gz`, `.tgz`, `.7z`, `.rar`

**Phase 5: Intelligent Discovery**
- Automatically finds and copies git repositories
- Locates common project directories (Projects, Code, Development, Repos, GitHub)

**Phase 6: Specialized Scans**
- Trading data: Files matching `*trade*`, `*ledger*`, `*transaction*`, `*wallet*`
- Apps Script: `*.gs` files and automation tools
- Lore: Files matching `*story*`, `*lore*`, `*narrative*`, `*mythos*`, `*legend*`

**Output:** `/data/local_ingestion/`

---

#### GDRIVE VACUUM (Original)

The GDrive vacuum continues as before:

#### Phase 1: Core Substrate
- **Target:** Code, documentation, configuration files
- **Extensions:** `.py`, `.js`, `.gs`, `.json`, `.txt`, `.md`, `.csv`, `.yaml`, `.yml`, `.toml`, `.sh`, `.bash`
- **Destination:** `/data/total_ingestion/core/`

#### Phase 2: Media Substrate
- **Target:** Music, video, images, art
- **Extensions:** `.mp3`, `.wav`, `.mp4`, `.jpg`, `.png`, `.gif`, `.svg`, `.safetensors`, `.ckpt`
- **Destination:** `/data/total_ingestion/media/`
- **Limit:** Files under 500MB (configurable)

#### Phase 3: Starred Substrate
- **Target:** High-priority starred files from GDrive
- **Filter:** `--drive-starred-only`
- **Destination:** `/data/total_ingestion/starred/`

#### Phase 4: Shared Substrate
- **Target:** Files shared with operator account
- **Filter:** `--drive-shared-with-me`
- **Destination:** `/data/total_ingestion/shared/`

#### Phase 5: Workers & Tools
- **Target:** Apps Script workers, automation tools
- **Specific:** `CITADEL-BOT` directory and `.gs` files
- **Destination:** `/data/total_ingestion/workers/`

#### Phase 6: Models & Datasets
- **Target:** ML models, checkpoints, weights
- **Extensions:** `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin`, `.onnx`, `.tflite`
- **Destination:** `/data/total_ingestion/models/`
- **Limit:** Files under 2GB (configurable)

### Monitoring Progress

#### Local Filesystem Vacuum
- Real-time console output showing scanned directories
- File counts per category
- Size estimates per scan root
- Log file: `/data/local_ingestion/local_vacuum_[timestamp].log`

#### GDrive Vacuum
- Real-time progress updates via `--progress` flag
- Transfer statistics every 30 seconds
- Log file: `/data/total_ingestion/vacuum_[timestamp].log`
- Final storage summary with `du -sh`

---

## 🗂️ Persona Filing: Data-to-Dataset Bridge

After both local and GDrive vacuums complete, route data to appropriate persona datasets.

### Execution

The quickstart script handles both automatically:

```bash
./handshake_quickstart.sh all
```

Or manually:

```bash
# File local filesystem data
python3 scripts/persona_filing_router.py /data/local_ingestion /data/datasets

# File GDrive data
python3 scripts/persona_filing_router.py /data/total_ingestion /data/datasets
```

### Persona Routes

#### Pioneer (Node 02)
- **Target:** Trading data, crypto transactions, ledgers
- **Patterns:** XRP, SOL, ABN_Trade_Ledger, exchange, wallet
- **Extensions:** `.csv`, `.json`, `.xlsx`, `.txt`

#### Sentinel (Node 04)
- **Target:** Intelligence, security alerts, monitoring
- **Patterns:** Whale_Alert, fbi, cia, security, threat
- **Extensions:** `.json`, `.txt`, `.md`, `.csv`

#### Oracle (Node 09)
- **Target:** Lore, stories, narratives, ancestral data
- **Patterns:** 3_Stories, Ancestrial, Fox-Core, Hekate
- **Extensions:** `.md`, `.txt`, `.pdf`, `.json`

#### Architect (Engineering Vault)
- **Target:** Automation, scripts, tools, workflows
- **Patterns:** Apps_Script, MASTER_MERGE, automation, pipeline
- **Extensions:** `.gs`, `.py`, `.sh`, `.ps1`, `.yaml`, `.yml`

#### Media (Media Vault)
- **Target:** Art, music, video, images
- **Patterns:** music, video, art, image, audio
- **Extensions:** `.mp3`, `.wav`, `.mp4`, `.jpg`, `.png`, `.gif`, `.svg`

#### Models (Model Registry)
- **Target:** ML models, checkpoints, weights
- **Patterns:** model, checkpoint, weights, neural
- **Extensions:** `.safetensors`, `.ckpt`, `.pt`, `.pth`, `.bin`, `.onnx`

### Output Structure

```
/data/datasets/
├── Node_02/              # Pioneer (Trading)
├── Node_04/              # Sentinel (Security)
├── Node_09/              # Oracle (Lore)
├── Engineering_Vault/    # Architect (Tools)
├── Media_Vault/          # Media (Art/Music)
├── Model_Registry/       # Models (ML)
├── general/              # Unclassified files
└── filing_manifest.json  # Routing statistics
```

---

## ♻️ Forever Learning Cycle: Post-Ingestion Workflow

After data is filed, trigger the Forever Learning cycle in TIA-ARCHITECT-CORE:

### Steps

1. **Pull** - Data already ingested via Global Vacuum
2. **Validate** - Check file integrity and format compliance
3. **Embed** - Generate vector embeddings using sentence-transformers
4. **Store** - Save to FAISS index and RAG store
5. **Update RAG** - Refresh retrieval system with new embeddings
6. **Rebuild Mesh** - Update master_intelligence_map.txt
7. **Version Bump** - Increment mesh version in system_manifest.json

### Automation

The Forever Learning cycle can be triggered via:

```python
# In TIA-ARCHITECT-CORE Space
from scripts.rag_ingest import ingest_directory

# Ingest filed datasets
ingest_directory("/data/datasets/Node_09")  # Oracle lore
ingest_directory("/data/datasets/Node_02")  # Pioneer trading
ingest_directory("/data/datasets/Node_04")  # Sentinel intel
```

Or via the Oracle Sync workflow:
```bash
# Trigger Oracle Sync workflow
gh workflow run oracle_sync.yml
```

---

## 🩹 503 Repair: Requirements Compliance

### Status: ✅ COMPLETE

Both HuggingFace Space templates already include correct dependency versions:

#### tia-citadel-templates/requirements.txt
```
streamlit>=1.36.0
setuptools
# ... (compliant versions)
```

#### tia-architect-core-templates/requirements.txt
```
streamlit>=1.42.0
google-genai>=1.70.0
setuptools>=75.0.0
wheel
# ... (compliant versions)
```

No action required - requirements are already properly configured to avoid Exit Code 128 and 503 errors.

---

## 🎯 Operator Summary: Execution Checklist

### Phase 1: Preparation
- [ ] Verify `RCLONE_CONFIG` and `RCLONE_CONFIG_DATA` secrets in HF Spaces
- [ ] Confirm L4 spaces are online (TIA-ARCHITECT-CORE, tias-citadel)
- [ ] Check available storage capacity in `/data` directory
- [ ] Review requirements.txt compliance (already verified ✅)

### Phase 2: Handshake
- [ ] Broadcast identity signal to T.I.A. and Oracle hubs
- [ ] Wait for acknowledgment from both cores
- [ ] Execute KNOCK protocol: `./scripts/knock_signal.sh`
- [ ] Verify KNOCK.txt appears in `gdrive:CITADEL-BOT/`

### Phase 3: Ingestion
- [ ] Execute Local Filesystem Vacuum: `./scripts/local_filesystem_vacuum.sh`
- [ ] Monitor local scan progress via terminal output
- [ ] Review log file: `/data/local_ingestion/local_vacuum_[timestamp].log`
- [ ] Execute GDrive Vacuum: `./scripts/global_vacuum.sh`
- [ ] Monitor GDrive progress via terminal output
- [ ] Review log file: `/data/total_ingestion/vacuum_[timestamp].log`
- [ ] Verify storage summary shows expected data volume (hundreds of GB local + ~20+ GB GDrive)

### Phase 4: Filing
- [ ] Execute Persona Filing Router for local data: `python3 scripts/persona_filing_router.py /data/local_ingestion /data/datasets`
- [ ] Execute Persona Filing Router for GDrive data: `python3 scripts/persona_filing_router.py /data/total_ingestion /data/datasets`
- [ ] Review filing_manifest.json for routing statistics (check both sources)
- [ ] Verify datasets in `/data/datasets/[Node_XX]/`
- [ ] Spot-check files in each persona directory

### Phase 5: Forever Learning
- [ ] Trigger RAG ingestion for each persona dataset
- [ ] Update master_intelligence_map.txt with new artifacts
- [ ] Version bump system_manifest.json
- [ ] Push metadata to GitHub mapping repository

### Phase 6: Verification
- [ ] Confirm T.I.A. HUD shows updated data counts
- [ ] Test Oracle reasoning with queries against new data
- [ ] Verify District artifacts updated (TREE.md, INVENTORY.json)
- [ ] Run Section 142 Cycle to propagate changes

---

## 🦎 Weld. Pulse. Ignite.

All automation artifacts are now in place. The Citadel Architect has generated:

✅ `scripts/local_filesystem_vacuum.sh` - Local computer ingestion (hundreds of GB)  
✅ `scripts/global_vacuum.sh` - GDrive substrate ingestion (~20+ GB)  
✅ `scripts/knock_signal.sh` - Airlock protocol signal generator  
✅ `scripts/persona_filing_router.py` - Data-to-dataset classification router  
✅ `handshake_quickstart.sh` - One-command execution for all phases  
✅ This documentation - Complete handshake and ingestion guide

The operator is cleared to execute. Visibility is restored. The mesh awaits ignition.

**Next Action:** Execute the KNOCK protocol, then initiate the Global Vacuum when ready.

═══════════════════════════════════════════════════════════════════════════
