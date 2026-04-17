"""
src.ingestion — Phase-2 activated harvester entry points.

Thin facade over :mod:`ingestion.omni_harvest` that matches the directive's
mandated path (`src/ingestion/harvester.py`).
"""

from src.ingestion.harvester import Harvester, SUPPORTED_EXTENSIONS, PARTITION_COUNT

__all__ = ["Harvester", "SUPPORTED_EXTENSIONS", "PARTITION_COUNT"]
