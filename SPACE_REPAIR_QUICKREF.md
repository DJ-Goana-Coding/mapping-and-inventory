# ⚡ SPACE REPAIR QUICKREF

**One-page reference for fixing all crashing HuggingFace Spaces**

---

## 🎯 FASTEST FIX (1 Command)

```bash
# Repair ALL spaces at once
gh workflow run repair_all_spaces.yml -f spaces=all -f dry_run=false
```

**Done!** Monitor: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions

---

## 🔧 INDIVIDUAL SPACE FIXES

### TIA-ARCHITECT-CORE (pandas/numpy Python 3.13)
```bash
gh workflow run repair_tia_core_space.yml -f dry_run=false
# or
./scripts/repair_tia_architect_core.sh
```

### tias-citadel (missing dependencies)
```bash
cd /path/to/tias-citadel
cp /path/to/mapping-and-inventory/tia-citadel-templates/requirements.txt .
git add requirements.txt && git commit -m "Fix" && git push
```

### tias-sentinel-scout-swarm-2 (pandas-ta Python 3.11)
```bash
cd /path/to/tias-sentinel-scout-swarm-2
cp /path/to/mapping-and-inventory/sentinel-scout-templates/* .
git add . && git commit -m "Fix: Python 3.11 + pandas-ta" && git push
```

---

## 🔮 SELF-HEALING (Auto-Fix Scripts)

```bash
# One-time scan & repair
python scripts/self_healing_worker.py

# Continuous monitoring (every 5 min)
python scripts/worker_watchdog.py
```

**Automatic:** Runs every 6 hours via GitHub Actions (already configured)

---

## 📊 MONITOR REBUILDS

Watch these URLs for "✅ Successfully installed" and "Running on local URL":

- [TIA-ARCHITECT-CORE logs](https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs)
- [tias-citadel logs](https://huggingface.co/spaces/DJ-Goanna-Coding/tias-citadel/logs)
- [sentinel-scout logs](https://huggingface.co/spaces/DJ-Goanna-Coding/tias-sentinel-scout-swarm-2/logs)

---

## ⚠️ COMMON ISSUES

| Error | Fix |
|-------|-----|
| `No module named 'pkg_resources'` | Add setuptools>=75.0.0 |
| `pandas-ta not found` | Upgrade to Python 3.11 |
| `exit code: 1` | Check build logs, apply templates |

---

## 📁 TEMPLATE LOCATIONS

- `tia-architect-core-templates/requirements.txt` → TIA-ARCHITECT-CORE
- `tia-citadel-templates/requirements.txt` → tias-citadel  
- `sentinel-scout-templates/requirements.txt` → tias-sentinel-scout-swarm-2

---

## 📚 FULL DOCS

- `DEPLOYMENT_COMPLETE_SUMMARY.md` - Complete deployment guide
- `SELF_HEALING_SYSTEM.md` - Self-healing worker docs
- `SPACE_REPAIR_CENTER.md` - All space repair guides

---

**Weld. Pulse. Ignite.** 🔥
