#!/usr/bin/env python3
"""
🛰️ OMNI-RECEPTION MASTER ORCHESTRATOR

Composes the five OMNI-RECEPTION IGNITION subsystems behind a single
entry point so the Librarian can be ignited with one call:

  1. **Deep Crawl** — :class:`src.ingestion.universal_rag.UniversalRAGEngine`
     recursively indexes the 12 ``DJ-Goana-Coding`` repos via ``GH_TOKEN``.
  2. **Vault Union** — :class:`src.ingestion.vault_indexer.VaultIndexer`
     walks ``Partition_01..46`` under the configured root.
  3. **GDrive Synapse** — :class:`ingestion.omni_harvest.gdrive_bridge.GDriveBridge`
     ingests the ``Citadel Archives`` folder.
  4. **Real-Time Bridge** — :class:`src.api.ingest_server.IngestServer`
     activates ``POST /v1/ingest`` for Oppo-Node + S10 telemetry.
  5. **Query Interface** — :class:`src.query.rag_engine.RAGQueryEngine`
     wired to the persistent (FAISS-backed when available) vector store.

This module performs **no** behavioural changes to the underlying
subsystems; it only composes them and surfaces a single status report
plus a CLI.  Each step is independent and failure-isolated: a failure in
one subsystem is recorded in the report and the remaining subsystems
still run.

Usage
-----
Library::

    from src.orchestration import OmniReceptionOrchestrator
    orch = OmniReceptionOrchestrator(vault_root="/repo")
    report = orch.ignite(deep_crawl=False, start_bridge=False)
    print(report.as_dict())

CLI::

    python -m src.orchestration.omni_reception --vault-root . --status
    python -m src.orchestration.omni_reception --ignite --no-deep-crawl

Persistence
-----------
The orchestrator resolves and exposes the on-disk path used by the
vector store (FAISS-backed when ``faiss`` is importable, linear-scan
fallback otherwise).  This is the "Forever Learning" substrate; both
backends share the same JSON layout so a deployment can install
``faiss`` later without losing records.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from src.ingestion.universal_rag import UniversalRAGEngine
from src.ingestion.vault_indexer import VaultIndexer
from src.query.rag_engine import RAGQueryEngine
from src.storage.vector_store import VectorStore

log = logging.getLogger(__name__)

# Default vault root: the repository root (parent of ``src``).
DEFAULT_VAULT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GDRIVE_FOLDER = "Citadel Archives"


@dataclass
class OmniReceptionReport:
    """Structured report returned by :meth:`OmniReceptionOrchestrator.ignite`."""

    started_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    finished_at: Optional[str] = None
    deep_crawl: Optional[Dict[str, Any]] = None
    vault_union: Optional[Dict[str, Any]] = None
    gdrive_synapse: Optional[Dict[str, Any]] = None
    real_time_bridge: Optional[Dict[str, Any]] = None
    query_interface: Optional[Dict[str, Any]] = None
    persistence: Optional[Dict[str, Any]] = None
    errors: List[Dict[str, str]] = field(default_factory=list)

    def record_error(self, subsystem: str, exc: BaseException) -> None:
        self.errors.append(
            {
                "subsystem": subsystem,
                "error": f"{type(exc).__name__}: {exc}",
            }
        )

    def as_dict(self) -> Dict[str, Any]:
        return {
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "deep_crawl": self.deep_crawl,
            "vault_union": self.vault_union,
            "gdrive_synapse": self.gdrive_synapse,
            "real_time_bridge": self.real_time_bridge,
            "query_interface": self.query_interface,
            "persistence": self.persistence,
            "errors": list(self.errors),
        }


class OmniReceptionOrchestrator:
    """Master orchestrator composing the five OMNI-RECEPTION subsystems."""

    def __init__(
        self,
        *,
        vault_root: Optional[Path] = None,
        gdrive_folder: str = DEFAULT_GDRIVE_FOLDER,
        vector_store: Optional[VectorStore] = None,
        gh_token: Optional[str] = None,
        repos: Optional[Sequence[str]] = None,
        ingest_host: str = "127.0.0.1",
        ingest_port: int = 0,
    ) -> None:
        self.vault_root = Path(vault_root) if vault_root else DEFAULT_VAULT_ROOT
        self.gdrive_folder = gdrive_folder
        self.ingest_host = ingest_host
        self.ingest_port = ingest_port

        # Build (or reuse) the persistent vector store first so every
        # subsystem shares the same Forever-Learning substrate.
        self.engine = UniversalRAGEngine(
            vector_store=vector_store,
            gh_token=gh_token,
            repos=repos,
        )
        self.vector_store: VectorStore = self.engine.vector_store
        self.query_engine = RAGQueryEngine(vector_store=self.vector_store)

        # Started lazily so importing this module never opens a socket.
        self._ingest_server = None  # type: ignore[assignment]

    # ------------------------------------------------------------------
    # Persistence introspection
    # ------------------------------------------------------------------

    def persistence_info(self) -> Dict[str, Any]:
        """Return resolved on-disk paths for the Forever-Learning substrate."""
        store = self.vector_store
        data_dir = getattr(store, "data_dir", None)
        path = getattr(store, "path", None)
        info: Dict[str, Any] = {
            "backend": store.__class__.__name__,
            "data_dir": str(data_dir) if data_dir else None,
            "path": str(path) if path else None,
            "exists": bool(path and Path(path).exists()),
            "record_count": len(store),
        }
        # Surface FAISS availability when the FAISS-backed store is in use.
        try:
            from src.storage.faiss_store import faiss_available

            info["faiss_available"] = faiss_available()
        except Exception:  # pragma: no cover - defensive
            info["faiss_available"] = False
        return info

    # ------------------------------------------------------------------
    # Subsystem activations
    # ------------------------------------------------------------------

    def run_deep_crawl(self) -> Dict[str, Any]:
        """Subsystem #1: recursive crawl of the 12 DJ-Goana-Coding repos."""
        return self.engine.deep_crawl()

    def run_vault_union(self) -> Dict[str, Any]:
        """Subsystem #2: index every Partition_01..46 directory under root."""
        indexer = VaultIndexer(root=self.vault_root, vector_store=self.vector_store)
        return indexer.index_all().as_dict()

    def run_gdrive_synapse(self) -> Dict[str, Any]:
        """Subsystem #3: ingest the Citadel Archives folder via GDrive bridge."""
        # Imported lazily so the orchestrator stays importable even when
        # the legacy ``ingestion`` package has optional deps missing.
        from ingestion.omni_harvest.gdrive_bridge import GDriveBridge

        bridge = GDriveBridge(folder=self.gdrive_folder)
        queued = bridge.ingest_archives()
        # Mirror queued documents into the persistent vector store so the
        # query engine can reach them via the shared substrate.
        for item in queued:
            title = str(item.get("title") or item.get("id") or "gdrive-doc")
            content = str(item.get("content") or "")
            doc_id = f"gdrive:{title}"
            self.vector_store.upsert(
                doc_id=doc_id,
                text=content,
                metadata={
                    "source": "gdrive",
                    "path": title,
                    "folder": self.gdrive_folder,
                },
            )
        status = bridge.status()
        status["mirrored_to_vector_store"] = len(queued)
        return status

    def start_real_time_bridge(self) -> Dict[str, Any]:
        """Subsystem #4: start ``POST /v1/ingest`` for Oppo-Node + S10."""
        from src.api.ingest_server import IngestServer

        if self._ingest_server is None:
            self._ingest_server = IngestServer(
                host=self.ingest_host, port=self.ingest_port
            )
            self._ingest_server.start()
        return {
            "url": self._ingest_server.url,
            "host": self._ingest_server.host,
            "port": self._ingest_server.port,
            "running": True,
        }

    def stop_real_time_bridge(self) -> None:
        if self._ingest_server is not None:
            self._ingest_server.stop()
            self._ingest_server = None

    def query_interface_status(self) -> Dict[str, Any]:
        """Subsystem #5: introspect the wired query engine."""
        return self.query_engine.status()

    # ------------------------------------------------------------------
    # Composite ignition
    # ------------------------------------------------------------------

    def ignite(
        self,
        *,
        deep_crawl: bool = True,
        vault_union: bool = True,
        gdrive_synapse: bool = True,
        start_bridge: bool = True,
    ) -> OmniReceptionReport:
        """Run every requested subsystem and return a combined report.

        Each subsystem is failure-isolated: an exception in one is
        captured in ``report.errors`` and the rest continue.
        """
        report = OmniReceptionReport()

        if deep_crawl:
            try:
                report.deep_crawl = self.run_deep_crawl()
            except Exception as exc:  # pragma: no cover - network/auth errors
                log.exception("deep_crawl failed")
                report.record_error("deep_crawl", exc)

        if vault_union:
            try:
                report.vault_union = self.run_vault_union()
            except Exception as exc:
                log.exception("vault_union failed")
                report.record_error("vault_union", exc)

        if gdrive_synapse:
            try:
                report.gdrive_synapse = self.run_gdrive_synapse()
            except Exception as exc:
                log.exception("gdrive_synapse failed")
                report.record_error("gdrive_synapse", exc)

        if start_bridge:
            try:
                report.real_time_bridge = self.start_real_time_bridge()
            except Exception as exc:
                log.exception("real_time_bridge failed")
                report.record_error("real_time_bridge", exc)

        try:
            report.query_interface = self.query_interface_status()
        except Exception as exc:  # pragma: no cover - defensive
            report.record_error("query_interface", exc)

        try:
            report.persistence = self.persistence_info()
        except Exception as exc:  # pragma: no cover - defensive
            report.record_error("persistence", exc)

        report.finished_at = datetime.now(timezone.utc).isoformat()
        return report

    # ------------------------------------------------------------------
    # Status (no side effects)
    # ------------------------------------------------------------------

    def status(self) -> Dict[str, Any]:
        return {
            "vault_root": str(self.vault_root),
            "gdrive_folder": self.gdrive_folder,
            "engine": self.engine.status(),
            "query_engine": self.query_interface_status(),
            "persistence": self.persistence_info(),
            "real_time_bridge_running": self._ingest_server is not None,
        }


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="omni_reception",
        description="OMNI-RECEPTION master orchestrator (Librarian ignition).",
    )
    parser.add_argument(
        "--vault-root",
        default=str(DEFAULT_VAULT_ROOT),
        help="Filesystem root containing Partition_01..46 (default: repo root).",
    )
    parser.add_argument(
        "--gdrive-folder",
        default=DEFAULT_GDRIVE_FOLDER,
        help='GDrive folder to ingest (default: "Citadel Archives").',
    )
    parser.add_argument(
        "--ingest-host",
        default="127.0.0.1",
        help="Bind host for /v1/ingest (default: 127.0.0.1; loopback-only).",
    )
    parser.add_argument(
        "--ingest-port", type=int, default=0,
        help="Bind port for /v1/ingest (default: 0 = ephemeral).",
    )
    parser.add_argument(
        "--gh-token",
        default=os.environ.get("GH_TOKEN"),
        help="GitHub token for Deep Crawl (default: $GH_TOKEN).",
    )

    actions = parser.add_mutually_exclusive_group()
    actions.add_argument(
        "--ignite", action="store_true",
        help="Run the requested subsystems and print the report.",
    )
    actions.add_argument(
        "--status", action="store_true",
        help="Print orchestrator status without running anything.",
    )

    parser.add_argument("--no-deep-crawl", action="store_true")
    parser.add_argument("--no-vault-union", action="store_true")
    parser.add_argument("--no-gdrive-synapse", action="store_true")
    parser.add_argument("--no-bridge", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    orch = OmniReceptionOrchestrator(
        vault_root=Path(args.vault_root),
        gdrive_folder=args.gdrive_folder,
        gh_token=args.gh_token,
        ingest_host=args.ingest_host,
        ingest_port=args.ingest_port,
    )

    if args.status or not args.ignite:
        print(json.dumps(orch.status(), indent=2, default=str))
        return 0

    report = orch.ignite(
        deep_crawl=not args.no_deep_crawl,
        vault_union=not args.no_vault_union,
        gdrive_synapse=not args.no_gdrive_synapse,
        start_bridge=not args.no_bridge,
    )
    print(json.dumps(report.as_dict(), indent=2, default=str))
    # Stop the bridge after printing so CLI invocations don't hang.
    orch.stop_real_time_bridge()
    return 2 if report.errors else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())


__all__ = [
    "OmniReceptionOrchestrator",
    "OmniReceptionReport",
    "DEFAULT_VAULT_ROOT",
    "DEFAULT_GDRIVE_FOLDER",
    "main",
]
