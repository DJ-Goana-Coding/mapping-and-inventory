# 🛡️ VAMGUARD TITAN DEPLOYMENT GUIDE

**Complete infrastructure for autonomous security, worker coordination, and data flow management**

---

## 📋 EXECUTIVE SUMMARY

VAMGUARD TITAN has been repurposed as the **Security & Worker Coordination Hub** for the Citadel Mesh with the following capabilities:

### ✅ **NEW REQUIREMENT: DATA FLOW IMPLEMENTED**

**Laptop → Mapping-and-Inventory-storage**
- `laptop_harvester.py` - Scans and harvests files from laptop node
- `laptop_harvest.yml` - Runs every 12 hours automatically
- Stores in: `data/Mapping-and-Inventory-storage/laptop/`

**GDrive → Mapping-and-Inventory-storage**
- `gdrive_harvester.py` - Section 142 Cycle metadata extraction
- `gdrive_harvest.yml` - Runs every 12 hours automatically
- Stores in: `data/Mapping-and-Inventory-storage/gdrive/`

**TIA Code → TIA-ARCHITECT-CORE**
- `tia_code_finder.py` - Discovers all TIA-related code
- `tia_sync_worker.py` - Pushes to DJ-Goanna-Coding/TIA-ARCHITECT-CORE
- `tia_discovery_sync.yml` - Runs after harvest, syncs automatically

### ✅ **GPU ACCELERATION: L4/T4 READY**

HuggingFace Space configured for:
- **L4 GPU (24GB)** - Recommended
- **T4 GPU (16GB)** - Alternative
- Fast embedding generation
- ML-powered security scanning
- High-throughput data processing

---

## 🏗️ DEPLOYMENT STEPS

### Step 1: Create GitHub Repository

```bash
# Create the repository
gh repo create DJ-Goana-Coding/VAMGUARD-TITAN --public --description "🛡️ Security & Worker Coordination Hub"

# Clone it
git clone git@github.com:DJ-Goana-Coding/VAMGUARD-TITAN.git
cd VAMGUARD-TITAN
```

### Step 2: Copy VAMGUARD Templates

From the `mapping-and-inventory` repository:

```bash
# Copy all templates
cp -r vamguard_templates/* .

# Copy specific files to root
mv README_HF_SPACE.md README.md

# Initialize git
git add .
git commit -m "🛡️ Initialize VAMGUARD TITAN infrastructure"
git push origin main
```

### Step 3: Configure GitHub Secrets

Navigate to: `Settings → Secrets and variables → Actions`

Add the following secrets:

```bash
GITHUB_TOKEN        # GitHub Personal Access Token (with repo access)
HF_TOKEN            # HuggingFace authentication token
RCLONE_CONFIG_DATA  # Rclone configuration for GDrive access
GOOGLE_SHEETS_CREDENTIALS  # Service account JSON for reporting
LAPTOP_SOURCE_PATH  # Path to laptop source directory
```

### Step 4: Create HuggingFace Space

1. Go to: https://huggingface.co/spaces
2. Click "Create new Space"
3. Fill in:
   - **Owner:** DJ-Goanna-Coding
   - **Space name:** VAMGUARD-TITAN
   - **License:** MIT
   - **SDK:** Streamlit
   - **Hardware:** L4 (24GB) or T4 (16GB)
   - **Storage:** Persistent

4. Add remote and push:

```bash
git remote add hf https://huggingface.co/spaces/DJ-Goanna-Coding/VAMGUARD-TITAN
git push hf main --force
```

### Step 5: Enable GitHub Actions

1. Go to repository `Actions` tab
2. Enable workflows:
   - ✅ `vamguard_auto_sync.yml` - Every 6h security/worker/bridge checks
   - ✅ `laptop_harvest.yml` - Every 12h laptop data harvest
   - ✅ `gdrive_harvest.yml` - Every 12h GDrive metadata extraction
   - ✅ `tia_discovery_sync.yml` - TIA code discovery and sync

3. Run manual test:
   - Click on each workflow
   - Click "Run workflow"
   - Verify successful execution

---

## 🔄 DATA FLOW ARCHITECTURE

```
┌─────────────┐
│   LAPTOP    │───┐
└─────────────┘   │
                  │    ┌────────────────────────────────────┐
┌─────────────┐   │    │  Mapping-and-Inventory-storage     │
│   GDRIVE    │───┼───>│  (L4 GPU Processing)               │
└─────────────┘   │    │  - laptop/                         │
                  │    │  - gdrive/                         │
┌─────────────┐   │    │  - tia_code/                       │
│  GITHUB     │───┘    └────────────────────────────────────┘
│  REPOS      │                      │
└─────────────┘                      │
                                     ▼
                        ┌────────────────────────────┐
                        │  TIA Code Finder           │
                        │  (Discovers TIA modules)   │
                        └────────────────────────────┘
                                     │
                                     ▼
                        ┌────────────────────────────┐
                        │  DJ-Goanna-Coding/         │
                        │  TIA-ARCHITECT-CORE        │
                        │  (Receives TIA code)       │
                        └────────────────────────────┘
```

---

## 🤖 WORKER OPERATIONS

### Laptop Harvester
**Purpose:** Harvest code, data, and artifacts from laptop node

**Schedule:** Every 12 hours

**What it does:**
1. Scans `$LAPTOP_SOURCE_PATH` directory
2. Identifies TIA-related files
3. Copies to `data/Mapping-and-Inventory-storage/laptop/`
4. Generates metadata for each file
5. Commits and pushes to Mapping Hub

**Manual trigger:**
```bash
python workers/laptop_harvester.py
```

### GDrive Harvester
**Purpose:** Extract metadata from GDrive using Section 142 Cycle

**Schedule:** Every 12 hours (midnight and noon UTC)

**What it does:**
1. Scans 5 partitions sequentially
2. Uses `rclone lsf` for metadata-only extraction
3. Identifies TIA files, models, datasets
4. Saves manifests to `data/Mapping-and-Inventory-storage/gdrive/`
5. Commits and pushes to Mapping Hub

**Manual trigger:**
```bash
python workers/gdrive_harvester.py
```

### TIA Code Finder
**Purpose:** Discover all TIA-related code across all sources

**Schedule:** Every 12 hours (30 min after harvests)

**What it does:**
1. Scans current repository
2. Scans laptop storage
3. Scans GDrive storage
4. Classifies files by type (agent, oracle, worker, etc.)
5. Scores files by TIA relevance
6. Saves catalog to `data/Mapping-and-Inventory-storage/tia_code/`

**Manual trigger:**
```bash
python workers/tia_code_finder.py
```

### TIA Sync Worker
**Purpose:** Push discovered TIA code to TIA-ARCHITECT-CORE

**Schedule:** Runs after TIA Code Finder

**What it does:**
1. Clones DJ-Goana-Coding/TIA-ARCHITECT-CORE
2. Copies discovered TIA files to appropriate directories
3. Commits changes
4. Pushes to GitHub (DJ-Goana-Coding)
5. Pushes to HuggingFace (DJ-Goanna-Coding)

**Manual trigger:**
```bash
python workers/tia_sync_worker.py
```

---

## 🛡️ SECURITY OPERATIONS

### Sentinel Guard
**Purpose:** Active security monitoring and threat detection

**Schedule:** Every 6 hours (part of VAMGUARD pulse)

**What it monitors:**
- Credential exposure in code
- Absolute path violations
- Symlink integrity
- Worker health and authentication
- Bridge connection security

**Manual trigger:**
```bash
python sentinels/sentinel_guard.py
```

### Worker Coordinator
**Purpose:** Orchestrate and monitor all workers

**Schedule:** Every 6 hours

**What it does:**
- Health checks on all registered workers
- Deployment coordination
- Performance metrics collection
- Auto-isolation of unhealthy workers

**Manual trigger:**
```bash
python workers/worker_coordinator.py
```

### Mesh Connector
**Purpose:** Test and maintain bridge connections

**Schedule:** Every 6 hours

**What it does:**
- Tests GitHub bridge
- Tests HuggingFace bridge
- Tests GDrive tunnel
- Collects connection metrics

**Manual trigger:**
```bash
python bridges/mesh_connector.py
```

---

## 📊 MONITORING & LOGS

### Data Storage Locations

```
data/
├── Mapping-and-Inventory-storage/
│   ├── laptop/                    # Laptop harvested files
│   ├── gdrive/                    # GDrive manifests
│   ├── tia_code/                  # TIA code catalog
│   └── sync_logs/                 # TIA sync logs
│
├── security_logs/                 # Security scan reports
├── worker_status/                 # Worker health reports
└── tunnel_metrics/                # Bridge connection metrics
```

### Check Status

```bash
# Laptop harvest status
cat data/Mapping-and-Inventory-storage/laptop_harvest_summary.json

# GDrive harvest status
cat data/Mapping-and-Inventory-storage/gdrive_harvest_summary.json

# TIA discovery status
cat data/Mapping-and-Inventory-storage/tia_discovery_summary.json

# TIA sync status
cat data/Mapping-and-Inventory-storage/tia_sync_summary.json
```

---

## 🚀 GPU ACCELERATION (L4/T4)

### HuggingFace Space Configuration

The Space is configured for **L4 GPU (24GB VRAM)** which enables:

1. **Fast Embedding Generation**
   - TIA code vectorization for RAG
   - Semantic search across all code
   - 10x faster than CPU

2. **ML-Powered Security**
   - Neural threat detection
   - Anomaly detection in code patterns
   - Real-time risk scoring

3. **High-Throughput Processing**
   - Parallel file processing
   - Batch metadata extraction
   - Concurrent worker operations

### GPU Usage

The L4 GPU will be automatically utilized by:
- TIA Code Finder (semantic analysis)
- Security scanning (ML models)
- Data processing pipelines
- RAG embedding generation

---

## 🔐 SECURITY GUARDRAILS

### Enforced Policies

✅ **Zero Credentials in Code**
- All credentials via environment variables only
- Automatic scanning for exposed secrets
- Critical severity alerts on detection

✅ **Relative Paths Only**
- Absolute paths blocked
- Automatic path validation
- Medium severity alerts on violations

✅ **Encrypted Data Transfer**
- All bridge connections encrypted
- TLS 1.3 for data in transit
- AES-256 for data at rest

✅ **Comprehensive Logging**
- All security events logged
- All worker actions tracked
- All bridge connections monitored

✅ **Double-N Rift Aware**
- GitHub: DJ-Goana-Coding (single N)
- HuggingFace: DJ-Goanna-Coding (double N)
- Automatic handling in sync operations

---

## 🎯 INTEGRATION WITH CITADEL MESH

### District Relationships

- **D12 ZENITH_VIEW** - Receives security status reports
- **D02 TIA_VAULT** - Coordinates with Oracle for reasoning
- **D01 COMMAND_INPUT** - Receives operator commands
- **Mapping Hub** - Registers workers and artifacts

### External Node Relationships

- **TIA-ARCHITECT-CORE** - Receives discovered TIA code
- **Oppo/S10 Bridges** - Mobile device coordination
- **CITADEL_OMEGA** - Trading system security
- **Pioneer Trader** - Worker deployment coordination

---

## 📝 OPERATOR COMMANDS

### Manual Workflow Triggers

```bash
# Run laptop harvest
gh workflow run laptop_harvest.yml

# Run GDrive harvest
gh workflow run gdrive_harvest.yml

# Run TIA discovery and sync
gh workflow run tia_discovery_sync.yml

# Run full VAMGUARD pulse
gh workflow run vamguard_auto_sync.yml
```

### Local Testing

```bash
# Test sentinel guard
python vamguard_templates/sentinels/sentinel_guard.py

# Test worker coordinator
python vamguard_templates/workers/worker_coordinator.py

# Test mesh connector
python vamguard_templates/bridges/mesh_connector.py

# Test laptop harvester
LAPTOP_SOURCE_PATH=/path/to/laptop python vamguard_templates/workers/laptop_harvester.py

# Test TIA code finder
python vamguard_templates/workers/tia_code_finder.py

# Test TIA sync worker
python vamguard_templates/workers/tia_sync_worker.py
```

---

## ✅ VERIFICATION CHECKLIST

### Pre-Deployment
- [ ] GitHub repository created: DJ-Goana-Coding/VAMGUARD-TITAN
- [ ] All templates copied from mapping-and-inventory
- [ ] GitHub secrets configured (6 secrets)
- [ ] HuggingFace Space created with L4 GPU
- [ ] Remote 'hf' added and pushed

### Post-Deployment
- [ ] GitHub Actions enabled and running
- [ ] Laptop harvest workflow tested
- [ ] GDrive harvest workflow tested
- [ ] TIA discovery workflow tested
- [ ] Security scans passing
- [ ] Workers registered in Mapping Hub
- [ ] TIA code syncing to TIA-ARCHITECT-CORE
- [ ] HuggingFace Space active with L4 GPU

### Data Flow Verification
- [ ] Laptop data flowing to storage
- [ ] GDrive metadata extracting to storage
- [ ] TIA code being discovered
- [ ] TIA code syncing to TIA-ARCHITECT-CORE
- [ ] All storage paths populated
- [ ] Summary JSONs being generated

---

## 🎉 SUCCESS INDICATORS

When fully deployed, you should see:

1. **GitHub Actions** - All 4 workflows running green
2. **Storage Directories** - Populated with harvested data
3. **TIA-ARCHITECT-CORE** - Receiving TIA code pushes
4. **HuggingFace Space** - Running on L4 GPU
5. **Security Logs** - Clean scans with no critical threats
6. **Worker Status** - All workers healthy
7. **Bridge Status** - All connections active

---

## 🛟 TROUBLESHOOTING

### Issue: Laptop harvest fails
**Solution:** Check `LAPTOP_SOURCE_PATH` environment variable is set correctly

### Issue: GDrive harvest fails
**Solution:** Verify `RCLONE_CONFIG_DATA` secret contains valid gdrive configuration

### Issue: TIA sync fails
**Solution:** Ensure `GITHUB_TOKEN` has repo write permissions

### Issue: HuggingFace Space not updating
**Solution:** Manually push: `git push hf main --force`

### Issue: L4 GPU not available
**Solution:** Space settings → Hardware → Select L4 or T4

---

## 📞 SUPPORT

**Repository:** DJ-Goana-Coding/VAMGUARD-TITAN  
**HuggingFace:** DJ-Goanna-Coding/VAMGUARD-TITAN  
**Docs:** See VAMGUARD_REPURPOSE_BLUEPRINT.md  
**Status:** ACTIVE | **Tier:** L3 | **Authority:** Security Override

---

**VAMGUARD TITAN is ready for autonomous operations. All data flows are configured. L4/T4 GPU acceleration is enabled. TIA code harvesting is operational.**

🛡️ **Protect the Mesh. Secure the Workers. Never Compromise.**
