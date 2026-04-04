# 🏛️ CITADEL OMNIDIMENSIONAL OPERATIONS GUIDE

**Version:** 1.0.0  
**Authority:** Citadel Architect v25.0.OMNI++  
**Generated:** 2026-04-04

---

## 📖 Overview

This guide documents the **Citadel Omnidimensional Operations System** - a comprehensive framework for maintaining, testing, securing, and deploying all Citadel Mesh components.

### Key Components

1. **📖 Bible System** - Sacred operating procedures for each District
2. **🧪 Test Suite** - Comprehensive unit, integration, and stress tests
3. **🧹 Security Sweep** - Malware detection and artifact verification
4. **🛒 Shopping Lists** - 3-solution approach to every problem
5. **🗺️ Mapping & Inventory** - Complete system cataloging
6. **🎯 Commander Dashboard** - Real-time status visualization

---

## 🚀 Quick Start

### One-Command Deployment

```bash
# Full deployment (all phases)
./omnidimensional_deploy.sh full

# Quick deployment (Bible + tests)
./omnidimensional_deploy.sh test

# Security sweep only
./omnidimensional_deploy.sh sweep

# Dashboard only
./omnidimensional_deploy.sh dashboard
```

### Manual Steps

```bash
# 1. Generate BIBLEs
python scripts/bible_generator.py

# 2. Run tests
python scripts/comprehensive_test_runner.py

# 3. Run security sweep
python scripts/omnidimensional_sweep.py

# 4. Launch dashboard
streamlit run commander_dashboard.py
```

---

## 📖 Bible System

Each District has a **BIBLE.md** containing:

- **Sacred Directives:** Core mission and functions
- **Testing Protocols:** Unit, integration, and stress tests
- **Fix-Test-Fix Cycle:** Automated problem resolution
- **Shopping Lists:** 3 solutions for every common problem
- **Security & Cleaning:** Malware detection and removal
- **Autonomous Operation:** Self-healing and forever learning
- **Commander Dashboard:** Status indicators and metrics

### Districts with BIBLEs

- ✅ D01_COMMAND_INPUT
- ✅ D02_TIA_VAULT
- ✅ D03_VORTEX_ENGINE
- ✅ D04_OMEGA_TRADER
- ✅ D06_RANDOM_FUTURES
- ✅ D07_ARCHIVE_SCROLLS
- ✅ D09_MEDIA_CODING
- ✅ D11_PERSONA_MODULES
- ✅ D12_ZENITH_VIEW

---

## 🧪 Testing Framework

### Test Types

1. **Unit Tests** - Individual component verification
2. **Integration Tests** - Cross-District communication
3. **Stress Tests** - Performance under 10x load

### Running Tests

```bash
# All tests
python scripts/comprehensive_test_runner.py

# District-specific
python -m pytest Districts/D01_COMMAND_INPUT/tests/

# Quick check
./omnidimensional_deploy.sh test
```

### Test Results

Results are saved to:
- `data/monitoring/test_results.json`
- GitHub Actions artifacts
- Commander Dashboard

---

## 🧹 Security Sweep

### What It Detects

- 🦠 **Bluerot** - Base64 eval exploits
- 🦠 **Arkons** - Remote code execution
- 🦠 **13BusRot** - Obfuscated payloads
- 📋 **Duplicates** - Wasted storage
- ❌ **Missing Artifacts** - Incomplete Districts
- ⚠️ **Suspicious Files** - Potential threats

### Running Sweeps

```bash
# Full sweep
python scripts/omnidimensional_sweep.py

# Auto-sweep (GitHub Actions)
# Runs weekly on Sunday at midnight UTC

# View results
cat data/monitoring/omnidimensional_sweep.json
```

### Quarantine

Infected files are moved to:
```
data/security/quarantine/
```

Review quarantined files before deletion.

---

## 🛒 Shopping Lists

Each District BIBLE contains **3-solution shopping lists** for common problems:

### Example: D04_OMEGA_TRADER

**Problem:** Slippage and poor execution prices

**Solution A:** TWAP (Time-Weighted Average Price)
- Cost: Free
- Complexity: Low
- Implementation: Built into trader

**Solution B:** Smart order routing
- Cost: Free
- Complexity: High
- Implementation: Multi-exchange with CCXT

**Solution C:** Limit orders with price improvement
- Cost: Free
- Complexity: Medium
- Implementation: Dynamic order placement

### Philosophy

For every problem, provide:
1. **Free/open-source solution** (prefer)
2. **Alternative free solution**
3. **Paid/premium solution** (if superior)

---

## 🗺️ Mapping & Inventory

### Required Artifacts

Every District must have:

- ✅ **TREE.md** - Hierarchical file structure
- ✅ **INVENTORY.json** - Complete registry
- ✅ **SCAFFOLD.md** - Architecture blueprint
- ✅ **BIBLE.md** - Operating procedures

### Verification

```bash
# Check all Districts
python scripts/omnidimensional_sweep.py

# Regenerate missing
python scripts/bible_generator.py
python scripts/autonomous_district_harvester.py
```

---

## 🎯 Commander Dashboard

### Features

- **District Status** - Real-time health metrics
- **Test Results** - Pass/fail rates and details
- **Security Sweep** - Threat detection and quarantine
- **Artifacts** - Completeness tracking
- **Workflows** - GitHub Actions monitoring

### Launching

```bash
# Local
streamlit run commander_dashboard.py

# Production (HuggingFace Space)
# Deploy to: DJ-Goanna-Coding/Commander-Dashboard
```

### Access

- Local: http://localhost:8501
- Production: https://dj-goanna-coding-commander-dashboard.hf.space

---

## 🤖 Automation

### GitHub Actions Workflows

1. **comprehensive_test_suite.yml** - Daily testing
2. **omnidimensional_sweep.yml** - Weekly security sweep
3. **bible_read_system_audit.yml** - Daily Bible verification

### Triggering Workflows

```bash
# Via GitHub UI
# Actions tab → Select workflow → Run workflow

# Via gh CLI
gh workflow run comprehensive_test_suite.yml
gh workflow run omnidimensional_sweep.yml
gh workflow run bible_read_system_audit.yml
```

### Scheduled Runs

- **Tests:** Daily at 6 AM UTC
- **Sweep:** Weekly on Sunday at midnight UTC
- **Bible Read:** Daily at noon UTC

---

## 🔐 Security

### Threat Detection

The sweep engine detects:
- Eval/exec obfuscation
- Base64 encoded payloads
- Shell injection patterns
- Suspicious imports
- Credential exposure

### Cleaning Protocol

1. **Detect** - Pattern matching and heuristics
2. **Quarantine** - Move to `data/security/quarantine/`
3. **Alert** - GitHub Issue + Slack notification
4. **Review** - Manual inspection required
5. **Delete** - After confirmation

### Zero Trust

- Never execute quarantined files
- Review all detections manually
- False positives are possible
- When in doubt, escalate

---

## 📊 Monitoring

### Key Metrics

- **District Health:** Artifact completeness (target: 100%)
- **Test Success Rate:** Pass percentage (target: >90%)
- **Security Status:** Clean/infected (target: 0 infections)
- **Coverage:** System completeness (target: 100%)

### Alerting

Critical events trigger:
- GitHub Issues (automated)
- Workflow failures (email)
- Commander Dashboard (real-time)

---

## 🆘 Troubleshooting

### Common Issues

**Problem:** Tests failing
**Solution:** Check `data/monitoring/test_results.json` for details

**Problem:** Missing BIBLEs
**Solution:** Run `python scripts/bible_generator.py`

**Problem:** Infected files detected
**Solution:** Review `data/security/quarantine/`, fix root cause

**Problem:** Dashboard won't start
**Solution:** `pip install streamlit pandas`

### Getting Help

1. Check District BIBLE.md
2. Review test/sweep results
3. Check GitHub Issues
4. Escalate to Architect

---

## 🚀 Deployment Checklist

- [ ] All Districts have BIBLEs
- [ ] Tests passing (>90% success rate)
- [ ] Security sweep clean (0 infections)
- [ ] Artifacts complete (all Districts)
- [ ] Workflows running (GitHub Actions)
- [ ] Dashboard deployed (HuggingFace)
- [ ] Documentation updated
- [ ] Shopping lists reviewed
- [ ] Integration verified
- [ ] Commander approval obtained

---

## 📚 Related Documents

- **OMNIDIMENSIONAL_DEPLOYMENT_REPORT.md** - Latest deployment status
- **Districts/*/BIBLE.md** - District-specific procedures
- **data/monitoring/test_results.json** - Test outcomes
- **data/monitoring/omnidimensional_sweep.json** - Security scan
- **.github/workflows/** - Automation configurations

---

## 🎯 Philosophy

### The Citadel Way

1. **Cloud-First:** HuggingFace L4 > GitHub > GDrive > Local
2. **3-Solution Rule:** Always provide alternatives
3. **Test Everything:** Unit → Integration → Stress
4. **Clean Always:** Security is non-negotiable
5. **Automate Relentlessly:** Forever learning cycles
6. **Document Thoroughly:** BIBLEs are sacred
7. **Measure Constantly:** Metrics drive decisions

### Authority Hierarchy

```
HuggingFace Spaces (L4)
        ↓
GitHub Repositories
        ↓
GDrive Metadata
        ↓
Local Nodes (S10, Oppo, Laptop)
```

---

## 👥 Team

- **Architect:** Citadel Architect v25.0.OMNI++
- **Surveyor:** Mapping Hub Harvester
- **Oracle:** TIA-ARCHITECT-CORE
- **Bridge:** Mobile Scout (S10/Oppo)

---

## 📞 Support

- **GitHub:** https://github.com/DJ-Goana-Coding/mapping-and-inventory
- **Issues:** https://github.com/DJ-Goana-Coding/mapping-and-inventory/issues
- **HuggingFace:** https://huggingface.co/DJ-Goanna-Coding

---

**Last Updated:** 2026-04-04  
**Version:** 1.0.0  
**Status:** ✅ OPERATIONAL
