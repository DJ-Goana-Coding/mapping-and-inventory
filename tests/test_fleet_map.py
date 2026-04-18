"""Tests for fleet_map (registry + crawler discovery), HF dataset objects,
crawler script, and ignite_tia --network-status."""

from __future__ import annotations

import io
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import build_global_manifest as bgm  # noqa: E402
from scripts import total_fleet_crawler as tfc  # noqa: E402
import ignite_tia  # noqa: E402


# --------------------------------------------------------------------------- #
# Fixture: a mini repo with the structure build_global_manifest expects.
# --------------------------------------------------------------------------- #
@pytest.fixture
def mini_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "requirements.txt").write_text("faiss-cpu>=1.8.0\n", encoding="utf-8")
    (root / "system_manifest.json").write_text(json.dumps({"v": 1}), encoding="utf-8")
    (root / "master_inventory.json").write_text(json.dumps([]), encoding="utf-8")
    (root / "districts.json").write_text(json.dumps({}), encoding="utf-8")
    (root / "FOUNDATION_MANIFEST.md").write_text("# x", encoding="utf-8")
    (root / "Partition_01").mkdir()
    (root / "fleet").mkdir()
    return root


# --------------------------------------------------------------------------- #
# fleet_map: registry + discovery
# --------------------------------------------------------------------------- #
def test_fleet_map_empty_when_no_registry(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    fm = json.loads(manifest_path.read_text())["fleet_map"]
    assert fm["entry_count"] == 0
    assert fm["entries"] == []
    assert fm["sources"]["registry"]["exists"] is False
    assert fm["sources"]["discovery"]["exists"] is False


def test_fleet_map_empty_when_registry_has_no_entries(mini_repo: Path) -> None:
    (mini_repo / "fleet" / "fleet_registry.json").write_text(
        json.dumps({"schema_version": "1.0.0", "entries": []}), encoding="utf-8"
    )
    _, manifest_path = bgm.generate(mini_repo)
    fm = json.loads(manifest_path.read_text())["fleet_map"]
    assert fm["entry_count"] == 0
    assert fm["entries"] == []
    assert fm["sources"]["registry"]["exists"] is True
    assert fm["sources"]["registry"]["entry_count"] == 0


def test_fleet_map_round_trips_registry_entries(mini_repo: Path) -> None:
    (mini_repo / "fleet" / "fleet_registry.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "entries": [
                    {
                        "repo_name": "Vortex",
                        "github_url": "https://github.com/DJ-Goana-Coding/Vortex",
                        "hf_space_url": "https://huggingface.co/spaces/x/y",
                        "role": "Vortex",
                        "status": "active",
                    },
                    {
                        "repo_name": "Pioneer",
                        "github_url": "https://github.com/DJ-Goana-Coding/Pioneer",
                        "role": "Pioneer",
                        "status": "active",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    _, manifest_path = bgm.generate(mini_repo)
    fm = json.loads(manifest_path.read_text())["fleet_map"]
    assert fm["entry_count"] == 2
    names = [e["repo_name"] for e in fm["entries"]]
    assert names == ["Pioneer", "Vortex"]  # alphabetised
    by_name = {e["repo_name"]: e for e in fm["entries"]}
    assert by_name["Vortex"]["source"] == "registry"
    assert by_name["Vortex"]["hf_space_url"] == "https://huggingface.co/spaces/x/y"
    # Pioneer had no hf_space_url in the registry — must NOT be invented.
    assert "hf_space_url" not in by_name["Pioneer"]


def test_fleet_map_registry_takes_precedence_over_discovery(mini_repo: Path) -> None:
    (mini_repo / "fleet" / "fleet_registry.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "entries": [
                    {
                        "repo_name": "Vortex",
                        "github_url": "https://github.com/DJ-Goana-Coding/Vortex",
                        "role": "Vortex",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (mini_repo / "fleet" / "fleet_discovery.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0.0",
                "entries": [
                    {
                        "repo_name": "Vortex",
                        "github_url": "https://github.com/DJ-Goana-Coding/Vortex",
                        "role": "OVERRIDE",
                        "has_system_manifest": True,
                        "has_file_index": True,
                        "module_count": 12,
                    },
                    {
                        "repo_name": "Newcomer",
                        "github_url": "https://github.com/DJ-Goana-Coding/Newcomer",
                        "has_system_manifest": False,
                        "has_file_index": True,
                        "module_count": 3,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    _, manifest_path = bgm.generate(mini_repo)
    fm = json.loads(manifest_path.read_text())["fleet_map"]
    by_name = {e["repo_name"]: e for e in fm["entries"]}
    assert by_name["Vortex"]["source"] == "registry"
    assert by_name["Vortex"]["role"] == "Vortex"  # NOT overridden by discovery
    assert by_name["Newcomer"]["source"] == "discovery"
    # Aggregate counts come from discovery file regardless of merge result.
    agg = fm["aggregate"]
    assert agg["total_repos"] == 2
    assert agg["repos_with_system_manifest"] == 1
    assert agg["repos_with_file_index"] == 2
    assert agg["total_modules"] == 15


def test_fleet_map_handles_malformed_registry(mini_repo: Path) -> None:
    (mini_repo / "fleet" / "fleet_registry.json").write_text(
        "{not json", encoding="utf-8"
    )
    _, manifest_path = bgm.generate(mini_repo)
    fm = json.loads(manifest_path.read_text())["fleet_map"]
    assert fm["entry_count"] == 0
    assert "error" in fm["sources"]["registry"]


# --------------------------------------------------------------------------- #
# HF dataset objects under external_references
# --------------------------------------------------------------------------- #
def test_hf_datasets_default_unverified(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    refs = json.loads(manifest_path.read_text())["external_references"]
    hf = refs["hf_datasets"]
    assert isinstance(hf, list) and len(hf) == 1
    ds = hf[0]
    assert ds["repo_id"] == "DJ-Goana-Coding/CITADEL_OMEGA_Inventory"
    assert ds["kind"] == "dataset"
    assert ds["env_var"] == "HF_DATASET_REPO"
    assert ds["verified"] is False
    assert ds["verified_at"] is None


def test_hf_datasets_verified_only_via_receipts(mini_repo: Path) -> None:
    (mini_repo / "fleet" / "hf_receipts.json").write_text(
        json.dumps(
            {
                "verified": {
                    "DJ-Goana-Coding/CITADEL_OMEGA_Inventory": {
                        "verified_at": "2026-04-18T00:00:00+00:00"
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    _, manifest_path = bgm.generate(mini_repo)
    hf = json.loads(manifest_path.read_text())["external_references"]["hf_datasets"]
    assert hf[0]["verified"] is True
    assert hf[0]["verified_at"] == "2026-04-18T00:00:00+00:00"


# --------------------------------------------------------------------------- #
# Crawler — opt-in via GH_TOKEN
# --------------------------------------------------------------------------- #
def test_crawler_no_op_without_token(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    out = tmp_path / "discovery.json"
    rc = tfc.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    assert not out.exists()
    captured = capsys.readouterr()
    assert "GH_TOKEN" in captured.err


def test_crawler_with_mocked_http_writes_discovery(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    repos_payload = [
        {
            "name": "Vortex",
            "html_url": "https://github.com/DJ-Goana-Coding/Vortex",
            "description": "vortex repo",
            "archived": False,
            "homepage": "https://huggingface.co/spaces/DJ-Goana-Coding/Vortex",
            "topics": [],
        },
        {
            "name": "Pioneer",
            "html_url": "https://github.com/DJ-Goana-Coding/Pioneer",
            "description": None,
            "archived": True,
            "homepage": None,
            "topics": ["hf-space:DJ-Goana-Coding/Pioneer"],
        },
    ]

    file_index_doc = {
        "schema_version": "1.0.0",
        "files": [
            {"path": "a.py", "extension": ".py"},
            {"path": "b.py", "extension": ".py"},
            {"path": "c.md", "extension": ".md"},
            {"path": "d.cs", "extension": ".cs"},
        ],
    }

    import base64

    def make_contents(text: str, sha: str) -> dict:
        return {
            "type": "file",
            "encoding": "base64",
            "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
            "sha": sha,
        }

    def fake_get_json(url, token, opener=None):
        assert token == "ghp_test"
        if "/orgs/" in url and "page=1" in url:
            return repos_payload
        if "page=2" in url:
            return []
        if url.endswith("/contents/README.md"):
            return make_contents("# readme", "sha-readme")
        if url.endswith("/contents/manifest.json"):
            if "Vortex" in url:
                return make_contents(
                    json.dumps({"role": "Vortex", "hf_space_url": "https://huggingface.co/spaces/x/Vortex"}),
                    "sha-mf-v",
                )
            return None  # Pioneer has no manifest.json
        if url.endswith("/contents/system_manifest.json"):
            if "Vortex" in url:
                return make_contents(json.dumps({"v": 1}), "sha-sm-v")
            return None
        if url.endswith("/contents/inventory/file_index.json"):
            if "Vortex" in url:
                return make_contents(json.dumps(file_index_doc), "sha-fi-v")
            return None
        return None

    out = tmp_path / "discovery.json"
    with patch.object(tfc, "_http_get_json", side_effect=fake_get_json):
        rc = tfc.main(["--root", str(tmp_path), "--output", str(out), "--org", "DJ-Goana-Coding"])
    assert rc == 0
    assert out.exists()

    data = json.loads(out.read_text())
    assert data["org"] == "DJ-Goana-Coding"
    assert data["entry_count"] == 2
    by_name = {e["repo_name"]: e for e in data["entries"]}

    v = by_name["Vortex"]
    assert v["github_url"] == "https://github.com/DJ-Goana-Coding/Vortex"
    assert v["status"] == "active"
    assert v["has_readme"] is True
    assert v["has_manifest"] is True
    assert v["has_system_manifest"] is True
    assert v["has_file_index"] is True
    assert v["role"] == "Vortex"
    # HF URL came from the sibling's own manifest.json (priority over homepage).
    assert v["hf_space_url"] == "https://huggingface.co/spaces/x/Vortex"
    # Module count: a.py + b.py + d.cs = 3 (markdown excluded).
    assert v["module_count"] == 3

    p = by_name["Pioneer"]
    assert p["status"] == "archived"
    assert p["has_manifest"] is False
    assert p["has_system_manifest"] is False
    assert p["has_file_index"] is False
    # HF URL constructed from the explicit hf-space topic marker only.
    assert p["hf_space_url"] == "https://huggingface.co/spaces/DJ-Goana-Coding/Pioneer"
    assert "module_count" not in p


def test_crawler_does_not_invent_hf_url(monkeypatch, tmp_path) -> None:
    """A repo with no self-declared HF Space MUST NOT get one fabricated."""
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    def fake_get_json(url, token, opener=None):
        if "/orgs/" in url and "page=1" in url:
            return [
                {
                    "name": "PlainRepo",
                    "html_url": "https://github.com/DJ-Goana-Coding/PlainRepo",
                    "homepage": "https://example.com/something",  # not HF
                    "topics": ["python", "ai"],  # no hf-space: marker
                    "archived": False,
                }
            ]
        if "page=2" in url:
            return []
        return None  # all file fetches → 404

    out = tmp_path / "d.json"
    with patch.object(tfc, "_http_get_json", side_effect=fake_get_json):
        rc = tfc.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    entry = json.loads(out.read_text())["entries"][0]
    assert "hf_space_url" not in entry


# --------------------------------------------------------------------------- #
# ignite_tia --network-status
# --------------------------------------------------------------------------- #
def test_network_status_all_gates_fail_by_default(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    manifest = ignite_tia.load_manifest(manifest_path)
    report = ignite_tia.network_status(manifest, repo_root=mini_repo)
    assert report["citadel_visible"] is False
    # Six gates: registry, discovery, hf, csharp_nexus, gdrive_tunnel, adobe_vts
    assert len(report["gates"]) == 6
    assert all(not g["ok"] for g in report["gates"])
    # Reasons must mention each failing area concretely.
    joined = "\n".join(report["reasons"])
    assert "fleet_registry.json" in joined
    assert "fleet_discovery.json" in joined
    assert "HF datasets" in joined
    assert "C# Private Nexus" in joined
    assert "GDrive" in joined
    assert "Adobe/VTS" in joined


def test_network_status_gates_flip_with_receipts(mini_repo: Path) -> None:
    # Populate registry, discovery, HF receipt, and nexus receipts.
    (mini_repo / "fleet" / "fleet_registry.json").write_text(
        json.dumps({"schema_version": "1.0.0", "entries": [
            {"repo_name": "R", "github_url": "https://github.com/x/R"}
        ]}),
        encoding="utf-8",
    )
    (mini_repo / "fleet" / "fleet_discovery.json").write_text(
        json.dumps({"schema_version": "1.0.0", "entries": []}),
        encoding="utf-8",
    )
    (mini_repo / "fleet" / "hf_receipts.json").write_text(
        json.dumps({"verified": {
            "DJ-Goana-Coding/CITADEL_OMEGA_Inventory": {"verified_at": "2026-04-18T00:00:00+00:00"}
        }}),
        encoding="utf-8",
    )
    (mini_repo / "fleet" / "nexus_receipts.json").write_text(
        json.dumps({
            "csharp_nexus_reachable": {"verified_at": "2026-04-18T00:00:00+00:00"},
            "gdrive_tunnel_open": {"verified_at": "2026-04-18T00:00:00+00:00"},
            "adobe_vts_query_ok": {"verified_at": "2026-04-18T00:00:00+00:00"},
        }),
        encoding="utf-8",
    )
    _, manifest_path = bgm.generate(mini_repo)
    manifest = ignite_tia.load_manifest(manifest_path)
    report = ignite_tia.network_status(manifest, repo_root=mini_repo)
    assert report["citadel_visible"] is True, report["reasons"]
    assert report["reasons"] == []


def test_network_status_cli_exit_codes(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "ignite_tia.py"),
         "--manifest", str(manifest_path), "--network-status"],
        capture_output=True, text=True, check=False,
        cwd=str(mini_repo),  # so receipts lookup uses mini_repo, NOT real repo
    )
    # All gates fail by default → exit code 2, "false" in stdout.
    assert result.returncode == 2
    assert "CITADEL VISIBLE" in result.stdout
    assert "false" in result.stdout
    assert "fleet_registry.json" in result.stdout


def test_summary_includes_fleet_map_line(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    summary = ignite_tia.summarise(ignite_tia.load_manifest(manifest_path))
    assert "fleet_map_entries" in summary
    assert "hf_datasets" in summary


def test_schema_version_unchanged(mini_repo: Path) -> None:
    """Schema major must stay at 1 so the .NET Nexus doesn't break."""
    _, manifest_path = bgm.generate(mini_repo)
    manifest = json.loads(manifest_path.read_text())
    assert manifest["schema_version"].startswith("1.")


def test_generation_remains_deterministic_with_fleet_map(mini_repo: Path) -> None:
    (mini_repo / "fleet" / "fleet_registry.json").write_text(
        json.dumps({"schema_version": "1.0.0", "entries": [
            {"repo_name": "A", "github_url": "https://github.com/x/A"},
            {"repo_name": "B", "github_url": "https://github.com/x/B"},
        ]}),
        encoding="utf-8",
    )
    _, p1 = bgm.generate(mini_repo)
    first = p1.read_text(encoding="utf-8")
    _, p2 = bgm.generate(mini_repo)
    assert first == p2.read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# Network status uses the ignite_tia REPO_ROOT receipts path by default
# --------------------------------------------------------------------------- #
def test_network_status_default_repo_root(mini_repo: Path) -> None:
    _, manifest_path = bgm.generate(mini_repo)
    manifest = ignite_tia.load_manifest(manifest_path)
    # Without an explicit repo_root it falls back to ignite_tia.REPO_ROOT,
    # which is the real project root. The receipts path string should
    # therefore reference the project's fleet/ directory.
    report = ignite_tia.network_status(manifest)
    assert report["receipts_path"].endswith("fleet/nexus_receipts.json")
