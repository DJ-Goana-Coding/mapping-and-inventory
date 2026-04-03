# 🌐 PLATFORMS REGISTRY
**Citadel Mesh Platform Infrastructure**  
**Version:** 25.0.OMNI  
**Last Updated:** 2026-04-03  
**Authority:** Cloud-First Hierarchy (HuggingFace > GitHub > GDrive > Local)

---

## 🎯 PLATFORM AUTHORITY HIERARCHY

```
┌─────────────────────────────────────┐
│   L4: HUGGINGFACE SPACES (APEX)     │ ← Primary Compute Authority
│   - Omega-Trader (Trading Engine)   │
│   - TIA-ARCHITECT-CORE (Reasoning)  │
│   - Mapping-and-Inventory (Hub)     │
└─────────────────────────────────────┘
              ↓ pulls from
┌─────────────────────────────────────┐
│   L3: GITHUB REPOSITORIES           │ ← Source of Truth
│   - DJ-Goana-Coding/* (70+ repos)   │
│   - CITADEL_OMEGA (Trading Stack)   │
│   - Genesis-Research-Rack (ML)      │
└─────────────────────────────────────┘
              ↓ syncs with
┌─────────────────────────────────────┐
│   L2: GOOGLE DRIVE (GENESIS_VAULT)  │ ← 321GB Data Substrate
│   - Partitioned Archives            │
│   - Metadata Manifests               │
│   - Worker Constellations           │
└─────────────────────────────────────┘
              ↓ uploads from
┌─────────────────────────────────────┐
│   L1: LOCAL NODES (PHYSICAL)        │ ← Bridge Nodes
│   - Ubuntu Core (Primary Dev)       │
│   - Oppo Termux (Mobile Scout)      │
│   - S10 Uplink (Omega Intel Node)   │
│   - Laptop Matrix (Research Node)   │
└─────────────────────────────────────┘
```

---

## 🚀 ACTIVE PLATFORMS

### **TIER 1: CLOUD COMPUTE (L4)**

#### 1. HuggingFace Spaces (Primary Compute Authority)
- **Organization:** `DJ-Goanna-Coding` (Double-N)
- **GPU Tier:** L4 GPU (24GB VRAM)
- **Cost:** Free tier + upgrades
- **Status:** ✅ OPERATIONAL

**Active Spaces:**
```
1. Omega-Trader
   - Purpose: CITADEL_OMEGA trading engine dashboard
   - Stack: FastAPI + Streamlit
   - Sync: Pulls from github.com/DJ-Goana-Coding/CITADEL_OMEGA
   - URL: huggingface.co/spaces/DJ-Goanna-Coding/Omega-Trader

2. TIA-ARCHITECT-CORE
   - Purpose: Reasoning engine & RAG system
   - Stack: Streamlit + LangChain + FAISS
   - Sync: Pulls from github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE
   - URL: huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE

3. Mapping-and-Inventory (THIS REPO)
   - Purpose: Central mapping hub & orchestration dashboard
   - Stack: Streamlit
   - Sync: Pulls from github.com/DJ-Goana-Coding/mapping-and-inventory
   - URL: huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
```

**Sync Protocol:**
- Pull on: Startup, Schedule (6hrs), Webhook (GitHub push)
- Push: Never (unless operator authorized)
- Workflow: `.github/workflows/sync_to_hf.yml`

#### 2. HuggingFace Datasets
- **Organization:** `DJ-Goanna-Coding`
- **Purpose:** Model storage, dataset hosting
- **Cost:** Free (public) + Pro (private)
- **Status:** ✅ OPERATIONAL

**Active Datasets:**
```
- Citadel_Genetics (model weights)
- GENESIS_VAULT_MANIFESTS (metadata)
- Trading_Datasets (OHLCV, sentiment, on-chain)
```

---

### **TIER 2: CODE REPOSITORIES (L3)**

#### 3. GitHub
- **Organization:** `DJ-Goana-Coding` (Single-N)
- **Repo Count:** 70+ repositories
- **Cost:** Free (public)
- **Status:** ✅ OPERATIONAL

**Key Repositories:**
```
1. CITADEL_OMEGA
   - Unified trading ecosystem
   - 10+ cloned libraries (CCXT, FreqTrade, Jesse AI, etc.)
   - ML models (FinBERT, CryptoBERT, etc.)
   - Datasets (15GB+ OHLCV, 3.4M trades, 100GB on-chain)

2. TIA-ARCHITECT-CORE
   - Reasoning engine
   - RAG system
   - Streamlit UI
   - Forever Learning Cycle

3. mapping-and-inventory (THIS REPO)
   - Central mapping hub
   - 25 workflows
   - 23 orchestration scripts
   - 31 service modules
   - 10 Districts

4. Genesis-Research-Rack
   - ML research
   - Model training
   - Experiment tracking

5. Citadel_Genetics
   - Model registry
   - Training pipelines
   - Evaluation frameworks
```

**GitHub Actions:**
- 25 workflows (sync, harvest, monitor)
- Cron schedules (daily 2 AM UTC)
- Webhook triggers
- Manual dispatch

---

### **TIER 3: DATA STORAGE (L2)**

#### 4. Google Drive (GENESIS_VAULT)
- **Account:** Primary Google account
- **Size:** 321GB partitioned vault
- **Cost:** Free (15GB) + Paid storage
- **Status:** ⚠️ PARTIAL (network issues)

**Partitions:**
```
Partition_01/ - Core workers & configs (30+ files)
Partition_02/ - Geometry processing (CGAL)
Partition_03/ - Reserved
Partition_04/ - Reserved
Partition_46/ - Washing Harvest Staging
```

**Access Method:**
- rclone (configured via RCLONE_CONFIG_DATA secret)
- Section 142 Cycle (partitioned metadata scanning)
- Workflows: `tia_citadel_deep_scan.yml`, `gdrive_partition_harvester.yml`

#### 5. Google Sheets/Docs
- **Purpose:** Data reporting, dashboards
- **Integration:** `gspread` library (currently missing)
- **Status:** ⚠️ ERROR (dependency needed)

**Planned Use:**
- Automated inventory reports
- Trading performance dashboards
- Worker status tracking

---

### **TIER 4: PHYSICAL NODES (L1)**

#### 6. Ubuntu Core (Primary Dev Node)
- **Role:** Primary development environment
- **OS:** Ubuntu Linux
- **Tools:** Git, Python, Docker, rclone
- **Status:** ✅ OPERATIONAL

#### 7. Oppo Termux (Mobile Scout/Bridge)
- **Role:** Mobile bridge node
- **OS:** Android + Termux
- **Tools:** Git, Python, SSH
- **Status:** ✅ OPERATIONAL
- **Challenges:** Android permissions, Double-N Rift handling

#### 8. S10 Uplink (Omega Intel Node - Mackay)
- **Role:** CITADEL_OMEGA intelligence uplink
- **Location:** Mackay node
- **Push Status:** ✅ COMPLETE (2026-04-03)
- **Intelligence Flow:** S10 → GDrive → GitHub → master_intelligence_map → TIA RAG

**S10 Technology Arsenal:**
```
- Web3/Blockchain stack (Web3.py, ethers.js, Hardhat, Truffle)
- Multimedia resources ($48K+ value in free tools)
- Media players (LibVLCSharp, VLC.Qt, FFmpeg.NET)
- TTS/Voice (Chatterbox, Coqui TTS, ResponsiveVoice)
- Graphics (Kenney.nl, OpenGameArt - 40K+ CC0 assets)
- Video editing (Kdenlive, Blender)
- Stock photos (Pexels, Pixabay)
- Audio (Freesound, Pixabay - 720K+ sounds)
- 3D models (Poly Haven - CC0)
```

#### 9. Laptop Matrix (Research Node)
- **Role:** Research & heavy compute node
- **Scan Status:** Completed (laptop_filesystem_scanner.py)
- **Integration:** `laptop_push_workflow.yml`, `laptop_master_merge_ingestion.yml`

---

## 🆓 FREE CLOUD PLATFORMS (AETHER HARVEST)

**Discovered in AETHER_HARVEST_COMPLETE.md:**

### **Compute Platforms**
1. **Replit** - Free tier for dev environments
2. **Glitch** - Free hosting for Node.js apps
3. **Railway** - $5/month free credit
4. **Render** - Free tier for web services
5. **Fly.io** - Free tier compute
6. **Deta** - Free cloud platform
7. **Vercel** - Free for personal projects
8. **Netlify** - Free tier hosting
9. **Cloudflare Pages** - Free static hosting
10. **GitHub Pages** - Free static sites

### **AI/ML Platforms**
11. **Google Colab** - Free GPU/TPU notebooks
12. **Kaggle Kernels** - Free GPU notebooks
13. **Paperspace Gradient** - Free tier GPU
14. **SageMaker Studio Lab** - Free ML environment

### **Database Platforms**
15. **MongoDB Atlas** - Free tier (512MB)
16. **PostgreSQL** (Supabase, Neon) - Free tiers
17. **Redis Cloud** - Free tier
18. **Firebase** - Free tier (Spark plan)

### **Storage Platforms**
19. **Cloudinary** - Free image/video storage
20. **Backblaze B2** - Free 10GB storage

---

## 🔧 DEVELOPMENT PLATFORMS

### **Package Registries**
- **PyPI** - Python packages
- **npm** - JavaScript packages
- **Docker Hub** - Container images

### **CI/CD Platforms**
- **GitHub Actions** - Free for public repos (✅ ACTIVE - 25 workflows)
- **GitLab CI** - Free tier
- **CircleCI** - Free tier

---

## 📊 MONITORING & ANALYTICS

### **Application Monitoring**
- **Sentry** - Free tier error tracking
- **LogRocket** - Free tier session replay
- **Datadog** - Free tier monitoring

### **Analytics**
- **Google Analytics** - Free
- **Plausible** (self-hosted) - Free

---

## 🔐 SECURITY & SECRETS

### **Secret Management**
- **GitHub Secrets** - Repository secrets (✅ ACTIVE)
  - `RCLONE_CONFIG_DATA` (GDrive access)
  - `HF_TOKEN` (HuggingFace auth)
- **Environment Variables** - HuggingFace Spaces
- **Doppler** - Free tier secret management (potential)

---

## 🌉 PLATFORM BRIDGES & CONNECTORS

### **Active Connectors (services/)**
```python
gdrive_connector.py          # Google Drive integration
tia_connector.py             # TIA-ARCHITECT-CORE bridge
dataset_connector.py         # HuggingFace Datasets
hf_bucket_connector.py       # HF storage buckets
repo_mapper.py               # GitHub repository mapping
neuron_processor.py          # AI model integration
district_librarian.py        # District artifact management
```

### **Sync Scripts**
```bash
global_sync.sh               # Multi-repo GitHub sync
sync_to_hf.yml              # GitHub → HuggingFace
gdrive_partition_harvester   # GDrive → GitHub metadata
s10_push_to_vault            # S10 → GDrive → GitHub
laptop_push_workflow         # Laptop → GitHub
```

---

## 📡 COMMUNICATION PLATFORMS

### **Collaboration**
- **GitHub Issues** - Task tracking
- **GitHub Discussions** - Community
- **GitHub Projects** - Project management

### **Notifications**
- **GitHub Actions Notifications** - Workflow status
- **Email** - Critical alerts

---

## 🎮 EXPERIMENTAL PLATFORMS

### **Blockchain/Web3** (S10 VAMGUARD Arsenal)
- **Ethereum** - Smart contracts
- **Polygon** - Layer 2 scaling
- **Hardhat** - Development framework
- **Truffle** - Development suite
- **Ganache** - Local blockchain
- **Infura** - Ethereum API
- **Alchemy** - Web3 infrastructure

### **Multimedia** (S10 Resources)
- **LibVLCSharp** - Media playback
- **FFmpeg** - Video processing
- **Blender** - 3D modeling/rendering
- **Kdenlive** - Video editing
- **Coqui TTS** - Text-to-speech
- **Kenney.nl** - Game assets (40K+ CC0)
- **OpenGameArt** - Free game graphics
- **Freesound** - Audio library (720K+ sounds)
- **Poly Haven** - 3D models (CC0)

---

## 🚦 PLATFORM STATUS MATRIX

| Platform | Status | Connectivity | Cost | Priority |
|----------|--------|--------------|------|----------|
| HuggingFace Spaces | ✅ OPERATIONAL | Connected | Free+Paid | CRITICAL |
| HuggingFace Datasets | ✅ OPERATIONAL | Connected | Free+Paid | HIGH |
| GitHub | ✅ OPERATIONAL | Connected | Free | CRITICAL |
| Google Drive | ⚠️ PARTIAL | Network Issues | Paid | HIGH |
| Google Sheets | ❌ ERROR | Missing gspread | Free | MEDIUM |
| Ubuntu Core | ✅ OPERATIONAL | Local | N/A | CRITICAL |
| Oppo Termux | ✅ OPERATIONAL | Local | N/A | MEDIUM |
| S10 Uplink | ✅ COMPLETE | Synced | N/A | MEDIUM |
| Laptop Matrix | ✅ OPERATIONAL | Local | N/A | MEDIUM |

---

## 🔄 SYNC TOPOLOGY

```
┌──────────────┐
│  S10 Node    │ ────┐
│  (Mackay)    │     │
└──────────────┘     │
                     ├──→ GDrive (GENESIS_VAULT 321GB)
┌──────────────┐     │
│ Oppo Termux  │ ────┤
│ (Mobile)     │     │
└──────────────┘     │
                     └──→ GitHub (DJ-Goana-Coding/*)
┌──────────────┐              ↓
│ Laptop Node  │ ─────────────┤
└──────────────┘              │
                              ├──→ master_inventory.json
┌──────────────┐              │     master_intelligence_map.txt
│ Ubuntu Core  │ ─────────────┤
└──────────────┘              │
                              └──→ HuggingFace Spaces (DJ-Goanna-Coding/*)
                                   ↓
                              TIA RAG + Streamlit UI
```

---

## 🎯 PLATFORM EXPANSION ROADMAP

### **Phase 1: Stabilization (Current)**
- ✅ Fix GDrive connectivity (rclone + Section 142)
- ✅ Install gspread for Google Sheets
- ✅ Complete first District harvest
- ✅ Stabilize HF Space syncs

### **Phase 2: Expansion (Next)**
- 🔲 Add MongoDB Atlas for structured data
- 🔲 Add Redis for caching/queues
- 🔲 Add Sentry for error tracking
- 🔲 Add Cloudinary for media assets

### **Phase 3: Advanced (Future)**
- 🔲 Web3 integration (Infura/Alchemy)
- 🔲 Advanced analytics (custom dashboards)
- 🔲 Multi-region redundancy
- 🔲 Edge compute nodes

---

## 📋 PLATFORM CREDENTIALS & ACCESS

**Stored in GitHub Secrets:**
```
RCLONE_CONFIG_DATA    # Google Drive access
HF_TOKEN              # HuggingFace authentication
GITHUB_TOKEN          # GitHub API access (auto)
```

**Stored in HuggingFace Space Secrets:**
```
HF_TOKEN              # Internal authentication
GITHUB_TOKEN          # For pulling from GitHub
```

**Environment Variables:**
- Managed per-platform
- Never committed to repos
- Injected via CI/CD or runtime

---

## 🛡️ PLATFORM SECURITY GUARDRAILS

1. **Never expose credentials in code**
2. **Use environment variables only**
3. **Rotate tokens quarterly**
4. **Monitor for unauthorized access**
5. **Enforce HTTPS/SSL everywhere**
6. **Use least-privilege access**
7. **Regular security audits**

---

## 📞 PLATFORM SUPPORT CONTACTS

- **HuggingFace:** support@huggingface.co
- **GitHub:** support@github.com
- **Google Drive:** Google Workspace support

---

## 📚 RELATED DOCUMENTATION

- `PROGRAMS.md` - Registry of all scripts, workflows, services
- `GRANTS.md` - Funding tracking framework
- `DEPLOYMENT_GUIDE.md` - Deployment procedures
- `FULL_AUTOMATION_GUIDE.md` - Automation reference

---

**Document Authority:** Citadel Architect v25.0.OMNI  
**Maintenance:** Auto-updated by platform discovery workflows  
**Last Audit:** 2026-04-03
