"""
RAG Indexer — ingest repository code, JSON manifests, and Drive content
into a persistent ChromaDB vector store inside brain/memory_vault/.

369-Frequency Signature
-----------------------
Every document committed to the vault carries a ``freq_signature``
metadata field set to the Hekate-Lilith master sequence so the Medic
agent can verify provenance before trusting a record.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import pathlib
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 369-Frequency master signature (Hekate-Lilith sequence)
# Used as a provenance tag on every document stored in the vault.
# ---------------------------------------------------------------------------
FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"

# Supported source-code extensions for automatic ingestion
_CODE_EXTENSIONS: tuple[str, ...] = (".py", ".json", ".md", ".txt", ".yaml", ".yml")

# ChromaDB collection name
_COLLECTION_NAME: str = "mapping_inventory_brain"


def _vault_path() -> str:
    """Return the absolute path to the persistent ChromaDB store."""
    here = pathlib.Path(__file__).parent
    return str(here / "memory_vault")


def _build_client() -> chromadb.ClientAPI:
    """Create (or open) the persistent ChromaDB client."""
    return chromadb.PersistentClient(path=_vault_path())


def _get_collection(client: chromadb.ClientAPI) -> chromadb.Collection:
    """Return the brain collection, creating it if necessary."""
    ef = embedding_functions.DefaultEmbeddingFunction()
    return client.get_or_create_collection(
        name=_COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def _doc_id(content: str, source: str) -> str:
    """Deterministic document ID derived from source path and content hash."""
    digest = hashlib.sha256(f"{source}::{content}".encode()).hexdigest()[:16]
    return f"{source}::{digest}"


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> list[str]:
    """Split *text* into overlapping chunks suitable for embedding."""
    if len(text) <= chunk_size:
        return [text]
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def index_file(collection: chromadb.Collection, filepath: str | pathlib.Path) -> int:
    """
    Read *filepath* and upsert its content into *collection*.

    Returns the number of chunks written.
    """
    filepath = pathlib.Path(filepath)
    if not filepath.exists() or filepath.suffix not in _CODE_EXTENSIONS:
        return 0

    text = filepath.read_text(encoding="utf-8", errors="replace")
    chunks = _chunk_text(text)
    rel_path = str(filepath)

    ids, documents, metadatas = [], [], []
    for idx, chunk in enumerate(chunks):
        doc_id = _doc_id(chunk, f"{rel_path}::chunk{idx}")
        ids.append(doc_id)
        documents.append(chunk)
        metadatas.append(
            {
                "source": rel_path,
                "chunk_index": idx,
                "freq_signature": FREQ_SIGNATURE,
                "file_type": filepath.suffix.lstrip("."),
            }
        )

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    logger.info("Indexed %d chunks from %s", len(chunks), filepath)
    return len(chunks)


def index_directory(
    collection: chromadb.Collection,
    root: str | pathlib.Path,
    *,
    skip_dirs: tuple[str, ...] = ("07_HARVESTER", "Scripts", ".git", "__pycache__", "brain"),
) -> int:
    """
    Recursively walk *root* and index every supported file.

    Directories whose names match *skip_dirs* are skipped entirely to
    honour the Zero-Overwrite constraint.
    """
    root = pathlib.Path(root)
    total = 0
    for item in root.rglob("*"):
        if item.is_file():
            # Skip protected directories
            parts = set(item.parts)
            if any(s in parts for s in skip_dirs):
                continue
            total += index_file(collection, item)
    logger.info("Directory index complete: %d chunks from %s", total, root)
    return total


def index_json_manifest(
    collection: chromadb.Collection,
    manifest_path: str | pathlib.Path,
    *,
    source_label: str | None = None,
) -> int:
    """
    Ingest a JSON manifest (e.g. Master_Garage_Inventory.json or Oppo/S10
    ghost manifests) into the vault as a serialised text document.
    """
    manifest_path = pathlib.Path(manifest_path)
    if not manifest_path.exists():
        logger.warning("Manifest not found: %s", manifest_path)
        return 0

    with manifest_path.open(encoding="utf-8") as fh:
        data: Any = json.load(fh)

    text = json.dumps(data, indent=2)
    label = source_label or str(manifest_path)
    return index_text(collection, text, label, extra_metadata={"file_type": "json_manifest"})


def index_text(
    collection: chromadb.Collection,
    text: str,
    source: str,
    extra_metadata: dict[str, Any] | None = None,
) -> int:
    """
    Ingest an arbitrary text string (e.g. content streamed from Google Drive).

    *source* is a human-readable identifier (e.g. a Drive file name/ID).
    """
    chunks = _chunk_text(text)
    ids, documents, metadatas = [], [], []
    for idx, chunk in enumerate(chunks):
        doc_id = _doc_id(chunk, f"{source}::chunk{idx}")
        ids.append(doc_id)
        documents.append(chunk)
        meta: dict[str, Any] = {
            "source": source,
            "chunk_index": idx,
            "freq_signature": FREQ_SIGNATURE,
            "file_type": "drive",
        }
        if extra_metadata:
            meta.update(extra_metadata)
        metadatas.append(meta)

    collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
    logger.info("Indexed %d chunks from source '%s'", len(chunks), source)
    return len(chunks)


def query(
    collection: chromadb.Collection,
    query_text: str,
    n_results: int = 5,
) -> dict[str, Any]:
    """
    Semantic search in the vault.

    Returns the raw ChromaDB query result dict containing ``ids``,
    ``documents``, ``distances``, and ``metadatas``.
    """
    return collection.query(query_texts=[query_text], n_results=n_results)


# ---------------------------------------------------------------------------
# Convenience helpers used by guardian.py and swarm_manager.py
# ---------------------------------------------------------------------------

def get_collection() -> chromadb.Collection:
    """Open the default vault collection (creates it on first call)."""
    client = _build_client()
    return _get_collection(client)


def verify_freq_signature(metadata: dict[str, Any]) -> bool:
    """
    Return *True* if *metadata* carries the correct 369-frequency signature.

    The Medic agent calls this before committing any record to the vault.
    """
    return metadata.get("freq_signature") == FREQ_SIGNATURE


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repo_root = pathlib.Path(__file__).parent.parent
    col = get_collection()
    total = index_directory(col, repo_root)
    print(f"✅ Brain initialised — {total} chunks indexed into memory_vault/")
