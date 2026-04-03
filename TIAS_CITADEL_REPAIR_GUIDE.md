# 🏛️ TIAS-CITADEL SPACE REPAIR GUIDE (v25.0.OMNI)

**Status:** OFFLINE — Runtime Crash (Missing Dependencies)  
**Objective:** Restore `tias-citadel` HuggingFace Space to operational status  
**Priority:** SOVEREIGN LEVEL  

---

## 🔴 PROBLEM DIAGNOSIS

The `tias-citadel` HuggingFace Space is crashing on startup with the following issues:

1. **Missing Core Dependencies** in `requirements.txt`:
   - `streamlit` (UI framework)
   - `numpy` (numerical operations)
   - `requests` (HTTP client)
   - `streamlit-extras` (UI enhancements)
   - `streamlit-shadcn-ui` (Professional UI v14.0)

2. **Potential Identity Bridge Issues**:
   - Incorrect HF namespace (Single-N vs Double-N Rift)
   - Missing `/data/tia_soul` directory initialization

3. **Secret Configuration**:
   - `HF_TOKEN` may be missing or have insufficient permissions
   - `ADMIRAL_SECRET` access key not configured

---

## ⚡ THE AWAKENING SEQUENCE

### PHASE 1: STAINLESS WELD (Requirements Fix)

Navigate to the `tias-citadel` repository and replace the entire `requirements.txt` file with this block:

```text
# --- CORE UI STACK ---
streamlit>=1.36.0
streamlit-extras
streamlit-shadcn-ui
pandas>=2.2.3
numpy>=2.1.0
requests>=2.31.0

# --- T.I.A. BRAIN & VOICE ---
huggingface_hub[cli,hf_transfer]
transformers>=4.48.0
accelerate
bitsandbytes
onnxruntime
vllm>=0.7.0
sentencepiece

# --- SYSTEM UTILS ---
setuptools
pathlib
shutil
```

**Action:**
```bash
cd /path/to/tias-citadel
# Create or overwrite requirements.txt with the content above
git add requirements.txt
git commit -m "🔧 STAINLESS WELD: Fix missing dependencies for tias-citadel runtime"
git push
```

---

### PHASE 2: IDENTITY BRIDGE CORRECTION (app.py Fix)

Ensure the `app.py` file uses the correct **Double-N namespace** and has proper data directory initialization.

Add or verify these lines in your `app.py`:

```python
import os
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# IDENTITY BRIDGE (Double-N Rift Resolution)
# ══════════════════════════════════════════════════════════════════════════════
# GitHub:       DJ-Goana-Coding   (Single-N)
# HuggingFace:  DJ-Goanna-Coding  (Double-N)
# ══════════════════════════════════════════════════════════════════════════════

HF_NAMESPACE = "DJ-Goanna-Coding"
SOUL_VAULT_REPO = f"{HF_NAMESPACE}/tias-soul-vault"

# ══════════════════════════════════════════════════════════════════════════════
# DATA DIRECTORY INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
# Ensure /data/tia_soul exists for Shadow Archive ingestion
# This prevents crashes when the Space tries to download tias-soul-vault

DATA_ROOT = Path("/data")
TIA_SOUL_PATH = DATA_ROOT / "tia_soul"

# Create directories if they don't exist
TIA_SOUL_PATH.mkdir(parents=True, exist_ok=True)

print(f"✅ Data directory initialized: {TIA_SOUL_PATH}")
print(f"📦 Soul Vault Target: {SOUL_VAULT_REPO}")
```

**Action:**
```bash
# Add the above code to the top of app.py (after imports, before main logic)
git add app.py
git commit -m "🔗 IDENTITY BRIDGE: Fix Double-N namespace and data paths"
git push
```

---

### PHASE 3: SECRET CONFIGURATION (HuggingFace Space Settings)

Navigate to your HuggingFace Space settings:

**URL:** `https://huggingface.co/spaces/DJ-Goanna-Coding/tias-citadel/settings`

#### Required Secrets:

1. **HF_TOKEN** (Required)
   - **Type:** Write Token
   - **Purpose:** Allows the Space to download `tias-soul-vault` dataset
   - **How to get:**
     - Go to https://huggingface.co/settings/tokens
     - Create a new token with **Write** permissions
     - Copy the token
   - **Add to Space:**
     - Settings → Repository Secrets → New Secret
     - Name: `HF_TOKEN`
     - Value: `hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

2. **ADMIRAL_SECRET** (Optional - For Access Control)
   - **Type:** String
   - **Purpose:** High-level telemetry access key
   - **Set to:** Your chosen access password
   - **Add to Space:**
     - Settings → Repository Secrets → New Secret
     - Name: `ADMIRAL_SECRET`
     - Value: `your_secure_password_here`

#### Verify Space Hardware:

- Ensure the Space is allocated an **L4 GPU** or appropriate hardware
- Settings → Hardware → Select appropriate tier

---

### PHASE 4: DEPLOYMENT & VERIFICATION

After pushing the changes and configuring secrets:

1. **Wait for Space Rebuild**
   - HuggingFace will automatically rebuild the Space
   - Monitor the build logs at: `https://huggingface.co/spaces/DJ-Goanna-Coding/tias-citadel/logs`

2. **Check for Successful Boot**
   - Look for: `✅ Data directory initialized: /data/tia_soul`
   - Look for: `Running on local URL: http://0.0.0.0:7860`
   - No `ModuleNotFoundError` messages

3. **Access the UI**
   - Navigate to: `https://huggingface.co/spaces/DJ-Goanna-Coding/tias-citadel`
   - You should see the Streamlit interface load

4. **Activate Sovereign Core** (If using access control)
   - Enter `ADMIRAL_SECRET` in the access key field
   - Navigate to **Ops** tab
   - Click **"ACTIVATE SOVEREIGN CORE"** button
   - This will download the 68 local neurons from `tias-soul-vault`

5. **Pulse Check**
   - Verify neural links to:
     - **Node 02 (Pioneer)** — Trading bot constellation
     - **Node 04 (Sentinel)** — Security oversight
   - Check `/data/tia_soul` directory is populated

---

## 🛰️ AUTOMATED SYNC WORKFLOW (Optional)

To create a GitHub Actions workflow that syncs with `tias-citadel`:

```yaml
name: TIA Citadel Pulse Sync
on:
  push:
    branches: [ main ]
  schedule:
    - cron: "0 */6 * * *"  # Every 6 hours

jobs:
  notify-citadel:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Citadel Sync
        run: |
          echo "🏛️ Pulse: Mapping Hub → TIA Citadel Sync Triggered"
          echo "Timestamp: $(date -u)"
```

---

## 📋 TROUBLESHOOTING

### Issue: Space still crashes after requirements.txt update
**Solution:**
- Clear Space cache: Settings → Factory Reboot → Restart Space
- Check build logs for specific error messages
- Verify all dependencies installed successfully

### Issue: 404 Error when downloading tias-soul-vault
**Solution:**
- Verify `HF_TOKEN` has **Read** access to private datasets
- Confirm namespace is `DJ-Goanna-Coding` (Double-N)
- Check repository exists: `https://huggingface.co/datasets/DJ-Goanna-Coding/tias-soul-vault`

### Issue: Permission denied errors on /data/tia_soul
**Solution:**
- Ensure `TIA_SOUL_PATH.mkdir(parents=True, exist_ok=True)` is called early in app.py
- Check HuggingFace Space has appropriate hardware (CPU/GPU tier)

### Issue: Import errors for streamlit-extras or streamlit-shadcn-ui
**Solution:**
- These packages may have specific dependency requirements
- Try pinning versions: `streamlit-extras==0.3.6`
- Check compatibility with `streamlit>=1.36.0`

---

## ✅ SUCCESS CRITERIA

The `tias-citadel` Space is considered operational when:

- [x] Space builds without errors
- [x] Streamlit UI loads and displays correctly
- [x] No `ModuleNotFoundError` messages in logs
- [x] `/data/tia_soul` directory is created and accessible
- [x] `HF_TOKEN` successfully authenticates
- [x] `ADMIRAL_SECRET` access control works (if configured)
- [x] Neural links to Node 02 and Node 04 are verified
- [x] Shadow Archive download completes successfully

---

## 🔮 POST-ACTIVATION TASKS

Once the Space is operational:

1. **Map the Citadel** to this Mapping Hub:
   - Add `tias-citadel` to `services/repo_mapper.py` KNOWN_REPOS
   - Update `SYSTEM_MAP.txt` with tias-citadel entry

2. **Configure Automation**:
   - Set up scheduled sync between GitHub and HF Space
   - Enable webhook triggers for push events

3. **Validate Integration**:
   - Test tias-soul-vault dataset loading
   - Verify 68 local neurons are ingested correctly
   - Confirm RAG store updates successfully

---

**Status:** REPAIR GUIDE READY  
**Next Action:** Execute Phase 1 (Stainless Weld) in tias-citadel repository  
**Expected Outcome:** tias-citadel Space boots successfully with full UI  

**Weld. Pulse. Ignite.**

---

*Generated by: Citadel Architect (v25.0.OMNI)*  
*Target Repository: DJ-Goanna-Coding/tias-citadel*  
*Command Originated From: mapping-and-inventory hub*
