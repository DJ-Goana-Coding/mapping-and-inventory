# 🔧 AUTONOMOUS REPAIR - QUICK REFERENCE

**One-page command reference for autonomous repository repair system**

---

## 🚀 QUICK START

```bash
# Full autonomous repair (recommended)
./autonomous_repair.sh full

# Scan repos only
./autonomous_repair.sh scan

# Repair without scanning
./autonomous_repair.sh repair

# Check system status
./autonomous_repair.sh status
```

---

## 📊 SYSTEM STATUS

```bash
# Recent scans
ls -lt data/monitoring/health_scan_*.json | head -5

# Recent repairs
ls -lt data/repairs/session_*.json | head -5

# Repair catalog
ls data/repairs/repair_catalog/

# Parts catalog
ls data/repairs/parts_catalog/
```

---

## 🔍 SCAN ONLY

```bash
# Manual scan
python3 scripts/broken_repo_scanner.py

# View latest scan
jq . $(ls -t data/monitoring/health_scan_*.json | head -1)

# Summary
jq '.summary' $(ls -t data/monitoring/health_scan_*.json | head -1)
```

---

## 🔧 REPAIR CYCLE

```bash
# Run repair orchestrator
python3 scripts/repo_repair_orchestrator.py

# View latest session
jq . $(ls -t data/repairs/session_*.json | head -1)

# View final report
cat $(ls -t data/repairs/final_report_*.txt | head -1)
```

---

## 📈 MONITORING

```bash
# Health scores
jq '.github_repos[] | {name: .repo_name, score: .health_score, status: .status}' \
  $(ls -t data/monitoring/health_scan_*.json | head -1)

# Critical issues
jq '.github_repos[] | select(.status == "critical")' \
  $(ls -t data/monitoring/health_scan_*.json | head -1)

# Repair success rate
jq '{
  total: .total_problems,
  fixed: .problems_fixed,
  rate: (.problems_fixed / .total_problems * 100)
}' $(ls -t data/repairs/session_*.json | head -1)
```

---

## 🤖 GITHUB ACTIONS

```bash
# Trigger workflow
gh workflow run "autonomous_repair.yml" --field mode=full

# View runs
gh run list --workflow=autonomous_repair.yml --limit 10

# Watch latest run
gh run watch $(gh run list --workflow=autonomous_repair.yml --limit 1 --json databaseId -q '.[0].databaseId')

# Download artifacts
gh run download $(gh run list --workflow=autonomous_repair.yml --limit 1 --json databaseId -q '.[0].databaseId')
```

---

## 🔐 ENVIRONMENT SETUP

```bash
# Required tokens
export GITHUB_TOKEN="ghp_..."
export HF_TOKEN="hf_..."

# Optional
export GH_PAT="ghp_..."  # For cross-repo pushes
```

---

## 📝 DOCUMENTATION

```bash
# Full guide
cat AUTONOMOUS_REPAIR_SYSTEM_GUIDE.md

# Component docs
cat scripts/repo_repair_orchestrator.py | head -20
cat scripts/broken_repo_scanner.py | head -20
```

---

## 🛠️ TROUBLESHOOTING

```bash
# Check logs
tail -100 $(ls -t data/repairs/repair_session_*.log | head -1)

# Check for errors
grep "ERROR" $(ls -t data/repairs/repair_session_*.log | head -1)

# Repair catalog for repo
cat data/repairs/repair_catalog/REPO_NAME_repair.md
```

---

## 📊 KEY METRICS

| Metric | Command |
|--------|---------|
| Repos scanned | `jq '.repos_scanned \| length' SESSION.json` |
| Broken repos | `jq '.repos_broken \| length' SESSION.json` |
| Repos repaired | `jq '.repos_repaired \| length' SESSION.json` |
| Problems fixed | `jq '.problems_fixed' SESSION.json` |
| Success rate | `jq '(.problems_fixed / .total_problems * 100)' SESSION.json` |

---

## 🎯 INTEGRATION POINTS

- **Omni-Audit:** Uses census builder, gap analyzer, solution generator
- **Citadel Awakening:** Runs as autonomous worker
- **Global Weld:** Updates master_inventory.json
- **Security Sentinel:** Monitors repo health
- **Command Center:** Displays repair status

---

## ⚡ PERFORMANCE

- **Scan:** 5-10 min for 50 repos
- **Repair:** 2-5 min per problem
- **Stress Test:** 3-8 min per repo
- **Total:** 30-60 min full cycle

---

## 🔄 AUTOMATED SCHEDULE

- **Daily at 03:00 UTC**
- After gap analysis completes
- Results auto-committed
- Issues created on failure

---

## 📞 HELP

- Full docs: `AUTONOMOUS_REPAIR_SYSTEM_GUIDE.md`
- Issues: Label `repair-system`
- Emergency: Label `critical`

---

**Last Updated:** 2026-04-04  
**Version:** 1.0.0
