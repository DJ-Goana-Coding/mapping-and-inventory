"""
telemetry_bridge.py — FastAPI APIRouter for /v1/system/status.

Exposes an aggregate health and RAG-state snapshot for the Librarian Hub
so the Vercel Command Deck and remote Citadel nodes can assess system
readiness in a single call. Also accepts inbound spoke-node telemetry
reports via POST so every repo can report its tunnel state to the Hub.

Usage
-----
Register this router in main_api.py::

    from telemetry_bridge import router as telemetry_router
    app.include_router(telemetry_router)

Endpoints
---------
GET /v1/system/status
    Returns a JSON object with:
    - ``rag``       — FAISS index stats (chunks, sources, loaded flag)
    - ``tunnels``   — reachability of HF / GDrive / GitHub (HEAD probes)
    - ``tokens``    — boolean presence of HF_TOKEN / GH_TOKEN /
                      CITADEL_ACCESS / ALLOWED_ORIGINS (never values)
    - ``devices``   — detected device intel directories and file counts
    - ``recent_reports`` — most recent inbound spoke telemetry reports
    - ``uptime_s``  — seconds since this process started
    - ``api_version`` — semver string

POST /v1/system/status
    Inbound spoke-node telemetry report (SOVEREIGN_HUD_ALIGNMENT v26.59
    SECRET_MIRROR_VALIDATION). Authenticated via the ``X-Citadel-Access``
    header matched against the ``CITADEL_ACCESS`` env secret using a
    constant-time compare. Body schema::

        { "repo": "<repo-name>", "status": "<status-string>",
          "tunnel": "active" | "inactive" | "<custom>" }

    Responses are kept in an in-memory ring buffer surfaced through the
    GET endpoint.
"""
from __future__ import annotations

import hmac
import os
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Deque, Dict, List, Optional

import requests
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from services.rag_hub import DEVICE_FRAGMENT_GLOBS, REPO_ROOT, get_hub

router = APIRouter()

_BOOT_TIME = time.monotonic()
_API_VERSION = "1.0.0"

# Device intel directories whose presence and file-count we surface.
_DEVICE_DIRS = (
    "S10_CITADEL_OMEGA_INTEL",
    "Partition_01",
    "Partition_02",
    "Partition_03",
    "Partition_04",
    "Partition_46",
    "Research/S10",
)


# ---------------------------------------------------------------------------
# In-memory spoke telemetry ring buffer
# ---------------------------------------------------------------------------

# Bounded ring buffer of the most recent spoke reports. Cheap, lock-guarded,
# and reset on process restart by design — durable persistence belongs to the
# Librarian's worker pipeline, not this lightweight HUD bridge.
_REPORT_BUFFER_MAX = 64
# How many of the most recent spoke reports to surface in GET /v1/system/status.
_RECENT_REPORTS_DISPLAY_LIMIT = 16
_report_buffer: Deque[Dict[str, object]] = deque(maxlen=_REPORT_BUFFER_MAX)
_report_lock = Lock()


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class RagStatus(BaseModel):
    loaded: bool
    chunks: int
    sources: List[str]
    model: str
    vector_store_dir: str


class TunnelStatus(BaseModel):
    name: str
    url: str
    status: str
    http_status: int | None = None
    detail: str | None = None


class DeviceDir(BaseModel):
    path: str
    exists: bool
    file_count: int


class SpokeReportRecord(BaseModel):
    repo: str
    status: str
    tunnel: str
    received_at: str


class SystemStatusResponse(BaseModel):
    api_version: str
    uptime_s: float
    tokens: Dict[str, bool]
    rag: RagStatus
    tunnels: Dict[str, TunnelStatus]
    devices: List[DeviceDir]
    device_glob_count: int
    recent_reports: List[SpokeReportRecord]
    hub: str = "mapping-and-inventory"


class SpokeReportRequest(BaseModel):
    repo: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., min_length=1, max_length=200)
    tunnel: str = Field(..., min_length=1, max_length=64)


class SpokeReportResponse(BaseModel):
    accepted: bool
    hub: str = "mapping-and-inventory"
    received_at: str
    buffered_reports: int


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _probe(name: str, url: str, timeout: float = 2.0) -> TunnelStatus:
    """HEAD-probe a URL and classify the result."""
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


def _count_files(directory: Path) -> int:
    """Count non-hidden, non-gitkeep files in a directory tree."""
    if not directory.is_dir():
        return 0
    return sum(
        1
        for p in directory.rglob("*")
        if p.is_file() and p.name not in (".gitkeep",) and not p.name.startswith(".")
    )


def _validate_citadel_access_header(presented: Optional[str]) -> None:
    """Validate the ``X-Citadel-Access`` header against the ``CITADEL_ACCESS``
    shared secret on inbound spoke reports.

    Comparison is constant-time. A 503 is raised if the hub itself is not
    configured with the secret (so the spoke knows the hub is misconfigured
    rather than silently dropping reports), and 401 if the presented value
    is missing or wrong.
    """
    expected = os.getenv("CITADEL_ACCESS")
    if not expected:
        raise HTTPException(
            status_code=503,
            detail="CITADEL_ACCESS is not configured on the Mapping Hub.",
        )
    if not presented or not hmac.compare_digest(presented, expected):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing CITADEL_ACCESS handshake.",
        )


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.get("/v1/system/status", response_model=SystemStatusResponse)
def system_status() -> SystemStatusResponse:
    """Aggregate health + RAG state for the Citadel Librarian.

    Combines the RAG index stats from ``/v1/stats``, the tunnel probe from
    ``/v1/system/tunnels``, and per-device-directory file counts into one
    response. The Vercel Command Deck uses this as the single "Green Light"
    panel for the entire hub.

    Token values are **never** included — only their boolean presence.
    """
    hub = get_hub()
    raw_stats = hub.stats()

    rag = RagStatus(
        loaded=raw_stats.get("loaded", False),
        chunks=raw_stats.get("chunks", 0),
        sources=raw_stats.get("sources", []),
        model=raw_stats.get("model", ""),
        vector_store_dir=raw_stats.get("vector_store_dir", ""),
    )

    tunnels = {
        "huggingface": _probe("huggingface", "https://huggingface.co/"),
        "gdrive": _probe("gdrive", "https://www.googleapis.com/drive/v3/about"),
        "github": _probe("github", "https://api.github.com/"),
    }

    devices = [
        DeviceDir(
            path=d,
            exists=(REPO_ROOT / d).is_dir(),
            file_count=_count_files(REPO_ROOT / d),
        )
        for d in _DEVICE_DIRS
    ]

    with _report_lock:
        recent = [
            SpokeReportRecord(**r)
            for r in list(_report_buffer)[-_RECENT_REPORTS_DISPLAY_LIMIT:]
        ]

    return SystemStatusResponse(
        api_version=_API_VERSION,
        uptime_s=round(time.monotonic() - _BOOT_TIME, 1),
        tokens={
            "hf_token": bool(os.getenv("HF_TOKEN")),
            "gh_token": bool(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
            "gemini_api_key": bool(os.getenv("GEMINI_API_KEY")),
            "github_webhook_secret": bool(os.getenv("GITHUB_WEBHOOK_SECRET")),
            "citadel_access": bool(os.getenv("CITADEL_ACCESS")),
            "allowed_origins": bool(os.getenv("ALLOWED_ORIGINS")),
        },
        rag=rag,
        tunnels=tunnels,
        devices=devices,
        device_glob_count=len(DEVICE_FRAGMENT_GLOBS),
        recent_reports=recent,
    )


@router.post("/v1/system/status", response_model=SpokeReportResponse)
def submit_spoke_report(
    report: SpokeReportRequest,
    x_citadel_access: Optional[str] = Header(default=None, alias="X-Citadel-Access"),
) -> SpokeReportResponse:
    """Accept a telemetry report from a spoke node.

    SOVEREIGN_HUD_ALIGNMENT v26.59 — SECRET_MIRROR_VALIDATION. Every node
    in the Citadel mesh reports its repo name, status string and tunnel
    state to the Mapping Hub Librarian. Authenticated by the
    ``CITADEL_ACCESS`` shared secret (header ``X-Citadel-Access``) so only
    authorized spokes can post.

    The repo / status / tunnel values from the body are stored verbatim in
    a bounded in-memory ring buffer so the Vercel HUD can render the
    most recent handshakes via ``GET /v1/system/status``.
    """
    _validate_citadel_access_header(x_citadel_access)

    received_at = datetime.now(timezone.utc).isoformat()
    record = {
        "repo": report.repo,
        "status": report.status,
        "tunnel": report.tunnel,
        "received_at": received_at,
    }
    with _report_lock:
        _report_buffer.append(record)
        buffered = len(_report_buffer)

    return SpokeReportResponse(
        accepted=True,
        received_at=received_at,
        buffered_reports=buffered,
    )
