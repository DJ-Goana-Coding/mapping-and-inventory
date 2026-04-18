"""Tests for ``scripts/cross_repo_rag_ingest`` — the cross-repo RAG corpus
ingester that writes ``fleet/fleet_corpus.jsonl``."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import cross_repo_rag_ingest as crri  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _make_contents(text: str | bytes, sha: str) -> dict:
    raw = text.encode("utf-8") if isinstance(text, str) else text
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(raw).decode("ascii"),
        "sha": sha,
    }


# --------------------------------------------------------------------------- #
# Opt-in gating
# --------------------------------------------------------------------------- #
def test_ingest_no_op_without_token(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    out = tmp_path / "corpus.jsonl"
    rc = crri.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    assert not out.exists()
    captured = capsys.readouterr()
    assert "GH_TOKEN" in captured.err


def test_ingest_rejects_nonpositive_max_bytes(
    monkeypatch, tmp_path, capsys
) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    out = tmp_path / "corpus.jsonl"
    rc = crri.main(
        ["--root", str(tmp_path), "--output", str(out), "--max-bytes", "0"]
    )
    assert rc == 2
    assert "max-bytes" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# Endpoint contract
# --------------------------------------------------------------------------- #
def test_list_owner_repos_uses_users_endpoint(monkeypatch) -> None:
    seen_urls: list[str] = []

    def fake_get(url, token, opener=None):
        seen_urls.append(url)
        return [] if "page=1" in url else None

    with patch.object(crri, "_http_get_json", side_effect=fake_get):
        repos = crri.list_owner_repos("DJ-Goana-Coding", "ghp_test")

    assert repos == []
    assert seen_urls, "should have made at least one HTTP call"
    assert "/users/DJ-Goana-Coding/repos" in seen_urls[0]
    # MUST NOT use the /orgs/ endpoint per the directive.
    assert all("/orgs/" not in u for u in seen_urls)


# --------------------------------------------------------------------------- #
# Full happy path
# --------------------------------------------------------------------------- #
def test_ingest_writes_corpus_with_mocked_http(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    repos_payload = [
        {"name": "Vortex"},
        {"name": "Pioneer-Trader"},
    ]

    vortex_readme = "# Vortex\n\nTalks to Pioneer-Trader via the GDrive tunnel."
    vortex_arch = "# Architecture\n\nNexus UI is .NET/C#."
    vortex_sysmf = json.dumps({"role": "Vortex", "v": 1})
    pioneer_readme = "# Pioneer-Trader\n\nUses GDrive bridge to reach Vortex."
    pioneer_manifest = json.dumps({"role": "Pioneer", "bridge": "gdrive"})

    def fake_get_json(url, token, opener=None):
        assert token == "ghp_test"
        if "/users/" in url and "page=1" in url:
            return repos_payload
        if "page=2" in url:
            return []
        # Per-file fetches.
        if url.endswith("/Vortex/contents/README.md"):
            return _make_contents(vortex_readme, "sha-v-readme")
        if url.endswith("/Vortex/contents/ARCHITECTURE.md"):
            return _make_contents(vortex_arch, "sha-v-arch")
        if url.endswith("/Vortex/contents/system_manifest.json"):
            return _make_contents(vortex_sysmf, "sha-v-sm")
        if url.endswith("/Pioneer-Trader/contents/README.md"):
            return _make_contents(pioneer_readme, "sha-p-readme")
        if url.endswith("/Pioneer-Trader/contents/manifest.json"):
            return _make_contents(pioneer_manifest, "sha-p-mf")
        # Everything else → 404.
        return None

    out = tmp_path / "corpus.jsonl"
    with patch.object(crri, "_http_get_json", side_effect=fake_get_json):
        rc = crri.main(
            [
                "--root",
                str(tmp_path),
                "--output",
                str(out),
                "--owner",
                "DJ-Goana-Coding",
            ]
        )
    assert rc == 0
    assert out.exists()

    lines = out.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]
    # Sorted by (repo, path).
    assert [(r["repo"], r["path"]) for r in records] == [
        ("Pioneer-Trader", "README.md"),
        ("Pioneer-Trader", "manifest.json"),
        ("Vortex", "ARCHITECTURE.md"),
        ("Vortex", "README.md"),
        ("Vortex", "system_manifest.json"),
    ]
    by_key = {(r["repo"], r["path"]): r for r in records}
    # Literal text content preserved verbatim.
    assert by_key[("Vortex", "README.md")]["content"] == vortex_readme
    assert by_key[("Vortex", "README.md")]["sha"] == "sha-v-readme"
    assert by_key[("Pioneer-Trader", "manifest.json")]["content"] == pioneer_manifest
    # No invented "truncated" flag for files within the cap.
    assert all("truncated" not in r for r in records)


# --------------------------------------------------------------------------- #
# Truncation and binary handling
# --------------------------------------------------------------------------- #
def test_ingest_truncates_oversized_files(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    big_text = "A" * 5000

    def fake_get_json(url, token, opener=None):
        if "/users/" in url and "page=1" in url:
            return [{"name": "Big"}]
        if "page=2" in url:
            return []
        if url.endswith("/Big/contents/README.md"):
            return _make_contents(big_text, "sha-big")
        return None

    out = tmp_path / "corpus.jsonl"
    with patch.object(crri, "_http_get_json", side_effect=fake_get_json):
        rc = crri.main(
            [
                "--root",
                str(tmp_path),
                "--output",
                str(out),
                "--max-bytes",
                "100",
            ]
        )
    assert rc == 0
    records = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["truncated"] is True
    assert records[0]["content"] == "A" * 100


def test_ingest_skips_binary_payloads(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    # Bytes containing a NUL → treated as binary and dropped.
    binary_blob = b"PNG\x00\x01\x02\x03binarydata"
    text_blob = "# clean text"

    def fake_get_json(url, token, opener=None):
        if "/users/" in url and "page=1" in url:
            return [{"name": "Mixed"}]
        if "page=2" in url:
            return []
        if url.endswith("/Mixed/contents/README.md"):
            return _make_contents(binary_blob, "sha-bin")
        if url.endswith("/Mixed/contents/ARCHITECTURE.md"):
            return _make_contents(text_blob, "sha-txt")
        return None

    out = tmp_path / "corpus.jsonl"
    with patch.object(crri, "_http_get_json", side_effect=fake_get_json):
        rc = crri.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    records = [json.loads(line) for line in out.read_text().splitlines()]
    # README dropped (binary); only ARCHITECTURE.md survives.
    assert len(records) == 1
    assert records[0]["path"] == "ARCHITECTURE.md"
    assert records[0]["content"] == text_blob


# --------------------------------------------------------------------------- #
# No fabrication: missing files do not produce empty records
# --------------------------------------------------------------------------- #
def test_ingest_omits_missing_files(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    def fake_get_json(url, token, opener=None):
        if "/users/" in url and "page=1" in url:
            return [{"name": "Sparse"}]
        if "page=2" in url:
            return []
        # Only README.md exists; everything else 404s.
        if url.endswith("/Sparse/contents/README.md"):
            return _make_contents("# sparse", "sha-only")
        return None

    out = tmp_path / "corpus.jsonl"
    with patch.object(crri, "_http_get_json", side_effect=fake_get_json):
        rc = crri.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    records = [json.loads(line) for line in out.read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["path"] == "README.md"
    # No empty-string filler for the missing files.
    assert all(r["content"] for r in records)


def test_ingest_emits_empty_corpus_when_owner_has_no_repos(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")

    def fake_get_json(url, token, opener=None):
        return [] if "page=1" in url else None

    out = tmp_path / "corpus.jsonl"
    with patch.object(crri, "_http_get_json", side_effect=fake_get_json):
        rc = crri.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    assert out.exists()
    assert out.read_text() == ""


# --------------------------------------------------------------------------- #
# Determinism
# --------------------------------------------------------------------------- #
def test_corpus_output_is_deterministic(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    repos = [{"name": "B"}, {"name": "A"}]

    def fake_get_json(url, token, opener=None):
        if "/users/" in url and "page=1" in url:
            return repos
        if "page=2" in url:
            return []
        if "/contents/README.md" in url:
            owner_repo = url.split("/repos/", 1)[1].split("/contents/")[0]
            name = owner_repo.split("/")[-1]
            return _make_contents(f"# {name}", f"sha-{name}")
        return None

    out1 = tmp_path / "c1.jsonl"
    out2 = tmp_path / "c2.jsonl"
    with patch.object(crri, "_http_get_json", side_effect=fake_get_json):
        crri.main(["--root", str(tmp_path), "--output", str(out1)])
        crri.main(["--root", str(tmp_path), "--output", str(out2)])
    assert out1.read_text() == out2.read_text()
    # Records sorted by (repo, path) regardless of API listing order.
    repos_in_order = [
        json.loads(line)["repo"] for line in out1.read_text().splitlines()
    ]
    assert repos_in_order == ["A", "B"]
