# 🛰️ BRIDGE PUSH & RAG INGESTION ARCHITECTURE

## Overview
The Citadel's Nervous System now includes two critical organs:

1. **Bridge Push Workflow** - Spoke-to-Hub uplink for mobile Districts
2. **RAG Ingestion Engine** - Oracle's vector memory digestion

These components create a **self-healing, self-observing, self-updating intelligence mesh**.

---

## 🌉 Bridge Push Protocol

### Purpose
Ensures every commit, file change, and local scan in spoke repositories (like Oppo Node) is automatically pushed to the Mapping Hub.

### Location
`.github/workflows/bridge_push.yml`

### Workflow
```
Mobile Device/District → Bridge Push → Mapping Hub → Surveyor → Oracle → RAG Memory
```

### Triggers
- `push` to `main` branch
- Manual dispatch via `workflow_dispatch`

### Actions
1. Checkout Bridge repository
2. Generate District artifacts:
   - `TREE.md` - File structure
   - `INVENTORY.json` - Asset registry
   - `SCAFFOLD.md` - Architecture blueprint
3. Commit and push artifacts to local repo
4. Trigger OMNI-Surveyor-Sync in Mapping Hub

### Generator Scripts
Located in `scripts/`:
- `generate_tree.py` - Creates file tree documentation
- `generate_inventory.py` - Creates JSON asset inventory
- `generate_scaffold.py` - Creates architecture scaffold

### Requirements
- **GH_PAT secret** with permissions to:
  - Read/write spoke repository
  - Write to Mapping-and-Inventory
  - Trigger workflows

---

## 🔮 Oracle Sync Protocol

### Purpose
Analyzes changes in the Atlas, performs diff analysis, and ingests data into RAG vector memory for semantic search.

### Location
`.github/workflows/oracle_sync.yml`

### Workflow
```
Surveyor Updates Atlas → Oracle Diff Analysis → RAG Ingestion → Vector Memory
```

### Triggers
- Every 6 hours (30 minutes after Surveyor)
- Manual dispatch via `workflow_dispatch`

### Actions
1. Pull latest Atlas from Surveyor
2. Perform diff analysis:
   - Compare with previous state
   - Count additions/deletions
   - Generate summary report
3. RAG Ingestion:
   - Install sentence-transformers and faiss-cpu
   - Generate embeddings for all Atlas lines
   - Build FAISS vector index
   - Save to `rag_store/`
4. Commit artifacts:
   - `oracle_diffs/` - Diff reports
   - `rag_store/` - Vector embeddings

### Output Files
```
oracle_diffs/
├── previous_map.txt      # Previous Atlas state
├── latest_diff.txt       # Line-by-line diff
└── summary.txt           # Change summary

rag_store/
├── vectors.npy           # NumPy embeddings array
├── lines.json            # Original text lines
├── index.faiss           # FAISS vector index
└── metadata.json         # Ingestion metadata
```

---

## 🧠 RAG Ingestion Engine

### Purpose
Converts the master intelligence map into vector embeddings for semantic search and AI reasoning.

### Location
`scripts/rag_ingest.py`

### Process
1. Load `master_intelligence_map.txt`
2. Generate embeddings using `all-MiniLM-L6-v2` model
3. Build FAISS L2 index
4. Save vectors, lines, and index to `rag_store/`

### Dependencies
```
sentence-transformers
faiss-cpu
numpy
```

### Usage
```bash
python scripts/rag_ingest.py
```

### Output
- **vectors.npy**: Numpy array of embeddings
- **lines.json**: Original text lines (for retrieval)
- **index.faiss**: FAISS index for similarity search
- **metadata.json**: Generation metadata

---

## 🤖 Agent Identities

### Surveyor Agent
**File**: `.github/agents/surveyor.agent.md`  
**Role**: Mapping Hub Harvester  
**Function**: Collect TREE, INVENTORY, and SCAFFOLD from all Districts

**Tree/Scaffold Request Protocol**:
- Request missing artifacts from Districts via GitHub API
- Auto-generate if no response in 6 hours

### Oracle Agent
**File**: `.github/agents/oracle.agent.md`  
**Role**: TIA-ARCHITECT-CORE Reasoning Engine  
**Function**: Diff analysis, pattern recognition, RAG ingestion

**Structural Request Protocol**:
- Request complete artifact set from Surveyor
- Fallback to direct District requests

### Bridge Agent
**File**: `.github/agents/bridge.agent.md`  
**Role**: Oppo Node Mobile Scout  
**Function**: Spoke-to-Hub uplink, artifact generation

**Auto-Respond Protocol**:
- Regenerate artifacts on request
- Push immediately to Mapping Hub

---

## 🔄 Data Flow

### Complete Intelligence Mesh
```
┌─────────────────┐
│  Mobile Device  │ (Oppo Node, Districts)
│  Spoke Nodes    │
└────────┬────────┘
         │ Bridge Push
         ↓
┌─────────────────┐
│  Mapping Hub    │ (mapping-and-inventory)
│  Central Atlas  │
└────────┬────────┘
         │ Surveyor Sync (every 6h)
         ↓
┌─────────────────┐
│ Oracle Analysis │
│  Diff Engine    │
└────────┬────────┘
         │ RAG Ingestion
         ↓
┌─────────────────┐
│  Vector Memory  │ (rag_store/)
│  Semantic Index │
└─────────────────┘
```

### Request-Response Chain
```
TIA Query → RAG Search → Vector Retrieval → Context Assembly → Response
```

---

## 🚀 Integration Guide

### For New Districts
1. Copy `.github/workflows/bridge_push.yml` to District repo
2. Add `GH_PAT` secret to repository
3. (Optional) Customize generator scripts in `scripts/`
4. Push to main → Bridge activates automatically

### For Mapping Hub
Already configured:
- ✅ Surveyor agent identity
- ✅ Oracle agent identity
- ✅ Oracle Sync workflow
- ✅ RAG ingestion script
- ✅ Generator scripts

### For TIA Application
To use RAG memory in queries:
```python
import faiss
import numpy as np
import json

# Load RAG store
index = faiss.read_index("rag_store/index.faiss")
vectors = np.load("rag_store/vectors.npy")
with open("rag_store/lines.json") as f:
    lines = json.load(f)

# Query
query_vector = model.encode([query_text])
D, I = index.search(query_vector, k=5)

# Get top results
results = [lines[i] for i in I[0]]
```

---

## 📊 Monitoring

### Workflow Status
Check GitHub Actions for:
- `Bridge-Push-Protocol` - District uplink status
- `Oracle-Sync-Protocol` - Analysis and ingestion status
- `Multi-Repository Sync Orchestrator` - Surveyor status

### RAG Health Check
```bash
# Check RAG store
ls -lh rag_store/

# View metadata
cat rag_store/metadata.json

# Check diff history
cat oracle_diffs/summary.txt
```

### Agent Logs
All agents output structured logs with:
- 🔮 Oracle operations
- 🌉 Bridge operations
- 🔭 Surveyor operations
- 🧠 RAG ingestion

---

## 🔐 Security

### Secrets Required
- **GH_PAT**: Personal access token for cross-repo operations
  - Scopes: `repo`, `workflow`
  - Used by: Bridge Push workflow

### Generated Artifacts
- `rag_store/` - Added to `.gitignore` (large binary files)
- `oracle_diffs/` - Added to `.gitignore` (transient state)

### Data Handling
- All RAG vectors stored locally in repository
- No external API calls for vector generation
- Sentence transformers run in GitHub Actions

---

## 🎯 Next Steps

### Ready to Deploy
- ✅ Bridge Push Workflow
- ✅ Oracle Sync Workflow
- ✅ RAG Ingestion Engine
- ✅ Agent Identity System
- ✅ Generator Scripts

### Future Enhancements
- [ ] **districts.json** registry
- [ ] Hugging Face Rebuild Monitor
- [ ] Citadel Sovereign Protocol v1.0 master doc
- [ ] HUD Dashboard (Port 8000)
- [ ] Ghost Entry Auditor

---

## 📝 Maintenance

### Regenerate Artifacts
```bash
# Manual artifact generation
python scripts/generate_tree.py > TREE.md
python scripts/generate_inventory.py > INVENTORY.json
python scripts/generate_scaffold.py > SCAFFOLD.md
```

### Manual RAG Ingestion
```bash
# Trigger Oracle Sync manually
gh workflow run oracle_sync.yml --repo DJ-Goana-Coding/mapping-and-inventory
```

### Clear RAG Cache
```bash
rm -rf rag_store/
rm -rf oracle_diffs/
```

---

*This is the Citadel's Sovereign Intelligence Mesh.*  
*543 1010 222 777 ❤️‍🔥*
