"""
core/bridge_protocol.py — Cross-Spoke Routing for S10 Phalanx

Provides secure query helpers that allow the Phalanx node to reach the
other spokes in the Hub-and-Spoke network.  All endpoint URLs are sourced
exclusively from environment variables (via ``os.environ.get()``) so that
no credentials are ever hard-coded (Ghost Protocol / Zero-Overwrite).

Spokes registered here:
* Legal Clearance  — Psinergy-Gate   (``HF_SPACE_CGAL_CORE``)
* Swarm Momentum   — Omega Scout     (``HF_SPACE_OMEGA_SCOUT``)
"""
from __future__ import annotations

import logging
import os
from typing import Any

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment-variable keys (never hard-code actual values)
# ---------------------------------------------------------------------------
_ENV_CGAL_CORE: str = "HF_SPACE_CGAL_CORE"
_ENV_OMEGA_SCOUT: str = "HF_SPACE_OMEGA_SCOUT"


def _get_endpoint(env_key: str) -> str | None:
    """Return the HF Space endpoint URL stored in *env_key*, or None."""
    url = os.environ.get(env_key)
    if not url:
        logger.warning("Environment variable '%s' is not set — spoke unreachable.", env_key)
    return url


def query_cgal_core(payload: dict[str, Any], timeout: int = 30) -> dict[str, Any] | None:
    """
    Send *payload* to the Legal Clearance spoke (Psinergy-Gate / CGAL_Core).

    The target URL is read from ``HF_SPACE_CGAL_CORE``.

    Returns the JSON response dict, or ``None`` on failure.
    """
    url = _get_endpoint(_ENV_CGAL_CORE)
    if not url:
        return None
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        logger.info("CGAL_Core responded with status %s.", response.status_code)
        return response.json()
    except requests.RequestException as exc:
        logger.error("CGAL_Core query failed: %s", exc)
        return None


def query_omega_scout(payload: dict[str, Any], timeout: int = 30) -> dict[str, Any] | None:
    """
    Send *payload* to the Swarm Momentum spoke (Omega Scout).

    The target URL is read from ``HF_SPACE_OMEGA_SCOUT``.

    Returns the JSON response dict, or ``None`` on failure.
    """
    url = _get_endpoint(_ENV_OMEGA_SCOUT)
    if not url:
        return None
    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        logger.info("Omega_Scout responded with status %s.", response.status_code)
        return response.json()
    except requests.RequestException as exc:
        logger.error("Omega_Scout query failed: %s", exc)
        return None


def get_spoke_status() -> dict[str, str]:
    """
    Return a status dict showing which spokes have endpoints configured.

    Useful for health-check endpoints and the Citadel dashboard.
    """
    return {
        "CGAL_Core": "configured" if os.environ.get(_ENV_CGAL_CORE) else "not configured",
        "Omega_Scout": "configured" if os.environ.get(_ENV_OMEGA_SCOUT) else "not configured",
    }
