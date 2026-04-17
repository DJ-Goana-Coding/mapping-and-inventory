"""src.storage — persistent vector brain for the Citadel."""

from src.storage.vector_store import (
    VectorStore,
    VectorRecord,
    hash_embed,
    EMBEDDING_DIM,
)

__all__ = ["VectorStore", "VectorRecord", "hash_embed", "EMBEDDING_DIM"]
