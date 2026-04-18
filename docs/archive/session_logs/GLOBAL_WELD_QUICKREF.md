# 🛡️ GLOBAL WELD QUICK REFERENCE

**Citadel Architect v25.0.OMNI+ - One-Shot Multi-Repo Sync**

---

## 🚀 Quick Start

```bash
# Basic usage (public repos only)
./global_sync.sh

# With credentials (for private repos + HF push)
export GITHUB_TOKEN="ghp_xxxxx"
export HF_TOKEN="hf_xxxxx"
./global_sync.sh

# Keep workspace for inspection
export KEEP_WORKSPACE=true
./global_sync.sh
```

---

## 📋 What It Does

1. ✅ Discovers all `DJ-Goana-Coding` repos (9+ repositories)
2. ✅ Clones/pulls each repo to `/tmp/citadel_sync_workspace`
3. ✅ Extracts `TREE.md`, `INVENTORY.json`, `SCAFFOLD.md` from all Districts
4. ✅ Aggregates into `master_inventory.json` and `master_intelligence_map.txt`
5. ✅ Commits consolidated artifacts to this repo
6. ✅ Pushes to GitHub (`origin/main`)
7. ✅ Pushes to HuggingFace Space (`DJ-Goanna-Coding/Mapping-and-Inventory`)

---

## 🔑 Required Secrets

| Variable | Purpose | Required? |
|----------|---------|-----------|
| `GITHUB_TOKEN` | Private repo access + API | Optional (recommended) |
| `HF_TOKEN` | HuggingFace Space sync | Optional (required for HF push) |

---

## 📊 Output Files

- `master_inventory.json` - Unified file inventory across all repos
- `master_intelligence_map.txt` - Consolidated TREE.md from all Districts
- `sync_reports/sync_report_YYYYMMDD_HHMMSS.txt` - Execution report

---

## 🏗️ Canonical Repositories

1. **mapping-and-inventory** - Central librarian
2. **ARK_CORE** - Core Districts
3. **TIA-ARCHITECT-CORE** - Oracle reasoning
4. **tias-citadel** - Citadel interface
5. **tias-sentinel-scout-swarm-2** - Trading scout
6. **goanna_coding** - Private reasoning
7. **Vortex_Web3** - Web3 operations
8. **Genesis-Research-Rack** - Research datasets
9. **Citadel_Genetics** - Genetic algorithms

---

## 🐛 Troubleshooting

**Problem:** "Failed to clone repository"  
**Solution:** Set `GITHUB_TOKEN` for private repo access

**Problem:** "Failed to push to HuggingFace"  
**Solution:** Set `HF_TOKEN` with Write permission

**Problem:** "No changes to commit"  
**Solution:** Normal - no new artifacts found

---

## 📚 Full Documentation

See [GLOBAL_WELD_GUIDE.md](GLOBAL_WELD_GUIDE.md) for complete documentation.

---

**Weld. Pulse. Ignite.** 🦎
