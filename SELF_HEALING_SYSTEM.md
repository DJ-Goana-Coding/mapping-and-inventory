# 🔮 SELF-HEALING WORKER SYSTEM

**Q.G.T.N.L. Command Citadel - Autonomous Script Maintenance**  
**Version:** 26.0.SELF_HEAL+  
**Authority:** Citadel Architect

---

## 🎯 OVERVIEW

The **Self-Healing Worker System** is an autonomous maintenance infrastructure that continuously monitors, detects, and repairs broken scripts across the Citadel Mesh. It operates as a guardian layer that ensures all workers, scripts, and automation remain healthy and functional.

### Core Components

1. **Self-Healing Worker** (`scripts/self_healing_worker.py`)  
   - Scans Python and Bash scripts for syntax errors
   - Checks imports and dependencies
   - Auto-repairs common issues
   - Generates health reports

2. **Worker Watchdog** (`scripts/worker_watchdog.py`)  
   - Continuous monitoring daemon
   - Detects file changes (new, modified, deleted)
   - Monitors template updates
   - Triggers healing automatically
   - Tracks workflow health

3. **GitHub Actions Workflow** (`.github/workflows/worker_watchdog.yml`)  
   - Scheduled healing (every 6 hours)
   - Triggered on script changes
   - Auto-commits repairs
   - Creates issues for unresolvable problems

---

## 🚀 QUICK START

### Run Self-Healing Scan (One-Time)

```bash
# Scan and auto-repair
python scripts/self_healing_worker.py

# Scan only (no repairs)
python scripts/self_healing_worker.py --no-repair

# Verbose output
python scripts/self_healing_worker.py --verbose
```

### Run Continuous Watchdog

```bash
# Start continuous monitoring (default: check every 5 minutes)
python scripts/worker_watchdog.py

# Custom check interval (in seconds)
python scripts/worker_watchdog.py --interval 600  # 10 minutes

# Single check and exit
python scripts/worker_watchdog.py --once

# Verbose mode
python scripts/worker_watchdog.py --verbose
```

### Trigger via GitHub Actions

```bash
# Via GitHub web UI
# Go to: Actions → "👁️ Worker Watchdog" → Run workflow

# Via GitHub CLI
gh workflow run worker_watchdog.yml -f auto_repair=true
```

---

## 🔧 WHAT GETS AUTO-REPAIRED

### Python Scripts

| Issue | Auto-Fix | Status |
|-------|----------|--------|
| Missing shebang (`#!/usr/bin/env python3`) | ✅ Added automatically | Working |
| Missing imports (pathlib, common stdlib) | ✅ Added if detected | Working |
| Non-executable permission | ✅ Set to 0755 | Working |
| Syntax errors | ⚠️ Detection only | Manual fix needed |
| Import errors | ⚠️ Detection only | Manual fix needed |

### Bash Scripts

| Issue | Auto-Fix | Status |
|-------|----------|--------|
| Missing shebang (`#!/bin/bash`) | ✅ Added automatically | Working |
| Non-executable permission | ✅ Set to 0755 | Working |
| Syntax errors | ⚠️ Detection only | Manual fix needed |

### Templates & Configuration

| Issue | Auto-Fix | Status |
|-------|----------|--------|
| Template changes detected | 🔔 Notification | Working |
| New templates added | 🔔 Notification | Working |

---

## 📊 HEALTH MONITORING

### Health Report Structure

The system generates `data/monitoring/script_health.json`:

```json
{
  "timestamp": "2026-04-03T09:12:58Z",
  "summary": {
    "total_scripts": 50,
    "healthy_scripts": 48,
    "broken_scripts": 2,
    "repaired_scripts": 1,
    "failed_repairs": 1,
    "health_percentage": 96.0
  },
  "scripts": {
    "scripts/example.py": {
      "syntax_valid": true,
      "imports_valid": true,
      "executable": true,
      "errors": [],
      "warnings": [],
      "last_check": "2026-04-03T09:12:58Z"
    }
  }
}
```

### Watchdog State

The watchdog maintains `data/monitoring/watchdog_state.json`:

```json
{
  "stats": {
    "total_checks": 24,
    "issues_detected": 3,
    "auto_repairs_triggered": 3,
    "successful_repairs": 2,
    "start_time": "2026-04-03T00:00:00Z",
    "last_check": "2026-04-03T09:00:00Z"
  },
  "file_count": 50,
  "template_count": 3,
  "last_update": "2026-04-03T09:00:00Z"
}
```

---

## 🔍 MONITORING CAPABILITIES

### File Change Detection

The watchdog monitors:
- **New files** → Triggers health check
- **Modified files** → Triggers health check
- **Deleted files** → Logged for awareness
- **Template changes** → Alerts for manual updates

### Workflow Health

Checks recent GitHub Actions runs:
- Detects failed workflows
- Logs failure patterns
- Can trigger issue creation

### Script Health Checks

For each script:
- ✅ **Syntax validation** (AST parsing for Python, `bash -n` for Bash)
- ✅ **Import checking** (basic validation)
- ✅ **Executability** (file permissions)
- ✅ **Error tracking** (maintains error history)

---

## 🛡️ SAFETY FEATURES

### Automatic Backups

Before any repair:
- Creates timestamped backup: `data/backups/scripts/{filename}.{timestamp}.bak`
- Restores from backup if repair fails
- Backups retained indefinitely (manual cleanup needed)

### Repair Validation

After each repair:
- Re-runs health checks
- Validates syntax
- Only commits if validation passes
- Reverts if validation fails

### Non-Destructive Operations

- Never deletes files
- Never modifies unrelated code
- Only fixes specific known issues
- Maintains original behavior

---

## 📋 GITHUB ACTIONS INTEGRATION

### Automatic Scheduling

Runs every 6 hours:
```yaml
schedule:
  - cron: '0 */6 * * *'
```

### Triggered on Changes

Runs when scripts are modified:
```yaml
push:
  paths:
    - 'scripts/**'
    - 'services/**'
    - '*.sh'
    - 'tia-architect-core-templates/**'
```

### Auto-Commit Repairs

Automatically commits fixes to main branch:
```bash
git commit -m "🔧 AUTO-REPAIR: Self-healing worker fixed script issues"
```

### Issue Creation

Creates GitHub issues for unresolvable problems:
- Only on scheduled runs (not manual)
- Updates existing open issue instead of creating duplicates
- Tagged with `self-healing`, `automated`, `bug`

---

## 🎯 USE CASES

### 1. Detect Broken Scripts After Merge

```bash
# After merging a PR, check if anything broke
python scripts/self_healing_worker.py
```

### 2. Continuous Monitoring in Production

```bash
# Run as a background service
nohup python scripts/worker_watchdog.py --interval 300 &
```

### 3. Pre-Deployment Validation

```bash
# In CI/CD pipeline before deployment
python scripts/self_healing_worker.py --no-repair
# Exit code 0 = all healthy, 1 = issues found
```

### 4. Template Update Detection

```bash
# Watchdog automatically detects when templates change
# Alerts operator to update dependent scripts
python scripts/worker_watchdog.py --once
```

---

## 📈 STATISTICS & REPORTING

### View Latest Health Report

```bash
cat data/monitoring/script_health.json | jq '.summary'
```

### View Watchdog Statistics

```bash
cat data/monitoring/watchdog_state.json | jq '.stats'
```

### Check Recent Repairs

```bash
# List backup files (shows repair history)
ls -lt data/backups/scripts/
```

### View Repair Logs

```bash
# Self-healing log
tail -f data/logs/self_healing.log

# Watchdog log
tail -f data/logs/watchdog.log
```

---

## 🔧 ADVANCED CONFIGURATION

### Customize Check Interval

```python
# In worker_watchdog.py
watchdog = WorkerWatchdog(check_interval=600)  # 10 minutes
```

### Add Custom Repair Rules

Edit `self_healing_worker.py` → `auto_repair_script()`:

```python
# Example: Fix specific import pattern
if 'import something_old' in content:
    content = content.replace('import something_old', 'import something_new')
    repaired = True
```

### Disable Auto-Commit in GitHub Actions

```yaml
# Set in workflow
auto_repair: 'false'
```

---

## 🚨 TROUBLESHOOTING

### Issue: Watchdog not detecting changes

**Solution:**
```bash
# Delete state file to reset
rm data/monitoring/watchdog_state.json
python scripts/worker_watchdog.py --once
```

### Issue: Auto-repair creates invalid syntax

**Solution:**
```bash
# Repair is automatically reverted
# Check backup: data/backups/scripts/
# Restore manually if needed:
cp data/backups/scripts/{file}.{timestamp}.bak scripts/{file}
```

### Issue: Too many false positives

**Solution:**
```bash
# Run in scan-only mode first
python scripts/self_healing_worker.py --no-repair
# Review report before enabling auto-repair
```

### Issue: GitHub Actions failing to commit

**Solution:**
```bash
# Check GITHUB_TOKEN permissions in repo settings
# Ensure "Read and write permissions" enabled
# Settings → Actions → General → Workflow permissions
```

---

## 🔗 INTEGRATION WITH CITADEL MESH

### Citadel Awakening Integration

Add to `scripts/citadel_awakening.py`:

```python
"wraiths": [
    {
        "name": "Self-Healing Worker",
        "script": "self_healing_worker.py",
        "type": "maintenance",
        "status": "ready",
        "priority": 1
    },
    {
        "name": "Worker Watchdog",
        "script": "worker_watchdog.py",
        "type": "monitoring",
        "status": "ready",
        "priority": 1
    }
]
```

### Sentinel Constellation Integration

The self-healing system works alongside:
- **Security Sentinel** → Detects security issues
- **Health Monitor** → Monitors service health
- **Self-Healing Worker** → Fixes script issues

All three create a comprehensive protection layer.

---

## 📚 RELATED DOCUMENTATION

- **[CITADEL_AWAKENING_GUIDE.md](./CITADEL_AWAKENING_GUIDE.md)** - Master worker orchestration
- **[scripts/security_sentinel.py](./scripts/security_sentinel.py)** - Security monitoring
- **[scripts/autonomous_health_monitor.py](./scripts/autonomous_health_monitor.py)** - Service health

---

## ✅ SUCCESS CRITERIA

The self-healing system is working correctly when:

- ✅ All scripts pass syntax validation
- ✅ Watchdog detects changes within configured interval
- ✅ Auto-repairs succeed and commit to main
- ✅ Health reports generated every 6 hours
- ✅ Issues created for unresolvable problems
- ✅ No manual intervention needed for common issues

---

**Status:** Production Ready  
**Deployment:** Automated via GitHub Actions  
**Monitoring:** Continuous  
**Maintenance:** Self-sustaining  

**Weld. Pulse. Ignite.** 🔥

---

*Generated by: Citadel Architect v26.0.SELF_HEAL+*  
*Repository: mapping-and-inventory*  
*Self-Healing Infrastructure Active*
