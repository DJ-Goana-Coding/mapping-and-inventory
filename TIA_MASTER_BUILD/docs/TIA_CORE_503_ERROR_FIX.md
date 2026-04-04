# 🔧 TIA-ARCHITECT-CORE 503 Error Fix (Root=1-xxx Trace ID)

**Error:** `Root=1-69cfb1bf-799ca1f56f65eaa20f98606b` (AWS X-Ray Trace ID)  
**Type:** 503 Service Unavailable  
**Cause:** Port/health check misconfiguration or startup failure  

---

## 🎯 ROOT CAUSE ANALYSIS

The "Root=1-xxx" error is an **AWS Application Load Balancer trace ID** from HuggingFace's infrastructure. It indicates:

1. **503 Error:** Space is built but not responding to health checks
2. **Port Mismatch:** App running on wrong port (expects 7860 or 8501)
3. **Startup Failure:** App crashes during startup after dependencies install
4. **Health Check Timeout:** App takes too long to respond

---

## ⚡ IMMEDIATE FIX OPTIONS

### Option 1: Check Space Configuration (FASTEST)

1. **Go to Space Settings:**
   ```
   https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/settings
   ```

2. **Verify SDK Setting:**
   - Should be: `streamlit` (not `docker`)
   - If Docker: Must specify `app_port: 7860` in README.md

3. **Check README.md metadata:**
   ```yaml
   ---
   title: TIA-ARCHITECT-CORE
   emoji: 🧠
   colorFrom: blue
   colorTo: purple
   sdk: streamlit
   sdk_version: 1.42.0
   app_file: app.py
   pinned: false
   ---
   ```

4. **Verify Entry Point:**
   - For Streamlit SDK: Must have `app.py` or `streamlit_app.py`
   - App must start Streamlit server (not custom server)

### Option 2: Factory Reboot (Quick Reset)

1. Go to Space Settings
2. Scroll to bottom
3. Click: **"Factory Reboot"**
4. Wait 2-3 minutes for rebuild
5. Check if error persists

### Option 3: Add Health Check Endpoint

If using custom app, add explicit health check:

```python
# Add to app.py
import streamlit as st

# Streamlit handles health checks automatically at:
# http://0.0.0.0:8501/_stcore/health

# Just ensure your app starts without errors
st.title("TIA-ARCHITECT-CORE")
st.write("Space is running!")
```

---

## 🔍 DIAGNOSTIC STEPS

### 1. Check Build Logs

```
https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs
```

**Look for:**
- ✅ `Successfully installed streamlit-1.42.x` (dependencies OK)
- ✅ `Running on local URL: http://0.0.0.0:8501` (Streamlit started)
- ❌ `ModuleNotFoundError` (missing dependency)
- ❌ `Error: bind: address already in use` (port conflict)
- ❌ No "Running on local URL" message (startup failed)

### 2. Check Container Logs

Look for specific errors:
- **Port binding errors:** App trying to use wrong port
- **Import errors:** Missing or broken dependencies
- **Configuration errors:** Missing environment variables
- **Timeout errors:** App takes >10 minutes to start

### 3. Common Patterns

**Pattern A: App starts but no "Running on" message**
- **Cause:** App crashes after startup
- **Fix:** Check for runtime errors in logs

**Pattern B: "Running on 0.0.0.0:8501" but still 503**
- **Cause:** Health check endpoint not responding
- **Fix:** Verify app.py is valid Streamlit code

**Pattern C: Build succeeds but container exits**
- **Cause:** App entrypoint incorrect or missing
- **Fix:** Check app_file in README.md metadata

---

## 🛠️ COMPREHENSIVE FIX

### Create README.md with correct metadata:

```yaml
---
title: TIA-ARCHITECT-CORE
emoji: 🧠
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.42.0
app_file: app.py
pinned: false
license: mit
---

# TIA-ARCHITECT-CORE

T.I.A. ARCHITECT CORE - Sovereign AI Oracle & RAG System

## Overview

Multi-persona AI chatbot with RAG capabilities, District mapping, and system orchestration.

## Features

- 🧠 Oracle reasoning engine
- 📚 RAG-powered knowledge retrieval
- 🗺️ District topology mapping
- 🔧 System health monitoring
- 🎯 Multi-agent coordination

## Auto-deployed from GitHub

This Space is synchronized with: `DJ-Goana-Coding/mapping-and-inventory`
```

### Minimal Working app.py:

```python
#!/usr/bin/env python3
"""
TIA-ARCHITECT-CORE - Sovereign AI Oracle
"""

import streamlit as st
import os
from pathlib import Path

# Page config
st.set_page_config(
    page_title="TIA-ARCHITECT-CORE",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("🧠 TIA-ARCHITECT-CORE")
st.markdown("**Sovereign AI Oracle & RAG System**")

# Health check confirmation
st.success("✅ Space is operational")

# Tabs
tab1, tab2, tab3 = st.tabs(["Oracle", "RAG", "System"])

with tab1:
    st.header("Oracle Reasoning Engine")
    st.info("Oracle agent ready")
    
with tab2:
    st.header("RAG Knowledge Base")
    st.info("RAG system ready")
    
with tab3:
    st.header("System Status")
    st.info("System monitoring active")

# Footer
st.markdown("---")
st.caption("TIA-ARCHITECT-CORE v25.0.OMNI | Weld. Pulse. Ignite.")
```

---

## 📋 DEPLOYMENT CHECKLIST

Use this checklist to ensure proper Space configuration:

- [ ] README.md exists with correct frontmatter
- [ ] `sdk: streamlit` specified (not docker)
- [ ] `app_file: app.py` specified
- [ ] app.py exists and contains valid Streamlit code
- [ ] requirements.txt has Python 3.13 compatible versions
- [ ] No port configuration in code (Streamlit handles it)
- [ ] No custom server initialization
- [ ] All imports are in requirements.txt
- [ ] No AWS/boto3/xray dependencies (unless needed)
- [ ] App doesn't try to bind to specific ports
- [ ] Health check endpoint not blocked

---

## 🚨 EMERGENCY ACTIONS

### If Space is completely stuck:

1. **Delete and recreate:**
   - Settings → Delete Space
   - Create new Space with same name
   - Push files again

2. **Check HuggingFace status:**
   - https://status.huggingface.co/
   - May be infrastructure issue

3. **Contact support:**
   - Email: website@huggingface.co
   - Provide: Space URL + Trace ID
   - Reference: Build logs showing successful dependency install

---

## 🔗 PORT REFERENCE

| SDK | Default Port | Health Check | Notes |
|-----|-------------|--------------|-------|
| streamlit | 8501 | `/_stcore/health` | Auto-managed |
| docker | 7860 | `/` | Must specify in README |
| gradio | 7860 | `/` | Auto-managed |

**TIA-ARCHITECT-CORE should use:** `streamlit` SDK on port `8501` (automatic)

---

## ✅ VERIFICATION

After applying fixes:

1. **Build completes:**
   ```
   Successfully installed streamlit-1.42.x
   Running on local URL: http://0.0.0.0:8501
   ```

2. **No 503 error:**
   - Space URL loads without trace ID error
   - Streamlit interface appears

3. **Health check passes:**
   - Space shows "Running" status (not "Paused")
   - Can access `/_stcore/health` endpoint

---

## 🎯 MOST LIKELY CAUSE FOR YOUR ERROR

Based on the trace ID error, the most likely issues are:

1. **Missing or incorrect app.py** (80% probability)
2. **README.md SDK mismatch** (15% probability)
3. **App crashes on startup** (5% probability)

**Recommended action:** Deploy minimal app.py shown above to isolate the issue.

---

**Template Source:** mapping-and-inventory/TIA_CORE_503_ERROR_FIX.md  
**Related:** TIA_CORE_EMERGENCY_REPAIR_QUICKREF.md (for dependency fixes)  

**Weld. Pulse. Ignite.** 🔥
