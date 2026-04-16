#!/usr/bin/env python3
"""
🛰️ RAG SYNC — Washed Harvest Bridge (v22.2122)

Wires the Hugging Face Spaces RAG into the Citadel inventory.
Applies the SovereignFilter to scrub ingestion and pushes mapping
data to the Ghost Fleet for decentralised recall.

Usage:
    from ingestion.rag_sync import RAGSync

    syncer = RAGSync()
    clean  = syncer.scrub_ingestion(raw_data)
    result = syncer.sync_to_spaces(clean)
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


# ---------------------------------------------------------------------------
# Sovereign filter configuration
# ---------------------------------------------------------------------------

# Categories excluded by default via the SovereignFilter.
DEFAULT_EXCLUDED_CATEGORIES: Set[str] = frozenset({"bible", "ark", "bottles"})

# Hugging Face organisation (double-n)
HF_ORG = "DJ-Goanna-Coding"
HF_SPACE_URL_TEMPLATE = f"https://huggingface.co/spaces/{HF_ORG}/{{space}}"


class SovereignFilter:
    """Content filter that excludes specified categories from ingestion.

    The default exclusion set (Bible, Ark, Bottles) can be extended or
    overridden at construction time.
    """

    def __init__(self, *, excluded: Optional[Set[str]] = None):
        self._excluded: Set[str] = set(excluded) if excluded is not None else set(DEFAULT_EXCLUDED_CATEGORIES)

    @property
    def excluded_categories(self) -> Set[str]:
        return set(self._excluded)

    def is_allowed(self, item: Dict[str, Any]) -> bool:
        """Return ``True`` when *item* is **not** in an excluded category."""
        cats = item.get("categories", [])
        if isinstance(cats, str):
            cats = [cats]
        return not any(c.lower() in self._excluded for c in cats)

    def apply(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return only the items that pass the filter."""
        return [i for i in items if self.is_allowed(i)]


class RAGSync:
    """Bridge between the Citadel inventory and HF Spaces RAG.

    ``scrub_ingestion`` applies the SovereignFilter, and
    ``sync_to_spaces`` pushes clean data to the Ghost Fleet.
    """

    def __init__(self, *, output_dir: Optional[Path] = None,
                 sovereign_filter: Optional[SovereignFilter] = None):
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "rag_sync")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._filter = sovereign_filter or SovereignFilter()
        self._sync_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Scrub ingestion
    # ------------------------------------------------------------------

    def scrub_ingestion(self, raw_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply the SovereignFilter to *raw_data*.

        Returns the scrubbed (allowed) items.
        """
        return self._filter.apply(raw_data)

    # ------------------------------------------------------------------
    # Sync to HF Spaces
    # ------------------------------------------------------------------

    def sync_to_spaces(self, clean_data: List[Dict[str, Any]], *,
                       space: str = "Mapping-and-Inventory-storage") -> Dict[str, Any]:
        """Push *clean_data* to the Ghost Fleet for decentralised recall.

        In the current implementation this persists the payload locally
        and records the target HF Space URL.  The actual push is
        performed by the GitHub Actions Pulse Sync workflow or the HF
        startup script.
        """
        target_url = HF_SPACE_URL_TEMPLATE.format(space=space)

        payload_path = self.output_dir / f"rag_payload_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        payload_path.write_text(json.dumps(clean_data, indent=2))

        result = {
            "target_space": space,
            "target_url": target_url,
            "items_pushed": len(clean_data),
            "payload_path": str(payload_path),
            "synced_at": datetime.now(timezone.utc).isoformat(),
        }

        self._sync_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @property
    def filter(self) -> SovereignFilter:
        """Access the underlying SovereignFilter."""
        return self._filter

    def sync_log(self) -> List[Dict[str, Any]]:
        """Return the log of all sync operations."""
        return list(self._sync_log)

    def status(self) -> Dict[str, Any]:
        """Return a summary of the RAG sync state."""
        return {
            "excluded_categories": sorted(self._filter.excluded_categories),
            "total_syncs": len(self._sync_log),
            "hf_org": HF_ORG,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    syncer = RAGSync()

    sample = [
        {"name": "genesis_vault.dat", "categories": ["sovereign", "lineage"]},
        {"name": "old_scrolls.dat", "categories": ["bible"]},
        {"name": "spectrum_map.json", "categories": ["research"]},
        {"name": "ark_backup.tar", "categories": ["ark"]},
        {"name": "frequency_log.csv", "categories": ["diagnostics"]},
    ]

    print("🛰️ RAG SYNC — Scrub Ingestion Demo")
    clean = syncer.scrub_ingestion(sample)
    print(f"   Raw items: {len(sample)}")
    print(f"   Clean items: {len(clean)}")
    print(f"   Excluded: {[i['name'] for i in sample if i not in clean]}")

    result = syncer.sync_to_spaces(clean)
    print(f"\n📡 Synced {result['items_pushed']} items → {result['target_url']}")
    print(json.dumps(syncer.status(), indent=2))


if __name__ == "__main__":
    main()
