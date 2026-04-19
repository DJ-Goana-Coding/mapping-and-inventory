# 🦴 SKELETON_TREE — Citadel Hub Architectural Map

> Generated as part of `QGTNL_TOTAL_SINGULARITY_WELD_v9293` → Section 1
> (`SKELETON_MAPPING`). Documents every Python entrypoint, HTTP route,
> service module, and runtime dependency that ships with this repo.
>
> Hand-curated from a recursive scan; refresh after material structural
> changes.

---

## 1. Runtime Entrypoints

| Process | File | Port | Notes |
|---|---|---|---|
| Streamlit HUD (HF Space face) | `app.py` | `7860` (`UI_PORT`) | User-facing operator UI. Launched by `scripts/start_hub.sh`. |
| FastAPI sidecar (API gateway) | `main_api.py` (`main_api:app`) | `10000` (`API_PORT`) | **PORT_WELD frequency.** Vercel Command Deck recognises this port. |
| Personal Archive RAG service | `scripts/personal_archive_rag_ingest.py` | `10000` (env `PORT`/`API_PORT`) | Standalone FastAPI — same port frequency. |
| Container | `Dockerfile` → `bash scripts/start_hub.sh` | exposes `7860`, `10000` | Multi-process weld. |

### Boot sequence

```
Dockerfile
  └─ scripts/start_hub.sh
       ├─ python -m services.rag_hub --reindex   (warm-up, non-fatal)
       ├─ uvicorn main_api:app --host 0.0.0.0 --port ${API_PORT:-10000}
       └─ streamlit run app.py --server.port ${UI_PORT:-7860}
```

---

## 2. HTTP Surface (FastAPI / Routers)

> Auto-discovered from `@app.get/post/...` decorators across the tree.

### `main_api.py` — primary API gateway
- Mounts sub-routers: `_telemetry_router`, `_bridge_router`, `_telemetry_v1_router`
- Routes:
  - `GET /healthz`
  - `POST /v1/ingest`
  - `POST /v1/ingest/device`
  - `GET  /v1/query`
  - `GET  /v1/stats`
  - `POST /v1/system/commit`
  - `GET  /v1/system/tunnels`
  - `POST /v1/webhook/github`

### `telemetry_bridge.py` — `telemetry_router`
- `GET /v1/system/status`

### `api/v1_telemetry.py` — `telemetry_v1` router
- `GET /v1/telemetry`

### `services/universal_bridge.py` — `bridge_router`
- `POST /v1/bridge/heartbeat`
- `POST /v1/bridge/ingest`
- `GET  /v1/bridge/spokes`

### `scripts/personal_archive_rag_ingest.py` — standalone
- `GET /search`
- `GET /entities`

### CORS allow-list (defaults — see `main_api.py`)
- `https://citadel-nexus-private.vercel.app` ← **Command Deck (CORS_LOCK)**
- `http://localhost:3000`, `http://localhost:5173`, `http://localhost:7860`
- Plus anything in the `ALLOWED_ORIGINS` env (comma/whitespace separated).
  Trailing slashes are normalised; the Vercel deck origin is force-restored
  if a misconfigured override drops it.

---

## 3. Service Modules

| Package | Modules |
|---|---|
| `api/` | `v1_telemetry` |
| `bridge/` | `asset_remediation` |
| `core/` | `genesis_alignment`, `self_healing_logic` |
| `ingestion/` | `rag_sync`, `universal_rag`, `omni_harvest/` |
| `inventory/` | `asset_vault`, `hardware_nodes`, `file_index.json` |
| `mapping/` | `regional_nodes`, `substrate_321` |
| `legal/` | `pvc_ledger` (`PvCLedger` dispute tracker + `PvCSovereignLedger` audit pipeline) |
| `services/` | `rag_hub`, `universal_bridge`, `tia_connector`, `gdrive_connector`, `appscript_worker_factory`, `coding_agent`, `code_executor`, `district_audit`, `district_librarian`, `dataset_connector`, `discovery_map`, `gemini_rotator`, `hf_bucket_connector`, `intel_summarizer`, `librarian_atlas`, `lore_gen`, `lore_transmuter`, `manifest_gen`, `market_sensor`, `neuron_processor`, `nuclear_push`, `omni_scanner`, `profit_sentry`, `reforge_remotes`, `repo_mapper`, `signal_probe`, `total_recon`, `washing_harvest`, `worker_archivist`, `worker_bridge`, `worker_hive_master`, `worker_reporter`, `aether_link`, `aetheric_engine`, `aetheric_probe`, `ark_engine` |
| `workers/` | `vacuum_shard_worker` |
| `security/` | `core/encryption_manager`, `core/quantum_vault`, `core/rate_limiter` |
| `registry/` | `personas.json` (Sovereign Registry — see §6) |

---

## 4. Runtime Dependencies (`requirements.txt`)

| Group | Packages |
|---|---|
| UI | `streamlit>=1.45.0` |
| Web framework | `fastapi>=0.110.0`, `uvicorn>=0.27.0`, `requests>=2.32.3` |
| Models / RAG | `sentence-transformers>=2.7.0`, `faiss-cpu>=1.8.0`, `huggingface-hub>=0.30.0`, `google-genai>=1.70.0` |
| Data | `numpy>=2.1.0`, `pandas>=2.2.0`, `plotly>=5.22.0`, `networkx>=3.3` |
| Google stack | `gspread>=6.1.0`, `google-auth>=2.29.0`, `google-auth-oauthlib>=1.2.0`, `google-api-python-client>=2.130.0` |
| Build hygiene | `setuptools>=75.0.0` (the "0.8.3 Ghost repellent") |

> No new dependencies are introduced by the QGTNL_v9293 weld. Multimedia
> harvesters (Librosa / OpenCV / VST) are intentionally **not** pulled in
> — see `PR notes / refused items` for rationale.

---

## 5. CI / Workflows (`.github/workflows/`)

Self-healing & repair surface (consolidated):

| Workflow | Purpose |
|---|---|
| `self_heal.yml` | **Single entrypoint** for self-heal; probes `/healthz` and dispatches the appropriate repair workflow on `503` / cron. |
| `autonomous_repair.yml` | Daily autonomous repo repair & integration. |
| `emergency_repair_tia_core.yml` | Manual emergency repair of the TIA Core HF Space. |
| `repair_all_spaces.yml` / `repair_tia_core_space.yml` | HF Space targeted repairs. |

CodeQL & validation:

- CodeQL is exercised via the `parallel_validation` tool used at the end
  of every QGTNL weld task.

---

## 6. Sovereign Registry

See `registry/personas.json` — maps each persona to its Toroidal Core and
functional block. The schema is documented in
`registry/README.md`.

---

## 7. Tests

- Test runner: `pytest` (`pytest.ini`, `testpaths = tests`).
- Total tests at last weld: **490 passing** (`python -m pytest -q`).
- Coverage of touched modules:
  - `legal/pvc_ledger.py` → `tests/test_omni_convergence_v22.py` (58 tests).
  - CORS / commit / HUD alignment → `tests/test_main_api_commit.py`,
    `tests/test_sovereign_hud_alignment.py`.

---

## 8. Out-of-scope refusals

The following directive items are **deliberately NOT implemented** in this
skeleton because they violate platform ToS, security policy, or are
infeasible inside CI:

1. Email/Password OAuth bypass for Google Drive/Sheets.
2. Direct downloaders for Sumo / Facebook / TikTok / YouTube.
3. Remote arbitrary command execution from the Vercel HUD.
4. Auto-pushed self-written install scripts on "Distress".
5. Mounting a 321 GB external Google Drive volume from inside the sandbox.

These are tracked in the PR description; if they need follow-up they
should be opened as separate, scoped issues for human review.
