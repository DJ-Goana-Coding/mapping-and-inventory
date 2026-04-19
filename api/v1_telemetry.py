"""
api/v1_telemetry.py — Full JSON status reporter for the Vercel HUD.

This module provides a FastAPI ``APIRouter`` with a single endpoint:

    GET /v1/telemetry

It aggregates and returns a rich JSON payload covering:
  * Device sync status (Oppo, S10) — last push timestamps, file counts
  * RAG health — FAISS index loaded/chunks/sources
  * Active key count — how many Gemini/HF keys are configured
  * Error logs — last N entries from self-healing log and worker status
  * Spoke registry summary — per-spoke last-seen and health
  * System uptime and version

Registration
------------
In ``main_api.py``::

    from api.v1_telemetry import router as telemetry_v1
    app.include_router(telemetry_v1)

The existing ``GET /v1/system/status`` (from ``telemetry_bridge.py``) remains
the lightweight "Green Light" panel.  This endpoint is the full diagnostic
dump for the Admiral HUD.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["telemetry-v1"])

REPO_ROOT = Path(__file__).resolve().parent.parent
_BOOT_TIME = time.monotonic()
_VERSION = "1.0.0"

# Paths
_WORKER_STATUS = REPO_ROOT / "worker_status.json"
_SPOKE_REGISTRY = REPO_ROOT / "data" / "spoke_sync_registry.json"
_HEAL_LOG = REPO_ROOT / "data" / "monitoring" / "self_healing_log.json"
_VACUUM_MANIFEST = REPO_ROOT / "data" / "vacuum_manifest.json"
_SHARD_MANIFEST = REPO_ROOT / "data" / "shards" / "shard_manifest.json"

_DEVICE_DIRS = {
    "oppo": ["Partition_01", "Partition_02", "Partition_03", "Partition_04", "Partition_46"],
    "s10": ["S10_CITADEL_OMEGA_INTEL", "Research/S10"],
}

_GEMINI_KEY_PREFIXES = ["GEMINI_API_KEY", "GEMINI_API_KEY_2", "GEMINI_API_KEY_3", "GEMINI_API_KEY_4"]
_HF_KEY_PREFIXES = ["HF_TOKEN", "HF_TOKEN_2"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_json(path: Path) -> Optional[dict]:
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return None


def _count_files(directory: Path) -> int:
    if not directory.is_dir():
        return 0
    return sum(
        1 for p in directory.rglob("*")
        if p.is_file() and p.name not in (".gitkeep",) and not p.name.startswith(".")
    )


def _device_sync_status() -> Dict[str, Any]:
    """Return per-device file counts and last-push timestamp from worker_status."""
    ws = _read_json(_WORKER_STATUS) or {}
    sync_status = ws.get("sync_status", {})
    result: Dict[str, Any] = {}

    for device, dirs in _DEVICE_DIRS.items():
        total_files = sum(_count_files(REPO_ROOT / d) for d in dirs)
        last_push = sync_status.get(f"{device}_last_push") or sync_status.get(f"{device.upper()}_last_push")
        result[device] = {
            "directories": dirs,
            "total_files": total_files,
            "last_push": last_push,
        }
    return result


def _rag_health() -> Dict[str, Any]:
    """Return RAG index stats without importing heavy ML deps unless already loaded."""
    try:
        from services.rag_hub import get_hub  # noqa: PLC0415
        hub = get_hub()
        stats = hub.stats()
        return {
            "loaded": stats.get("loaded", False),
            "chunks": stats.get("chunks", 0),
            "sources": stats.get("sources", []),
            "model": stats.get("model", ""),
            "vector_store_dir": stats.get("vector_store_dir", ""),
        }
    except Exception as exc:  # noqa: BLE001
        return {"loaded": False, "chunks": 0, "sources": [], "error": str(exc)}


def _active_key_count() -> Dict[str, Any]:
    """Count how many API keys are configured per service."""
    gemini_count = sum(1 for k in _GEMINI_KEY_PREFIXES if os.getenv(k))
    # Also count comma-separated bundle
    bundle = os.getenv("GEMINI_API_KEYS", "")
    if bundle:
        gemini_count += len([k.strip() for k in bundle.split(",") if k.strip()])

    hf_count = sum(1 for k in _HF_KEY_PREFIXES if os.getenv(k))
    hf_bundle = os.getenv("HF_TOKENS", "")
    if hf_bundle:
        hf_count += len([k.strip() for k in hf_bundle.split(",") if k.strip()])

    return {
        "gemini": gemini_count,
        "hf_token": hf_count,
        "gh_token": 1 if (os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN")) else 0,
        "spoke_shared_secret": 1 if os.getenv("SPOKE_SHARED_SECRET") else 0,
        "github_webhook_secret": 1 if os.getenv("GITHUB_WEBHOOK_SECRET") else 0,
        "gdrive_service_account": 1 if os.getenv("GDRIVE_SERVICE_ACCOUNT_JSON") else 0,
    }


def _error_logs(max_entries: int = 20) -> List[Dict[str, Any]]:
    """Return the last N error records from self-healing log and worker status."""
    errors: List[Dict[str, Any]] = []

    # Self-healing log
    heal = _read_json(_HEAL_LOG) or {}
    for record in heal.get("records", [])[-max_entries:]:
        if record.get("hf_status") not in ("healthy", "no_space"):
            errors.append({
                "source": "self_healing",
                "spoke": record.get("spoke_name"),
                "timestamp": record.get("checked_at"),
                "hf_status": record.get("hf_status"),
                "hf_http_code": record.get("hf_http_code"),
                "heal_outcome": record.get("heal_outcome"),
            })

    # Worker status errors
    ws = _read_json(_WORKER_STATUS) or {}
    for worker_id, wdata in ws.get("workers", {}).items():
        for err in wdata.get("errors", []):
            errors.append({
                "source": f"worker:{worker_id}",
                "timestamp": wdata.get("last_run"),
                "error": err,
            })

    errors.sort(key=lambda e: e.get("timestamp") or "", reverse=True)
    return errors[:max_entries]


def _spoke_registry_summary() -> Dict[str, Any]:
    """Return per-spoke last-seen and sync count from the spoke registry."""
    reg = _read_json(_SPOKE_REGISTRY) or {}
    spokes = reg.get("spokes", {})
    summary = {
        "total": len(spokes),
        "spokes": {},
    }
    for name, info in spokes.items():
        summary["spokes"][name] = {  # type: ignore[index]
            "last_seen": info.get("last_sync") or info.get("last_seen"),
            "sync_count": info.get("sync_count", 0),
            "status": info.get("sync_status") or info.get("heartbeat_status") or "unknown",
            "url": info.get("url") or info.get("repo_url"),
        }
    return summary


def _shard_summary() -> Dict[str, Any]:
    """Return domain shard stats if the vacuum has run."""
    manifest = _read_json(_SHARD_MANIFEST)
    if not manifest:
        return {"available": False}
    domains = manifest.get("domains", {})
    return {
        "available": True,
        "total_files": manifest.get("total_files", 0),
        "generated_at": manifest.get("generated_at"),
        "domains": {
            dom: {
                "file_count": stats.get("file_count", 0),
                "total_bytes": stats.get("total_bytes", 0),
            }
            for dom, stats in domains.items()
            if stats.get("file_count", 0) > 0
        },
    }


# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------


class TelemetryResponse(BaseModel):
    version: str
    uptime_s: float
    timestamp: str
    device_sync: Dict[str, Any]
    rag_health: Dict[str, Any]
    active_keys: Dict[str, Any]
    error_logs: List[Dict[str, Any]]
    spoke_registry: Dict[str, Any]
    shard_summary: Dict[str, Any]
    worker_status_available: bool


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------


@router.get("/v1/telemetry", response_model=TelemetryResponse)
def get_telemetry() -> TelemetryResponse:
    """Full diagnostic dump for the Vercel Admiral HUD.

    Aggregates all subsystem health into a single response:
    - ``device_sync`` — Oppo/S10 file counts and last push timestamps
    - ``rag_health`` — FAISS index state
    - ``active_keys`` — count of configured API keys per service
    - ``error_logs`` — last 20 errors from self-healing and workers
    - ``spoke_registry`` — every registered spoke with last-seen
    - ``shard_summary`` — domain vacuum shard counts (TECH/BIO/LEGAL/TRADE)

    Values are **never** secrets — only counts and booleans for tokens.
    """
    return TelemetryResponse(
        version=_VERSION,
        uptime_s=round(time.monotonic() - _BOOT_TIME, 1),
        timestamp=datetime.now(timezone.utc).isoformat(),
        device_sync=_device_sync_status(),
        rag_health=_rag_health(),
        active_keys=_active_key_count(),
        error_logs=_error_logs(),
        spoke_registry=_spoke_registry_summary(),
        shard_summary=_shard_summary(),
        worker_status_available=_WORKER_STATUS.exists(),
    )
