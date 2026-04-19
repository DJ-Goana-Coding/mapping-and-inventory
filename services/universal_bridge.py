"""
services/universal_bridge.py — Spoke-agnostic RAG data receiver.

Any spoke node in the Citadel Mesh can POST its RAG payload to the Librarian
Hub using this receiver.  The handler is deliberately permissive about header
naming (case-insensitive, underscore/hyphen agnostic) and about the shape of
the JSON body so that Termux-built clients, Vercel edge functions, and GitHub
Actions workflows can all reach the Hub without custom adapters.

Registration
------------
Add to ``main_api.py``::

    from services.universal_bridge import router as bridge_router
    app.include_router(bridge_router)

Endpoints
---------
POST /v1/bridge/ingest
    Receive a RAG payload from any spoke.  Writes the payload to
    ``data/spoke_artifacts/<spoke_name>/`` and queues a FAISS reindex if
    content-bearing text fragments are included.

GET  /v1/bridge/spokes
    Return the current spoke registry (spoke name → last-seen metadata).

POST /v1/bridge/heartbeat
    Lightweight ping from a spoke.  Updates last-seen timestamp only.

Authentication
--------------
The Hub validates the ``X-Spoke-Token``, ``X-Hub-Token``, or ``Authorization``
header against the ``SPOKE_SHARED_SECRET`` environment variable.  If the
variable is not set the endpoint is open (development mode — warn in logs).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import re
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, Request
from pydantic import BaseModel, Field

logger = logging.getLogger("universal_bridge")

router = APIRouter(tags=["spoke-bridge"])

REPO_ROOT = Path(__file__).resolve().parent.parent
SPOKE_ARTIFACTS_DIR = REPO_ROOT / "data" / "spoke_artifacts"
SPOKE_REGISTRY_PATH = REPO_ROOT / "data" / "spoke_sync_registry.json"

_registry_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Header normalisation helpers
# ---------------------------------------------------------------------------

_HEADER_ALIASES: Dict[str, List[str]] = {
    "spoke_token": [
        "x-spoke-token", "x_spoke_token",
        "x-hub-token",   "x_hub_token",
        "authorization",
    ],
    "spoke_name": [
        "x-spoke-name", "x_spoke_name",
        "x-node-name",  "x_node_name",
        "x-device-id",  "x_device_id",
    ],
    "spoke_url": [
        "x-spoke-url",  "x_spoke_url",
        "x-repo-url",   "x_repo_url",
        "x-source-url", "x_source_url",
    ],
}


def _normalise_headers(raw: dict) -> Dict[str, str]:
    """Return a flat dict with normalised (lowercase, underscored) keys."""
    return {
        re.sub(r"[-\s]+", "_", k.lower().strip()): v
        for k, v in raw.items()
    }


def _extract_header(normalised: Dict[str, str], canonical: str) -> Optional[str]:
    """Return the first non-empty value for *canonical* from alias list."""
    for alias in _HEADER_ALIASES.get(canonical, [canonical]):
        v = normalised.get(alias)
        if v:
            # Strip Bearer prefix for auth headers
            if alias == "authorization":
                scheme, _, token = v.partition(" ")
                if scheme.lower() == "bearer" and token:
                    return token
                return None
            return v
    return None


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------


def _verify_spoke_token(token: Optional[str]) -> bool:
    """Constant-time check against SPOKE_SHARED_SECRET.

    Returns True if secret is unconfigured (open mode) or if the token matches.
    """
    secret = os.getenv("SPOKE_SHARED_SECRET")
    if not secret:
        logger.warning(
            "SPOKE_SHARED_SECRET not set — bridge running in OPEN mode. "
            "Any caller can POST to /v1/bridge/ingest."
        )
        return True
    if not token:
        return False
    return hmac.compare_digest(token.strip(), secret.strip())


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def _load_registry() -> dict:
    if SPOKE_REGISTRY_PATH.exists():
        try:
            return json.loads(SPOKE_REGISTRY_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    return {
        "registry_version": "2.0.0",
        "hub": "mapping-and-inventory",
        "last_updated": "",
        "total_spokes": 0,
        "spokes": {},
    }


def _save_registry(reg: dict) -> None:
    SPOKE_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    reg["last_updated"] = datetime.now(timezone.utc).isoformat()
    reg["total_spokes"] = len(reg.get("spokes", {}))
    SPOKE_REGISTRY_PATH.write_text(
        json.dumps(reg, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def _update_registry(name: str, url: str, meta: dict) -> None:
    with _registry_lock:
        reg = _load_registry()
        existing = reg["spokes"].get(name, {})
        reg["spokes"][name] = {
            **existing,
            "name": name,
            "url": url,
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "sync_count": existing.get("sync_count", 0) + 1,
            **{k: v for k, v in meta.items() if k not in ("name", "url")},
        }
        _save_registry(reg)


# ---------------------------------------------------------------------------
# Background reindex
# ---------------------------------------------------------------------------


def _maybe_reindex(spoke_name: str, fragments: List[str]) -> None:
    """If text fragments were included, write them and trigger a reindex."""
    if not fragments:
        return
    try:
        from services.rag_hub import get_hub  # lazy import to stay test-friendly
        safe_dir_name = re.sub(r"[^\w\-]", "_", spoke_name)[:64]
        spoke_dir = SPOKE_ARTIFACTS_DIR / safe_dir_name
        spoke_dir.mkdir(parents=True, exist_ok=True)
        harvest_path = spoke_dir / "rag_fragments.txt"
        harvest_path.write_text("\n\n---\n\n".join(fragments), encoding="utf-8")
        logger.info("Wrote %d fragment(s) from %s → %s", len(fragments), spoke_name, harvest_path)
        # Trigger full reindex so new spoke content enters the FAISS index.
        hub = get_hub()
        result = hub.reindex(extra_paths=[str(harvest_path.relative_to(REPO_ROOT))])
        logger.info(
            "Reindex after spoke '%s' ingest: %d chunks from %d fragments",
            spoke_name,
            result.get("chunks_indexed", 0),
            len(result.get("fragments", [])),
        )
    except Exception:  # noqa: BLE001
        logger.exception("Background reindex after spoke ingest failed")


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------


class SpokeIngestPayload(BaseModel):
    """Flexible ingest payload — all fields except ``spoke_name`` are optional."""

    spoke_name: str = Field(..., description="Unique identifier for the sending node.")
    spoke_url: str = Field(default="", description="GitHub / HF Space URL of the spoke.")
    fragments: List[str] = Field(
        default_factory=list,
        description="Raw text fragments to add to the Librarian's FAISS index.",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary metadata stored in the spoke registry.",
    )
    artifacts: Dict[str, str] = Field(
        default_factory=dict,
        description="Named file payloads (filename → UTF-8 text content) to persist.",
    )


class SpokeHeartbeatPayload(BaseModel):
    spoke_name: str
    status: str = "ok"
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@router.post("/v1/bridge/ingest", status_code=202)
async def bridge_ingest(
    request: Request,
    background_tasks: BackgroundTasks,
) -> dict:
    """Receive a RAG payload from any spoke node.

    Accepts ``application/json`` with any of the fields defined in
    :class:`SpokeIngestPayload`.  The ``spoke_name`` can also come from the
    ``X-Spoke-Name`` (or equivalent) header if absent from the body.

    All header lookups are case-insensitive and hyphen/underscore agnostic.
    """
    norm = _normalise_headers(dict(request.headers))
    token = _extract_header(norm, "spoke_token")
    if not _verify_spoke_token(token):
        raise HTTPException(status_code=401, detail="Invalid or missing spoke token.")

    try:
        body: Dict[str, Any] = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Request body must be valid JSON.")

    # spoke_name can come from body or from header
    spoke_name = body.get("spoke_name") or _extract_header(norm, "spoke_name")
    if not spoke_name:
        raise HTTPException(status_code=400, detail="spoke_name is required (body or header).")

    spoke_url = body.get("spoke_url", "") or _extract_header(norm, "spoke_url") or ""
    fragments: List[str] = body.get("fragments", [])
    artifacts: Dict[str, str] = body.get("artifacts", {})
    metadata: Dict[str, Any] = body.get("metadata", {})

    # Sanitise spoke_name to a safe directory component (alphanumeric, hyphens, underscores).
    safe_spoke_dir_name = re.sub(r"[^\w\-]", "_", spoke_name)[:64]

    # Persist named artifact files
    if artifacts:
        spoke_dir = SPOKE_ARTIFACTS_DIR / safe_spoke_dir_name
        spoke_dir.mkdir(parents=True, exist_ok=True)
        for filename, content in artifacts.items():
            # Strip directory components, then remove any characters outside
            # a safe allowlist so the final path stays within spoke_dir.
            safe_name = re.sub(r"[^\w\-.]", "_", Path(filename).name)[:128]
            if not safe_name or safe_name.startswith("."):
                # Skip hidden or empty filenames
                continue
            artifact_path = spoke_dir / safe_name
            # Final guard: confirm resolved path is still inside spoke_dir.
            if spoke_dir not in artifact_path.resolve().parents and artifact_path.resolve() != spoke_dir:
                logger.warning("Rejected artifact path escape attempt: %s", filename)
                continue
            artifact_path.write_text(content, encoding="utf-8")
        logger.info("Wrote %d artifact(s) for spoke '%s'", len(artifacts), spoke_name)

    # Update registry
    _update_registry(spoke_name, spoke_url, {**metadata, "fragments_received": len(fragments)})

    # Queue reindex in background
    if fragments:
        background_tasks.add_task(_maybe_reindex, spoke_name, fragments)

    return {
        "accepted": True,
        "spoke": spoke_name,
        "fragments_queued": len(fragments),
        "artifacts_saved": len(artifacts),
        "reindex": "queued" if fragments else "skipped",
    }


@router.get("/v1/bridge/spokes")
def bridge_spokes() -> dict:
    """Return the current spoke registry."""
    with _registry_lock:
        reg = _load_registry()
    return reg


@router.post("/v1/bridge/heartbeat", status_code=202)
async def bridge_heartbeat(
    request: Request,
) -> dict:
    """Lightweight liveness ping from a spoke.

    Updates last-seen timestamp in the registry without triggering a reindex.
    """
    norm = _normalise_headers(dict(request.headers))
    token = _extract_header(norm, "spoke_token")
    if not _verify_spoke_token(token):
        raise HTTPException(status_code=401, detail="Invalid or missing spoke token.")

    try:
        body: Dict[str, Any] = await request.json()
    except Exception:
        body = {}

    spoke_name = body.get("spoke_name") or _extract_header(norm, "spoke_name") or "unknown"
    spoke_url = body.get("spoke_url", "") or ""
    status = body.get("status", "ok")

    _update_registry(spoke_name, spoke_url, {"heartbeat_status": status})

    return {
        "accepted": True,
        "spoke": spoke_name,
        "status": status,
        "hub_time": datetime.now(timezone.utc).isoformat(),
    }
