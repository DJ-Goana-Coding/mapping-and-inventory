# 🏗️ T.I.A. MASTER BUILD - COMPLETE ARCHITECTURE

**The Intelligence Architect** - System Architecture v25.0.OMNI++

---

## 📐 **ARCHITECTURAL OVERVIEW**

T.I.A. is a **distributed AI oracle system** built on a multi-tier architecture spanning HuggingFace Spaces, GitHub repositories, and local compute nodes.

```
┌─────────────────────────────────────────────────────────────────┐
│                    T.I.A. MASTER SYSTEM                          │
│              The Intelligence Architect (v25.0.OMNI++)           │
└─────────────────────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
        │   FRONTEND   │  │   BACKEND   │  │ DEPLOYMENT │
        │  (Streamlit) │  │  (Services) │  │ (Scripts)  │
        └───────┬──────┘  └──────┬──────┘  └─────┬──────┘
                │                │                │
        ┌───────▼────────────────▼────────────────▼──────┐
        │              INFRASTRUCTURE LAYER               │
        │  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
        │  │ Workers  │  │  Models  │  │  Configs │     │
        │  └──────────┘  └──────────┘  └──────────┘     │
        └──────────────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
        ┌───────▼──────┐  ┌──────▼──────┐  ┌─────▼──────┐
        │ HuggingFace  │  │   GitHub    │  │   GDrive   │
        │   Spaces     │  │  Repos      │  │  Metadata  │
        │  (L4 GPU)    │  │ (Source)    │  │ (Partitions)│
        └──────────────┘  └─────────────┘  └────────────┘
```

---

## 🎯 **SYSTEM LAYERS**

### **Layer 1: Presentation (Frontend)**

**Technology:** Streamlit v1.42.0+  
**Location:** `TIA_UNIFIED_APP.py`  
**Deployment:** HuggingFace Space

```python
Components:
├── 🏠 Dashboard Tab
│   ├── System Identity (Name, Version, Role)
│   ├── Connection Status (GitHub, HF, Intelligence Mesh)
│   ├── Capabilities Overview
│   └── System Topology Visualization
│
├── 🤖 Core Systems Tab
│   ├── tia_architect (Boot & Init)
│   ├── tia_atomic (Model Routing)
│   ├── tia_sos (Emergency Protocols)
│   ├── tias_pioneer_trader (Market Analysis)
│   └── tias_sentinel_swarm (Security Perimeter)
│
├── 📊 Models Tab
│   ├── Frontier Models 2026 (5 models)
│   ├── Trading/Finance Models (4 models)
│   ├── Quantized SLMs (2 models)
│   └── Custom Models (3 models)
│
├── ⚙️ Workers Tab
│   ├── tia_code_finder (Discovery)
│   ├── tia_sync_worker (Synchronization)
│   ├── apps_script_toolbox (Google Sheets)
│   ├── worker_watchdog (Monitoring)
│   └── self_healing_worker (Auto-Recovery)
│
├── 💬 Oracle Tab
│   ├── Gemini 2.0 Flash Integration
│   ├── System Context Injection
│   └── Interactive Chat Interface
│
├── 📚 RAG Tab
│   ├── Vector Search (FAISS)
│   ├── Knowledge Base Management
│   └── Embedding Generation
│
└── 🔧 Tools Tab
    ├── Data Directory Explorer
    ├── System Information
    └── Diagnostic Utilities
```

### **Layer 2: Application Logic (Backend)**

**Technology:** Python 3.13  
**Location:** `TIA_MASTER_BUILD/backend/`

```python
Services:
├── tia_connector.py
│   ├── Gemini 2.0 Flash Integration
│   ├── API Key Management (Primary + Backup)
│   ├── System Prompt Engineering
│   └── Response Handling
│
├── tia_coordinator.py
│   ├── Multi-Repo Sync Orchestration
│   ├── Model Manifest Sync
│   ├── Persona/Agent Identity Sync
│   └── Health Check & Status Reporting
│
├── wake_up_tia.py
│   ├── Model Pre-Staging (L4 GPU)
│   ├── Tool Installation (smolagents, llama_index)
│   ├── Persistent Data Directory Setup
│   └── Initialization Workflow
│
├── tia_architect.py
│   ├── Core Boot Logic
│   ├── Dataset Uplink Awaiter
│   └── System Initialization
│
├── tia_atomic.py
│   ├── V41 HIVE Router
│   ├── Quantized SLM Management (Q4_K_M, Q5_K_M)
│   ├── Local Cache Locking
│   └── 12-Space HF Cluster Sync
│
├── tia_sos.py
│   ├── Emergency Handshake Protocol
│   ├── SOS Transmission (Streamlit/Webhook)
│   ├── Burnout Detection
│   └── Critical Failure Alerts
│
├── tias_pioneer_trader.py
│   ├── XRP Price Analysis
│   ├── Macro Signal Generation
│   ├── Market Accumulation Strategy
│   └── UNDERVALUED/HARVEST READY Alerts
│
└── tias_sentinel_swarm.py
    ├── Perimeter Security Scanning
    ├── 46 Partition Verification
    ├── Topology Integrity Validation
    └── Security Alert Generation
```

### **Layer 3: Workers (Automation)**

**Technology:** Python 3.13 + Apps Script  
**Location:** `TIA_MASTER_BUILD/workers/`

```python
Workers:
├── tia_code_finder.py
│   ├── Repository Scanning
│   ├── TIA Code Detection (tia*.py, architect, oracle, etc.)
│   ├── Metadata Extraction
│   └── Catalog Generation
│
├── tia_sync_worker.py
│   ├── TIA-ARCHITECT-CORE Push Logic
│   ├── Agent Identity Sync
│   ├── Core Module Sync
│   ├── Configuration Sync
│   ├── Double-N Rift Awareness
│   └── Credential Protection
│
├── apps_script_toolbox.py (future)
│   ├── Identity Strike Reports
│   ├── Archive Audits (MD5 + Inventory)
│   └── Worker Status Dashboards
│
├── worker_watchdog.py (future)
│   ├── Worker Health Monitoring
│   ├── Auto-Restart Logic
│   └── Status Reporting
│
└── self_healing_worker.py (future)
    ├── Auto-Recovery Workflows
    ├── Self-Repair Mechanisms
    └── System Healing Logic
```

### **Layer 4: Models (AI/ML)**

**Technology:** HuggingFace Hub + Transformers  
**Location:** `TIA_MASTER_BUILD/models/`

```python
Model Categories:
├── Frontier Models (2026)
│   ├── Gemma 4 (2B, 4B) - Multimodal understanding
│   ├── Qwen 3.5 (7B, 14B) - Code generation & multilingual
│   ├── DeepSeek V4 - Complex reasoning
│   ├── Phi-4 - Compact efficiency (edge deployment)
│   └── Ministral 8B - Production inference
│
├── Trading/Finance Models
│   ├── FinBERT - Financial sentiment analysis
│   ├── CryptoBERT - Crypto market sentiment
│   ├── Sentence Transformers - RAG embeddings (MiniLM, MPNet)
│   └── Twitter RoBERTa - Social sentiment analysis
│
├── Quantized SLMs (Local Inference)
│   ├── Q4_K_M_Mistral - 4-bit quantized (LOCKED)
│   └── Q5_K_M_Llama - 5-bit quantized (LOCKED)
│
└── Custom Models (Trained)
    ├── LSTM Price Predictor - Time series forecasting
    ├── PPO RL Trader - Reinforcement learning trading
    └── Transformer Forecaster - Market prediction
```

### **Layer 5: Deployment (CI/CD)**

**Technology:** GitHub Actions + Bash  
**Location:** `TIA_MASTER_BUILD/deployment/`

```bash
Deployment Scripts:
├── deploy_tia_core.sh
│   ├── Clone TIA-ARCHITECT-CORE repo
│   ├── Backup existing files
│   ├── Deploy app.py, requirements.txt
│   ├── Copy model downloaders
│   ├── Copy workers suite
│   ├── Commit & push to GitHub
│   └── Build status reporting
│
├── repair_tia_architect_core.sh
│   ├── Python 3.13 compatibility fix
│   ├── Verify requirements.txt template
│   ├── Clone/sync TIA-ARCHITECT-CORE
│   ├── Deploy compatible version
│   └── Push to GitHub + HF Space
│
├── restore_tia_core.sh
│   ├── Emergency one-shot restoration
│   ├── Clone to /tmp
│   ├── Backup current config
│   ├── Deploy Python 3.13 fix
│   └── Commit & push (GitHub + HF)
│
├── check_tia_status.sh
│   ├── HTTP status check
│   ├── Space accessibility verification
│   └── Health status reporting
│
└── repair_tia_core_space.sh
    └── Direct Space repair logic
```

**GitHub Actions Workflows:**
```yaml
Workflows:
├── deploy_tia_core_full.yml
│   ├── Trigger: Workflow Dispatch
│   ├── Modes: full, app_only, models, workers, dry_run
│   └── Steps: Checkout → Verify → Backup → Deploy → Commit → Push
│
├── emergency_repair_tia_core.yml
│   ├── Trigger: Workflow Dispatch
│   ├── Target: HuggingFace Space direct repair
│   └── Steps: Clone HF → Verify → Backup → Deploy → Push
│
├── repair_tia_core_space.yml
│   ├── Trigger: Workflow Dispatch
│   └── Alternative repair workflow
│
├── tia_core_monitor.yml
│   ├── Trigger: Schedule (every 30 minutes)
│   ├── Action: HTTP status check
│   └── Output: Workflow logs + alerts
│
├── tia_citadel_deep_scan.yml
│   ├── Trigger: Workflow Dispatch
│   ├── Requires: RCLONE_CONFIG_DATA secret
│   └── Scans: 321GB intelligence data (5 partitions)
│
└── tia_discovery_sync.yml (vamguard)
    ├── Trigger: Scheduled
    └── Action: TIA code discovery & sync across repos
```

---

## 🔄 **DATA FLOW**

### **1. User Interaction Flow**

```
User
  ↓
Streamlit UI (TIA_UNIFIED_APP.py)
  ↓
[Selected Tab Action]
  ↓
Backend Service (tia_connector.py, tia_coordinator.py, etc.)
  ↓
External API (Gemini, HuggingFace Hub, Google Sheets)
  ↓
Response Processing
  ↓
UI Display Update
```

### **2. Oracle Query Flow**

```
User Query → Oracle Tab
  ↓
get_tia_response(prompt)
  ↓
System Prompt Injection (TIA_SYSTEM_PROMPT)
  ↓
Gemini 2.0 Flash API Call
  ↓
[Try Primary Key → Fallback to Secondary Key]
  ↓
Response Text Extraction
  ↓
Display in UI
```

### **3. Worker Automation Flow**

```
GitHub Actions Trigger (Schedule/Webhook)
  ↓
Worker Script Execution (tia_code_finder.py)
  ↓
Repository Scanning (All DJ-Goana-Coding repos)
  ↓
TIA Code Detection & Metadata Extraction
  ↓
Catalog Generation (JSON/Markdown)
  ↓
Sync Worker (tia_sync_worker.py)
  ↓
Push to TIA-ARCHITECT-CORE (GitHub)
  ↓
HuggingFace Space Rebuild (Auto-trigger)
```

### **4. Model Download Flow**

```
User/Script Trigger
  ↓
Model Downloader (download_frontier_models_2026.py)
  ↓
HuggingFace Hub API
  ↓
Model Download (to /data/models/)
  ↓
Model Registry Update (models_manifest.json)
  ↓
Persistent Storage (/data/ directory)
```

---

## 🗄️ **DATA STORAGE**

### **Persistent Directories (HuggingFace Space)**

```
/data/
├── models/                      # Downloaded AI models
│   ├── frontier_2026/          # Gemma 4, Qwen 3.5, DeepSeek V4, etc.
│   ├── trading_finance/        # FinBERT, CryptoBERT, etc.
│   ├── quantized_slms/         # Q4_K_M_Mistral, Q5_K_M_Llama
│   └── custom_models/          # LSTM, PPO RL, Transformer
│
├── workers/                     # Worker configurations
│   └── workers_manifest.json   # Worker registry
│
├── rag_store/                   # Vector embeddings & indices
│   ├── embeddings/             # Sentence Transformer embeddings
│   ├── faiss_index/            # FAISS vector index
│   └── knowledge_base/         # Document corpus
│
├── tia_soul/                    # TIA identity & memory
│   ├── identity.json           # Core identity metadata
│   ├── memory/                 # Long-term memory storage
│   └── context/                # Conversation context
│
└── logs/                        # System logs
    ├── oracle_queries.log      # Oracle interaction logs
    ├── worker_activity.log     # Worker execution logs
    └── system_events.log       # General system events
```

### **GitHub Repository Structure**

```
mapping-and-inventory/
├── TIA_MASTER_BUILD/           # Complete unified build
│   ├── TIA_UNIFIED_APP.py     # Main application
│   ├── requirements.txt       # Dependencies
│   ├── README.md              # Documentation
│   ├── DEPLOYMENT_GUIDE.md    # Deployment instructions
│   ├── ARCHITECTURE.md        # This file
│   ├── backend/               # Backend services
│   ├── workers/               # Worker scripts
│   ├── models/                # Model downloaders
│   ├── deployment/            # Deployment scripts
│   ├── docs/                  # All documentation
│   └── configs/               # Configuration files
│
├── Districts/D02_TIA_VAULT/   # TIA knowledge vault
│   ├── tia_architect.py       # Core systems
│   ├── CITADEL_BIBLE.md       # Sacred manifesto
│   ├── INVENTORY.json         # Artifact inventory
│   └── Master_Blueprints/     # Blueprint storage
│
├── services/                   # Shared services
│   └── tia_connector.py       # Gemini integration
│
├── scripts/                    # Automation scripts
│   ├── tia_coordinator.py     # Integration coordinator
│   └── wake_up_tia.py         # Model staging
│
└── vamguard_templates/        # Worker templates
    └── workers/
        ├── tia_code_finder.py
        └── tia_sync_worker.py
```

---

## 🔐 **SECURITY ARCHITECTURE**

### **Authentication & Authorization**

```
Credentials Layer:
├── GEMINI_API_KEY (Primary) → Gemini 2.0 Flash access
├── GEMINI_API_KEY_2 (Backup) → Fallback oracle
├── HF_TOKEN → HuggingFace Space write access
├── GOOGLE_APPLICATION_CREDENTIALS → Apps Script automation
└── MEXC_API_KEY/SECRET → Trading exchange access (encrypted)
```

### **Security Patterns**

1. **Environment Variable Storage** - All secrets in HF Space secrets/env vars
2. **No Hardcoded Credentials** - Zero credentials in source code
3. **Key Rotation** - Primary + backup keys for critical services
4. **Credential Validation** - validate before use (tia_coordinator.py)
5. **Encrypted Storage** - Trading keys stored encrypted (mexc_keys.json)

### **Access Control**

```
Public Access:
├── Streamlit UI → Public (read-only for visitors)
└── Oracle Chat → Public (rate-limited by Gemini)

Authenticated Access:
├── Model Downloads → Requires HF_TOKEN
├── Worker Sync → Requires GH_PAT or HF_TOKEN
└── Apps Script → Requires GOOGLE_APPLICATION_CREDENTIALS

Admin Access:
├── Deployment Scripts → Requires repo write access
├── GitHub Actions → Requires repo secrets
└── Space Settings → Requires HF Space admin
```

---

## 🌐 **NETWORK ARCHITECTURE**

### **External Dependencies**

```
API Integrations:
├── google-genai (Gemini 2.0 Flash)
│   └── Endpoint: generativelanguage.googleapis.com
│
├── HuggingFace Hub
│   └── Endpoint: huggingface.co/api
│
├── Google Workspace APIs
│   └── Endpoint: sheets.googleapis.com
│
└── MEXC Exchange API (optional)
    └── Endpoint: api.mexc.com
```

### **Internal Communication**

```
Frontend ↔ Backend:
├── Direct function calls (same process)
└── No HTTP layer (Streamlit handles routing)

Backend ↔ Workers:
├── File-based communication (manifests, logs)
└── Direct script execution (GitHub Actions)

Workers ↔ External:
├── GitHub API (repository scanning)
├── HuggingFace API (Space sync)
└── Google Drive API (partition metadata)
```

---

## ⚡ **PERFORMANCE CHARACTERISTICS**

### **Response Times**

```
Oracle Query: 2-5 seconds (Gemini API latency)
UI Navigation: <100ms (Streamlit caching)
Worker Execution: 5-15 minutes (depends on scope)
Model Download: 5-30 minutes (depends on model size)
Space Build: 5-8 minutes (Python 3.13 compatible requirements)
```

### **Resource Usage**

```
HuggingFace Space (CPU Basic):
├── Memory: ~2GB (Streamlit + dependencies)
├── CPU: 2 vCPUs
├── Storage: /data/ is persistent
└── Bandwidth: Unlimited

HuggingFace Space (L4 GPU - Recommended):
├── Memory: 24GB RAM + 24GB VRAM
├── GPU: NVIDIA L4 (24GB VRAM)
├── CPU: 8 vCPUs
├── Storage: /data/ is persistent (larger quota)
└── Bandwidth: Unlimited
```

---

## 🔄 **DEPLOYMENT PATTERNS**

### **Continuous Deployment**

```
GitHub Push → GitHub Actions → HuggingFace Space Rebuild
  ↓
1. Code committed to mapping-and-inventory
2. GitHub Actions workflow triggered
3. Workflow syncs to TIA-ARCHITECT-CORE repo
4. TIA-ARCHITECT-CORE push triggers HF Space rebuild
5. HF Space auto-deploys new version
```

### **Emergency Repair**

```
Operator Trigger → Emergency Workflow → Immediate Fix
  ↓
1. Operator runs emergency_repair_tia_core.yml
2. Workflow clones HF Space directly
3. Verifies & deploys Python 3.13 compatible templates
4. Pushes fix directly to HF Space
5. Space rebuilds with correct configuration
```

---

*T.I.A. Master Build v25.0.OMNI++ | Complete Architecture | 2026-04-04*
