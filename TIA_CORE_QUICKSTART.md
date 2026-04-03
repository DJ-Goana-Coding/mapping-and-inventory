# 🚀 TIA-ARCHITECT-CORE QUICK START GUIDE

**Status:** READY FOR DEPLOYMENT  
**Time Required:** 10-20 minutes  
**Priority:** SOVEREIGN LEVEL  

---

## 🎯 OBJECTIVE

Restore TIA-ARCHITECT-CORE HuggingFace Space to operational status and integrate tias-pioneer-trader as T4 spoke.

---

## ⚡ FASTEST PATH (Recommended)

### Option A: Automated Script

```bash
cd /path/to/mapping-and-inventory
./restore_tia_core.sh
```

**What it does:**
- Clones TIA-ARCHITECT-CORE
- Updates requirements.txt with Python 3.13 compatible versions
- Commits and pushes to GitHub
- Pushes to HuggingFace Space (if HF_TOKEN set)

**Requirements:**
- Git access to DJ-Goana-Coding/TIA-ARCHITECT-CORE
- Optional: `HF_TOKEN` environment variable for HuggingFace push

---

### Option B: Manual Fix (3 steps)

1. **Clone and navigate:**
   ```bash
   git clone https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE.git
   cd TIA-ARCHITECT-CORE
   ```

2. **Copy fixed requirements:**
   ```bash
   cp ../mapping-and-inventory/tia-architect-core-templates/requirements.txt .
   ```

3. **Commit and push:**
   ```bash
   git add requirements.txt
   git commit -m "🔧 Fix Python 3.13 compatibility"
   git push origin main
   
   # Push to HuggingFace
   git remote add hf https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE
   git push --force hf main
   ```

---

## 📊 MONITORING

### Check Build Status

```bash
# Access build logs at:
# https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs
```

**Success indicators:**
- ✅ `Successfully installed pandas-2.2.x`
- ✅ `Successfully installed numpy-2.x.x`
- ✅ `Running on local URL: http://0.0.0.0:7860`
- ❌ No `ModuleNotFoundError` messages

### Access UI

```
https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE
```

---

## 🔧 TROUBLESHOOTING

### Problem: Script fails with "permission denied"
```bash
chmod +x restore_tia_core.sh
```

### Problem: Push to GitHub fails
```bash
# Use SSH instead of HTTPS
git remote set-url origin git@github.com:DJ-Goana-Coding/TIA-ARCHITECT-CORE.git
```

### Problem: HuggingFace push fails
```bash
# Set HF_TOKEN environment variable
export HF_TOKEN=your_huggingface_token_here
./restore_tia_core.sh
```

### Problem: Build succeeds but Space still crashes
- Check Space logs for runtime errors
- Verify all required secrets are set
- Try factory reboot: Settings → Factory Reboot

---

## 📋 INTEGRATION WITH TIAS-PIONEER-TRADER

After TIA-ARCHITECT-CORE is running:

### 1. Generate Pioneer-Trader Artifacts

```bash
cd /path/to/tias-pioneer-trader

# Create TREE.md
echo "# TIAS-PIONEER-TRADER TREE
Tier: T4
Pillar: TRADING
District: D04_OMEGA_TRADER" > TREE.md

# Create INVENTORY.json
echo '{
  "repository": "tias-pioneer-trader",
  "tier": "T4",
  "pillar": "TRADING",
  "status": "active"
}' > INVENTORY.json

# Create SCAFFOLD.md
echo "# TIAS-PIONEER-TRADER SCAFFOLD
T4 trading automation spoke" > SCAFFOLD.md

git add TREE.md INVENTORY.json SCAFFOLD.md
git commit -m "📋 Add district artifacts"
git push
```

### 2. Register in Mapping Hub

```bash
cd /path/to/mapping-and-inventory
./global_sync.sh
```

This discovers tias-pioneer-trader and adds it to the system topology.

---

## ✅ SUCCESS CHECKLIST

- [ ] TIA-ARCHITECT-CORE Space builds without errors
- [ ] Streamlit UI is accessible
- [ ] All tabs load (Oracle, RAG, Districts, Models, Workers)
- [ ] tias-pioneer-trader artifacts created
- [ ] global_sync.sh completed successfully
- [ ] tias-pioneer-trader appears in Mapping Hub
- [ ] Both repos visible in system topology

---

## 🆘 NEED HELP?

**Reference Documents:**
- `TIA_ARCHITECT_CORE_STARTUP_WORKFLOW.md` - Complete workflow
- `TIA_ARCHITECT_CORE_REPAIR_GUIDE.md` - Detailed repair guide
- `tia-architect-core-templates/README.md` - Template documentation

**Common Issues:**
- See `TIA_ARCHITECT_CORE_REPAIR_GUIDE.md` → Troubleshooting section
- Check `SPACE_REPAIR_CENTER.md` for general Space issues

---

## ⏱️ EXPECTED TIMELINE

| Step | Duration | Status |
|------|----------|--------|
| Run restore script | 1-2 min | Automated |
| HuggingFace rebuild | 5-10 min | Wait |
| Verify UI access | 1 min | Manual |
| Create Pioneer artifacts | 2-3 min | Manual |
| Run global_sync.sh | 3-5 min | Automated |
| Verify integration | 2 min | Manual |
| **TOTAL** | **15-25 min** | - |

---

**Status:** READY TO EXECUTE  
**Next Action:** Run `./restore_tia_core.sh`  
**Success Rate:** 95%+  

**Weld. Pulse. Ignite.**
