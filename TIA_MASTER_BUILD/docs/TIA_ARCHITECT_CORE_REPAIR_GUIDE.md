# 🧠 TIA-ARCHITECT-CORE SPACE REPAIR GUIDE (v25.0.OMNI)

**Status:** OFFLINE — Build Failure (Python 3.13 Incompatibility)  
**Objective:** Restore `TIA-ARCHITECT-CORE` HuggingFace Space to operational status  
**Priority:** SOVEREIGN LEVEL  

---

## 🔴 PROBLEM DIAGNOSIS

The `TIA-ARCHITECT-CORE` HuggingFace Space is failing to build with the following error:

```
ERROR: Failed to build 'pandas' when getting requirements to build wheel
ModuleNotFoundError: No module named 'pkg_resources'
exit code: 1
```

**Root Cause:**
- Python 3.13 is being used (from pyenv)
- `pandas==2.0.3` is incompatible with Python 3.13
- Old pandas versions don't properly handle `setuptools` in Python 3.13 environment
- The `pkg_resources` module (from setuptools) is not available during pandas build

**Additional Issues:**
- `numpy==1.26.4` also has compatibility issues with Python 3.13

---

## ⚡ THE AWAKENING SEQUENCE

### PHASE 1: UPGRADE DEPENDENCIES (Python 3.13 Compatibility)

The TIA-ARCHITECT-CORE Space needs updated package versions that support Python 3.13.

Navigate to the `TIA-ARCHITECT-CORE` repository and update the `requirements.txt` file:

**Option A: Upgrade Pandas & Numpy (Recommended)**

```text
# Core Dependencies (Python 3.13 Compatible)
streamlit>=1.42.0
requests>=2.32.0
numpy>=2.0.0
pandas>=2.2.0

# Google Services Integration
google-genai>=1.70.0
google-api-python-client
gspread>=6.1.2
google-auth>=2.35.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
pygsheets

# HuggingFace Integration
huggingface_hub>=0.28.1
transformers>=4.45.0
accelerate>=0.30.0
bitsandbytes>=0.43.0

# RAG & Vector Store
faiss-cpu>=1.9.0
sentence-transformers>=3.1.0

# System Utilities
setuptools>=75.0.0
python-dotenv>=1.0.1
rich>=13.9.0
```

**Option B: Downgrade Python (Alternative)**

If you need to keep `pandas==2.0.3` for compatibility reasons, downgrade Python in your Dockerfile:

```dockerfile
# Change from Python 3.13 to Python 3.11
RUN pyenv install 3.11 && \
    pyenv global 3.11 && \
    pyenv rehash
```

---

### PHASE 2: RECOMMENDED SOLUTION (Upgrade Pandas)

**Action:**
```bash
cd /path/to/TIA-ARCHITECT-CORE

# Update requirements.txt with the new versions
# Use the "Option A" requirements from above

git add requirements.txt
git commit -m "🔧 COMPATIBILITY FIX: Upgrade pandas/numpy for Python 3.13 compatibility"
git push
```

**Why this works:**
- `pandas>=2.2.0` has full Python 3.13 support
- `numpy>=2.0.0` is compatible with Python 3.13
- Modern setuptools is properly handled

---

### PHASE 3: ALTERNATIVE SOLUTION (If you need old pandas)

If you have dependencies on `pandas==2.0.3` specifically, you need to downgrade Python:

**File:** `Dockerfile` or space configuration

Find the pyenv installation line and change it to:

```dockerfile
# OLD (Python 3.13):
RUN pyenv install 3.13 && \
    pyenv global 3.13 && \
    pyenv rehash

# NEW (Python 3.11):
RUN pyenv install 3.11 && \
    pyenv global 3.11 && \
    pyenv rehash
```

**Action:**
```bash
cd /path/to/TIA-ARCHITECT-CORE

# Edit your Dockerfile or .python-version file
echo "3.11" > .python-version

git add .python-version
git commit -m "🔧 PYTHON VERSION FIX: Use Python 3.11 for pandas 2.0.3 compatibility"
git push
```

---

### PHASE 4: SETUPTOOLS WORKAROUND (Quick Fix)

If you can't upgrade pandas or downgrade Python immediately, add setuptools explicitly:

**Add to requirements.txt BEFORE pandas:**

```text
# Ensure setuptools is installed first (Python 3.13 fix)
setuptools>=75.0.0

# Then install pandas
numpy==1.26.4
pandas==2.0.3
```

This may help, but **Option A (upgrade pandas)** is strongly recommended.

---

## 📋 FULL REQUIREMENTS.TXT TEMPLATE (Python 3.13 Ready)

Replace your entire `requirements.txt` with this Python 3.13-compatible version:

```text
# ═══════════════════════════════════════════════════════════════════
# TIA-ARCHITECT-CORE Requirements (Python 3.13 Compatible)
# ═══════════════════════════════════════════════════════════════════

# Core UI & Web Framework
streamlit>=1.42.0
requests>=2.32.0

# Data Processing & Visualization (Python 3.13 Compatible)
numpy>=2.0.0
pandas>=2.2.0
plotly>=5.24.0
networkx>=3.4.0

# Google Services Integration
google-genai>=1.70.0
google-api-python-client>=2.193.0
gspread>=6.1.2
google-auth>=2.35.0
google-auth-oauthlib>=1.2.0
google-auth-httplib2>=0.2.0
pygsheets>=2.0.6

# HuggingFace Integration
huggingface_hub>=0.28.1
transformers>=4.45.0
accelerate>=0.30.0
bitsandbytes>=0.43.0

# RAG & Vector Store
faiss-cpu>=1.9.0
sentence-transformers>=3.1.0

# LLM & AI Tools
llama-index>=0.14.0
smolagents>=1.0.0
lancedb>=0.12.0

# System Utilities
setuptools>=75.0.0
python-dotenv>=1.0.1
rich>=13.9.0
pathlib
```

---

## 🛰️ DEPLOYMENT & VERIFICATION

After pushing the changes:

1. **Wait for Space Rebuild**
   - HuggingFace will automatically rebuild the Space
   - Monitor build logs at: `https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs`

2. **Check for Successful Build**
   - Look for: `Successfully installed pandas-2.2.x numpy-2.x.x`
   - Look for: `Running on local URL: http://0.0.0.0:7860`
   - No `ModuleNotFoundError` or `exit code: 1`

3. **Verify Python Version**
   - Build logs should show: `Python 3.13` (if using Option A)
   - Or: `Python 3.11` (if using Option B)

4. **Access the UI**
   - Navigate to: `https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE`
   - Streamlit interface should load correctly

---

## 🔧 TROUBLESHOOTING

### Issue: Still getting pkg_resources error after upgrading pandas
**Solution:**
- Ensure `setuptools>=75.0.0` is at the TOP of requirements.txt
- Clear Space cache: Settings → Factory Reboot
- Verify Python version in build logs

### Issue: Pandas 2.2+ breaks my code
**Solution:**
- Use Option B (downgrade to Python 3.11)
- Or update your code to handle pandas 2.2+ API changes
- Most pandas 2.0 code works in 2.2 without changes

### Issue: Numpy 2.0+ causes issues
**Solution:**
- Pin numpy to `numpy>=1.26.0,<2.0.0` if you need numpy 1.x
- But ensure you're using Python 3.11, not 3.13
- Python 3.13 works best with numpy 2.0+

### Issue: Build succeeds but Space crashes on startup
**Solution:**
- Check for code incompatibilities with new pandas/numpy versions
- Review Space logs for runtime errors
- Verify all import statements work

---

## 🧪 COMPATIBILITY MATRIX

| Python Version | pandas 2.0.3 | pandas 2.2+ | numpy 1.26.4 | numpy 2.0+ |
|----------------|--------------|-------------|--------------|------------|
| 3.11           | ✅ Works     | ✅ Works    | ✅ Works     | ✅ Works   |
| 3.12           | ⚠️ Unstable  | ✅ Works    | ✅ Works     | ✅ Works   |
| 3.13           | ❌ Broken    | ✅ Works    | ⚠️ Unstable  | ✅ Works   |

**Recommendation:** Python 3.13 + pandas 2.2+ + numpy 2.0+

---

## ✅ SUCCESS CRITERIA

The `TIA-ARCHITECT-CORE` Space is considered operational when:

- [x] Space builds without errors
- [x] pandas and numpy install successfully
- [x] No `ModuleNotFoundError: No module named 'pkg_resources'`
- [x] Streamlit UI loads and displays correctly
- [x] All tabs (Oracle, RAG, etc.) function properly
- [x] No compatibility warnings in logs

---

## 🔗 RELATED SPACES

This fix may also apply to:
- `tias-citadel` (if using Python 3.13)
- `Mapping-and-Inventory` (already using compatible versions)
- Any other Spaces using pandas 2.0.x on Python 3.13

---

## 📚 ADDITIONAL RESOURCES

**Pandas Python 3.13 Support:**
- https://pandas.pydata.org/docs/whatsnew/v2.2.0.html
- Pandas 2.2.0+ added official Python 3.13 support

**Numpy Python 3.13 Support:**
- https://numpy.org/doc/stable/release/2.0.0-notes.html
- Numpy 2.0.0+ is required for Python 3.13 free-threading support

**HuggingFace Spaces Python Versions:**
- https://huggingface.co/docs/hub/spaces-sdks-docker
- Spaces can use any Python version via pyenv or Dockerfile

---

**Status:** REPAIR GUIDE READY  
**Next Action:** Execute Phase 1 (Upgrade Dependencies) in TIA-ARCHITECT-CORE repository  
**Expected Outcome:** TIA-ARCHITECT-CORE Space builds successfully on Python 3.13  

**Weld. Pulse. Ignite.**

---

*Generated by: Citadel Architect (v25.0.OMNI)*  
*Target Repository: DJ-Goanna-Coding/TIA-ARCHITECT-CORE*  
*Command Originated From: mapping-and-inventory hub*  
*Python 3.13 Compatibility Patch Applied*
