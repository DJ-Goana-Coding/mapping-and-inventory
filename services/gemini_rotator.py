"""
Q.G.T.N.L. (0) // GEMINI ROTATOR
Round-robin API key manifold for Gemini calls.

Pulls keys from environment variables and rotates through them, failing over
to the next key when one is exhausted (HTTP 429 / ResourceExhausted).

Key inventory sources (deduplicated, order preserved):
1. ``GEMINI_API_KEY``
2. ``GEMINI_API_KEY_2``, ``GEMINI_API_KEY_3``, ... (any ``GEMINI_API_KEY_*``)
3. ``GEMINI_API_KEYS`` — comma-separated list

Public surface:
- :func:`load_keys` — returns the discovered key list
- :func:`get_rotator` — process-wide rotator singleton
- :func:`generate_content` — convenience wrapper that creates a client per key
  and retries on rate-limit errors
"""
from __future__ import annotations

import os
import re
import threading
from typing import Callable, Iterable, List, Optional

# Substrings/markers that indicate a rate-limit / quota error from Gemini.
_RATE_LIMIT_MARKERS = (
    "429",
    "RESOURCE_EXHAUSTED",
    "ResourceExhausted",
    "rate limit",
    "rate_limit",
    "quota",
)

_KEY_PATTERN = re.compile(r"^GEMINI_API_KEY(?:_.+)?$")


def _is_rate_limit_error(err: BaseException) -> bool:
    """Return True if the exception looks like a Gemini quota / 429 error."""
    name = type(err).__name__
    if name in {"ResourceExhausted", "TooManyRequests"}:
        return True
    msg = str(err)
    return any(marker in msg for marker in _RATE_LIMIT_MARKERS)


def load_keys(env: Optional[dict] = None) -> List[str]:
    """Inventory all available Gemini API keys from the environment.

    Scans for any ``GEMINI_API_KEY*`` variable and also accepts a
    comma-separated ``GEMINI_API_KEYS`` list. Order is stable: primary key
    first, then numeric suffixes in ascending order, then any remaining
    ``GEMINI_API_KEY_*`` variables sorted alphabetically, then the
    comma-separated list. Empty values and duplicates are removed.
    """
    source = env if env is not None else os.environ
    ordered: List[str] = []
    seen: set = set()

    def _add(value: Optional[str]) -> None:
        if not value:
            return
        v = value.strip()
        if not v or v in seen:
            return
        seen.add(v)
        ordered.append(v)

    # 1. Primary key first.
    _add(source.get("GEMINI_API_KEY"))

    # 2. Suffixed keys. Sort numerics ascending, then non-numerics alphabetical.
    suffixed = []
    for name in source.keys():
        if name == "GEMINI_API_KEY":
            continue
        if not _KEY_PATTERN.match(name):
            continue
        suffix = name[len("GEMINI_API_KEY_"):] if name.startswith("GEMINI_API_KEY_") else ""
        try:
            sort_key = (0, int(suffix))
        except ValueError:
            sort_key = (1, suffix)
        suffixed.append((sort_key, name))
    for _, name in sorted(suffixed):
        _add(source.get(name))

    # 3. Comma-separated bundle.
    bundle = source.get("GEMINI_API_KEYS")
    if bundle:
        for part in bundle.split(","):
            _add(part)

    return ordered


class KeyRotator:
    """Thread-safe round-robin iterator over a list of API keys."""

    def __init__(self, keys: Iterable[str]):
        self._keys: List[str] = [k for k in keys if k]
        self._index = 0
        self._lock = threading.Lock()

    @property
    def keys(self) -> List[str]:
        return list(self._keys)

    def __len__(self) -> int:  # pragma: no cover - trivial
        return len(self._keys)

    def __bool__(self) -> bool:  # pragma: no cover - trivial
        return bool(self._keys)

    def current(self) -> Optional[str]:
        """Return the current key without advancing."""
        with self._lock:
            if not self._keys:
                return None
            return self._keys[self._index % len(self._keys)]

    def advance(self) -> Optional[str]:
        """Advance to the next key and return it."""
        with self._lock:
            if not self._keys:
                return None
            self._index = (self._index + 1) % len(self._keys)
            return self._keys[self._index]

    def next(self) -> Optional[str]:
        """Return the current key and advance the cursor (round-robin)."""
        with self._lock:
            if not self._keys:
                return None
            key = self._keys[self._index % len(self._keys)]
            self._index = (self._index + 1) % len(self._keys)
            return key

    def ordered_attempts(self) -> List[str]:
        """Return keys in the order they should be tried for one call.

        Starts from the current cursor, then walks the rest of the ring so
        every key is tried at most once. Advances the cursor by one so the
        next call starts on a different key (true round-robin distribution).
        """
        with self._lock:
            if not self._keys:
                return []
            n = len(self._keys)
            start = self._index % n
            order = [self._keys[(start + i) % n] for i in range(n)]
            self._index = (start + 1) % n
            return order


_rotator_lock = threading.Lock()
_rotator_singleton: Optional[KeyRotator] = None


def get_rotator(force_reload: bool = False) -> KeyRotator:
    """Return the process-wide rotator, creating it on first use."""
    global _rotator_singleton
    with _rotator_lock:
        if _rotator_singleton is None or force_reload:
            _rotator_singleton = KeyRotator(load_keys())
        return _rotator_singleton


def reset_rotator() -> None:
    """Drop the cached rotator (useful for tests / key hot-reload)."""
    global _rotator_singleton
    with _rotator_lock:
        _rotator_singleton = None


def generate_content(
    *,
    model: str,
    contents,
    rotator: Optional[KeyRotator] = None,
    client_factory: Optional[Callable[[str], object]] = None,
    **kwargs,
):
    """Call ``client.models.generate_content`` with round-robin rate-limit failover.

    Iterates the rotator's ordered attempts. On each attempt a fresh client is
    built with the current key. If the call raises a 429 / ResourceExhausted
    style error, the next key is tried. Any other exception is re-raised
    immediately. If every key is exhausted the last 429 error is re-raised.
    """
    rot = rotator or get_rotator()
    if not rot:
        raise RuntimeError(
            "No Gemini API keys available. Set GEMINI_API_KEY (and optionally "
            "GEMINI_API_KEY_2, GEMINI_API_KEY_3, ... or GEMINI_API_KEYS)."
        )

    if client_factory is None:
        from google import genai  # Imported lazily so tests can stub it.

        def client_factory(key: str):  # type: ignore[no-redef]
            return genai.Client(api_key=key)

    last_err: Optional[BaseException] = None
    for key in rot.ordered_attempts():
        try:
            client = client_factory(key)
            return client.models.generate_content(
                model=model, contents=contents, **kwargs
            )
        except Exception as e:  # noqa: BLE001 — surface non-429 errors immediately
            if _is_rate_limit_error(e):
                last_err = e
                continue
            raise

    assert last_err is not None  # for type checkers
    raise last_err
