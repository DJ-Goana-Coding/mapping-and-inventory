"""
services/rag_hub.py — Master Hub RAG engine.

Provides a small, dependency-light FAISS-backed semantic index over the
"Master Harvest" fragments (TIA_MASTER_HARVEST.txt, AETHER manifests,
harvest reports, and the master_harvest_manifest.json). Used by the
FastAPI sidecar (main_api.py) to serve /v1/ingest and /v1/query.

Design goals
------------
* Zero side-effects at import time: heavy deps (faiss, sentence-transformers)
  are imported lazily inside ``_get_model`` / ``_get_faiss`` so unit tests and
  the Streamlit faceplate can import this module without paying the cost.
* Deterministic on-disk layout under ``data/vector_store/`` so the index
  survives container restarts and is easy to ship in the HF Space.
* Cross-mesh: ``DEFAULT_FRAGMENT_PATHS`` enumerates every Master Harvest
  fragment family (TIA, AETHER, generic harvest reports, manifest schema)
  so ``/v1/query`` searches across the whole mesh out of the box.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import threading
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

logger = logging.getLogger("rag_hub")

# ---------------------------------------------------------------------------
# Paths & defaults
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
VECTOR_STORE_DIR = REPO_ROOT / "data" / "vector_store"
INDEX_PATH = VECTOR_STORE_DIR / "harvest.index"
META_PATH = VECTOR_STORE_DIR / "harvest_meta.json"

# Embedding model — small, CPU-friendly, ships under ~90 MB.
EMBEDDING_MODEL_NAME = os.environ.get(
    "RAG_HUB_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)
EMBEDDING_DIM = 384  # MiniLM-L6-v2 fixed dimension

# Canonical Master Harvest fragments. Globs are evaluated relative to REPO_ROOT.
# Cross-mesh weld: covers TIA, AETHER, generic harvest reports, and the
# machine-readable manifest schema, so /v1/query can answer questions that
# span every fragment family without further configuration.
DEFAULT_FRAGMENT_GLOBS: Sequence[str] = (
    "TIA_MASTER_HARVEST.txt",
    "AETHER_HARVEST_COMPLETE.md",
    "harvest_report.md",
    "data/master_harvest_manifest.json",
    "data/AETHER_HARVEST_DISCOVERY_MANIFEST.json",
    "data/master_harvest/INDEX.md",
)

# Chunking parameters. Conservative defaults — small enough to keep the
# embedding cost low, large enough to retain useful local context.
CHUNK_CHAR_SIZE = 1200
CHUNK_CHAR_OVERLAP = 150


# ---------------------------------------------------------------------------
# Lazy heavy-dep accessors
# ---------------------------------------------------------------------------

_model_lock = threading.Lock()
_model_singleton = None


def _get_model():
    """Lazy-load and cache the sentence-transformers model."""
    global _model_singleton
    if _model_singleton is not None:
        return _model_singleton
    with _model_lock:
        if _model_singleton is None:
            from sentence_transformers import SentenceTransformer  # noqa: WPS433

            logger.info("Loading embedding model %s", EMBEDDING_MODEL_NAME)
            _model_singleton = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _model_singleton


def _get_faiss():
    """Lazy import of faiss so import-time stays cheap."""
    import faiss  # noqa: WPS433

    return faiss


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Chunk:
    """A single indexed text chunk."""

    id: int
    source: str  # path relative to REPO_ROOT
    chunk_index: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QueryResult:
    source: str
    chunk_index: int
    score: float
    text: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class IndexState:
    chunks: List[Chunk] = field(default_factory=list)
    model_name: str = EMBEDDING_MODEL_NAME
    dim: int = EMBEDDING_DIM


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_dirs() -> None:
    VECTOR_STORE_DIR.mkdir(parents=True, exist_ok=True)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        logger.warning("Could not read %s: %s", path, exc)
        return ""


def _chunk_text(
    text: str,
    size: int = CHUNK_CHAR_SIZE,
    overlap: int = CHUNK_CHAR_OVERLAP,
) -> List[str]:
    if not text:
        return []
    if size <= 0:
        raise ValueError("size must be positive")
    if overlap < 0 or overlap >= size:
        raise ValueError("overlap must be >= 0 and < size")
    step = size - overlap
    chunks: List[str] = []
    for start in range(0, len(text), step):
        piece = text[start : start + size].strip()
        if piece:
            chunks.append(piece)
        if start + size >= len(text):
            break
    return chunks


def _resolve_fragments(
    globs: Sequence[str], extra_paths: Optional[Iterable[str]] = None
) -> List[Path]:
    """Resolve fragment glob patterns against REPO_ROOT, deduped & sorted."""
    seen: set[Path] = set()
    out: List[Path] = []
    patterns = list(globs)
    if extra_paths:
        patterns.extend(extra_paths)
    for pattern in patterns:
        for match in sorted(REPO_ROOT.glob(pattern)):
            if match.is_file() and match not in seen:
                seen.add(match)
                out.append(match)
    return out


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class RagHub:
    """In-memory + on-disk RAG index over Master Harvest fragments."""

    def __init__(self, vector_store_dir: Path = VECTOR_STORE_DIR) -> None:
        self.vector_store_dir = vector_store_dir
        self.index_path = vector_store_dir / "harvest.index"
        self.meta_path = vector_store_dir / "harvest_meta.json"
        self._lock = threading.Lock()
        self._state: Optional[IndexState] = None
        self._faiss_index = None

    # --- persistence -------------------------------------------------------

    def _load_meta(self) -> Optional[IndexState]:
        if not self.meta_path.exists():
            return None
        try:
            raw = json.loads(self.meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            logger.warning("Could not load index meta: %s", exc)
            return None
        chunks = [Chunk(**c) for c in raw.get("chunks", [])]
        return IndexState(
            chunks=chunks,
            model_name=raw.get("model_name", EMBEDDING_MODEL_NAME),
            dim=int(raw.get("dim", EMBEDDING_DIM)),
        )

    def _save_meta(self, state: IndexState) -> None:
        _ensure_dirs()
        payload = {
            "model_name": state.model_name,
            "dim": state.dim,
            "chunks": [c.to_dict() for c in state.chunks],
        }
        self.meta_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def load(self) -> bool:
        """Load index from disk. Returns True if a usable index was loaded."""
        with self._lock:
            state = self._load_meta()
            if state is None or not state.chunks or not self.index_path.exists():
                return False
            faiss = _get_faiss()
            try:
                self._faiss_index = faiss.read_index(str(self.index_path))
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not read FAISS index: %s", exc)
                return False
            self._state = state
            return True

    # --- ingestion ---------------------------------------------------------

    def reindex(
        self,
        extra_paths: Optional[Iterable[str]] = None,
        globs: Sequence[str] = DEFAULT_FRAGMENT_GLOBS,
    ) -> dict:
        """Rebuild the FAISS index from Master Harvest fragments on disk."""
        with self._lock:
            fragments = _resolve_fragments(globs, extra_paths)
            chunks: List[Chunk] = []
            chunk_id = 0
            for path in fragments:
                rel = path.relative_to(REPO_ROOT).as_posix()
                text = _read_text(path)
                pieces = _chunk_text(text)
                for idx, piece in enumerate(pieces):
                    chunks.append(
                        Chunk(id=chunk_id, source=rel, chunk_index=idx, text=piece)
                    )
                    chunk_id += 1

            if not chunks:
                logger.warning("No chunks produced; nothing to index")
                self._state = IndexState(chunks=[])
                self._faiss_index = None
                # Still persist an empty meta so callers can introspect state.
                self._save_meta(self._state)
                return {
                    "fragments": [p.relative_to(REPO_ROOT).as_posix() for p in fragments],
                    "chunks_indexed": 0,
                }

            model = _get_model()
            embeddings = model.encode(
                [c.text for c in chunks],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )

            faiss = _get_faiss()
            dim = int(embeddings.shape[1])
            # Inner-product on L2-normalized vectors == cosine similarity.
            index = faiss.IndexFlatIP(dim)
            index.add(embeddings)

            _ensure_dirs()
            faiss.write_index(index, str(self.index_path))

            self._state = IndexState(chunks=chunks, dim=dim)
            self._faiss_index = index
            self._save_meta(self._state)

            return {
                "fragments": [p.relative_to(REPO_ROOT).as_posix() for p in fragments],
                "chunks_indexed": len(chunks),
                "dim": dim,
            }

    # --- query -------------------------------------------------------------

    def query(self, q: str, k: int = 5) -> List[QueryResult]:
        if not q or not q.strip():
            return []
        if k <= 0:
            return []

        with self._lock:
            if self._state is None or self._faiss_index is None:
                # Try to lazily load from disk before giving up.
                if not self.load():
                    return []

            assert self._state is not None
            assert self._faiss_index is not None
            if not self._state.chunks:
                return []

            model = _get_model()
            embedding = model.encode(
                [q],
                convert_to_numpy=True,
                normalize_embeddings=True,
                show_progress_bar=False,
            )
            top_k = min(k, len(self._state.chunks))
            scores, ids = self._faiss_index.search(embedding, top_k)

            out: List[QueryResult] = []
            for score, idx in zip(scores[0].tolist(), ids[0].tolist()):
                if idx < 0 or idx >= len(self._state.chunks):
                    continue
                chunk = self._state.chunks[idx]
                out.append(
                    QueryResult(
                        source=chunk.source,
                        chunk_index=chunk.chunk_index,
                        score=float(score),
                        text=chunk.text,
                    )
                )
            return out

    # --- introspection -----------------------------------------------------

    def stats(self) -> dict:
        with self._lock:
            if self._state is None:
                # Try to load once for accurate stats.
                self.load()
            chunks = self._state.chunks if self._state else []
            sources = sorted({c.source for c in chunks})
            return {
                "loaded": self._faiss_index is not None,
                "chunks": len(chunks),
                "sources": sources,
                "model": self._state.model_name if self._state else EMBEDDING_MODEL_NAME,
                "vector_store_dir": str(self.vector_store_dir),
            }


# Module-level singleton convenience for the FastAPI sidecar.
_default_hub: Optional[RagHub] = None
_default_hub_lock = threading.Lock()


def get_hub() -> RagHub:
    global _default_hub
    if _default_hub is not None:
        return _default_hub
    with _default_hub_lock:
        if _default_hub is None:
            _default_hub = RagHub()
            # Best-effort load; ignore failures (will be rebuilt on first ingest).
            _default_hub.load()
    return _default_hub


# ---------------------------------------------------------------------------
# CLI entry point: ``python -m services.rag_hub --reindex``
# ---------------------------------------------------------------------------


def _main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Master Harvest RAG hub")
    parser.add_argument("--reindex", action="store_true", help="Rebuild the FAISS index from disk")
    parser.add_argument("--query", type=str, default=None, help="Run a query against the index")
    parser.add_argument("-k", type=int, default=5, help="Top-k results for --query")
    parser.add_argument("--stats", action="store_true", help="Print index stats and exit")
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    hub = RagHub()

    if args.reindex:
        result = hub.reindex()
        print(json.dumps(result, indent=2))

    if args.query:
        if not hub.load() and not args.reindex:
            print("[!] No index found. Run with --reindex first.")
            return 1
        results = hub.query(args.query, k=args.k)
        print(json.dumps([r.to_dict() for r in results], indent=2, ensure_ascii=False))

    if args.stats or (not args.reindex and not args.query):
        print(json.dumps(hub.stats(), indent=2))

    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(_main())
