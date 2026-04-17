#!/usr/bin/env python3
"""
🌐 UNIVERSAL RAG — Cultural & Creative Content Ingestion (v22.2124)

Extends the Washed Harvest to include cultural assets:
  • Music lyrics (DJ Goanna Anthems)
  • Narrative stories (e.g. "The Blink Wanderer")
  • Substrate mapping data

The ``SovereignFilter`` (excluding Bible, Ark, Bottles) is applied to
**all** inputs including the 321GB substrate mapping data.

Usage:
    from ingestion.universal_rag import UniversalRAG

    rag = UniversalRAG()
    rag.ingest_lyric("Goanna Rising", "We rise through the ancient dust...")
    rag.ingest_story("The Blink Wanderer", "In the folds of time she walked...")
    result = rag.flush_to_spaces()
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from ingestion.rag_sync import RAGSync, SovereignFilter


# ---------------------------------------------------------------------------
# Content type constants
# ---------------------------------------------------------------------------

CONTENT_TYPE_LYRIC = "lyric"
CONTENT_TYPE_STORY = "story"
CONTENT_TYPE_SUBSTRATE = "substrate_mapping"


class UniversalRAG:
    """Cultural, creative, and substrate content ingestion pipeline.

    All content is passed through ``SovereignFilter`` before being
    pushed to HF Spaces.
    """

    def __init__(
        self,
        *,
        sovereign_filter: Optional[SovereignFilter] = None,
        rag_sync: Optional[RAGSync] = None,
        output_dir: Optional[Path] = None,
    ):
        self._filter = sovereign_filter or SovereignFilter()
        self._sync = rag_sync or RAGSync(sovereign_filter=self._filter)
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "universal_rag")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._pending: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Ingestion helpers
    # ------------------------------------------------------------------

    def ingest_lyric(
        self,
        title: str,
        content: str,
        *,
        artist: str = "DJ Goanna",
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Queue a lyric document for RAG ingestion.

        Parameters
        ----------
        title:   Song or track title.
        content: Lyric text.
        artist:  Performing artist (defaults to "DJ Goanna").
        tags:    Optional extra metadata tags.
        """
        item: Dict[str, Any] = {
            "content_type": CONTENT_TYPE_LYRIC,
            "title": title,
            "content": content,
            "artist": artist,
            "categories": ["creative", "music"] + (tags or []),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pending.append(item)
        return item

    def ingest_story(
        self,
        title: str,
        content: str,
        *,
        author: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Queue a narrative story document for RAG ingestion.

        Parameters
        ----------
        title:   Story title.
        content: Story text.
        author:  Optional author name.
        tags:    Optional extra metadata tags.
        """
        item: Dict[str, Any] = {
            "content_type": CONTENT_TYPE_STORY,
            "title": title,
            "content": content,
            "author": author,
            "categories": ["creative", "narrative"] + (tags or []),
            "ingested_at": datetime.now(timezone.utc).isoformat(),
        }
        self._pending.append(item)
        return item

    def ingest_substrate_data(
        self,
        packets: List[Dict[str, Any]],
        *,
        source: str = "321GB Substrate",
    ) -> List[Dict[str, Any]]:
        """Queue 321GB Substrate mapping packets for RAG ingestion.

        The SovereignFilter is applied during ``flush_to_spaces``; this
        method simply wraps each packet with content-type metadata.

        Parameters
        ----------
        packets: List of data-packet dicts (e.g. from ``Substrate321.get_manifest()``).
        source:  Label identifying the upstream data source.
        """
        items: List[Dict[str, Any]] = []
        for packet in packets:
            item: Dict[str, Any] = {
                "content_type": CONTENT_TYPE_SUBSTRATE,
                "source": source,
                "categories": ["substrate", "mapping"],
                **packet,
                "ingested_at": datetime.now(timezone.utc).isoformat(),
            }
            items.append(item)
        self._pending.extend(items)
        return items

    # ------------------------------------------------------------------
    # Flush (scrub + sync)
    # ------------------------------------------------------------------

    def flush_to_spaces(self, *, space: str = "Mapping-and-Inventory-storage") -> Dict[str, Any]:
        """Apply the SovereignFilter and push all pending items to HF Spaces.

        Clears the pending queue on success.

        Returns a summary with raw count, filtered count, and the sync result.
        """
        raw_count = len(self._pending)
        clean = self._sync.scrub_ingestion(self._pending)
        result = self._sync.sync_to_spaces(clean, space=space)
        self._pending.clear()

        return {
            "raw_items": raw_count,
            "filtered_items": raw_count - len(clean),
            "pushed_items": len(clean),
            "sync_result": result,
            "flushed_at": datetime.now(timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # Pending queue inspection
    # ------------------------------------------------------------------

    def pending_items(self) -> List[Dict[str, Any]]:
        """Return a copy of the items queued for the next flush."""
        return list(self._pending)

    def pending_count(self) -> int:
        """Return the number of items currently in the pending queue."""
        return len(self._pending)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        """Return a summary of the Universal RAG state."""
        type_counts: Dict[str, int] = {}
        for item in self._pending:
            ct = item.get("content_type", "unknown")
            type_counts[ct] = type_counts.get(ct, 0) + 1

        return {
            "pending_count": self.pending_count(),
            "pending_by_type": type_counts,
            "excluded_categories": sorted(self._filter.excluded_categories),
            "total_syncs": len(self._sync.sync_log()),
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    rag = UniversalRAG()

    rag.ingest_lyric(
        "Goanna Rising",
        "We rise through the ancient dust, the land remembers who we are...",
    )
    rag.ingest_story(
        "The Blink Wanderer",
        "In the folds of time she walked, leaving footprints only the stars could read...",
    )

    print("🌐 UNIVERSAL RAG — Status (before flush)")
    print(json.dumps(rag.status(), indent=2))

    result = rag.flush_to_spaces()
    print(f"\n📡 Flush: {result['pushed_items']} items pushed to HF Spaces")
    print(f"   Filtered: {result['filtered_items']}")


if __name__ == "__main__":
    main()
