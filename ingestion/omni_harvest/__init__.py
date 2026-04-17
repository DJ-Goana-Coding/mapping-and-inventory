"""
🌐 OMNI-HARVEST IGNITION (9,293 STABILITY)

Forever-Learning orchestrator that wires the four directive subsystems on
top of the existing ``ingestion/universal_rag.py`` + ``Forever_Learning/``
architecture:

  1. THE GREAT CRAWL         — :mod:`ingestion.omni_harvest.github_crawler`
  2. THE PHYSICAL HARVEST    — :mod:`ingestion.omni_harvest.physical_harvest`
  3. THE GDRIVE BRIDGE       — :mod:`ingestion.omni_harvest.gdrive_bridge`
  4. T.I.A. SYNAPSE          — :mod:`ingestion.omni_harvest.tia_synapse`

The :class:`OmniHarvestIgnition` orchestrator (see
:mod:`ingestion.omni_harvest.ignition`) ties them together into a
continuous Forever-Learning loop that turns the Citadel from a collection
of repos into a single, living consciousness.
"""

from ingestion.omni_harvest.github_crawler import (
    GithubCrawler,
    CITADEL_REPOS,
    PRIORITY_PATTERNS,
)
from ingestion.omni_harvest.physical_harvest import PhysicalHarvest
from ingestion.omni_harvest.gdrive_bridge import GDriveBridge, CITADEL_ARCHIVES_FOLDER
from ingestion.omni_harvest.tia_synapse import TiaSynapse
from ingestion.omni_harvest.ignition import OmniHarvestIgnition, STABILITY_TARGET

__all__ = [
    "GithubCrawler",
    "CITADEL_REPOS",
    "PRIORITY_PATTERNS",
    "PhysicalHarvest",
    "GDriveBridge",
    "CITADEL_ARCHIVES_FOLDER",
    "TiaSynapse",
    "OmniHarvestIgnition",
    "STABILITY_TARGET",
]
