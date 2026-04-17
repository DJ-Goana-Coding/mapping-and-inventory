#!/usr/bin/env python3
"""
🧠 T.I.A. RAG QUERY ENGINE — Cross-Domain Inference surface.

Wraps :class:`src.storage.vector_store.VectorStore` with a thin RAG-style
query engine that T.I.A. can use to perform cross-domain inference, e.g.::

    engine.cross_domain_inference(
        "Compare Partition_01 logic with today's Vortex trade logs",
        domains=["partition_01", "vortex"],
    )

Each "domain" is expressed as a metadata predicate (simple key/value
filters).  The engine returns the top matching records for each domain
plus a joint similarity score so T.I.A. can reason across them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Sequence

from src.storage.vector_store import VectorStore


# Predicate used to classify a record into a "domain" (e.g. Partition_01,
# Vortex trade logs, etc.).  The predicate receives the record metadata
# and returns a bool.
DomainPredicate = Callable[[Mapping[str, Any]], bool]


def _path_contains(substring: str) -> DomainPredicate:
    lowered = substring.lower()

    def predicate(meta: Mapping[str, Any]) -> bool:
        path = str(meta.get("path") or meta.get("source") or "").lower()
        return lowered in path

    return predicate


# Built-in cross-domain shortcuts used by the directive examples.
BUILTIN_DOMAINS: Dict[str, DomainPredicate] = {
    "citadel_bible": _path_contains("CITADEL_BIBLE.md"),
    "vortex": _path_contains("vortex"),
    "archive_vault": lambda meta: str(meta.get("source", "")).lower() == "archive_vault",
    "districts": lambda meta: str(meta.get("source", "")).lower() == "districts",
    "forever_learning": lambda meta: str(meta.get("source", "")).lower()
    == "forever_learning",
    "github_crawl": lambda meta: str(meta.get("source", "")).lower() == "github_crawl",
    "gdrive": lambda meta: str(meta.get("source", "")).lower() == "gdrive",
}

# Also register one alias per Partition_01..46.
for _n in range(1, 47):
    BUILTIN_DOMAINS[f"partition_{_n:02d}"] = _path_contains(f"Partition_{_n:02d}")


@dataclass
class CrossDomainAnswer:
    """Result of a :meth:`RAGQueryEngine.cross_domain_inference` call."""

    query: str
    domains: List[str]
    per_domain: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    joint_score: float = 0.0
    generated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "domains": list(self.domains),
            "per_domain": {k: list(v) for k, v in self.per_domain.items()},
            "joint_score": self.joint_score,
            "generated_at": self.generated_at,
        }


class RAGQueryEngine:
    """RAG query engine with cross-domain inference."""

    def __init__(
        self,
        *,
        vector_store: Optional[VectorStore] = None,
        domain_registry: Optional[Dict[str, DomainPredicate]] = None,
    ) -> None:
        self.vector_store = vector_store if vector_store is not None else VectorStore()
        self.domains: Dict[str, DomainPredicate] = dict(BUILTIN_DOMAINS)
        if domain_registry:
            self.domains.update(domain_registry)

    # ------------------------------------------------------------------
    # Domain registration
    # ------------------------------------------------------------------

    def register_domain(self, name: str, predicate: DomainPredicate) -> None:
        self.domains[name.lower()] = predicate

    def list_domains(self) -> List[str]:
        return sorted(self.domains.keys())

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve(
        self,
        query: str,
        *,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Return top-*k* records from the vector store."""
        return self.vector_store.query(
            query, top_k=top_k, metadata_filter=metadata_filter
        )

    # ------------------------------------------------------------------
    # Cross-domain inference
    # ------------------------------------------------------------------

    def cross_domain_inference(
        self,
        query: str,
        *,
        domains: Sequence[str],
        top_k: int = 5,
    ) -> CrossDomainAnswer:
        """Retrieve the top-*k* records per declared domain.

        Unknown domain names are accepted as free-text substring
        predicates over the ``path`` / ``source`` metadata.
        """
        if not domains:
            raise ValueError("cross_domain_inference requires at least one domain")

        all_results = self.vector_store.query(query, top_k=max(50, top_k * 10))

        per_domain: Dict[str, List[Dict[str, Any]]] = {}
        joint_total = 0.0
        joint_count = 0

        for domain in domains:
            key = domain.lower()
            predicate = self.domains.get(key) or _path_contains(domain)
            hits = [r for r in all_results if predicate(r.get("metadata") or {})][:top_k]
            per_domain[domain] = hits
            if hits:
                joint_total += max(r["score"] for r in hits)
                joint_count += 1

        joint_score = joint_total / joint_count if joint_count else 0.0
        return CrossDomainAnswer(
            query=query,
            domains=list(domains),
            per_domain=per_domain,
            joint_score=joint_score,
        )

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "vector_store": self.vector_store.status(),
            "domain_count": len(self.domains),
            "builtin_domains": sorted(BUILTIN_DOMAINS.keys())[:10],
        }
