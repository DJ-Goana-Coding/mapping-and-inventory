"""
Tests for the OMNI-HARVEST IGNITION (9,293 STABILITY) orchestrator and its
four subsystems:

  - ingestion.omni_harvest.github_crawler
  - ingestion.omni_harvest.physical_harvest
  - ingestion.omni_harvest.gdrive_bridge
  - ingestion.omni_harvest.tia_synapse
  - ingestion.omni_harvest.ignition
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ingestion.universal_rag import UniversalRAG
from ingestion.omni_harvest import (
    CITADEL_REPOS,
    GithubCrawler,
    PhysicalHarvest,
    GDriveBridge,
    TiaSynapse,
    OmniHarvestIgnition,
    STABILITY_TARGET,
)
from ingestion.omni_harvest.physical_harvest import TelemetryError


# ---------------------------------------------------------------------------
# GithubCrawler
# ---------------------------------------------------------------------------


class TestGithubCrawler:
    def test_default_repo_list_has_twelve_entries(self):
        assert len(CITADEL_REPOS) == 12

    def test_priority_patterns_match_directive_files(self):
        crawler = GithubCrawler(repos=["x/y"], fetcher=lambda *_: [])
        assert crawler.is_priority("docs/CITADEL_BIBLE.md")
        assert crawler.is_priority("V19_NORDIC_MATRIX.md")
        assert crawler.is_priority("Partition_01/notes.txt")
        assert crawler.is_priority("some/Partition_42/deep.md")
        assert not crawler.is_priority("README.md")
        assert not crawler.is_priority("src/main.py")

    def test_crawl_all_orders_priority_documents_first(self):
        def fake_fetcher(owner_repo, ref, token):
            return [
                {"path": "src/app.py", "type": "blob", "size": 10},
                {"path": "CITADEL_BIBLE.md", "type": "blob", "size": 20},
                {"path": "Partition_03/plan.md", "type": "blob", "size": 30},
                {"path": "README.md", "type": "blob", "size": 40},
            ]

        crawler = GithubCrawler(repos=["a/b", "c/d"], fetcher=fake_fetcher, token="tok")
        docs = crawler.crawl_all()

        assert len(docs) == 8
        priority_count = sum(1 for d in docs if d.priority)
        assert priority_count == 4  # 2 repos * 2 priority files

        # The first N documents must all be priority.
        for doc in docs[:priority_count]:
            assert doc.priority
        for doc in docs[priority_count:]:
            assert not doc.priority

        status = crawler.status()
        assert status["repo_count"] == 2
        assert status["token_present"] is True
        assert status["last_priority_count"] == 4

    def test_crawl_records_unavailable_repos(self):
        crawler = GithubCrawler(repos=["offline/one"], fetcher=lambda *_: [])
        docs = crawler.crawl_all()
        assert docs == []
        assert crawler.status()["unavailable_repos"] == ["offline/one"]

    def test_crawl_feeds_universal_rag_when_provided(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path / "rag")
        crawler = GithubCrawler(
            repos=["a/b"],
            fetcher=lambda *_: [{"path": "CITADEL_BIBLE.md", "type": "blob"}],
            universal_rag=rag,
        )
        crawler.crawl_all()
        assert rag.pending_count() == 1
        pending = rag.pending_items()[0]
        assert "CITADEL_BIBLE.md" in pending["title"]
        assert "priority" in pending["categories"]


# ---------------------------------------------------------------------------
# PhysicalHarvest
# ---------------------------------------------------------------------------


class TestPhysicalHarvest:
    def test_process_hardware_json_adds_new_node(self):
        harvester = PhysicalHarvest()
        before = len(harvester.hardware.list_nodes())

        record = harvester.process_telemetry(
            {
                "source": "oppo-node",
                "kind": "hardware.json",
                "data": {
                    "nodes": {
                        "node_04_oppo": {
                            "label": "Oppo Node",
                            "type": "mobile",
                            "role": "Librarian",
                        }
                    }
                },
            }
        )
        assert record["updates"] == ["node_04_oppo"]
        after_nodes = harvester.hardware.list_nodes()
        assert len(after_nodes) == before + 1
        assert any(n["id"] == "node_04_oppo" for n in after_nodes)

    def test_process_hardware_json_merges_existing_node(self):
        harvester = PhysicalHarvest()
        harvester.process_telemetry(
            {
                "source": "s10",
                "kind": "hardware.json",
                "data": {"nodes": {"node_01_s10": {"battery_pct": 77}}},
            }
        )
        node = harvester.hardware.get_node("node_01_s10")
        assert node["battery_pct"] == 77
        # Original fields preserved.
        assert node["chipset"] == "Exynos 9820"

    def test_process_assets_json_registers_assets(self):
        harvester = PhysicalHarvest()
        record = harvester.process_telemetry(
            {
                "source": "oppo-node",
                "kind": "assets.json",
                "data": {
                    "assets": [
                        {"id": "cable_001", "kind": "usb-c", "length_m": 2},
                        {"id": "drive_007", "kind": "ssd", "size_gb": 1024},
                    ]
                },
            }
        )
        assert record["updates"] == ["cable_001", "drive_007"]

    def test_accepts_raw_json_string_payload(self):
        harvester = PhysicalHarvest()
        payload = json.dumps(
            {
                "source": "s10",
                "kind": "hardware.json",
                "data": {"nodes": {"node_99_probe": {"label": "probe"}}},
            }
        )
        record = harvester.process_telemetry(payload)
        assert record["updates"] == ["node_99_probe"]

    def test_rejects_unknown_source(self):
        harvester = PhysicalHarvest()
        with pytest.raises(TelemetryError):
            harvester.process_telemetry(
                {"source": "ghost", "kind": "hardware.json", "data": {"nodes": {}}}
            )

    def test_rejects_unknown_kind(self):
        harvester = PhysicalHarvest()
        with pytest.raises(TelemetryError):
            harvester.process_telemetry(
                {"source": "s10", "kind": "mystery.json", "data": {}}
            )

    def test_listen_iterates_through_websocket_factory(self):
        messages = [
            {
                "source": "s10",
                "kind": "hardware.json",
                "data": {"nodes": {"node_01_s10": {"battery_pct": 55}}},
            },
            {
                "source": "oppo-node",
                "kind": "assets.json",
                "data": {"assets": [{"id": "widget_1"}]},
            },
        ]
        harvester = PhysicalHarvest(websocket_factory=lambda url: iter(messages))
        processed = harvester.listen("ws://example/telemetry")
        assert len(processed) == 2
        assert processed[0]["kind"] == "hardware.json"

    def test_listen_without_factory_raises(self):
        harvester = PhysicalHarvest()
        with pytest.raises(RuntimeError):
            harvester.listen("ws://x")


# ---------------------------------------------------------------------------
# GDriveBridge
# ---------------------------------------------------------------------------


class TestGDriveBridge:
    def test_ingests_documents_from_custom_lister(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path / "rag")
        items = [
            {"name": "scroll_01.md", "mime_type": "text/markdown", "content": "alpha"},
            {"name": "scroll_02.txt", "mime_type": "text/plain", "content": "beta"},
        ]
        bridge = GDriveBridge(lister=lambda folder: items, universal_rag=rag)
        queued = bridge.ingest_archives()

        assert len(queued) == 2
        titles = {q["title"] for q in queued}
        assert titles == {"scroll_01.md", "scroll_02.txt"}
        assert rag.pending_count() == 2
        assert all("gdrive" in q["categories"] for q in queued)
        assert bridge.status()["last_ingested_count"] == 2

    def test_skips_entries_without_name(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path / "rag")
        bridge = GDriveBridge(
            lister=lambda folder: [{"name": "", "content": "x"}, {"content": "y"}],
            universal_rag=rag,
        )
        assert bridge.ingest_archives() == []


# ---------------------------------------------------------------------------
# TiaSynapse
# ---------------------------------------------------------------------------


class TestTiaSynapse:
    def test_index_and_query_against_synthetic_sources(self, tmp_path):
        vault = tmp_path / "Archive_Vault"
        districts = tmp_path / "Districts"
        forever = tmp_path / "Forever_Learning"
        vault.mkdir()
        districts.mkdir()
        forever.mkdir()

        (vault / "master.md").write_text("citadel bridge signal")
        (districts / "d01.md").write_text("district command signal resonance")
        (forever / "neuron.json").write_text('{"tag":"signal"}')

        synapse = TiaSynapse(source_dirs=[vault, districts, forever])
        status = synapse.index()

        assert status["document_count"] == 3
        assert set(status["sources"]) == {
            "Archive_Vault",
            "Districts",
            "Forever_Learning",
        }

        results = synapse.query("signal", top_k=5)
        assert results, "expected query results for token 'signal'"
        assert results[0]["source"] in {"Archive_Vault", "Districts", "Forever_Learning"}

    def test_on_new_data_updates_live_index(self):
        synapse = TiaSynapse(source_dirs=[])
        synapse.index()
        assert synapse.document_count() == 0

        synapse.on_new_data(
            doc_id="crawl:x/y:CITADEL_BIBLE.md",
            text="citadel bible nordic matrix",
            source="github_crawl",
        )
        assert synapse.document_count() == 1

        # Re-registering the same doc_id must not duplicate.
        synapse.on_new_data(
            doc_id="crawl:x/y:CITADEL_BIBLE.md",
            text="citadel bible updated",
            source="github_crawl",
        )
        assert synapse.document_count() == 1

        results = synapse.query("bible")
        assert results and results[0]["doc_id"] == "crawl:x/y:CITADEL_BIBLE.md"


# ---------------------------------------------------------------------------
# OmniHarvestIgnition
# ---------------------------------------------------------------------------


def _fake_gh_fetcher(owner_repo, ref, token):
    # One priority + one standard file per repo.
    return [
        {"path": "CITADEL_BIBLE.md", "type": "blob", "size": 10},
        {"path": "src/main.py", "type": "blob", "size": 20},
    ]


def _build_ignition(tmp_path):
    rag = UniversalRAG(output_dir=tmp_path / "rag")
    crawler = GithubCrawler(
        repos=["a/b", "c/d"],
        fetcher=_fake_gh_fetcher,
        universal_rag=rag,
    )
    gdrive = GDriveBridge(
        lister=lambda folder: [
            {"name": "archive_01.md", "content": "alpha signal"},
        ],
        universal_rag=rag,
    )
    synapse = TiaSynapse(source_dirs=[])
    telemetry_messages = [
        {
            "source": "s10",
            "kind": "hardware.json",
            "data": {"nodes": {"node_probe": {"label": "probe"}}},
        }
    ]
    ignition = OmniHarvestIgnition(
        universal_rag=rag,
        github_crawler=crawler,
        gdrive_bridge=gdrive,
        tia_synapse=synapse,
        telemetry_source=lambda: iter(telemetry_messages),
        sleeper=lambda _: None,
    )
    return ignition


class TestOmniHarvestIgnition:
    def test_stability_target_constant(self):
        assert STABILITY_TARGET == 9293

    def test_single_tick_runs_all_subsystems(self, tmp_path):
        ignition = _build_ignition(tmp_path)
        result = ignition.tick()

        assert result.iteration == 1
        assert result.crawled_documents == 4  # 2 repos * 2 files
        assert result.priority_documents == 2
        assert result.telemetry_packets == 1
        assert result.gdrive_documents == 1
        # 4 crawl docs + 1 telemetry node + 1 gdrive doc
        assert result.synapse_new_documents == 6
        # Flush ran; RAG queue is empty afterwards.
        assert ignition.universal_rag.pending_count() == 0

    def test_run_with_iterations_executes_bounded_loop(self, tmp_path):
        ignition = _build_ignition(tmp_path)
        results = ignition.run(iterations=3, interval_seconds=0)

        assert len(results) == 3
        assert [r.iteration for r in results] == [1, 2, 3]
        status = ignition.status()
        assert status["iterations_completed"] == 3
        assert status["stability_target"] == STABILITY_TARGET
        assert status["subsystems"]["github_crawler"]["repo_count"] == 2

    def test_run_respects_should_continue(self, tmp_path):
        ignition = _build_ignition(tmp_path)
        results = ignition.run(
            iterations=10,
            interval_seconds=0,
            should_continue=lambda ig: ig._iteration < 2,
        )
        # Stops *before* running when predicate is False: 1st call allows tick
        # (0 < 2), 2nd call allows tick (1 < 2), 3rd call blocks (2 < 2 False).
        assert len(results) == 2
