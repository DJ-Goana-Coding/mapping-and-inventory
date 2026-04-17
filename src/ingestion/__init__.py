"""
src.ingestion — Phase-2/3 activated harvester entry points.

Thin facade over :mod:`ingestion.omni_harvest` that matches the directives'
mandated paths (``src/ingestion/harvester.py`` and
``src/ingestion/universal_rag.py``).
"""

from src.ingestion.harvester import Harvester, SUPPORTED_EXTENSIONS, PARTITION_COUNT
from src.ingestion.vault_indexer import VaultIndexer, VaultIndexResult
from src.ingestion.universal_rag import UniversalRAGEngine, CulturalRAG

__all__ = [
    "Harvester",
    "SUPPORTED_EXTENSIONS",
    "PARTITION_COUNT",
    "VaultIndexer",
    "VaultIndexResult",
    "UniversalRAGEngine",
    "CulturalRAG",
]
