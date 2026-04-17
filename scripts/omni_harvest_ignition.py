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

    ignition = OmniHarvestIgnition()

    if args.status_only:
        print(json.dumps(ignition.status(), indent=2, default=str))
        return 0

    logging.info(
        "🔥 Ignition online — stability target = %d", STABILITY_TARGET
    )
    results = ignition.run(
        iterations=args.iterations,
        interval_seconds=args.interval,
    )
    summary = {
        "stability_target": STABILITY_TARGET,
        "ticks_executed": len(results),
        "status": ignition.status(),
    }
    print(json.dumps(summary, indent=2, default=str))
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
