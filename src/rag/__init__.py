"""
src.rag — Path-compliance facade for the T.I.A. RAG Query Engine.

The OMNI-RECEPTION directive specifies the literal path
``src/rag/query_engine.py``; the canonical implementation lives at
``src/query/rag_engine.py``.  This package re-exports the same symbols so
both paths resolve to the same objects.
"""

from src.rag.query_engine import (
    BUILTIN_DOMAINS,
    CrossDomainAnswer,
    DomainPredicate,
    RAGQueryEngine,
)

__all__ = [
    "BUILTIN_DOMAINS",
    "CrossDomainAnswer",
    "DomainPredicate",
    "RAGQueryEngine",
]
