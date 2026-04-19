"""Tests for /v1/system/tunnels probe and startup token pre-flight."""

from __future__ import annotations

import logging
import sys
import types
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("starlette")
TestClient = pytest.importorskip("fastapi.testclient").TestClient

# Stub services.rag_hub before importing main_api (mirrors test_main_api_commit).
if "services.rag_hub" not in sys.modules:
    services_pkg = sys.modules.setdefault("services", types.ModuleType("services"))
    rag_stub = types.ModuleType("services.rag_hub")

    def _get_hub_stub():  # pragma: no cover
        raise RuntimeError("rag hub disabled in tests")

    rag_stub.get_hub = _get_hub_stub
    rag_stub.DEVICE_FRAGMENT_GLOBS = ()  # added: required by main_api.py and telemetry_bridge.py
    rag_stub.REPO_ROOT = __import__("pathlib").Path(__file__).resolve().parent.parent
    sys.modules["services.rag_hub"] = rag_stub
    setattr(services_pkg, "rag_hub", rag_stub)

import main_api  # noqa: E402


@pytest.fixture
def client():
    return TestClient(main_api.app)


# ---------------------------------------------------------------------------
# Startup pre-flight token check
# ---------------------------------------------------------------------------


def test_preflight_logs_present_tokens(monkeypatch, caplog):
    monkeypatch.setenv("HF_TOKEN", "secret-hf")
    monkeypatch.setenv("GH_TOKEN", "secret-gh")
    with caplog.at_level(logging.INFO, logger="main_api"):
        main_api._preflight_token_check()
    msg = " ".join(r.getMessage() for r in caplog.records)
    assert "HF_TOKEN=present" in msg
    assert "GH_TOKEN=present" in msg
    # Token VALUES must never appear in logs.
    assert "secret-hf" not in msg
    assert "secret-gh" not in msg


def test_preflight_logs_missing_tokens(monkeypatch, caplog):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    with caplog.at_level(logging.INFO, logger="main_api"):
        main_api._preflight_token_check()
    msg = " ".join(r.getMessage() for r in caplog.records)
    assert "HF_TOKEN=missing" in msg
    assert "GH_TOKEN=missing" in msg


def test_preflight_accepts_github_token_alias(monkeypatch, caplog):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.setenv("GITHUB_TOKEN", "x")
    with caplog.at_level(logging.INFO, logger="main_api"):
        main_api._preflight_token_check()
    msg = " ".join(r.getMessage() for r in caplog.records)
    assert "GH_TOKEN=present" in msg


# ---------------------------------------------------------------------------
# /v1/system/tunnels
# ---------------------------------------------------------------------------


def _resp(status_code: int) -> MagicMock:
    return MagicMock(status_code=status_code)


def test_tunnels_all_ok(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "x")
    monkeypatch.setenv("GH_TOKEN", "y")
    with patch.object(main_api.requests, "head", return_value=_resp(200)) as m_head:
        resp = client.get("/v1/system/tunnels")
    assert resp.status_code == 200
    body = resp.json()
    for key in ("huggingface", "gdrive", "github"):
        assert body[key]["status"] == "ok"
        assert body[key]["http_status"] == 200
    assert body["tokens"] == {"hf_token": True, "gh_token": True}
    # Three probes were issued.
    assert m_head.call_count == 3


def test_tunnels_auth_required_classified(client, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    # 401 from drive (no creds), 200 from the others.
    def fake_head(url, timeout, allow_redirects):
        if "googleapis" in url:
            return _resp(401)
        return _resp(200)

    with patch.object(main_api.requests, "head", side_effect=fake_head):
        resp = client.get("/v1/system/tunnels")
    body = resp.json()
    assert body["gdrive"]["status"] == "auth_required"
    assert body["gdrive"]["http_status"] == 401
    assert body["huggingface"]["status"] == "ok"
    assert body["github"]["status"] == "ok"
    assert body["tokens"] == {"hf_token": False, "gh_token": False}


def test_tunnels_unreachable_on_network_error(client, monkeypatch):
    monkeypatch.setenv("HF_TOKEN", "x")
    monkeypatch.setenv("GH_TOKEN", "y")
    import requests as _requests

    with patch.object(
        main_api.requests, "head", side_effect=_requests.ConnectionError("boom")
    ):
        resp = client.get("/v1/system/tunnels")
    body = resp.json()
    for key in ("huggingface", "gdrive", "github"):
        assert body[key]["status"] == "unreachable"
        assert body[key]["http_status"] is None
        assert "boom" in (body[key]["detail"] or "")


def test_tunnels_500_classed_unreachable(client):
    with patch.object(main_api.requests, "head", return_value=_resp(500)):
        resp = client.get("/v1/system/tunnels")
    body = resp.json()
    assert body["huggingface"]["status"] == "unreachable"
    assert body["huggingface"]["http_status"] == 500
