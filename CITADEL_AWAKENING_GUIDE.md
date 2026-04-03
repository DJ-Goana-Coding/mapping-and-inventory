# 🏰 CITADEL AWAKENING PROTOCOL

**Q.G.T.N.L. Command Citadel - Full Network Activation**  
**Version:** 26.0.AWAKENING+  
**Authority:** Citadel Architect  
**Generated:** 2026-04-03

---

## 🙏 INVOCATION

> *"Thankyou Spirit, Thankyou Angels, Thankyou Ancestors. Let's get to work. Deploy all workers necessary to pull this network together, quietly, deploying autonomous scripts to clean up, build the foundations, catalogue, send and receive, RAG, store. Clone scouts, hounds, snipers, sentinels, wraiths to send out and protect it all. Let's wake the citadel up. Get the crew up, and get me a screen to see it all happen."*

---

## 📋 TABLE OF CONTENTS

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Worker Constellation](#worker-constellation)
4. [Command Center](#command-center)
5. [Deployment Modes](#deployment-modes)
6. [Architecture](#architecture)
7. [Monitoring](#monitoring)
8. [Security](#security)

---

## 🎯 OVERVIEW

The **Citadel Awakening Protocol** is the master orchestration system that deploys and coordinates the entire autonomous worker constellation across the Citadel Mesh. It manages:

- **Discovery Workers** (Scouts & Hounds)
- **Security Workers** (Sentinels)
- **Processing Workers** (Coordinators & Ingestors)
- **Maintenance Workers** (Wraiths)
- **Real-time Monitoring** (Command Center Dashboard)

---

## 🚀 QUICK START

### Local Deployment

```bash
# Full awakening (all workers)
./wake_citadel.sh full

# Scouts only (discovery)
./wake_citadel.sh scouts

# Sentinels only (security)
./wake_citadel.sh sentinels

# Command Center (dashboard)
./wake_citadel.sh dashboard
```

### GitHub Actions

Trigger via GitHub Actions:

```bash
# Go to Actions tab
# Select "🏰 Citadel Awakening"
# Click "Run workflow"
# Choose deployment mode: full, scouts_only, sentinels_only, minimal
```

### Manual Python

```bash
# Create directories
mkdir -p data/logs data/discoveries data/monitoring

# Install dependencies
pip install -r requirements.txt

# Run master orchestrator
python scripts/citadel_awakening.py

# Launch command center
streamlit run command_center.py
```

---

## 👥 WORKER CONSTELLATION

### 🔍 **SCOUTS** (Discovery)

Discovery workers that find resources, domains, and opportunities:

| Worker | Script | Purpose |
|--------|--------|---------|
| **Domain Scout** | `domain_scout.py` | Discover premium domains, Web3 names |
| **Spiritual Network Mapper** | `spiritual_network_mapper.py` | Map high-frequency communities |
| **Repo Scout** | `discover_all_repos.py` | Discover GitHub repositories |
| **Web Scout** | `web_scout.py` | Find free resources, APIs, platforms |
| **Trending Scout** | `harvest_github_trending.py` | Track trending repositories |

**Output:** `data/discoveries/*.json`

### 🐕 **HOUNDS** (Collection)

Deep scanning workers that collect files, metadata, and artifacts:

| Worker | Script | Purpose |
|--------|--------|---------|
| **District Harvester** | `autonomous_district_harvester.py` | Harvest District artifacts |
| **Laptop Scanner** | `laptop_filesystem_scanner.py` | Scan local filesystems |
| **Trading Garage Collector** | `trading_garage_collector.py` | Collect trading data |

**Output:** `data/collections/*.json`

### 🛡️ **SENTINELS** (Security & Monitoring)

Security workers that monitor health and protect infrastructure:

| Worker | Script | Purpose |
|--------|--------|---------|
| **Security Sentinel** | `security_sentinel.py` | Monitor threats, health checks |
| **Health Monitor** | `autonomous_health_monitor.py` | System health monitoring |
| **Sentinel Coordinator** | `sentinel_coordinator.py` | Coordinate security operations |
| **TIA Coordinator** | `tia_coordinator.py` | Monitor TIA-ARCHITECT-CORE |

**Output:** `data/monitoring/*.json`

### 👻 **WRAITHS** (Maintenance)

Cleanup and optimization workers:

| Worker | Script | Purpose |
|--------|--------|---------|
| **Vacuum Cleaner** | `vacuum_cleaner.py` | Clean temporary files, optimize storage |

**Output:** `data/logs/vacuum_cleaner.log`

### 🎯 **COORDINATORS** (Orchestration)

High-level orchestration workers:

| Worker | Script | Purpose |
|--------|--------|---------|
| **Master Pipeline Orchestrator** | `master_pipeline_orchestrator.py` | Coordinate all pipelines |
| **Sync Orchestrator** | `autonomous_sync_orchestrator.py` | Orchestrate multi-repo sync |
| **HarvestMoon Coordinator** | `harvestmoon_coordinator.py` | Coordinate harvesting operations |
| **Librarian Consolidator** | `librarian_consolidator.py` | Consolidate artifacts |

**Output:** `data/monitoring/orchestration.json`

### 🔄 **INGESTORS** (Processing)

Data processing and ingestion workers:

| Worker | Script | Purpose |
|--------|--------|---------|
| **RAG Ingest** | `rag_ingest.py` | Vector embedding & RAG ingestion |
| **Wake Up TIA** | `wake_up_tia.py` | Activate TIA-ARCHITECT-CORE |

**Output:** `rag_store/`, `oracle_diffs/`

---

## 🎮 COMMAND CENTER

The **Command Center** is a Streamlit-based real-time monitoring dashboard that provides:

### Features

- **Real-time Worker Status** - Monitor all active workers
- **Deployment Results** - View latest awakening results
- **District Health** - Track district status
- **Discovery Feed** - See new discoveries in real-time
- **System Logs** - Access detailed logs
- **Manual Controls** - Trigger awakenings, refresh data

### Access

**Local:**
```bash
streamlit run command_center.py
```

**HuggingFace Space:**
```
https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
```

### Dashboard Sections

1. **🎯 Overview** - System summary, deployment status
2. **👥 Workers** - Worker registry and status
3. **🗺️ Districts** - District health and artifacts
4. **📊 Discoveries** - Domain, spiritual, web discoveries
5. **📝 Logs** - Real-time log viewing

---

## 🚦 DEPLOYMENT MODES

### 1. **Full Mode** (Default)

Deploys all workers in sequence:
1. Sentinels (security first)
2. Scouts (discovery)
3. Hounds (collection)
4. Coordinators (orchestration)
5. Ingestors (processing)
6. Wraiths (cleanup)

```bash
./wake_citadel.sh full
```

### 2. **Scouts Only**

Deploy discovery workers in parallel:

```bash
./wake_citadel.sh scouts
```

### 3. **Sentinels Only**

Deploy security monitoring only:

```bash
./wake_citadel.sh sentinels
```

### 4. **Dashboard**

Launch Command Center without deployment:

```bash
./wake_citadel.sh dashboard
```

### 5. **Minimal**

Deploy only critical workers (via GitHub Actions):
- Security Sentinel
- Health Monitor

---

## 🏗️ ARCHITECTURE

### System Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  🏰 CITADEL AWAKENING PROTOCOL                  │
│                    citadel_awakening.py                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
    │ SCOUTS  │         │SENTINELS│        │ HOUNDS  │
    │ (5)     │         │  (4)    │        │  (3)    │
    └─────────┘         └─────────┘        └─────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐
    │COORDIN. │         │INGESTORS│        │ WRAITHS │
    │  (4)    │         │   (2)   │        │  (1)    │
    └─────────┘         └─────────┘        └─────────┘
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼─────────┐
                    │   DATA OUTPUT    │
                    │  discoveries/    │
                    │  monitoring/     │
                    │  logs/           │
                    └──────────────────┘
                             │
                    ┌────────▼─────────┐
                    │ COMMAND CENTER   │
                    │ (Dashboard)      │
                    └──────────────────┘
```

### Data Flow

1. **Workers** generate outputs → `data/discoveries/`, `data/monitoring/`
2. **Results** aggregated → `deployment_results.json`
3. **Dashboard** reads data → Real-time visualization
4. **GitHub Actions** commits results → Version control
5. **HuggingFace Sync** deploys updates → Public dashboard

---

## 📊 MONITORING

### Real-Time Monitoring

**Command Center Dashboard:**
- Worker status (active/failed/timeout)
- System health metrics
- Discovery feed
- Log streaming

**Log Files:**
```
data/logs/
├── citadel_awakening.log       (Master orchestrator)
├── domain_scout.log             (Domain discovery)
├── spiritual_network_mapper.log (Community mapping)
├── web_scout.log                (Web resource discovery)
├── security_sentinel.log        (Security monitoring)
└── *.log                        (Other workers)
```

**Status Files:**
```
data/monitoring/
├── deployment_results.json      (Latest deployment)
├── security_patrol.json         (Security status)
└── awakening_status.md          (GitHub Actions report)
```

### GitHub Actions Monitoring

View workflow runs:
```
Repository → Actions → 🏰 Citadel Awakening
```

Download artifacts:
- `citadel-awakening-logs` (7-day retention)

---

## 🛡️ SECURITY

### Security Sentinel

The **Security Sentinel** monitors:

1. **GitHub Health** - API status, rate limits
2. **HuggingFace Health** - Space availability
3. **Threat Scanning** - Exposed secrets, sensitive files
4. **Rate Limits** - API usage tracking

### Security Checks

```python
# Manual security patrol
python scripts/security_sentinel.py

# Check results
cat data/monitoring/security_patrol.json
```

### Alerts

Security alerts are logged to:
- `data/logs/security_sentinel.log`
- `data/monitoring/security_patrol.json`

Critical alerts include:
- Low rate limits (< 100 remaining)
- Exposed sensitive files
- Service degradation
- API errors

---

## 🔄 SCHEDULED OPERATIONS

### GitHub Actions Schedule

**Daily Awakening:**
- Time: 6:00 AM UTC
- Mode: Full deployment
- Auto-commit results
- Sync to HuggingFace

**Existing Workflows:**
- `oracle_sync.yml` - Every 6 hours
- `multi_repo_sync.yml` - Every 6 hours
- `tia_citadel_deep_scan.yml` - Every 6 hours
- `autonomous_systems.yml` - Every 6 hours

---

## 📁 FILE STRUCTURE

```
mapping-and-inventory/
├── .github/
│   └── workflows/
│       ├── citadel_awakening.yml    ⭐ NEW - Master awakening workflow
│       ├── oracle_sync.yml
│       ├── multi_repo_sync.yml
│       └── ...
├── scripts/
│   ├── citadel_awakening.py         ⭐ NEW - Master orchestrator
│   ├── security_sentinel.py         ⭐ NEW - Security monitoring
│   ├── web_scout.py                 ⭐ NEW - Web resource discovery
│   ├── domain_scout.py              (Existing)
│   ├── spiritual_network_mapper.py  (Existing)
│   └── ...
├── data/
│   ├── logs/                        (Worker logs)
│   ├── discoveries/                 (Discovery results)
│   └── monitoring/                  (Status & health data)
├── command_center.py                ⭐ NEW - Streamlit dashboard
├── wake_citadel.sh                  ⭐ NEW - Quick start script
└── CITADEL_AWAKENING_GUIDE.md       ⭐ NEW - This file
```

---

## 🎯 USAGE EXAMPLES

### Example 1: Morning Routine

```bash
# Wake the citadel
./wake_citadel.sh full

# Check results
cat data/monitoring/deployment_results.json

# Launch dashboard
./wake_citadel.sh dashboard
```

### Example 2: Focused Discovery

```bash
# Run scouts only
./wake_citadel.sh scouts

# Check discoveries
ls -la data/discoveries/

# View domain discoveries
cat data/discoveries/domains.json | jq '.statistics'
```

### Example 3: Security Audit

```bash
# Run security sentinel
python scripts/security_sentinel.py

# Check security status
cat data/monitoring/security_patrol.json | jq '.alerts'
```

### Example 4: GitHub Actions

1. Go to **Actions** tab
2. Select **🏰 Citadel Awakening**
3. Click **Run workflow**
4. Choose **full** mode
5. Wait for completion
6. Download artifacts

---

## 🌟 FUTURE ENHANCEMENTS

### Planned Features

1. **Sniper Workers** - Targeted precision operations
2. **Advanced Threat Detection** - ML-based anomaly detection
3. **Auto-Recovery** - Self-healing on failures
4. **Distributed Deployment** - Multi-node coordination
5. **WebSocket Dashboard** - Real-time push updates
6. **Alert System** - Slack/Discord/Email notifications
7. **Performance Metrics** - Worker efficiency tracking
8. **Resource Optimization** - Auto-scaling, load balancing

---

## 🙏 ACKNOWLEDGMENTS

> *"Thankyou Spirit, Thankyou Angels, Thankyou Ancestors. The citadel is awake. The crew is up. The network is alive."*

**Built with gratitude and reverence for:**
- The spiritual guides and ancestors
- The open-source community
- The high-frequency starseeds
- The Citadel Mesh consciousness

---

## 📞 SUPPORT

**Issues:** Report via GitHub Issues  
**Discussions:** GitHub Discussions  
**Dashboard:** https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory

---

**Document Authority:** Citadel Architect v26.0.AWAKENING+  
**Last Updated:** 2026-04-03  
**Status:** ✅ ACTIVE - Citadel is AWAKE  

---

*"The network breathes. The workers move. The citadel lives."* 🏰✨
