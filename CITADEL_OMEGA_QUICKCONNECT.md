# 🚀 CITADEL_OMEGA Quick Connect

**For operators who need to connect CITADEL_OMEGA immediately**

---

## ⚡ One-Command Connection (From mapping-and-inventory)

```bash
# Set your GitHub token
export GITHUB_TOKEN=ghp_your_token_here

# Deploy workflows to CITADEL_OMEGA
python scripts/deploy_workflows_to_spokes.py --repos CITADEL_OMEGA
```

**Done!** CITADEL_OMEGA is now connected.

---

## 🔍 Verify Connection

```bash
./verify_citadel_omega_connection.sh
```

---

## 📊 Monitor First Sync

### In CITADEL_OMEGA:
```
https://github.com/DJ-Goana-Coding/CITADEL_OMEGA/actions
```
Watch for "Spoke to Mapping Hub" workflow run.

### In mapping-and-inventory:
```bash
# Check for synced artifacts
ls data/spoke_artifacts/CITADEL_OMEGA/

# Check registry entry
cat data/spoke_sync_registry.json | jq '.spokes["CITADEL_OMEGA"]'
```

---

## ✅ Success Indicators

- ✅ Workflow appears in CITADEL_OMEGA Actions
- ✅ First sync completes successfully  
- ✅ Artifacts appear in `data/spoke_artifacts/CITADEL_OMEGA/`
- ✅ Registry shows CITADEL_OMEGA entry

---

## 📚 Full Documentation

- **Complete Guide:** `CITADEL_OMEGA_CONNECTION_GUIDE.md`
- **Agent Config:** `.github/agents/citadel-omega.agent.md`
- **General Hub Sync:** `REPOSITORY_CONNECTION_GUIDE.md`

---

## 🆘 Troubleshooting

**Problem:** "GITHUB_TOKEN not set"  
**Solution:** `export GITHUB_TOKEN=ghp_your_token_here`

**Problem:** "Registry not found"  
**Solution:** `python scripts/discover_all_repos.py` first

**Problem:** "Workflow already exists"  
**Solution:** Add `--force` flag to overwrite

**Problem:** Hub not receiving sync  
**Solution:** Check both repo Actions tabs for errors

---

## 🌐 What Gets Synced

From CITADEL_OMEGA to mapping-and-inventory:
- `TREE.md` - Directory structure
- `INVENTORY.json` - Component registry
- `SCAFFOLD.md` - Architecture blueprint
- `system_manifest.json` - System metadata  
- `README.md` - Documentation

**Frequency:** Every 6 hours + on push to main

---

## 🎯 Next Steps After Connection

1. **Verify Sync:**
   ```bash
   cat data/spoke_sync_registry.json | jq '.spokes["CITADEL_OMEGA"]'
   ```

2. **Add HuggingFace Push (Optional):**
   - Add `HF_TOKEN` secret to CITADEL_OMEGA
   - Workflow already deployed

3. **Monitor Performance:**
   - Check Actions for successful runs
   - Verify artifacts update regularly

---

**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Ready for Deployment

---
