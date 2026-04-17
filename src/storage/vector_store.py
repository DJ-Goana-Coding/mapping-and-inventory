#!/usr/bin/env python3
"""
🧠 VECTOR BRAIN — Persistent vector store for the Citadel.

A dependency-free vector store that embeds every harvested byte and
persists it to disk.  Embeddings are produced by a deterministic
hash-based encoder (``hash_embed``) so the module is portable across
environments that cannot install heavy ML stacks.  The ``embedder`` is
pluggable — drop in a sentence-transformer or HF-embedding call and the
rest of the pipeline is unaffected.

Every ``upsert`` is atomically flushed to ``<data_dir>/vector_store.json``,
so nothing harvested is ever lost between restarts.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import tempfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

# Embedding dimension for the default hash-based encoder.
EMBEDDING_DIM = 128

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


def _tokenise(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text or "")]


def hash_embed(text: str, dim: int = EMBEDDING_DIM) -> List[float]:
    """Deterministic hash-based bag-of-tokens embedding.

    The result is L2-normalised so cosine similarity collapses to a dot
    product.  Empty / non-text inputs return a zero vector.
    """
    vec = [0.0] * dim
    tokens = _tokenise(text)
    if not tokens:
        return vec
    for tok in tokens:
        h = hashlib.blake2b(tok.encode("utf-8"), digest_size=8).digest()
        idx = int.from_bytes(h[:4], "big") % dim
        sign = 1.0 if (h[4] & 1) else -1.0
        vec[idx] += sign
    norm = math.sqrt(sum(v * v for v in vec))
    if norm == 0.0:
        return vec
    return [v / norm for v in vec]


Embedder = Callable[[str], Sequence[float]]


@dataclass
class VectorRecord:
    """A single persisted vector record."""

    doc_id: str
    text: str
    embedding: List[float]
    metadata: Dict[str, Any] = field(default_factory=dict)
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, payload: Dict[str, Any]) -> "VectorRecord":
        return cls(
            doc_id=payload["doc_id"],
            text=payload.get("text", ""),
            embedding=list(payload.get("embedding") or []),
            metadata=dict(payload.get("metadata") or {}),
            updated_at=payload.get("updated_at")
            or datetime.now(timezone.utc).isoformat(),
        )


def _cosine(a: Sequence[float], b: Sequence[float]) -> float:
    if not a or not b:
        return 0.0
    # Vectors are L2-normalised by the default embedder; still, compute
    # the full cosine so external embedders work correctly.
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class VectorStore:
    """Persistent cosine-similarity vector store."""

    DEFAULT_FILENAME = "vector_store.json"

    def __init__(
        self,
        *,
        data_dir: Optional[Path] = None,
        filename: str = DEFAULT_FILENAME,
        embedder: Optional[Embedder] = None,
        autoflush: bool = True,
    ) -> None:
        self.data_dir = Path(data_dir) if data_dir else (
            Path(__file__).resolve().parents[2] / "data" / "vector_store"
        )
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.data_dir / filename
        self.embedder: Embedder = embedder or hash_embed
        self.autoflush = autoflush
        self._records: Dict[str, VectorRecord] = {}
        self._load()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self.path.exists():
            return
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        for item in payload.get("records", []):
            try:
                rec = VectorRecord.from_json(item)
            except KeyError:
                continue
            self._records[rec.doc_id] = rec

    def flush(self) -> Path:
        """Atomically persist the store to disk."""
        payload = {
            "version": 1,
            "embedding_dim": EMBEDDING_DIM,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "records": [r.to_json() for r in self._records.values()],
        }
        # Atomic write via tempfile + rename.
        fd, tmp_path = tempfile.mkstemp(prefix="vector_store.", suffix=".json", dir=str(self.data_dir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fp:
                json.dump(payload, fp, ensure_ascii=False, indent=2)
            os.replace(tmp_path, self.path)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            raise
        return self.path

    # ------------------------------------------------------------------
    # Upsert / delete
    # ------------------------------------------------------------------

    def upsert(
        self,
        doc_id: str,
        text: str,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VectorRecord:
        """Embed *text* and (re)insert it under *doc_id*."""
        embedding = list(self.embedder(text))
        record = VectorRecord(
            doc_id=doc_id,
            text=text,
            embedding=embedding,
            metadata=dict(metadata or {}),
        )
        self._records[doc_id] = record
        if self.autoflush:
            self.flush()
        return record

    def upsert_many(
        self, items: Iterable[Tuple[str, str, Optional[Dict[str, Any]]]]
    ) -> List[VectorRecord]:
        prev = self.autoflush
        self.autoflush = False
        try:
            records = [self.upsert(did, text, metadata=meta) for did, text, meta in items]
        finally:
            self.autoflush = prev
        if self.autoflush:
            self.flush()
        return records

    def delete(self, doc_id: str) -> bool:
        removed = self._records.pop(doc_id, None) is not None
        if removed and self.autoflush:
            self.flush()
        return removed

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(
        self,
        text: str,
        *,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Return the top-*k* records ranked by cosine similarity.

        ``metadata_filter`` keeps only records whose metadata contains
        every (key, value) pair in the filter.
        """
        if not self._records:
            return []
        embedding = list(self.embedder(text))

        def matches(rec: VectorRecord) -> bool:
            if not metadata_filter:
                return True
            return all(rec.metadata.get(k) == v for k, v in metadata_filter.items())

        scored: List[Tuple[float, VectorRecord]] = []
        for rec in self._records.values():
            if not matches(rec):
                continue
            scored.append((_cosine(embedding, rec.embedding), rec))
        scored.sort(key=lambda pair: pair[0], reverse=True)

        results: List[Dict[str, Any]] = []
        for score, rec in scored[:top_k]:
            results.append(
                {
                    "doc_id": rec.doc_id,
                    "score": score,
                    "metadata": dict(rec.metadata),
                    "text": rec.text,
                }
            )
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def __len__(self) -> int:
        return len(self._records)

    def __contains__(self, doc_id: object) -> bool:
        return doc_id in self._records

    def get(self, doc_id: str) -> Optional[VectorRecord]:
        return self._records.get(doc_id)

    def all_ids(self) -> List[str]:
        return list(self._records.keys())

    def status(self) -> Dict[str, Any]:
        return {
            "record_count": len(self._records),
            "path": str(self.path),
            "embedding_dim": EMBEDDING_DIM,
            "persistent": True,
        }
