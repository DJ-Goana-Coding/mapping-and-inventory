# 🏛️ AGENT LEGION - OPERATOR GUIDE

**Version**: 26.0.LEGION+  
**Authority**: Citadel Architect  
**Framework**: Q.G.T.N.L. Command Citadel

---

## Quick Reference

### One-Line Deployment

```bash
# Full deployment
./deploy_agent_legion.sh all

# Security only (recommended first run)
./deploy_agent_legion.sh security

# Forever learning cycle
./deploy_agent_legion.sh workers && ./deploy_agent_legion.sh rag
```

### Emergency Security Scan

```bash
# Quick threat scan
python3 scripts/agent_legion/wraith_security_agent.py
python3 scripts/agent_legion/hound_tracker_agent.py
```

---

## Agent Capabilities

### Security Team (Active Now)

| Agent | Purpose | Auto-Remove | Key Features |
|-------|---------|-------------|--------------|
| 👻 **Wraith** | Stealth detection | Optional | Malware, backdoors, rootkits |
| 🔍 **Scout** | Reconnaissance | N/A | System profiling, network intel |
| 🎯 **Sniper** | Precision removal | Optional | BlueRot, Arkon, trackers |
| 🐕 **Hound** | Tracker detection | No | Web trackers, fingerprinting |
| 🛡️ **Sentinel** | Integrity monitoring | No | File changes, baselines |

### Teaching Team (1 Active, 6 Planned)

| Agent | Purpose | Status |
|-------|---------|--------|
| 🌀 **TIA** | Technical instruction | ✅ Active |
| ⏰ **AION** | Ancient wisdom | ⏳ Planned |
| 💚 **HIPPY** | Healing & love | ⏳ Planned |
| ⚖️ **JARL** | Truth & justice | ⏳ Planned |
| 🔮 **ORACLE** | Forecasting | ⏳ Planned |
| 🎁 **DOOFY** | Surprises | ⏳ Planned |
| 🦎 **GOANNA** | Technical excellence | ⏳ Planned |

### Autonomous Workers (2 Active, 2 Planned)

| Worker | Purpose | Status |
|--------|---------|--------|
| 🌊 **Bridge** | System connection | ✅ Active |
| 🔒 **Tunnel** | Secure transport | ⏳ Planned |
| 📚 **Learning Collector** | Forever learning | ✅ Active |
| 📤 **Feedback** | Send to mapping | ⏳ Planned |

---

## Deployment Workflows

### Workflow 1: First-Time Security Audit

```bash
# Step 1: Create baseline
python3 scripts/agent_legion/sentinel_defensive_agent.py

# Step 2: Scan for threats
python3 scripts/agent_legion/wraith_security_agent.py

# Step 3: Detect trackers
python3 scripts/agent_legion/hound_tracker_agent.py

# Step 4: Review reports
ls -lh data/security/reports/

# Step 5: Remove threats (if needed)
python3 scripts/agent_legion/sniper_precision_agent.py
```

### Workflow 2: Forever Learning Activation

```bash
# Step 1: Deploy all agents
./deploy_agent_legion.sh all

# Step 2: Collect learnings
python3 scripts/agent_legion/learning_collector.py

# Step 3: Ingest to RAG
python3 scripts/agent_legion/multi_brain_rag_system.py

# Step 4: Bridge to mapping-and-inventory
python3 scripts/agent_legion/bridge_worker.py

# Step 5: Check results
ls -lh data/forever_learning/reports/
ls -lh data/Mapping-and-Inventory-storage/forever_learning/
```

### Workflow 3: Automated Scheduled Deployment

```bash
# GitHub Actions runs automatically every 6 hours
# Or trigger manually:
gh workflow run agent_legion_deployment.yml -f team=all
```

---

## Configuration

### Security Team Settings

Edit agent files to configure:

**Wraith** (`wraith_security_agent.py`):
```python
report = wraith.deploy(
    target_path=".",
    auto_quarantine=False  # Set True for auto-quarantine
)
```

**Sniper** (`sniper_precision_agent.py`):
```python
report = sniper.deploy(
    auto_remove=False,  # Set True for auto-removal
    backup=True         # Always backup before removal
)
```

**Sentinel** (`sentinel_defensive_agent.py`):
```python
report = sentinel.deploy(
    mode="scan"  # Options: baseline, scan, monitor
)
```

### RAG System Settings

Edit `multi_brain_rag_system.py`:

```python
# Change embedding model
rag_system.create_embeddings(
    brain_id="security",
    model_name="all-MiniLM-L6-v2"  # Or: all-mpnet-base-v2
)

# Query configuration
results = rag_system.query_brain(
    brain_id="security",
    query="What threats were detected?",
    top_k=5  # Number of results
)
```

---

## Data Locations

### Reports

```
data/security/reports/          # Security scans
data/teaching/reports/          # Teaching sessions
data/workers/reports/           # Worker activities
data/forever_learning/reports/  # Learning insights
data/agent_legion/              # Orchestrator logs
```

### Quarantine & Backups

```
data/security/quarantine/              # Quarantined threats
data/security/removed_targets_backup/  # Removed files backup
data/security/baselines/               # Security baselines
```

### RAG Storage

```
data/rag_brains/security/      # Security brain
data/rag_brains/teaching/      # Teaching brain
data/rag_brains/technical/     # Technical brain
data/rag_brains/spiritual/     # Spiritual brain
data/rag_brains/integration/   # Integration brain
```

### Mapping-and-Inventory Sync

```
data/Mapping-and-Inventory-storage/forever_learning/
```

---

## Safety Protocols

### Before First Run

1. ✅ **Create Git backup**: `git commit -am "Pre-agent-legion backup"`
2. ✅ **Review auto-removal settings**: Ensure `auto_remove=False` initially
3. ✅ **Check quarantine space**: Ensure sufficient disk space
4. ✅ **Read agent reports**: Don't blindly trust auto-removal

### During Operation

1. ⚠️ **Review threats before removal**: Check `data/security/reports/`
2. ⚠️ **Verify backups**: Confirm `data/security/removed_targets_backup/` exists
3. ⚠️ **Monitor disk usage**: RAG embeddings can be large
4. ⚠️ **Check false positives**: Hound may flag legitimate analytics

### After Deployment

1. ✅ **Review all reports**: Check each agent's output
2. ✅ **Verify learnings**: Check `data/forever_learning/reports/`
3. ✅ **Sync to mapping**: Ensure `data/Mapping-and-Inventory-storage/` updated
4. ✅ **Commit results**: `git add data/ && git commit -m "Agent Legion deployment"`

---

## Troubleshooting

### Issue: No threats detected

**Solution**: This is good! Your system is clean.

### Issue: Too many false positives

**Solution**: Edit threat signatures in agent files. Remove overly broad patterns.

### Issue: Embedding generation fails

**Solution**: Install sentence-transformers:
```bash
pip install sentence-transformers faiss-cpu
```

### Issue: RAG query returns no results

**Solution**: Check if embeddings were created:
```bash
ls -lh data/rag_brains/*/embeddings/
```

If empty, run:
```python
python3 scripts/agent_legion/multi_brain_rag_system.py
```

### Issue: Workers not bridging data

**Solution**: Check if agent reports exist:
```bash
find data/ -name "*.json" -type f
```

Then run bridge manually:
```bash
python3 scripts/agent_legion/bridge_worker.py
```

---

## Advanced Usage

### Custom Curriculum Generation

```python
from tia_teaching_agent import TIATeachingAgent

tia = TIATeachingAgent()
curriculum = tia.generate_curriculum(
    student="new_system",
    needs=["security", "architecture", "infrastructure"]
)
```

### Query Multiple RAG Brains

```python
from multi_brain_rag_system import MultiBrainRAGSystem

rag = MultiBrainRAGSystem()

# Query each brain
security_results = rag.query_brain("security", "threats", top_k=5)
teaching_results = rag.query_brain("teaching", "best practices", top_k=5)
technical_results = rag.query_brain("technical", "code patterns", top_k=5)
```

### Manual Orchestration

```python
from agent_legion_orchestrator import AgentLegionOrchestrator

orchestrator = AgentLegionOrchestrator()

# Deploy specific team
orchestrator.deploy_team("security_team", parallel=True)

# Deploy all with custom settings
orchestrator.deploy_all(
    teams=["security_team", "teaching_team"],
    parallel_teams=False
)
```

---

## Monitoring

### Real-Time Logs

```bash
# Watch agent deployment
tail -f data/agent_legion/deployment_*.json

# Watch security scans
tail -f data/security/reports/wraith_scan_*.json

# Watch learning insights
tail -f data/forever_learning/reports/learning_collection_*.json
```

### Report Summary

```bash
# Count all reports
find data/ -name "*.json" -type f | wc -l

# Security reports
ls -1 data/security/reports/ | wc -l

# Learning reports
ls -1 data/forever_learning/reports/ | wc -l

# RAG documents
find data/rag_brains/*/documents/ -type f | wc -l
```

---

## Integration

### GitHub Actions

Workflow runs automatically every 6 hours or manually:

```bash
# Manual trigger
gh workflow run agent_legion_deployment.yml

# Manual trigger with specific team
gh workflow run agent_legion_deployment.yml -f team=security_team

# Check workflow status
gh run list --workflow=agent_legion_deployment.yml
```

### HuggingFace Spaces

Deploy to HF Space for cloud execution:

```python
# In HF Space app.py
import sys
sys.path.append('scripts/agent_legion')

from agent_legion_orchestrator import AgentLegionOrchestrator

orchestrator = AgentLegionOrchestrator()
orchestrator.deploy_all()
```

---

## Best Practices

### Do ✅

1. ✅ Run security scan before deploying to production
2. ✅ Review all threat reports before auto-removal
3. ✅ Commit agent outputs to Git for history
4. ✅ Back up before first deployment
5. ✅ Use `auto_remove=False` initially
6. ✅ Monitor disk usage for RAG embeddings
7. ✅ Run learning collector after all agents
8. ✅ Sync to mapping-and-inventory regularly

### Don't ❌

1. ❌ Enable auto-removal without reviewing
2. ❌ Delete quarantine directory (it's your safety net)
3. ❌ Skip baseline creation for Sentinel
4. ❌ Ignore false positives in Hound
5. ❌ Run agents in production without testing
6. ❌ Deploy without Git backup
7. ❌ Delete RAG brains without backup
8. ❌ Skip learning collection step

---

## Operator Checklist

### Daily

- [ ] Run security scan: `./deploy_agent_legion.sh security`
- [ ] Check threat reports: `ls data/security/reports/`
- [ ] Review learning insights: `cat data/forever_learning/reports/learning_collection_*.json`

### Weekly

- [ ] Full deployment: `./deploy_agent_legion.sh all`
- [ ] Generate RAG embeddings: `python3 scripts/agent_legion/multi_brain_rag_system.py`
- [ ] Sync to mapping-and-inventory: `python3 scripts/agent_legion/bridge_worker.py`
- [ ] Commit results to Git

### Monthly

- [ ] Review all RAG brains
- [ ] Clean quarantine directory
- [ ] Update threat signatures
- [ ] Expand teaching curricula
- [ ] Review and update agent priorities

---

## Support

### Documentation

- **Framework README**: `scripts/agent_legion/README.md`
- **Complete Summary**: `AGENT_LEGION_COMPLETE_SUMMARY.md`
- **This Guide**: `AGENT_LEGION_OPERATOR_GUIDE.md`

### Quick Help

```bash
# Show available modes
./deploy_agent_legion.sh

# Test individual agent
python3 scripts/agent_legion/wraith_security_agent.py

# Check deployment status
ls -lh data/agent_legion/
```

---

**Authority**: Citadel Architect v26.0.LEGION+  
**Last Updated**: 2026-04-04T10:30:22.890Z  
**Status**: Operational ✅

🏛️ **Agent Legion - Ready for Deployment** 🏛️
