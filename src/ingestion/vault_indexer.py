#!/usr/bin/env python3
"""
🗄️ VAULT INDEXER — Partition_01..46 deep recursion.

Walks ``Partition_01`` through ``Partition_46`` under a given root and
embeds **every** file (regardless of extension) into the persistent
vector store.  The directive is explicit: these are the Citadel's
"primary memory banks", so we do not filter by file type the way the
GitHub Great-Crawl harvester does.

Binary or otherwise undecodable files are read with ``errors='replace'``
and stored as best-effort UTF-8.  Files exceeding ``max_bytes`` (default
1 MiB) are truncated.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from src.storage.vector_store import VectorStore

log = logging.getLogger(__name__)

PARTITION_RE = re.compile(r"^Partition_(0*[1-9]|[1-3][0-9]|4[0-6])$")

# Files larger than this many bytes are truncated to keep embeddings sane.
DEFAULT_MAX_BYTES = 1 * 1024 * 1024


@dataclass
class VaultIndexResult:
    """Summary returned by :meth:`VaultIndexer.index_all`."""

    partitions_seen: List[str] = field(default_factory=list)
    files_indexed: int = 0
    bytes_indexed: int = 0
    skipped_files: int = 0
    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: str = ""

    def as_dict(self) -> Dict[str, Any]:
        return asdict(self)


class VaultIndexer:
    """Recursive Partition vault indexer."""

    def __init__(
        self,
        *,
        root: Path,
        vector_store: Optional[VectorStore] = None,
        max_bytes: int = DEFAULT_MAX_BYTES,
    ) -> None:
        self.root = Path(root)
        self.vector_store = (
            vector_store if vector_store is not None else VectorStore()
        )
        self.max_bytes = max_bytes

    # ------------------------------------------------------------------
    # Discovery
    # ------------------------------------------------------------------

    def discover_partitions(self) -> List[Path]:
        """Return existing ``Partition_xx`` directories under ``root``."""
        if not self.root.is_dir():
            return []
        partitions: List[Path] = []
        for entry in sorted(self.root.iterdir()):
            if entry.is_dir() and PARTITION_RE.match(entry.name):
                partitions.append(entry)
        return partitions

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index_all(self) -> VaultIndexResult:
        """Index every file in every discovered Partition directory."""
        result = VaultIndexResult()
        partitions = self.discover_partitions()
        result.partitions_seen = [p.name for p in partitions]

        # Disable autoflush during a bulk pass for speed; flush once at end.
        prev_autoflush = self.vector_store.autoflush
        self.vector_store.autoflush = False
        try:
            for partition in partitions:
                self._index_partition(partition, result)
        finally:
            self.vector_store.autoflush = prev_autoflush
            self.vector_store.flush()

        result.finished_at = datetime.now(timezone.utc).isoformat()
        return result

    def _index_partition(self, partition: Path, result: VaultIndexResult) -> None:
        for path in sorted(partition.rglob("*")):
            if not path.is_file():
                continue
            try:
                size = path.stat().st_size
            except OSError as exc:
                log.warning("vault: cannot stat %s: %s", path, exc)
                result.skipped_files += 1
                continue
            try:
                if size > self.max_bytes:
                    with path.open("rb") as fp:
                        raw = fp.read(self.max_bytes)
                    text = raw.decode("utf-8", errors="replace")
                    truncated = True
                else:
                    text = path.read_text(encoding="utf-8", errors="replace")
                    truncated = False
            except OSError as exc:
                log.warning("vault: cannot read %s: %s", path, exc)
                result.skipped_files += 1
                continue

            relative = path.relative_to(self.root).as_posix()
            self.vector_store.upsert(
                doc_id=f"vault:{relative}",
                text=text,
                metadata={
                    "source": "vault",
                    "partition": partition.name,
                    "path": relative,
                    "bytes": size,
                    "truncated": truncated,
                },
            )
            result.files_indexed += 1
            result.bytes_indexed += min(size, self.max_bytes)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def index_iterable(self, paths: Iterable[Path]) -> int:
        """Index an arbitrary iterable of *paths*; returns count indexed."""
        n = 0
        for p in paths:
            path = Path(p)
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            self.vector_store.upsert(
                doc_id=f"vault:{path.as_posix()}",
                text=text,
                metadata={"source": "vault", "path": path.as_posix()},
            )
            n += 1
        return n
