"""Tests for ``scripts/topology_mapper`` — the synaptic topology mapper
that writes ``fleet/fleet_topology.json`` (+ ``fleet/fleet_topology.md``)."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts import topology_mapper as tm  # noqa: E402


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _b64_contents(text: str) -> dict:
    return {
        "type": "file",
        "encoding": "base64",
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        "sha": "sha-test",
    }


def _tree(paths: list[str], truncated: bool = False) -> dict:
    return {
        "sha": "branch-sha",
        "truncated": truncated,
        "tree": [{"path": p, "type": "blob"} for p in paths]
        + [{"path": "some/dir", "type": "tree"}],  # ignored: not a blob
    }


# --------------------------------------------------------------------------- #
# Opt-in gating
# --------------------------------------------------------------------------- #
def test_topology_no_op_without_token(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    out = tmp_path / "topo.json"
    rc = tm.main(["--root", str(tmp_path), "--output", str(out)])
    assert rc == 0
    assert not out.exists()
    assert "GH_TOKEN" in capsys.readouterr().err


def test_topology_rejects_nonpositive_caps(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    rc = tm.main([
        "--root", str(tmp_path),
        "--output", str(tmp_path / "t.json"),
        "--max-workflows", "0",
    ])
    assert rc == 2
    assert "max-workflows" in capsys.readouterr().err


# --------------------------------------------------------------------------- #
# Classifier rules
# --------------------------------------------------------------------------- #
def test_classifier_buckets_paths_correctly() -> None:
    samples = {
        ".github/workflows/sync.yml": ("github_workflow", tm.CAT_WORKER),
        ".github/workflows/build.yaml": ("github_workflow", tm.CAT_WORKER),
        "scripts/sync_daemon.py": ("daemon_script", tm.CAT_WORKER),
        "scripts/my_worker.sh": ("worker_script", tm.CAT_WORKER),
        "ops/crontab": ("cron_schedule", tm.CAT_WORKER),

        "config/rclone.conf": ("rclone_config", tm.CAT_BRIDGE),
        "config/rclone-citadel.conf": ("rclone_config", tm.CAT_BRIDGE),
        "links/CITADEL-BOT/README.md": ("citadel_bot_link", tm.CAT_BRIDGE),
        "hooks/github_webhook.yaml": ("webhook_config", tm.CAT_BRIDGE),
        "net/cloudflare_tunnel.yml": ("tunnel_config", tm.CAT_BRIDGE),
        "bridge/gdrive.py": ("bridge_module", tm.CAT_BRIDGE),

        "rag/faiss_index/index.bin": ("faiss_index", tm.CAT_RAG),
        "models/embeddings/all-MiniLM/file.bin": ("embeddings_store", tm.CAT_RAG),
        "stores/chroma_db/data.parquet": ("chroma_store", tm.CAT_RAG),
        "vector_store/manifest.json": ("vector_store", tm.CAT_RAG),
        "indexes/my_corpus.faiss": ("faiss_artifact", tm.CAT_RAG),
        "rag_pioneer.json": ("rag_manifest", tm.CAT_RAG),
        "system_manifest.json": ("system_manifest", tm.CAT_RAG),
    }
    for path, expected in samples.items():
        assert tm.classify_path(path) == expected, path

    # Unrelated paths return None — we don't fabricate categories.
    for non_artifact in ("README.md", "src/main.py", "docs/intro.md", "LICENSE"):
        assert tm.classify_path(non_artifact) is None, non_artifact


def test_workflow_takes_precedence_over_keyword_match() -> None:
    # Workflow YAML basenames that also contain "webhook" must classify
    # as workers (workflow rule comes first), not as bridges.
    kind, category = tm.classify_path(".github/workflows/webhook.yml")
    assert (kind, category) == ("github_workflow", tm.CAT_WORKER)


def test_classify_paths_returns_sorted_buckets() -> None:
    paths = [
        ".github/workflows/zz.yml",
        ".github/workflows/aa.yml",
        "bridge/gdrive.py",
        "rag_x.json",
        "src/unrelated.py",
    ]
    buckets = tm.classify_paths(paths)
    assert [a["path"] for a in buckets[tm.CAT_WORKER]] == [
        ".github/workflows/aa.yml",
        ".github/workflows/zz.yml",
    ]
    assert buckets[tm.CAT_BRIDGE] == [
        {"path": "bridge/gdrive.py", "kind": "bridge_module"}
    ]
    assert buckets[tm.CAT_RAG] == [
        {"path": "rag_x.json", "kind": "rag_manifest"}
    ]


# --------------------------------------------------------------------------- #
# Edge extraction
# --------------------------------------------------------------------------- #
def test_extract_repo_references_owner_qualified_and_token() -> None:
    text = (
        "name: sync\n"
        "on: push\n"
        "jobs:\n"
        "  call:\n"
        "    uses: DJ-Goana-Coding/Vortex/.github/workflows/x.yml@main\n"
        "    env:\n"
        "      TARGET: Pioneer-Trader\n"
    )
    refs = tm._extract_repo_references(
        text,
        owner="DJ-Goana-Coding",
        candidates={"Vortex", "Pioneer-Trader", "Self", "Unrelated"},
        self_name="Self",
    )
    assert refs == {"Vortex", "Pioneer-Trader"}


def test_extract_repo_references_excludes_self() -> None:
    text = "uses: DJ-Goana-Coding/Self/.github/workflows/x.yml@main"
    refs = tm._extract_repo_references(
        text,
        owner="DJ-Goana-Coding",
        candidates={"Self", "Other"},
        self_name="Self",
    )
    assert refs == set()


# --------------------------------------------------------------------------- #
# Full happy path
# --------------------------------------------------------------------------- #
def _install_fake_http(monkeypatch, repos: list[dict], trees: dict[str, dict],
                       workflow_files: dict[tuple[str, str], str]):
    """Register a single fake _http_get_json that serves the given fixtures."""

    def fake_get(url, token, opener=None):
        assert token == "ghp_test"
        if "/users/" in url and "page=1" in url:
            return repos
        if "page=" in url:  # later pages are empty
            return []
        # Tree calls: /repos/{owner}/{repo}/git/trees/{branch}?recursive=1
        if "/git/trees/" in url:
            for repo, tree in trees.items():
                if f"/{repo}/git/trees/" in url:
                    return tree
            return None
        # Contents calls for workflow files.
        if "/contents/.github/workflows/" in url:
            for (repo, path), text in workflow_files.items():
                if f"/{repo}/contents/{path}" in url:
                    return _b64_contents(text)
            return None
        return None

    return patch.object(tm, "_http_get_json", side_effect=fake_get)


def test_topology_full_run_with_edges_and_orphans(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    repos = [
        {"name": "Vortex", "default_branch": "main", "archived": False,
         "html_url": "https://github.com/DJ-Goana-Coding/Vortex"},
        {"name": "Pioneer-Trader", "default_branch": "main", "archived": False,
         "html_url": "https://github.com/DJ-Goana-Coding/Pioneer-Trader"},
        {"name": "Lonely", "default_branch": "main", "archived": False,
         "html_url": "https://github.com/DJ-Goana-Coding/Lonely"},
    ]
    trees = {
        "Vortex": _tree([
            ".github/workflows/sync.yml",
            "bridge/gdrive.py",
            "rag/faiss_index/index.bin",
            "README.md",
        ]),
        "Pioneer-Trader": _tree([
            ".github/workflows/trade.yml",
            "config/rclone.conf",
            "src/main.py",
        ]),
        "Lonely": _tree(["README.md", "src/main.py"]),  # → orphan
    }
    workflow_files = {
        ("Vortex", ".github/workflows/sync.yml"):
            "name: sync\non: push\njobs:\n  call:\n"
            "    uses: DJ-Goana-Coding/Pioneer-Trader/.github/workflows/x.yml@main\n",
        ("Pioneer-Trader", ".github/workflows/trade.yml"):
            "name: trade\non: schedule\njobs:\n  notify:\n"
            "    env:\n      TARGET: Vortex\n",
    }

    out = tmp_path / "topo.json"
    rep = tmp_path / "topo.md"
    with _install_fake_http(monkeypatch, repos, trees, workflow_files):
        rc = tm.main([
            "--root", str(tmp_path),
            "--output", str(out),
            "--report", str(rep),
        ])
    assert rc == 0
    assert out.exists() and rep.exists()

    data = json.loads(out.read_text())
    assert data["owner"] == "DJ-Goana-Coding"
    assert data["summary"]["repos_scanned"] == 3
    assert data["summary"]["orphan_count"] == 1
    assert data["orphans"] == ["Lonely"]

    by_repo = {n["repo"]: n for n in data["nodes"]}
    assert by_repo["Vortex"]["is_orphan"] is False
    assert by_repo["Lonely"]["is_orphan"] is True
    assert by_repo["Lonely"]["artifact_count"] == 0
    # Vortex carries one of each category.
    v = by_repo["Vortex"]["artifacts"]
    assert [a["kind"] for a in v["workers"]] == ["github_workflow"]
    assert [a["kind"] for a in v["bridges"]] == ["bridge_module"]
    assert [a["kind"] for a in v["rags"]] == ["faiss_index"]

    # Edges: Vortex→Pioneer-Trader (via workflow) and Pioneer-Trader→Vortex.
    edges = data["edges"]
    triples = {(e["from"], e["to"], e["via"]) for e in edges}
    assert ("Vortex", "Pioneer-Trader", "github_workflow") in triples
    assert ("Pioneer-Trader", "Vortex", "github_workflow") in triples
    # No self-edges.
    assert all(e["from"] != e["to"] for e in edges)

    # Markdown companion calls out the orphan.
    md = rep.read_text()
    assert "# Fleet topology" in md
    assert "Lonely" in md
    assert "Cross-repo edges" in md


def test_topology_archived_repo_status(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    repos = [{"name": "Old", "default_branch": "main", "archived": True}]
    trees = {"Old": _tree(["README.md"])}
    out = tmp_path / "t.json"
    with _install_fake_http(monkeypatch, repos, trees, {}):
        rc = tm.main(["--root", str(tmp_path), "--output", str(out),
                       "--report", str(tmp_path / "r.md")])
    assert rc == 0
    node = json.loads(out.read_text())["nodes"][0]
    assert node["status"] == "archived"
    assert node["is_orphan"] is True


def test_topology_handles_truncated_tree(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    repos = [{"name": "Big", "default_branch": "main"}]
    trees = {"Big": _tree([".github/workflows/x.yml"], truncated=True)}
    out = tmp_path / "t.json"
    with _install_fake_http(monkeypatch, repos, trees, {}):
        rc = tm.main(["--root", str(tmp_path), "--output", str(out),
                       "--report", str(tmp_path / "r.md")])
    assert rc == 0
    node = json.loads(out.read_text())["nodes"][0]
    assert node["tree_truncated"] is True


def test_topology_is_deterministic(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    repos = [
        {"name": "B", "default_branch": "main"},
        {"name": "A", "default_branch": "main"},
    ]
    trees = {
        "A": _tree(["bridge/x.py", ".github/workflows/a.yml"]),
        "B": _tree(["rag_x.json", ".github/workflows/b.yml"]),
    }
    workflows = {
        ("A", ".github/workflows/a.yml"): "uses: DJ-Goana-Coding/B/x.yml@main\n",
        ("B", ".github/workflows/b.yml"): "env:\n  TARGET: A\n",
    }
    o1 = tmp_path / "1.json"
    o2 = tmp_path / "2.json"
    with _install_fake_http(monkeypatch, repos, trees, workflows):
        tm.main(["--root", str(tmp_path), "--output", str(o1),
                  "--report", str(tmp_path / "r1.md")])
    with _install_fake_http(monkeypatch, repos, trees, workflows):
        tm.main(["--root", str(tmp_path), "--output", str(o2),
                  "--report", str(tmp_path / "r2.md")])

    # Strip the variable timestamp before comparing.
    d1 = json.loads(o1.read_text())
    d2 = json.loads(o2.read_text())
    d1.pop("generated_at")
    d2.pop("generated_at")
    assert d1 == d2

    # Nodes alphabetised.
    assert [n["repo"] for n in d1["nodes"]] == ["A", "B"]


def test_topology_empty_owner(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")

    def fake_get(url, token, opener=None):
        return [] if "page=1" in url else None

    out = tmp_path / "t.json"
    rep = tmp_path / "t.md"
    with patch.object(tm, "_http_get_json", side_effect=fake_get):
        rc = tm.main(["--root", str(tmp_path), "--output", str(out),
                       "--report", str(rep)])
    assert rc == 0
    data = json.loads(out.read_text())
    assert data["nodes"] == []
    assert data["edges"] == []
    assert data["orphans"] == []
    assert data["summary"]["repos_scanned"] == 0
    md = rep.read_text()
    assert "No orphans detected" in md
    assert "No cross-repo references detected" in md


# --------------------------------------------------------------------------- #
# Hugging Face dataset detection
# --------------------------------------------------------------------------- #
def test_extract_hf_dataset_refs_from_text() -> None:
    text = (
        "uses: actions/checkout@v4\n"
        "env:\n"
        "  DS: https://huggingface.co/datasets/DJ-Goana-Coding/CITADEL_OMEGA_Inventory\n"
        "  ALSO: huggingface.co/datasets/some-org/another_set\n"
        "  MODEL: https://huggingface.co/some-org/not-a-dataset\n"
    )
    refs = tm._extract_hf_dataset_refs(text)
    assert refs == {
        "DJ-Goana-Coding/CITADEL_OMEGA_Inventory",
        "some-org/another_set",
    }


def test_hf_refs_from_repo_metadata_sources() -> None:
    repo_meta = {
        "name": "Vortex",
        "homepage": "https://huggingface.co/datasets/DJ-Goana-Coding/X",
        "description": "See https://huggingface.co/datasets/Other/Y for more.",
        "topics": ["ai", "hf-dataset:DJ-Goana-Coding/Z", "hf-dataset:bad"],
    }
    refs = tm._hf_refs_from_repo_meta(repo_meta)
    assert refs == {
        "DJ-Goana-Coding/X",
        "Other/Y",
        "DJ-Goana-Coding/Z",  # malformed "hf-dataset:bad" topic skipped
    }


def test_hf_dataset_path_classifier() -> None:
    samples = {
        "datasets.json": ("hf_dataset_declaration", tm.CAT_HF),
        "config/hf_dataset_main.yml": ("hf_dataset_declaration", tm.CAT_HF),
        "huggingface.yaml": ("hf_dataset_declaration", tm.CAT_HF),
    }
    for path, expected in samples.items():
        assert tm.classify_path(path) == expected, path


def test_topology_records_hf_datasets_from_workflows_and_metadata(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")

    repos = [
        {
            "name": "Vortex",
            "default_branch": "main",
            "homepage": "https://huggingface.co/datasets/DJ-Goana-Coding/V_DS",
            "topics": ["hf-dataset:DJ-Goana-Coding/Extra"],
        },
    ]
    trees = {"Vortex": _tree([".github/workflows/sync.yml"])}
    workflows = {
        ("Vortex", ".github/workflows/sync.yml"):
            "env:\n  DS: https://huggingface.co/datasets/Other/Y\n",
    }
    out = tmp_path / "t.json"
    with _install_fake_http(monkeypatch, repos, trees, workflows):
        rc = tm.main([
            "--root", str(tmp_path),
            "--output", str(out),
            "--report", str(tmp_path / "r.md"),
            "--missing-links", str(tmp_path / "m.md"),
        ])
    assert rc == 0
    node = json.loads(out.read_text())["nodes"][0]
    slugs = {r["repo_id"] for r in node["hf_datasets"]}
    assert slugs == {
        "DJ-Goana-Coding/V_DS",       # from homepage
        "DJ-Goana-Coding/Extra",      # from topics
        "Other/Y",                    # from workflow YAML
    }
    # Each record must cite its evidence (no fabrication).
    for r in node["hf_datasets"]:
        assert r["evidence"]
    # And the topology grew an hf_dataset_reference edge per record.
    edges = json.loads(out.read_text())["edges"]
    hf_edges = [e for e in edges if e["via"] == "hf_dataset_reference"]
    assert {e["to"] for e in hf_edges} == {
        "hf://DJ-Goana-Coding/V_DS",
        "hf://DJ-Goana-Coding/Extra",
        "hf://Other/Y",
    }
    # HF presence flips Vortex out of orphan status even with no other
    # workers/RAGs apart from the workflow.
    assert node["is_orphan"] is False


# --------------------------------------------------------------------------- #
# Missing-link audit
# --------------------------------------------------------------------------- #
def _node(name: str, *, workers=0, bridges=0, rags=0, hf=0) -> dict:
    return {
        "repo": name,
        "github_url": f"https://github.com/x/{name}",
        "default_branch": "main",
        "status": "active",
        "tree_truncated": False,
        "artifacts": {
            "bridges": [{"path": f"b{i}", "kind": "k"} for i in range(bridges)],
            "rags":    [{"path": f"r{i}", "kind": "k"} for i in range(rags)],
            "workers": [{"path": f"w{i}", "kind": "github_workflow"}
                        for i in range(workers)],
            "hf_datasets_paths": [],
        },
        "hf_datasets": [{"repo_id": f"o/d{i}", "evidence": "github_metadata"}
                        for i in range(hf)],
        "artifact_count": workers + bridges + rags + hf,
        "is_orphan": (workers + bridges + rags + hf) == 0,
    }


def test_audit_missing_links_buckets_correctly() -> None:
    topology = {
        "owner": "x",
        "generated_at": "2026-04-18T00:00:00+00:00",
        "summary": {},
        "nodes": [
            _node("Orphan"),                        # → orphan
            _node("OnlyWorker", workers=1),         # → source_only
            _node("OnlyBridge", bridges=1),         # → sink_only
            _node("OnlyRag", rags=1),               # → sink_only
            _node("OnlyHF", hf=1),                  # → sink_only
            _node("Healthy", workers=1, bridges=1), # excluded
        ],
        "edges": [
            {"from": "Healthy", "to": "Orphan", "via": "github_workflow",
             "evidence": ".github/workflows/x.yml"},  # broken
            {"from": "Healthy", "to": "OnlyWorker", "via": "github_workflow",
             "evidence": ".github/workflows/y.yml"},  # ok
            {"from": "Healthy", "to": "hf://o/d", "via": "hf_dataset_reference",
             "evidence": "github_metadata"},          # hf edges ignored
        ],
        "orphans": ["Orphan"],
    }
    audit = tm.audit_missing_links(topology)
    assert audit["orphans"] == ["Orphan"]
    assert audit["source_only"] == ["OnlyWorker"]
    assert audit["sink_only"] == ["OnlyBridge", "OnlyHF", "OnlyRag"]
    assert len(audit["edges_to_orphan_targets"]) == 1
    assert audit["edges_to_orphan_targets"][0]["to"] == "Orphan"
    s = audit["summary"]
    assert s["orphan_count"] == 1
    assert s["source_only_count"] == 1
    assert s["sink_only_count"] == 3
    assert s["broken_edge_count"] == 1


def test_render_missing_links_includes_all_sections() -> None:
    topology = {
        "owner": "x", "generated_at": "2026-04-18T00:00:00+00:00",
        "summary": {}, "nodes": [_node("L")], "edges": [], "orphans": ["L"],
    }
    md = tm.render_missing_links(topology)
    assert "# Missing links" in md
    assert "## Orphan repositories" in md
    assert "## Source-only nodes" in md
    assert "## Sink-only nodes" in md
    assert "## Broken edges" in md
    assert "`L`" in md
    # Empty sections render `_None._` rather than being silently dropped.
    assert md.count("_None._") == 3  # source_only, sink_only, broken_edges


def test_render_missing_links_all_clean() -> None:
    topology = {
        "owner": "x", "generated_at": "2026-04-18T00:00:00+00:00",
        "summary": {},
        "nodes": [_node("Healthy", workers=1, rags=1)],
        "edges": [], "orphans": [],
    }
    md = tm.render_missing_links(topology)
    # All four sections should report _None._
    assert md.count("_None._") == 4


def test_main_writes_missing_links_file(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("GH_TOKEN", "ghp_test")
    repos = [
        {"name": "Healthy", "default_branch": "main"},
        {"name": "Lonely", "default_branch": "main"},
    ]
    trees = {
        "Healthy": _tree([".github/workflows/x.yml", "bridge/g.py"]),
        "Lonely": _tree(["README.md"]),
    }
    out = tmp_path / "t.json"
    rep = tmp_path / "t.md"
    miss = tmp_path / "missing.md"
    with _install_fake_http(monkeypatch, repos, trees, {}):
        rc = tm.main([
            "--root", str(tmp_path),
            "--output", str(out),
            "--report", str(rep),
            "--missing-links", str(miss),
        ])
    assert rc == 0
    assert miss.exists()
    content = miss.read_text()
    assert "# Missing links" in content
    assert "`Lonely`" in content
