"""
workers/vacuum_shard_worker.py — Domain sharding worker for GDrive/data content.

Scans the local ``data/`` tree and any configured GDrive mount points, then
classifies every file into one of four Specialist Domains:

  TECH    — code, scripts, models, datasets, configs
  BIO     — health, genetics, spiritual, frequency, personal
  LEGAL   — legal documents, compliance, PvC ledgers, contracts
  TRADE   — trading strategies, crypto, financial, market data

Files are hard-linked (or copied when cross-device) into
``data/shards/<DOMAIN>/``.  A ``data/shards/shard_manifest.json`` is written
on every run so the Librarian knows which shard holds each document and can
route queries to the correct domain index.

Run modes
---------
* **CLI**::

      python workers/vacuum_shard_worker.py
      python workers/vacuum_shard_worker.py --source-dir /mnt/gdrive --dry-run
      python workers/vacuum_shard_worker.py --domains TECH TRADE

* **Imported**::

      from workers.vacuum_shard_worker import run_vacuum_sharding, DOMAINS

"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import os
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

logger = logging.getLogger("vacuum_shard_worker")

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SOURCE_DIR = REPO_ROOT / "data"
SHARDS_DIR = REPO_ROOT / "data" / "shards"
MANIFEST_PATH = SHARDS_DIR / "shard_manifest.json"


# ---------------------------------------------------------------------------
# Domain definitions
# ---------------------------------------------------------------------------


class Domain(str, Enum):
    TECH = "TECH"
    BIO = "BIO"
    LEGAL = "LEGAL"
    TRADE = "TRADE"
    MISC = "MISC"  # catch-all


DOMAINS = list(Domain)

# Each domain has a set of path-prefix keywords and file-name keywords.
# Path segments are checked case-insensitively.
_DOMAIN_PATH_RULES: List[Tuple[Domain, Sequence[str]]] = [
    (Domain.TRADE, [
        "trading", "trade", "crypto", "token", "market", "mexc", "pioneer_trader",
        "financial", "iso20022", "blockchain", "profit", "forex", "broker",
        "mexc_balance", "mexc_fleet", "precious_metal",
    ]),
    (Domain.LEGAL, [
        "legal", "compliance", "contract", "pvc", "ledger", "abn", "licence",
        "gdpr", "terms", "policy", "security",
    ]),
    (Domain.BIO, [
        "spiritual", "bio", "genetics", "health", "frequency", "chakra",
        "healing", "soul", "aether", "personal_archive", "persona",
        "transmission", "lore", "vibration", "tarot", "zodiac", "ancestor",
        "dna", "genesis_alignment", "substrate",
    ]),
    (Domain.TECH, [
        "model", "dataset", "code", "script", "worker", "vector_store",
        "rag", "repo", "config", "manifest", "agent", "pipeline", "deploy",
        "api", "webhook", "citadel_mesh", "spoke", "worker_constellation",
        "tools", "libraries", "discovery", "research_run",
    ]),
]

_TEXT_EXTENSIONS = {
    ".md", ".txt", ".json", ".csv", ".yaml", ".yml",
    ".py", ".sh", ".js", ".ts", ".html", ".xml", ".toml",
}
_SKIP_DIRS = {
    "__pycache__", ".git", "node_modules", "shards",
    "vector_store",  # FAISS index — binary, skip
}
_SKIP_FILES = {".gitkeep", ".DS_Store"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ShardEntry:
    source_path: str
    shard_path: str
    domain: str
    size_bytes: int
    sha256_prefix: str  # first 16 hex chars — enough for dedup checks
    mtime_iso: str


@dataclass
class DomainStats:
    domain: str
    file_count: int = 0
    total_bytes: int = 0


@dataclass
class ShardManifest:
    generated_at: str
    source_dir: str
    shards_dir: str
    total_files: int
    total_bytes: int
    domains: Dict[str, DomainStats] = field(default_factory=dict)
    entries: List[ShardEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["domains"] = {k: asdict(v) for k, v in self.domains.items()}
        return d


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def classify(path: Path) -> Domain:
    """Classify a file into a domain based on its path segments."""
    parts_lower = [p.lower() for p in path.parts]
    stem_lower = path.stem.lower()

    for domain, keywords in _DOMAIN_PATH_RULES:
        for kw in keywords:
            if any(kw in part for part in parts_lower) or kw in stem_lower:
                return domain

    return Domain.MISC


# ---------------------------------------------------------------------------
# Core scan + shard logic
# ---------------------------------------------------------------------------


def _sha256_prefix(path: Path, n_bytes: int = 8192) -> str:
    h = hashlib.sha256()
    try:
        with path.open("rb") as f:
            h.update(f.read(n_bytes))
    except OSError:
        return "unreadable"
    return h.hexdigest()[:16]


def scan_and_shard(
    source_dir: Path,
    shards_dir: Path,
    target_domains: Optional[Sequence[Domain]] = None,
    dry_run: bool = False,
) -> ShardManifest:
    """Walk *source_dir*, classify each file, and copy it into *shards_dir/<DOMAIN>/*.

    Parameters
    ----------
    source_dir:     Root directory to scan (default: ``data/``).
    shards_dir:     Where shard subdirs are written (default: ``data/shards/``).
    target_domains: If provided, only shard files belonging to these domains.
    dry_run:        Classify and report without writing files.

    Returns
    -------
    :class:`ShardManifest` describing every classified file.
    """
    active = set(target_domains) if target_domains else set(Domain)
    entries: List[ShardEntry] = []
    domain_stats: Dict[str, DomainStats] = {d.value: DomainStats(domain=d.value) for d in Domain}

    if not dry_run:
        for dom in active:
            (shards_dir / dom.value).mkdir(parents=True, exist_ok=True)

    for path in sorted(source_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name in _SKIP_FILES or path.name.startswith("."):
            continue
        if any(skip in path.parts for skip in _SKIP_DIRS):
            continue

        rel = path.relative_to(source_dir)
        domain = classify(path)
        if domain not in active:
            continue

        try:
            stat = path.stat()
        except OSError:
            continue

        shard_path = shards_dir / domain.value / rel.as_posix().replace("/", "_")
        sha_prefix = _sha256_prefix(path)
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()

        if not dry_run:
            shard_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                shutil.copy2(path, shard_path)
            except OSError as exc:
                logger.warning("Could not copy %s → %s: %s", path, shard_path, exc)
                continue

        entries.append(
            ShardEntry(
                source_path=str(rel),
                shard_path=str(shard_path.relative_to(shards_dir.parent)
                               if not dry_run else shard_path),
                domain=domain.value,
                size_bytes=stat.st_size,
                sha256_prefix=sha_prefix,
                mtime_iso=mtime,
            )
        )
        domain_stats[domain.value].file_count += 1
        domain_stats[domain.value].total_bytes += stat.st_size

    total_bytes = sum(s.total_bytes for s in domain_stats.values())
    manifest = ShardManifest(
        generated_at=datetime.now(tz=timezone.utc).isoformat(),
        source_dir=str(source_dir),
        shards_dir=str(shards_dir),
        total_files=len(entries),
        total_bytes=total_bytes,
        domains=domain_stats,
        entries=entries,
    )
    return manifest


def run_vacuum_sharding(
    source_dir: Path = DEFAULT_SOURCE_DIR,
    shards_dir: Path = SHARDS_DIR,
    target_domains: Optional[Sequence[Domain]] = None,
    dry_run: bool = False,
    manifest_path: Optional[Path] = None,
) -> ShardManifest:
    """Public entry point: scan, shard, and persist manifest."""
    logger.info("Scanning %s → shards in %s ...", source_dir, shards_dir)
    manifest = scan_and_shard(source_dir, shards_dir, target_domains, dry_run)

    if not dry_run:
        out = manifest_path or MANIFEST_PATH
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(manifest.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Manifest written to %s", out)

    for dom_name, stats in sorted(manifest.domains.items(), key=lambda x: -x[1].file_count):
        if stats.file_count:
            logger.info("  %s: %d files  %s bytes", dom_name, stats.file_count, f"{stats.total_bytes:,}")
    logger.info("Total: %d files / %d bytes", manifest.total_files, manifest.total_bytes)
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
        description="Vacuum-shard worker: classify data/ files into domain shards"
    )
    parser.add_argument("--source-dir", type=Path, default=DEFAULT_SOURCE_DIR)
    parser.add_argument("--shards-dir", type=Path, default=SHARDS_DIR)
    parser.add_argument("--domains", nargs="+", choices=[d.value for d in Domain], default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--manifest-out", type=Path, default=None)
    args = parser.parse_args(argv)

    target = [Domain(d) for d in args.domains] if args.domains else None
    run_vacuum_sharding(args.source_dir, args.shards_dir, target, args.dry_run, args.manifest_out)
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
