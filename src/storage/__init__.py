"""src.storage — persistent vector brain for the Citadel."""

from src.storage.vector_store import (
    VectorStore,
    VectorRecord,
    hash_embed,
    EMBEDDING_DIM,
)
from src.storage.faiss_store import FaissVectorStore, faiss_available

__all__ = [
    "VectorStore",
    "VectorRecord",
    "hash_embed",
    "EMBEDDING_DIM",
    "FaissVectorStore",
    "faiss_available",
]
