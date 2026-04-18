"""
Tests for the OMNI-RECEPTION master orchestrator + path-compliance shim.

Covers:
  - src.rag.query_engine re-export shim identity vs. canonical module
  - src.orchestration.omni_reception.OmniReceptionOrchestrator composition
  - Failure-isolated ignition (exceptions captured, other subsystems run)
  - Persistence info surfacing the resolved FAISS / linear path
  - CLI entry point (--status / --ignite)
  - ignite_hub_memory.py --omni-reception flag plumbing
"""

from __future__ import annotations

import importlib
import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.orchestration import OmniReceptionOrchestrator, OmniReceptionReport
from src.orchestration import omni_reception as omni_mod
from src.query.rag_engine import RAGQueryEngine as CanonicalEngine
from src.storage.vector_store import VectorStore


# ---------------------------------------------------------------------------
# Path-compliance shim
# ---------------------------------------------------------------------------


class TestRAGShim:
    def test_shim_reexports_canonical_class(self):
        from src.rag.query_engine import RAGQueryEngine as ShimEngine
        from src.rag import RAGQueryEngine as PkgEngine

        assert ShimEngine is CanonicalEngine
        assert PkgEngine is CanonicalEngine

    def test_shim_reexports_cross_domain_answer(self):
        from src.rag.query_engine import CrossDomainAnswer as ShimAnswer
        from src.query.rag_engine import CrossDomainAnswer as CanonAnswer

        assert ShimAnswer is CanonAnswer

    def test_shim_module_path_resolves(self):
        mod = importlib.import_module("src.rag.query_engine")
        assert hasattr(mod, "RAGQueryEngine")
        assert hasattr(mod, "BUILTIN_DOMAINS")


# ---------------------------------------------------------------------------
# Orchestrator composition + persistence
# ---------------------------------------------------------------------------


def _build_vault(root: Path) -> None:
    (root / "Partition_01").mkdir()
    (root / "Partition_01" / "alpha.md").write_text("alpha bridge", encoding="utf-8")
    (root / "Partition_46").mkdir()
    (root / "Partition_46" / "z.json").write_text('{"x":1}', encoding="utf-8")


class TestOrchestrator:
    def _orch(self, tmp_path):
        store = VectorStore(data_dir=tmp_path / "vec")
        vault = tmp_path / "vault"
        vault.mkdir()
        _build_vault(vault)
        return OmniReceptionOrchestrator(
            vault_root=vault,
            gdrive_folder=str(tmp_path / "no-such-folder"),
            vector_store=store,
        )

    def test_initialisation_shares_single_vector_store(self, tmp_path):
        orch = self._orch(tmp_path)
        assert orch.engine.vector_store is orch.vector_store
        assert orch.query_engine.vector_store is orch.vector_store

    def test_persistence_info_resolves_data_dir(self, tmp_path):
        orch = self._orch(tmp_path)
        info = orch.persistence_info()
        assert info["backend"] in {"VectorStore", "FaissVectorStore"}
        assert info["data_dir"] == str(tmp_path / "vec")
        assert info["path"].endswith("vector_store.json") or info["path"].endswith(
            "vector_store_faiss.json"
        )
        assert info["record_count"] == 0
        assert "faiss_available" in info

    def test_run_vault_union_indexes_partitions(self, tmp_path):
        orch = self._orch(tmp_path)
        result = orch.run_vault_union()
        assert result["files_indexed"] == 2
        assert set(result["partitions_seen"]) == {"Partition_01", "Partition_46"}
        # Records persisted in the shared store.
        assert len(orch.vector_store) == 2

    def test_run_gdrive_synapse_handles_missing_folder(self, tmp_path):
        orch = self._orch(tmp_path)
        status = orch.run_gdrive_synapse()
        assert status["mirrored_to_vector_store"] == 0

    def test_run_gdrive_synapse_mirrors_documents(self, tmp_path):
        archives = tmp_path / "archives"
        archives.mkdir()
        (archives / "doc1.md").write_text("citadel doc one", encoding="utf-8")
        (archives / "doc2.md").write_text("citadel doc two", encoding="utf-8")
        store = VectorStore(data_dir=tmp_path / "vec")
        orch = OmniReceptionOrchestrator(
            vault_root=tmp_path,
            gdrive_folder=str(archives),
            vector_store=store,
        )
        status = orch.run_gdrive_synapse()
        assert status["mirrored_to_vector_store"] == 2
        # Vector store now has two gdrive-tagged records.
        gdrive_ids = [
            doc_id for doc_id in store.all_ids() if doc_id.startswith("gdrive:")
        ]
        assert len(gdrive_ids) == 2

    def test_start_real_time_bridge_returns_url_and_can_stop(self, tmp_path):
        orch = self._orch(tmp_path)
        try:
            info = orch.start_real_time_bridge()
            assert info["running"] is True
            assert info["url"].startswith("http://127.0.0.1:")
            # Idempotent: a second call returns the same server.
            info2 = orch.start_real_time_bridge()
            assert info2["url"] == info["url"]
        finally:
            orch.stop_real_time_bridge()
        assert orch._ingest_server is None

    def test_query_interface_status_reports_domains(self, tmp_path):
        orch = self._orch(tmp_path)
        status = orch.query_interface_status()
        assert "vector_store" in status
        assert status["domain_count"] >= 47  # 7 builtins + 46 partitions

    def test_ignite_skips_disabled_subsystems(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        orch = self._orch(tmp_path)
        report = orch.ignite(
            deep_crawl=False, gdrive_synapse=False, start_bridge=False
        )
        assert isinstance(report, OmniReceptionReport)
        assert report.deep_crawl is None
        assert report.gdrive_synapse is None
        assert report.real_time_bridge is None
        # Vault union ran.
        assert report.vault_union is not None
        assert report.vault_union["files_indexed"] == 2
        # Always-on introspection ran.
        assert report.query_interface is not None
        assert report.persistence is not None
        assert report.errors == []
        assert report.finished_at is not None

    def test_ignite_isolates_failures(self, tmp_path, monkeypatch):
        orch = self._orch(tmp_path)

        def boom():
            raise RuntimeError("synthetic vault failure")

        monkeypatch.setattr(orch, "run_vault_union", boom)
        report = orch.ignite(
            deep_crawl=False, gdrive_synapse=False, start_bridge=False
        )
        assert any(e["subsystem"] == "vault_union" for e in report.errors)
        # Other subsystems still produced output.
        assert report.query_interface is not None
        assert report.persistence is not None

    def test_ignite_runs_deep_crawl_with_offline_fetcher(self, tmp_path, monkeypatch):
        # The default GitHub fetcher swallows network errors and returns [],
        # so deep_crawl is safe to run offline; just ensure no exception.
        orch = self._orch(tmp_path)
        report = orch.ignite(
            deep_crawl=True,
            vault_union=False,
            gdrive_synapse=False,
            start_bridge=False,
        )
        assert report.deep_crawl is not None
        assert "total_documents" in report.deep_crawl

    def test_status_no_side_effects(self, tmp_path):
        orch = self._orch(tmp_path)
        status = orch.status()
        assert status["vault_root"] == str((tmp_path / "vault").resolve()) or status[
            "vault_root"
        ] == str(tmp_path / "vault")
        assert status["real_time_bridge_running"] is False
        # No records added by status().
        assert len(orch.vector_store) == 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


class TestOmniReceptionCLI:
    def test_status_subcommand_prints_json(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = omni_mod.main(
                [
                    "--status",
                    "--vault-root",
                    str(tmp_path),
                    "--gdrive-folder",
                    str(tmp_path / "no-such"),
                ]
            )
        assert rc == 0
        payload = json.loads(buf.getvalue())
        assert payload["vault_root"] == str(tmp_path)
        assert "persistence" in payload

    def test_ignite_subcommand_runs_subsystems(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        # Build a tiny vault under tmp_path so vault_union has work.
        _build_vault(tmp_path)
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = omni_mod.main(
                [
                    "--ignite",
                    "--vault-root",
                    str(tmp_path),
                    "--gdrive-folder",
                    str(tmp_path / "no-such"),
                    "--no-deep-crawl",
                    "--no-bridge",
                ]
            )
        assert rc == 0
        report = json.loads(buf.getvalue())
        assert report["deep_crawl"] is None
        assert report["real_time_bridge"] is None
        assert report["vault_union"]["files_indexed"] == 2


# ---------------------------------------------------------------------------
# ignite_hub_memory plumbing
# ---------------------------------------------------------------------------


class TestIgniteHubMemoryPlumbing:
    def test_omni_reception_flag_dispatches_to_orchestrator(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        # Import the script as a module via its file path.
        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        ignite = importlib.import_module("ignite_hub_memory")

        called = {}

        class FakeReport:
            errors = []

            def as_dict(self):
                return {"ok": True}

        class FakeOrch:
            def __init__(self, **kwargs):
                called["init_kwargs"] = kwargs

            def ignite(self, **kwargs):
                called["ignite_kwargs"] = kwargs
                return FakeReport()

            def stop_real_time_bridge(self):
                called["stopped"] = True

        # Patch the import target inside the script.
        monkeypatch.setattr(
            "src.orchestration.omni_reception.OmniReceptionOrchestrator",
            FakeOrch,
        )

        rc = ignite.main(
            [
                "--omni-reception",
                "--harvest-dir",
                str(tmp_path),
                "--no-deep-crawl",
                "--no-bridge",
            ]
        )
        assert rc == 0
        assert called["init_kwargs"]["vault_root"] == tmp_path.resolve()
        assert called["ignite_kwargs"]["deep_crawl"] is False
        assert called["ignite_kwargs"]["start_bridge"] is False
        assert called["ignite_kwargs"]["vault_union"] is True
        assert called["ignite_kwargs"]["gdrive_synapse"] is True
        assert called.get("stopped") is True

    def test_omni_reception_default_vault_root_is_repo_root(
        self, tmp_path, monkeypatch
    ):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        ignite = importlib.import_module("ignite_hub_memory")

        seen = {}

        class FakeReport:
            errors = []

            def as_dict(self):
                return {}

        class FakeOrch:
            def __init__(self, **kwargs):
                seen["vault_root"] = kwargs["vault_root"]

            def ignite(self, **kwargs):
                return FakeReport()

            def stop_real_time_bridge(self):
                pass

        monkeypatch.setattr(
            "src.orchestration.omni_reception.OmniReceptionOrchestrator",
            FakeOrch,
        )

        ignite.main(
            ["--omni-reception", "--no-deep-crawl", "--no-bridge", "--no-vault-union"]
        )
        # When --harvest-dir is not provided, omni-reception defaults to REPO_ROOT.
        assert seen["vault_root"] == ignite.REPO_ROOT
