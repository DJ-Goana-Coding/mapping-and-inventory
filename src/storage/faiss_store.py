#!/usr/bin/env python3
"""
🧠 FAISS Vector Store — persistent FAISS-backed vector brain.

Fulfils the OMNI-RECEPTION directive: "Ensure persistence in the FAISS
vector store."

If the optional ``faiss`` dependency is installed, all queries are routed
through a FAISS ``IndexFlatIP`` for fast cosine search (vectors are L2-
normalised by the default :func:`hash_embed` embedder, so inner-product
== cosine).  When FAISS is **not** installed (the default in this repo's
CI environment) the class transparently falls back to the parent
:class:`VectorStore` linear scan.  The on-disk format is identical
either way, so a deployment can install ``faiss`` later without losing a
single record.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence

from src.storage.vector_store import (
    EMBEDDING_DIM,
    Embedder,
    VectorRecord,
    VectorStore,
    hash_embed,
)

log = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import faiss  # type: ignore
    import numpy as np  # type: ignore

    _FAISS_AVAILABLE = True
except Exception:  # pragma: no cover
    faiss = None  # type: ignore
    np = None  # type: ignore
    _FAISS_AVAILABLE = False


def faiss_available() -> bool:
    """Return True when the optional ``faiss`` dependency is importable."""
    return _FAISS_AVAILABLE


class FaissVectorStore(VectorStore):
    """Drop-in :class:`VectorStore` replacement using FAISS for ANN."""

    DEFAULT_FILENAME = "vector_store_faiss.json"

    def __init__(
        self,
        *,
        data_dir: Optional[Path] = None,
        filename: str = DEFAULT_FILENAME,
        embedder: Optional[Embedder] = None,
        autoflush: bool = True,
    ) -> None:
        super().__init__(
            data_dir=data_dir,
            filename=filename,
            embedder=embedder,
            autoflush=autoflush,
        )
        self._faiss_index = None  # built lazily
        self._faiss_ids: List[str] = []
        self._faiss_dirty = True

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _ensure_index(self) -> None:
        if not _FAISS_AVAILABLE:
            return
        if self._faiss_index is not None and not self._faiss_dirty:
            return
        # (Re)build FAISS index from current records.
        index = faiss.IndexFlatIP(EMBEDDING_DIM)  # type: ignore[union-attr]
        ids: List[str] = []
        vectors: List[List[float]] = []
        for rec in self._records.values():
            if not rec.embedding:
                continue
            vectors.append(rec.embedding)
            ids.append(rec.doc_id)
        if vectors:
            arr = np.asarray(vectors, dtype="float32")  # type: ignore[union-attr]
            index.add(arr)
        self._faiss_index = index
        self._faiss_ids = ids
        self._faiss_dirty = False

    # ------------------------------------------------------------------
    # Override mutating ops to invalidate the FAISS index
    # ------------------------------------------------------------------

    def upsert(self, doc_id: str, text: str, *, metadata=None) -> VectorRecord:
        rec = super().upsert(doc_id, text, metadata=metadata)
        self._faiss_dirty = True
        return rec

    def delete(self, doc_id: str) -> bool:
        removed = super().delete(doc_id)
        if removed:
            self._faiss_dirty = True
        return removed

    # ------------------------------------------------------------------
    # Query — FAISS path with linear-scan fallback
    # ------------------------------------------------------------------

    def query(
        self,
        text: str,
        *,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if not _FAISS_AVAILABLE or not self._records:
            return super().query(
                text, top_k=top_k, metadata_filter=metadata_filter
            )

        self._ensure_index()
        if not self._faiss_ids:
            return []

        # Over-fetch to give the metadata filter room to discard hits.
        fetch_k = top_k * 5 if metadata_filter else top_k
        fetch_k = max(1, min(fetch_k, len(self._faiss_ids)))

        embedding = list(self.embedder(text))
        query_vec = np.asarray([embedding], dtype="float32")  # type: ignore[union-attr]
        scores, idx = self._faiss_index.search(query_vec, fetch_k)  # type: ignore[union-attr]

        results: List[Dict[str, Any]] = []
        for score, i in zip(scores[0].tolist(), idx[0].tolist()):
            if i < 0 or i >= len(self._faiss_ids):
                continue
            doc_id = self._faiss_ids[i]
            rec = self._records.get(doc_id)
            if rec is None:
                continue
            if metadata_filter and not all(
                rec.metadata.get(k) == v for k, v in metadata_filter.items()
            ):
                continue
            results.append(
                {
                    "doc_id": rec.doc_id,
                    "score": float(score),
                    "metadata": dict(rec.metadata),
                    "text": rec.text,
                }
            )
            if len(results) >= top_k:
                break
        return results

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        info = super().status()
        info["faiss_available"] = _FAISS_AVAILABLE
        info["backend"] = "faiss" if _FAISS_AVAILABLE else "linear"
        return info


__all__ = ["FaissVectorStore", "faiss_available"]
