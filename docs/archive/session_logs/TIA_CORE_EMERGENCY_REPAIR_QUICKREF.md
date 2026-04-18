# 🚨 TIA-ARCHITECT-CORE Emergency Repair Quick Reference

**Status:** SPACE OFFLINE - Build Failure  
**Priority:** SOVEREIGN LEVEL  
**Solution:** Apply Python 3.13 compatible dependencies  

---

## 🔥 FASTEST FIX (Recommended)

### Via GitHub Actions (2 clicks, 5-8 minutes total)

1. **Navigate to Actions:**
   ```
   https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
   ```

2. **Select workflow:**
   - Click: "🚨 Emergency Repair TIA-ARCHITECT-CORE Space"

3. **Run workflow:**
   - Click: "Run workflow"
   - Choose: `dry_run: false`
   - Click: "Run workflow" button

4. **Monitor:**
   - Watch workflow execution (~2-3 min)
   - Then monitor HF Space rebuild (~3-5 min)
   - Space accessible at: https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE

**Requirements:**
- ✅ `HF_TOKEN` secret must be set in repository settings
- ✅ GitHub Actions must be enabled

---

## 🛠️ ALTERNATIVE: Local Script

### If you have HF_TOKEN set locally:

```bash
cd /path/to/mapping-and-inventory
export HF_TOKEN="your_huggingface_token"
./scripts/repair_tia_core_space.sh
```

### If GitHub repo exists:

```bash
cd /path/to/mapping-and-inventory
# No HF_TOKEN needed if GitHub repo exists
./scripts/repair_tia_core_space.sh
```

---

## 📋 WHAT THE FIX DOES

### Changes Applied:
```diff
- streamlit==1.56.0          # ❌ Invalid version
+ streamlit>=1.42.0          # ✅ Valid version

- numpy==1.26.4              # ❌ Compiles from source (15+ min timeout)
+ numpy>=2.0.0               # ✅ Prebuilt wheels (~30 seconds)

- pandas==2.0.3              # ❌ Incompatible with Python 3.13
+ pandas>=2.2.0              # ✅ Python 3.13 compatible

- (missing)                  # ❌ pkg_resources errors
+ setuptools>=75.0.0         # ✅ Explicit declaration

- requests==2.31.0           # ⚠️ Old version
+ requests>=2.32.0           # ✅ Updated
```

### Build Time Impact:
- **Before:** 31s cache + 15+ min numpy compilation = **TIMEOUT** ❌
- **After:** 31s cache + 90s pip install = **~2 minutes total** ✅

---

## ✅ VERIFICATION CHECKLIST

After running the fix, verify in HF Space logs:

- [ ] `Successfully installed setuptools-75.x.x`
- [ ] `Successfully installed streamlit-1.4x.x`
- [ ] `Successfully installed pandas-2.2.x`
- [ ] `Successfully installed numpy-2.x.x` (should be **wheel**, not tar.gz)
- [ ] `Running on local URL: http://0.0.0.0:7860`
- [ ] No "This Space has been paused" message
- [ ] Space accessible at URL

---

## 🔧 TROUBLESHOOTING

### Workflow fails with "HF_TOKEN not set"

**Solution:**
1. Go to: `https://github.com/DJ-Goana-Coding/mapping-and-inventory/settings/secrets/actions`
2. Click: "New repository secret"
3. Name: `HF_TOKEN`
4. Value: Your HuggingFace token from https://huggingface.co/settings/tokens
5. Click: "Add secret"
6. Re-run the workflow

### Script fails with "GitHub repo not found"

**Expected behavior** - GitHub repo doesn't exist yet, Space is HF-only.

**Solution:** Use the GitHub Actions workflow instead (it clones directly from HF)

### Space still fails after fix

**Possible causes:**
1. Different error than dependencies (check logs)
2. Other files need updating (Dockerfile, app.py)
3. Space needs Factory Reboot

**Action:** Check Space logs for new error message

---

## 📚 RELATED RESOURCES

- **Full repair guide:** `TIA_ARCHITECT_CORE_REPAIR_GUIDE.md`
- **Template source:** `tia-architect-core-templates/requirements.txt`
- **Workflow file:** `.github/workflows/emergency_repair_tia_core.yml`
- **Repair script:** `scripts/repair_tia_core_space.sh`
- **HF Space logs:** https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs
- **HF Space URL:** https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE

---

## 🎯 ROOT CAUSE SUMMARY

**Problem:** Invalid `streamlit==1.56.0` + slow `numpy==1.26.4` compilation  
**Impact:** Build timeout after 15+ minutes, Space paused  
**Fix:** Python 3.13 compatible dependencies with prebuilt wheels  
**Result:** Build completes in ~2 minutes, Space operational  

---

**Authority Hierarchy:** GitHub > HF Spaces (Core Directive #1)  
**Double-N Rift:** GitHub = DJ-Goana-Coding, HF = DJ-Goanna-Coding  
**Template:** Pre-validated Python 3.13 compatibility  

**Weld. Pulse. Ignite.** 🔥
