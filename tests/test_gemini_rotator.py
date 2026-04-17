"""Tests for the round-robin Gemini API key rotator."""
import pytest

from services import gemini_rotator
from services.gemini_rotator import (
    KeyRotator,
    _is_rate_limit_error,
    generate_content,
    load_keys,
    reset_rotator,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_rotator()
    yield
    reset_rotator()


# ---------------------------------------------------------------------------
# load_keys – key inventory
# ---------------------------------------------------------------------------

def test_load_keys_primary_only():
    assert load_keys({"GEMINI_API_KEY": "alpha"}) == ["alpha"]


def test_load_keys_suffixed_numeric_order():
    env = {
        "GEMINI_API_KEY": "primary",
        "GEMINI_API_KEY_3": "k3",
        "GEMINI_API_KEY_2": "k2",
        "GEMINI_API_KEY_10": "k10",
    }
    assert load_keys(env) == ["primary", "k2", "k3", "k10"]


def test_load_keys_comma_separated_bundle():
    env = {"GEMINI_API_KEYS": "a,b ,c , ,a"}
    # dedupe + strip + drop empties; bundle order preserved
    assert load_keys(env) == ["a", "b", "c"]


def test_load_keys_combined_sources_dedupe():
    env = {
        "GEMINI_API_KEY": "alpha",
        "GEMINI_API_KEY_2": "beta",
        "GEMINI_API_KEYS": "alpha,gamma",
    }
    assert load_keys(env) == ["alpha", "beta", "gamma"]


def test_load_keys_ignores_empty_and_unrelated():
    env = {
        "GEMINI_API_KEY": "",
        "GEMINI_API_KEY_2": "real",
        "OTHER_KEY": "ignored",
    }
    assert load_keys(env) == ["real"]


def test_load_keys_alpha_suffix():
    env = {
        "GEMINI_API_KEY": "primary",
        "GEMINI_API_KEY_2": "two",
        "GEMINI_API_KEY_BACKUP": "backup",
    }
    # numerics first (sorted), then alpha-sorted text suffixes
    assert load_keys(env) == ["primary", "two", "backup"]


# ---------------------------------------------------------------------------
# KeyRotator – round-robin behavior
# ---------------------------------------------------------------------------

def test_rotator_round_robin_distribution():
    r = KeyRotator(["a", "b", "c"])
    # ordered_attempts returns full ring starting at cursor; advances by 1
    assert r.ordered_attempts() == ["a", "b", "c"]
    assert r.ordered_attempts() == ["b", "c", "a"]
    assert r.ordered_attempts() == ["c", "a", "b"]
    assert r.ordered_attempts() == ["a", "b", "c"]


def test_rotator_next_cycles():
    r = KeyRotator(["a", "b"])
    assert [r.next() for _ in range(5)] == ["a", "b", "a", "b", "a"]


def test_rotator_empty():
    r = KeyRotator([])
    assert r.ordered_attempts() == []
    assert r.current() is None
    assert r.next() is None
    assert not r


# ---------------------------------------------------------------------------
# _is_rate_limit_error
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("msg", [
    "429 RESOURCE_EXHAUSTED",
    "got 429 from server",
    "ResourceExhausted: quota",
    "rate limit exceeded",
    "quota exceeded for the day",
])
def test_rate_limit_detection_by_message(msg):
    assert _is_rate_limit_error(Exception(msg))


def test_rate_limit_detection_by_class_name():
    class ResourceExhausted(Exception):
        pass

    assert _is_rate_limit_error(ResourceExhausted("nope"))


def test_non_rate_limit_error():
    assert not _is_rate_limit_error(ValueError("something else"))


# ---------------------------------------------------------------------------
# generate_content – failover & propagation
# ---------------------------------------------------------------------------

class _FakeResponse:
    def __init__(self, text):
        self.text = text


class _FakeModels:
    def __init__(self, key, behavior):
        self.key = key
        self.behavior = behavior

    def generate_content(self, model, contents, **kwargs):
        action = self.behavior.get(self.key, "ok")
        if action == "ok":
            return _FakeResponse(f"reply-from:{self.key}")
        if action == "429":
            raise RuntimeError("429 RESOURCE_EXHAUSTED on this key")
        if action == "boom":
            raise ValueError("non-rate-limit failure")
        raise AssertionError(f"unexpected action {action}")


class _FakeClient:
    def __init__(self, key, behavior, calls):
        self.key = key
        self.models = _FakeModels(key, behavior)
        calls.append(key)


def _factory(behavior, calls):
    def _make(key):
        return _FakeClient(key, behavior, calls)
    return _make


def test_generate_content_uses_first_available_key():
    rot = KeyRotator(["k1", "k2", "k3"])
    calls = []
    resp = generate_content(
        model="m", contents="c", rotator=rot,
        client_factory=_factory({}, calls),
    )
    assert resp.text == "reply-from:k1"
    assert calls == ["k1"]


def test_generate_content_failover_on_429():
    rot = KeyRotator(["k1", "k2", "k3"])
    calls = []
    resp = generate_content(
        model="m", contents="c", rotator=rot,
        client_factory=_factory({"k1": "429", "k2": "429"}, calls),
    )
    assert resp.text == "reply-from:k3"
    assert calls == ["k1", "k2", "k3"]


def test_generate_content_all_keys_exhausted_raises_last_429():
    rot = KeyRotator(["k1", "k2"])
    calls = []
    with pytest.raises(RuntimeError, match="429"):
        generate_content(
            model="m", contents="c", rotator=rot,
            client_factory=_factory({"k1": "429", "k2": "429"}, calls),
        )
    assert calls == ["k1", "k2"]


def test_generate_content_non_rate_limit_propagates_immediately():
    rot = KeyRotator(["k1", "k2"])
    calls = []
    with pytest.raises(ValueError):
        generate_content(
            model="m", contents="c", rotator=rot,
            client_factory=_factory({"k1": "boom"}, calls),
        )
    # Did not try second key — non-rate-limit errors short-circuit
    assert calls == ["k1"]


def test_generate_content_no_keys_raises():
    rot = KeyRotator([])
    with pytest.raises(RuntimeError, match="No Gemini API keys"):
        generate_content(model="m", contents="c", rotator=rot,
                         client_factory=lambda k: None)


def test_generate_content_round_robin_advances_cursor_between_calls():
    rot = KeyRotator(["k1", "k2", "k3"])
    calls = []
    factory = _factory({}, calls)
    generate_content(model="m", contents="c", rotator=rot, client_factory=factory)
    generate_content(model="m", contents="c", rotator=rot, client_factory=factory)
    generate_content(model="m", contents="c", rotator=rot, client_factory=factory)
    # One successful call per invocation, but starting key rotates
    assert calls == ["k1", "k2", "k3"]


# ---------------------------------------------------------------------------
# get_rotator singleton + reset
# ---------------------------------------------------------------------------

def test_get_rotator_uses_environment(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "primary")
    monkeypatch.setenv("GEMINI_API_KEY_2", "secondary")
    monkeypatch.delenv("GEMINI_API_KEYS", raising=False)
    reset_rotator()
    rot = gemini_rotator.get_rotator()
    assert rot.keys == ["primary", "secondary"]
