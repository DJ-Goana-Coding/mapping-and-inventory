"""
Tests for the Phase-3 OMNI-RECEPTION layer:

  - src.ingestion.universal_rag.UniversalRAGEngine
  - src.ingestion.vault_indexer.VaultIndexer
  - src.storage.faiss_store.FaissVectorStore (linear fallback path)
  - src.api.ask_server.AskServer (/v1/ask)
"""

import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.api import AskServer, ASK_PATH
from src.ingestion import (
    UniversalRAGEngine,
    VaultIndexer,
    VaultIndexResult,
)
from src.query import RAGQueryEngine
from src.storage import FaissVectorStore, VectorStore, faiss_available


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _post_json(url, payload):
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# UniversalRAGEngine
# ---------------------------------------------------------------------------


class TestUniversalRAGEngine:
    def test_ingest_text_persists_and_filters(self, tmp_path):
        store = VectorStore(data_dir=tmp_path)
        engine = UniversalRAGEngine(vector_store=store)
        engine.ingest_text(
            "alpha", "vortex trade logs alpha signal", metadata={"path": "demo.md"}
        )
        engine.ingest_text("beta", "chicken soup recipe", source="kitchen")

        # Vector store has both documents.
        assert len(store) == 2
        # Source metadata is preserved.
        assert store.get("alpha").metadata["source"] == "external"
        assert store.get("beta").metadata["source"] == "kitchen"

    def test_ingest_paths_reads_files(self, tmp_path):
        f1 = tmp_path / "a.md"
        f1.write_text("alpha content", encoding="utf-8")
        f2 = tmp_path / "b.txt"
        f2.write_text("beta content", encoding="utf-8")
        missing = tmp_path / "missing.md"

        engine = UniversalRAGEngine(vector_store=VectorStore(data_dir=tmp_path / "vec"))
        results = engine.ingest_paths([f1, f2, missing])
        assert len(results) == 2
        assert all("doc_id" in r for r in results)

    def test_status_exposes_token_presence(self, tmp_path, monkeypatch):
        monkeypatch.delenv("GH_TOKEN", raising=False)
        engine = UniversalRAGEngine(
            vector_store=VectorStore(data_dir=tmp_path), gh_token="abc"
        )
        st = engine.status()
        assert st["gh_token_present"] is True
        assert "vector_store" in st
        assert len(st["repos"]) >= 1


# ---------------------------------------------------------------------------
# VaultIndexer
# ---------------------------------------------------------------------------


class TestVaultIndexer:
    def _build_vault(self, tmp_path):
        # Create three Partition_xx dirs + a non-Partition dir + nested files.
        (tmp_path / "Partition_01").mkdir()
        (tmp_path / "Partition_01" / "alpha.md").write_text(
            "alpha bridge logic", encoding="utf-8"
        )
        nested = tmp_path / "Partition_01" / "deep" / "deeper"
        nested.mkdir(parents=True)
        (nested / "core.py").write_text("print('hi')", encoding="utf-8")

        (tmp_path / "Partition_23").mkdir()
        (tmp_path / "Partition_23" / "data.json").write_text(
            '{"x":1}', encoding="utf-8"
        )

        (tmp_path / "Partition_46").mkdir()
        (tmp_path / "Partition_46" / "binary.dat").write_bytes(b"\x00\x01\x02")

        # Out-of-range — must NOT be indexed.
        (tmp_path / "Partition_47").mkdir()
        (tmp_path / "Partition_47" / "noise.md").write_text("nope", encoding="utf-8")
        (tmp_path / "OtherFolder").mkdir()
        (tmp_path / "OtherFolder" / "x.md").write_text("nope", encoding="utf-8")

    def test_discover_partitions_filters_to_01_through_46(self, tmp_path):
        self._build_vault(tmp_path)
        indexer = VaultIndexer(root=tmp_path, vector_store=VectorStore(data_dir=tmp_path / "v"))
        names = [p.name for p in indexer.discover_partitions()]
        assert names == ["Partition_01", "Partition_23", "Partition_46"]

    def test_index_all_indexes_every_file_recursively(self, tmp_path):
        self._build_vault(tmp_path)
        store = VectorStore(data_dir=tmp_path / "vec")
        indexer = VaultIndexer(root=tmp_path, vector_store=store)
        result = indexer.index_all()
        assert isinstance(result, VaultIndexResult)
        # Indexed: alpha.md, core.py, data.json, binary.dat = 4
        assert result.files_indexed == 4
        assert set(result.partitions_seen) == {
            "Partition_01",
            "Partition_23",
            "Partition_46",
        }
        # No file from Partition_47 / OtherFolder.
        for doc_id in store.all_ids():
            assert "Partition_47" not in doc_id
            assert "OtherFolder" not in doc_id
        # Metadata is populated.
        rec = store.get("vault:Partition_01/alpha.md")
        assert rec is not None
        assert rec.metadata["partition"] == "Partition_01"

    def test_index_all_truncates_oversize_files(self, tmp_path):
        (tmp_path / "Partition_01").mkdir()
        big = tmp_path / "Partition_01" / "big.md"
        big.write_text("A" * 5000, encoding="utf-8")

        store = VectorStore(data_dir=tmp_path / "vec")
        indexer = VaultIndexer(root=tmp_path, vector_store=store, max_bytes=1000)
        indexer.index_all()
        rec = store.get("vault:Partition_01/big.md")
        assert rec is not None
        assert rec.metadata["truncated"] is True
        assert len(rec.text) == 1000

    def test_handles_missing_root_gracefully(self, tmp_path):
        indexer = VaultIndexer(
            root=tmp_path / "does-not-exist",
            vector_store=VectorStore(data_dir=tmp_path),
        )
        result = indexer.index_all()
        assert result.files_indexed == 0
        assert result.partitions_seen == []


# ---------------------------------------------------------------------------
# FaissVectorStore (with graceful fallback)
# ---------------------------------------------------------------------------


class TestFaissVectorStore:
    def test_status_reports_backend(self, tmp_path):
        store = FaissVectorStore(data_dir=tmp_path)
        status = store.status()
        assert status["faiss_available"] is faiss_available()
        assert status["backend"] in ("faiss", "linear")
        assert status["persistent"] is True

    def test_query_returns_ranked_results(self, tmp_path):
        store = FaissVectorStore(data_dir=tmp_path)
        store.upsert("a", "vortex trade logs alpha", metadata={"source": "x"})
        store.upsert("b", "chicken soup recipe", metadata={"source": "x"})
        store.upsert("c", "alpha citadel bible", metadata={"source": "x"})
        hits = store.query("alpha", top_k=2)
        assert len(hits) == 2
        ids = [h["doc_id"] for h in hits]
        # Both alpha-bearing docs must appear ahead of the soup recipe.
        assert "b" not in ids[:2]

    def test_persistence_roundtrip(self, tmp_path):
        s1 = FaissVectorStore(data_dir=tmp_path)
        s1.upsert("x", "alpha bridge", metadata={"k": "v"})
        s2 = FaissVectorStore(data_dir=tmp_path)
        assert "x" in s2
        assert s2.get("x").metadata["k"] == "v"

    def test_metadata_filter_applied(self, tmp_path):
        store = FaissVectorStore(data_dir=tmp_path)
        store.upsert("a", "alpha signal", metadata={"source": "A"})
        store.upsert("b", "alpha signal", metadata={"source": "B"})
        hits = store.query("alpha", top_k=5, metadata_filter={"source": "B"})
        assert [h["doc_id"] for h in hits] == ["b"]

    def test_delete_invalidates_index(self, tmp_path):
        store = FaissVectorStore(data_dir=tmp_path)
        store.upsert("x", "alpha")
        assert store.delete("x") is True
        assert store.query("alpha", top_k=1) == []


# ---------------------------------------------------------------------------
# AskServer (/v1/ask)
# ---------------------------------------------------------------------------


class TestAskServer:
    def _engine(self, tmp_path):
        store = VectorStore(data_dir=tmp_path)
        store.upsert(
            "p01",
            "alpha bridge partition logic",
            metadata={"source": "github_crawl", "path": "Partition_01/alpha.md"},
        )
        store.upsert(
            "vortex",
            "vortex trade logs alpha signal",
            metadata={"source": "districts", "path": "Vortex/trade_logs.md"},
        )
        store.upsert(
            "kitchen",
            "chicken soup recipe",
            metadata={"source": "gdrive", "path": "kitchen/recipe.md"},
        )
        return RAGQueryEngine(vector_store=store)

    def test_post_v1_ask_flat_retrieval(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            status, body = _post_json(
                f"{server.url}{ASK_PATH}", {"query": "alpha", "top_k": 2}
            )
            assert status == 200
            assert body["ok"] is True
            assert len(body["hits"]) == 2

    def test_post_v1_ask_cross_domain(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            status, body = _post_json(
                f"{server.url}{ASK_PATH}",
                {
                    "query": "Compare Partition_01 logic with today's Vortex trade logs",
                    "domains": ["partition_01", "vortex"],
                },
            )
            assert status == 200
            assert body["ok"] is True
            answer = body["answer"]
            assert set(answer["domains"]) == {"partition_01", "vortex"}
            assert answer["per_domain"]["partition_01"][0]["doc_id"] == "p01"
            assert answer["per_domain"]["vortex"][0]["doc_id"] == "vortex"
            assert 0.0 < answer["joint_score"] <= 1.0

    def test_post_v1_ask_missing_query_returns_400(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            status, body = _post_json(f"{server.url}{ASK_PATH}", {"top_k": 5})
            assert status == 400
            assert "query" in body["error"]

    def test_post_v1_ask_invalid_domains_returns_400(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            status, body = _post_json(
                f"{server.url}{ASK_PATH}",
                {"query": "x", "domains": [1, 2, 3]},
            )
            assert status == 400

    def test_post_v1_ask_invalid_top_k(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            status, body = _post_json(
                f"{server.url}{ASK_PATH}",
                {"query": "x", "top_k": "many"},
            )
            assert status == 400

    def test_unknown_route_returns_404(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            status, body = _post_json(
                f"{server.url}/v1/unknown", {"query": "x"}
            )
            assert status == 404

    def test_health_endpoint(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            with urllib.request.urlopen(f"{server.url}/health", timeout=5) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                assert resp.status == 200
                assert payload["ok"] is True
                assert "vector_store" in payload["status"]

    def test_invalid_json_returns_400(self, tmp_path):
        with AskServer(engine=self._engine(tmp_path)) as server:
            req = urllib.request.Request(
                f"{server.url}{ASK_PATH}",
                data=b"not-json",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5):
                    pytest.fail("expected 400")
            except urllib.error.HTTPError as exc:
                assert exc.code == 400
