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
import re
from dataclasses import dataclass, field
from typing import Any

from brain.indexer import export_system_bible, get_collection, query as vault_query

logger = logging.getLogger(__name__)

# Path for the security audit log (relative to the repo root)
_REPO_ROOT = pathlib.Path(__file__).parent.parent
SECURITY_ALERTS_LOG: pathlib.Path = _REPO_ROOT / "SECURITY_ALERTS.log"

# ---------------------------------------------------------------------------
# 5-File Purification — protected core-logic filenames
# ---------------------------------------------------------------------------
# Writes targeting any of these filenames are unconditionally blocked to
# preserve the integrity of the sovereign execution environment.
_PURIFICATION_FILES: frozenset[str] = frozenset(
    {
        "brain.py",
        "logger.py",
        "bridge.py",
        "gatekeeper.py",
        "run_trader.py",
    }
)

# ---------------------------------------------------------------------------
# Ghost Protocol — credential / PII redaction patterns
# ---------------------------------------------------------------------------
# Applied before any cloud-mirroring event to strip raw API keys, ABNs, and
# common PII from outbound content.  Patterns are ordered by specificity.
_REDACTION_RULES: list[tuple[re.Pattern[str], str]] = [
    # Australian Business Number: XX XXX XXX XXX or XX-XXX-XXX-XXX
    (re.compile(r"\b\d{2}[\s\-]\d{3}[\s\-]\d{3}[\s\-]\d{3}\b"), "[REDACTED_ABN]"),
    # Generic API / secret key — long hex or base64-like token (≥40 chars).
    # 40-char threshold reduces false positives from long-but-non-sensitive
    # identifiers (e.g. file hashes, UUIDs) while still catching typical key
    # formats (HuggingFace: hf_..., GitHub: ghp_..., OpenAI: sk-...).
    (re.compile(r"\b[A-Za-z0-9_\-]{40,}\b"), "[REDACTED_TOKEN]"),
    # Email addresses
    (re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"), "[REDACTED_EMAIL]"),
    # Phone numbers (international and local Australian formats)
    (re.compile(r"\b(?:\+61|0)[2-9]\d{8}\b"), "[REDACTED_PHONE]"),
]


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


def _append_corruption_alert(system_id: str, matching_source: str, proposed_snippet: str) -> None:
    """Append a corruption-detection record to SECURITY_ALERTS.log."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = (
        f"[{timestamp}] CORRUPTION DETECTED | "
        f"system={system_id!r} | "
        f"matching_source={matching_source!r} | "
        f"snippet={proposed_snippet[:80]!r}\n"
    )
    try:
        with SECURITY_ALERTS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        logger.warning("Guardian: could not write SECURITY_ALERTS.log (%s).", exc)


def _append_purification_alert(filepath: str) -> None:
    """Append a 5-File Purification veto record to SECURITY_ALERTS.log."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    entry = (
        f"[{timestamp}] PURIFICATION VETO | "
        f"filepath={filepath!r} is a protected sovereign file — write blocked.\n"
    )
    try:
        with SECURITY_ALERTS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        logger.warning("Guardian: could not write SECURITY_ALERTS.log (%s).", exc)


def redact_credentials(text: str) -> str:
    """
    Ghost Protocol — redact API keys, ABN details, and PII from *text*.

    Applies the :data:`_REDACTION_RULES` patterns in order, replacing each
    match with its corresponding placeholder.  Call this function before any
    cloud-mirroring event to prevent raw credentials or personal data from
    leaving the local environment.

    Parameters
    ----------
    text:
        The raw string to sanitise.

    Returns
    -------
    str
        A copy of *text* with all matched sensitive patterns replaced by
        safe placeholders (e.g. ``[REDACTED_TOKEN]``, ``[REDACTED_EMAIL]``).
    """
    for pattern, placeholder in _REDACTION_RULES:
        text = pattern.sub(placeholder, text)
    return text


def prepare_system_recovery(system_id: str) -> list[dict]:
    """
    Self-Healing Protocol — prepare a recovery snapshot for *system_id*.

    Queries the brain vault for all Bible / core-logic records tagged with
    *system_id* and returns them as a list of export dicts.  The caller can
    serialise the result and use it to reboot the target system from a
    known-good RAG backup.

    Parameters
    ----------
    system_id:
        Sovereign system identifier (e.g. ``"pioneer-trader"``).

    Returns
    -------
    list[dict]
        Export records — each entry contains ``id``, ``document``, and
        ``metadata`` fields sourced from the brain vault.
    """
    collection = get_collection()
    records = export_system_bible(collection, system_id)
    logger.info(
        "Self-Healing: recovery snapshot prepared for system '%s' — %d records.",
        system_id,
        len(records),
    )
    return records

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

            # Self-Healing Protocol — if the matching record is a Bible /
            # core-logic file, flag the owning system as corrupted and prepare
            # a recovery snapshot from the RAG backup.
            best_meta = metadatas[best_idx] or {}
            if best_meta.get("is_bible") == "true":
                system_id = best_meta.get("system_origin", "unknown")
                _append_corruption_alert(system_id, best_source, proposed_content)
                logger.warning(
                    "Guardian: Bible record corruption detected for system '%s' "
                    "(source=%r). Preparing RAG recovery snapshot.",
                    system_id,
                    best_source,
                )
                try:
                    prepare_system_recovery(system_id)
                except Exception as exc:
                    logger.error(
                        "Guardian: self-healing recovery failed for system '%s': %s",
                        system_id,
                        exc,
                    )

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
        existing vault documents.  Additionally enforces the **5-File
        Purification** rule: writes to any of the protected sovereign files
        (``brain.py``, ``logger.py``, ``bridge.py``, ``gatekeeper.py``,
        ``run_trader.py``) are unconditionally blocked regardless of
        similarity score.
        """
        # 5-File Purification — hard block on protected sovereign filenames.
        target_name = pathlib.Path(filepath).name
        if target_name in _PURIFICATION_FILES:
            _append_purification_alert(filepath)
            logger.warning(
                "Guardian: 5-File Purification VETO — '%s' is a protected file.",
                filepath,
            )
            raise GuardianVetoError(
                1.0,
                filepath,
                f"5-File Purification Hard Veto — '{filepath}' is a protected "
                "sovereign file and cannot be overwritten.",
            )

        self.check(content, raise_on_veto=True)
        path = pathlib.Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info("Guardian: write approved → %s", filepath)
