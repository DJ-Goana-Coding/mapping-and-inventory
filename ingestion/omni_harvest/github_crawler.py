#!/usr/bin/env python3
"""
📚 THE GREAT CRAWL — GitHub indexer for the 12 Citadel repos.

Uses the ``GH_TOKEN`` sprayed by ARK_CORE to recursively index all repos
in the mesh, prioritising ``CITADEL_BIBLE.md``, ``V19_NORDIC_MATRIX.md``
and all ``Partition_xx`` folders.

Network calls are performed via a pluggable ``fetcher`` callable so the
crawler is fully testable offline.  The default fetcher uses
``urllib`` against the GitHub REST API — if it is unavailable the crawl
degrades gracefully and records the failure.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence

from ingestion.universal_rag import UniversalRAG


# ---------------------------------------------------------------------------
# The 12 Citadel repositories
# ---------------------------------------------------------------------------

CITADEL_REPOS: Sequence[str] = (
    "DJ-Goana-Coding/mapping-and-inventory",
    "DJ-Goana-Coding/tia-architect-core",
    "DJ-Goana-Coding/tia-citadel",
    "DJ-Goana-Coding/sentinel-scout",
    "DJ-Goana-Coding/vamguard-titan",
    "DJ-Goana-Coding/omega-trader",
    "DJ-Goana-Coding/omega-omni",
    "DJ-Goana-Coding/bridge-nexus",
    "DJ-Goana-Coding/quantum-forge",
    "DJ-Goana-Coding/persona-modules",
    "DJ-Goana-Coding/archive-scrolls",
    "DJ-Goana-Coding/zenith-view",
)

# Priority filename / path regex patterns.  Anything matching one of
# these is ingested first.
PRIORITY_PATTERNS: Sequence[str] = (
    r"(^|/)CITADEL_BIBLE\.md$",
    r"(^|/)V19_NORDIC_MATRIX\.md$",
    r"(^|/)Partition_\d+(/|$)",
)


Fetcher = Callable[[str, str, Optional[str]], List[Dict[str, Any]]]
"""Signature: ``fetcher(owner_repo, ref, token) -> list[{"path", "type", ...}]``."""


# ---------------------------------------------------------------------------
# Default fetcher (GitHub tree API) — best-effort, offline-safe.
# ---------------------------------------------------------------------------

def _default_fetcher(owner_repo: str, ref: str, token: Optional[str]) -> List[Dict[str, Any]]:
    """Best-effort GitHub REST fetcher.

    Uses the git-trees recursive endpoint.  Returns an empty list (and
    does *not* raise) when the network is unreachable or the token is
    invalid — the crawler will record that repo as unavailable.
    """
    try:  # pragma: no cover - network path, exercised only in live runs
        import urllib.request
        import urllib.error

        url = f"https://api.github.com/repos/{owner_repo}/git/trees/{ref}?recursive=1"
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json"})
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(req, timeout=15) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
        return [entry for entry in payload.get("tree", []) if entry.get("type") == "blob"]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Crawl artefacts
# ---------------------------------------------------------------------------

@dataclass
class CrawlDocument:
    """A single document discovered by the Great Crawl."""

    repo: str
    path: str
    priority: bool
    size: Optional[int] = None
    sha: Optional[str] = None
    discovered_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_rag_item(self) -> Dict[str, Any]:
        """Convert to the UniversalRAG ``ingest_story`` payload shape."""
        title = f"{self.repo}:{self.path}"
        content = (
            f"Repository: {self.repo}\n"
            f"Path: {self.path}\n"
            f"Priority: {self.priority}\n"
            f"Size: {self.size if self.size is not None else 'unknown'}\n"
        )
        return {
            "title": title,
            "content": content,
            "tags": ["citadel-crawl", "priority" if self.priority else "standard"],
        }


# ---------------------------------------------------------------------------
# GithubCrawler
# ---------------------------------------------------------------------------

class GithubCrawler:
    """Recursive indexer for the 12 Citadel repos.

    Parameters
    ----------
    repos:
        Sequence of ``owner/repo`` strings. Defaults to
        :data:`CITADEL_REPOS`.
    token:
        Optional GitHub token. Falls back to ``os.environ['GH_TOKEN']``.
    fetcher:
        Pluggable tree fetcher — see :data:`Fetcher`.  The default uses
        ``urllib`` against the GitHub REST API; tests can inject a stub.
    priority_patterns:
        Regex patterns (compiled against each file path). Matches are
        ingested first.
    universal_rag:
        Optional :class:`UniversalRAG` instance used to stream documents
        into the vector store.
    """

    def __init__(
        self,
        *,
        repos: Optional[Sequence[str]] = None,
        token: Optional[str] = None,
        fetcher: Optional[Fetcher] = None,
        priority_patterns: Optional[Sequence[str]] = None,
        universal_rag: Optional[UniversalRAG] = None,
        ref: str = "HEAD",
    ) -> None:
        self.repos: List[str] = list(repos) if repos is not None else list(CITADEL_REPOS)
        self.token = token if token is not None else os.environ.get("GH_TOKEN")
        self._fetcher: Fetcher = fetcher or _default_fetcher
        self._patterns = [
            re.compile(p) for p in (priority_patterns or PRIORITY_PATTERNS)
        ]
        self.universal_rag = universal_rag
        self.ref = ref

        self._unavailable: List[str] = []
        self._last_crawl: List[CrawlDocument] = []

    # ------------------------------------------------------------------
    # Crawl
    # ------------------------------------------------------------------

    def is_priority(self, path: str) -> bool:
        """Return ``True`` when *path* matches any priority pattern."""
        return any(p.search(path) for p in self._patterns)

    def crawl_repo(self, owner_repo: str) -> List[CrawlDocument]:
        """Crawl a single repository and return discovered documents."""
        entries = self._fetcher(owner_repo, self.ref, self.token)
        if not entries:
            self._unavailable.append(owner_repo)
            return []

        docs: List[CrawlDocument] = []
        for entry in entries:
            path = entry.get("path", "")
            if not path:
                continue
            docs.append(
                CrawlDocument(
                    repo=owner_repo,
                    path=path,
                    priority=self.is_priority(path),
                    size=entry.get("size"),
                    sha=entry.get("sha"),
                )
            )
        # Priority files first, then alphabetical by path for stable ordering.
        docs.sort(key=lambda d: (0 if d.priority else 1, d.path))
        return docs

    def crawl_all(self) -> List[CrawlDocument]:
        """Crawl every configured repo and return the combined document list.

        Priority documents across *all* repos come first, preserving the
        directive's requirement to ingest Bible / Nordic Matrix / Partitions
        before the long tail of ordinary files.
        """
        self._unavailable = []
        all_docs: List[CrawlDocument] = []
        for repo in self.repos:
            all_docs.extend(self.crawl_repo(repo))

        all_docs.sort(key=lambda d: (0 if d.priority else 1, d.repo, d.path))
        self._last_crawl = all_docs

        if self.universal_rag is not None:
            for doc in all_docs:
                payload = doc.as_rag_item()
                self.universal_rag.ingest_story(
                    payload["title"],
                    payload["content"],
                    author=doc.repo,
                    tags=payload["tags"],
                )
        return all_docs

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def priority_documents(self) -> List[CrawlDocument]:
        """Return the priority subset of the last crawl."""
        return [d for d in self._last_crawl if d.priority]

    def status(self) -> Dict[str, Any]:
        return {
            "repo_count": len(self.repos),
            "token_present": bool(self.token),
            "last_document_count": len(self._last_crawl),
            "last_priority_count": len(self.priority_documents()),
            "unavailable_repos": list(self._unavailable),
            "priority_patterns": [p.pattern for p in self._patterns],
        }
