#!/usr/bin/env python3
"""
📚 THE GREAT CRAWL — Activated Harvester (Phase 2).

Wraps :class:`ingestion.omni_harvest.github_crawler.GithubCrawler` to fulfil
the extended directive:

  * Use ``GH_TOKEN`` to recursively index all 12 ``DJ-Goana-Coding`` repos.
  * Archive every ``.py``, ``.md``, and ``.json`` file.
  * Prioritise ``CITADEL_BIBLE.md`` and all 46 ``Partition_xx`` folders.

Every harvested document is embedded + persisted into
:class:`src.storage.vector_store.VectorStore` and also funnelled through
:class:`ingestion.universal_rag.UniversalRAG` so the existing Forever-
Learning loop remains the single source of truth.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from ingestion.universal_rag import UniversalRAG
from ingestion.omni_harvest.github_crawler import (
    CITADEL_REPOS,
    CrawlDocument,
    Fetcher,
    GithubCrawler,
)
from src.storage.vector_store import VectorStore


# File types we archive.
SUPPORTED_EXTENSIONS = (".py", ".md", ".json")

# Number of Partition folders that must be prioritised.
PARTITION_COUNT = 46

# Priority regex patterns: Citadel Bible + every Partition_01..46.
_PARTITION_PATTERN = (
    r"(^|/)Partition_(0*[1-9]|[1-3][0-9]|4[0-6])(/|$)"
)
_BIBLE_PATTERN = r"(^|/)CITADEL_BIBLE\.md$"
PRIORITY_PATTERNS = (_BIBLE_PATTERN, _PARTITION_PATTERN)


# A blob-body fetcher lets the harvester pull file contents so the vector
# store receives real bytes instead of metadata stubs.  It is optional and
# offline-safe — if no fetcher is provided the harvester falls back to
# metadata-only embeddings.
BodyFetcher = Callable[[str, str, Optional[str]], Optional[str]]


@dataclass
class HarvestResult:
    """Per-run summary returned by :meth:`Harvester.harvest`."""

    total_documents: int
    archived_documents: int
    priority_documents: int
    vector_records: int
    unavailable_repos: List[str]
    started_at: str
    finished_at: str

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class Harvester:
    """Phase-2 Great Crawl harvester."""

    def __init__(
        self,
        *,
        repos: Sequence[str] = CITADEL_REPOS,
        token: Optional[str] = None,
        fetcher: Optional[Fetcher] = None,
        body_fetcher: Optional[BodyFetcher] = None,
        universal_rag: Optional[UniversalRAG] = None,
        vector_store: Optional[VectorStore] = None,
        ref: str = "HEAD",
    ) -> None:
        self.universal_rag = universal_rag or UniversalRAG()
        self.vector_store = vector_store if vector_store is not None else VectorStore()
        self.body_fetcher = body_fetcher
        self._crawler = GithubCrawler(
            repos=repos,
            token=token,
            fetcher=fetcher,
            priority_patterns=PRIORITY_PATTERNS,
            universal_rag=None,  # the Harvester drives RAG directly
            ref=ref,
        )
        self._last_result: Optional[HarvestResult] = None

    # ------------------------------------------------------------------
    # Filtering
    # ------------------------------------------------------------------

    @staticmethod
    def is_archivable(path: str) -> bool:
        """Return ``True`` when *path* has an archivable extension."""
        lowered = path.lower()
        return any(lowered.endswith(ext) for ext in SUPPORTED_EXTENSIONS)

    # ------------------------------------------------------------------
    # Crawl
    # ------------------------------------------------------------------

    def harvest(self) -> HarvestResult:
        """Execute one Great-Crawl pass across every configured repo."""
        started = datetime.now(timezone.utc).isoformat()
        raw_docs: List[CrawlDocument] = self._crawler.crawl_all()
        archivable = [d for d in raw_docs if self.is_archivable(d.path)]

        # Priority documents first (already sorted by the crawler, but
        # we re-sort after filtering to keep the invariant intact).
        archivable.sort(key=lambda d: (0 if d.priority else 1, d.repo, d.path))

        vector_written = 0
        for doc in archivable:
            body = self._load_body(doc)
            item = self.universal_rag.ingest_story(
                title=f"{doc.repo}:{doc.path}",
                content=body,
                author=doc.repo,
                tags=[
                    "citadel-crawl",
                    "priority" if doc.priority else "standard",
                    doc.path.rsplit(".", 1)[-1].lower(),
                ],
            )
            self.vector_store.upsert(
                doc_id=f"repo:{doc.repo}:{doc.path}",
                text=body,
                metadata={
                    "repo": doc.repo,
                    "path": doc.path,
                    "priority": doc.priority,
                    "source": "github_crawl",
                    "rag_title": item["title"],
                },
            )
            vector_written += 1

        finished = datetime.now(timezone.utc).isoformat()
        result = HarvestResult(
            total_documents=len(raw_docs),
            archived_documents=len(archivable),
            priority_documents=sum(1 for d in archivable if d.priority),
            vector_records=vector_written,
            unavailable_repos=list(self._crawler.status()["unavailable_repos"]),
            started_at=started,
            finished_at=finished,
        )
        self._last_result = result
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_body(self, doc: CrawlDocument) -> str:
        """Return the document body, falling back to metadata stubs."""
        if self.body_fetcher is not None:
            try:
                body = self.body_fetcher(doc.repo, doc.path, self._crawler.token)
            except Exception:  # pragma: no cover - defensive
                body = None
            if body:
                return body
        return (
            f"[Citadel archive stub]\n"
            f"Repository: {doc.repo}\n"
            f"Path: {doc.path}\n"
            f"Priority: {doc.priority}\n"
            f"Size: {doc.size if doc.size is not None else 'unknown'}\n"
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def last_result(self) -> Optional[HarvestResult]:
        return self._last_result

    def status(self) -> Dict[str, Any]:
        return {
            "supported_extensions": list(SUPPORTED_EXTENSIONS),
            "partition_count": PARTITION_COUNT,
            "crawler": self._crawler.status(),
            "vector_store": self.vector_store.status(),
            "last_result": self._last_result.as_dict() if self._last_result else None,
        }
