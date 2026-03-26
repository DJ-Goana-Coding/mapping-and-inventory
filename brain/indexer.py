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

# ---------------------------------------------------------------------------
# Origin Isolation — system-origin tag map
# ---------------------------------------------------------------------------
# Maps path fragments / directory names to sovereign system IDs.
# The order matters: more-specific patterns should appear first.
_SYSTEM_ORIGIN_MAP: list[tuple[str, str]] = [
    ("pioneer-trader", "pioneer-trader"),
    ("Pioneer_Vortex", "Pioneer_Vortex"),
    ("CITADEL_OMEGA", "CITADEL_OMEGA"),
    ("citadel-vortex", "citadel-vortex"),
    ("perimeter-scout", "perimeter-scout"),
    ("S10_Phalanx", "S10_Phalanx"),
    ("Oppo_Omega", "Oppo_Omega"),
    ("CGAL_Core", "CGAL_Core"),
    ("Genesis", "Genesis"),
    ("Harvestmoon", "Harvestmoon"),
    ("fleet_registry/pioneer", "pioneer-trader"),
    ("fleet_registry/Pioneer_Vortex", "Pioneer_Vortex"),
    ("fleet_registry/CITADEL", "CITADEL_OMEGA"),
    ("fleet_registry/citadel-vortex", "citadel-vortex"),
    ("fleet_registry/perimeter", "perimeter-scout"),
    ("fleet_registry/S10_Phalanx", "S10_Phalanx"),
    ("fleet_registry/Oppo_Omega", "Oppo_Omega"),
    ("fleet_registry/CGAL", "CGAL_Core"),
    ("fleet_registry/Genesis", "Genesis"),
    ("fleet_registry/Harvestmoon", "Harvestmoon"),
    ("nodes/S10_Phalanx", "S10_Phalanx"),
    ("nodes/Oppo_Omega", "Oppo_Omega"),
]

# ---------------------------------------------------------------------------
# 12 Dimensional Districts — district tag map
# ---------------------------------------------------------------------------
# Maps directory-name fragments (as they appear in Drive / filesystem paths)
# to their canonical district IDs.  When a file's path contains one of these
# fragments its metadata receives a ``district`` field.
_DISTRICT_MAP: dict[str, str] = {
    "01": "01_GENESIS_CORE",
    "02": "02_INTELLIGENCE_LAYER",
    "03": "03_COMMAND_CONTROL",
    "04": "04_OUTPUT_HARVEST",
    "05": "05_MARKET_SIGNALS",
    "06": "06_MEMORY_ARCHIVE",
    "07": "07_TRADER",
    "08": "08_SECURITY_PERIMETER",
    "09": "09_LEGAL_CLEARANCE",
    "10": "10_RESOURCE_ALLOCATION",
    "11": "11_SWARM_INTELLIGENCE",
    "12": "12_ORACLE_ETHICS",
}

# Keywords used for CGAL / Legal Stack cross-linking.
# Any file referencing these strings is tagged with a link to CGAL_Core,
# regardless of which system the file originates from.
_LEGAL_COMPLIANCE_KEYWORDS: tuple[str, ...] = ("CGAL", "1986 Legal Stack")

# Filename patterns that identify a system's "Bible" (core logic).
# Records matching these patterns receive ``is_bible: "true"`` in metadata
# so the Self-Healing Protocol can locate and export them during a reboot.
_BIBLE_PATTERNS: tuple[str, ...] = (
    "bible",
    "BIBLE",
    "core_logic",
    "CORE_LOGIC",
    "TOTALITY",
    "KNOWLEDGE_GRAPH",
    "manifest",
    "MANIFEST",
)

# Ghost-manifest filenames targeted by Task 2 (Ghost-Memory Infiltration).
# These are indexed regardless of .gitignore rules because they are addressed
# by explicit path, not by directory walk.
_GHOST_MANIFEST_NAMES: tuple[str, ...] = ("TOTALITY.json", "KNOWLEDGE_GRAPH.json")

# Glob pattern used to discover ghost_deep_scan sidecar files.
_GHOST_SCAN_PATTERN: str = "*ghost_deep_scan*"

# Keywords used to detect cross-spoke API references inside S10_Phalanx code.
# When found, the chunk is tagged with the linked spoke IDs in metadata.
_S10_SPOKE_KEYWORDS: dict[str, str] = {
    "CGAL": "CGAL_Core",
    "Omega": "Oppo_Omega",
}

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


def _detect_s10_spoke_links(text: str) -> list[str]:
    """
    Scan *text* for cross-spoke API references (CGAL, Omega).

    Returns a sorted list of spoke IDs that are referenced in the text,
    e.g. ``["CGAL_Core", "Omega"]``.  Used to populate the
    ``linked_spokes`` metadata field for S10_Phalanx records.
    """
    linked: list[str] = []
    for keyword, spoke_id in _S10_SPOKE_KEYWORDS.items():
        if keyword in text and spoke_id not in linked:
            linked.append(spoke_id)
    return sorted(linked)


def _detect_system_origin(source: str) -> str | None:
    """
    Return the sovereign system ID for *source* using :data:`_SYSTEM_ORIGIN_MAP`.

    Scans the source string for known path fragments and returns the first
    match.  Returns ``None`` when the source cannot be attributed to any
    known system (e.g. hub-level files).
    """
    for fragment, system_id in _SYSTEM_ORIGIN_MAP:
        if fragment in source:
            return system_id
    return None


def _detect_district(source: str) -> str | None:
    """
    Return the district ID for *source* based on :data:`_DISTRICT_MAP`.

    Scans the path parts for a segment whose name starts with a two-digit
    district prefix (``"01"``–``"12"``).  Returns the canonical district ID
    when found, or ``None`` for hub-level / unclassified files.
    """
    for part in pathlib.Path(source).parts:
        for prefix, district_id in _DISTRICT_MAP.items():
            if part.startswith(prefix + "_") or part == prefix:
                return district_id
    return None


def _detect_cgal_link(text: str) -> bool:
    """
    Return *True* if *text* references CGAL or the 1986 Legal Stack.

    When *True* the caller should attach a ``cgal_link: "CGAL_Core"``
    metadata field to signal a cross-node legal dependency.

    Uses word-boundary–aware matching to avoid false positives from
    partial word matches (e.g. ``"MYCGALTEST"`` would not match).
    """
    import re

    for kw in _LEGAL_COMPLIANCE_KEYWORDS:
        # Build a word-boundary pattern: \b works on alphanumeric edges;
        # for keywords containing spaces (e.g. "1986 Legal Stack") we
        # anchor on non-alphanumeric boundaries at start/end of the phrase.
        pattern = r"(?<![A-Za-z0-9])" + re.escape(kw) + r"(?![A-Za-z0-9])"
        if re.search(pattern, text):
            return True
    return False


def _is_bible_file(filepath: pathlib.Path) -> bool:
    """
    Return *True* when *filepath* matches a known Bible / core-logic pattern.

    The Self-Healing Protocol uses this flag to locate the authoritative
    memory context for each system so the Hub can export and reboot it if
    the originating node goes offline or corrupts.
    """
    name_lower = filepath.stem.lower()
    for pattern in _BIBLE_PATTERNS:
        if pattern.lower() in name_lower:
            return True
    return False


def export_system_bible(
    collection: chromadb.Collection,
    system_id: str,
) -> list[dict[str, Any]]:
    """
    Self-Healing Protocol — export the isolated memory context for *system_id*.

    Queries the vault for all records tagged with ``system_origin=system_id``
    and ``is_bible="true"``.  Returns a list of metadata dicts that can be
    serialised and used to reboot the target system from a known-good state.

    Parameters
    ----------
    collection:
        The open ChromaDB collection to query.
    system_id:
        Sovereign system identifier (e.g. ``"pioneer-trader"``).
    """
    results = collection.get(
        where={"$and": [{"system_origin": system_id}, {"is_bible": "true"}]},
        include=["metadatas", "documents"],
    )
    records: list[dict[str, Any]] = []
    ids = results.get("ids", [])
    docs = results.get("documents") or []
    metas = results.get("metadatas") or []
    for doc_id, doc, meta in zip(ids, docs, metas):
        records.append({"id": doc_id, "document": doc, "metadata": meta})
    logger.info(
        "Self-Healing: exported %d Bible records for system '%s'.",
        len(records),
        system_id,
    )
    return records


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

    # Determine whether this file belongs to the S10_Phalanx node so that
    # cross-spoke link detection can be applied to every chunk.
    is_s10 = "S10_Phalanx" in rel_path

    # Origin Isolation — detect which sovereign system owns this file.
    system_origin = _detect_system_origin(rel_path)

    # District tagging — detect which of the 12 Dimensional Districts this file belongs to.
    district = _detect_district(rel_path)

    # Self-Healing Protocol — flag Bible / core-logic files for reboot export.
    is_bible = _is_bible_file(filepath)

    ids, documents, metadatas = [], [], []
    for idx, chunk in enumerate(chunks):
        doc_id = _doc_id(chunk, f"{rel_path}::chunk{idx}")
        ids.append(doc_id)
        documents.append(chunk)
        meta: dict[str, Any] = {
            "source": rel_path,
            "chunk_index": idx,
            "freq_signature": FREQ_SIGNATURE,
            "file_type": filepath.suffix.lstrip("."),
        }
        # Origin Isolation tag — ensures RAG metadata carries the native system ID.
        if system_origin:
            meta["system_origin"] = system_origin
        # District tag — identifies which of the 12 Dimensional Districts owns this record.
        if district:
            meta["district"] = district
        # Self-Healing flag — marks Bible/core-logic records for reboot export.
        if is_bible:
            meta["is_bible"] = "true"
        if is_s10:
            linked = _detect_s10_spoke_links(chunk)
            if linked:
                meta["linked_spokes"] = ",".join(linked)
                logger.debug(
                    "S10 cross-spoke links detected in %s chunk %d: %s",
                    filepath,
                    idx,
                    linked,
                )
        # CGAL / 1986 Legal Stack cross-link — applies to every file, not just S10.
        if _detect_cgal_link(chunk):
            meta["cgal_link"] = "CGAL_Core"
            logger.debug("CGAL cross-link detected in %s chunk %d.", filepath, idx)
        metadatas.append(meta)

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
    When *source* contains a known system path fragment the record is
    automatically tagged with ``system_origin`` (Origin Isolation).
    """
    # Origin Isolation — derive system_origin from the source label if possible.
    system_origin = _detect_system_origin(source)

    # District tagging — detect district from the source label.
    district = _detect_district(source)

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
        # Attach origin tag when the source can be attributed to a known system.
        if system_origin:
            meta["system_origin"] = system_origin
        # District tag — identifies which of the 12 Dimensional Districts owns this record.
        if district:
            meta["district"] = district
        # CGAL / 1986 Legal Stack cross-link — applies to all ingested content.
        if _detect_cgal_link(chunk):
            meta["cgal_link"] = "CGAL_Core"
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


def index_ghost_manifests(
    collection: chromadb.Collection,
    root: str | pathlib.Path | None = None,
) -> int:
    """
    Task 2 — Ghost-Memory Infiltration.

    Force-index the Oppo/S10 node manifests (``TOTALITY.json``,
    ``KNOWLEDGE_GRAPH.json``) and any file matching ``*ghost_deep_scan*``
    found under *root*.  Files are addressed by explicit path so they are
    ingested regardless of any ``.gitignore`` or ``skip_dirs`` constraints
    that would normally exclude them.

    Every record is signed with :data:`FREQ_SIGNATURE` (the
    ``69-333-222-92-93-999-777-88-29-369`` sequence).

    Returns the total number of chunks committed to the vault.
    """
    search_root = pathlib.Path(root) if root else pathlib.Path(__file__).parent.parent
    total = 0

    # 1. Named ghost manifests
    for name in _GHOST_MANIFEST_NAMES:
        candidate = search_root / name
        if candidate.exists():
            total += index_json_manifest(
                collection,
                candidate,
                source_label=f"ghost_manifest::{name}",
            )
            logger.info("Ghost-Memory: indexed manifest '%s'.", name)
        else:
            logger.debug("Ghost-Memory: manifest '%s' not found at '%s'.", name, candidate)

    # 2. Files matching *ghost_deep_scan* anywhere under the root
    for ghost_file in search_root.rglob(_GHOST_SCAN_PATTERN):
        if not ghost_file.is_file():
            continue
        if ghost_file.suffix in _CODE_EXTENSIONS:
            total += index_file(collection, ghost_file)
        else:
            # Unknown extension — ingest raw text best-effort
            try:
                text = ghost_file.read_text(encoding="utf-8", errors="replace")
                total += index_text(
                    collection,
                    text,
                    source=f"ghost_deep_scan::{ghost_file}",
                    extra_metadata={"file_type": ghost_file.suffix.lstrip(".") or "unknown"},
                )
            except OSError as exc:
                logger.warning("Ghost-Memory: could not read '%s': %s", ghost_file, exc)
        logger.info("Ghost-Memory: indexed ghost_deep_scan file '%s'.", ghost_file)

    logger.info("Ghost-Memory infiltration complete — %d chunks committed.", total)
    return total


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    repo_root = pathlib.Path(__file__).parent.parent
    col = get_collection()
    total = index_directory(col, repo_root)
    print(f"✅ Brain initialised — {total} chunks indexed into memory_vault/")
