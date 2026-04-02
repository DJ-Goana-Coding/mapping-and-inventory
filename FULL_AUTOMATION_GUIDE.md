# CITADEL OMEGA - Full Automation Guide

## Overview

This guide covers the complete automation system for managing pulls, workflows, and merges across all CITADEL OMEGA repositories.

## 🎯 Automation Capabilities

The automation system provides:

1. **Automated Pulls** - Sync all repositories with their remote main branches
2. **Automated Workflows** - Trigger all GitHub Actions workflows on schedule or demand
3. **Automated Merges** - Auto-merge eligible PRs to main branch with safety checks
4. **Multi-Repository Orchestration** - Manage operations across all CITADEL repos
5. **Status Monitoring** - Track repository health and workflow status

---

## 🚀 Quick Start

### Method 1: Interactive Script (Recommended)

```bash
./automate_all.sh
```

This launches an interactive menu with options for:
- Pull latest changes
- Trigger workflows
- Check and merge PRs
- Full automation
- Status reports
- Multi-repository sync

### Method 2: GitHub Actions Workflows

#### Auto Sync and Run All Workflows

Automatically runs daily at 2:00 AM UTC or on-demand:

```bash
# Trigger manually via GitHub CLI
gh workflow run auto_sync_and_run.yml --ref main

# Or via GitHub Actions web interface:
# https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
```

**What it does:**
- ✅ Pulls latest changes from main
- ✅ Triggers all workflows (TIA_CITADEL_DEEP_SCAN, S10_PUSH_TO_VAULT, sync_to_hf)
- ✅ Monitors workflow status
- ✅ Reports completion

#### Multi-Repository Sync Orchestrator

Runs every 6 hours or on-demand:

```bash
gh workflow run multi_repo_sync.yml --ref main
```

**What it does:**
- ✅ Syncs current repository
- ✅ Checks repository status
- ✅ Reports on all related repositories
- ✅ Prepares for future multi-repo management

#### Auto-Merge to Main

Automatically triggered on PR events or on-demand:

```bash
gh workflow run auto_merge_to_main.yml --ref main
```

**What it does:**
- ✅ Checks PR eligibility (label, status checks, conflicts)
- ✅ Auto-merges approved PRs
- ✅ Triggers workflows after merge
- ✅ Cleans up merged branches

---

## 📋 Detailed Workflow Documentation

### 1. Auto Sync and Run All Workflows

**File:** `.github/workflows/auto_sync_and_run.yml`

**Schedule:** Daily at 2:00 AM UTC

**Manual Trigger:**
```bash
gh workflow run auto_sync_and_run.yml \
  --ref main \
  -f run_workflows=true \
  -f merge_to_main=false
```

**Inputs:**
- `run_workflows` (boolean, default: true) - Run all workflows after sync
- `merge_to_main` (boolean, default: false) - Auto-merge eligible PRs

**Steps:**
1. Checkout repository with full history
2. Configure Git credentials
3. Pull latest from main branch
4. Check open PRs for auto-merge eligibility
5. Trigger all workflows:
   - TIA_CITADEL_DEEP_SCAN
   - S10_PUSH_TO_VAULT
   - sync_to_hf
6. Monitor workflow status

### 2. Multi-Repository Sync Orchestrator

**File:** `.github/workflows/multi_repo_sync.yml`

**Schedule:** Every 6 hours

**Manual Trigger:**
```bash
gh workflow run multi_repo_sync.yml \
  --ref main \
  -f target_repos=all \
  -f operation=sync \
  -f trigger_workflows=false
```

**Inputs:**
- `target_repos` (string, default: "all") - Repos to sync
- `operation` (choice: sync/pull/status) - Operation to perform
- `trigger_workflows` (boolean, default: false) - Trigger workflows after sync

**Steps:**
1. Checkout mapping-and-inventory
2. Define repository list from SYSTEM_MAP.txt
3. Sync current repository
4. Check repository status (commits, PRs, workflows)
5. Report on related repositories
6. Optionally trigger workflows

**Future Expansion:**
The workflow is designed to support multiple repositories:
- omega-trading-system
- forever-learning
- CITADEL_ARK
- memory-codex

### 3. Auto-Merge to Main

**File:** `.github/workflows/auto_merge_to_main.yml`

**Triggers:**
- PR opened, synchronized, reopened, or labeled
- Manual workflow dispatch

**Manual Trigger:**
```bash
gh workflow run auto_merge_to_main.yml \
  --ref main \
  -f pr_number=123
```

**Inputs:**
- `pr_number` (string, optional) - Specific PR to check/merge

**Auto-Merge Requirements:**
1. ✅ PR must have `auto-merge` label
2. ✅ All status checks must pass
3. ✅ No merge conflicts (mergeable state)

**Steps:**
1. Check PR eligibility
2. Verify auto-merge label exists
3. Check all status checks passed
4. Verify no conflicts
5. Auto-merge with squash commit
6. Delete branch after merge
7. Report status

**Safety Features:**
- Conservative by default (requires explicit label)
- Checks all status checks
- Prevents merge if conflicts exist
- Deletes branch automatically after merge

---

## 🎮 Interactive Script Usage

### Launch the Script

```bash
./automate_all.sh
```

### Menu Options

#### 1. 📥 Pull latest changes from main

Synchronizes the local main branch with the remote:
```bash
git fetch origin
git checkout main
git pull origin main
```

#### 2. 🚀 Trigger all workflows

Triggers all three workflows:
- TIA_CITADEL_DEEP_SCAN (321GB scan)
- S10_PUSH_TO_VAULT (device sync)
- sync_to_hf (HuggingFace deployment)

#### 3. 🔀 Check and merge eligible PRs

Lists open PRs and checks for auto-merge eligibility:
- Shows all open PRs
- Displays auto-merge requirements
- Reports which PRs are eligible

#### 4. ⚡ Full automation (pull + workflows + merge)

Runs the complete automation sequence:
1. Pull latest changes
2. Trigger all workflows
3. Check for mergeable PRs

#### 5. 📊 Status report

Displays comprehensive repository status:
- Current branch
- Git status
- Recent commits (last 5)
- Open pull requests
- Recent workflow runs (last 5)

#### 6. 🔄 Sync all related repositories

Syncs the current repo and reports on related repos:
- mapping-and-inventory (current)
- omega-trading-system
- forever-learning
- CITADEL_ARK
- memory-codex

#### 7. 🛠️ Manual workflow dispatch

Interactive workflow selector:
1. tia_citadel_deep_scan.yml
2. s10_push_to_vault.yml
3. sync_to_hf.yml
4. auto_sync_and_run.yml
5. multi_repo_sync.yml
6. auto_merge_to_main.yml

---

## 🔐 Security & Safety

### Pull Operations

✅ **Safe:**
- Only pulls from origin/main
- No force operations
- Preserves local changes

### Workflow Triggers

✅ **Safe:**
- Requires GitHub authentication
- Uses workflow_dispatch (manual trigger)
- Respects workflow permissions
- Handles secret validation errors gracefully

### Auto-Merge

✅ **Safe with precautions:**
- Requires explicit `auto-merge` label
- Checks all status checks
- Prevents merge with conflicts
- Manual approval recommended for code changes

⚠️ **Recommendations:**
1. Use `auto-merge` label only for trusted automated PRs
2. Require at least 1 approval for code changes
3. Enable branch protection rules
4. Monitor merged PRs regularly

---

## 📊 Monitoring & Troubleshooting

### View Workflow Status

```bash
# List recent workflow runs
gh run list --limit 10

# Watch a specific run
gh run watch <run-id>

# View logs
gh run view <run-id> --log

# View failed jobs only
gh run list --status failure
```

### View PR Status

```bash
# List open PRs
gh pr list --state open

# View specific PR
gh pr view <pr-number>

# Check PR status
gh pr checks <pr-number>
```

### Common Issues

#### Issue: "Workflow trigger failed (may need secrets)"

**Solution:**
Check that required secrets exist:
- `RCLONE_CONFIG_DATA` (for TIA_CITADEL_DEEP_SCAN, S10_PUSH_TO_VAULT)
- `HF_TOKEN` (for sync_to_hf)

See [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) for secret setup.

#### Issue: "PR not eligible for auto-merge"

**Solution:**
Verify requirements:
1. Add `auto-merge` label to PR
2. Wait for all status checks to pass
3. Resolve any merge conflicts

#### Issue: "Not authenticated with GitHub"

**Solution:**
```bash
gh auth login
```

Follow the prompts to authenticate.

---

## 🗓️ Scheduled Operations

### Daily (2:00 AM UTC)
- Auto Sync and Run All Workflows
- Pulls latest changes
- Triggers all workflows

### Every 6 Hours
- Multi-Repository Sync Orchestrator
- Syncs all repositories
- Reports status

### On PR Events
- Auto-Merge to Main
- Checks PR eligibility
- Auto-merges if requirements met

---

## 🔧 Configuration

### Enable/Disable Scheduled Runs

Edit `.github/workflows/auto_sync_and_run.yml`:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
    # - cron: '0 */6 * * *'  # Every 6 hours
    # - cron: '0 0 * * 0'  # Weekly on Sunday
```

### Customize Auto-Merge Behavior

Edit `.github/workflows/auto_merge_to_main.yml`:

```yaml
# Change required label
HAS_AUTO_MERGE=$(echo "$PR_INFO" | jq -r '.labels[]? | select(.name == "auto-merge") | .name')

# Change to "ready-to-merge", "approved", etc.
```

### Add More Repositories

Edit `.github/workflows/multi_repo_sync.yml`:

```yaml
repos:
  - name: "omega-trading-system"
    owner: "DJ-Goana-Coding"
    pillar: "TRADING"
  # Add more repos here
```

---

## 📚 Related Documentation

- [WORKFLOW_GUIDE.md](WORKFLOW_GUIDE.md) - Complete workflow documentation
- [RUN_ALL_WORKFLOWS.md](RUN_ALL_WORKFLOWS.md) - Step-by-step workflow instructions
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Deployment procedures
- [SYSTEM_MAP.txt](SYSTEM_MAP.txt) - Repository architecture

---

## 🎯 Best Practices

### Daily Operations

1. **Morning Check:**
   ```bash
   ./automate_all.sh
   # Select: Status report
   ```

2. **Trigger Workflows:**
   ```bash
   # If data updated or changes merged
   gh workflow run auto_sync_and_run.yml
   ```

3. **Monitor Results:**
   ```bash
   gh run list --limit 5
   ```

### PR Management

1. **Create PR:**
   ```bash
   gh pr create --title "Feature: X" --body "Description"
   ```

2. **Add auto-merge label (if appropriate):**
   ```bash
   gh pr edit <pr-number> --add-label "auto-merge"
   ```

3. **Monitor merge:**
   ```bash
   gh pr view <pr-number>
   ```

### Multi-Repository Workflow

1. **Daily sync all repos:**
   ```bash
   gh workflow run multi_repo_sync.yml \
     -f operation=sync \
     -f trigger_workflows=true
   ```

2. **Weekly full automation:**
   ```bash
   gh workflow run auto_sync_and_run.yml \
     -f run_workflows=true \
     -f merge_to_main=true
   ```

---

## ✅ Success Indicators

### Automated Pull Success
- ✅ Main branch up to date
- ✅ No merge conflicts
- ✅ Clean git status

### Workflow Trigger Success
- ✅ All 3 workflows triggered
- ✅ Green checkmarks in Actions tab
- ✅ Artifacts generated

### Auto-Merge Success
- ✅ PR merged to main
- ✅ Branch deleted
- ✅ Workflows triggered on main

---

## 🚨 Emergency Procedures

### Stop Automated Operations

```bash
# Disable scheduled runs
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

**Last Updated:** 2026-04-02
**Version:** 1.0.0
**Maintainer:** CITADEL OMEGA Team
