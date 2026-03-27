"""
Industry 03 — The Resonance Engine (Culture & Narrative Control)
================================================================
Focus: Media Coding, 111Hz Frequency, The Meaning Ledger, Intent Manifestation.

This script automates the compilation and broadcast of sovereign cultural
assets.  It synchronises two primary Citadel districts:

* **D09 — Media Coding** : raw creative inputs (lyrics, stems, DJ sets,
  frequency-tuning tracks).
* **D04 — The Librarian** : the permanent archive (rendered audio-visual
  output, the Meaning Ledger).

Operational model
-----------------
1. **Scan** ``D09/Compiled_Outputs/`` for new or unarchived assets.
2. **Classify** each asset by its frequency signature (111 Hz, 369 Hz, etc.)
   and content type (audio, visual, text).
3. **Archive** qualified assets to ``D04`` with a standardised metadata
   record appended to ``D04/meaning_ledger.log``.
4. **Broadcast** a summary manifest so downstream Swarm nodes can pull the
   latest cultural payload.

Purpose
-------
The Resonance Engine counteracts psychological "Data-Bleed" from the
administrative fiction by continuously saturating the Sovereign Architect's
local environment with high-frequency, self-generated truth and artistic
intent — 111 Hz and 369 Hz tuning anchors are the primary counterweights.

Usage::

    python3 scripts/industry_03_resonance.py --initiate-broadcast
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import pathlib
import shutil
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

CITADEL_ROOT: pathlib.Path = pathlib.Path(
    os.environ.get("CITADEL_ARK_ROOT", str(pathlib.Path.home() / "CITADEL_ARK"))
)

D04_PATH: pathlib.Path = CITADEL_ROOT / "D04"
D09_PATH: pathlib.Path = CITADEL_ROOT / "D09"

COMPILED_OUTPUTS_DIR: pathlib.Path = D09_PATH / "Compiled_Outputs"
ARCHIVE_DIR: pathlib.Path = D04_PATH / "Archive"
MEANING_LEDGER: pathlib.Path = D04_PATH / "meaning_ledger.log"
BROADCAST_MANIFEST: pathlib.Path = D09_PATH / "broadcast_manifest.json"

#: Frequency tuning anchors in Hz and their associated content tags.
FREQUENCY_ANCHORS: dict[float, list[str]] = {
    111.0: ["healing", "clarity", "111Hz", "sovereign_tone"],
    369.0: ["creation", "manifestation", "369Hz", "freq_signature"],
    432.0: ["nature", "harmony", "432Hz"],
    528.0: ["repair", "love", "528Hz"],
    852.0: ["intuition", "awakening", "852Hz"],
    909.0: ["kinetic_anchor", "techno_pulse", "completion_loop", "hard_reset", "909Hz", "swing"],
}

#: Supported audio/visual/text extensions and their content types.
ASSET_EXTENSIONS: dict[str, str] = {
    ".mp3": "audio",
    ".wav": "audio",
    ".flac": "audio",
    ".ogg": "audio",
    ".aac": "audio",
    ".mp4": "visual",
    ".mov": "visual",
    ".mkv": "visual",
    ".png": "visual",
    ".jpg": "visual",
    ".jpeg": "visual",
    ".gif": "visual",
    ".txt": "text",
    ".md": "text",
    ".pdf": "text",
    ".lrc": "text",  # lyrics
}


# ---------------------------------------------------------------------------
# Asset classification
# ---------------------------------------------------------------------------


def _detect_frequency(name: str) -> float | None:
    """
    Detect the dominant frequency anchor from a filename.

    Checks the filename (case-insensitively) for numeric patterns that
    match known :data:`FREQUENCY_ANCHORS` (e.g. "111", "111hz", "111Hz").
    Returns the matching frequency in Hz, or *None* if no anchor is found.
    """
    lower = name.lower()
    for freq in FREQUENCY_ANCHORS:
        tag = str(int(freq))
        if tag + "hz" in lower or tag + "_hz" in lower or f"_{tag}" in lower or f"-{tag}" in lower:
            return freq
    return None


def classify_asset(path: pathlib.Path) -> dict[str, Any]:
    """
    Classify a single asset file by content type and frequency anchor.

    Parameters
    ----------
    path:
        Path to the asset file.

    Returns
    -------
    dict
        Metadata record with keys ``name``, ``content_type``, ``frequency_hz``,
        ``tags``, ``size_bytes``, and ``sha256``.
    """
    suffix = path.suffix.lower()
    content_type = ASSET_EXTENSIONS.get(suffix, "unknown")
    frequency_hz = _detect_frequency(path.name)
    tags: list[str] = []
    if frequency_hz is not None:
        tags = list(FREQUENCY_ANCHORS.get(frequency_hz, []))

    size_bytes = path.stat().st_size if path.exists() else 0

    # Compute SHA-256 for integrity verification (chunked for large files)
    sha = hashlib.sha256()
    try:
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(65536), b""):
                sha.update(chunk)
        digest = sha.hexdigest()
    except OSError:
        digest = "UNREADABLE"

    return {
        "name": path.name,
        "relative_path": str(path),
        "content_type": content_type,
        "frequency_hz": frequency_hz,
        "tags": tags,
        "size_bytes": size_bytes,
        "sha256": digest,
    }


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def scan_compiled_outputs(output_dir: pathlib.Path) -> list[dict[str, Any]]:
    """
    Recursively scan *output_dir* for cultural assets.

    Returns a list of classification dicts (one per discovered file).
    Unknown extensions are included with ``content_type="unknown"`` so
    nothing is silently dropped.
    """
    if not output_dir.exists():
        logger.info("Compiled outputs directory not found — creating: %s", output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return []

    assets: list[dict[str, Any]] = []
    for item in sorted(output_dir.rglob("*")):
        if item.is_file():
            assets.append(classify_asset(item))

    logger.info("Scan complete — %d asset(s) found in %s", len(assets), output_dir)
    return assets


# ---------------------------------------------------------------------------
# Archiver
# ---------------------------------------------------------------------------


def _append_ledger(ledger_path: pathlib.Path, record: str) -> None:
    """Append *record* to *ledger_path*, creating the file if needed."""
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    with ledger_path.open("a", encoding="utf-8") as fh:
        fh.write(record + "\n")


def archive_assets(
    assets: list[dict[str, Any]],
    archive_dir: pathlib.Path,
    ledger_path: pathlib.Path,
) -> list[dict[str, Any]]:
    """
    Copy each asset in *assets* to *archive_dir*, organised by content type,
    and append a Meaning Ledger entry for each archived file.

    Returns the list of successfully archived asset records (with an added
    ``archived_path`` key).
    """
    archived: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc).isoformat()

    for asset in assets:
        src = pathlib.Path(asset["relative_path"])
        if not src.exists():
            logger.warning("Asset not found — skipping: %s", src)
            continue

        # Organise into sub-directories by content type
        dest_dir = archive_dir / asset["content_type"]
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / src.name

        # Avoid overwriting if the SHA-256 already matches
        if dest.exists():
            existing_sha = hashlib.sha256(dest.read_bytes()).hexdigest()
            if existing_sha == asset["sha256"]:
                logger.debug("Already archived (unchanged): %s", dest)
                asset["archived_path"] = str(dest)
                asset["archive_status"] = "ALREADY_CURRENT"
                archived.append(asset)
                continue

        shutil.copy2(src, dest)
        asset["archived_path"] = str(dest)
        asset["archive_status"] = "ARCHIVED"
        asset["archived_at"] = now

        ledger_record = (
            f"[{now}] CULTURAL_LOOM_ACTIVE | "
            f"asset={src.name} | "
            f"content_type={asset['content_type']} | "
            f"frequency_hz={asset['frequency_hz']} | "
            f"sha256={asset['sha256'][:16]}... | "
            f"dest={dest}"
        )
        _append_ledger(ledger_path, ledger_record)
        logger.info("Archived: %s → %s", src.name, dest)
        archived.append(asset)

    return archived


# ---------------------------------------------------------------------------
# Broadcast
# ---------------------------------------------------------------------------


def build_broadcast_manifest(
    archived: list[dict[str, Any]],
    manifest_path: pathlib.Path,
) -> dict[str, Any]:
    """
    Compile a broadcast manifest from the list of *archived* assets and
    write it to *manifest_path*.

    Returns the manifest dict.
    """
    now = datetime.now(timezone.utc).isoformat()

    # Group by frequency anchor for easy downstream filtering
    by_frequency: dict[str, list[str]] = {}
    for asset in archived:
        freq_key = f"{asset['frequency_hz']}Hz" if asset.get("frequency_hz") else "UNTAGGED"
        by_frequency.setdefault(freq_key, []).append(asset["name"])

    manifest: dict[str, Any] = {
        "freq_signature": FREQ_SIGNATURE,
        "broadcast_timestamp": now,
        "total_assets": len(archived),
        "by_frequency": by_frequency,
        "by_content_type": {
            ct: [a["name"] for a in archived if a.get("content_type") == ct]
            for ct in {a.get("content_type") for a in archived}
        },
        "broadcast_status": "CULTURAL_LOOM_ACTIVE",
    }

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    logger.info("Broadcast manifest written → %s", manifest_path)
    return manifest


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def initiate_broadcast(
    output_dir: pathlib.Path = COMPILED_OUTPUTS_DIR,
    archive_dir: pathlib.Path = ARCHIVE_DIR,
    ledger_path: pathlib.Path = MEANING_LEDGER,
    manifest_path: pathlib.Path = BROADCAST_MANIFEST,
) -> dict[str, Any]:
    """
    Execute the full Resonance Engine broadcast sequence.

    Steps
    -----
    1. Scan ``D09/Compiled_Outputs/`` for cultural assets.
    2. Classify each asset by content type and frequency anchor.
    3. Archive qualified assets to ``D04/Archive/``.
    4. Append Meaning Ledger entries for each new archive event.
    5. Write a broadcast manifest to ``D09/broadcast_manifest.json``.

    Returns the broadcast manifest dict.
    """
    logger.info("Resonance Engine — initiating cultural asset broadcast …")

    assets = scan_compiled_outputs(output_dir)
    archived = archive_assets(assets, archive_dir, ledger_path)
    manifest = build_broadcast_manifest(archived, manifest_path)

    logger.info(
        "Resonance Engine broadcast complete — %d asset(s) archived | CULTURAL_LOOM_ACTIVE",
        len(archived),
    )
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Industry 03 — The Resonance Engine: cultural asset compilation & broadcast.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--initiate-broadcast",
        action="store_true",
        help="Scan D09, archive to D04, and emit a broadcast manifest.",
    )
    parser.add_argument(
        "--output-dir",
        type=pathlib.Path,
        default=COMPILED_OUTPUTS_DIR,
        help="D09 Compiled_Outputs directory to scan.",
    )
    parser.add_argument(
        "--archive-dir",
        type=pathlib.Path,
        default=ARCHIVE_DIR,
        help="D04 Archive directory to write to.",
    )
    parser.add_argument(
        "--ledger",
        type=pathlib.Path,
        default=MEANING_LEDGER,
        help="D04 Meaning Ledger log file path.",
    )
    parser.add_argument(
        "--manifest",
        type=pathlib.Path,
        default=BROADCAST_MANIFEST,
        help="D09 broadcast manifest JSON path.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and classify assets but do not archive or write any files.",
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

    if not args.initiate_broadcast:
        parser.print_help()
        return 0

    if args.dry_run:
        assets = scan_compiled_outputs(args.output_dir)
        print(json.dumps({"dry_run": True, "assets_found": len(assets), "assets": assets}, indent=2))
        return 0

    manifest = initiate_broadcast(
        output_dir=args.output_dir,
        archive_dir=args.archive_dir,
        ledger_path=args.ledger,
        manifest_path=args.manifest,
    )
    print(manifest["broadcast_status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
