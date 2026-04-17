"""RAG ingestion engine for the Mapping-and-Inventory hub.

Reads knowledge sources (master harvest markdown archives + the legacy
``master_intelligence_map.txt``) and builds a FAISS vector store that the
downstream Oracle / semantic search layer can query.

Hardened for production:

* Heavy optional deps (``sentence-transformers``, ``faiss``, ``numpy``) are
  imported lazily so a missing wheel can never take down the whole Space.
* A deterministic mock-embedding fallback keeps the pipeline functional when
  the real transformer stack is unavailable.
* The ingest source directory defaults to ``data/master_harvest/`` but can be
  overridden via CLI args or the ``MASTER_HARVEST_DIR`` env var so the core
  ingestion scripts stay mapped to the central archive drop-zone.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("rag_ingest")

# Default locations used across the Citadel mesh.
DEFAULT_HARVEST_DIR = Path(os.environ.get("MASTER_HARVEST_DIR", "data/master_harvest"))
DEFAULT_LEGACY_MAP = Path("master_intelligence_map.txt")
DEFAULT_RAG_STORE = Path(os.environ.get("RAG_STORE_DIR", "rag_store"))
EMBED_MODEL_NAME = os.environ.get("RAG_EMBED_MODEL", "all-MiniLM-L6-v2")
MOCK_DIM = 384  # matches all-MiniLM-L6-v2


def _read_text_file(path: Path) -> List[str]:
    """Read a text file and return non-empty stripped lines."""
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            return [line.strip() for line in f if line.strip()]
    except OSError as exc:
        logger.warning("⚠️  Could not read %s: %s", path, exc)
        return []


def load_map(path) -> List[str]:
    """Backwards-compatible loader for a single intelligence map file."""
    p = Path(path)
    if not p.exists():
        logger.warning("%s not found. Returning empty list.", p)
        return []
    return _read_text_file(p)


def load_harvest_corpus(
    harvest_dir: Path = DEFAULT_HARVEST_DIR,
    legacy_map: Path = DEFAULT_LEGACY_MAP,
) -> Tuple[List[str], List[dict]]:
    """Collect every ingest-worthy line from the master harvest directory.

    Falls back to ``master_intelligence_map.txt`` when the directory is empty
    or missing so existing workflows keep functioning.

    Returns a tuple of ``(lines, line_metadata)`` where ``line_metadata`` is a
    list parallel to ``lines`` describing the source file for each entry.
    """
    lines: List[str] = []
    line_metadata: List[dict] = []

    harvest_dir = Path(harvest_dir)
    if harvest_dir.exists() and harvest_dir.is_dir():
        logger.info("📂 Scanning harvest directory: %s", harvest_dir)
        patterns = ("*.md", "*.txt", "*.markdown")
        files: List[Path] = []
        for pat in patterns:
            files.extend(sorted(harvest_dir.rglob(pat)))
        for fp in files:
            # Skip the placeholder keep-file.
            if fp.name == ".gitkeep":
                continue
            file_lines = _read_text_file(fp)
            for ln in file_lines:
                lines.append(ln)
                line_metadata.append({"source": str(fp)})
            logger.info("  • %s (%d lines)", fp, len(file_lines))
    else:
        logger.warning("⚠️  Harvest directory missing: %s", harvest_dir)

    if not lines:
        logger.info("↪️  Falling back to legacy map: %s", legacy_map)
        legacy_lines = load_map(legacy_map)
        lines.extend(legacy_lines)
        line_metadata.extend({"source": str(legacy_map)} for _ in legacy_lines)

    return lines, line_metadata


def _load_sentence_transformer():
    """Import sentence-transformers lazily, returning ``None`` on failure."""
    try:
        from sentence_transformers import SentenceTransformer  # type: ignore
    except ImportError as exc:
        logger.warning(
            "⚠️  sentence-transformers unavailable (%s). Using deterministic mock embeddings.",
            exc,
        )
        return None
    try:
        return SentenceTransformer(EMBED_MODEL_NAME)
    except Exception as exc:
        logger.error("❌ Failed to load model %s: %s", EMBED_MODEL_NAME, exc)
        return None


def _mock_embeddings(lines: Sequence[str]):
    """Deterministic hash-based embeddings used when the real stack is missing."""
    try:
        import numpy as np  # type: ignore
    except ImportError:  # pragma: no cover - numpy missing entirely
        logger.error("❌ numpy not available; cannot build embeddings.")
        raise

    vectors = np.zeros((len(lines), MOCK_DIM), dtype="float32")
    for i, line in enumerate(lines):
        # Seed per-line so output is stable across runs.
        seed = abs(hash(line)) % (2**32)
        local = np.random.default_rng(seed=seed)
        vectors[i] = local.standard_normal(MOCK_DIM).astype("float32")
    return vectors


def generate_embeddings(lines: Sequence[str]):
    """Generate embeddings for ``lines`` using the real model or a safe fallback."""
    try:
        import numpy as np  # type: ignore
    except ImportError as exc:
        logger.error("❌ numpy unavailable (%s); cannot generate embeddings.", exc)
        raise RuntimeError("numpy is required for embedding generation") from exc

    model = _load_sentence_transformer()
    if model is None:
        return _mock_embeddings(lines), True

    try:
        vectors = model.encode(
            list(lines), convert_to_numpy=True, show_progress_bar=True
        )
        return np.asarray(vectors, dtype="float32"), False
    except Exception as exc:
        logger.error("❌ Embedding generation failed (%s). Falling back to mock.", exc)
        return _mock_embeddings(lines), True


def _build_index(embeddings):
    """Build a FAISS index when available, else return ``None``."""
    try:
        import faiss  # type: ignore
    except Exception as exc:
        logger.warning("⚠️  faiss not available (%s). Skipping index build.", exc)
        return None
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    return index


def run_ingest(
    harvest_dir: Path = DEFAULT_HARVEST_DIR,
    legacy_map: Path = DEFAULT_LEGACY_MAP,
    rag_store: Path = DEFAULT_RAG_STORE,
) -> dict:
    """Execute the full ingestion pipeline and return a summary dict."""
    logger.info("🧠 RAG Ingestion Engine — harvest=%s store=%s", harvest_dir, rag_store)

    lines, line_metadata = load_harvest_corpus(harvest_dir, legacy_map)
    if not lines:
        logger.warning("⚠️  No data to ingest. Exiting gracefully.")
        return {
            "status": "no_data",
            "total_lines": 0,
            "harvest_dir": str(harvest_dir),
        }

    logger.info("✅ Loaded %d lines", len(lines))

    try:
        embeddings, used_mock = generate_embeddings(lines)
    except RuntimeError as exc:
        logger.warning("⚠️  Embedding stage skipped: %s", exc)
        return {
            "status": "deps_missing",
            "total_lines": len(lines),
            "harvest_dir": str(harvest_dir),
            "error": str(exc),
        }
    logger.info(
        "✅ Generated %d embeddings (dim=%d, mock=%s)",
        embeddings.shape[0],
        embeddings.shape[1],
        used_mock,
    )

    rag_store = Path(rag_store)
    rag_store.mkdir(parents=True, exist_ok=True)

    try:
        import numpy as np  # type: ignore

        np.save(rag_store / "vectors.npy", embeddings)
        logger.info("✅ Saved vectors.npy")
    except Exception as exc:
        logger.error("❌ Could not persist vectors: %s", exc)

    with (rag_store / "lines.json").open("w", encoding="utf-8") as f:
        json.dump(lines, f, indent=2)
    logger.info("✅ Saved lines.json")

    with (rag_store / "sources.json").open("w", encoding="utf-8") as f:
        json.dump(line_metadata, f, indent=2)
    logger.info("✅ Saved sources.json")

    index = _build_index(embeddings)
    index_vectors = 0
    if index is not None:
        try:
            import faiss  # type: ignore

            faiss.write_index(index, str(rag_store / "index.faiss"))
            index_vectors = int(index.ntotal)
            logger.info("✅ Saved index.faiss (%d vectors)", index_vectors)
        except Exception as exc:
            logger.error("❌ Could not persist FAISS index: %s", exc)

    metadata = {
        "total_lines": len(lines),
        "embedding_dimension": int(embeddings.shape[1]),
        "model": EMBED_MODEL_NAME if not used_mock else f"mock::{MOCK_DIM}",
        "used_mock_embeddings": used_mock,
        "harvest_dir": str(harvest_dir),
        "legacy_map": str(legacy_map),
        "index_vectors": index_vectors,
        "generated": datetime.now(timezone.utc).isoformat(),
    }
    with (rag_store / "metadata.json").open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    logger.info("✅ Saved metadata.json")

    logger.info("🔮 RAG ingestion complete — %d vectors stored.", index_vectors or len(lines))
    metadata["status"] = "ok"
    return metadata


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--harvest-dir",
        default=str(DEFAULT_HARVEST_DIR),
        help="Directory containing master harvest markdown archives.",
    )
    parser.add_argument(
        "--legacy-map",
        default=str(DEFAULT_LEGACY_MAP),
        help="Fallback master_intelligence_map.txt path.",
    )
    parser.add_argument(
        "--rag-store",
        default=str(DEFAULT_RAG_STORE),
        help="Destination directory for vectors/index/metadata.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        summary = run_ingest(
            harvest_dir=Path(args.harvest_dir),
            legacy_map=Path(args.legacy_map),
            rag_store=Path(args.rag_store),
        )
    except Exception as exc:  # pragma: no cover - catch-all for uptime guarantee
        logger.exception("💥 RAG ingestion failed: %s", exc)
        return 1
    return 0 if summary.get("status") in {"ok", "no_data", "deps_missing"} else 2


if __name__ == "__main__":
    sys.exit(main())
