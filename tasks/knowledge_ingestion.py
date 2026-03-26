"""
Knowledge Ingestion — Master Librarian Total Knowledge Crawl
============================================================
Executes a full recursive crawl of the ``E:\\RECOVERY_STAGING\\`` directory
using the ``MASTER_SYSTEM_MAP_2.csv`` category map, sorts files into
sovereign knowledge categories, and indexes metadata into District 04.

Categories
----------
* ``Quantum_Math``      — quantum mechanics, linear algebra, signal theory
* ``Bio_Science``       — biology, neuroscience, bioinformatics
* ``Universal_Lore``    — history, philosophy, esoteric/sovereign canon
* ``Military_Tech``     — defence systems, tactical frameworks, hardware specs
* ``Web3_Blockchain``   — crypto, smart contracts, DeFi, tokenomics

High-priority model weights are flagged for migration to the 1TB HF Rack
(``nodes/HF_Rack/``).

Usage
-----
Run directly::

    python -m tasks.knowledge_ingestion

Or call programmatically::

    from tasks.knowledge_ingestion import KnowledgeIngestionEngine
    engine = KnowledgeIngestionEngine()
    report = engine.run()
"""
from __future__ import annotations

import csv
import logging
import os
import pathlib
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Default root path for the Recovery Staging drive.
#: Override at runtime via the ``RECOVERY_STAGING_ROOT`` environment variable
#: (e.g. ``export RECOVERY_STAGING_ROOT=/mnt/recovery`` on Linux/macOS).
#: The default is the Windows path specified in the Phase 21 mandate.
RECOVERY_STAGING_ROOT: pathlib.Path = pathlib.Path(r"E:\RECOVERY_STAGING")

#: Path to the category map CSV (override via ``MASTER_SYSTEM_MAP_PATH`` env var).
MASTER_SYSTEM_MAP_DEFAULT: pathlib.Path = (
    pathlib.Path(__file__).parent.parent / "MASTER_SYSTEM_MAP_2.csv"
)

#: District 04 output path for indexed metadata.
DISTRICT_04_PATH: pathlib.Path = (
    pathlib.Path(__file__).parent.parent / "District_04_OUTPUT_HARVEST"
)

#: HF Rack destination for high-priority model weights.
HF_RACK_PATH: pathlib.Path = (
    pathlib.Path(__file__).parent.parent / "nodes" / "HF_Rack"
)

#: Recognised sovereign knowledge categories.
CATEGORIES: list[str] = [
    "Quantum_Math",
    "Bio_Science",
    "Universal_Lore",
    "Military_Tech",
    "Web3_Blockchain",
]

#: File extensions that indicate high-priority model weights for HF Rack migration.
MODEL_WEIGHT_EXTENSIONS: frozenset[str] = frozenset(
    {".bin", ".pt", ".pth", ".safetensors", ".gguf", ".ggml", ".pkl", ".h5"}
)

# ---------------------------------------------------------------------------
# Keyword maps for auto-categorisation
# ---------------------------------------------------------------------------
_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "Quantum_Math": [
        "quantum", "fourier", "eigen", "tensor", "matrix", "linear algebra",
        "signal", "frequency", "wave", "hilbert", "schrodinger",
    ],
    "Bio_Science": [
        "biology", "neuroscience", "genome", "dna", "rna", "protein",
        "bioinformatics", "neural", "synapse", "cortex", "anatomy",
    ],
    "Universal_Lore": [
        "lore", "history", "philosophy", "sovereign", "esoteric", "myth",
        "doofy", "citadel", "vortex", "archive", "legend", "story",
    ],
    "Military_Tech": [
        "defence", "defense", "military", "tactical", "weapon", "radar",
        "combat", "ballistic", "intel", "recon", "spec ops",
    ],
    "Web3_Blockchain": [
        "blockchain", "crypto", "defi", "nft", "smart contract", "solidity",
        "ethereum", "bitcoin", "tokenomics", "web3", "dao",
    ],
}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class IngestionRecord:
    """Metadata record for a single ingested file."""

    filename: str
    category: str
    relative_path: str
    size_bytes: int
    high_priority_model: bool = False
    hf_rack_candidate: bool = False
    extra_meta: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _classify_file(filename: str, extra_hint: str = "") -> str:
    """
    Auto-classify *filename* into one of :data:`CATEGORIES`.

    Checks both the filename and *extra_hint* (e.g. a CSV description column)
    against :data:`_CATEGORY_KEYWORDS`.  Falls back to ``"Universal_Lore"``
    when no keyword matches.
    """
    combined = (filename + " " + extra_hint).lower()
    for category, keywords in _CATEGORY_KEYWORDS.items():
        if any(kw in combined for kw in keywords):
            return category
    return "Universal_Lore"


def _load_master_map(csv_path: pathlib.Path) -> dict[str, str]:
    """
    Load *csv_path* (``MASTER_SYSTEM_MAP_2.csv``) into a filename→category
    lookup dict.  Columns expected: ``filename``, ``category``.
    """
    mapping: dict[str, str] = {}
    if not csv_path.exists():
        logger.warning(
            "KnowledgeIngestion: master map not found at %s — auto-classify only.",
            csv_path,
        )
        return mapping

    with csv_path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            fname = row.get("filename", "").strip()
            cat = row.get("category", "").strip()
            if fname and cat in CATEGORIES:
                mapping[fname] = cat

    logger.info(
        "KnowledgeIngestion: loaded %d entries from master map.", len(mapping)
    )
    return mapping


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------


class KnowledgeIngestionEngine:
    """
    Recursive crawl engine for ``E:\\RECOVERY_STAGING\\``.

    Parameters
    ----------
    staging_root:
        Override for the recovery staging root path.
    master_map_path:
        Override for the ``MASTER_SYSTEM_MAP_2.csv`` path.
    """

    def __init__(
        self,
        staging_root: pathlib.Path | str | None = None,
        master_map_path: pathlib.Path | str | None = None,
    ) -> None:
        env_root = os.getenv("RECOVERY_STAGING_ROOT")
        self.staging_root = pathlib.Path(
            staging_root or env_root or RECOVERY_STAGING_ROOT
        )
        self.master_map_path = pathlib.Path(
            master_map_path
            or os.getenv("MASTER_SYSTEM_MAP_PATH", str(MASTER_SYSTEM_MAP_DEFAULT))
        )
        self._master_map: dict[str, str] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> dict[str, Any]:
        """
        Execute the full crawl and return an ingestion report.

        Returns
        -------
        dict
            Summary containing ``total_files``, ``by_category``,
            ``hf_rack_candidates``, and ``records``.
        """
        self._master_map = _load_master_map(self.master_map_path)

        if not self.staging_root.exists():
            logger.warning(
                "KnowledgeIngestion: staging root %s does not exist — "
                "returning empty report.",
                self.staging_root,
            )
            return self._empty_report()

        records: list[IngestionRecord] = []
        for file_path in self.staging_root.rglob("*"):
            if not file_path.is_file():
                continue
            record = self._process_file(file_path)
            records.append(record)

        self._write_district04_index(records)

        by_category: dict[str, int] = {cat: 0 for cat in CATEGORIES}
        hf_candidates: list[str] = []
        for rec in records:
            by_category[rec.category] = by_category.get(rec.category, 0) + 1
            if rec.hf_rack_candidate:
                hf_candidates.append(rec.relative_path)

        logger.info(
            "KnowledgeIngestion: crawl complete — %d files | %s",
            len(records),
            by_category,
        )

        return {
            "total_files": len(records),
            "by_category": by_category,
            "hf_rack_candidates": hf_candidates,
            "records": [self._record_to_dict(r) for r in records],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _process_file(self, file_path: pathlib.Path) -> IngestionRecord:
        rel = str(file_path.relative_to(self.staging_root))
        size = file_path.stat().st_size
        hint = self._master_map.get(file_path.name, "")
        category = hint if hint else _classify_file(file_path.name)
        is_model = file_path.suffix.lower() in MODEL_WEIGHT_EXTENSIONS

        return IngestionRecord(
            filename=file_path.name,
            category=category,
            relative_path=rel,
            size_bytes=size,
            high_priority_model=is_model,
            hf_rack_candidate=is_model,
        )

    def _write_district04_index(self, records: list[IngestionRecord]) -> None:
        """Write a lightweight TSV index of all records into District 04."""
        try:
            DISTRICT_04_PATH.mkdir(parents=True, exist_ok=True)
            index_path = DISTRICT_04_PATH / "knowledge_ingestion_index.tsv"
            with index_path.open("w", encoding="utf-8") as fh:
                fh.write(
                    "filename\tcategory\trelative_path\tsize_bytes\thf_rack_candidate\n"
                )
                for rec in records:
                    fh.write(
                        f"{rec.filename}\t{rec.category}\t"
                        f"{rec.relative_path}\t{rec.size_bytes}\t"
                        f"{rec.hf_rack_candidate}\n"
                    )
            logger.info(
                "KnowledgeIngestion: District 04 index written → %s", index_path
            )
        except OSError as exc:
            logger.warning(
                "KnowledgeIngestion: could not write District 04 index (%s).", exc
            )

    @staticmethod
    def _record_to_dict(rec: IngestionRecord) -> dict[str, Any]:
        return {
            "filename": rec.filename,
            "category": rec.category,
            "relative_path": rec.relative_path,
            "size_bytes": rec.size_bytes,
            "hf_rack_candidate": rec.hf_rack_candidate,
        }

    @staticmethod
    def _empty_report() -> dict[str, Any]:
        return {
            "total_files": 0,
            "by_category": {cat: 0 for cat in CATEGORIES},
            "hf_rack_candidates": [],
            "records": [],
        }


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    engine = KnowledgeIngestionEngine()
    report = engine.run()
    print(f"Ingestion complete — {report['total_files']} files processed.")
    for cat, count in report["by_category"].items():
        print(f"  {cat}: {count}")
    if report["hf_rack_candidates"]:
        print(f"HF Rack candidates: {len(report['hf_rack_candidates'])}")
