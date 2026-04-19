"""
local_vacuum_worker.py — Background shard-and-index worker for data/.

Scans the repository's ``data/`` directory, organises every file into
named content shards based on file type and source prefix, and writes a
``data/vacuum_manifest.json`` that the Librarian can use to track what has
been ingested and what is new.

Run modes
---------
* **Standalone CLI**::

      python local_vacuum_worker.py
      python local_vacuum_worker.py --data-dir /custom/path --dry-run

* **Imported utility** (called from scripts or tests)::

      from local_vacuum_worker import run_vacuum, VacuumManifest

Shard layout
------------
Each file is assigned to exactly one shard based on path prefix rules
defined in ``SHARD_RULES``.  The manifest records per-shard stats and a
flat ``files`` list so downstream consumers can request only the shards
they need.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("local_vacuum_worker")

REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = REPO_ROOT / "data"
MANIFEST_PATH = DEFAULT_DATA_DIR / "vacuum_manifest.json"

# ---------------------------------------------------------------------------
# Shard classification rules
# (first matching prefix wins; "default" catches everything else)
# ---------------------------------------------------------------------------

SHARD_RULES: List[tuple[str, str]] = [
    # Device node intel
    ("master_harvest", "shard_master_harvest"),
    ("personal_archive", "shard_personal_archive"),
    ("rag_brains", "shard_rag_brains"),
    ("rag_sync", "shard_rag_sync"),
    ("vector_store", "shard_vector_store"),
    # Personas / characters
    ("personas", "shard_personas"),
    # Discoveries / solutions
    ("discoveries", "shard_discoveries"),
    ("solutions", "shard_solutions"),
    # Worker / constellation state
    ("worker_constellation", "shard_workers"),
    ("workers", "shard_workers"),
    # Financial / trading data
    ("trading_strategies", "shard_trading"),
    ("crypto_tokens", "shard_trading"),
    ("iso20022", "shard_trading"),
    # Models / datasets
    ("models", "shard_models"),
    ("datasets", "shard_datasets"),
    # Security and audits
    ("security", "shard_security"),
    ("audits", "shard_audits"),
    # Research / intelligence
    ("research_runs", "shard_research"),
    ("spiritual_intelligence", "shard_research"),
    ("spiritual_discovery", "shard_research"),
    # Agent / mesh configs
    ("agent_legion", "shard_agents"),
    ("citadel_mesh", "shard_agents"),
    # Spoke and sync artefacts
    ("spoke_artifacts", "shard_spokes"),
    ("spoke_sync_registry", "shard_spokes"),
    ("sync_reports", "shard_spokes"),
    # Manifests / indexes (catch-all for top-level JSON)
    ("Mapping-and-Inventory-storage", "shard_storage"),
]

_DEFAULT_SHARD = "shard_misc"

# File extensions that are worth indexing for RAG.
_TEXT_EXTENSIONS = {".md", ".txt", ".json", ".csv", ".yaml", ".yml", ".py", ".sh"}
# Extensions that are binary / large — record them in the manifest but skip content hash.
_BINARY_EXTENSIONS = {".index", ".bin", ".pkl", ".db", ".sqlite", ".zip", ".tar", ".gz"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class FileEntry:
    path: str          # relative to data_dir
    shard: str
    size_bytes: int
    extension: str
    sha256: Optional[str]  # None for binary / skipped files
    mtime_iso: str


@dataclass
class ShardStats:
    shard: str
    file_count: int
    total_bytes: int
    text_files: int
    binary_files: int


@dataclass
class VacuumManifest:
    generated_at: str
    data_dir: str
    total_files: int
    total_bytes: int
    shards: Dict[str, ShardStats] = field(default_factory=dict)
    files: List[FileEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["shards"] = {k: asdict(v) for k, v in self.shards.items()}
        return d


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def _classify_shard(rel_path: str) -> str:
    """Return the shard name for a path relative to data_dir."""
    for prefix, shard in SHARD_RULES:
        if rel_path.startswith(prefix):
            return shard
    return _DEFAULT_SHARD


def _sha256_file(path: Path, max_bytes: int = 10 * 1024 * 1024) -> Optional[str]:
    """Compute SHA-256 of file contents, capped at ``max_bytes`` for large files."""
    try:
        h = hashlib.sha256()
        with path.open("rb") as fh:
            remaining = max_bytes
            while remaining > 0:
                chunk = fh.read(min(65536, remaining))
                if not chunk:
                    break
                h.update(chunk)
                remaining -= len(chunk)
        return h.hexdigest()
    except OSError as exc:
        logger.warning("Could not hash %s: %s", path, exc)
        return None


def scan_directory(data_dir: Path) -> List[FileEntry]:
    """Walk data_dir and return a FileEntry for every file found."""
    entries: List[FileEntry] = []
    for path in sorted(data_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in (".gitkeep",) or path.name.startswith("."):
            continue
        try:
            stat = path.stat()
        except OSError:
            continue
        rel = path.relative_to(data_dir).as_posix()
        ext = path.suffix.lower()
        is_binary = ext in _BINARY_EXTENSIONS
        sha = None if is_binary else _sha256_file(path)
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        entries.append(
            FileEntry(
                path=rel,
                shard=_classify_shard(rel),
                size_bytes=stat.st_size,
                extension=ext,
                sha256=sha,
                mtime_iso=mtime,
            )
        )
    return entries


def build_manifest(entries: List[FileEntry], data_dir: Path) -> VacuumManifest:
    """Aggregate FileEntry list into a VacuumManifest with per-shard stats."""
    shards: Dict[str, ShardStats] = {}
    total_bytes = 0

    for entry in entries:
        total_bytes += entry.size_bytes
        s = shards.setdefault(
            entry.shard,
            ShardStats(
                shard=entry.shard,
                file_count=0,
                total_bytes=0,
                text_files=0,
                binary_files=0,
            ),
        )
        s.file_count += 1
        s.total_bytes += entry.size_bytes
        if entry.extension in _BINARY_EXTENSIONS:
            s.binary_files += 1
        else:
            s.text_files += 1

    return VacuumManifest(
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        data_dir=str(data_dir),
        total_files=len(entries),
        total_bytes=total_bytes,
        shards=shards,
        files=entries,
    )


def run_vacuum(
    data_dir: Path = DEFAULT_DATA_DIR,
    manifest_path: Optional[Path] = None,
    dry_run: bool = False,
) -> VacuumManifest:
    """Scan data_dir, build the manifest, and write it to disk.

    Args:
        data_dir:      Root directory to scan (default: ``data/``).
        manifest_path: Where to write the JSON manifest.
                       Defaults to ``data/vacuum_manifest.json``.
        dry_run:       If True, scan and build but do not write to disk.

    Returns:
        The completed :class:`VacuumManifest`.
    """
    if manifest_path is None:
        manifest_path = data_dir / "vacuum_manifest.json"

    logger.info("Scanning %s ...", data_dir)
    entries = scan_directory(data_dir)
    manifest = build_manifest(entries, data_dir)

    shard_summary = ", ".join(
        f"{s.shard}={s.file_count}" for s in sorted(manifest.shards.values(), key=lambda x: -x.file_count)
    )
    logger.info(
        "Vacuum complete: %d files / %d bytes across %d shards [%s]",
        manifest.total_files,
        manifest.total_bytes,
        len(manifest.shards),
        shard_summary,
    )

    if not dry_run:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("Manifest written to %s", manifest_path)

    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _main(argv=None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = argparse.ArgumentParser(
        description="Shard-and-index worker: scan data/ and emit vacuum_manifest.json"
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=DEFAULT_DATA_DIR,
        help="Root directory to scan (default: data/)",
    )
    parser.add_argument(
        "--manifest-out",
        type=Path,
        default=None,
        help="Output path for the manifest JSON (default: <data-dir>/vacuum_manifest.json)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Scan and print stats without writing to disk",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print a human-readable shard summary after scanning",
    )
    args = parser.parse_args(argv)

    manifest = run_vacuum(
        data_dir=args.data_dir,
        manifest_path=args.manifest_out,
        dry_run=args.dry_run,
    )

    if args.summary or args.dry_run:
        print(f"\n{'='*60}")
        print(f"VACUUM SUMMARY — {manifest.generated_at}")
        print(f"{'='*60}")
        print(f"  Total files : {manifest.total_files}")
        print(f"  Total bytes : {manifest.total_bytes:,}")
        print(f"  Shards      : {len(manifest.shards)}")
        print()
        for shard in sorted(manifest.shards.values(), key=lambda s: -s.file_count):
            print(
                f"  {shard.shard:<30}  {shard.file_count:>5} files  "
                f"{shard.total_bytes:>12,} bytes"
            )
        print(f"{'='*60}\n")

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
