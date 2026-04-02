# 📡 Workflow Monitoring Guide

## Overview
This guide explains how to monitor GitHub Actions workflow runs in real-time using the GitHub CLI (`gh`).

## Prerequisites
- GitHub CLI installed (`gh` command)
- Authenticated with GitHub (`gh auth login`)

## Monitoring Live Workflow Runs

### ✅ Correct Command: `gh run watch`

To monitor a workflow run in real-time as it progresses:

```bash
gh run watch <run-id>
```

**Example:**
```bash
gh run watch 23840652380
```

This command will:
- ✅ Display live updates as the workflow progresses
- ✅ Show each job and step as it executes
- ✅ Update every 3 seconds by default
- ✅ Exit when the workflow completes

### Options for `gh run watch`

| Flag | Description |
|------|-------------|
| `--compact` | Show only relevant/failed steps (cleaner output) |
| `--exit-status` | Exit with non-zero status if the run fails |
| `-i, --interval <seconds>` | Set refresh interval (default: 3 seconds) |

**Examples:**
```bash
# Watch with compact output (recommended for long workflows)
gh run watch 23840652380 --compact

# Watch with custom refresh interval (5 seconds)
gh run watch 23840652380 --interval 5

# Watch and exit with error code if workflow fails
gh run watch 23840652380 --exit-status
```

## Other Useful Commands

### View Workflow Run Summary
```bash
gh run view <run-id>
```

### View Workflow Run Logs
```bash
# View all logs
gh run view <run-id> --log

# View only failed steps
gh run view <run-id> --log-failed
```

### List Recent Workflow Runs
```bash
# List all runs
gh run list

# List runs for a specific workflow
gh run list --workflow=tia_citadel_deep_scan.yml

# List with specific status
gh run list --status=in_progress
gh run list --status=completed
gh run list --status=failure
```

### View Workflow Run in Browser
```bash
gh run view <run-id> --web
```

## Monitoring TIA_CITADEL_DEEP_SCAN Workflow

The `TIA_CITADEL_DEEP_SCAN` workflow performs a deep scan of Google Drive and can take several minutes. Here's how to monitor it:

### 1. Trigger the Workflow
```bash
gh workflow run tia_citadel_deep_scan.yml
```

### 2. Get the Run ID
```bash
gh run list --workflow=tia_citadel_deep_scan.yml --limit 1
```

### 3. Watch the Run
```bash
gh run watch <run-id> --compact
```

### Expected Steps
When monitoring `TIA_CITADEL_DEEP_SCAN`, you'll see these steps:
1. ✅ **Checkout Repository** - Quick (5-10 seconds)
2. ✅ **Install Rclone** - Quick (10-20 seconds)
3. ✅ **Configure Rclone** - Quick (< 5 seconds)
4. ✅ **Test Connection** - Quick (5-10 seconds)
5. 🔄 **Deep Scan** - SLOW (2-5 minutes) - Mapping 321GB of Google Drive
6. 🔄 **Pull GDrive Full Vault** - Variable (depends on data)
7. 🔄 **Pull Oppo Cargo** - Variable
8. 🔄 **Pull S10 Cargo** - Variable
9. 🔄 **Pull S10 CITADEL_OMEGA_INTEL** - Variable
10. 🔄 **Pull Laptop Cargo** - Variable
11. ✅ **Upload Intelligence Map** - Quick

## Common Issues

### ❌ "unknown flag: --follow"
**Problem:** `gh run view` does not support a `--follow` flag.

**Solution:** Use `gh run watch` instead:
```bash
# ❌ WRONG
gh run view 23840652380 --follow

# ✅ CORRECT
gh run watch 23840652380
```

### ⏳ "run is still in progress; logs will be available when it is complete"
**Problem:** You're trying to view logs with `gh run view --log` while the run is still in progress.

**Solution:** Use `gh run watch` to monitor live progress, or wait until completion to view logs.

### 🔒 Authentication Issues
**Problem:** Commands fail with authentication errors.

**Solution:** Make sure you're logged in:
```bash
gh auth login
gh auth status
```

## Quick Reference

| Task | Command |
|------|---------|
| Watch live run | `gh run watch <run-id>` |
| Watch compactly | `gh run watch <run-id> --compact` |
| View summary | `gh run view <run-id>` |
| View logs | `gh run view <run-id> --log` |
| View failed logs only | `gh run view <run-id> --log-failed` |
| List recent runs | `gh run list` |
| List specific workflow | `gh run list --workflow=<name>.yml` |
| Trigger workflow | `gh workflow run <name>.yml` |
| Open in browser | `gh run view <run-id> --web` |

## Pro Tips

1. **Use `--compact` for long workflows** - It makes the output much cleaner
2. **Open in browser for visual monitoring** - `gh run view <run-id> --web`
3. **Check status before viewing logs** - Use `gh run view <run-id>` first
4. **Use `--exit-status` in CI/CD** - Exit with proper error codes for automation
5. **Set custom intervals for slow workflows** - `--interval 10` for workflows that take many minutes

## Resources

- [GitHub CLI Documentation](https://cli.github.com/manual/)
- [GitHub CLI Run Commands](https://cli.github.com/manual/gh_run)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
