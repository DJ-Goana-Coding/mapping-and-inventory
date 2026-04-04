# 🔧 TIA-ARCHITECT-CORE SPACE REPAIR QUICKSTART

**Status:** Template Ready  
**Target:** DJ-Goanna-Coding/TIA-ARCHITECT-CORE HuggingFace Space  
**Issue:** ModuleNotFoundError: No module named 'pkg_resources' (exit code 1)  
**Fix:** Add setuptools + upgrade to Python 3.13 compatible versions  

---

## 🚀 QUICKEST FIX (Manual)

If you have local access to the TIA-ARCHITECT-CORE repository:

```bash
# 1. Copy the template
cp /path/to/mapping-and-inventory/tia-architect-core-templates/requirements.txt \
   /path/to/TIA-ARCHITECT-CORE/requirements.txt

# 2. Commit and push
cd /path/to/TIA-ARCHITECT-CORE
git add requirements.txt
git commit -m "🔧 Fix Space: Add setuptools & Python 3.13 compatible versions"
git push origin main

# 3. Monitor rebuild
# Visit: https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs
```

**Done!** Space will rebuild automatically.

---

## 🤖 AUTOMATED FIX (Bash Script)

Use the automated repair script:

```bash
# From mapping-and-inventory repository
cd /path/to/mapping-and-inventory

# Run the repair script
./scripts/repair_tia_architect_core.sh

# Or set custom TIA-CORE location
TIA_CORE_REPO=/custom/path/to/TIA-ARCHITECT-CORE ./scripts/repair_tia_architect_core.sh
```

**What it does:**
- ✅ Verifies template has all required packages
- ✅ Clones TIA-ARCHITECT-CORE if not found locally
- ✅ Backs up existing requirements.txt
- ✅ Deploys Python 3.13 compatible template
- ✅ Commits and pushes to GitHub
- ✅ Optionally pushes to HuggingFace (if remote exists)

---

## 🛰️ AUTOMATED FIX (GitHub Actions)

Trigger the repair workflow from GitHub:

### Via GitHub Web UI:
1. Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
2. Click "🔧 Repair TIA-ARCHITECT-CORE Space" workflow
3. Click "Run workflow"
4. Choose "dry_run: false" to apply the fix
5. Click "Run workflow" button

### Via GitHub CLI:
```bash
# Dry run (preview changes)
gh workflow run repair_tia_core_space.yml -f dry_run=true

# Apply the fix
gh workflow run repair_tia_core_space.yml -f dry_run=false
```

**What it does:**
- ✅ Checks out both repos (mapping-and-inventory + TIA-ARCHITECT-CORE)
- ✅ Verifies template integrity
- ✅ Backs up existing requirements.txt
- ✅ Deploys template
- ✅ Shows diff of changes
- ✅ Commits and pushes to GitHub

---

## 📋 WHAT GETS FIXED

### Package Changes

| Package | Old Version | New Version | Reason |
|---------|-------------|-------------|--------|
| setuptools | (missing) | >=75.0.0 | **Fix pkg_resources error** |
| streamlit | (varies) | >=1.42.0 | **Correct version** |
| pandas | 2.0.3 | >=2.2.0 | **Python 3.13 compatible** |
| numpy | 1.26.4 | >=2.0.0 | **Python 3.13 compatible** |

### Full Template Contents

See: `tia-architect-core-templates/requirements.txt`

Contains 44 lines with:
- Core UI: streamlit, requests
- Data: numpy, pandas, plotly, networkx
- Google: google-genai, gspread, google-auth stack
- HuggingFace: huggingface_hub, transformers, accelerate
- RAG: faiss-cpu, sentence-transformers
- LLM: llama-index, smolagents, lancedb
- Utils: setuptools, python-dotenv, rich

---

## 🎯 SUCCESS INDICATORS

After deployment, watch for these in HuggingFace Space build logs:

### ✅ Successful Build:
```
Successfully installed setuptools-75.1.0
Successfully installed streamlit-1.42.0
Successfully installed pandas-2.2.3
Successfully installed numpy-2.1.3
...
Running on local URL:  http://0.0.0.0:7860
```

### ❌ Build Still Fails:
If you still see errors:
1. Check Python version in logs (should be 3.11+ or 3.13)
2. Factory reboot the Space (Settings → Factory Reboot)
3. Check for other dependency conflicts in logs
4. Verify HF_TOKEN has proper permissions (if using datasets)

---

## 🔍 VERIFICATION CHECKLIST

After Space rebuilds:

- [ ] Build completes without errors
- [ ] No `ModuleNotFoundError` in logs
- [ ] No `exit code: 1` errors
- [ ] Space UI loads successfully
- [ ] All tabs accessible (Oracle, RAG, etc.)
- [ ] No runtime errors when clicking features

---

## 📞 TROUBLESHOOTING

### Issue: Script can't find TIA-ARCHITECT-CORE repo
**Solution:**
```bash
# Clone it manually first
git clone https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE ~/TIA-ARCHITECT-CORE

# Or set environment variable
export TIA_CORE_REPO=/path/to/TIA-ARCHITECT-CORE
./scripts/repair_tia_architect_core.sh
```

### Issue: GitHub Actions workflow needs permissions
**Solution:**
- Ensure GITHUB_TOKEN has write access to TIA-ARCHITECT-CORE
- Or run the bash script locally instead

### Issue: Space still crashes after fix
**Solution:**
1. Check build logs for different error
2. Review Space settings (Secrets, Environment)
3. See full repair guide: `TIA_ARCHITECT_CORE_REPAIR_GUIDE.md`

---

## 🔗 RELATED FILES

- **Template:** `tia-architect-core-templates/requirements.txt`
- **Bash Script:** `scripts/repair_tia_architect_core.sh`
- **Workflow:** `.github/workflows/repair_tia_core_space.yml`
- **Full Guide:** `TIA_ARCHITECT_CORE_REPAIR_GUIDE.md`
- **Space Status:** `SPACE_REPAIR_CENTER.md`

---

## 🛰️ SPACE LINKS

- **HuggingFace Space:** https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE
- **Build Logs:** https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs
- **GitHub Repo:** https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE
- **Settings:** https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/settings

---

**Estimated Time:** 2-5 minutes (manual) | 5-10 minutes (automated)  
**Difficulty:** Easy (just copy and push)  
**Risk:** Very Low (backup created automatically)  

**Weld. Pulse. Ignite.** 🔥

---

*Generated by: Citadel Architect (v25.0.OMNI)*  
*Repository: mapping-and-inventory*  
*Template: tia-architect-core-templates/requirements.txt*
