---
title: Mapping & Inventory
emoji: 🏰
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
datasets:
  - DJ-Goana-Coding/master-inventory
---

# CITADEL OMEGA — Mapping & Inventory Librarian

Central mapping and inventory dashboard for the Q.G.T.N.L. Citadel Omega system.

Connects ARK repos, GDrive, T.I.A., datasets, and all device nodes.

## Tabs
- 🗺️ **System Map** — Interactive connection graph of all repos, spaces, and nodes
- 📚 **Librarian** — Searchable master inventory ledger
- 📦 **Datasets** — Connected datasets with live status (local / GDrive / HuggingFace)
- 🧠 **T.I.A. Oracle** — Gemini-powered AI chat with system context
- ☁️ **Cloud Sync** — rclone-based GDrive sync controls

## Workflows

### 🌉 Global Repository Bridge (NEW)

**Automatic Discovery & Bridging of All Repositories:**

```bash
# Discover all DJ-Goana-Coding repositories
python scripts/discover_all_repos.py

# View registry
cat repo_bridge_registry.json | jq .

# Trigger bridge workflow
gh workflow run global_repo_bridge.yml
```

**Bridge System Features:**
- ✅ **Auto-Discovery** - Finds all DJ-Goana-Coding repos via GitHub API
- ✅ **Connection Mapping** - Maps repo relationships and dependencies
- ✅ **Dual-Sync** - Syncs to GitHub + HuggingFace Space
- ✅ **Privacy Support** - Handles private repositories with authentication
- ✅ **Statistics** - Generates comprehensive repo analytics

**See [REPO_BRIDGE_GUIDE.md](REPO_BRIDGE_GUIDE.md) for complete bridge documentation.**

---

### 🤖 Full Automation System

**⚡ Quick Start - Complete Automation:**

```bash
# Interactive automation menu (recommended)
./automate_all.sh

# Or trigger automated workflows
gh workflow run auto_sync_and_run.yml
```

**New Automation Features:**
- ✅ **Scheduled Operations** - Daily auto-sync and workflow runs
- ✅ **Auto-Merge PRs** - Safely merge approved PRs to main
- ✅ **Multi-Repo Sync** - Coordinate across all CITADEL repos
- ✅ **Global Weld** - One-shot sync of all DJ-Goana-Coding repos with artifact aggregation
- ✅ **Global Bridge** - Discover and link all repositories to central hub
- ✅ **Status Monitoring** - Real-time repository health checks

**See [FULL_AUTOMATION_GUIDE.md](FULL_AUTOMATION_GUIDE.md) for complete automation documentation.**

**🛡️ Global Weld - Multi-Repository Sync:**

```bash
# Sync all repos, aggregate artifacts, push to GitHub + HuggingFace
./global_sync.sh

# With credentials for private repos
export GITHUB_TOKEN="ghp_your_token"
export HF_TOKEN="hf_your_token"
./global_sync.sh
```

**See [GLOBAL_WELD_GUIDE.md](GLOBAL_WELD_GUIDE.md) for complete Global Weld documentation.**

**🚗 Trading Garages - Aggregated Bot Collections:**

```bash
# Collect all trading bots into organized garages
python scripts/trading_garage_collector.py

# View garage index
cat Trading_Garages/GARAGE_INDEX.json | jq .

# Explore a garage
ls Trading_Garages/Trading_Garage_Alpha/repos/
```

**Trading Garage Features:**
- ✅ **Auto-Classification** - Automatically categorizes trading repos
- ✅ **Triple Garage System** - Alpha (bots), Beta (analysis), Omega (connectors)
- ✅ **Dual Location** - Keeps originals + creates centralized copies
- ✅ **Manifest Generation** - Detailed metadata for each garage
- ✅ **Genesis Integration** - Works alongside Genesis garage concept

**See [Trading_Garages/TRADING_GARAGE_GUIDE.md](Trading_Garages/TRADING_GARAGE_GUIDE.md) for complete garage documentation.**

---

**📋 Manual Workflow Triggers:**

```bash
# Use the manual trigger script
./trigger_all_workflows.sh
```

Or trigger manually via GitHub Actions web interface:
1. Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. Click each workflow and select "Run workflow"

**See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for workflow-specific documentation.**

### Core Workflows

1. **Global Repository Bridge** - Discovers all repos, generates topology (every 12 hours)
2. **TIA_CITADEL_DEEP_SCAN** - Scans 321GB across 5 partitions, generates intelligence map
3. **S10_PUSH_TO_VAULT** - Syncs S10 device data to Google Drive vault
4. **Sync to HuggingFace Space** - Deploys dashboard to HuggingFace (auto-triggers on push to main)

### Automation Workflows

5. **Auto Sync and Run All Workflows** - Daily automated sync + workflow triggers (2 AM UTC)
6. **Multi-Repository Sync Orchestrator** - Every 6 hours, syncs all related repos
7. **Auto-Merge to Main** - Automatically merges approved PRs with safety checks
8. **TIA Core Health Monitor** - Every 30 minutes, checks TIA-ARCHITECT-CORE status

**Monitoring Live Runs:**
- Use `gh run watch <run-id>` to monitor in real-time
- See [WORKFLOW_MONITORING_GUIDE.md](WORKFLOW_MONITORING_GUIDE.md) for detailed instructions
- Use the helper script: `./watch_workflow.sh --compact` for easy monitoring

## System Architecture

### Four Pillar Framework
The CITADEL OMEGA system is organized into four foundational pillars:
- 🏛️ **TRADING** — Market operations, automation, strategies (D04, D06, Partition_04)
- 📜 **LORE** — Documentation, memory, knowledge preservation (D01, D02, D07, D11)
- 🧠 **MEMORY** — Data storage, archives, intelligence maps (D09, Research/, Archive_Vault)
- 🌐 **WEB3** — Blockchain, decentralized systems (D03, Partition_03)

See [SYSTEM_MAP.txt](SYSTEM_MAP.txt) for complete pillar categorization and sector mapping.

### Districts & Sectors (D01-D13)
Currently implemented:
- ✅ **D01_COMMAND_INPUT** — Command center & UI
- ✅ **D02_TIA_VAULT** — T.I.A. Oracle knowledge repository
- ✅ **D03_VORTEX_ENGINE** — Decentralized compute orchestration
- ✅ **D04_OMEGA_TRADER** — Core trading algorithms
- ✅ **D06_RANDOM_FUTURES** — Futures analysis & Monte Carlo simulations
- ✅ **D07_ARCHIVE_SCROLLS** — Historical records & documentation
- ✅ **D09_MEDIA_CODING** — Media archives & coding resources
- ✅ **D11_PERSONA_MODULES** — AI personality frameworks

Missing sectors (D05, D08, D10, D12, D13) are planned for future implementation.
**D12_ZENITH_VIEW** will serve as the master command center when established.

### T.I.A. Master Harvest System
The Librarian tab is powered by the T.I.A. Master Harvest system, which:
- Automatically consolidates evidence fragments from distributed sources
- Scans Research/ cargo bays (GDrive, Oppo, S10, Laptop)
- Generates MD5-verified inventory (master_inventory.json)
- Creates intelligence maps (master_intelligence_map.txt)

See [TIA_MASTER_HARVEST.txt](TIA_MASTER_HARVEST.txt) for complete harvest documentation.

### Symlink Protection
All GDrive sync operations use `--skip-links` to prevent:
- Circular symlink loops (D12 Zenith View issue)
- Android permission blocks
- Infinite recursion during deep scans

This is critical for the D12_ZENITH_VIEW command center when it's implemented.

## Secrets Required

### GitHub Actions Secrets
| Secret | Purpose | Required For | Permissions |
|--------|---------|--------------|-------------|
| `RCLONE_CONFIG_DATA` | Google Drive sync via rclone | tia_citadel_deep_scan.yml, Cloud Sync tab | Read/Write GDrive |
| `GEMINI_API_KEY` | T.I.A. Oracle AI responses | T.I.A. Oracle tab, AI analysis | Gemini API access |
| `HF_TOKEN` | HuggingFace operations | sync_to_hf.yml workflow | **Write permissions required** |
| `GITHUB_TOKEN` | GitHub remote access | Workflow commits, pushes, private repo access | Auto-provided by GitHub Actions |
| `GOOGLE_SHEETS_CREDENTIALS` | Google Sheets reporting (optional) | worker_reporter.py, Section 44 audits | Google Sheets API |
| `VOID_ORACLE_KEY` | Evidence fragment scraper (optional) | Void Oracle integration (future) | Void Oracle API |

**Note:** `GITHUB_TOKEN` is required for accessing private repositories in the bridge system.

### HuggingFace Space Secrets
These secrets must also be configured in your HuggingFace Space settings at:
`https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory/settings`

| Secret | Purpose |
|--------|---------|
| `RCLONE_CONFIG_DATA` | Enable GDrive sync from HF Space |
| `GEMINI_API_KEY` | Enable T.I.A. Oracle in deployed Space |
| `GITHUB_TOKEN` | Enable GitHub API calls from Space |

**Important Notes:**
- `HF_TOKEN` must have **Write** permissions to successfully push via `sync_to_hf.yml`
- `VOID_ORACLE_KEY` is only required if you're running the Evidence Fragment Scraper
- `GOOGLE_SHEETS_CREDENTIALS` is only needed for Google Sheets audit reporting
