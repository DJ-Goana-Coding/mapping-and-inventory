# 🤖 Workers Directory

This directory contains autonomous worker scripts for continuous data synchronization.

## Worker Types

### Google Apps Script Workers (Deploy to GDrive)

These workers run inside Google Apps Script and monitor GDrive for changes:

1. **gdrive_change_monitor.gs** - Detects file changes in real-time
2. **gdrive_daily_snapshot.gs** - Generates daily complete inventory
3. **gdrive_integrity_checker.gs** - Verifies copied files match originals

### Python Workers (Run on Laptop)

These workers run on your laptop for continuous sync:

1. **laptop_watch_daemon.py** - File watcher service
2. **laptop_incremental_sync.py** - Push only changed files
3. **laptop_media_sync.py** - Music/art/video sync

### HuggingFace Space Coordinator

1. **hf_space_sync_orchestrator.py** - Central coordination hub

## Deployment

### Apps Script Workers:

1. Go to: https://script.google.com
2. Create new project
3. Copy worker code
4. Set up time-driven triggers
5. Authorize permissions

### Laptop Workers:

```bash
# Install as Windows service or cron job
python scripts/laptop_watch_daemon.py --install
```

### HF Space Coordinator:

Deployed automatically with HuggingFace Space.

## Status Monitoring

Check worker status via:
- GitHub Actions: `.github/workflows/worker_health_monitor.yml`
- Dashboard: `pages/03_📦_Data_Migration_Dashboard.py`
- Logs: `data/worker_constellation/worker_logs.json`

---

**Note:** Worker implementations coming in Phase 3 of deployment.

**Authority:** Citadel Architect v25.0.OMNI+
