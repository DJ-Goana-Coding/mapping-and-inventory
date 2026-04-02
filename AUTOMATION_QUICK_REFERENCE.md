# CITADEL OMEGA - Automation Quick Reference

## 🚀 Quick Commands

### Interactive Menu
```bash
./automate_all.sh
```

### One-Line Automation
```bash
# Full automation (pull + all workflows)
gh workflow run auto_sync_and_run.yml --ref main

# Sync all repos
gh workflow run multi_repo_sync.yml --ref main -f trigger_workflows=true

# Check/merge PRs
gh workflow run auto_merge_to_main.yml --ref main
```

---

## 📋 Common Operations

### Daily Workflow
```bash
# 1. Pull latest
git pull origin main

# 2. Trigger all workflows
./trigger_all_workflows.sh

# 3. Check status
gh run list --limit 5
```

### PR Management
```bash
# Create PR
gh pr create --title "..." --body "..."

# Add auto-merge label (for automated PRs only)
gh pr edit <pr-number> --add-label "auto-merge"

# Merge manually
gh pr merge <pr-number> --squash --delete-branch
```

### Workflow Monitoring
```bash
# List runs
gh run list

# Watch specific run
gh run watch <run-id>

# View logs
gh run view <run-id> --log

# Cancel run
gh run cancel <run-id>
```

---

## 🤖 Automated Workflows

| Workflow | Schedule | Purpose |
|----------|----------|---------|
| **Auto Sync and Run** | Daily 2 AM UTC | Pull + trigger all workflows |
| **Multi-Repo Sync** | Every 6 hours | Sync all CITADEL repos |
| **Auto-Merge** | On PR events | Merge approved PRs |

---

## ✅ Auto-Merge Requirements

To enable auto-merge for a PR:
1. ✅ Add `auto-merge` label
2. ✅ All status checks must pass
3. ✅ No merge conflicts

```bash
gh pr edit <pr-number> --add-label "auto-merge"
```

⚠️ **Use only for:**
- Automated dependency updates
- Bot-generated PRs
- Documentation updates
- Non-code changes

🚨 **Do NOT use for:**
- Code changes requiring review
- Breaking changes
- Security updates

---

## 📊 Status Checks

### Repository Health
```bash
# Full status report
./automate_all.sh
# Select: 5) Status report

# Quick checks
git status
gh pr list --state open
gh run list --limit 5
```

### Workflow Status
```bash
# Check all workflows
gh workflow list

# View specific workflow runs
gh run list --workflow=auto_sync_and_run.yml
gh run list --workflow=multi_repo_sync.yml
gh run list --workflow=auto_merge_to_main.yml
```

---

## 🔧 Manual Workflow Triggers

```bash
# TIA_CITADEL_DEEP_SCAN (321GB scan)
gh workflow run tia_citadel_deep_scan.yml --ref main

# S10_PUSH_TO_VAULT (device sync)
gh workflow run s10_push_to_vault.yml --ref main \
  -f sync_intel=true -f sync_cargo=true

# Sync to HuggingFace
gh workflow run sync_to_hf.yml --ref main

# Auto Sync and Run
gh workflow run auto_sync_and_run.yml --ref main \
  -f run_workflows=true -f merge_to_main=false

# Multi-Repo Sync
gh workflow run multi_repo_sync.yml --ref main \
  -f operation=sync -f trigger_workflows=true

# Auto-Merge
gh workflow run auto_merge_to_main.yml --ref main \
  -f pr_number=123
```

---

## 🚨 Emergency Procedures

### Stop All Automation
```bash
# Disable scheduled workflows
gh workflow disable auto_sync_and_run.yml
gh workflow disable multi_repo_sync.yml
gh workflow disable auto_merge_to_main.yml

# Cancel running workflows
gh run list --status in_progress --json databaseId -q '.[].databaseId' | \
  xargs -I {} gh run cancel {}
```

### Re-enable Automation
```bash
gh workflow enable auto_sync_and_run.yml
gh workflow enable multi_repo_sync.yml
gh workflow enable auto_merge_to_main.yml
```

---

## 📚 Documentation

- [FULL_AUTOMATION_GUIDE.md](FULL_AUTOMATION_GUIDE.md) - Complete automation documentation
- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Workflow-specific documentation
- [RUN_ALL_WORKFLOWS.md](RUN_ALL_WORKFLOWS.md) - Step-by-step instructions
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment procedures

---

## 🎯 Best Practices

### Daily Operations
1. ✅ Check status report in morning
2. ✅ Review automated workflow runs
3. ✅ Monitor open PRs

### Weekly Operations
1. ✅ Run full automation check
2. ✅ Review merged PRs
3. ✅ Update documentation if needed

### Monthly Operations
1. ✅ Review automation schedules
2. ✅ Update secrets if needed
3. ✅ Audit auto-merged PRs

---

## 🔑 Required Secrets

| Secret | Used By | Purpose |
|--------|---------|---------|
| `RCLONE_CONFIG_DATA` | TIA_CITADEL_DEEP_SCAN, S10_PUSH_TO_VAULT | Google Drive access |
| `HF_TOKEN` | sync_to_hf | HuggingFace deployment |
| `GITHUB_TOKEN` | All workflows | GitHub API access (auto-provided) |

---

## 🌐 Links

- **Actions:** https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
- **HuggingFace:** https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
- **Repository:** https://github.com/DJ-Goana-Coding/mapping-and-inventory

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-02
