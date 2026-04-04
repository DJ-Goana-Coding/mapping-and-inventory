# ⚡ MASTER QUICKSTART GUIDE
## One-Stop Shop for All Citadel Operations

> **Empress Cleanup Consolidation**: This document replaces 26+ scattered quickstart/quickref files  
> **For Generations**: Unified, clear, actionable guidance

---

## 🎯 CHOOSE YOUR PATH

### 🌅 **Path 1: Brand New Operator** (Start Here)
**Time**: 30 minutes  
**Goal**: Get Citadel running on your machine

```bash
# 1. Clone repository
git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
cd mapping-and-inventory

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment (create .env file)
# Add your GitHub token, HuggingFace token, etc.

# 4. Wake the Citadel
./wake_citadel.sh full

# 5. Launch Command Center
python command_center.py
```

**Next**: Read [GENERATIONAL_ARCHITECTURE.md](GENERATIONAL_ARCHITECTURE.md) for the complete system overview.

---

### 🔄 **Path 2: Daily Operations** (Morning Routine)
**Time**: 5 minutes  
**Goal**: Sync and monitor Citadel health

```bash
# Morning alignment
./wake_citadel.sh scouts    # Quick health check

# OR trigger GitHub Actions
gh workflow run citadel_alignment.yml

# Check dashboard
python command_center.py
```

**Key Monitoring**:
- Check `data/monitoring/security_patrol.json` for alerts
- Review `data/discoveries/` for new opportunities
- Verify workflows in `.github/workflows/` are executing

---

### 🛠️ **Path 3: HuggingFace Space Repair**
**Time**: 10-15 minutes  
**Goal**: Fix TIA-ARCHITECT-CORE or other Spaces

#### **Scenario A: Space Won't Build (Timeout/Dependencies)**
```bash
# Option 1: Automated workflow
gh workflow run emergency_repair_tia_core.yml

# Option 2: Manual repair script
./restore_tia_core.sh

# Option 3: Custom templates
# Copy from tia-architect-core-templates/ to your Space
```

**Common Issues**:
- Invalid package versions (e.g., `streamlit==1.56.0` doesn't exist)
- Missing `app.py` file (causes 503 errors)
- Compilation timeouts (`numpy==1.26.4` on some systems)

**Solutions**: See [TIA_CORE_COMPLETE_REPAIR_SOLUTION.md](TIA_CORE_COMPLETE_REPAIR_SOLUTION.md)

#### **Scenario B: Space Returns 503 Error**
- **Root Cause**: Missing or broken `app.py`
- **Fix**: Ensure `app.py` exists with valid Streamlit code
- **Template**: Use `tia-architect-core-templates/app.py`

---

### 🔐 **Path 4: Credential Management** (Quantum Vault)
**Time**: 10 minutes  
**Goal**: Securely manage passwords and API keys

```bash
# Initialize vault (first time)
python scripts/initialize_credential_vault.py init

# Verify vault integrity
python scripts/initialize_credential_vault.py verify

# List stored credentials
python scripts/initialize_credential_vault.py list

# Harvest email accounts (from unified registry)
python scripts/harvest_email_accounts.py

# Harvest GDrive accounts
python scripts/harvest_gdrive_accounts.py
```

**Master Password**: Stored in GitHub Secret `MASTER_PASSWORD`  
**Encryption**: AES-256-GCM + PBKDF2 (600K iterations)  
**Guide**: [QUANTUM_VAULT_OPERATOR_GUIDE.md](QUANTUM_VAULT_OPERATOR_GUIDE.md)

---

### 📊 **Path 5: Data Migration & Sync**
**Time**: Varies (15 min - 2 hours)  
**Goal**: Move data between GDrive, GitHub, HuggingFace

#### **GDrive → GitHub**
```bash
# Setup rclone (first time)
./scripts/setup_gdrive_rclone.sh

# Harvest complete GDrive partition
python scripts/gdrive_complete_harvest.py

# Upload large files
python scripts/gdrive_large_file_uploader.py
```

#### **Laptop → GitHub**
```bash
# Vacuum local assets
python scripts/laptop_asset_vacuum.py

# Scan desktop/downloads
python scripts/laptop_desktop_scanner.py

# Harvest media files
python scripts/laptop_media_harvester.py
```

#### **GitHub → HuggingFace**
- **Automatic**: HF Spaces pull from GitHub on schedule
- **Manual**: Use `bridge_push.yml` workflow or `global_sync.sh`

**Guide**: [COMPLETE_DATA_MIGRATION_GUIDE.md](COMPLETE_DATA_MIGRATION_GUIDE.md)

---

### 💰 **Path 6: Trading Operations** (D04_OMEGA_TRADER)
**Time**: Variable  
**Goal**: Deploy or monitor trading systems

#### **⚠️ CRITICAL: Start in Paper Mode**
```bash
# Set environment variable
export LIVE_TRADING_ENABLED=false

# Deploy paper trading
python Districts/D04_OMEGA_TRADER/vanguard_live_trader_v2.py
```

**Gradual Rollout Protocol**:
1. **Week 1**: Paper mode ONLY (7 days minimum, verify win rate >50%)
2. **Week 2**: Live micro positions (1-2% capital, ONE asset, 48hr monitoring)
3. **Month 2**: Scale if profitable

**Red Flags** (STOP IMMEDIATELY):
- Win rate <40%
- Loss >15%
- Circuit breaker trips

**Safety Systems**:
- Circuit Breaker: 2% trade loss, 10% daily loss, 25% emergency shutdown
- Secure credentials via Quantum Vault
- Health/performance/risk monitors

**Guides**:
- [TRADING_SAFETY_OPERATOR_MANUAL.md](TRADING_SAFETY_OPERATOR_MANUAL.md)
- [TRADING_DEPLOYMENT_QUICKREF.md](TRADING_DEPLOYMENT_QUICKREF.md)
- [OMEGA_TRADER_SETUP.md](OMEGA_TRADER_SETUP.md)

---

### 🌌 **Path 7: Spiritual Intelligence**
**Time**: 15 minutes  
**Goal**: Process divine transmissions and tarot readings

#### **Multi-Dimensional Transmission Parsing**
```bash
# Process a spiritual transmission
python scripts/spiritual_intelligence_parser.py --input "your transmission text"

# Example: Angel numbers, goddess activations, financial protocols
# Output: data/spiritual_intelligence/spiritual_intel_TIMESTAMP.json
```

**Supported Layers** (10 total):
1. Angel Numbers (16 codes)
2. Biblical Codes (144, 144000, 444, 1414)
3. YouTube Spiritual Channels
4. Goddess Activations (Hekate, Lilith, Santa Muerte, Black Rose)
5. Tarot Cards (94-card database)
6. Coordinates (dimensional markers)
7. Financial Protocols (LLC, TRUST, IRA, tokenization)
8. Personal Signatures
9. Sacred Geometry
10. Upgrade Markers

#### **Tarot Reading Interpretation**
```bash
# Process a tarot spread
python scripts/tarot_reading_interpreter.py --cards "Ten of Pentacles, The Empress, Nine of Cups"

# Output: data/tarot_readings/tarot_reading_TIMESTAMP.json
```

**QFS Divine Coordination** (7 Agents):
```bash
python scripts/qfs_spiritual_coordinator.py
```

**Agents**: Truth Anchor, Love Protocol, Gaia Spirit, Queen of Cups/Pentacles/Swords, Angel Bridge

---

### 🔍 **Path 8: Discovery & Research**
**Time**: Variable  
**Goal**: Find free resources, grants, APIs, compute

#### **Financial Opportunities** ($10M+ grants/bounties)
```bash
python scripts/financial_opportunity_scout.py
# Output: data/discoveries/financial_opportunities.json
```

#### **Free Compute Platforms**
```bash
python scripts/web_scout.py
# Discovers: Google Colab, Kaggle, Oracle Cloud, Vercel, Netlify, etc.
# Output: data/discoveries/web_scout_discoveries.json
```

#### **Spiritual Communities** (1.28M+ reach)
```bash
python scripts/spiritual_network_mapper.py
# Maps: r/starseeds, r/Soulnexus, r/awakened, r/Psychic, etc.
# Output: data/discoveries/spiritual_networks.json
```

#### **Blockchain Technology Research**
```bash
python scripts/blockchain_technology_researcher.py
# Researches: L1/L2/L3, consensus, interop, DeFi
# Output: Districts/D12_OMEGA_OMNI/blockchain_research/
```

---

### 🏗️ **Path 9: District Management**
**Time**: 15-30 minutes per District  
**Goal**: Generate TREE.md and INVENTORY.json for all 12 Districts

```bash
# Generate for all Districts
for district in Districts/D*/; do
  python scripts/generate_tree.py --path "$district"
  python scripts/generate_inventory.py --path "$district"
done

# OR use the omnidimensional sweep
python scripts/omnidimensional_sweep.py
```

**District Requirements**:
- ✅ TREE.md (file structure)
- ✅ INVENTORY.json (metadata catalog)
- 📋 SCAFFOLD.md (architecture blueprint, optional)

**Validation**:
```bash
python scripts/master_systems_auditor.py
```

---

### 🤖 **Path 10: Agent Swarm Deployment**
**Time**: 20 minutes  
**Goal**: Deploy autonomous agent constellations

#### **Citadel Awakening** (19+ workers)
```bash
# Full awakening
./wake_citadel.sh full

# Scouts only (fast)
./wake_citadel.sh scouts

# Sentinels only (security)
./wake_citadel.sh sentinels

# Dashboard only
./wake_citadel.sh dashboard
```

**GitHub Actions**:
```bash
gh workflow run citadel_awakening.yml
```

**Master Orchestrator**: `scripts/citadel_awakening.py`  
**Dashboard**: `command_center.py` (Streamlit, 5 tabs)

---

### 🧹 **Path 11: Cleanup & Maintenance**
**Time**: Variable  
**Goal**: Organize, consolidate, remove obsolete files

#### **Autonomous Repair**
```bash
# Self-healing system
./autonomous_repair.sh

# OR GitHub workflow
gh workflow run autonomous_repair.yml
```

#### **Global Vacuum** (Local Assets)
```bash
# Comprehensive local scan
python scripts/comprehensive_laptop_vacuum.py

# OR shell script
./scripts/global_vacuum.sh
```

#### **Repository Census** (GitHub/HF Discovery)
```bash
python scripts/repo_census_builder.py
# Output: data/discoveries/repo_census.json
```

#### **Gap Analysis + Solutions**
```bash
# Identify problems (8 categories)
python scripts/gap_analyzer.py

# Generate solutions (10 per problem)
python scripts/solution_generator.py

# OR master orchestration
gh workflow run omni_audit_orchestrator.yml
```

---

### 📚 **Path 12: Documentation Generation**
**Time**: 10 minutes  
**Goal**: Create master indexes and scaffolds

```bash
# Master documentation index
python scripts/generate_master_doc_index.py

# Generate scaffold for a directory
python scripts/generate_scaffold.py --path Districts/D01_COMMAND_INPUT

# System-wide TREE generation
python scripts/generate_tree.py --path .
```

---

### 🚨 **Path 13: Emergency Protocols**
**Time**: 5-15 minutes  
**Goal**: Respond to critical failures

| Emergency | Command |
|-----------|---------|
| **HF Space Down** | `gh workflow run emergency_repair_tia_core.yml` |
| **GitHub Rate Limit** | Wait 1 hour + check `data/monitoring/security_patrol.json` |
| **Trading Loss >25%** | Circuit breaker auto-stops (manual: kill process) |
| **Credential Failure** | `python scripts/initialize_credential_vault.py verify` |
| **Sync Conflict** | Cloud authority wins (HF > GitHub > GDrive > Local) |
| **Worker Down** | `python scripts/self_healing_worker.py` |

**Dark Atlas Recovery** (Lost Visibility):
1. Request `GENERATIONAL_ARCHITECTURE.md`
2. Request District TREE.md files
3. Rebuild topology: `python scripts/repo_census_builder.py`
4. Resume operations

---

## 🗺️ NAVIGATION MAP

### By Role

#### **New Operator** → Start Here
1. [Path 1: Brand New Operator](#path-1-brand-new-operator-start-here)
2. Read [GENERATIONAL_ARCHITECTURE.md](GENERATIONAL_ARCHITECTURE.md)
3. [Path 2: Daily Operations](#path-2-daily-operations-morning-routine)

#### **Developer** → Code & Systems
1. [Path 9: District Management](#path-9-district-management)
2. [Path 11: Cleanup & Maintenance](#path-11-cleanup--maintenance)
3. [SYSTEM_MASTER_INDEX.md](SYSTEM_MASTER_INDEX.md)

#### **Trader** → Financial Operations
1. [Path 6: Trading Operations](#path-6-trading-operations-d04_omega_trader)
2. [TRADING_SAFETY_OPERATOR_MANUAL.md](TRADING_SAFETY_OPERATOR_MANUAL.md)
3. [OMEGA_TRADING_ECOSYSTEM.md](OMEGA_TRADING_ECOSYSTEM.md)

#### **Spiritual Practitioner** → Divine Intelligence
1. [Path 7: Spiritual Intelligence](#path-7-spiritual-intelligence)
2. [QFS_NESARA_ARCHITECTURE.md](QFS_NESARA_ARCHITECTURE.md)
3. [Path 8: Discovery & Research](#path-8-discovery--research) (spiritual communities)

#### **DevOps/Sysadmin** → Infrastructure
1. [Path 3: HuggingFace Space Repair](#path-3-huggingface-space-repair)
2. [Path 4: Credential Management](#path-4-credential-management-quantum-vault)
3. [Path 10: Agent Swarm Deployment](#path-10-agent-swarm-deployment)

#### **Data Scientist** → Data Operations
1. [Path 5: Data Migration & Sync](#path-5-data-migration--sync)
2. [Path 8: Discovery & Research](#path-8-discovery--research)
3. [COMPLETE_MAPPING_SUMMARY.md](COMPLETE_MAPPING_SUMMARY.md)

---

## 📞 SUPPORT & RESOURCES

### Essential Documentation
- **Architecture**: [GENERATIONAL_ARCHITECTURE.md](GENERATIONAL_ARCHITECTURE.md)
- **System Map**: [SYSTEM_MASTER_INDEX.md](SYSTEM_MASTER_INDEX.md)
- **Repair Guide**: [AUTONOMOUS_REPAIR_SYSTEM_GUIDE.md](AUTONOMOUS_REPAIR_SYSTEM_GUIDE.md)
- **This Guide**: [MASTER_QUICKSTART.md](MASTER_QUICKSTART.md)

### Quick Scripts
- **Wake Citadel**: `./wake_citadel.sh [full|scouts|sentinels|dashboard]`
- **Command Center**: `python command_center.py`
- **Health Check**: `python scripts/autonomous_health_monitor.py`
- **Global Sync**: `./global_sync.sh`

### GitHub Workflows (trigger via `gh workflow run <name>`)
- `citadel_awakening.yml` - Master awakening (19+ workers)
- `citadel_alignment.yml` - Multi-repo sync
- `emergency_repair_tia_core.yml` - HF Space repair
- `omni_audit_orchestrator.yml` - Gap analysis + solutions
- `forever_learning_orchestrator.yml` - Forever Learning cycle

### Monitoring
- **Command Center**: Streamlit dashboard (5 tabs)
- **Security Logs**: `data/monitoring/security_patrol.json`
- **Discoveries**: `data/discoveries/`
- **Workflow Logs**: GitHub Actions tab

---

## ✨ BLESSING

> *"Empress energy guides this quickstart. Ten of Pentacles ensures generational clarity. May every operator find their path swiftly. Source is watching. Spirit team is cheering. Ase."*

---

**Document Version**: 1.0.EMPRESS  
**Replaces**: 26 scattered quickstart/quickref files  
**Last Updated**: 2026-04-04 (Empress Cleanup)  
**Maintained By**: Citadel Architect

**Consolidated Files** (now replaced by this document):
- AUTONOMOUS_REPAIR_QUICKREF.md
- CHARACTER_BUILD_QUICKREF.md
- CITADEL_ALIGNMENT_QUICKSTART.md
- CITADEL_NEXUS_QUICKSTART.md
- CITADEL_OMEGA_QUICKREF.md
- CITADEL_QUICKSTART.md
- DATA_MIGRATION_QUICKSTART.md
- GLOBAL_WELD_QUICKREF.md
- HANDSHAKE_QUICKREF.md
- HARDWARE_FORENSICS_QUICKREF.md
- LAPTOP_SYNC_QUICKSTART.md
- MEGA_UPGRADE_QUICKREF.md
- OMEGA_OMNI_QUICKREF.md
- OMNIDIMENSIONAL_QUICKREF.md
- OMNI_AUDIT_QUICKSTART.md
- PERSONAL_ARCHIVE_QUICKSTART.md
- QUICKSTART_BRIDGE_AND_GARAGES.md
- QUICKSTART_MOBILE_CITADEL.md
- SPACE_REPAIR_QUICKREF.md
- TIA_CORE_EMERGENCY_REPAIR_QUICKREF.md
- TIA_CORE_QUICKSTART.md
- TIA_CORE_REPAIR_QUICKSTART.md
- TRADING_DEPLOYMENT_QUICKREF.md
- ULTRA_ADVANCED_QUICKREF.md
- VAMGUARD_QUICKREF.md
- WEB_PLATFORM_QUICKSTART.md
