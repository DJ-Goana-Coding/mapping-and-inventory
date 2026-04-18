# Vector Store

This directory holds the FAISS index (`harvest.index`) and chunk metadata (`harvest_meta.json`) used by the Master Hub FastAPI sidecar (`main_api.py`) and `services/rag_hub.py`.

Files here are generated; do not commit them. Rebuild with:

```bash
python -m services.rag_hub --reindex
# or, against the running sidecar:
curl -X POST http://localhost:8000/v1/ingest
```
