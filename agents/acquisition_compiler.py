"""
Universal Acquisition Matrix — Staging Scaffolding
====================================================
Framework script for T.I.A. and ORACLE to stage global model and dataset
acquisition targets before any bandwidth is allocated.

Constraint: This module is a **staging ground only**. It does NOT contain
any download, scraping, or execution logic. All targets are staged here
by the personas and reviewed before any network operations commence.

Usage::

    matrix = UniversalAcquisitionMatrix()
    matrix.stage("Universal_Knowledge", name="wikipedia-en", source="huggingface")
    matrix.summary()
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Acquisition categories — mapped to fleet directives
# ---------------------------------------------------------------------------

ACQUISITION_CATEGORIES: list[str] = [
    "Universal_Knowledge",
    "Quantum_Math",
    "Biological_Sim",
    "High_Freq_Trading",
    "Audio_Generative",
    "Code_Purification",
    "Dark_Matter_AION_Bridge",
]


# ---------------------------------------------------------------------------
# Target dataclass
# ---------------------------------------------------------------------------


@dataclass
class AcquisitionTarget:
    """
    Represents a single staged acquisition target (model or dataset).

    All fields are informational only — no download logic is executed here.
    """

    name: str
    category: str
    source: str
    notes: str = ""
    staged_by: str = "T.I.A."
    staged_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Universal Acquisition Matrix
# ---------------------------------------------------------------------------


class UniversalAcquisitionMatrix:
    """
    Staging registry for all model and dataset acquisition targets.

    Targets are grouped by category and held in memory until the fleet
    authorises bandwidth allocation. No network calls are made here.

    Attributes
    ----------
    targets:
        Dict mapping each acquisition category to its list of staged targets.
    """

    def __init__(self) -> None:
        self.targets: dict[str, list[AcquisitionTarget]] = {
            category: [] for category in ACQUISITION_CATEGORIES
        }

    # ------------------------------------------------------------------
    # Staging
    # ------------------------------------------------------------------

    def stage(
        self,
        category: str,
        name: str,
        source: str,
        notes: str = "",
        staged_by: str = "T.I.A.",
        metadata: dict[str, Any] | None = None,
    ) -> AcquisitionTarget:
        """
        Stage a new acquisition target in the given *category*.

        Parameters
        ----------
        category:
            One of the defined ``ACQUISITION_CATEGORIES``.
        name:
            Human-readable name for the model or dataset.
        source:
            Origin location (e.g. ``"huggingface"``, ``"arxiv"``, ``"kaggle"``).
        notes:
            Optional free-text notes from the staging persona.
        staged_by:
            Name of the persona staging this target.
        metadata:
            Optional dict of extra attributes.

        Returns
        -------
        AcquisitionTarget
            The staged target entry.

        Raises
        ------
        ValueError
            If *category* is not a recognised acquisition category.
        """
        if category not in self.targets:
            raise ValueError(
                f"Unknown category '{category}'. "
                f"Valid categories: {ACQUISITION_CATEGORIES}"
            )

        target = AcquisitionTarget(
            name=name,
            category=category,
            source=source,
            notes=notes,
            staged_by=staged_by,
            metadata=metadata or {},
        )
        self.targets[category].append(target)
        logger.info(
            "[AcquisitionMatrix] Staged '%s' in category '%s' (by %s).",
            name,
            category,
            staged_by,
        )
        return target

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, int]:
        """
        Return a dict mapping each category to its current staged target count.
        """
        return {cat: len(targets) for cat, targets in self.targets.items()}

    def total_staged(self) -> int:
        """Return the total number of staged targets across all categories."""
        return sum(len(t) for t in self.targets.values())

    def to_dict(self) -> dict[str, Any]:
        """
        Serialise the full matrix to a plain dict suitable for JSON export.
        """
        return {
            "generated": datetime.now(timezone.utc).isoformat(),
            "total_staged": self.total_staged(),
            "categories": {
                cat: [
                    {
                        "name": t.name,
                        "source": t.source,
                        "notes": t.notes,
                        "staged_by": t.staged_by,
                        "staged_at": t.staged_at,
                        "metadata": t.metadata,
                    }
                    for t in targets
                ]
                for cat, targets in self.targets.items()
            },
        }

    def export_json(self, path: str | Path) -> None:
        """
        Write the serialised matrix to *path* as a JSON file.

        No download logic is triggered by this export.
        """
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
        logger.info("[AcquisitionMatrix] Exported staging manifest to %s.", out)
