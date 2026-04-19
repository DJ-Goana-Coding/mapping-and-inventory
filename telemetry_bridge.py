"""
telemetry_bridge.py — FastAPI APIRouter for GET /v1/system/status.

Exposes an aggregate health and RAG-state snapshot for the Librarian Hub
so the Vercel Command Deck and remote Citadel nodes can assess system
readiness in a single call.

Usage
-----
Register this router in main_api.py::

    from telemetry_bridge import router as telemetry_router
    app.include_router(telemetry_router)

Endpoint
--------
GET /v1/system/status
    Returns a JSON object with:
    - ``rag``       — FAISS index stats (chunks, sources, loaded flag)
    - ``tunnels``   — reachability of HF / GDrive / GitHub (HEAD probes)
    - ``tokens``    — boolean presence of HF_TOKEN and GH_TOKEN (never values)
    - ``devices``   — detected device intel directories and file counts
    - ``uptime_s``  — seconds since this process started
    - ``api_version`` — semver string
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Dict, List

import requests
from fastapi import APIRouter
from pydantic import BaseModel

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


class SystemStatusResponse(BaseModel):
    api_version: str
    uptime_s: float
    tokens: Dict[str, bool]
    rag: RagStatus
    tunnels: Dict[str, TunnelStatus]
    devices: List[DeviceDir]
    device_glob_count: int


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


# ---------------------------------------------------------------------------
# Route
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

    return SystemStatusResponse(
        api_version=_API_VERSION,
        uptime_s=round(time.monotonic() - _BOOT_TIME, 1),
        tokens={
            "hf_token": bool(os.getenv("HF_TOKEN")),
            "gh_token": bool(os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")),
            "gemini_api_key": bool(os.getenv("GEMINI_API_KEY")),
            "github_webhook_secret": bool(os.getenv("GITHUB_WEBHOOK_SECRET")),
        },
        rag=rag,
        tunnels=tunnels,
        devices=devices,
        device_glob_count=len(DEVICE_FRAGMENT_GLOBS),
    )
