"""Tests for SOVEREIGN_HUD_ALIGNMENT v26.59 weld:

* PORT_RESONANCE_WELD — start_hub.sh / Dockerfile use port 10000.
* CORS_GATE_AUTHORIZATION — Vercel command deck always present, env-extended.
* SECRET_MIRROR_VALIDATION — POST /v1/system/status authenticated by
  CITADEL_ACCESS, payload buffered and surfaced via GET.
"""

from __future__ import annotations

import importlib
import sys
import types
from pathlib import Path

import pytest

# Skip module gracefully if FastAPI isn't installed.
pytest.importorskip("fastapi")
pytest.importorskip("starlette")
TestClient = pytest.importorskip("fastapi.testclient").TestClient

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Ensure the real ``services`` package is importable as a package BEFORE we
# stub out ``services.rag_hub`` — otherwise ``setdefault('services', ...)``
# would replace the real package with a non-package ModuleType and break
# ``from services.universal_bridge import ...`` inside main_api.
import services  # noqa: F401,E402

if "services.rag_hub" not in sys.modules:
    rag_stub = types.ModuleType("services.rag_hub")

    def _get_hub_stub():  # pragma: no cover - replaced per-test as needed
        raise RuntimeError("rag hub disabled in tests")

    rag_stub.get_hub = _get_hub_stub
    rag_stub.DEVICE_FRAGMENT_GLOBS = ()
    rag_stub.REPO_ROOT = PROJECT_ROOT
    sys.modules["services.rag_hub"] = rag_stub
    setattr(services, "rag_hub", rag_stub)


# ---------------------------------------------------------------------------
# PORT_RESONANCE_WELD — config files reference port 10000
# ---------------------------------------------------------------------------


def test_start_hub_default_port_is_10000():
    """The FastAPI sidecar must default to the welded resonance port 10000."""
    text = (PROJECT_ROOT / "scripts" / "start_hub.sh").read_text(encoding="utf-8")
    assert 'API_PORT="${API_PORT:-10000}"' in text


def test_dockerfile_exposes_port_10000():
    text = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "EXPOSE 10000" in text
    # Old default must be gone so HF Space rebuilds bind correctly.
    assert "EXPOSE 8000" not in text


# ---------------------------------------------------------------------------
# CORS_GATE_AUTHORIZATION — env-extended allow list
# ---------------------------------------------------------------------------


def _reload_main_api():
    """Reload main_api so the module-level ALLOWED_ORIGINS picks up env."""
    if "main_api" in sys.modules:
        return importlib.reload(sys.modules["main_api"])
    import main_api  # noqa: E402

    return main_api


def test_default_allow_list_contains_command_deck(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    main_api = _reload_main_api()
    expected = "https://citadel-nexus-private.vercel.app"
    assert any(o == expected for o in main_api.ALLOWED_ORIGINS)
    for origin in main_api.ALLOWED_ORIGINS:
        assert not origin.endswith("/"), f"trailing slash on {origin!r}"


def test_env_allowed_origins_extends_static_list(monkeypatch):
    monkeypatch.setenv(
        "ALLOWED_ORIGINS",
        "https://hub.example.com, https://spoke.example.com/",
    )
    main_api = _reload_main_api()
    assert any(o == "https://hub.example.com" for o in main_api.ALLOWED_ORIGINS)
    # Trailing slash normalized away.
    assert any(o == "https://spoke.example.com" for o in main_api.ALLOWED_ORIGINS)
    assert not any(o == "https://spoke.example.com/" for o in main_api.ALLOWED_ORIGINS)
    # Command deck still guaranteed.
    assert any(
        o == "https://citadel-nexus-private.vercel.app"
        for o in main_api.ALLOWED_ORIGINS
    )
    # No duplicates.
    assert len(main_api.ALLOWED_ORIGINS) == len(set(main_api.ALLOWED_ORIGINS))


def test_env_allowed_origins_does_not_drop_command_deck(monkeypatch):
    """Even a malformed override cannot strip the Vercel command deck."""
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://only-spoke.example.com")
    main_api = _reload_main_api()
    assert any(
        o == "https://citadel-nexus-private.vercel.app"
        for o in main_api.ALLOWED_ORIGINS
    )


# ---------------------------------------------------------------------------
# SECRET_MIRROR_VALIDATION — POST /v1/system/status spoke reports
# ---------------------------------------------------------------------------


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("ALLOWED_ORIGINS", raising=False)
    main_api = _reload_main_api()
    # Reset the in-memory ring buffer between tests.
    import telemetry_bridge

    telemetry_bridge._report_buffer.clear()
    return TestClient(main_api.app)


def _payload(**overrides):
    base = {
        "repo": "mapping-and-inventory",
        "status": "9,293_STABILITY",
        "tunnel": "active",
    }
    base.update(overrides)
    return base


def test_post_status_requires_citadel_access_configured(client, monkeypatch):
    monkeypatch.delenv("CITADEL_ACCESS", raising=False)
    resp = client.post(
        "/v1/system/status",
        json=_payload(),
        headers={"X-Citadel-Access": "anything"},
    )
    assert resp.status_code == 503
    assert "CITADEL_ACCESS" in resp.json()["detail"]


def test_post_status_rejects_missing_header(client, monkeypatch):
    monkeypatch.setenv("CITADEL_ACCESS", "shared-secret")
    resp = client.post("/v1/system/status", json=_payload())
    assert resp.status_code == 401


def test_post_status_rejects_bad_secret(client, monkeypatch):
    monkeypatch.setenv("CITADEL_ACCESS", "shared-secret")
    resp = client.post(
        "/v1/system/status",
        json=_payload(),
        headers={"X-Citadel-Access": "wrong"},
    )
    assert resp.status_code == 401


def test_post_status_accepts_valid_report(client, monkeypatch):
    monkeypatch.setenv("CITADEL_ACCESS", "shared-secret")
    resp = client.post(
        "/v1/system/status",
        json=_payload(),
        headers={"X-Citadel-Access": "shared-secret"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["accepted"] is True
    assert body["hub"] == "mapping-and-inventory"
    assert body["buffered_reports"] == 1
    assert body["received_at"]


def test_post_status_validates_payload_shape(client, monkeypatch):
    monkeypatch.setenv("CITADEL_ACCESS", "shared-secret")
    # Missing required field "tunnel".
    resp = client.post(
        "/v1/system/status",
        json={"repo": "x", "status": "y"},
        headers={"X-Citadel-Access": "shared-secret"},
    )
    assert resp.status_code == 422


def test_get_status_surfaces_recent_reports_and_secret_presence(client, monkeypatch):
    monkeypatch.setenv("CITADEL_ACCESS", "shared-secret")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://hub.example.com")

    # Stub get_hub() so GET works without sentence-transformers / faiss.
    import telemetry_bridge

    monkeypatch.setattr(
        telemetry_bridge,
        "get_hub",
        lambda: types.SimpleNamespace(
            stats=lambda: {
                "loaded": False,
                "chunks": 0,
                "sources": [],
                "model": "",
                "vector_store_dir": "",
            }
        ),
    )
    # Suppress real network HEAD probes.
    monkeypatch.setattr(
        telemetry_bridge,
        "_probe",
        lambda name, url, timeout=2.0: telemetry_bridge.TunnelStatus(
            name=name, url=url, status="ok", http_status=200
        ),
    )

    # Send a spoke report.
    resp = client.post(
        "/v1/system/status",
        json=_payload(),
        headers={"X-Citadel-Access": "shared-secret"},
    )
    assert resp.status_code == 200

    # Pull the GET aggregate.
    resp = client.get("/v1/system/status")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["hub"] == "mapping-and-inventory"
    assert body["tokens"]["citadel_access"] is True
    assert body["tokens"]["allowed_origins"] is True
    assert len(body["recent_reports"]) == 1
    record = body["recent_reports"][0]
    assert record["repo"] == "mapping-and-inventory"
    assert record["status"] == "9,293_STABILITY"
    assert record["tunnel"] == "active"
    assert record["received_at"]


def test_ring_buffer_caps_at_max(client, monkeypatch):
    monkeypatch.setenv("CITADEL_ACCESS", "shared-secret")
    import telemetry_bridge

    cap = telemetry_bridge._REPORT_BUFFER_MAX
    for i in range(cap + 5):
        resp = client.post(
            "/v1/system/status",
            json=_payload(repo=f"spoke-{i}"),
            headers={"X-Citadel-Access": "shared-secret"},
        )
        assert resp.status_code == 200
    assert len(telemetry_bridge._report_buffer) == cap
    # Oldest entries evicted, newest retained.
    assert telemetry_bridge._report_buffer[-1]["repo"] == f"spoke-{cap + 4}"
