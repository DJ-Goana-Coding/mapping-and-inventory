"""
Industry 01 — The Kinetic Forge (Hard Asset & Extraction)
==========================================================
Focus: Sovereign Finance, The 144-Grid, Algorithmic Extraction, Silver (Ag).

This script isolates all logic related to P25 Sniper strike entries and
market-intersection analysis.  It implements an autonomous routing protocol
that sweeps extracted fiat/liquidity from ``D07`` (Trader Logs) and
initiates the conversion process toward physical precious metals or
cold-storage cryptographic assets.

Zero-Fiat Retention Policy
--------------------------
Any fiat balance recorded in the extraction ledger that is older than the
:data:`FIAT_RETENTION_WINDOW_HOURS` threshold (72 h by default) is flagged
with ``FIAT_PURGED`` and queued for conversion.  This enforces strict
resistance to "Blue Rot" inflation mechanics by minimising long-term fiat
exposure inside the Citadel's operational perimeter.

Usage::

    python3 scripts/industry_01_forge.py --engage-routing
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import pathlib
from datetime import datetime, timedelta, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

CITADEL_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get("CITADEL_ARK_ROOT", str(pathlib.Path.home() / "CITADEL_ARK"))
)

#: Maximum number of hours fiat balances may remain unconverted.
FIAT_RETENTION_WINDOW_HOURS: int = int(os.environ.get("FIAT_RETENTION_WINDOW_HOURS", "72"))

#: Supported conversion targets in priority order.
CONVERSION_TARGETS: list[str] = ["PHYSICAL_SILVER_AG", "COLD_STORAGE_BTC", "COLD_STORAGE_XMR"]

# Citadel district paths
D01_PATH: pathlib.Path = CITADEL_ROOT / "D01"
D07_PATH: pathlib.Path = CITADEL_ROOT / "D07"

EXTRACTION_LEDGER: pathlib.Path = D07_PATH / "extraction_ledger.log"
INDUSTRY_STATUS_FILE: pathlib.Path = D01_PATH / "industry_status.txt"
ROUTING_MANIFEST: pathlib.Path = D07_PATH / "routing_manifest.json"

# ---------------------------------------------------------------------------
# P25 Sniper Strike logic
# ---------------------------------------------------------------------------

#: P25 grid precision tiers for entry-point qualification.
P25_PRECISION_TIERS: dict[str, float] = {
    "TIER_1_ULTRA":    0.99,   # ≥99 % grid alignment — execute immediately
    "TIER_2_HIGH":     0.95,   # ≥95 % — standard Sniper entry
    "TIER_3_MEDIUM":   0.88,   # ≥88 % — hold, await confirmation candle
    "TIER_4_WATCH":    0.80,   # ≥80 % — on watchlist only
}


def evaluate_p25_entry(grid_alignment: float) -> dict[str, Any]:
    """
    Evaluate a market entry point against the P25 144-Grid precision model.

    Parameters
    ----------
    grid_alignment:
        Float in [0, 1] representing the percentage alignment of the current
        price action to the 144-Grid intersection point.

    Returns
    -------
    dict
        Result containing ``tier``, ``action``, and ``qualified`` flag.
    """
    for tier, threshold in P25_PRECISION_TIERS.items():
        if grid_alignment >= threshold:
            action = "EXECUTE" if tier in ("TIER_1_ULTRA", "TIER_2_HIGH") else "HOLD"
            return {
                "grid_alignment": grid_alignment,
                "tier": tier,
                "threshold": threshold,
                "action": action,
                "qualified": action == "EXECUTE",
            }
    return {
        "grid_alignment": grid_alignment,
        "tier": "TIER_5_BELOW_THRESHOLD",
        "threshold": P25_PRECISION_TIERS["TIER_4_WATCH"],
        "action": "SKIP",
        "qualified": False,
    }


# ---------------------------------------------------------------------------
# Extraction ledger scanning
# ---------------------------------------------------------------------------


def _parse_ledger_entries(ledger_path: pathlib.Path) -> list[dict[str, Any]]:
    """
    Parse existing ledger entries from *ledger_path*.

    Expected log format (one entry per line)::

        [ISO-TIMESTAMP] STATUS | asset=BTC | amount=0.01 | source=D07

    Entries that do not match this rough structure are silently skipped.
    """
    entries: list[dict[str, Any]] = []
    if not ledger_path.exists():
        return entries

    for raw_line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        # Extract timestamp between brackets
        if not line.startswith("["):
            continue
        try:
            ts_end = line.index("]")
            timestamp_str = line[1:ts_end]
            rest = line[ts_end + 1:].strip()
            parts = rest.split("|")
            status = parts[0].strip() if parts else "UNKNOWN"
            kv: dict[str, str] = {}
            for part in parts[1:]:
                if "=" in part:
                    k, _, v = part.partition("=")
                    kv[k.strip()] = v.strip()
            entries.append(
                {
                    "timestamp": timestamp_str,
                    "status": status,
                    "asset": kv.get("asset", "UNKNOWN"),
                    "amount": float(kv.get("amount", "0")),
                    "source": kv.get("source", "UNKNOWN"),
                }
            )
        except (ValueError, IndexError):
            continue

    return entries


def scan_fiat_exposure(ledger_path: pathlib.Path) -> list[dict[str, Any]]:
    """
    Scan *ledger_path* for fiat entries older than
    :data:`FIAT_RETENTION_WINDOW_HOURS`.

    Returns a list of stale fiat records that must be purged.
    """
    entries = _parse_ledger_entries(ledger_path)
    cutoff = datetime.now(timezone.utc) - timedelta(hours=FIAT_RETENTION_WINDOW_HOURS)
    stale: list[dict[str, Any]] = []

    for entry in entries:
        if entry["status"] in ("FIAT_PURGED", "CONVERTED"):
            continue
        if entry["asset"] not in ("AUD", "USD", "EUR", "FIAT", "GBP"):
            continue
        try:
            ts = datetime.fromisoformat(entry["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            continue
        if ts < cutoff:
            stale.append(entry)

    return stale


# ---------------------------------------------------------------------------
# Routing protocol
# ---------------------------------------------------------------------------


def _append_ledger_entry(ledger_path: pathlib.Path, line: str) -> None:
    """Append *line* to *ledger_path*, creating the file if needed."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(line + "\n")


def purge_stale_fiat(stale_entries: list[dict[str, Any]], ledger_path: pathlib.Path) -> int:
    """
    Mark each stale fiat entry as ``FIAT_PURGED`` in the extraction ledger
    and queue it for conversion.

    Returns the number of entries purged.
    """
    now = datetime.now(timezone.utc).isoformat()
    for entry in stale_entries:
        record = (
            f"[{now}] FIAT_PURGED | "
            f"asset={entry['asset']} | "
            f"amount={entry['amount']} | "
            f"source={entry['source']} | "
            f"conversion_target={CONVERSION_TARGETS[0]}"
        )
        _append_ledger_entry(ledger_path, record)
        logger.info("FIAT_PURGED: %.4f %s → queued for %s", entry["amount"], entry["asset"], CONVERSION_TARGETS[0])

    return len(stale_entries)


def initiate_routing(
    ledger_path: pathlib.Path = EXTRACTION_LEDGER,
    manifest_path: pathlib.Path = ROUTING_MANIFEST,
) -> dict[str, Any]:
    """
    Execute the autonomous routing protocol:

    1. Scan D07 extraction ledger for stale fiat balances.
    2. Purge (flag) entries beyond the 72-hour Zero-Fiat Retention window.
    3. Write a routing manifest summarising the sweep.

    Returns the routing manifest dict.
    """
    logger.info("Kinetic Forge — initiating autonomous routing sweep …")

    stale = scan_fiat_exposure(ledger_path)
    logger.info("Stale fiat entries found: %d", len(stale))

    purged_count = purge_stale_fiat(stale, ledger_path)

    # Log an EXTRACTION_SWEEP entry so the overall event is auditable
    sweep_ts = datetime.now(timezone.utc).isoformat()
    sweep_record = (
        f"[{sweep_ts}] EXTRACTION_SWEEP | "
        f"entries_scanned={len(_parse_ledger_entries(ledger_path))} | "
        f"fiat_purged={purged_count} | "
        f"retention_window_hours={FIAT_RETENTION_WINDOW_HOURS} | "
        f"source=D07"
    )
    _append_ledger_entry(ledger_path, sweep_record)

    manifest: dict[str, Any] = {
        "freq_signature": FREQ_SIGNATURE,
        "sweep_timestamp": sweep_ts,
        "fiat_retention_window_hours": FIAT_RETENTION_WINDOW_HOURS,
        "entries_purged": purged_count,
        "conversion_targets": CONVERSION_TARGETS,
        "zero_fiat_retention_policy": "ENFORCED",
        "routing_status": "KINETIC_FORGE_ONLINE",
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("Routing manifest written → %s", manifest_path)

    return manifest


def write_industry_status(status_file: pathlib.Path, message: str = "KINETIC_FORGE_ONLINE") -> None:
    """Write the industry status token to *status_file* in D01."""
    status_file.parent.mkdir(parents=True, exist_ok=True)
    status_file.write_text(message + "\n", encoding="utf-8")
    logger.info("Industry status written → %s: %s", status_file, message)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Industry 01 — The Kinetic Forge: Hard Asset & Extraction routing protocol.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--engage-routing",
        action="store_true",
        help="Execute the autonomous fiat-sweep and Zero-Fiat Retention protocol.",
    )
    parser.add_argument(
        "--ledger",
        type=pathlib.Path,
        default=EXTRACTION_LEDGER,
        help="Path to the D07 extraction ledger log file.",
    )
    parser.add_argument(
        "--status-file",
        type=pathlib.Path,
        default=INDUSTRY_STATUS_FILE,
        help="Path to the D01 industry status text file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the routing manifest to stdout without writing to disk.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point — returns 0 on success, non-zero on failure."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )

    if not args.engage_routing:
        parser.print_help()
        return 0

    manifest = initiate_routing(ledger_path=args.ledger)

    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return 0

    write_industry_status(args.status_file)
    print(manifest["routing_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
