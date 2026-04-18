"""Tests for the FastAPI sidecar: CORS unlock and /v1/system/commit pipeline."""

from __future__ import annotations

import base64
from unittest.mock import MagicMock, patch

import pytest

# Skip the whole module gracefully if FastAPI isn't installed in the env.
fastapi = pytest.importorskip("fastapi")
pytest.importorskip("starlette")
TestClient = pytest.importorskip("fastapi.testclient").TestClient

# Stub out the rag_hub dependency so importing main_api doesn't try to load
# heavy ML models (sentence-transformers / faiss) during tests.
import sys
import types

if "services.rag_hub" not in sys.modules:
    services_pkg = sys.modules.setdefault("services", types.ModuleType("services"))
    rag_stub = types.ModuleType("services.rag_hub")

    def _get_hub_stub():  # pragma: no cover - replaced per-test as needed
        raise RuntimeError("rag hub disabled in tests")

    rag_stub.get_hub = _get_hub_stub
    sys.modules["services.rag_hub"] = rag_stub
    setattr(services_pkg, "rag_hub", rag_stub)

import main_api  # noqa: E402


@pytest.fixture
def client():
    return TestClient(main_api.app)


# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------


def test_command_deck_origin_in_allow_list_no_trailing_slash():
    expected_origin = "https://citadel-nexus-private.vercel.app"
    # Use equality membership (not substring) so this is an exact-match check.
    assert any(o == expected_origin for o in main_api.ALLOWED_ORIGINS)
    for origin in main_api.ALLOWED_ORIGINS:
        assert not origin.endswith("/"), f"trailing slash on {origin!r}"


def test_cors_preflight_allows_command_deck(client):
    resp = client.options(
        "/healthz",
        headers={
            "Origin": "https://citadel-nexus-private.vercel.app",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert resp.status_code in (200, 204)
    assert (
        resp.headers.get("access-control-allow-origin")
        == "https://citadel-nexus-private.vercel.app"
    )


def test_cors_actual_request_includes_allow_origin(client):
    resp = client.get(
        "/healthz",
        headers={"Origin": "https://citadel-nexus-private.vercel.app"},
    )
    assert resp.status_code == 200
    assert (
        resp.headers.get("access-control-allow-origin")
        == "https://citadel-nexus-private.vercel.app"
    )


# ---------------------------------------------------------------------------
# /v1/system/commit
# ---------------------------------------------------------------------------


def _payload(**overrides):
    base = {
        "repo": "mapping-and-inventory",
        "message": "tia: commit from command deck",
        "files": [{"path": "tmp/example.txt", "content": "hello world"}],
    }
    base.update(overrides)
    return base


def test_commit_requires_hf_token_configured(client, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")
    resp = client.post("/v1/system/commit", json=_payload(), headers={"X-HF-Token": "anything"})
    assert resp.status_code == 503


def test_commit_rejects_bad_hf_token(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")
    resp = client.post("/v1/system/commit", json=_payload(), headers={"X-HF-Token": "wrong"})
    assert resp.status_code == 401


def test_commit_rejects_missing_hf_token_header(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")
    resp = client.post("/v1/system/commit", json=_payload())
    assert resp.status_code == 401


def test_commit_requires_gh_token_configured(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    resp = client.post(
        "/v1/system/commit",
        json=_payload(),
        headers={"X-HF-Token": "secret-hf"},
    )
    assert resp.status_code == 503


def test_commit_rejects_path_traversal(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")
    bad = _payload(files=[{"path": "../etc/passwd", "content": "x"}])
    resp = client.post(
        "/v1/system/commit",
        json=bad,
        headers={"X-HF-Token": "secret-hf"},
    )
    assert resp.status_code == 400


def test_commit_rejects_absolute_path(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")
    bad = _payload(files=[{"path": "/etc/passwd", "content": "x"}])
    resp = client.post(
        "/v1/system/commit",
        json=bad,
        headers={"X-HF-Token": "secret-hf"},
    )
    assert resp.status_code == 400


def test_commit_creates_new_file_via_github_contents_api(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")

    get_resp = MagicMock(status_code=404, content=b"")
    put_resp = MagicMock(
        status_code=201,
        content=b"{}",
    )
    put_resp.json.return_value = {
        "content": {"sha": "abc123", "html_url": "https://github.com/x/y/blob/main/tmp/example.txt"},
        "commit": {"sha": "deadbeef"},
    }

    with patch.object(main_api.requests, "get", return_value=get_resp) as m_get, patch.object(
        main_api.requests, "put", return_value=put_resp
    ) as m_put:
        resp = client.post(
            "/v1/system/commit",
            json=_payload(branch="main"),
            headers={"Authorization": "Bearer secret-hf"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["repo"] == "mapping-and-inventory"
    assert body["branch"] == "main"
    assert len(body["results"]) == 1
    result = body["results"][0]
    assert result["status"] == "created"
    assert result["sha"] == "abc123"
    assert result["commit_sha"] == "deadbeef"

    # Verify GitHub API was called against the DJ-Goana-Coding org by default
    # with proper auth and base64-encoded content.
    assert m_get.call_count == 1
    get_args, get_kwargs = m_get.call_args
    assert get_args[0] == (
        "https://api.github.com/repos/DJ-Goana-Coding/mapping-and-inventory/"
        "contents/tmp/example.txt"
    )
    assert get_kwargs["headers"]["Authorization"] == "Bearer gh-xyz"

    assert m_put.call_count == 1
    put_args, put_kwargs = m_put.call_args
    payload = put_kwargs["json"]
    assert payload["message"] == "tia: commit from command deck"
    assert payload["branch"] == "main"
    assert "sha" not in payload  # no existing file
    assert base64.b64decode(payload["content"]).decode("utf-8") == "hello world"


def test_commit_updates_existing_file_with_sha(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")

    get_resp = MagicMock(status_code=200, content=b"{}")
    get_resp.json.return_value = {"sha": "old-sha-1"}
    put_resp = MagicMock(status_code=200, content=b"{}")
    put_resp.json.return_value = {
        "content": {"sha": "new-sha-2", "html_url": "https://example/x"},
        "commit": {"sha": "commit-sha-3"},
    }

    with patch.object(main_api.requests, "get", return_value=get_resp), patch.object(
        main_api.requests, "put", return_value=put_resp
    ) as m_put:
        resp = client.post(
            "/v1/system/commit",
            json=_payload(),
            headers={"X-HF-Token": "secret-hf"},
        )

    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["results"][0]["status"] == "updated"
    assert body["results"][0]["sha"] == "new-sha-2"
    assert m_put.call_args.kwargs["json"]["sha"] == "old-sha-1"


def test_commit_reports_github_error_per_file(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "gh-xyz")

    get_resp = MagicMock(status_code=404, content=b"")
    put_resp = MagicMock(status_code=422, content=b"bad", text="validation failed")

    with patch.object(main_api.requests, "get", return_value=get_resp), patch.object(
        main_api.requests, "put", return_value=put_resp
    ):
        resp = client.post(
            "/v1/system/commit",
            json=_payload(),
            headers={"X-HF-Token": "secret-hf"},
        )

    assert resp.status_code == 200
    result = resp.json()["results"][0]
    assert result["status"] == "error"
    assert "422" in (result["detail"] or "")
