#!/usr/bin/env python3
"""
🧠 T.I.A. SYNAPSE — Query Engine for Archive_Vault, Districts and Forever_Learning.

Builds a simple in-memory keyword index over every document in
``Archive_Vault/``, ``Districts/`` and ``Forever_Learning/``.  New
documents added by the crawler / GDrive bridge / physical harvest are
registered through :meth:`TiaSynapse.on_new_data`, keeping the index
live (the "Forever_Learning updates the index in real-time" requirement).
"""

from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_SOURCE_DIRS: Tuple[Path, ...] = (
    REPO_ROOT / "Archive_Vault",
    REPO_ROOT / "Districts",
    REPO_ROOT / "Forever_Learning",
)

# Extensions we pull text out of for the index.  Everything else is
# indexed by filename metadata only.
TEXT_EXTENSIONS = {".md", ".txt", ".json", ".yml", ".yaml", ".py", ".rst", ".ini"}

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]{2,}")


def _tokenise(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class TiaSynapse:
    """Live keyword-ranked query engine for the Citadel's data floors."""

    def __init__(
        self,
        *,
        source_dirs: Optional[Iterable[Path]] = None,
        max_bytes_per_file: int = 200_000,
    ) -> None:
        self.source_dirs: List[Path] = [
            Path(p) for p in (source_dirs if source_dirs is not None else DEFAULT_SOURCE_DIRS)
        ]
        self.max_bytes_per_file = max_bytes_per_file

        # doc_id -> {source, path, tokens (Counter), length, added_at}
        self._documents: Dict[str, Dict[str, Any]] = {}
        # token -> set of doc_ids
        self._postings: Dict[str, set] = defaultdict(set)

    # ------------------------------------------------------------------
    # Indexing
    # ------------------------------------------------------------------

    def index(self) -> Dict[str, Any]:
        """Walk every configured source directory and (re)build the index."""
        self._documents.clear()
        self._postings.clear()

        for base in self.source_dirs:
            if not base.exists():
                continue
            for path in base.rglob("*"):
                if not path.is_file():
                    continue
                self._index_file(base, path)
        return self.status()

    def _index_file(self, base: Path, path: Path) -> None:
        try:
            if path.suffix.lower() in TEXT_EXTENSIONS and path.stat().st_size <= self.max_bytes_per_file:
                text = path.read_text(encoding="utf-8", errors="replace")
            else:
                text = path.name
        except OSError:
            text = path.name

        doc_id = f"{base.name}:{path.relative_to(base).as_posix()}"
        self._register_document(
            doc_id=doc_id,
            source=base.name,
            path=str(path),
            text=text,
        )

    # ------------------------------------------------------------------
    # Live updates — called from Forever_Learning / crawler / bridge.
    # ------------------------------------------------------------------

    def on_new_data(
        self,
        doc_id: str,
        text: str,
        *,
        source: str = "forever_learning",
        path: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Register (or replace) a document in the live index."""
        return self._register_document(
            doc_id=doc_id,
            source=source,
            path=path or doc_id,
            text=text,
        )

    def _register_document(
        self,
        *,
        doc_id: str,
        source: str,
        path: str,
        text: str,
    ) -> Dict[str, Any]:
        # Remove old postings if this is a re-registration.
        existing = self._documents.get(doc_id)
        if existing is not None:
            for token in existing["tokens"]:
                self._postings[token].discard(doc_id)

        tokens = Counter(_tokenise(text))
        record = {
            "source": source,
            "path": path,
            "tokens": tokens,
            "length": sum(tokens.values()),
            "added_at": datetime.now(timezone.utc).isoformat(),
        }
        self._documents[doc_id] = record
        for token in tokens:
            self._postings[token].add(doc_id)
        return {"doc_id": doc_id, **{k: v for k, v in record.items() if k != "tokens"}}

    # ------------------------------------------------------------------
    # Query
    # ------------------------------------------------------------------

    def query(self, text: str, *, top_k: int = 10) -> List[Dict[str, Any]]:
        """Return the top-*k* documents ranked by shared-token frequency."""
        q_tokens = _tokenise(text)
        if not q_tokens:
            return []

        scores: Counter = Counter()
        for token in q_tokens:
            for doc_id in self._postings.get(token, ()):
                scores[doc_id] += self._documents[doc_id]["tokens"][token]

        results: List[Dict[str, Any]] = []
        for doc_id, score in scores.most_common(top_k):
            doc = self._documents[doc_id]
            results.append(
                {
                    "doc_id": doc_id,
                    "source": doc["source"],
                    "path": doc["path"],
                    "score": score,
                }
            )
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def document_count(self) -> int:
        return len(self._documents)

    def sources(self) -> List[str]:
        return sorted({d["source"] for d in self._documents.values()})

    def status(self) -> Dict[str, Any]:
        return {
            "document_count": self.document_count(),
            "token_count": len(self._postings),
            "sources": self.sources(),
            "configured_dirs": [str(p) for p in self.source_dirs],
        }

    def to_json(self) -> str:  # pragma: no cover - convenience
        return json.dumps(self.status(), indent=2)
