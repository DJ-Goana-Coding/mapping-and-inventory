"""
main_api.py — FastAPI sidecar for the Master Hub.

Runs alongside the Streamlit faceplate (app.py) inside the same HF Space
container. Streamlit owns port 7860 (the user-facing UI); this sidecar owns
port 8000 (the API gateway). They are launched together by
``scripts/start_hub.sh`` which is the container CMD.

Endpoints
---------
* ``GET  /healthz``        — liveness probe.
* ``GET  /v1/stats``       — index introspection.
* ``POST /v1/ingest``      — (re)build the FAISS index over Master Harvest
                              fragments. Optional body: ``{"reindex": true,
                              "extra_paths": ["docs/extra/*.md"]}``.
* ``GET  /v1/query``       — semantic search across all indexed fragments.
                              Query params: ``q`` (required), ``k`` (default 5).
* ``POST /v1/query``       — same as GET, JSON body ``{"q": ..., "k": ...}``.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

from services.rag_hub import get_hub

logger = logging.getLogger("main_api")

app = FastAPI(
    title="CITADEL OMEGA — Master Hub API",
    description=(
        "FastAPI sidecar for the Mapping-and-Inventory HF Space. "
        "Exposes /v1/ingest and /v1/query backed by a local FAISS index over "
        "Master Harvest fragments."
    ),
    version="1.0.0",
)


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class IngestRequest(BaseModel):
    reindex: bool = Field(
        default=True,
        description="Rebuild the FAISS index from disk. Currently the only supported mode.",
    )
    extra_paths: Optional[List[str]] = Field(
        default=None,
        description="Additional glob patterns (relative to repo root) to include in the index.",
    )


class IngestResponse(BaseModel):
    status: str
    fragments: List[str]
    chunks_indexed: int
    dim: Optional[int] = None


class QueryRequest(BaseModel):
    q: str
    k: int = 5


class QueryHit(BaseModel):
    source: str
    chunk_index: int
    score: float
    text: str


class QueryResponse(BaseModel):
    query: str
    k: int
    hits: List[QueryHit]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/healthz")
def healthz() -> dict:
    return {"status": "ok"}


@app.get("/v1/stats")
def stats() -> dict:
    return get_hub().stats()


@app.post("/v1/ingest", response_model=IngestResponse)
def ingest(req: Optional[IngestRequest] = None) -> IngestResponse:
    payload = req or IngestRequest()
    if not payload.reindex:
        raise HTTPException(
            status_code=400,
            detail="Only reindex=true is supported in this build.",
        )
    try:
        result = get_hub().reindex(extra_paths=payload.extra_paths)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Reindex failed")
        raise HTTPException(status_code=500, detail=f"reindex failed: {exc}") from exc
    return IngestResponse(
        status="ok",
        fragments=result.get("fragments", []),
        chunks_indexed=int(result.get("chunks_indexed", 0)),
        dim=result.get("dim"),
    )


def _run_query(q: str, k: int) -> QueryResponse:
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="query 'q' must not be empty")
    if k <= 0 or k > 50:
        raise HTTPException(status_code=400, detail="k must be in [1, 50]")
    hub = get_hub()
    hits = hub.query(q, k=k)
    return QueryResponse(
        query=q,
        k=k,
        hits=[QueryHit(**h.to_dict()) for h in hits],
    )


@app.get("/v1/query", response_model=QueryResponse)
def query_get(
    q: str = Query(..., description="Natural-language query"),
    k: int = Query(5, ge=1, le=50),
) -> QueryResponse:
    return _run_query(q, k)


@app.post("/v1/query", response_model=QueryResponse)
def query_post(req: QueryRequest) -> QueryResponse:
    return _run_query(req.q, req.k)
