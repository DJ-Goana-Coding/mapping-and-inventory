#!/usr/bin/env python3
"""
🗂️ THE GDRIVE BRIDGE — ingest the "Citadel Archives" folder.

A thin bridge over Google Drive that walks the Citadel Archives folder
and maps every document into the Universal-RAG vector store.  All I/O
goes through a pluggable ``lister`` callable so the connector runs
identically against a live Drive API or an offline fixture.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

from ingestion.universal_rag import UniversalRAG


CITADEL_ARCHIVES_FOLDER = "Citadel Archives"

Lister = Callable[[str], Iterable[Dict[str, Any]]]
"""Signature: ``lister(folder_name) -> iterable of {"name", "mime_type", "content", ...}``."""


def _local_folder_lister(folder_name: str) -> Iterable[Dict[str, Any]]:
    """Default lister that mirrors a local directory named *folder_name*.

    Useful for offline mode / CI: point the bridge at a local folder
    containing the archives and it behaves like a Drive connector.
    """
    base = Path(folder_name)
    if not base.exists() or not base.is_dir():
        return []
    items: List[Dict[str, Any]] = []
    for path in sorted(base.rglob("*")):
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            content = ""
        items.append(
            {
                "name": str(path.relative_to(base)),
                "mime_type": "text/plain",
                "content": content,
                "size": path.stat().st_size,
            }
        )
    return items


class GDriveBridge:
    """Ingest every file under the Citadel Archives into the vector store."""

    def __init__(
        self,
        *,
        folder: str = CITADEL_ARCHIVES_FOLDER,
        lister: Optional[Lister] = None,
        universal_rag: Optional[UniversalRAG] = None,
    ) -> None:
        self.folder = folder
        self._lister: Lister = lister or _local_folder_lister
        self.universal_rag = universal_rag or UniversalRAG()
        self._last_ingest: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------

    def ingest_archives(self) -> List[Dict[str, Any]]:
        """Walk the archives folder and queue each document for RAG sync.

        Returns the list of queued RAG items.
        """
        queued: List[Dict[str, Any]] = []
        for item in self._lister(self.folder):
            name = str(item.get("name") or "").strip()
            if not name:
                continue
            content = item.get("content")
            if content is None:
                # Fall back to a metadata-only stub so the document is
                # still indexable even when the body is inaccessible.
                content = f"[GDrive document: {name}]"
            rag_item = self.universal_rag.ingest_story(
                title=name,
                content=str(content),
                author="Citadel Archives (GDrive)",
                tags=[
                    "gdrive",
                    "citadel-archives",
                    str(item.get("mime_type") or "unknown"),
                ],
            )
            queued.append(rag_item)
        self._last_ingest = queued
        return queued

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def last_ingest(self) -> List[Dict[str, Any]]:
        return list(self._last_ingest)

    def status(self) -> Dict[str, Any]:
        return {
            "folder": self.folder,
            "last_ingested_count": len(self._last_ingest),
            "bridge_ready": self._lister is not None,
            "last_run_at": datetime.now(timezone.utc).isoformat(),
        }
