"""
Fleet Router — Cross-System Neural Linking
==========================================
Establishes the routing matrix so the Master Brain knows where every
cloud node (Hugging Face Space) lives.  Each entry maps a well-known
environment variable to the URL of its corresponding HF Space, enabling
secure cross-system communication via ``os.environ.get()``.

This module is additive (Zero Hub Overwrite): it does not modify any
``backend/`` logic and introduces no new external dependencies.
"""
from __future__ import annotations

import logging
import os
import pathlib
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Routing matrix — env-var key → HF Space URL
# ---------------------------------------------------------------------------
# Each entry is (env_var_name, system_id, description).
# The actual URL is resolved at runtime from the environment so that no
# secrets are hard-coded in source control.
_ROUTES: list[tuple[str, str, str]] = [
    (
        "HF_SPACE_TIAS_PIONEER",
        "pioneer-trader",
        "Tias Pioneer Trader — quantitative trading and market-analysis pipelines.",
    ),
    (
        "HF_SPACE_SENTINEL_SWARM",
        "perimeter-scout",
        "Tias Sentinel Scout Swarm — distributed perimeter-recon and threat-detection.",
    ),
    (
        "HF_SPACE_CGAL_CORE",
        "CGAL_Core",
        "CGAL Core — legal clearance and compliance gateway (Psinergy-Gate).",
    ),
    (
        "HF_SPACE_OMEGA_TRADER",
        "S10_Phalanx",
        "Omega Trader — momentum and market-sentiment execution node (S10_Phalanx).",
    ),
    (
        "HF_SPACE_OMEGA_SCOUT",
        "perimeter-scout",
        "Omega Scout — swarm intelligence scout for the perimeter-scout system.",
    ),
    (
        "HF_SPACE_HARVESTMOON",
        "Harvestmoon",
        "Harvestmoon — seasonal-cycle harvest and resource-allocation node.",
    ),
    # S10 Spoke — Phalanx nodes (DJ-Goana-Coding/Phalanx_*)
    (
        "HF_SPACE_PHALANX_PIONEER",
        "Phalanx_Pioneer",
        "Phalanx Pioneer — S10 primary trading and analysis spoke.",
    ),
    (
        "HF_SPACE_PHALANX_SHADOW",
        "Phalanx_Shadow",
        "Phalanx Shadow — S10 shadow/backup sector spoke.",
    ),
    (
        "HF_SPACE_PHALANX_VAULT",
        "Phalanx_Vault",
        "Phalanx Vault — S10 AI Vault and model-storage spoke.",
    ),
    # Oppo Spoke — Omega nodes
    (
        "HF_SPACE_OMEGA_ARCHIVE",
        "Oppo_Omega",
        "Omega Archive — Oppo hardware long-term archival and recovery spoke.",
    ),
]

# ---------------------------------------------------------------------------
# Local Bridge — hardware drive map ingestion
# ---------------------------------------------------------------------------
# Default location for local hardware drive maps produced by the sovereign
# nodes.  Override via the ``LOCAL_BRAIN_DUMP_DIR`` environment variable.
_DEFAULT_LOCAL_BRAIN_DUMP: str = "/Local_Brain_Dump"
_DRIVE_MAP_FILES: tuple[str, ...] = ("D_DRIVE_MAP.txt", "E_DRIVE_MAP.txt")


def get_route(env_var: str) -> Optional[str]:
    """
    Return the HF Space URL for the given environment variable key.

    Returns ``None`` when the variable is not set rather than raising, so
    callers can decide whether a missing route is fatal.

    Parameters
    ----------
    env_var:
        One of the well-known ``HF_SPACE_*`` variable names defined in this
        module (e.g. ``"HF_SPACE_TIAS_PIONEER"``).
    """
    url = os.environ.get(env_var)
    if url is None:
        logger.debug("FleetRouter: env var '%s' is not set.", env_var)
    return url


def get_all_routes() -> dict[str, Optional[str]]:
    """
    Return a mapping of every known env-var key to its resolved URL.

    Unset variables appear as ``None`` so callers can detect offline nodes.
    """
    return {env_var: get_route(env_var) for env_var, _, _ in _ROUTES}


def get_system_routes(system_id: str) -> dict[str, Optional[str]]:
    """
    Return all routes that belong to a specific system.

    Parameters
    ----------
    system_id:
        The system identifier (e.g. ``"pioneer-trader"``, ``"Omega"``,
        ``"CGAL_Core"``, ``"perimeter-scout"``, ``"Harvestmoon"``).
    """
    return {
        env_var: get_route(env_var)
        for env_var, sid, _ in _ROUTES
        if sid == system_id
    }


def describe_routes() -> list[dict[str, str]]:
    """
    Return a list of route descriptors (without resolved URLs) suitable for
    logging or manifest generation.
    """
    return [
        {"env_var": env_var, "system_id": system_id, "description": desc}
        for env_var, system_id, desc in _ROUTES
    ]


def log_route_status() -> None:
    """
    Emit an INFO-level log entry for every route showing its online/offline
    status based on whether the environment variable is currently set.
    """
    for env_var, system_id, _ in _ROUTES:
        url = get_route(env_var)
        status = "ONLINE" if url else "OFFLINE (env var not set)"
        logger.info("FleetRouter [%s] %s → %s", system_id, env_var, status)


def ingest_local_drive_maps(
    brain_collection: "chromadb.Collection | None" = None,  # type: ignore[name-defined]
    dump_dir: str | None = None,
) -> dict[str, str | None]:
    """
    Local Bridge — read ``D_DRIVE_MAP.txt`` and ``E_DRIVE_MAP.txt`` from the
    ``/Local_Brain_Dump/`` directory (or the directory specified by the
    ``LOCAL_BRAIN_DUMP_DIR`` environment variable) and optionally index them
    into the brain vault.

    Parameters
    ----------
    brain_collection:
        An open ChromaDB collection returned by ``brain.indexer.get_collection()``.
        When provided the content of each map file is ingested via
        ``brain.indexer.index_text()`` so the local drive topology becomes
        searchable in the RAG vault.  Pass *None* to skip indexing.
    dump_dir:
        Override the default local-brain-dump directory.  Falls back to the
        ``LOCAL_BRAIN_DUMP_DIR`` environment variable and finally to
        ``/Local_Brain_Dump``.

    Returns
    -------
    dict[str, str | None]
        Mapping of filename → file content (``None`` when the file is not
        found or cannot be read).
    """
    base = pathlib.Path(
        dump_dir
        or os.environ.get("LOCAL_BRAIN_DUMP_DIR", _DEFAULT_LOCAL_BRAIN_DUMP)
    )
    results: dict[str, str | None] = {}

    for filename in _DRIVE_MAP_FILES:
        target = base / filename
        if not target.exists():
            logger.warning("LocalBridge: drive map not found — %s", target)
            results[filename] = None
            continue
        try:
            content = target.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            logger.warning("LocalBridge: could not read %s — %s", target, exc)
            results[filename] = None
            continue

        results[filename] = content
        logger.info("LocalBridge: ingested drive map '%s' (%d chars).", filename, len(content))

        if brain_collection is not None:
            try:
                from brain.indexer import index_text  # local import to avoid circular dep
                index_text(
                    brain_collection,
                    content,
                    source=f"local_brain_dump::{filename}",
                    extra_metadata={"file_type": "drive_map", "local_bridge": "true"},
                )
            except Exception as exc:  # pragma: no cover
                logger.error("LocalBridge: failed to index %s into brain vault: %s", filename, exc)

    return results
