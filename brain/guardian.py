"""
Anti-Overwrite Guardian Protocol
=================================
Before any file-write or code-generation the agent calls
``Guardian.check(proposed_content)``.

If the proposed content is semantically similar (>= *threshold*, default 85 %)
to **any** document already in the brain vault the guardian issues a
**Hard Veto** — raising ``GuardianVetoError`` — so the existing scaffolding
is never silently overwritten.

Blocked overwrite attempts are appended to ``SECURITY_ALERTS.log`` in the
repository root so the Commander can audit all veto events.
"""
from __future__ import annotations

import datetime
import logging
import os
import pathlib
from dataclasses import dataclass, field
from typing import Any

from brain.indexer import get_collection, query as vault_query

logger = logging.getLogger(__name__)

# Path for the security audit log (relative to the repo root)
_REPO_ROOT = pathlib.Path(__file__).parent.parent
SECURITY_ALERTS_LOG: pathlib.Path = _REPO_ROOT / "SECURITY_ALERTS.log"


def _append_security_alert(similarity: float, matching_source: str, proposed_snippet: str) -> None:
    """Append a single blocked-write record to SECURITY_ALERTS.log."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = (
        f"[{timestamp}] GUARDIAN VETO | "
        f"similarity={similarity:.1%} | "
        f"matching_source={matching_source!r} | "
        f"snippet={proposed_snippet[:80]!r}\n"
    )
    try:
        with SECURITY_ALERTS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        logger.warning("Guardian: could not write SECURITY_ALERTS.log (%s).", exc)

# Default cosine-similarity threshold for issuing a veto (0 = identical, 1 = orthogonal
# in ChromaDB's cosine-distance representation where distance = 1 - similarity).
# A *distance* value below (1 - threshold) means similarity >= threshold.
DEFAULT_THRESHOLD: float = 0.85


class GuardianVetoError(RuntimeError):
    """
    Raised when proposed content is too similar to existing vault content.

    Attributes
    ----------
    similarity : float
        Cosine similarity score that triggered the veto (0–1 scale).
    matching_source : str
        Source identifier of the most similar existing document.
    """

    def __init__(self, similarity: float, matching_source: str, message: str = "") -> None:
        self.similarity = similarity
        self.matching_source = matching_source
        super().__init__(
            message
            or (
                f"Guardian Hard Veto — proposed content matches '{matching_source}' "
                f"with {similarity:.1%} similarity (threshold {DEFAULT_THRESHOLD:.0%}). "
                "Operation aborted to protect existing scaffolding."
            )
        )


@dataclass
class GuardianResult:
    """Outcome of a guardian check."""

    vetoed: bool
    similarity: float = 0.0
    matching_source: str = ""
    top_matches: list[dict[str, Any]] = field(default_factory=list)


class Guardian:
    """
    Semantic similarity gate for file-write and code-generation operations.

    Parameters
    ----------
    threshold:
        Fraction in [0, 1].  Operations whose best-match similarity reaches
        or exceeds this value are vetoed.  Defaults to ``DEFAULT_THRESHOLD``.
    n_results:
        Number of nearest-neighbour candidates retrieved from the vault per
        check.  A higher value gives a more exhaustive scan at the cost of
        latency.
    """

    def __init__(
        self,
        threshold: float = DEFAULT_THRESHOLD,
        n_results: int = 5,
    ) -> None:
        self.threshold = threshold
        self.n_results = n_results
        self._collection = get_collection()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check(self, proposed_content: str, *, raise_on_veto: bool = True) -> GuardianResult:
        """
        Perform a semantic similarity scan against the brain vault.

        Parameters
        ----------
        proposed_content:
            The text that is about to be written / generated.
        raise_on_veto:
            When *True* (default) a ``GuardianVetoError`` is raised
            automatically if the check is vetoed.  Set to *False* to
            receive a ``GuardianResult`` and decide yourself.

        Returns
        -------
        GuardianResult
            Contains the veto flag, best similarity score, and matching
            source reference.

        Raises
        ------
        GuardianVetoError
            If ``raise_on_veto=True`` and similarity >= threshold.
        """
        if not proposed_content.strip():
            logger.debug("Guardian: empty content — pass-through.")
            return GuardianResult(vetoed=False)

        try:
            raw = vault_query(self._collection, proposed_content, n_results=self.n_results)
        except Exception as exc:  # vault may be empty on first run
            logger.warning("Guardian: vault query failed (%s) — allowing write.", exc)
            return GuardianResult(vetoed=False)

        distances: list[float] = raw.get("distances", [[]])[0]
        metadatas: list[dict] = raw.get("metadatas", [[]])[0]
        documents: list[str] = raw.get("documents", [[]])[0]

        if not distances:
            return GuardianResult(vetoed=False)

        # ChromaDB returns cosine *distance* (0 = same, 2 = opposite for
        # non-normalised vectors; 0–1 when space="cosine").  Convert to similarity.
        best_distance = min(distances)
        best_similarity = max(0.0, 1.0 - best_distance)
        best_idx = distances.index(best_distance)
        best_source = (metadatas[best_idx] or {}).get("source", "unknown")

        top_matches = [
            {
                "source": (metadatas[i] or {}).get("source", "unknown"),
                "similarity": max(0.0, 1.0 - distances[i]),
                "snippet": documents[i][:120] if i < len(documents) else "",
            }
            for i in range(len(distances))
        ]

        logger.debug(
            "Guardian: best similarity=%.2f source=%s threshold=%.2f",
            best_similarity,
            best_source,
            self.threshold,
        )

        if best_similarity >= self.threshold:
            _append_security_alert(best_similarity, best_source, proposed_content)
            result = GuardianResult(
                vetoed=True,
                similarity=best_similarity,
                matching_source=best_source,
                top_matches=top_matches,
            )
            if raise_on_veto:
                raise GuardianVetoError(best_similarity, best_source)
            return result

        return GuardianResult(
            vetoed=False,
            similarity=best_similarity,
            matching_source=best_source,
            top_matches=top_matches,
        )

    def safe_write(self, filepath: str, content: str) -> None:
        """
        Write *content* to *filepath* only after a successful guardian check.

        Raises ``GuardianVetoError`` if the content is too similar to
        existing vault documents.
        """
        self.check(content, raise_on_veto=True)
        import pathlib

        path = pathlib.Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info("Guardian: write approved → %s", filepath)
