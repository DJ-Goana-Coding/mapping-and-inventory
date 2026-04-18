# 🏛️ CITADEL OMNIDIMENSIONAL QUICK REFERENCE

**Version:** 1.0.0 | **Date:** 2026-04-04 | **Status:** ✅ OPERATIONAL

---

## ⚡ One-Command Operations

```bash
# Full deployment (all phases)
./omnidimensional_deploy.sh full

# Quick test only
./omnidimensional_deploy.sh test

# Security sweep only
./omnidimensional_deploy.sh sweep

# Dashboard only
./omnidimensional_deploy.sh dashboard
```

---

## 📖 Bible Operations

```bash
# Generate all District BIBLEs
python scripts/bible_generator.py

# View a District BIBLE
cat Districts/D01_COMMAND_INPUT/BIBLE.md

# Search for specific info
grep -r "Shopping List" Districts/*/BIBLE.md
```

---

## 🧪 Testing

```bash
# Run all tests
python scripts/comprehensive_test_runner.py

# Run District-specific tests
python -m pytest Districts/D04_OMEGA_TRADER/tests/

# View test results
cat data/monitoring/test_results.json | jq .summary
```

---

## 🧹 Security Sweep

```bash
# Run full sweep
python scripts/omnidimensional_sweep.py

# View sweep results
cat data/monitoring/omnidimensional_sweep.json | jq .summary

# Check quarantine
ls -R data/security/quarantine/

# Restore false positive
mv data/security/quarantine/path/to/file.py original/location/
```

---

## 🎯 Commander Dashboard

```bash
# Install dependencies (first time only)
pip install streamlit pandas

# Launch dashboard
streamlit run commander_dashboard.py

# Access at:
# http://localhost:8501
```

---

## 🤖 GitHub Actions

```bash
# Trigger test suite
gh workflow run comprehensive_test_suite.yml

# Trigger security sweep
gh workflow run omnidimensional_sweep.yml

# Trigger Bible audit
gh workflow run bible_read_system_audit.yml

# View workflow status
gh run list --limit 10
```

---

## 📊 Status Checks

```bash
# District health
for d in Districts/D*; do
  echo "$(basename $d): $(ls $d/*.md $d/*.json 2>/dev/null | wc -l)/4 artifacts"
done

# Test status
python -c "import json; r=json.load(open('data/monitoring/test_results.json')); print(f\"Tests: {r['summary']['success_rate']}% pass rate\")"

# Security status
python -c "import json; r=json.load(open('data/monitoring/omnidimensional_sweep.json')); print(f\"Security: {r['summary']['infected_files']} infections\")"
```

---

## 🛠️ Common Fixes

### Missing BIBLEs
```bash
python scripts/bible_generator.py
```

### Failed Tests
```bash
cat data/monitoring/test_results.json | jq .details
# Review failures and fix code
python scripts/comprehensive_test_runner.py
```

### Security Alerts
```bash
# Review quarantined files
ls -l data/security/quarantine/
# If false positive, restore
# If real threat, investigate and fix source
```

### Dashboard Won't Start
```bash
pip install --upgrade streamlit pandas
streamlit run commander_dashboard.py
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `Districts/*/BIBLE.md` | District operating procedures |
| `scripts/bible_generator.py` | Generate BIBLEs |
| `scripts/omnidimensional_sweep.py` | Security scanner |
| `scripts/comprehensive_test_runner.py` | Test executor |
| `commander_dashboard.py` | Status dashboard |
| `omnidimensional_deploy.sh` | Master deployment |
| `data/monitoring/test_results.json` | Test outcomes |
| `data/monitoring/omnidimensional_sweep.json` | Security scan |
| `data/security/quarantine/` | Infected files |

---

## 🔥 Emergency Procedures

### System Contaminated
```bash
# 1. Run sweep
python scripts/omnidimensional_sweep.py

# 2. Review quarantine
ls -R data/security/quarantine/

# 3. Fix source of infection
# 4. Re-run sweep to verify
python scripts/omnidimensional_sweep.py
```

### Tests All Failing
```bash
# 1. Check Python version
python --version  # Should be 3.11+

# 2. Reinstall dependencies
pip install -r requirements.txt

# 3. Run tests again
python scripts/comprehensive_test_runner.py
```

### Missing District Artifacts
```bash
# 1. Run Bible generator
python scripts/bible_generator.py

# 2. Run District harvester (if exists)
python scripts/autonomous_district_harvester.py

# 3. Verify completeness
python scripts/omnidimensional_sweep.py
```

---

## 🎓 Best Practices

1. **Run sweep weekly** - Catch threats early
2. **Test before commits** - Prevent broken code
3. **Review quarantine** - False positives happen
4. **Update BIBLEs** - Keep docs current
5. **Monitor dashboard** - Stay informed
6. **Automate everything** - Let workflows handle it
7. **Document changes** - Future you will thank you

---

## 📞 Support

- **Documentation:** `OMNIDIMENSIONAL_OPERATIONS_GUIDE.md`
- **Completion Report:** `OMNIDIMENSIONAL_DEPLOYMENT_COMPLETE.md`
- **District BIBLEs:** `Districts/*/BIBLE.md`
- **GitHub Issues:** https://github.com/DJ-Goana-Coding/mapping-and-inventory/issues

---

## 🎯 Quick Stats

- **Districts:** 9
- **BIBLEs:** 9 (100%)
- **Scripts:** 4
- **Workflows:** 3
- **Test Scenarios:** 27+
- **Security Patterns:** 11
- **Documentation Pages:** 4

---

## ✨ One-Liners

```bash
# Full status
./omnidimensional_deploy.sh full && cat OMNIDIMENSIONAL_DEPLOYMENT_REPORT.md

# Quick health check
python scripts/omnidimensional_sweep.py && python scripts/comprehensive_test_runner.py

# Dashboard
streamlit run commander_dashboard.py

# Emergency clean
python scripts/omnidimensional_sweep.py && ls -R data/security/quarantine/
```

---

**Citadel Architect v25.0.OMNI++** | **ALL SYSTEMS GO!** 🚀
