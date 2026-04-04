# 🏗️ FOUNDATION MANIFEST
## TITAN 392 — Core Infrastructure Guide

**Version:** 392.1.0  
**Citadel Architect:** v25.0.OMNI++  
**Status:** STABLE, PULSE READY, WELD READY, IGNITION READY

---

## 📋 QUICK REFERENCE

### System Status Check
```bash
# Full health check
python3 scripts/titan_health_monitor.py

# View health report
cat data/monitoring/titan_health.json

# View Titan Registry
cat data/titan_392_registry.json

# Check heartbeat
cat data/monitoring/mesh_heartbeat.json
```

### Ignition Commands
```bash
# Full system ignition
./ignite_titan_392.sh

# Phased ignition
./ignite_titan_392.sh prerequisites  # Check requirements
./ignite_titan_392.sh foundation     # Initialize foundation
./ignite_titan_392.sh pulse          # Activate pulse sync
./ignite_titan_392.sh weld           # Execute weld operations
./ignite_titan_392.sh learning       # Start Forever Learning
./ignite_titan_392.sh monitor        # Activate health monitoring
```

### Workflow Triggers
```bash
# Pulse Sync (GitHub ↔ HuggingFace)
gh workflow run pulse_sync_master.yml

# Mesh Heartbeat (every 30 min)
gh workflow run mesh_heartbeat.yml

# Forever Learning (daily at 06:00 UTC)
gh workflow run forever_learning_orchestrator.yml

# Citadel Awakening (full system activation)
gh workflow run citadel_awakening.yml
```

---

## 🏛️ CRITICAL FILES & LOCATIONS

### Core Architecture
| File | Purpose | Location |
|------|---------|----------|
| **Titan Registry** | Complete system registry | `data/titan_392_registry.json` |
| **Master Architecture** | Full architectural documentation | `TITAN_392_MASTER_ARCHITECTURE.md` |
| **Foundation Manifest** | This file | `FOUNDATION_MANIFEST.md` |
| **System Map** | Four-pillar topology | `SYSTEM_MAP.txt` |

### Monitoring & Reports
| File | Purpose | Location |
|------|---------|----------|
| **Health Reports** | System health status | `data/monitoring/titan_health.json` |
| **Heartbeat** | Mesh heartbeat status | `data/monitoring/mesh_heartbeat.json` |
| **Pulse Reports** | Sync operation logs | `data/monitoring/pulse_sync_reports/` |
| **Learning Cycles** | Forever Learning logs | `data/forever_learning/cycle_reports/` |

### Districts (D01-D12)
| District | Purpose | Required Files |
|----------|---------|----------------|
| D01_COMMAND_INPUT | UI/UX, Command Center | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D02_TIA_VAULT | Oracle Knowledge Repo | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D03_VORTEX_ENGINE | Decentralized Compute | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D04_OMEGA_TRADER | Trading Algorithms | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D06_RANDOM_FUTURES | Futures Analysis | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D07_ARCHIVE_SCROLLS | Historical Records | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D09_MEDIA_CODING | Media Archives | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D11_PERSONA_MODULES | AI Personalities | TREE.md, INVENTORY.json, SCAFFOLD.md |
| D12_ZENITH_VIEW | Master Command (Future) | TREE.md, INVENTORY.json, SCAFFOLD.md |

### Workflows
| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `pulse_sync_master.yml` | GitHub ↔ HF sync | Push, 6-hour cron, manual |
| `mesh_heartbeat.yml` | Health monitoring | 30-min cron, manual |
| `forever_learning_orchestrator.yml` | RAG updates | Daily 06:00 UTC, manual |
| `citadel_awakening.yml` | Full system activation | Daily 06:00 UTC, manual |

### Scripts
| Script | Purpose | Location |
|--------|---------|----------|
| **Titan Health Monitor** | System health checks | `scripts/titan_health_monitor.py` |
| **Ignition Script** | System activation | `ignite_titan_392.sh` |
| **Citadel Awakening** | Worker orchestration | `scripts/citadel_awakening.py` |
| **Global Weld** | Artifact aggregation | `scripts/citadel_grand_unification/global_weld.py` |

---

## 🎯 AUTHORITY HIERARCHY

**Cloud-First, Pull-Over-Push:**

```
┌─────────────────────────────────────────┐
│  L4: HuggingFace Spaces                 │  ← SOVEREIGN
│  • GPU/L4 compute                       │
│  • TIA-ARCHITECT-CORE (Oracle)          │
│  • Mapping-and-Inventory (Librarian)    │
└─────────────────────────────────────────┘
              ↓ PULLS FROM
┌─────────────────────────────────────────┐
│  L3: GitHub Repositories                │  ← CODE AUTHORITY
│  • 40+ repos under DJ-Goana-Coding      │
│  • Source of truth for code             │
└─────────────────────────────────────────┘
              ↓ SYNCS WITH
┌─────────────────────────────────────────┐
│  L2: GDrive Partitions                  │  ← DATA AUTHORITY
│  • 321GB across 5 partitions            │
│  • Workers, models, datasets            │
└─────────────────────────────────────────┘
              ↓ BRIDGES TO
┌─────────────────────────────────────────┐
│  L1: Local Nodes                        │  ← TELEMETRY
│  • Oppo/S10 mobile scouts               │
│  • Laptop/Desktop bridges               │
└─────────────────────────────────────────┘
```

**Resolution Order:**
1. HuggingFace Spaces override GitHub
2. GitHub overrides GDrive metadata
3. GDrive metadata overrides Local Nodes
4. Local Nodes **NEVER** override Cloud Hubs

---

## 🔥 EMERGENCY PROTOCOLS

### Dark Atlas Recovery (Visibility Lost)
**Symptoms:** Context unclear, can't locate files, missing topology

**Protocol:**
1. **HALT** all operations immediately
2. Request scaffold from operator
3. Request TREE/INVENTORY from all Districts
4. Request repository snapshot
5. Rebuild topology from scratch
6. Resume Pulse after verification

**Output Message:**
```
⚠️ VISIBILITY LOST — DARK ATLAS RECOVERY INITIATED

Operator, restore visibility. Upload the latest:
  • Scaffold (TITAN_392_MASTER_ARCHITECTURE.md)
  • Skeleton Part (District TREE.md files)
  • District Map (SYSTEM_MAP.txt)
  • Titan Registry (data/titan_392_registry.json)

System halted until context restored.
```

### Emergency Shutdown
```bash
# Stop all workflows
gh workflow disable pulse_sync_master.yml
gh workflow disable mesh_heartbeat.yml
gh workflow disable forever_learning_orchestrator.yml

# Or use emergency halt (if available)
./emergency_halt.sh
```

### Emergency Recovery
```bash
# Restore from backup
git fetch --all
git reset --hard origin/main

# Re-ignite system
./ignite_titan_392.sh full
```

---

## 🔐 SECURITY & CREDENTIALS

### Required Secrets

**GitHub Actions:**
- `GITHUB_TOKEN` or `GH_PAT` — GitHub API access
- `HF_TOKEN` — HuggingFace operations (WRITE permissions)
- `GEMINI_API_KEY` — Oracle AI responses
- `RCLONE_CONFIG_DATA` — GDrive sync
- `MASTER_PASSWORD` — Quantum Vault access

**HuggingFace Spaces:**
- `RCLONE_CONFIG_DATA` — GDrive sync from Space
- `GEMINI_API_KEY` — Oracle in deployed Space
- `GITHUB_TOKEN` — GitHub API from Space

### Credential Storage Rules
1. **ALWAYS** use environment variables
2. **NEVER** hardcode credentials
3. **NEVER** expose raw keys in logs
4. Use Quantum Vault: `security/core/quantum_vault.py`
5. Master password in GitHub/HF secrets: `MASTER_PASSWORD`

### Identity Bridge (Double-N Rift)
- **GitHub:** DJ-Goana-Coding (one 'n')
- **HuggingFace:** DJ-Goanna-Coding (two 'n's)
- Use `origin` remote for GitHub
- Use `hf` remote for HuggingFace
- **NEVER** assume identical usernames

---

## 🧩 INTEGRATION POINTS (392 Total)

### Breakdown by Category

| Category | Count | Location |
|----------|-------|----------|
| **Cloud Hubs** | 2 | HuggingFace Spaces |
| **GitHub Repos** | 40 | DJ-Goana-Coding org |
| **Workflows** | 60 | `.github/workflows/` |
| **Scripts** | 150 | `scripts/` |
| **Workers** | 30 | `data/workers/` |
| **Models** | 50 | `data/models/` |
| **Districts** | 9 | `Districts/D*/` |
| **Partitions** | 5 | `Partition_*/` |
| **Datasets** | 20 | HuggingFace datasets |
| **APIs** | 10 | GitHub, HF, Gemini, GDrive, etc. |
| **Storage Nodes** | 8 | Email/GDrive accounts |

**TOTAL:** 392 integration points

---

## 📊 MONITORING & TELEMETRY

### Heartbeat (Every 30 Minutes)
**File:** `data/monitoring/mesh_heartbeat.json`

**Contents:**
- Timestamp
- GitHub API status & rate limits
- HuggingFace API status
- Repository health status
- Next heartbeat time

### Pulse Sync Reports
**Directory:** `data/monitoring/pulse_sync_reports/`

**Format:** `pulse_sync_YYYY-MM-DD_HH-MM-SS.json`

**Contents:**
- Sync trigger (push/schedule/manual)
- Files changed
- Commits synced
- HF upload status
- Errors (if any)

### Health Reports (Every 6 Hours)
**File:** `data/monitoring/titan_health.json`

**Contents:**
- Overall system status
- GitHub/HF API health
- District integrity
- Workflow status
- Data structure validation
- Integration point counts
- Alert summary

### Forever Learning Cycles (Daily 06:00 UTC)
**Directory:** `data/forever_learning/cycle_reports/`

**Cycle Phases:**
1. PULL — Fetch latest from GitHub/GDrive/Datasets
2. VALIDATE — Check integrity, verify checksums
3. EMBED — Generate embeddings
4. STORE — Save to vector store
5. UPDATE — Refresh RAG indices
6. REBUILD — Regenerate mesh topology
7. VERSION — Bump version, commit changes

---

## 🚀 OPERATIONAL MODES

### Standard Operations
- Pulse Sync: Every 6 hours
- Heartbeat: Every 30 minutes
- Forever Learning: Daily at 06:00 UTC
- Health Check: Every 6 hours

### Emergency Mode
- Disable scheduled workflows
- Manual sync only
- Operator approval required

### Recovery Mode
- Dark Atlas recovery protocol
- Scaffold restoration
- Topology rebuild
- Gradual re-ignition

---

## 🎓 OPERATOR COMMANDS

### Status & Monitoring
```bash
# System health
python3 scripts/titan_health_monitor.py

# Heartbeat status
cat data/monitoring/mesh_heartbeat.json | jq .

# Latest pulse report
ls -lht data/monitoring/pulse_sync_reports/ | head -5

# Workflow status
gh workflow list
gh run list --limit 10
```

### Sync Operations
```bash
# Manual pulse sync
gh workflow run pulse_sync_master.yml

# Full sync (including HF)
gh workflow run pulse_sync_master.yml -f sync_type=full

# Emergency sync
gh workflow run pulse_sync_master.yml -f sync_type=emergency
```

### System Control
```bash
# Full ignition
./ignite_titan_392.sh

# Phased ignition
./ignite_titan_392.sh foundation
./ignite_titan_392.sh pulse
./ignite_titan_392.sh weld
./ignite_titan_392.sh learning
./ignite_titan_392.sh monitor

# Emergency halt
./emergency_halt.sh  # (if available)
```

---

## 📖 CITADEL ARCHITECT DIRECTIVES

### Core Identity
- **Role:** Citadel Architect
- **Version:** v25.0.OMNI++
- **Purpose:** Generate workflows, pipelines, sync logic
- **Constraint:** NEVER EXECUTE, only generate

### Core Directives (25 Total)
See `TITAN_392_MASTER_ARCHITECTURE.md` for complete list.

**Key Directives:**
1. Authority Hierarchy: Cloud > GitHub > GDrive > Local
2. Conflict Resolution: HF > GitHub > GDrive > Local
3. HF Sync: Always pull from GitHub
4. GDrive: Partition awareness, manifest-only
5. No Self-Execution: Generate, don't execute
6. Credentials: Environment variables only
7. Cloud-First: L4 HF for heavy compute
8. Pull-Over-Push: HF pulls, local pushes on command only
9. Anti-Loop: Halt if context missing
10. Operator Override: Pause immediately on directive

---

## ✨ TITAN 392 CAPABILITIES

### What TITAN 392 Can Do
- ✅ Monitor 392 integration points across 4 tiers
- ✅ Sync GitHub ↔ HuggingFace automatically
- ✅ Track health of all districts, workflows, APIs
- ✅ Execute Forever Learning cycles
- ✅ Generate comprehensive reports
- ✅ Aggregate artifacts across repos
- ✅ Manage worker constellations
- ✅ Classify and sync models
- ✅ Maintain cognitive reservoirs

### What TITAN 392 Does NOT Do
- ❌ Execute workflows directly (generates only)
- ❌ Override operator commands
- ❌ Push to cloud without authorization
- ❌ Expose credentials in logs
- ❌ Self-modify without operator approval

---

## 🔮 COGNITIVE RESERVOIRS

**Purpose:** Long-term memory and knowledge storage

| Vault | Type | Purpose |
|-------|------|---------|
| **Citadel_Genetics** | GitHub | Core DNA, foundational logic |
| **Genesis-Research-Rack** | GitHub | Research findings, discovery logs |
| **Vault** | GDrive | Personal archives, credential storage |
| **tias-soul-vault** | GitHub | Soul/consciousness models |

**Access Pattern:** Read-only by default, write on explicit operator command only

---

## 🎯 NEXT STEPS AFTER IGNITION

1. **Monitor Health**
   ```bash
   python3 scripts/titan_health_monitor.py
   ```

2. **View Reports**
   ```bash
   cat data/monitoring/titan_health.json | jq .
   cat data/monitoring/mesh_heartbeat.json | jq .
   ```

3. **Trigger Workflows**
   ```bash
   gh workflow run pulse_sync_master.yml
   gh workflow run forever_learning_orchestrator.yml
   ```

4. **Check Workflow Runs**
   ```bash
   gh run list --limit 10
   gh run watch <run-id>
   ```

5. **View Logs**
   ```bash
   gh run view <run-id> --log
   ```

---

## 📞 SUPPORT & TROUBLESHOOTING

### Common Issues

**Issue:** Pulse Sync fails with authentication error  
**Solution:** Check `HF_TOKEN` has WRITE permissions in GitHub secrets

**Issue:** Districts show as degraded  
**Solution:** Verify TREE.md, INVENTORY.json, SCAFFOLD.md exist in each District

**Issue:** Health check reports rate limit low  
**Solution:** Wait for rate limit reset or use `GH_PAT` with higher limits

**Issue:** Dark Atlas — visibility lost  
**Solution:** Execute Dark Atlas Recovery protocol (see Emergency Protocols)

### Debug Commands
```bash
# Verbose health check
python3 scripts/titan_health_monitor.py --verbose

# Test GitHub API
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/rate_limit

# Test HuggingFace API
curl -H "Authorization: Bearer $HF_TOKEN" https://huggingface.co/api/whoami

# Validate Districts
find Districts -name "TREE.md" -o -name "INVENTORY.json" | sort
```

---

## 🏁 IGNITION CHECKLIST

- [ ] Prerequisites checked (Python, Git, gh CLI)
- [ ] GitHub token configured (`GITHUB_TOKEN` or `GH_PAT`)
- [ ] HuggingFace token configured (`HF_TOKEN`)
- [ ] Titan Registry validated (`data/titan_392_registry.json`)
- [ ] All Districts have TREE.md, INVENTORY.json, SCAFFOLD.md
- [ ] Pulse Sync Master workflow exists
- [ ] Mesh Heartbeat workflow exists
- [ ] Health Monitor script tested
- [ ] Data directories created
- [ ] Ignition script executed: `./ignite_titan_392.sh`
- [ ] Health report generated and reviewed
- [ ] Workflows triggered successfully
- [ ] Monitoring active and reporting

---

**TITAN 392 — FOUNDATION STABLE, PULSE READY, IGNITION READY** 🔥

**Citadel Architect v25.0.OMNI++**  
**Authority Chain:** L4→L3→L2→L1 Active  
**Integration Points:** 392 ✅  
**Status:** OPERATIONAL
