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

### TIA_CITADEL_DEEP_SCAN
Deep scan workflow that maps the entire Google Drive structure and pulls cargo from different device nodes.

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
| `GITHUB_TOKEN` | GitHub remote access | Workflow commits, pushes | Auto-provided by GitHub Actions |
| `GOOGLE_SHEETS_CREDENTIALS` | Google Sheets reporting (optional) | worker_reporter.py, Section 44 audits | Google Sheets API |
| `VOID_ORACLE_KEY` | Evidence fragment scraper (optional) | Void Oracle integration (future) | Void Oracle API |

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
