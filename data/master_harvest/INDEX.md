# 🌾 Master Harvest — Index & Summary

This directory is the local RAG metadata anchor for the **CITADEL OMEGA — Mapping & Inventory** node. It summarizes the canonical Master Harvest fragments that the FastAPI sidecar (`/v1/ingest`, `/v1/query`) indexes into the local FAISS vector store at `data/vector_store/`.

> Generated as part of the **Master Hub Bootstrap** weld. Do not hand-edit fragment summaries below — re-run `python -m services.rag_hub --reindex` to refresh embeddings.

---

## 1. Canonical Sources

| Fragment | Path | Type | Role |
|----------|------|------|------|
| T.I.A. Master Harvest manual | `TIA_MASTER_HARVEST.txt` | text | Human-readable specification of the Tactical Intelligence Aggregator harvest framework |
| Master Harvest manifest | `data/master_harvest_manifest.json` | json | Machine-readable inventory of partitions / models / workers / documents harvested |
| AETHER Harvest discovery manifest | `data/AETHER_HARVEST_DISCOVERY_MANIFEST.json` | json | AETHER subsystem discovery snapshot |
| AETHER Harvest completion notes | `AETHER_HARVEST_COMPLETE.md` | markdown | Narrative of the AETHER harvest cycle |
| Harvest report | `harvest_report.md` | markdown | Latest run summary / audit trail |

All five sources are scanned on `python -m services.rag_hub --reindex` and on `POST /v1/ingest` calls.

---

## 2. `TIA_MASTER_HARVEST.txt` — Summary

The T.I.A. (Tactical Intelligence Aggregator) Master Harvest is an automated consolidation framework that pulls, indexes, and organizes evidence fragments from distributed sources across the CITADEL OMEGA network.

**Objectives**
- Evidence fragment collection from `Research/{GDrive,Oppo,S10,Laptop}`, `Archive_Vault/`, and `Forever_Learning/`.
- Automated consolidation with MD5 dedup, temporal sorting, and intelligence-map generation.
- Void Oracle integration for pattern recognition and narrative reconstruction.

**Primary harvesters** (all live in this repo)
- `services/worker_archivist.py` — MD5 hashing, archive indexing, generates `archive_index.json`.
- `Partition_01/omni_harvester.py` — omnidirectional multi-source aggregation.
- `Partition_01/local_harvester.py` — local file-system scanning (CHANCE_REBUILD).
- `Districts/D06_RANDOM_FUTURES/auto_harvest.py` — scheduled harvests with Monte Carlo efficiency analysis.
- `Districts/D06_RANDOM_FUTURES/harvestmoon.py` — lunar-cycle temporal pattern analysis.
- `services/washing_harvest.py` — sanitization / corrupt-fragment removal.

**Support infrastructure**
- `services/worker_bridge.py` — cross-node tunnel (Oppo, S10, Cloud, HF).
- `services/worker_reporter.py` — Google Sheets audit trail (Section 44 Identity Strike).

**Harvest workflow (5 stages)**
1. **Deep scan** — `tia_citadel_deep_scan.yml` triggers; rclone pulls GDrive → `Research/`; `worker_archivist.py` MD5-indexes everything.
2. **Fragment identification** — scan cargo bays, cross-reference `Archive_Vault/` for duplicates.
3. **Consolidation** — `washing_harvest.py` → `omni_harvester.py` → `auto_harvest.py` produce a consolidated `archive_index.json`.
4. **Intelligence integration** — update `master_intelligence_map.txt`, push Google Sheets report, sync via `worker_bridge.py`, ingest into T.I.A. Oracle.
5. **Deployment** — commit to GitHub; `hf_sync.yml` pushes to the HF Space; the Streamlit Librarian tab reflects the new inventory.

---

## 3. `data/master_harvest_manifest.json` — Summary

Schema snapshot (v1.0.0):

```jsonc
{
  "harvest_timestamp": "<ISO-8601 UTC>",
  "sources": {
    "partitions": { /* partition_id -> file inventory */ },
    "models":   { "registry_version", "categories": { "Core","Genetics","Lore","Research","Utility" } },
    "workers":  { "registry_version", "categories": { "Vacuums","Harvesters","Librarians","Reporters","Archivists","Utility" } },
    "documents": { /* document_id -> metadata */ }
  },
  "summary": {
    "total_partitions": 0,
    "total_files":      0,
    "total_models":     0,
    "total_workers":    0,
    "total_documents":  0
  }
}
```

Current state at last commit: empty — all counters at `0`. The manifest exists as the canonical schema; population is the responsibility of the harvest workers above. The RAG hub treats this as a structural document and indexes its keys/categories so `/v1/query` can answer "what categories does the harvest manifest define?" without the manifest being populated.

---

## 4. Architecture (current)

```
┌────────────────────────────────────────────────────────────┐
│                  HF SPACE (sdk: docker, port 7860)         │
│                                                            │
│   ┌─────────────────────┐     ┌──────────────────────┐     │
│   │  Streamlit faceplate│ ◄─► │  FastAPI sidecar     │     │
│   │  app.py  :7860      │     │  main_api.py :8000   │     │
│   │  (HUD, Librarian,   │     │   POST /v1/ingest    │     │
│   │   T.I.A. Oracle)    │     │   GET  /v1/query     │     │
│   └─────────────────────┘     └──────────┬───────────┘     │
│                                          │                 │
│                                          ▼                 │
│                            ┌──────────────────────────┐    │
│                            │ services/rag_hub.py      │    │
│                            │  faiss-cpu + sentence-   │    │
│                            │  transformers (MiniLM)   │    │
│                            │  index → data/vector_    │    │
│                            │  store/                  │    │
│                            └──────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
              ▲
              │  hf_sync.yml (push main → HF Space)
              │
        GitHub Actions
```

The sidecar is **co-located** in the same container; both processes are launched by `scripts/start_hub.sh` on container start. The Streamlit faceplate remains the user-facing UI on port 7860; the FastAPI sidecar exposes the API gateway internally on port 8000 (and is reachable via the Streamlit reverse proxy or container-internal calls).

---

## 5. Historical Fixes (chronological)

- **Stability 9,290 → 9,293 audit** — verified `hf_sync.yml` integrity, confirmed `sdk: docker` + port 7860 are correct, identified empty `data/master_harvest/` and missing `/v1/{ingest,query}` endpoints.
- **Master Hub bootstrap (this commit)** — added FastAPI sidecar, FAISS vector store under `data/vector_store/`, populated this INDEX.md, archived 30+ duplicate `*_SUMMARY.md` / `*_QUICKREF.md` files into `docs/archive/session_logs/`.

---

## 6. Re-indexing

```bash
# From repo root, inside the container or a local venv with requirements.txt installed:
python -m services.rag_hub --reindex

# Or via the API (after the sidecar is up):
curl -X POST http://localhost:8000/v1/ingest -H 'Content-Type: application/json' -d '{"reindex": true}'
curl 'http://localhost:8000/v1/query?q=harvest+workflow&k=5'
```
