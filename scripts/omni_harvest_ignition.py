#!/usr/bin/env python3
"""
🔥 OMNI-HARVEST IGNITION CLI.

Runs the Forever-Learning continuous loop that ties together the four
directive subsystems — GitHub Great Crawl, Physical Harvest (WebSocket
telemetry), GDrive Bridge, and the T.I.A. Synapse query engine.

Usage::

    python scripts/omni_harvest_ignition.py --iterations 1
    python scripts/omni_harvest_ignition.py --interval 300   # continuous
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Make the repo root importable when invoked directly.
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ingestion.omni_harvest import OmniHarvestIgnition, STABILITY_TARGET  # noqa: E402
from src.storage import VectorStore  # noqa: E402


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OMNI-HARVEST IGNITION Forever-Learning loop")
    parser.add_argument(
        "--iterations",
        type=int,
        default=None,
        help="Number of ticks to run (default: continuous).",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=300.0,
        help="Seconds to sleep between ticks (default: 300).",
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="Print subsystem status and exit without running a tick.",
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as a 24/7 background cycle (continuous loop, no iteration limit).",
    )
    parser.add_argument(
        "--vector-store-dir",
        type=str,
        default=None,
        help="Directory for persistent vector store (default: data/vector_store).",
    )
    parser.add_argument(
        "--ingest-port",
        type=int,
        default=None,
        help="When set, starts the /v1/ingest HTTP server on this port.",
    )
    parser.add_argument(
        "--ingest-host",
        type=str,
        default="127.0.0.1",
        help=(
            "Host interface for /v1/ingest (default: 127.0.0.1 / loopback only). "
            "Use 0.0.0.0 to accept telemetry from S10/Oppo-Node over the network — "
            "only do this behind a trusted boundary / reverse proxy with authentication."
        ),
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose logging.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    ignition = OmniHarvestIgnition(
        vector_store=VectorStore(
            data_dir=Path(args.vector_store_dir) if args.vector_store_dir else None
        ),
    )

    ingest_server = None
    if args.ingest_port is not None:
        from src.api import IngestServer  # local import: optional

        ingest_server = IngestServer(
            host=args.ingest_host,
            port=args.ingest_port,
            harvester=ignition.physical_harvest,
        )
        ingest_server.start()
        logging.info(
            "🛰️ /v1/ingest listening on %s%s",
            ingest_server.url,
            " (PUBLIC BIND — ensure the endpoint is protected)"
            if args.ingest_host not in ("127.0.0.1", "localhost", "::1")
            else "",
        )

    if args.status_only:
        try:
            print(json.dumps(ignition.status(), indent=2, default=str))
        finally:
            if ingest_server is not None:
                ingest_server.stop()
        return 0

    iterations = None if args.daemon else args.iterations
    logging.info(
        "🔥 Ignition online — stability target = %d%s",
        STABILITY_TARGET,
        " (daemon mode)" if args.daemon else "",
    )
    try:
        results = ignition.run(
            iterations=iterations,
            interval_seconds=args.interval,
        )
    except KeyboardInterrupt:  # pragma: no cover - interactive path
        logging.info("Ignition interrupted by operator")
        results = ignition.history()
    finally:
        if ingest_server is not None:
            ingest_server.stop()
    summary = {
        "stability_target": STABILITY_TARGET,
        "ticks_executed": len(results),
        "status": ignition.status(),
    }
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
