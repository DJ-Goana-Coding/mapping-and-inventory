#!/usr/bin/env python3
"""
🔥 OMNI-HARVEST IGNITION — Forever-Learning orchestrator.

Ties the four directive subsystems into a single continuous loop:

  1. THE GREAT CRAWL     (``GithubCrawler``)
  2. THE PHYSICAL HARVEST (``PhysicalHarvest``)
  3. THE GDRIVE BRIDGE    (``GDriveBridge``)
  4. T.I.A. SYNAPSE       (``TiaSynapse``)

Each ``tick()`` runs the three ingest flows, flushes the Universal-RAG
queue to HF Spaces, and registers every new document into the T.I.A.
Synapse index (the Forever-Learning real-time update hook).

Call :meth:`OmniHarvestIgnition.run` to execute the continuous loop.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Iterable, List, Optional

from ingestion.universal_rag import UniversalRAG
from ingestion.omni_harvest.github_crawler import GithubCrawler
from ingestion.omni_harvest.physical_harvest import PhysicalHarvest
from ingestion.omni_harvest.gdrive_bridge import GDriveBridge
from ingestion.omni_harvest.tia_synapse import TiaSynapse

log = logging.getLogger(__name__)

# Directive-mandated stability target.
STABILITY_TARGET = 9293


@dataclass
class TickResult:
    """Summary of a single ignition tick."""

    iteration: int
    started_at: str
    finished_at: str
    crawled_documents: int
    priority_documents: int
    telemetry_packets: int
    gdrive_documents: int
    synapse_documents: int
    synapse_new_documents: int
    rag_flush: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()


class OmniHarvestIgnition:
    """Orchestrator for the Forever-Learning continuous loop."""

    def __init__(
        self,
        *,
        universal_rag: Optional[UniversalRAG] = None,
        github_crawler: Optional[GithubCrawler] = None,
        physical_harvest: Optional[PhysicalHarvest] = None,
        gdrive_bridge: Optional[GDriveBridge] = None,
        tia_synapse: Optional[TiaSynapse] = None,
        telemetry_source: Optional[Callable[[], Iterable[Any]]] = None,
        sleeper: Callable[[float], None] = time.sleep,
        stability_target: int = STABILITY_TARGET,
    ) -> None:
        self.universal_rag = universal_rag or UniversalRAG()
        self.github_crawler = github_crawler or GithubCrawler(universal_rag=self.universal_rag)
        self.physical_harvest = physical_harvest or PhysicalHarvest()
        self.gdrive_bridge = gdrive_bridge or GDriveBridge(universal_rag=self.universal_rag)
        self.tia_synapse = tia_synapse or TiaSynapse()
        self.telemetry_source = telemetry_source
        self.sleeper = sleeper
        self.stability_target = stability_target

        # Align the crawler and bridge to share our RAG instance.
        self.github_crawler.universal_rag = self.universal_rag
        self.gdrive_bridge.universal_rag = self.universal_rag

        self._history: List[TickResult] = []
        self._iteration = 0

    # ------------------------------------------------------------------
    # One tick of the loop
    # ------------------------------------------------------------------

    def tick(self) -> TickResult:
        """Run one Forever-Learning cycle across all four subsystems."""
        self._iteration += 1
        started = datetime.now(timezone.utc).isoformat()
        synapse_before = self.tia_synapse.document_count()

        # 1. Great Crawl
        crawl_docs = self.github_crawler.crawl_all()
        priority = [d for d in crawl_docs if d.priority]
        for doc in crawl_docs:
            self.tia_synapse.on_new_data(
                doc_id=f"crawl:{doc.repo}:{doc.path}",
                text=f"{doc.repo} {doc.path}",
                source="github_crawl",
                path=doc.path,
            )

        # 2. Physical Harvest — optional telemetry source.
        telemetry_packets = 0
        if self.telemetry_source is not None:
            for payload in self.telemetry_source():
                try:
                    record = self.physical_harvest.process_telemetry(payload)
                except Exception:  # pragma: no cover - defensive
                    log.exception("Telemetry packet rejected")
                    continue
                telemetry_packets += 1
                for node_id in record.get("updates", []):
                    self.tia_synapse.on_new_data(
                        doc_id=f"telemetry:{record['source']}:{node_id}",
                        text=f"{record['source']} {record['kind']} {node_id}",
                        source="physical_harvest",
                        path=f"{record['source']}/{record['kind']}/{node_id}",
                    )

        # 3. GDrive Bridge
        gdrive_items = self.gdrive_bridge.ingest_archives()
        for item in gdrive_items:
            title = item.get("title", "")
            self.tia_synapse.on_new_data(
                doc_id=f"gdrive:{title}",
                text=f"{title} {item.get('content', '')}",
                source="gdrive_bridge",
                path=title,
            )

        # 4. Flush Universal-RAG queue to HF Spaces.
        try:
            flush = self.universal_rag.flush_to_spaces()
        except Exception as exc:  # pragma: no cover - network guard
            log.warning("Universal RAG flush failed: %s", exc)
            flush = {"error": str(exc)}

        synapse_after = self.tia_synapse.document_count()
        finished = datetime.now(timezone.utc).isoformat()

        result = TickResult(
            iteration=self._iteration,
            started_at=started,
            finished_at=finished,
            crawled_documents=len(crawl_docs),
            priority_documents=len(priority),
            telemetry_packets=telemetry_packets,
            gdrive_documents=len(gdrive_items),
            synapse_documents=synapse_after,
            synapse_new_documents=max(0, synapse_after - synapse_before),
            rag_flush=flush,
        )
        self._history.append(result)
        return result

    # ------------------------------------------------------------------
    # Continuous loop
    # ------------------------------------------------------------------

    def run(
        self,
        *,
        iterations: Optional[int] = None,
        interval_seconds: float = 300.0,
        should_continue: Optional[Callable[["OmniHarvestIgnition"], bool]] = None,
    ) -> List[TickResult]:
        """Run the Forever-Learning loop.

        Parameters
        ----------
        iterations:
            If ``None``, runs until ``should_continue`` returns ``False``
            (the default ``should_continue`` always returns ``True``,
            producing a true continuous loop).  Otherwise runs at most
            that many iterations — useful for bounded / test executions.
        interval_seconds:
            Sleep time between ticks.  The sleeper is injectable for
            tests (pass ``sleeper=lambda _ : None`` at construction).
        should_continue:
            Optional predicate called before each tick.  Return ``False``
            to stop the loop.
        """
        results: List[TickResult] = []
        i = 0
        while True:
            if iterations is not None and i >= iterations:
                break
            if should_continue is not None and not should_continue(self):
                break
            results.append(self.tick())
            i += 1
            if iterations is not None and i >= iterations:
                break
            self.sleeper(interval_seconds)
        return results

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def history(self) -> List[TickResult]:
        return list(self._history)

    def status(self) -> Dict[str, Any]:
        return {
            "stability_target": self.stability_target,
            "iterations_completed": self._iteration,
            "last_tick": self._history[-1].as_dict() if self._history else None,
            "subsystems": {
                "github_crawler": self.github_crawler.status(),
                "physical_harvest": self.physical_harvest.status(),
                "gdrive_bridge": self.gdrive_bridge.status(),
                "tia_synapse": self.tia_synapse.status(),
            },
        }
