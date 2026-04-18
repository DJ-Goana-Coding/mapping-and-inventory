"""Tests for the global manifest generator and the ignite_tia loader."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import build_global_manifest as bgm  # noqa: E402
import ignite_tia  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixture: a miniature repo that mirrors the real layout
# --------------------------------------------------------------------------- #
@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()

    # requirements.txt with the RAG deps we look for.
    (root / "requirements.txt").write_text(
        "streamlit>=1.45.0\n"
        "faiss-cpu>=1.8.0\n"
        "sentence-transformers>=2.7.0\n"
        "huggingface-hub>=0.30.0\n",
        encoding="utf-8",
    )

    # Existing manifests.
    (root / "system_manifest.json").write_text(
        json.dumps({"system_id": "TEST", "version": "1"}), encoding="utf-8"
    )
    (root / "master_inventory.json").write_text(
        json.dumps([{"name": "a"}, {"name": "b"}]), encoding="utf-8"
    )
    (root / "districts.json").write_text(
        json.dumps({"districts": [], "total_districts": 0}), encoding="utf-8"
    )
    (root / "FOUNDATION_MANIFEST.md").write_text("# foundation", encoding="utf-8")

    # Live + one non-live partition.
    for n in (1, 2, 3, 4, 7, 46):
        (root / f"Partition_{n:02d}").mkdir()
        (root / f"Partition_{n:02d}" / "README.md").write_text("p", encoding="utf-8")

    # A bypass script that should be flagged "present" but never have its
    # contents leaked into the manifest.
    scripts = root / "scripts"
    scripts.mkdir()
    (scripts / "setup_gdrive_rclone.sh").write_text(
        "SECRET_PASSWORD=hunter2\n", encoding="utf-8"
    )

    # Files that must be redacted (path only, no hash, no contents).
    (root / "credentials.json").write_text("SECRET_PASSWORD=hunter2", encoding="utf-8")
    (root / "rclone.conf").write_text("SECRET_PASSWORD=hunter2", encoding="utf-8")
    (root / "service_account_dev.json").write_text(
        "SECRET_PASSWORD=hunter2", encoding="utf-8"
    )
    (root / ".env").write_text("SECRET_PASSWORD=hunter2", encoding="utf-8")
    (root / "key.pem").write_text("SECRET_PASSWORD=hunter2", encoding="utf-8")

    # Some normal source files.
    (root / "app.py").write_text("print('hi')\n", encoding="utf-8")

    # Excluded dirs that must not appear in the index.
    (root / ".git").mkdir()
    (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "x.pyc").write_text("junk", encoding="utf-8")

    return root


# --------------------------------------------------------------------------- #
# Generator
# --------------------------------------------------------------------------- #
def test_generate_writes_both_artifacts(mini_repo: Path) -> None:
    file_index_path, manifest_path = bgm.generate(mini_repo)
    assert file_index_path.exists()
    assert manifest_path.exists()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key in (
        "schema_version",
        "generated_at",
        "repo_assets",
        "manifests",
        "rag_dependencies",
        "external_references",
        "bypass_scripts_present",
    ):
        assert key in manifest, f"missing {key}"


def test_redaction_blocks_secret_contents(mini_repo: Path) -> None:
    file_index_path, manifest_path = bgm.generate(mini_repo)
    raw_index = file_index_path.read_text(encoding="utf-8")
    raw_manifest = manifest_path.read_text(encoding="utf-8")

    # The unique sentinel from every secret file must never appear anywhere.
    assert "hunter2" not in raw_index
    assert "hunter2" not in raw_manifest

    index = json.loads(raw_index)
    secret_paths = {
        "credentials.json",
        "rclone.conf",
        "service_account_dev.json",
        ".env",
        "key.pem",
    }
    by_path = {entry["path"]: entry for entry in index["files"]}
    for sp in secret_paths:
        assert sp in by_path, f"redacted file {sp} should still be listed"
        entry = by_path[sp]
        assert entry["redacted"] is True
        assert "sha256_16" not in entry


def test_excluded_dirs_are_pruned(mini_repo: Path) -> None:
    file_index_path, _ = bgm.generate(mini_repo)
    paths = {e["path"] for e in json.loads(file_index_path.read_text())["files"]}
    assert not any(p.startswith(".git/") for p in paths)
    assert not any(p.startswith("__pycache__/") for p in paths)


def test_partition_classification(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    manifest = json.loads(manifest_path.read_text())
    parts = manifest["repo_assets"]["partitions"]
    assert parts["total_declared"] == 46
    assert parts["live_ids"] == [1, 2, 3, 4, 46]
    assert parts["live_present"] == [1, 2, 3, 4, 46]
    assert parts["live_missing"] == []
    assert 7 in parts["remote_archived_ids"]
    assert 1 not in parts["remote_archived_ids"]


def test_rag_dependency_detection(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    manifest = json.loads(manifest_path.read_text())
    presence = manifest["rag_dependencies"]["present"]
    assert presence == {
        "faiss-cpu": True,
        "sentence-transformers": True,
        "huggingface-hub": True,
    }


def test_external_references_have_operator_inputs(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    refs = json.loads(manifest_path.read_text())["external_references"]
    assert refs["gdrive_archive_id"] == "CITADEL-BOT-INDEX"
    assert refs["hf_dataset_storage"] == "DJ-Goana-Coding/CITADEL_OMEGA_Inventory"


def test_bypass_scripts_presence_only(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    bypass = json.loads(manifest_path.read_text())["bypass_scripts_present"]
    assert bypass["scripts/setup_gdrive_rclone.sh"] is True
    # Other candidate scripts that don't exist in the mini repo must be False.
    assert bypass["scripts/initialize_credential_vault.py"] is False


def test_generation_is_deterministic(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    first = manifest_path.read_text(encoding="utf-8")
    # Re-run without modifying the tree.
    _, manifest_path2 = bgm.generate(mini_repo)
    second = manifest_path2.read_text(encoding="utf-8")
    assert first == second


def test_manifests_section_references_existing_files(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    manifests = json.loads(manifest_path.read_text())["manifests"]
    sm = manifests["system_manifest.json"]
    assert sm["exists"] is True
    assert sm["kind"] == "object"
    assert "system_id" in sm["top_level_keys"]
    mi = manifests["master_inventory.json"]
    assert mi["exists"] is True
    assert mi["kind"] == "array"
    assert mi["length"] == 2
    # Missing manifests are reported as not present, not omitted.
    assert manifests["worker_status.json"]["exists"] is False


# --------------------------------------------------------------------------- #
# ignite_tia loader
# --------------------------------------------------------------------------- #
def test_ignite_tia_loads_generated_manifest(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    loaded = ignite_tia.load_manifest(manifest_path)
    assert loaded["schema_version"].startswith("1.")
    assert loaded["external_references"]["gdrive_archive_id"] == "CITADEL-BOT-INDEX"


def test_ignite_tia_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ignite_tia.ManifestError):
        ignite_tia.load_manifest(tmp_path / "nope.json")


def test_ignite_tia_rejects_invalid_schema(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"schema_version": "9.0.0"}), encoding="utf-8")
    with pytest.raises(ignite_tia.ManifestError):
        ignite_tia.load_manifest(bad)


def test_ignite_tia_rejects_missing_keys(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"schema_version": "1.0.0"}), encoding="utf-8")
    with pytest.raises(ignite_tia.ManifestError):
        ignite_tia.load_manifest(bad)


def test_ignite_tia_summary_runs(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    summary = ignite_tia.summarise(ignite_tia.load_manifest(manifest_path))
    assert "schema_version" in summary
    assert "CITADEL-BOT-INDEX" in summary


def test_ignite_tia_cli(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "ignite_tia.py"),
         "--manifest", str(manifest_path)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "CITADEL-BOT-INDEX" in result.stdout


# --------------------------------------------------------------------------- #
# rag_knowledge_base section
# --------------------------------------------------------------------------- #
def _rkb_fixture(root: Path) -> None:
    """Add files exercising the classifier and deep-read logic."""
    # Files inside scanned partitions with various semantic purposes.
    (root / "Partition_01" / "trader_engine.py").write_text("x", encoding="utf-8")
    (root / "Partition_01" / "adobe_plugin.json").write_text("{}", encoding="utf-8")
    (root / "Partition_02" / "notes.txt").write_text("note", encoding="utf-8")
    (root / "Partition_03" / "architecture.md").write_text("# arch", encoding="utf-8")
    (root / "Partition_04" / "system_manifest.json").write_text("{}", encoding="utf-8")
    (root / "Partition_46" / "random.bin").write_bytes(b"\x00")  # excluded ext
    # A README somewhere outside the partitions.
    (root / "docs").mkdir(exist_ok=True)
    (root / "docs" / "README.md").write_text("hi", encoding="utf-8")


def test_rag_knowledge_base_section_present(mini_repo: Path) -> None:
    _rkb_fixture(mini_repo)
    _, manifest_path = bgm.generate(mini_repo)
    rkb = json.loads(manifest_path.read_text())["rag_knowledge_base"]
    assert rkb["schema_version"].startswith("1.")
    assert "Partition_01" in rkb["scope"]["partitions_scanned"]
    assert "Partition_46" in rkb["scope"]["partitions_present"]
    assert rkb["scope"]["partition_file_extensions"] == [".json", ".md", ".py", ".txt"]
    assert "unclassified" in rkb["classifier"]["labels"]


def test_rag_classifier_labels(mini_repo: Path) -> None:
    _rkb_fixture(mini_repo)
    _, manifest_path = bgm.generate(mini_repo)
    rkb = json.loads(manifest_path.read_text())["rag_knowledge_base"]
    by_part = {p["partition"]: p for p in rkb["partitions"]}
    paths = {f["path"]: f for f in by_part["Partition_01"]["files"]}
    assert paths["Partition_01/trader_engine.py"]["semantic_purpose"] == "Trading Logic"
    assert paths["Partition_01/adobe_plugin.json"]["semantic_purpose"] == "Adobe Plugin"
    arch = {f["path"]: f for f in by_part["Partition_03"]["files"]}
    assert arch["Partition_03/architecture.md"]["semantic_purpose"] == "Architecture Doc"
    sysm = {f["path"]: f for f in by_part["Partition_04"]["files"]}
    assert sysm["Partition_04/system_manifest.json"]["semantic_purpose"] == "System Manifest"


def test_rag_partition_scan_excludes_other_extensions(mini_repo: Path) -> None:
    _rkb_fixture(mini_repo)
    _, manifest_path = bgm.generate(mini_repo)
    rkb = json.loads(manifest_path.read_text())["rag_knowledge_base"]
    by_part = {p["partition"]: p for p in rkb["partitions"]}
    paths = {f["path"] for f in by_part["Partition_46"]["files"]}
    assert all(not p.endswith(".bin") for p in paths)


def test_rag_deep_read_index_finds_all(mini_repo: Path) -> None:
    _rkb_fixture(mini_repo)
    _, manifest_path = bgm.generate(mini_repo)
    rkb = json.loads(manifest_path.read_text())["rag_knowledge_base"]
    docs = rkb["deep_read_documents"]["documents"]
    paths = {d["path"] for d in docs}
    # README.md from /docs and from each Partition fixture directory plus
    # the architecture.md and system_manifest.json from the fixtures must
    # all appear in the deep-read index.
    assert "docs/README.md" in paths
    assert "Partition_03/architecture.md" in paths
    assert "Partition_04/system_manifest.json" in paths
    assert "system_manifest.json" in paths  # root-level manifest from base fixture


def test_rag_cross_repo_status_is_honest(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    rkb = json.loads(manifest_path.read_text())["rag_knowledge_base"]
    cri = rkb["cross_repo_ingestion"]
    assert cri["status"] == "not_available_in_sandbox"
    assert cri["discovery_exists"] is False
    assert "total_fleet_crawler.py" in cri["hint"]


def test_rag_section_is_deterministic(mini_repo: Path) -> None:
    _rkb_fixture(mini_repo)
    _, manifest_path = bgm.generate(mini_repo)
    first = manifest_path.read_text(encoding="utf-8")
    _, manifest_path2 = bgm.generate(mini_repo)
    assert first == manifest_path2.read_text(encoding="utf-8")


def test_rag_secret_files_in_partitions_redacted(tmp_path: Path) -> None:
    # Build a minimal repo with a secret-looking file inside a scanned partition.
    root = tmp_path / "repo"
    root.mkdir()
    (root / "requirements.txt").write_text("\n", encoding="utf-8")
    p = root / "Partition_01"
    p.mkdir()
    (p / "credentials.json").write_text("hunter2-partition", encoding="utf-8")
    (p / "ok.py").write_text("x", encoding="utf-8")
    _, manifest_path = bgm.generate(root)
    raw = manifest_path.read_text(encoding="utf-8")
    assert "hunter2-partition" not in raw
    rkb = json.loads(raw)["rag_knowledge_base"]
    by_part = {pp["partition"]: pp for pp in rkb["partitions"]}
    by_path = {f["path"]: f for f in by_part["Partition_01"]["files"]}
    assert by_path["Partition_01/credentials.json"]["redacted"] is True
    assert "sha256_16" not in by_path["Partition_01/credentials.json"]
    assert by_path["Partition_01/ok.py"].get("redacted") is None
    assert "sha256_16" in by_path["Partition_01/ok.py"]
