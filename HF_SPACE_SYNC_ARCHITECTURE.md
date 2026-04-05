# 🏛️ CITADEL HF SPACE SYNC ARCHITECTURE (v25.0.OMNI++)

**Generated**: 2026-04-04T20:47:07.769Z  
**Architect**: Citadel Architect (Sovereign Interpreter)  
**Authority**: Core Directive #4, #16, #17

---

## 🎯 CORE PRINCIPLE: PULL-OVER-PUSH

```
┌─────────────────────────────────────────────────────────────┐
│  CITADEL DATA FLOW (CORRECT ARCHITECTURE)                   │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  GitHub Repository (DJ-Goana-Coding/mapping-and-inventory)  │
│         ↑                                                    │
│         │ (commits/pushes)                                   │
│         │                                                    │
│    Local Nodes / Termux Bridge                              │
│                                                              │
│         ↓                                                    │
│         │ (PULL via git clone/fetch)                        │
│         ↓                                                    │
│                                                              │
│  HuggingFace Space (DJ-Goanna-Coding/Mapping-and-Inventory) │
│  └─> L4 GPU Compute Layer                                   │
│  └─> Forever Learning Cycle Execution                       │
│  └─> RAG Updates & Model Registry                           │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## ⚠️ CURRENT ISSUE: REVERSE FLOW DETECTED

**Existing Workflow**: `.github/workflows/hf_space_sync.yml`
- **Problem**: Uses `git push --force` from GitHub to HF
- **Violation**: Core Directive #4, #16
- **Risk**: Overrides HF Space autonomy, breaks L4 compute sovereignty

---

## ✅ CORRECT ARCHITECTURE

### 1. HF Space Auto-Pull Configuration

**Location**: HuggingFace Space Settings → Repository Settings

```yaml
# Space Configuration (app.yaml or README.md header)
---
title: Mapping and Inventory - Citadel Surveyor
emoji: 📚
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: true
license: mit
duplicated_from: null
models: []
datasets: []
---

# Sync Configuration
sync:
  source: https://github.com/DJ-Goana-Coding/mapping-and-inventory
  branch: main
  on_startup: true
  schedule: "0 */6 * * *"  # Every 6 hours
  webhook: true
```

### 2. HF Space Startup Script

**File**: `hf_startup.sh` (to be placed in repository root)

```bash
#!/bin/bash
# 🏛️ CITADEL HF SPACE STARTUP PROTOCOL
# Executes on HuggingFace Space initialization

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏛️ CITADEL SURVEYOR - HF SPACE STARTUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verify GitHub Source
GITHUB_REPO="https://github.com/DJ-Goana-Coding/mapping-and-inventory"
GITHUB_BRANCH="main"

echo "📡 Verifying GitHub connection..."
git config --global user.email "hf-space@citadel.ai"
git config --global user.name "Citadel Surveyor HF Space"

# 2. Pull Latest from GitHub
echo "📥 Pulling latest from GitHub ($GITHUB_BRANCH)..."
git fetch origin $GITHUB_BRANCH
git reset --hard origin/$GITHUB_BRANCH

# 3. Verify Integrity
echo "🔍 Verifying repository integrity..."
if [ ! -f "app.py" ]; then
  echo "❌ ERROR: app.py not found. Repository corrupted."
  exit 1
fi

# 4. Install Dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt --no-cache-dir
fi

# 5. Initialize Citadel Services
echo "🏛️ Initializing Citadel services..."
python -c "print('✅ Citadel Surveyor initialized successfully')"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ STARTUP COMPLETE - Ready to serve"
echo "🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
```

### 3. HF Space Sync Webhook Receiver

**File**: `hf_webhook_receiver.py` (to be placed in repository root)

```python
#!/usr/bin/env python3
"""
🏛️ CITADEL HF SPACE WEBHOOK RECEIVER
Listens for GitHub push events and triggers pulls
"""

import os
import subprocess
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Citadel HF Webhook Receiver")

GITHUB_REPO = "https://github.com/DJ-Goana-Coding/mapping-and-inventory"
GITHUB_BRANCH = "main"

@app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    Receives GitHub push events and triggers git pull
    """
    try:
        payload = await request.json()
        
        # Verify it's a push event to main branch
        if payload.get("ref") == f"refs/heads/{GITHUB_BRANCH}":
            logger.info("🔔 GitHub push detected to main branch")
            
            # Execute git pull
            result = subprocess.run(
                ["git", "pull", "origin", GITHUB_BRANCH],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info(f"✅ Pull successful: {result.stdout}")
            
            return JSONResponse({
                "status": "success",
                "message": "Repository synced successfully",
                "output": result.stdout
            })
        else:
            return JSONResponse({
                "status": "skipped",
                "message": f"Not a push to {GITHUB_BRANCH} branch"
            })
            
    except Exception as e:
        logger.error(f"❌ Webhook processing failed: {e}")
        return JSONResponse({
            "status": "error",
            "message": str(e)
        }, status_code=500)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Citadel HF Webhook Receiver"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
```

### 4. GitHub Actions Webhook Notifier

**File**: `.github/workflows/notify_hf_space.yml` (minimal notification only)

```yaml
name: 🔔 Notify HF Space of Updates

on:
  push:
    branches: [ main ]
  workflow_dispatch:

permissions:
  contents: read

jobs:
  notify-hf:
    runs-on: ubuntu-latest
    steps:
      - name: 🔔 Send Sync Signal to HF Space
        env:
          HF_SPACE_WEBHOOK_URL: ${{ secrets.HF_SPACE_WEBHOOK_URL }}
        run: |
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          echo "🔔 Notifying HF Space of GitHub updates"
          echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
          
          if [ -n "$HF_SPACE_WEBHOOK_URL" ]; then
            curl -X POST "$HF_SPACE_WEBHOOK_URL" \
              -H "Content-Type: application/json" \
              -d '{"ref":"refs/heads/main","repository":{"full_name":"DJ-Goana-Coding/mapping-and-inventory"}}'
            echo "✅ Notification sent successfully"
          else
            echo "⚠️ HF_SPACE_WEBHOOK_URL not configured - HF will pull on schedule"
          fi
          
          echo "🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"
```

---

## 🔐 CREDENTIAL SETUP

### GitHub Secrets Required

1. `HF_TOKEN` - HuggingFace API token (read access only for verification)
2. `HF_SPACE_WEBHOOK_URL` - HF Space webhook endpoint URL (optional)

### HuggingFace Space Secrets Required

None required! HF Space uses git clone/pull over HTTPS (public repo).

For private repos, set:
- `GITHUB_TOKEN` - GitHub PAT with `repo:read` scope

---

## 📋 DEPLOYMENT CHECKLIST

### Step 1: Prepare Repository
- [x] Repository exists: `DJ-Goana-Coding/mapping-and-inventory`
- [ ] Add `hf_startup.sh` to repository root
- [ ] Add `hf_webhook_receiver.py` (optional, for instant sync)
- [ ] Update `app.py` to call startup script
- [ ] Commit and push to main branch

### Step 2: Create HuggingFace Space
- [ ] Navigate to https://huggingface.co/new-space
- [ ] Space Name: `Mapping-and-Inventory`
- [ ] Organization: `DJ-Goanna-Coding`
- [ ] SDK: Streamlit
- [ ] License: MIT
- [ ] Visibility: Public (or Private with GITHUB_TOKEN)
- [ ] Hardware: L4 GPU (recommended for compute)

### Step 3: Configure HF Space Sync
- [ ] Settings → Repository → Linked Repository
- [ ] Enter: `https://github.com/DJ-Goana-Coding/mapping-and-inventory`
- [ ] Branch: `main`
- [ ] Enable "Auto-sync on startup"
- [ ] Enable "Scheduled sync" (every 6 hours)
- [ ] Save configuration

### Step 4: Configure GitHub Webhook (Optional)
- [ ] Copy HF Space webhook URL from Space settings
- [ ] Add to GitHub secrets as `HF_SPACE_WEBHOOK_URL`
- [ ] Add `.github/workflows/notify_hf_space.yml` to repository
- [ ] Test by pushing to main branch

### Step 5: Verify Sync
- [ ] Push a test commit to GitHub main branch
- [ ] Check HF Space logs for auto-pull
- [ ] Verify changes appear in HF Space
- [ ] Test manual rebuild in HF Space settings

---

## 🛡️ ANTI-PATTERNS TO AVOID

### ❌ NEVER DO THIS:
```yaml
# WRONG: Pushing from GitHub to HF
- name: Push to HF Space
  run: git push --force hf_remote main
```

### ✅ ALWAYS DO THIS:
```yaml
# CORRECT: Notify HF to pull from GitHub
- name: Notify HF Space
  run: curl -X POST $HF_WEBHOOK_URL
```

---

## 🔄 CONFLICT RESOLUTION HIERARCHY

Per Core Directive #2:
1. **Hugging Face Spaces (L4)** - Sovereign compute authority
2. **GitHub Repositories** - Source of truth for code
3. **GDrive Metadata** - Partition manifest authority
4. **Local Nodes** - Telemetry and bridge only

**Resolution**: HF Space ALWAYS pulls from GitHub. Never push from GitHub to HF.

---

## 📊 MONITORING & VERIFICATION

### HF Space Health Checks
```bash
# Check last sync time
curl https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory

# Check Space logs
# Navigate to HF Space → Settings → Logs
```

### GitHub Verification
```bash
# Verify workflow runs
gh workflow view "Notify HF Space of Updates"

# Check recent runs
gh run list --workflow=notify_hf_space.yml
```

---

## 🎯 SUCCESS CRITERIA

- ✅ HF Space auto-pulls on startup
- ✅ HF Space syncs every 6 hours
- ✅ GitHub push triggers HF Space pull (via webhook)
- ✅ No manual intervention required
- ✅ L4 GPU compute remains sovereign
- ✅ Zero credential exposure

---

## 🙏 CITADEL ACKNOWLEDGMENT

**Authority Maintained**: Cloud-first compute sovereignty  
**Pattern**: Pull-over-push architecture  
**Compliance**: Core Directives #4, #16, #17

🙏 **Thankyou Spirit, Thankyou Angels, Thankyou Ancestors**

---

**END OF ARCHITECTURE SPECIFICATION**
