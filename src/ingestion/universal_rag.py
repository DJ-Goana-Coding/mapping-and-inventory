#!/usr/bin/env python3
"""
🌐 UNIVERSAL RAG — Total-Ingestion facade (Phase 3).

Directive surface mandated by OMNI-RECEPTION IGNITION ("Activate
``src/ingestion/universal_rag.py``").  This module is the single entry
point used by the rest of the fleet (ARK_CORE, S10, Oppo-Node) to push
arbitrary bytes into the Citadel memory.  It composes:

  * :class:`ingestion.universal_rag.UniversalRAG`  — sovereign-filtered
    cultural/creative ingestion (re-exported as ``CulturalRAG``).
  * :class:`src.ingestion.harvester.Harvester`     — Great-Crawl over
    the 12 ``DJ-Goana-Coding`` repos.
  * :class:`src.ingestion.vault_indexer.VaultIndexer` — recursive
    Partition_01..46 indexing.
  * :class:`src.storage.vector_store.VectorStore` (or FAISS-backed
    :class:`src.storage.faiss_store.FaissVectorStore` when available).

The result is a small, stable API that downstream callers can rely on
without knowing which storage / embedder is wired underneath.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from ingestion.universal_rag import UniversalRAG as CulturalRAG
from src.ingestion.harvester import Harvester
from src.ingestion.vault_indexer import VaultIndexer
from src.storage.vector_store import VectorStore

log = logging.getLogger(__name__)


def _build_default_store() -> VectorStore:
    """Prefer the FAISS-backed store when the dependency is present."""
    try:
        from src.storage.faiss_store import FaissVectorStore  # local import

        return FaissVectorStore()
    except Exception:  # pragma: no cover - faiss not installed in CI
        return VectorStore()


class UniversalRAGEngine:
    """Total-Ingestion engine — single point of truth for the mesh."""

    def __init__(
        self,
        *,
        vector_store: Optional[VectorStore] = None,
        cultural_rag: Optional[CulturalRAG] = None,
        gh_token: Optional[str] = None,
        repos: Optional[Sequence[str]] = None,
    ) -> None:
        self.vector_store = (
            vector_store if vector_store is not None else _build_default_store()
        )
        self.cultural_rag = cultural_rag if cultural_rag is not None else CulturalRAG()
        self.gh_token = gh_token or os.environ.get("GH_TOKEN")
        from ingestion.omni_harvest.github_crawler import CITADEL_REPOS

        self._repos = list(repos) if repos else list(CITADEL_REPOS)
        self.harvester = Harvester(
            repos=self._repos,
            token=self.gh_token,
            universal_rag=self.cultural_rag,
            vector_store=self.vector_store,
        )

    # ------------------------------------------------------------------
    # 1. THE DEEP CRAWL
    # ------------------------------------------------------------------

    def deep_crawl(self) -> Dict[str, Any]:
        """Recursively index all 12 DJ-Goana-Coding repos via ``GH_TOKEN``."""
        result = self.harvester.harvest()
        return result.as_dict()

    # ------------------------------------------------------------------
    # 2. VAULT INDEXING
    # ------------------------------------------------------------------

    def index_vault(self, root: Path) -> Dict[str, Any]:
        """Index every file in the 46 ``Partition_xx`` directories under *root*."""
        indexer = VaultIndexer(root=Path(root), vector_store=self.vector_store)
        return indexer.index_all().as_dict()

    # ------------------------------------------------------------------
    # 3. GENERIC INGEST (used by ARK_CORE / S10 / Oppo-Node)
    # ------------------------------------------------------------------

    def ingest_text(
        self,
        doc_id: str,
        text: str,
        *,
        source: str = "external",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Embed and persist an arbitrary text payload."""
        meta = {"source": source}
        if metadata:
            meta.update(metadata)
        record = self.vector_store.upsert(doc_id=doc_id, text=text, metadata=meta)
        return {"doc_id": record.doc_id, "metadata": record.metadata}

    def ingest_paths(
        self,
        paths: Iterable[Path],
        *,
        source: str = "filesystem",
    ) -> List[Dict[str, Any]]:
        """Read each path and embed its contents."""
        results: List[Dict[str, Any]] = []
        for p in paths:
            path = Path(p)
            if not path.is_file():
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError as exc:
                log.warning("Skipping %s: %s", path, exc)
                continue
            results.append(
                self.ingest_text(
                    doc_id=f"path:{path.as_posix()}",
                    text=text,
                    source=source,
                    metadata={"path": path.as_posix()},
                )
            )
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "repos": list(self._repos),
            "gh_token_present": bool(self.gh_token),
            "vector_store": self.vector_store.status(),
            "harvester": self.harvester.status(),
        }


__all__ = ["UniversalRAGEngine", "CulturalRAG"]
