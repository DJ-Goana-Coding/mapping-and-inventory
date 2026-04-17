"""
Tests for the v22.2122 System Decode modules:
  - mapping.substrate_321
  - mapping.regional_nodes
  - inventory.hardware_nodes
  - inventory.asset_vault
  - ingestion.rag_sync
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mapping.substrate_321 import Substrate321, ARCHETYPES, PERSONAS
from mapping.regional_nodes import RegionalNodeMapper, MACKAY_COORDS
from inventory.hardware_nodes import HardwareInventory, DEFAULT_NODES, TARGET_FREQUENCY_HZ
from inventory.asset_vault import AssetVault
from ingestion.rag_sync import RAGSync, SovereignFilter


# =========================================================================
# mapping.substrate_321
# =========================================================================


class TestSubstrate321:
    """Tests for the 321 GB Substrate engine."""

    def test_map_resonance_returns_tags(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        result = engine.map_resonance({"file": "sovereign_data.dat"})
        assert "resonance_tags" in result
        assert "frequency_hz" in result
        assert result["frequency_hz"] == 144

    def test_map_resonance_matches_specific_archetype(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        result = engine.map_resonance({"description": "sovereign lineage record"})
        assert "Ancient Royalty" in result["resonance_tags"]

    def test_map_resonance_defaults_all_archetypes(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        result = engine.map_resonance({"file": "random_data.bin"})
        assert len(result["resonance_tags"]) == len(ARCHETYPES)

    def test_map_resonance_timestamp(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        result = engine.map_resonance({"x": 1})
        assert "mapped_at" in result

    def test_layer_archetype_valid(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        view = engine.layer_archetype("systems_architect")
        assert view["active"] is True
        assert view["focus"] == "infrastructure"
        assert engine.active_persona == "systems_architect"

    def test_layer_archetype_dj_goanna(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        view = engine.layer_archetype("dj_goanna")
        assert view["focus"] == "creative"

    def test_layer_archetype_quant_commander(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        view = engine.layer_archetype("quant_commander")
        assert view["focus"] == "financial"

    def test_layer_archetype_invalid(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        with pytest.raises(ValueError, match="Unknown persona"):
            engine.layer_archetype("nonexistent")

    def test_manifest_accumulates(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        engine.map_resonance({"a": 1})
        engine.map_resonance({"b": 2})
        assert len(engine.get_manifest()) == 2

    def test_save_manifest(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        engine.map_resonance({"test": True})
        path = engine.save_manifest()
        assert path.exists()

    def test_substrate_status(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        status = engine.substrate_status()
        assert status["capacity_gb"] == 321
        assert status["target_frequency_hz"] == 144
        assert status["archetypes_loaded"] == len(ARCHETYPES)
        assert status["personas_loaded"] == len(PERSONAS)

    def test_encrypt_decrypt_roundtrip(self, tmp_path):
        engine = Substrate321(storage_root=tmp_path)
        if engine._fernet is None:
            pytest.skip("cryptography not installed")
        original = b"sovereign data payload"
        encrypted = engine.encrypt_payload(original)
        assert encrypted != original
        assert engine.decrypt_payload(encrypted) == original


# =========================================================================
# mapping.regional_nodes
# =========================================================================


class TestRegionalNodeMapper:
    """Tests for the Mackay/Queensland geospatial mapper."""

    def test_sync_local_toroid(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        state = mapper.sync_local_toroid()
        assert state["field_frequency_hz"] == 144
        assert "aligned" in state
        assert isinstance(state["aligned"], bool)

    def test_pvc_hotspots_seeded(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        spots = mapper.pvc_hotspots()
        assert len(spots) >= 4

    def test_add_pvc_hotspot(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        _ = mapper.pvc_hotspots()  # seed
        before = len(mapper.pvc_hotspots())
        mapper.add_pvc_hotspot(label="Test Camera", lat=-21.2, lon=149.2)
        assert len(mapper.pvc_hotspots()) == before + 1

    def test_add_node(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        before = len(mapper.list_nodes())
        mapper.add_node(node_id="test_node", label="Test", lat=-21.0, lon=149.0)
        assert len(mapper.list_nodes()) == before + 1

    def test_haversine_distance(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        dist = mapper._haversine(-21.15, 149.18, -21.15, 149.18)
        assert dist == 0.0

    def test_haversine_nonzero(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        dist = mapper._haversine(-21.15, 149.18, -21.42, 149.22)
        assert dist > 0

    def test_save_map(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        mapper.sync_local_toroid()
        path = mapper.save_map()
        assert path.exists()
        data = json.loads(path.read_text())
        assert "nodes" in data
        assert "anchor" in data

    def test_status(self, tmp_path):
        mapper = RegionalNodeMapper(output_dir=tmp_path)
        status = mapper.status()
        assert status["anchor"]["region"] == "Mackay, Queensland, Australia"
        assert status["target_frequency_hz"] == 144

    def test_mackay_coords(self):
        assert MACKAY_COORDS["latitude"] == -21.15
        assert MACKAY_COORDS["longitude"] == 149.18


# =========================================================================
# inventory.hardware_nodes
# =========================================================================


class TestHardwareInventory:
    """Tests for the physical hardware fleet tracker."""

    def test_default_nodes_loaded(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        assert len(inv.list_nodes()) == len(DEFAULT_NODES)

    def test_get_node_s10(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        node = inv.get_node("node_01_s10")
        assert node["chipset"] == "Exynos 9820"

    def test_get_node_invalid(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        with pytest.raises(KeyError, match="Unknown node"):
            inv.get_node("nonexistent")

    def test_frequency_check_aligned(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        result = inv.frequency_check("node_01_s10")
        assert result["aligned"] is True
        assert result["measured_hz"] == 144
        assert result["target_hz"] == 144

    def test_frequency_check_all(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        results = inv.frequency_check_all()
        assert len(results) == len(DEFAULT_NODES)
        assert all(r["aligned"] for r in results)

    def test_offline_sync_s10(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        assert inv.offline_sync("node_01_s10") is True

    def test_offline_sync_laptops(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        assert inv.offline_sync("node_02_laptops") is False

    def test_set_offline_sync(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        inv.set_offline_sync("node_02_laptops", True)
        assert inv.offline_sync("node_02_laptops") is True

    def test_add_node(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        inv.add_node("node_04_tablet", {"label": "Tablet", "type": "mobile"})
        assert len(inv.list_nodes()) == len(DEFAULT_NODES) + 1

    def test_log_diagnostic(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        entry = inv.log_diagnostic("node_03_ute", {"event": "short_circuit_test", "result": "pass"})
        assert "timestamp" in entry

    def test_save(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        path = inv.save()
        assert path.exists()
        data = json.loads(path.read_text())
        assert "nodes" in data
        assert data["version"] == "v22.2122"

    def test_status(self, tmp_path):
        inv = HardwareInventory(output_dir=tmp_path)
        status = inv.status()
        assert status["total_nodes"] == len(DEFAULT_NODES)
        assert status["nodes_aligned"] == len(DEFAULT_NODES)
        assert "node_01_s10" in status["offline_capable"]


# =========================================================================
# inventory.asset_vault
# =========================================================================


class TestAssetVault:
    """Tests for the digital asset ledger."""

    def test_xrp_ledger_sync(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        result = vault.xrp_ledger_sync(holdings_xrp=1500.0, price_aud=1.90)
        assert result["asset"] == "XRP"
        assert result["value_aud"] == 2850.0
        assert result["milestones"]["price_1_90"] is True
        assert result["milestones"]["portfolio_510k"] is False

    def test_xrp_milestone_510k(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        result = vault.xrp_ledger_sync(holdings_xrp=300_000.0, price_aud=2.0)
        assert result["milestones"]["portfolio_510k"] is True

    def test_pi_network_node(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        result = vault.pi_network_node(balance_pi=40.56)
        assert result["asset"] == "Pi Network"
        assert result["balance_pi"] == 40.56
        assert result["rpc_status"] == "online"

    def test_domain_bind_node_new(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        result = vault.domain_bind_node("newsite.com.au")
        assert result["domain"] == "newsite.com.au"
        assert len(vault.list_domains()) == 3  # 2 default + 1 new

    def test_domain_bind_node_update(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        vault.domain_bind_node("mackaycrypto.com.au", status="suspended")
        domains = vault.list_domains()
        matched = [d for d in domains if d["domain"] == "mackaycrypto.com.au"]
        assert len(matched) == 1
        assert matched[0]["status"] == "suspended"

    def test_default_domains(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        domains = vault.list_domains()
        names = [d["domain"] for d in domains]
        assert "mackaycrypto.com.au" in names
        assert "qldai.au" in names

    def test_add_unclaimed_asset(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        entry = vault.add_unclaimed_asset(description="Historical ABN reparation", abn="12345678901")
        assert entry["source"] == "ASIC Moneysmart"
        assert entry["status"] == "identified"
        assert len(vault.list_unclaimed_assets()) == 1

    def test_save(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        vault.xrp_ledger_sync(holdings_xrp=100, price_aud=1.50)
        path = vault.save()
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["version"] == "v22.2122"

    def test_status(self, tmp_path):
        vault = AssetVault(output_dir=tmp_path)
        status = vault.status()
        assert status["xrp_synced"] is False
        assert status["domains_registered"] == 2


# =========================================================================
# ingestion.rag_sync
# =========================================================================


class TestSovereignFilter:
    """Tests for the SovereignFilter content gate."""

    def test_default_exclusions(self):
        sf = SovereignFilter()
        assert "bible" in sf.excluded_categories
        assert "ark" in sf.excluded_categories
        assert "bottles" in sf.excluded_categories

    def test_allows_non_excluded(self):
        sf = SovereignFilter()
        assert sf.is_allowed({"categories": ["research"]}) is True

    def test_blocks_excluded(self):
        sf = SovereignFilter()
        assert sf.is_allowed({"categories": ["bible"]}) is False
        assert sf.is_allowed({"categories": ["ark"]}) is False
        assert sf.is_allowed({"categories": ["bottles"]}) is False

    def test_blocks_case_insensitive(self):
        sf = SovereignFilter()
        assert sf.is_allowed({"categories": ["Bible"]}) is False
        assert sf.is_allowed({"categories": ["ARK"]}) is False

    def test_apply_filters_list(self):
        sf = SovereignFilter()
        items = [
            {"name": "a", "categories": ["research"]},
            {"name": "b", "categories": ["bible"]},
            {"name": "c", "categories": ["data"]},
        ]
        result = sf.apply(items)
        assert len(result) == 2
        assert all(i["name"] != "b" for i in result)

    def test_custom_exclusions(self):
        sf = SovereignFilter(excluded={"custom_cat"})
        assert sf.is_allowed({"categories": ["bible"]}) is True
        assert sf.is_allowed({"categories": ["custom_cat"]}) is False

    def test_string_category(self):
        sf = SovereignFilter()
        assert sf.is_allowed({"categories": "bible"}) is False
        assert sf.is_allowed({"categories": "research"}) is True

    def test_no_categories_allowed(self):
        sf = SovereignFilter()
        assert sf.is_allowed({"name": "no_cat"}) is True


class TestRAGSync:
    """Tests for the RAG sync bridge."""

    def test_scrub_ingestion(self, tmp_path):
        syncer = RAGSync(output_dir=tmp_path)
        raw = [
            {"name": "good.json", "categories": ["research"]},
            {"name": "bad.json", "categories": ["ark"]},
        ]
        clean = syncer.scrub_ingestion(raw)
        assert len(clean) == 1
        assert clean[0]["name"] == "good.json"

    def test_sync_to_spaces(self, tmp_path):
        syncer = RAGSync(output_dir=tmp_path)
        data = [{"name": "test.json", "categories": ["data"]}]
        result = syncer.sync_to_spaces(data)
        assert result["items_pushed"] == 1
        assert "DJ-Goanna-Coding" in result["target_url"]
        assert Path(result["payload_path"]).exists()

    def test_sync_log_accumulates(self, tmp_path):
        syncer = RAGSync(output_dir=tmp_path)
        syncer.sync_to_spaces([{"a": 1}])
        syncer.sync_to_spaces([{"b": 2}])
        assert len(syncer.sync_log()) == 2

    def test_status(self, tmp_path):
        syncer = RAGSync(output_dir=tmp_path)
        status = syncer.status()
        assert "bible" in status["excluded_categories"]
        assert status["hf_org"] == "DJ-Goanna-Coding"

    def test_filter_access(self, tmp_path):
        syncer = RAGSync(output_dir=tmp_path)
        assert isinstance(syncer.filter, SovereignFilter)
