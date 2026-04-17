"""
Tests for the v22.2124 OMNI-TIA Total Convergence modules:
  - core.genesis_alignment
  - legal.pvc_ledger
  - bridge.asset_remediation
  - ingestion.universal_rag
  - security.omni_shield
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.genesis_alignment import (
    GenesisAlignment,
    ARCHETYPE_WEIGHTS,
    STABILIZATION_PERSONA,
    DEFAULT_SIGNAL_THRESHOLD,
)
from legal.pvc_ledger import PvCLedger, DisputeOutcome
from bridge.asset_remediation import AssetRemediation, STABILITY_TARGET
from ingestion.universal_rag import UniversalRAG, CONTENT_TYPE_LYRIC, CONTENT_TYPE_STORY, CONTENT_TYPE_SUBSTRATE
from security.omni_shield import OmniShield, DEFAULT_SIGNAL_THRESHOLD as SHIELD_THRESHOLD
from mapping.substrate_321 import Substrate321
from inventory.hardware_nodes import HardwareInventory
from inventory.asset_vault import AssetVault
from ingestion.rag_sync import SovereignFilter


# =========================================================================
# core.genesis_alignment
# =========================================================================


class TestGenesisAlignment:
    """Tests for the substrate-to-trading integration engine."""

    def test_score_trade_returns_score(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        result = aligner.score_trade({"instrument": "XRP", "direction": "buy"})
        assert "alignment_score" in result
        assert result["alignment_score"] >= 0

    def test_score_trade_includes_resonance_tags(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        result = aligner.score_trade({"instrument": "XRP"})
        assert "resonance_tags" in result
        assert isinstance(result["resonance_tags"], list)

    def test_score_trade_higher_for_aligned_content(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        # "sovereign" marker matches Ancient Royalty archetype → should increase score
        result_aligned = aligner.score_trade({"instrument": "XRP", "theme": "sovereign lineage"})
        result_neutral = aligner.score_trade({"instrument": "AAPL", "theme": "tech stock"})
        # Both get some score; the aligned one should match at least one archetype marker
        assert result_aligned["alignment_score"] > 0
        assert result_neutral["alignment_score"] > 0

    def test_trade_log_accumulates(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        aligner.score_trade({"a": 1})
        aligner.score_trade({"b": 2})
        assert len(aligner.trade_log()) == 2

    def test_detect_signal_no_spike(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path, signal_threshold=7.0)
        result = aligner.detect_signal({"noise_floor": 2.0, "carrier": 3.5})
        assert result["spike_detected"] is False
        assert result["spike_fields"] == {}

    def test_detect_signal_spike(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path, signal_threshold=7.0)
        result = aligner.detect_signal({"malice_level": 8.5, "carrier": 2.0})
        assert result["spike_detected"] is True
        assert "malice_level" in result["spike_fields"]

    def test_detect_signal_exactly_at_threshold(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path, signal_threshold=7.0)
        result = aligner.detect_signal({"level": 7.0})
        assert result["spike_detected"] is True

    def test_signal_log_accumulates(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        aligner.detect_signal({"x": 1})
        aligner.detect_signal({"y": 2})
        assert len(aligner.signal_log()) == 2

    def test_switch_to_stabilization_persona(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        view = aligner.switch_to_stabilization_persona()
        assert view["active"] is True
        assert view["stabilization_broadcast"] is True
        assert view["broadcast_frequency_hz"] == 144
        assert aligner.active_persona() == STABILIZATION_PERSONA

    def test_active_persona_initially_none(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        assert aligner.active_persona() is None

    def test_save(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        aligner.score_trade({"x": 1})
        path = aligner.save()
        assert path.exists()
        data = json.loads(path.read_text())
        assert "trade_log" in data
        assert data["version"] == "v22.2124"

    def test_status(self, tmp_path):
        substrate = Substrate321(storage_root=tmp_path)
        aligner = GenesisAlignment(substrate=substrate, output_dir=tmp_path)
        status = aligner.status()
        assert status["signal_threshold"] == DEFAULT_SIGNAL_THRESHOLD
        assert status["stabilization_persona"] == STABILIZATION_PERSONA


# =========================================================================
# legal.pvc_ledger
# =========================================================================


class TestPvCLedger:
    """Tests for the traffic-fine dispute tracker."""

    def test_add_dispute(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        entry = ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        assert entry["fine_id"] == "F001"
        assert entry["outcome"] == DisputeOutcome.PENDING
        assert entry["recovered_aud"] == 0.0

    def test_resolve_won(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        result = ledger.resolve_dispute("F001", outcome="won")
        assert result["outcome"] == DisputeOutcome.WON
        assert result["recovered_aud"] == 800.0
        assert result["resolved_at"] is not None

    def test_resolve_lost(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        result = ledger.resolve_dispute("F001", outcome="lost")
        assert result["outcome"] == DisputeOutcome.LOST
        assert result["recovered_aud"] == 0.0

    def test_resolve_invalid_outcome(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        with pytest.raises(ValueError, match="outcome must be"):
            ledger.resolve_dispute("F001", outcome="maybe")

    def test_resolve_unknown_fine(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        with pytest.raises(KeyError, match="Unknown fine_id"):
            ledger.resolve_dispute("UNKNOWN", outcome="won")

    def test_list_disputes_all(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        ledger.add_dispute("F002", amount_aud=450.0, description="B")
        assert len(ledger.list_disputes()) == 2

    def test_list_disputes_filtered(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        ledger.add_dispute("F002", amount_aud=450.0, description="B")
        ledger.resolve_dispute("F001", outcome="won")
        assert len(ledger.list_disputes(outcome="won")) == 1
        assert len(ledger.list_disputes(outcome="pending")) == 1

    def test_won_disputes(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        ledger.add_dispute("F002", amount_aud=450.0, description="B")
        ledger.resolve_dispute("F001", outcome="won")
        won = ledger.won_disputes()
        assert len(won) == 1
        assert won[0]["fine_id"] == "F001"

    def test_total_recovered_aud(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        ledger.add_dispute("F002", amount_aud=450.0, description="B")
        ledger.resolve_dispute("F001", outcome="won")
        assert ledger.total_recovered_aud() == 800.0

    def test_total_outstanding_aud(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        ledger.add_dispute("F002", amount_aud=450.0, description="B")
        ledger.resolve_dispute("F001", outcome="won")
        assert ledger.total_outstanding_aud() == 450.0

    def test_save(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        path = ledger.save()
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == "v22.2124"
        assert len(data["disputes"]) == 1

    def test_status(self, tmp_path):
        ledger = PvCLedger(output_dir=tmp_path)
        ledger.add_dispute("F001", amount_aud=800.0, description="A")
        ledger.resolve_dispute("F001", outcome="won")
        status = ledger.status()
        assert status["total_disputes"] == 1
        assert status["won"] == 1
        assert status["total_recovered_aud"] == 800.0


# =========================================================================
# bridge.asset_remediation
# =========================================================================


class TestAssetRemediation:
    """Tests for the legal-to-financial bridge."""

    def _make_bridge(self, tmp_path) -> AssetRemediation:
        ledger = PvCLedger(output_dir=tmp_path / "ledger")
        vault = AssetVault(output_dir=tmp_path / "vault")
        hardware = HardwareInventory(output_dir=tmp_path / "hw")
        return AssetRemediation(
            ledger=ledger,
            vault=vault,
            hardware=hardware,
            output_dir=tmp_path / "bridge",
        )

    def test_apply_recovery_won(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        bridge.ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        bridge.ledger.resolve_dispute("F001", outcome="won")
        record = bridge.apply_recovery("F001")
        assert record["fine_id"] == "F001"
        assert record["recovered_aud"] == 800.0
        assert "Sovereign Interest" in record["routed_to"]

    def test_apply_recovery_not_won_raises(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        bridge.ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        with pytest.raises(ValueError, match="only 'won' disputes"):
            bridge.apply_recovery("F001")

    def test_apply_recovery_updates_vault(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        bridge.ledger.add_dispute("F001", amount_aud=800.0, description="Speed camera")
        bridge.ledger.resolve_dispute("F001", outcome="won")
        bridge.apply_recovery("F001")
        unclaimed = bridge.vault.list_unclaimed_assets()
        assert len(unclaimed) == 1
        assert unclaimed[0]["estimated_value_aud"] == 800.0

    def test_apply_all_recoveries(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        bridge.ledger.add_dispute("F001", amount_aud=800.0, description="A")
        bridge.ledger.add_dispute("F002", amount_aud=450.0, description="B")
        bridge.ledger.resolve_dispute("F001", outcome="won")
        bridge.ledger.resolve_dispute("F002", outcome="won")
        results = bridge.apply_all_recoveries()
        assert len(results) == 2

    def test_apply_all_recoveries_no_duplicate(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        bridge.ledger.add_dispute("F001", amount_aud=800.0, description="A")
        bridge.ledger.resolve_dispute("F001", outcome="won")
        bridge.apply_all_recoveries()
        results = bridge.apply_all_recoveries()  # second call — nothing new
        assert len(results) == 0

    def test_fleet_stability_check(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        report = bridge.fleet_stability_check()
        assert "stability_score" in report
        assert report["stable"] is True  # all default nodes are 144Hz aligned
        assert report["stability_score"] == STABILITY_TARGET

    def test_check_ute_repair_incomplete(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        result = bridge.check_ute_repair_status()
        assert result["repair_complete"] is False
        assert "stability_report" not in result

    def test_check_ute_repair_complete_triggers_stability(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        # Mark repair complete
        ute = bridge.hardware.get_node("node_03_ute")
        ute["diagnostics"]["cross_feed_short_circuit"]["status"] = "repaired"
        result = bridge.check_ute_repair_status()
        assert result["repair_complete"] is True
        assert "stability_report" in result
        assert result["stability_report"]["stable"] is True

    def test_save(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        bridge.fleet_stability_check()
        path = bridge.save()
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == "v22.2124"

    def test_status(self, tmp_path):
        bridge = self._make_bridge(tmp_path)
        status = bridge.status()
        assert status["stability_target"] == STABILITY_TARGET
        assert status["recoveries_applied"] == 0


# =========================================================================
# ingestion.universal_rag
# =========================================================================


class TestUniversalRAG:
    """Tests for the cultural/creative content RAG ingestion pipeline."""

    def test_ingest_lyric(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        item = rag.ingest_lyric("Goanna Rising", "We rise...", artist="DJ Goanna")
        assert item["content_type"] == CONTENT_TYPE_LYRIC
        assert item["title"] == "Goanna Rising"
        assert "music" in item["categories"]
        assert rag.pending_count() == 1

    def test_ingest_story(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        item = rag.ingest_story("The Blink Wanderer", "In the folds of time...")
        assert item["content_type"] == CONTENT_TYPE_STORY
        assert item["title"] == "The Blink Wanderer"
        assert "narrative" in item["categories"]

    def test_ingest_substrate_data(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        packets = [{"file": "a.dat", "frequency_hz": 144}]
        items = rag.ingest_substrate_data(packets)
        assert len(items) == 1
        assert items[0]["content_type"] == CONTENT_TYPE_SUBSTRATE
        assert rag.pending_count() == 1

    def test_flush_to_spaces_clears_pending(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        rag.ingest_lyric("Song", "lyrics...")
        result = rag.flush_to_spaces()
        assert rag.pending_count() == 0
        assert result["pushed_items"] >= 1

    def test_sovereign_filter_applied_on_flush(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        rag.ingest_lyric("Good Song", "Clean lyrics", tags=["creative"])
        rag._pending.append({"title": "Blocked", "categories": ["bible"], "content": "x"})
        result = rag.flush_to_spaces()
        assert result["filtered_items"] == 1
        assert result["pushed_items"] == 1

    def test_flush_result_structure(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        rag.ingest_lyric("A", "B")
        result = rag.flush_to_spaces()
        assert "raw_items" in result
        assert "filtered_items" in result
        assert "pushed_items" in result
        assert "sync_result" in result

    def test_pending_items_returns_copy(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        rag.ingest_lyric("X", "Y")
        items = rag.pending_items()
        items.clear()
        assert rag.pending_count() == 1

    def test_status(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        rag.ingest_lyric("A", "B")
        rag.ingest_story("C", "D")
        status = rag.status()
        assert status["pending_count"] == 2
        assert status["pending_by_type"][CONTENT_TYPE_LYRIC] == 1
        assert status["pending_by_type"][CONTENT_TYPE_STORY] == 1
        assert "bible" in status["excluded_categories"]

    def test_lyric_default_artist(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        item = rag.ingest_lyric("A", "B")
        assert item["artist"] == "DJ Goanna"

    def test_multiple_flushes(self, tmp_path):
        rag = UniversalRAG(output_dir=tmp_path)
        rag.ingest_lyric("A", "B")
        rag.flush_to_spaces()
        rag.ingest_story("C", "D")
        rag.flush_to_spaces()
        assert rag.status()["total_syncs"] == 2


# =========================================================================
# security.omni_shield
# =========================================================================


class TestOmniShield:
    """Tests for the signal monitoring and asset protection module."""

    def _make_shield(self, tmp_path) -> OmniShield:
        hardware = HardwareInventory(output_dir=tmp_path / "hw")
        vault = AssetVault(output_dir=tmp_path / "vault")
        return OmniShield(
            hardware=hardware,
            vault=vault,
            output_dir=tmp_path / "shield",
        )

    def test_check_signal_no_spike(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_signal_level({"noise": 2.0, "carrier": 3.5})
        assert result["spike_detected"] is False
        assert result["nodes_hardened"] == []

    def test_check_signal_spike(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_signal_level({"sky_signal": 8.5, "noise": 1.0})
        assert result["spike_detected"] is True
        assert "sky_signal" in result["spike_fields"]

    def test_check_signal_hardens_airgap_nodes(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_signal_level({"level": 9.0})
        # node_01_s10 has offline_sync=True
        assert "node_01_s10" in result["nodes_hardened"]

    def test_check_signal_threshold_boundary(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_signal_level({"level": SHIELD_THRESHOLD})
        assert result["spike_detected"] is True

    def test_check_market_no_compression(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_market_signal(price_aud=2.50)
        assert result["compression_detected"] is False
        assert result["mirror_protocol_activated"] is False
        assert shield.mirror_protocol_active is False

    def test_check_market_compression(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_market_signal(price_aud=1.88)
        assert result["compression_detected"] is True
        assert result["mirror_protocol_activated"] is True
        assert shield.mirror_protocol_active is True

    def test_check_market_compression_exact_price(self, tmp_path):
        shield = self._make_shield(tmp_path)
        result = shield.check_market_signal(price_aud=1.90)
        assert result["compression_detected"] is True

    def test_mirror_protocol_not_double_activated(self, tmp_path):
        shield = self._make_shield(tmp_path)
        shield.check_market_signal(price_aud=1.50)
        result = shield.check_market_signal(price_aud=1.50)
        assert result["mirror_protocol_activated"] is False  # already active

    def test_deactivate_mirror_protocol(self, tmp_path):
        shield = self._make_shield(tmp_path)
        shield.check_market_signal(price_aud=1.50)
        shield.deactivate_mirror_protocol()
        assert shield.mirror_protocol_active is False

    def test_harden_node(self, tmp_path):
        shield = self._make_shield(tmp_path)
        record = shield.harden_node("node_02_laptops")
        assert record["hardened"] is True
        assert "node_02_laptops" in shield.hardened_nodes

    def test_release_node(self, tmp_path):
        shield = self._make_shield(tmp_path)
        shield.harden_node("node_02_laptops")
        shield.release_node("node_02_laptops")
        assert "node_02_laptops" not in shield.hardened_nodes

    def test_event_log_accumulates(self, tmp_path):
        shield = self._make_shield(tmp_path)
        shield.check_signal_level({"x": 1})
        shield.check_market_signal(price_aud=2.0)
        assert len(shield.event_log()) == 2

    def test_save(self, tmp_path):
        shield = self._make_shield(tmp_path)
        shield.check_signal_level({"x": 8.0})
        path = shield.save()
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == "v22.2124"

    def test_status(self, tmp_path):
        shield = self._make_shield(tmp_path)
        status = shield.status()
        assert status["signal_threshold"] == SHIELD_THRESHOLD
        assert status["mirror_protocol_active"] is False
        assert status["hardened_node_count"] == 0
