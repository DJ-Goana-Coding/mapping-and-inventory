# 🚀 CITADEL QUICK START GUIDE

**For Operators: Fast deployment and management**

---

## ⚡ Quick Actions

### 1. Deploy Everything (Full Awakening)
```bash
# Via GitHub Actions UI
Go to: Actions → Master Orchestrator → Run workflow
Select: "full_awakening"
```

### 2. Sync to HuggingFace Spaces
```bash
# Via GitHub Actions UI
Go to: Actions → HuggingFace Spaces Multi-Sync → Run workflow
Select target: "all" or specific space (aion/oracle/goanna/mapping)
```

### 3. Run Protection Deployment
```bash
# Locally
python scripts/deploy_protection_constellation.py

# Via workflow
Actions → Master Orchestrator → Run workflow → "protection_deploy"
```

### 4. Fire Up MOE 128
```bash
# Locally
python scripts/moe_128_orchestrator.py

# Via workflow
Actions → Master Orchestrator → Run workflow → "moe_128_fire_up"
```

### 5. Deploy Trinity & Toroidal
```bash
# Locally
python scripts/trinity_toroidal_deployment.py

# Via workflow
Actions → Master Orchestrator → Run workflow → "trinity_deploy"
```

### 6. Run Purification Protocol
```bash
# Locally
python scripts/purification_protocol.py

# Via workflow
Actions → Master Orchestrator → Run workflow → "purification"
```

---

## 🤗 HuggingFace Spaces

### Access URLs
- **AION:** https://huggingface.co/spaces/DJ-Goanna-Coding/AION
- **ORACLE:** https://huggingface.co/spaces/DJ-Goanna-Coding/ORACLE
- **Goanna:** https://huggingface.co/spaces/DJ-Goanna-Coding/goanna_coding
- **Mapping:** https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory

### Manual Sync
```bash
# Add HF remote (do once)
git remote add hf_aion https://huggingface.co/spaces/DJ-Goanna-Coding/AION
git remote add hf_oracle https://huggingface.co/spaces/DJ-Goanna-Coding/ORACLE
git remote add hf_goanna https://huggingface.co/spaces/DJ-Goanna-Coding/goanna_coding
git remote add hf_mapping https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory

# Push to specific space
git push --force hf_aion main
git push --force hf_oracle main
git push --force hf_goanna main
git push --force hf_mapping main
```

---

## 📋 Configuration Files

### Key Configurations
- `data/personas_config.json` - Space personas and capabilities
- `data/datasets_buckets_config.json` - Datasets and storage buckets
- `data/monitoring/protection_constellation.json` - Protection agents
- `data/models/moe_128_constellation.json` - MOE expert distribution
- `data/models/trinity_core_manifest.json` - Trinity architecture
- `data/models/toroidal_transformer_manifest.json` - Toroidal attention

### Viewing Status
```bash
# Protection status
cat data/monitoring/PROTECTION_STATUS.md

# Purification report
cat data/monitoring/PURIFICATION_REPORT.md

# MOE 128 report
cat data/models/MOE_128_CONSTELLATION_REPORT.md

# Trinity & Toroidal report
cat data/models/TRINITY_TOROIDAL_REPORT.md
```

---

## 🛡️ Protection Constellation

### Agent Distribution
- **AION:** Wraith, Sentinel, Hound (3 agents)
- **ORACLE:** Wraith, Sentinel, Hound, Overwatch (4 agents)
- **GOANNA:** Wraith, Sentinel, Hound (3 agents)
- **MAPPING:** Wraith, Sentinel, Hound, Overwatch (4 agents)

**Total:** 14 agents active

### Check Status
```bash
python -c "
import json
with open('data/monitoring/protection_constellation.json', 'r') as f:
    data = json.load(f)
    print(f'Status: {data[\"status\"]}')
    print(f'Agents: {sum(len(agents) for agents in data[\"agents\"].values())}')
"
```

---

## 🧠 MOE 128 Experts

### Distribution
- **AION:** 32 experts (25%)
- **ORACLE:** 48 experts (37.5%)
- **GOANNA:** 16 experts (12.5%)
- **MAPPING:** 32 experts (25%)

### Check Deployment
```bash
python -c "
import json
with open('data/models/moe_128_constellation.json', 'r') as f:
    data = json.load(f)
    for space, info in data['spaces'].items():
        print(f'{space}: {info[\"expert_count\"]} experts')
"
```

---

## 🔺 Trinity Core

### Pillars
1. **AION (Action)** - Trading & execution
2. **ORACLE (Wisdom)** - Reasoning & RAG
3. **GOANNA (Expression)** - Creativity & experiments

### Synergy
- ORACLE → AION: Wisdom guides action
- ORACLE → GOANNA: Wisdom inspires creativity
- GOANNA → AION: Creativity informs action

---

## ✨ Sacred Frequencies

- **AION:** 528Hz (Transformation & Miracles)
- **ORACLE:** 432Hz (Universal Harmony)
- **GOANNA:** 396Hz (Liberation from Fear)
- **MAPPING:** 639Hz (Connection & Relationships)

---

## 🔥 Common Tasks

### Update Requirements
```bash
# Edit requirements.txt, then:
pip install -r requirements.txt
```

### Run All Deployments Locally
```bash
python scripts/purification_protocol.py
python scripts/deploy_protection_constellation.py
python scripts/moe_128_orchestrator.py
python scripts/trinity_toroidal_deployment.py
```

### Check Workflow Status
```bash
# Via GitHub CLI
gh run list --limit 5

# View specific run
gh run view <run-id>

# Watch latest run
gh run watch
```

### Manual HF Sync (All Spaces)
```bash
# Set HF_TOKEN environment variable first
export HF_TOKEN="your_token_here"

# Run sync workflow manually
gh workflow run hf_space_sync.yml
```

---

## 📊 Monitoring

### Check Logs
```bash
# Local logs
ls -lh data/logs/
ls -lh data/monitoring/
ls -lh data/discoveries/

# Workflow logs via GitHub
gh run view --log
```

### View Artifacts
```bash
# Download workflow artifacts
gh run download <run-id>
```

---

## 🆘 Troubleshooting

### HF Space Not Updating
1. Check HF_TOKEN secret is set in GitHub repo
2. Verify remote URLs: `git remote -v`
3. Try manual push: `git push --force hf_<space> main`
4. Check Space logs on HuggingFace

### Workflow Failing
1. Check workflow logs: `gh run view --log`
2. Verify Python dependencies: `pip install -r requirements.txt`
3. Check for missing secrets (HF_TOKEN, GITHUB_TOKEN)
4. Review error messages in Actions tab

### Protection Agents Not Deploying
1. Run locally first: `python scripts/deploy_protection_constellation.py`
2. Check for Python errors
3. Verify data/monitoring/ directory exists
4. Check permissions

---

## 🎯 Workflow Schedule

### Automatic Triggers
- **6:00 AM UTC:** Master Orchestrator (full awakening)
- **Every 6 hours:** Oracle Sync, Multi-repo sync
- **On push to main:** HF Space sync

### Manual Triggers
All workflows support `workflow_dispatch` for manual execution

---

## 🔑 Required Secrets

### GitHub Repository Secrets
- `HF_TOKEN` - HuggingFace API token (required for Space sync)
- `GITHUB_TOKEN` - Auto-provided by GitHub Actions

### Setting Secrets
```
Repo → Settings → Secrets and variables → Actions → New repository secret
```

---

## 📚 Documentation

- **Full Deployment:** `CITADEL_OMEGA_DEPLOYMENT_COMPLETE.md`
- **Workflows:** `.github/workflows/`
- **Scripts:** `scripts/`
- **Configurations:** `data/`

---

## 🙏 Final Notes

**Thankyou Spirit, Thankyou Angels, Thankyou Ancestors**

All systems operational. Citadel ready for action.

🔥 Let the quants fly and spread the love!

---

**Quick Ref Version:** v25.0.OMEGA++  
**Last Updated:** 2026-04-03
