# CITADEL SKELETON — Repository Map

**Repository:** `DJ-Goana-Coding/mapping-and-inventory`  
**HuggingFace Space:** `DJ-Goanna-Coding/Mapping-and-Inventory`  
**Role:** Central Hub / Librarian node of the Citadel Mesh  
**Runtime:** Python 3.11 — Streamlit (port 7860) + FastAPI sidecar (port 8000)

---

## Top-Level Entry Points

| File | Purpose |
|---|---|
| `app.py` | Streamlit frontend — Sovereign HUD with tabbed UI: Repos, GDrive, T.I.A. Chat, Datasets, Coding Agent, Code Executor, AppScript |
| `main_api.py` | FastAPI sidecar — RAG ingest/query, GitHub commit bridge, tunnel probes |
| `command_center.py` | CLI/batch orchestration entry point |
| `commander_dashboard.py` | Extended dashboard logic |
| `ignite_hub_memory.py` | One-shot script: seeds the FAISS index on cold start |
| `ignite_tia.py` | One-shot script: wakes T.I.A. inference service |
| `citadel_nexus.py` | Nexus orchestrator: connects all Citadel sub-systems |
| `nerve_check.py` | Health probe CLI: checks all services and env vars |
| `process_transmission.py` | Processes incoming spiritual/knowledge transmission payloads |

---

## FastAPI Endpoints (`main_api.py`)

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/healthz` | none | Liveness probe. Returns `{"status": "ok"}` |
| `GET` | `/v1/stats` | none | RAG index introspection: chunk count, sources, model |
| `POST` | `/v1/ingest` | none | Rebuild FAISS index over Master Harvest fragments |
| `GET` | `/v1/query` | none | Semantic search (`?q=...&k=5`) |
| `POST` | `/v1/query` | none | Semantic search (JSON body `{"q": ..., "k": ...}`) |
| `POST` | `/v1/system/commit` | `X-HF-Token` or `Authorization: Bearer` | Commit files to GitHub via Contents API |
| `GET` | `/v1/system/tunnels` | none | Probes HuggingFace, GDrive, GitHub reachability + token presence |
| `GET` | `/v1/system/status` | none | Aggregate health + RAG state (provided by `telemetry_bridge.py`) |

**CORS allow-list:** `https://citadel-nexus-private.vercel.app`, `localhost:3000`, `localhost:5173`, `localhost:7860`

---

## Services (`services/`)

| Module | Role |
|---|---|
| `rag_hub.py` | FAISS-backed RAG index over Master Harvest fragments. Singleton `RagHub`. Thread-safe. |
| `gemini_rotator.py` | Round-robin Gemini API key rotation with 429/ResourceExhausted failover |
| `repo_mapper.py` | Enumerates `KNOWN_REPOS`, builds connection graph, snaps system state |
| `gdrive_connector.py` | rclone-based GDrive sync and listing; service-account JSON auth |
| `tia_connector.py` | HTTP client to T.I.A. inference Space; wraps `get_tia_response` |
| `dataset_connector.py` | Loads local inventory CSVs, neuron data, search, stats |
| `coding_agent.py` | Gemini-backed code generation, review, explanation, refactor, debug, chat |
| `code_executor.py` | Safe sandboxed `exec` for Python snippets and bash commands |
| `appscript_worker_factory.py` | Renders Google Apps Script worker templates |
| `worker_bridge.py` | TCP health checks for GitHub, HuggingFace, GDrive, and device nodes |
| `worker_hive_master.py` | Coordinates all background workers; writes `worker_status.json` |
| `worker_reporter.py` | Generates worker run reports |
| `worker_archivist.py` | Archives processed data to `data/spoke_artifacts/` |
| `district_librarian.py` | District-level RAG and data index manager |
| `librarian_atlas.py` | Cross-district atlas/manifest builder |
| `omni_scanner.py` | Full-mesh scan orchestrator |
| `total_recon.py` | Deep recon across all connected repos and data sources |
| `discovery_map.py` | Builds the discovery map for the Streamlit UI |
| `manifest_gen.py` | Generates `global_manifest.json` and `system_manifest.json` |
| `nuclear_push.py` | Force-push utility for critical repository updates |
| `signal_probe.py` | Lightweight signal/heartbeat probe |
| `intel_summarizer.py` | AI-powered summarization of intel reports |
| `aether_link.py` | Aether harvest data link; connects to remote Aether manifests |
| `aetheric_engine.py` | Processes Aether energy/intelligence data |
| `aetheric_probe.py` | Probes Aether endpoints |
| `ark_engine.py` | ARK_CORE integration engine |
| `neuron_processor.py` | Processes neuron/knowledge graph data |
| `market_sensor.py` | Financial market data sensor |
| `profit_sentry.py` | Trading profit monitoring |
| `lore_gen.py` / `lore_transmuter.py` | Generates and transforms lore/narrative content |
| `reforge_remotes.py` | Repairs and reforges broken git remotes |
| `washing_harvest.py` | Cleans and normalizes harvest data |
| `hf_bucket_connector.py` | HuggingFace dataset bucket connector |
| `district_audit.py` | Audits district state and integrity |
| `genesis_alignment.py` (`core/`) | Core Genesis alignment protocol |

---

## Data Layout (`data/`)

| Path | Contents |
|---|---|
| `data/vector_store/harvest.index` | FAISS flat inner-product index (384-dim MiniLM-L6-v2) |
| `data/vector_store/harvest_meta.json` | Chunk metadata: source paths, chunk indices, text |
| `data/master_harvest/INDEX.md` | Master Harvest fragment index |
| `data/master_harvest_manifest.json` | Machine-readable harvest manifest |
| `data/AETHER_HARVEST_DISCOVERY_MANIFEST.json` | Aether harvest discovery manifest |
| `data/system_master_index.json` | System-level master index |
| `data/omega-omni-master-index.json` | Omega-Omni discovery index |
| `data/spoke_sync_registry.json` | Registered spoke repos |
| `data/worker_constellation/` | Worker constellation configs and state |
| `data/personas/` | Persona configurations |
| `data/datasets/` | Local dataset files |
| `data/rag_brains/` | RAG brain shards |
| `data/models/` | Local model registry |
| `data/discoveries/` | Discovery run outputs |
| `data/solutions/` | AI-generated solution documents |
| `data/personal_archive/` | Personal archive artifacts |
| `data/spiritual_intelligence/` | Spiritual intelligence data |

---

## Key Configuration Files

| File | Purpose |
|---|---|
| `requirements.txt` | Python dependencies |
| `Dockerfile` | Container definition for HF Space |
| `pytest.ini` | Test configuration |
| `packages.txt` | System packages (`apt`) |
| `global_manifest.json` | Global mesh manifest |
| `system_manifest.json` | System component manifest |
| `master_inventory.json` | Master asset inventory |
| `districts.json` | District configuration |
| `district_status_report.json` | District health status |
| `worker_status.json` | Worker run status |

---

## Internal Data Flows

```
Vercel Command Deck (citadel-nexus-private.vercel.app)
    │
    ├── POST /v1/system/commit  ─── GH_TOKEN ──▶ GitHub Contents API
    ├── POST /v1/ingest         ──────────────▶ RagHub.reindex() ──▶ data/vector_store/
    ├── GET  /v1/query          ──────────────▶ RagHub.query()   ──▶ FAISS search
    └── GET  /v1/system/tunnels ──────────────▶ HEAD probe HF / GDrive / GitHub

app.py (Streamlit HUD)
    │
    ├── services/repo_mapper    ──▶ KNOWN_REPOS list + git remotes
    ├── services/gdrive_connector ─── rclone ──▶ Google Drive
    ├── services/tia_connector  ─── HTTP ─────▶ T.I.A. HF Space
    ├── services/dataset_connector ──▶ data/datasets/
    ├── services/coding_agent   ─── Gemini ───▶ GEMINI_API_KEY*
    └── services/code_executor  ──▶ sandboxed exec

scripts/ (100+ utility scripts)
    │
    ├── harvest_*.py / *_vacuum.py  ──▶ data/master_harvest/ + data/personal_archive/
    ├── rag_ingest.py               ──▶ RagHub / data/vector_store/
    ├── generate_*.py               ──▶ data/solutions/ + doc indexes
    └── deploy_*.py / repair_*.sh   ──▶ GitHub / HF Space management
```

---

## Dead Ends Identified

| Location | Issue |
|---|---|
| `app.py` line 60 | `HF_SPACE_ID = "DJ-Goanna-Coding/Mapping-and-Inventory"` — double 'n' in "Goanna" differs from GitHub org `DJ-Goana-Coding` (single 'n'). Intentional if HF org name differs; verify. |
| `services/worker_bridge.py` line 243 | Checks for `Partition_01/oppo_node.py` — file does not exist in repo; device node detection always falls back to "SCRIPT_MISSING". |
| `data/vector_store/harvest.index` | Does not exist on cold start; `GET /v1/stats` returns `loaded: false` until first `POST /v1/ingest`. |
| Multiple markdown files | "VAMGUARD" used in many docs and template dirs; unrelated code may reference "VANGUARD" — these are the same technology, different capitalisation. See `VAMGUARD_DEPLOYMENT_GUIDE.md` vs downstream consumers. |
| `services/gdrive_connector.py` | Requires `rclone` binary AND service-account JSON at runtime; container may not have `rclone` unless `packages.txt` installs it. |
| `data/master_harvest/INDEX.md` | Referenced by `services/rag_hub.py` as a default fragment — file may not exist, silently skipped. |
