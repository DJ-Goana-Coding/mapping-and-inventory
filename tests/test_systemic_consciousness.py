"""
Tests for the Phase-2 Systemic Consciousness layer:

  - src.storage.vector_store.VectorStore
  - src.ingestion.harvester.Harvester
  - src.api.ingest_server.IngestServer
  - src.query.rag_engine.RAGQueryEngine
  - ingestion.omni_harvest.ignition.OmniHarvestIgnition (vector-store wiring)
"""

import json
import sys
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.omni_harvest import OmniHarvestIgnition
from ingestion.omni_harvest.github_crawler import GithubCrawler
from ingestion.omni_harvest.gdrive_bridge import GDriveBridge
from ingestion.omni_harvest.tia_synapse import TiaSynapse
from ingestion.universal_rag import UniversalRAG
from src.api import IngestServer, INGEST_PATH
from src.ingestion import Harvester, SUPPORTED_EXTENSIONS, PARTITION_COUNT
from src.query import RAGQueryEngine
from src.storage import VectorStore, hash_embed, EMBEDDING_DIM


# ---------------------------------------------------------------------------
# VectorStore
# ---------------------------------------------------------------------------


class TestVectorStore:
    def test_hash_embed_shape_and_norm(self):
        vec = hash_embed("citadel bible nordic matrix")
        assert len(vec) == EMBEDDING_DIM
        # L2 norm ~ 1.
        norm = sum(v * v for v in vec) ** 0.5
        assert norm == pytest.approx(1.0, rel=1e-6)

    def test_hash_embed_empty_input(self):
        assert hash_embed("") == [0.0] * EMBEDDING_DIM
        assert hash_embed("!!!") == [0.0] * EMBEDDING_DIM

    def test_upsert_persists_across_instances(self, tmp_path):
        store1 = VectorStore(data_dir=tmp_path)
        store1.upsert("doc1", "citadel bible", metadata={"source": "test"})
        store1.upsert("doc2", "vortex trade logs", metadata={"source": "test"})

        # New instance should load the same records from disk.
        store2 = VectorStore(data_dir=tmp_path)
        assert len(store2) == 2
        assert "doc1" in store2
        assert store2.get("doc2").metadata["source"] == "test"

    def test_query_ranks_semantic_neighbours_first(self, tmp_path):
        store = VectorStore(data_dir=tmp_path)
        store.upsert("bible", "citadel bible nordic matrix", metadata={"tag": "bible"})
        store.upsert("trade", "vortex trade logs output", metadata={"tag": "trade"})
        store.upsert("misc", "chicken soup recipe", metadata={"tag": "misc"})

        results = store.query("citadel bible", top_k=2)
        assert results[0]["doc_id"] == "bible"
        assert results[0]["score"] > results[1]["score"]

    def test_metadata_filter(self, tmp_path):
        store = VectorStore(data_dir=tmp_path)
        store.upsert("a", "alpha signal", metadata={"source": "A"})
        store.upsert("b", "alpha signal", metadata={"source": "B"})
        hits = store.query("alpha", top_k=5, metadata_filter={"source": "B"})
        assert [h["doc_id"] for h in hits] == ["b"]

    def test_delete(self, tmp_path):
        store = VectorStore(data_dir=tmp_path)
        store.upsert("x", "payload")
        assert store.delete("x") is True
        assert store.delete("x") is False
        assert len(store) == 0


# ---------------------------------------------------------------------------
# Harvester
# ---------------------------------------------------------------------------


class TestHarvester:
    def test_archivable_extensions(self):
        assert Harvester.is_archivable("CITADEL_BIBLE.md")
        assert Harvester.is_archivable("src/main.py")
        assert Harvester.is_archivable("data/config.JSON")
        assert not Harvester.is_archivable("binary.bin")
        assert not Harvester.is_archivable("image.png")
        assert SUPPORTED_EXTENSIONS == (".py", ".md", ".json")
        assert PARTITION_COUNT == 46

    def test_harvest_archives_filters_and_prioritises(self, tmp_path):
        def fetcher(owner_repo, ref, token):
            return [
                {"path": "CITADEL_BIBLE.md", "type": "blob", "size": 10},
                {"path": "Partition_01/alpha.py", "type": "blob", "size": 20},
                {"path": "Partition_46/omega.json", "type": "blob", "size": 30},
                {"path": "docs/image.png", "type": "blob", "size": 40},
                {"path": "README.md", "type": "blob", "size": 50},
            ]

        store = VectorStore(data_dir=tmp_path / "vec")
        rag = UniversalRAG(output_dir=tmp_path / "rag")
        harvester = Harvester(
            repos=["a/b"],
            token="tok",
            fetcher=fetcher,
            universal_rag=rag,
            vector_store=store,
        )
        result = harvester.harvest()
        assert result.total_documents == 5
        # Drops the .png file.
        assert result.archived_documents == 4
        # Bible + Partition_01 + Partition_46.
        assert result.priority_documents == 3
        assert result.vector_records == 4
        # Persistence: records are in the vector store.
        assert len(store) == 4

    def test_partition_regex_covers_all_46(self):
        harvester = Harvester(repos=["a/b"], fetcher=lambda *_: [])
        for n in range(1, 47):
            assert harvester._crawler.is_priority(f"Partition_{n:02d}/x.md")
        # Partition_47 is out-of-range for this directive.
        assert not harvester._crawler.is_priority("Partition_47/x.md")

    def test_body_fetcher_is_used_when_provided(self, tmp_path):
        def fetcher(owner_repo, ref, token):
            return [{"path": "README.md", "type": "blob"}]

        def body_fetcher(repo, path, token):
            return f"BODY::{repo}::{path}"

        store = VectorStore(data_dir=tmp_path / "vec")
        harvester = Harvester(
            repos=["x/y"],
            fetcher=fetcher,
            body_fetcher=body_fetcher,
            universal_rag=UniversalRAG(output_dir=tmp_path / "rag"),
            vector_store=store,
        )
        harvester.harvest()
        rec = store.get("repo:x/y:README.md")
        assert rec is not None
        assert "BODY::x/y::README.md" in rec.text


# ---------------------------------------------------------------------------
# IngestServer (/v1/ingest)
# ---------------------------------------------------------------------------


def _post_json(url: str, payload):
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


class TestIngestServer:
    def test_post_v1_ingest_processes_telemetry(self):
        with IngestServer() as server:
            status, body = _post_json(
                f"{server.url}{INGEST_PATH}",
                {
                    "source": "s10",
                    "kind": "hardware.json",
                    "data": {"nodes": {"node_01_s10": {"battery_pct": 88}}},
                },
            )
            assert status == 200
            assert body["ok"] is True
            assert body["record"]["updates"] == ["node_01_s10"]
            assert server.harvester.hardware.get_node("node_01_s10")["battery_pct"] == 88

    def test_post_invalid_json_returns_400(self):
        with IngestServer() as server:
            req = urllib.request.Request(
                f"{server.url}{INGEST_PATH}",
                data=b"not-json",
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    pytest.fail(f"expected 400 error, got {resp.status}")
            except urllib.error.HTTPError as exc:
                assert exc.code == 400

    def test_post_unknown_source_returns_400(self):
        with IngestServer() as server:
            status, body = _post_json(
                f"{server.url}{INGEST_PATH}",
                {"source": "ghost", "kind": "hardware.json", "data": {"nodes": {}}},
            )
            assert status == 400
            assert "ghost" in body["error"]

    def test_unknown_route_returns_404(self):
        with IngestServer() as server:
            status, body = _post_json(
                f"{server.url}/v1/unknown", {"source": "s10", "kind": "hardware.json", "data": {}}
            )
            assert status == 404

    def test_health_endpoint(self):
        with IngestServer() as server:
            with urllib.request.urlopen(f"{server.url}/health", timeout=5) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                assert resp.status == 200
                assert body["ok"] is True
                assert body["status"]["supported_kinds"]


# ---------------------------------------------------------------------------
# RAGQueryEngine (Cross-Domain Inference)
# ---------------------------------------------------------------------------


class TestRAGQueryEngine:
    def _build_engine(self, tmp_path):
        store = VectorStore(data_dir=tmp_path)
        store.upsert(
            "partition01:alpha",
            "alpha bridge signal partition logic",
            metadata={"source": "github_crawl", "path": "Partition_01/alpha.md"},
        )
        store.upsert(
            "vortex:today",
            "vortex trade logs alpha signal bridge",
            metadata={"source": "districts", "path": "Vortex/trade_logs.md"},
        )
        store.upsert(
            "unrelated:doc",
            "chicken soup recipe",
            metadata={"source": "gdrive", "path": "kitchen/recipe.md"},
        )
        return RAGQueryEngine(vector_store=store)

    def test_retrieve_ranks_vector_store_results(self, tmp_path):
        engine = self._build_engine(tmp_path)
        hits = engine.retrieve("alpha signal", top_k=2)
        assert hits
        ids = [h["doc_id"] for h in hits]
        assert "partition01:alpha" in ids or "vortex:today" in ids

    def test_cross_domain_inference_partitions_and_vortex(self, tmp_path):
        engine = self._build_engine(tmp_path)
        answer = engine.cross_domain_inference(
            "Compare Partition_01 logic with today's Vortex trade logs",
            domains=["partition_01", "vortex"],
        )
        assert set(answer.domains) == {"partition_01", "vortex"}
        assert answer.per_domain["partition_01"], "expected a partition_01 hit"
        assert answer.per_domain["vortex"], "expected a vortex hit"
        assert answer.per_domain["partition_01"][0]["doc_id"] == "partition01:alpha"
        assert answer.per_domain["vortex"][0]["doc_id"] == "vortex:today"
        assert 0.0 < answer.joint_score <= 1.0

    def test_cross_domain_accepts_freetext_predicates(self, tmp_path):
        engine = self._build_engine(tmp_path)
        answer = engine.cross_domain_inference(
            "alpha signal", domains=["kitchen"],  # free-text: matches recipe path
        )
        assert answer.per_domain["kitchen"][0]["doc_id"] == "unrelated:doc"

    def test_cross_domain_requires_at_least_one_domain(self, tmp_path):
        engine = self._build_engine(tmp_path)
        with pytest.raises(ValueError):
            engine.cross_domain_inference("x", domains=[])

    def test_answer_as_dict_is_json_serialisable(self, tmp_path):
        engine = self._build_engine(tmp_path)
        answer = engine.cross_domain_inference(
            "alpha", domains=["partition_01"],
        )
        json.dumps(answer.as_dict())  # should not raise


# ---------------------------------------------------------------------------
# OmniHarvestIgnition wired with the persistent VectorStore
# ---------------------------------------------------------------------------


class TestIgnitionVectorStoreWiring:
    def test_tick_persists_every_byte_into_vector_store(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path / "rag")
        crawler = GithubCrawler(
            repos=["a/b"],
            fetcher=lambda *_: [
                {"path": "CITADEL_BIBLE.md", "type": "blob"},
                {"path": "src/main.py", "type": "blob"},
            ],
            universal_rag=rag,
        )
        bridge = GDriveBridge(
            lister=lambda folder: [{"name": "scroll.md", "content": "alpha"}],
            universal_rag=rag,
        )
        synapse = TiaSynapse(source_dirs=[])
        store = VectorStore(data_dir=tmp_path / "vec")
        ignition = OmniHarvestIgnition(
            universal_rag=rag,
            github_crawler=crawler,
            gdrive_bridge=bridge,
            tia_synapse=synapse,
            vector_store=store,
            telemetry_source=lambda: iter(
                [
                    {
                        "source": "oppo-node",
                        "kind": "hardware.json",
                        "data": {"nodes": {"node_probe": {"label": "probe"}}},
                    }
                ]
            ),
            sleeper=lambda _: None,
        )
        result = ignition.tick()
        # 2 crawled + 1 telemetry node + 1 gdrive = 4 vector records.
        assert result.vector_records == 4
        assert len(store) == 4
        # Persistence roundtrip.
        store2 = VectorStore(data_dir=tmp_path / "vec")
        assert len(store2) == 4
