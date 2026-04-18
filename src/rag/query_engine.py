#!/usr/bin/env python3
"""
🧠 src/rag/query_engine.py — Path-compliance re-export shim.

The OMNI-RECEPTION IGNITION directive mandates the literal module path
``src/rag/query_engine.py``.  The canonical implementation lives at
:mod:`src.query.rag_engine`; this module re-exports its public API so
imports against either path resolve to the same objects.

Example::

    from src.rag.query_engine import RAGQueryEngine

This is the same class instance referenced by ``src.query.rag_engine``;
no duplicate code paths are introduced.
"""

from __future__ import annotations

from src.query.rag_engine import (
    BUILTIN_DOMAINS,
    CrossDomainAnswer,
    DomainPredicate,
    RAGQueryEngine,
    _path_contains,
)

__all__ = [
    "BUILTIN_DOMAINS",
    "CrossDomainAnswer",
    "DomainPredicate",
    "RAGQueryEngine",
    "_path_contains",
]
