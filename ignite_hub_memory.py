#!/usr/bin/env python3
"""Hub Ignition Script — triggers the central RAG ingestion for the hub.

This standalone script points the central ingestion process at
``data/master_harvest/`` so the Mapping-and-Inventory knowledge base is
absorbed automatically.

Two modes are supported:

1. **Local call** (default): imports ``scripts/rag_ingest.py`` and runs
   ``run_ingest`` in-process. Works in any environment that has the repo
   checked out.
2. **Remote HTTP POST**: when ``--remote`` or ``HUB_API_URL`` is supplied,
   posts to a local FastAPI instance (``POST {url}/ingest``) so a long-lived
   service can handle the ingestion asynchronously.
3. **OMNI-RECEPTION ignition**: when ``--omni-reception`` is supplied, runs
   :class:`src.orchestration.omni_reception.OmniReceptionOrchestrator` to
   compose the five Librarian subsystems (Deep Crawl, Vault Union, GDrive
   Synapse, Real-Time Bridge, Query Interface) into a single in-process
   ignition.

Usage:

    # Local in-process ignition (default)
    python ignite_hub_memory.py

    # Point at a custom harvest directory
    python ignite_hub_memory.py --harvest-dir data/master_harvest

    # Trigger a running FastAPI hub
    python ignite_hub_memory.py --remote http://127.0.0.1:8000

    # Trigger the OMNI-RECEPTION master orchestrator
    python ignite_hub_memory.py --omni-reception
    python ignite_hub_memory.py --omni-reception --no-deep-crawl --no-bridge

Exit codes:
    0 = ingestion kicked off successfully
    1 = configuration error (missing deps / bad args)
    2 = ingestion pipeline returned an error
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
DEFAULT_HARVEST_DIR = REPO_ROOT / "data" / "master_harvest"
DEFAULT_RAG_STORE = REPO_ROOT / "rag_store"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("ignite_hub_memory")


def _ingest_locally(harvest_dir: Path, rag_store: Path) -> int:
    """Invoke scripts/rag_ingest.run_ingest in-process."""
    if str(SCRIPTS_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPTS_DIR))

    try:
        import rag_ingest  # type: ignore
    except Exception as exc:
        logger.error("❌ Could not import scripts/rag_ingest.py: %s", exc)
        return 1

    logger.info("🔥 Igniting local ingestion against %s", harvest_dir)
    try:
        summary = rag_ingest.run_ingest(
            harvest_dir=harvest_dir,
            rag_store=rag_store,
        )
    except Exception as exc:
        logger.exception("💥 Local ingestion failed: %s", exc)
        return 2

    logger.info("📊 Ingestion summary: %s", json.dumps(summary, indent=2))
    status = summary.get("status")
    if status not in {"ok", "no_data", "deps_missing"}:
        return 2
    return 0


def _ingest_remote(api_url: str, harvest_dir: Path) -> int:
    """POST to a running FastAPI hub to trigger ingestion."""
    try:
        import requests  # type: ignore
    except Exception as exc:
        logger.error("❌ `requests` not installed: %s", exc)
        return 1

    endpoint = api_url.rstrip("/") + "/ingest"
    payload = {
        "harvest_dir": str(harvest_dir),
        "source": "ignite_hub_memory",
    }
    logger.info("🛰️  POST %s payload=%s", endpoint, payload)

    try:
        resp = requests.post(endpoint, json=payload, timeout=60)
    except Exception as exc:
        logger.error("❌ HTTP request failed: %s", exc)
        return 2

    if resp.status_code >= 400:
        logger.error(
            "❌ Hub returned %s: %s", resp.status_code, resp.text[:500]
        )
        return 2

    logger.info("✅ Hub accepted ignition: %s", resp.text[:500])
    return 0


def _ingest_omni_reception(harvest_dir: Path, args) -> int:
    """Trigger the OMNI-RECEPTION master orchestrator in-process."""
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    try:
        from src.orchestration.omni_reception import OmniReceptionOrchestrator
    except Exception as exc:
        logger.error("❌ Could not import OmniReceptionOrchestrator: %s", exc)
        return 1

    logger.info("🛰️  Igniting OMNI-RECEPTION orchestrator (vault_root=%s)", harvest_dir)
    try:
        orch = OmniReceptionOrchestrator(vault_root=harvest_dir)
        report = orch.ignite(
            deep_crawl=not args.no_deep_crawl,
            vault_union=not args.no_vault_union,
            gdrive_synapse=not args.no_gdrive_synapse,
            start_bridge=not args.no_bridge,
        )
    except Exception as exc:
        logger.exception("💥 OMNI-RECEPTION ignition failed: %s", exc)
        return 2
    finally:
        try:
            orch.stop_real_time_bridge()  # type: ignore[name-defined]
        except Exception:  # pragma: no cover - defensive
            pass

    logger.info(
        "📊 OMNI-RECEPTION report: %s",
        json.dumps(report.as_dict(), indent=2, default=str),
    )
    return 2 if report.errors else 0


def _parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--harvest-dir",
        default=str(DEFAULT_HARVEST_DIR),
        help="Directory to ingest. Defaults to data/master_harvest/.",
    )
    parser.add_argument(
        "--rag-store",
        default=str(DEFAULT_RAG_STORE),
        help="Output RAG store directory (local mode only).",
    )
    parser.add_argument(
        "--remote",
        default=os.environ.get("HUB_API_URL"),
        help="Base URL of a running FastAPI hub (e.g. http://127.0.0.1:8000). "
             "If omitted, ingestion runs in-process.",
    )
    parser.add_argument(
        "--omni-reception",
        action="store_true",
        help="Trigger the OMNI-RECEPTION master orchestrator instead of "
             "the legacy harvest-dir ingestion path.",
    )
    parser.add_argument("--no-deep-crawl", action="store_true",
                        help="OMNI-RECEPTION: skip the GitHub Deep Crawl.")
    parser.add_argument("--no-vault-union", action="store_true",
                        help="OMNI-RECEPTION: skip the Partition_xx Vault Union.")
    parser.add_argument("--no-gdrive-synapse", action="store_true",
                        help="OMNI-RECEPTION: skip the GDrive External Synapse.")
    parser.add_argument("--no-bridge", action="store_true",
                        help="OMNI-RECEPTION: skip starting the /v1/ingest bridge.")
    return parser.parse_args(argv)


def main(argv: Optional[list] = None) -> int:
    args = _parse_args(argv)
    # When the OMNI-RECEPTION orchestrator is requested and the user
    # didn't override --harvest-dir, default the vault root to the repo
    # root so Partition_01..46 are discoverable.
    if args.omni_reception and args.harvest_dir == str(DEFAULT_HARVEST_DIR):
        harvest_dir = REPO_ROOT
    else:
        harvest_dir = Path(args.harvest_dir).resolve()
    rag_store = Path(args.rag_store).resolve()

    if not harvest_dir.exists():
        logger.warning(
            "⚠️  Harvest directory %s does not exist; creating it.", harvest_dir
        )
        harvest_dir.mkdir(parents=True, exist_ok=True)

    logger.info("🏰 Hub Ignition — harvest_dir=%s", harvest_dir)

    if args.omni_reception:
        return _ingest_omni_reception(harvest_dir, args)
    if args.remote:
        return _ingest_remote(args.remote, harvest_dir)
    return _ingest_locally(harvest_dir, rag_store)


if __name__ == "__main__":
    sys.exit(main())
