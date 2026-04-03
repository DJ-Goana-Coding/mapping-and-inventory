# 🏰 CITADEL MESH REPAIR CENTER (v25.0.OMNI)

**Central Command for HuggingFace Space Diagnostics & Recovery**

This repository contains complete repair guides and templates for all Citadel Omega Spaces.

---

## 🚨 CURRENT STATUS

### Mapping-and-Inventory (THIS SPACE)
- **Status:** ✅ **OPERATIONAL** (Fixed)
- **Issue:** Duplicate package versions causing build conflicts
- **Resolution:** Consolidated requirements.txt, removed duplicates
- **Space URL:** https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory

### tias-citadel
- **Status:** 🔴 **OFFLINE** (Runtime Crash)
- **Issue:** Missing core dependencies (streamlit, numpy, requests)
- **Resolution:** Apply repair templates from `tia-citadel-templates/`
- **Space URL:** https://huggingface.co/spaces/DJ-Goanna-Coding/tias-citadel
- **Repair Guide:** [TIAS_CITADEL_REPAIR_GUIDE.md](./TIAS_CITADEL_REPAIR_GUIDE.md)

### TIA-ARCHITECT-CORE
- **Status:** 🔴 **OFFLINE** (Build Failure)
- **Issue:** pandas 2.0.3 incompatible with Python 3.13 (pkg_resources error)
- **Resolution:** Upgrade pandas to 2.2+, numpy to 2.0+, add setuptools
- **Space URL:** https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE
- **Repair Guide:** [TIA_ARCHITECT_CORE_REPAIR_GUIDE.md](./TIA_ARCHITECT_CORE_REPAIR_GUIDE.md)

### tias-sentinel-scout-swarm-2
- **Status:** 🔴 **OFFLINE** (Build Failure)
- **Issue:** pandas-ta requires Python >=3.11, Space using Python 3.9
- **Resolution:** Upgrade to Python 3.11 + compatible pandas-ta version
- **Space URL:** https://huggingface.co/spaces/DJ-Goanna-Coding/tias-sentinel-scout-swarm-2
- **Template:** `sentinel-scout-templates/`

---

## 📁 REPAIR RESOURCES

### Documentation
- **[TIAS_CITADEL_REPAIR_GUIDE.md](./TIAS_CITADEL_REPAIR_GUIDE.md)** — Complete repair instructions for tias-citadel Space
- **[TIA_ARCHITECT_CORE_REPAIR_GUIDE.md](./TIA_ARCHITECT_CORE_REPAIR_GUIDE.md)** — Python 3.13 compatibility fix for TIA-ARCHITECT-CORE
- **[TIA_CORE_REPAIR_QUICKSTART.md](./TIA_CORE_REPAIR_QUICKSTART.md)** — Fast repair guide with 3 deployment methods
- **[SELF_HEALING_SYSTEM.md](./SELF_HEALING_SYSTEM.md)** — Autonomous script monitoring and repair system

### Template Files

#### tias-citadel-templates/
```
tia-citadel-templates/
├── requirements.txt       # Complete dependency manifest
├── app_py_header.py      # Identity Bridge & data initialization
└── README.md             # Quick deployment guide
```

**Quick Deploy:**
```bash
# Copy requirements.txt to tias-citadel repo
cp tia-citadel-templates/requirements.txt /path/to/tias-citadel/
# Add app_py_header.py content to top of app.py
# Configure HF_TOKEN secret in Space settings
# Push and rebuild
```

#### tia-architect-core-templates/
```
tia-architect-core-templates/
├── requirements.txt       # Python 3.13 compatible dependencies
└── README.md             # Compatibility guide
```

#### sentinel-scout-templates/
```
sentinel-scout-templates/
├── requirements.txt       # Python 3.11+ compatible (pandas-ta fix)
├── .python-version       # Python 3.11
└── README.md             # Compatibility guide
```

**Automated Deploy (ALL SPACES):**
```bash
# Option 1: Repair all spaces with one script
./scripts/repair_all_spaces.sh

# Option 2: Trigger GitHub Actions for all spaces
gh workflow run repair_all_spaces.yml -f spaces=all -f dry_run=false

# Option 3: Repair individual space
./scripts/repair_tia_architect_core.sh
# or
gh workflow run repair_tia_core_space.yml -f dry_run=false
```

---

## 🔧 COMMON ISSUES & SOLUTIONS

### Issue: Duplicate Package Versions
**Symptom:** `ERROR: Cannot install package==X.X and package==Y.Y`  
**Solution:** Consolidate to single version using `>=` constraints  
**Example:** Change `streamlit==1.36.0` + `streamlit==1.42.0` → `streamlit>=1.42.0`

### Issue: ModuleNotFoundError: No module named 'pkg_resources'
**Symptom:** Build fails when installing pandas on Python 3.13  
**Solution:** Upgrade pandas to 2.2+ and numpy to 2.0+, add setuptools>=75.0.0  
**Affected:** TIA-ARCHITECT-CORE

### Issue: No matching distribution found for pandas-ta
**Symptom:** pandas-ta requires Python >=3.11, Space using Python 3.9  
**Solution:** Upgrade to Python 3.11+ OR use old pandas-ta (0.2.46b0)  
**Affected:** tias-sentinel-scout-swarm-2

### Issue: Missing Core Dependencies
**Symptom:** Space crashes on startup with import errors  
**Solution:** Add missing packages to requirements.txt  
**Affected:** tias-citadel

### Issue: 404 Error Downloading Private Dataset
**Symptom:** Cannot download tias-soul-vault  
**Solution:** 
1. Verify HF_TOKEN has Read/Write permissions
2. Check namespace is `DJ-Goanna-Coding` (Double-N)
3. Ensure dataset exists and Space has access

---

## 🛰️ IDENTITY BRIDGE REFERENCE

**The Double-N Rift:**
- **GitHub:** `DJ-Goana-Coding` (Single-N)
- **HuggingFace:** `DJ-Goanna-Coding` (Double-N)

Always use the correct namespace for each platform to avoid 404 errors.

**Correct HuggingFace References:**
```python
HF_NAMESPACE = "DJ-Goanna-Coding"
SOUL_VAULT_REPO = f"{HF_NAMESPACE}/tias-soul-vault"
```

---

## 🏛️ SPACE ARCHITECTURE

```
CITADEL MESH (HuggingFace Spaces)
│
├── Mapping-and-Inventory ✅ OPERATIONAL
│   ├── Purpose: Central librarian & system map
│   ├── Tech: Streamlit, Docker
│   └── Status: Active
│
├── tias-citadel 🔴 OFFLINE
│   ├── Purpose: Sovereign command surface
│   ├── Tech: Streamlit, T.I.A. neural net
│   └── Issue: Missing dependencies
│
└── TIA-ARCHITECT-CORE 🔴 OFFLINE
    ├── Purpose: Oracle reasoning engine
    ├── Tech: Streamlit, Python 3.13, RAG
    └── Issue: Python 3.13 incompatibility
```

---

## ⚡ QUICK REPAIR WORKFLOW

### For tias-citadel:
```bash
# 1. Clone/navigate to tias-citadel repo
cd /path/to/tias-citadel

# 2. Apply requirements fix
cp /path/to/mapping-and-inventory/tia-citadel-templates/requirements.txt .

# 3. Update app.py with Identity Bridge
# Add content from tia-citadel-templates/app_py_header.py to top of app.py

# 4. Configure secrets in HuggingFace Space settings
# - HF_TOKEN (Write permissions)
# - ADMIRAL_SECRET (optional)

# 5. Push and rebuild
git add requirements.txt app.py
git commit -m "🔧 STAINLESS WELD: Fix runtime dependencies"
git push
```

### For TIA-ARCHITECT-CORE:
```bash
# OPTION 1: Automated Repair Script (Recommended)
cd /path/to/mapping-and-inventory
./scripts/repair_tia_architect_core.sh

# OPTION 2: GitHub Actions Workflow
# Go to: https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions
# Run: "🔧 Repair TIA-ARCHITECT-CORE Space" workflow

# OPTION 3: Manual Deployment
cd /path/to/TIA-ARCHITECT-CORE
cp /path/to/mapping-and-inventory/tia-architect-core-templates/requirements.txt .
git add requirements.txt
git commit -m "🔧 Fix Space: Add setuptools & Python 3.13 compatible versions"
git push origin main

# 4. Monitor build logs
# Should see: Successfully installed setuptools-75.x pandas-2.2.x numpy-2.x.x streamlit-1.4x
```

---

## 📊 DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] Identify failing Space and error type
- [ ] Review appropriate repair guide
- [ ] Prepare template files
- [ ] Backup existing configurations

### Deployment
- [ ] Apply requirements.txt fix
- [ ] Update code (if needed)
- [ ] Configure Space secrets
- [ ] Push changes to trigger rebuild

### Post-Deployment
- [ ] Monitor build logs
- [ ] Verify successful installation
- [ ] Test Space UI functionality
- [ ] Confirm all tabs/features work
- [ ] Update status in this file

---

## 🔮 COMPATIBILITY MATRIX

| Space | Python | Streamlit | pandas | numpy | Status |
|-------|--------|-----------|--------|-------|--------|
| Mapping-and-Inventory | 3.11 | 1.42+ | 2.2+ | - | ✅ Active |
| tias-citadel | 3.11+ | 1.36+ | 2.2+ | 2.1+ | 🔴 Needs Fix |
| TIA-ARCHITECT-CORE | 3.13 | 1.56 | 2.2+ | 2.0+ | 🔴 Needs Fix |

---

## 📞 SUPPORT PROTOCOLS

### If Spaces Continue to Fail:
1. **Check HuggingFace Status:** https://status.huggingface.co/
2. **Review Build Logs:** Space Settings → Logs → Build logs
3. **Factory Reboot:** Space Settings → Factory Reboot
4. **Clear Cache:** Delete Space and recreate (last resort)

### Common Build Log Patterns:
- `exit code: 1` → Dependency conflict or missing package
- `ModuleNotFoundError` → Missing import in requirements.txt
- `404 Not Found` → Incorrect namespace or private repo access
- `Permission denied` → Insufficient HF_TOKEN permissions

---

## 🏁 SUCCESS CRITERIA

A Space is considered **OPERATIONAL** when:
- ✅ Build completes without errors
- ✅ Space UI loads and displays correctly
- ✅ All tabs and features function properly
- ✅ No runtime errors in logs
- ✅ Can access external resources (datasets, APIs)

---

## 📚 RELATED DOCUMENTATION

- **[SYSTEM_MAP.txt](./SYSTEM_MAP.txt)** — Four Pillar Architecture overview
- **[districts.json](./districts.json)** — District registry and metadata
- **[README.md](./README.md)** — Main repository documentation
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** — Full deployment procedures

---

**Last Updated:** 2026-04-03  
**Architect Version:** v25.0.OMNI  
**Repair Status:** 1/3 Spaces Operational

**Weld. Pulse. Ignite.**

---

*Generated by: Citadel Architect*  
*Repository: mapping-and-inventory*  
*Mission: Restore Citadel Mesh to full operational status*
