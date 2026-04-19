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
* ``POST /v1/system/commit`` — T.I.A. Master Coder pipeline. Receives raw file
                                contents from the Vercel command deck and
                                commits them to the DJ-Goana-Coding org via
                                the GitHub Contents API. Authenticated with
                                ``HF_TOKEN`` (header ``X-HF-Token``); commits
                                are pushed using ``GH_TOKEN``.
* ``GET  /v1/system/tunnels`` — Reachability probe for the Hugging Face,
                                Google Drive and GitHub tunnels plus the
                                presence (never the value) of ``HF_TOKEN``
                                and ``GH_TOKEN``. The "Green Light" panel
                                for the Vercel HUD.
"""

from __future__ import annotations

import base64
import hmac
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Optional

import requests
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.rag_hub import get_hub

logger = logging.getLogger("main_api")


def _preflight_token_check() -> None:
    """Log whether HF_TOKEN and GH_TOKEN are configured.

    Only the *presence* (boolean) is ever logged — never the token value or
    any prefix/suffix of it. This lets the Vercel HUD fail-fast on missing
    credentials instead of waiting for a 503 on first commit attempt.
    """
    hf_present = bool(os.getenv("HF_TOKEN"))
    gh_present = bool(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN"))
    logger.info(
        "preflight: HF_TOKEN=%s GH_TOKEN=%s",
        "present" if hf_present else "missing",
        "present" if gh_present else "missing",
    )


@asynccontextmanager
async def _lifespan(_app: FastAPI):
    _preflight_token_check()
    yield


app = FastAPI(
    title="CITADEL OMEGA — Master Hub API",
    description=(
        "FastAPI sidecar for the Mapping-and-Inventory HF Space. "
        "Exposes /v1/ingest and /v1/query backed by a local FAISS index over "
        "Master Harvest fragments."
    ),
    version="1.0.0",
    lifespan=_lifespan,
)


# ---------------------------------------------------------------------------
# CORS — Citadel Command Deck (Vercel) is the absolute command face.
# ---------------------------------------------------------------------------

# Permanent allow-list. The Vercel command deck URL MUST be present with no
# trailing slash so browser preflights succeed for the live operator UI.
CITADEL_COMMAND_DECK_ORIGIN = "https://citadel-nexus-private.vercel.app"

ALLOWED_ORIGINS: List[str] = [
    CITADEL_COMMAND_DECK_ORIGIN,
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:7860",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# T.I.A. Master Coder pipeline — GitHub commit bridge
# ---------------------------------------------------------------------------

GITHUB_API = "https://api.github.com"
DEFAULT_GH_ORG = "DJ-Goana-Coding"


def _require_hf_token(
    x_hf_token: Optional[str] = Header(default=None, alias="X-HF-Token"),
    authorization: Optional[str] = Header(default=None),
) -> str:
    """Authenticate the Vercel command deck via the operator's ``HF_TOKEN``.

    Accepts the token in either the ``X-HF-Token`` header or a standard
    ``Authorization: Bearer <token>`` header. Comparison is constant-time.
    """
    expected = os.getenv("HF_TOKEN")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="HF_TOKEN is not configured on the server.",
        )

    presented = x_hf_token
    if not presented and authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value:
            presented = value

    if not presented or not hmac.compare_digest(presented, expected):
        raise HTTPException(status_code=401, detail="Invalid or missing HF_TOKEN.")
    return presented


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


class CommitFile(BaseModel):
    path: str = Field(..., description="Repository-relative file path, e.g. 'src/app.py'.")
    content: str = Field(..., description="Raw file content (UTF-8 text).")


class CommitRequest(BaseModel):
    repo: str = Field(..., description="Target repository name within the DJ-Goana-Coding org.")
    message: str = Field(..., description="Commit message.")
    files: List[CommitFile] = Field(..., min_length=1, description="Files to create or update.")
    branch: Optional[str] = Field(default=None, description="Target branch (defaults to repo default branch).")
    owner: str = Field(default=DEFAULT_GH_ORG, description="Repository owner / organization.")


class CommitFileResult(BaseModel):
    path: str
    status: str
    sha: Optional[str] = None
    commit_sha: Optional[str] = None
    html_url: Optional[str] = None
    detail: Optional[str] = None


class CommitResponse(BaseModel):
    repo: str
    branch: Optional[str]
    results: List[CommitFileResult]


class TunnelStatus(BaseModel):
    name: str
    url: str
    status: str  # "ok" | "unreachable" | "auth_required"
    http_status: Optional[int] = None
    detail: Optional[str] = None


class TunnelsResponse(BaseModel):
    huggingface: TunnelStatus
    gdrive: TunnelStatus
    github: TunnelStatus
    tokens: dict


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


# ---------------------------------------------------------------------------
# T.I.A. Master Coder — POST /v1/system/commit
# ---------------------------------------------------------------------------


def _github_headers(gh_token: str) -> dict:
    return {
        "Authorization": f"Bearer {gh_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "citadel-omega-master-hub",
    }


def _commit_one_file(
    *,
    owner: str,
    repo: str,
    path: str,
    content: str,
    message: str,
    branch: Optional[str],
    gh_token: str,
    timeout: float = 30.0,
) -> CommitFileResult:
    """Create or update a single file via the GitHub Contents API."""
    api_url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    headers = _github_headers(gh_token)

    # Look up existing SHA so we can update rather than 422.
    existing_sha: Optional[str] = None
    get_params = {"ref": branch} if branch else None
    try:
        get_resp = requests.get(api_url, headers=headers, params=get_params, timeout=timeout)
    except requests.RequestException as exc:
        return CommitFileResult(path=path, status="error", detail=f"GET failed: {exc}")
    if get_resp.status_code == 200:
        try:
            existing_sha = get_resp.json().get("sha")
        except ValueError:
            existing_sha = None
    elif get_resp.status_code not in (404,):
        return CommitFileResult(
            path=path,
            status="error",
            detail=f"GitHub GET returned status {get_resp.status_code}",
        )

    payload: dict = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
    }
    if branch:
        payload["branch"] = branch
    if existing_sha:
        payload["sha"] = existing_sha

    try:
        put_resp = requests.put(api_url, headers=headers, json=payload, timeout=timeout)
    except requests.RequestException as exc:
        return CommitFileResult(path=path, status="error", detail=f"PUT failed: {exc}")

    if put_resp.status_code in (200, 201):
        body = put_resp.json() if put_resp.content else {}
        content_meta = body.get("content") or {}
        commit_meta = body.get("commit") or {}
        return CommitFileResult(
            path=path,
            status="updated" if existing_sha else "created",
            sha=content_meta.get("sha"),
            commit_sha=commit_meta.get("sha"),
            html_url=content_meta.get("html_url"),
        )

    return CommitFileResult(
        path=path,
        status="error",
        detail=f"GitHub PUT returned status {put_resp.status_code}",
    )


@app.post("/v1/system/commit", response_model=CommitResponse)
def system_commit(
    req: CommitRequest,
    _hf_token: str = Depends(_require_hf_token),
) -> CommitResponse:
    """Commit raw code from the Vercel command deck to GitHub.

    Authenticated via ``HF_TOKEN``; pushes are performed using ``GH_TOKEN``
    against the configured organization (default ``DJ-Goana-Coding``).
    """
    gh_token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")
    if not gh_token:
        raise HTTPException(
            status_code=503,
            detail="GH_TOKEN is not configured on the server.",
        )

    # Defensive path validation — block traversal, absolute paths, backslashes,
    # control chars, and any '..' fragment anywhere in a segment.
    for f in req.files:
        norm = f.path.strip()
        segments = norm.split("/")
        invalid = (
            not norm
            or norm.startswith("/")
            or "\\" in norm
            or any(ord(c) < 0x20 for c in norm)
            or any(seg in ("", ".", "..") for seg in segments)
            or any(".." in seg for seg in segments)
        )
        if invalid:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file path: {f.path!r}",
            )

    results = [
        _commit_one_file(
            owner=req.owner,
            repo=req.repo,
            path=f.path,
            content=f.content,
            message=req.message,
            branch=req.branch,
            gh_token=gh_token,
        )
        for f in req.files
    ]

    return CommitResponse(repo=req.repo, branch=req.branch, results=results)


# ---------------------------------------------------------------------------
# Tunnel reachability probe — GET /v1/system/tunnels
# ---------------------------------------------------------------------------


def _probe_tunnel(name: str, url: str, timeout: float = 2.0) -> TunnelStatus:
    """HEAD-probe an upstream tunnel and classify the result.

    Any 2xx/3xx response is "ok". 401/403 is "auth_required" (the tunnel is
    reachable, credentials are the only thing missing). Anything else —
    timeouts, DNS errors, connection refused — is "unreachable".
    """
    try:
        resp = requests.head(url, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        return TunnelStatus(name=name, url=url, status="unreachable", detail=str(exc))

    code = resp.status_code
    if 200 <= code < 400:
        status = "ok"
    elif code in (401, 403):
        status = "auth_required"
    else:
        status = "unreachable"
    return TunnelStatus(name=name, url=url, status=status, http_status=code)


@app.get("/v1/system/tunnels", response_model=TunnelsResponse)
def system_tunnels() -> TunnelsResponse:
    """Reachability probe for the three Vercel-HUD "Green Light" tunnels.

    Probes Hugging Face, Google Drive, and GitHub with a short HEAD request
    and reports per-tunnel status alongside the presence (never the value) of
    ``HF_TOKEN`` and ``GH_TOKEN``.
    """
    return TunnelsResponse(
        huggingface=_probe_tunnel("huggingface", "https://huggingface.co/"),
        gdrive=_probe_tunnel("gdrive", "https://www.googleapis.com/drive/v3/about"),
        github=_probe_tunnel("github", "https://api.github.com/"),
        tokens={
            "hf_token": bool(os.getenv("HF_TOKEN")),
            "gh_token": bool(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
        },
    )
