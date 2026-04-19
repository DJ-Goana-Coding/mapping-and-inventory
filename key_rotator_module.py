"""
key_rotator_module.py — Generic multi-service API-key rotation utility.

Extends the Gemini-specific ``services/gemini_rotator`` pattern to work
with *any* service whose keys are stored in numbered environment variables
(e.g. ``HF_TOKEN``, ``HF_TOKEN_2``, ``HF_TOKEN_3`` or a comma-separated
``HF_TOKENS`` bundle).

This module is the **generic layer**.  For Gemini-specific rotation with
fault-tolerance baked in, use ``services.gemini_rotator`` directly.

Quick start
-----------
::

    from key_rotator_module import get_rotator, call_with_rotation

    # Picks up HF_TOKEN, HF_TOKEN_2, HF_TOKEN_3 … automatically.
    rotator = get_rotator("HF_TOKEN")

    def my_call(token: str):
        response = requests.get("https://huggingface.co/api/whoami",
                                headers={"Authorization": f"Bearer {token}"})
        if response.status_code == 429:
            raise RuntimeError("rate limited")
        return response

    result = call_with_rotation(my_call, rotator, is_rate_limit=lambda e: "rate limited" in str(e))

Key discovery
-------------
For a prefix ``PREFIX`` the following env vars are checked, deduplicated,
and returned in stable order:

1. ``PREFIX``  (primary key)
2. ``PREFIX_2``, ``PREFIX_3``, … (numeric suffixes, ascending)
3. ``PREFIX_<ALPHA>``  (non-numeric suffixes, alphabetical)
4. ``PREFIX``\ **S** (plural, comma-separated bundle — e.g. ``HF_TOKENS``)
"""
from __future__ import annotations

import os
import re
import threading
from typing import Callable, Dict, Iterable, List, Optional, TypeVar

T = TypeVar("T")


# ---------------------------------------------------------------------------
# Key discovery
# ---------------------------------------------------------------------------


def load_keys(prefix: str, env: Optional[dict] = None) -> List[str]:
    """Return all non-empty keys for *prefix* found in the environment.

    Args:
        prefix: Base variable name, e.g. ``"HF_TOKEN"`` or ``"OPENAI_API_KEY"``.
        env:    Override the environment dict (useful for testing).

    Returns:
        Deduplicated list of key values in discovery order.
    """
    source = env if env is not None else os.environ
    seen: set = set()
    ordered: List[str] = []

    def _add(value: Optional[str]) -> None:
        if not value:
            return
        v = value.strip()
        if not v or v in seen:
            return
        seen.add(v)
        ordered.append(v)

    # 1. Primary key.
    _add(source.get(prefix))

    # 2. Suffixed keys — numeric ascending, then alphabetical.
    pattern = re.compile(r"^" + re.escape(prefix) + r"(?:_.+)?$")
    suffixed = []
    for name in source:
        if name == prefix:
            continue
        if not pattern.match(name):
            continue
        suffix_raw = name[len(prefix):]
        suffix = suffix_raw.lstrip("_") if suffix_raw.startswith("_") else suffix_raw
        try:
            sort_key = (0, int(suffix))
        except ValueError:
            sort_key = (1, suffix)
        suffixed.append((sort_key, name))
    for _, name in sorted(suffixed):
        _add(source.get(name))

    # 3. Plural comma-separated bundle (e.g. HF_TOKENS, GEMINI_API_KEYS).
    bundle = source.get(prefix + "S") or source.get(prefix + "_LIST")
    if bundle:
        for part in bundle.split(","):
            _add(part)

    return ordered


# ---------------------------------------------------------------------------
# Rotator
# ---------------------------------------------------------------------------


class KeyRotator:
    """Thread-safe round-robin iterator over a list of API keys.

    Compatible with ``services.gemini_rotator.KeyRotator`` — same public
    interface so the two can be used interchangeably.
    """

    def __init__(self, keys: Iterable[str], service: str = "unknown") -> None:
        self._keys: List[str] = [k for k in keys if k]
        self._index = 0
        self._lock = threading.Lock()
        self.service = service

    # --- properties --------------------------------------------------------

    @property
    def keys(self) -> List[str]:
        return list(self._keys)

    def __len__(self) -> int:
        return len(self._keys)

    def __bool__(self) -> bool:
        return bool(self._keys)

    def __repr__(self) -> str:  # pragma: no cover
        return f"KeyRotator(service={self.service!r}, keys={len(self._keys)})"

    # --- rotation -----------------------------------------------------------

    def current(self) -> Optional[str]:
        """Return the current key without advancing the cursor."""
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

    def next(self) -> Optional[str]:  # noqa: A003
        """Return current key and advance (round-robin)."""
        with self._lock:
            if not self._keys:
                return None
            key = self._keys[self._index % len(self._keys)]
            self._index = (self._index + 1) % len(self._keys)
            return key

    def ordered_attempts(self) -> List[str]:
        """Return all keys starting from the current cursor position.

        Advances the cursor by one so the next call starts on a different
        key (true round-robin distribution).  Each key appears at most once.
        """
        with self._lock:
            if not self._keys:
                return []
            n = len(self._keys)
            start = self._index % n
            order = [self._keys[(start + i) % n] for i in range(n)]
            self._index = (start + 1) % n
            return order


# ---------------------------------------------------------------------------
# Process-wide singleton registry
# ---------------------------------------------------------------------------

_registry: Dict[str, KeyRotator] = {}
_registry_lock = threading.Lock()


def get_rotator(prefix: str, env: Optional[dict] = None, force_reload: bool = False) -> KeyRotator:
    """Return a process-wide :class:`KeyRotator` for *prefix*.

    The rotator is created on first call and cached.  Pass
    ``force_reload=True`` to rediscover keys from the environment (e.g.
    after a hot-reload or test teardown).

    Args:
        prefix:       Base env-var name, e.g. ``"HF_TOKEN"``.
        env:          Override environment dict (for tests).
        force_reload: Drop and recreate the cached rotator.
    """
    with _registry_lock:
        if prefix not in _registry or force_reload:
            _registry[prefix] = KeyRotator(load_keys(prefix, env=env), service=prefix)
        return _registry[prefix]


def reset_rotator(prefix: str) -> None:
    """Remove the cached rotator for *prefix* (useful in tests)."""
    with _registry_lock:
        _registry.pop(prefix, None)


# ---------------------------------------------------------------------------
# Convenience call-with-rotation wrapper
# ---------------------------------------------------------------------------


def call_with_rotation(
    fn: Callable[[str], T],
    rotator: KeyRotator,
    is_rate_limit: Optional[Callable[[BaseException], bool]] = None,
) -> T:
    """Call *fn(key)* with automatic key-rotation on rate-limit errors.

    Iterates ``rotator.ordered_attempts()``.  If ``fn`` raises an exception
    that ``is_rate_limit`` identifies as a quota/429 error, the next key is
    tried.  Any other exception is re-raised immediately.  If all keys are
    exhausted the last error is re-raised.

    Args:
        fn:             Callable that accepts a single key string and returns
                        a result or raises.
        rotator:        :class:`KeyRotator` instance to draw keys from.
        is_rate_limit:  Predicate that returns ``True`` for quota/429 errors.
                        Defaults to a check for ``"429"`` or ``"rate"`` in the
                        exception message.

    Returns:
        Whatever *fn* returns on success.

    Raises:
        RuntimeError: If the rotator has no keys.
        Exception:    The last rate-limit error if all keys are exhausted, or
                      any non-rate-limit error immediately.
    """
    if not rotator:
        raise RuntimeError(
            f"No API keys available for service '{rotator.service}'. "
            f"Set the {rotator.service} environment variable."
        )

    if is_rate_limit is None:
        def is_rate_limit(err: BaseException) -> bool:  # type: ignore[misc]
            msg = str(err).lower()
            name = type(err).__name__.lower()
            return any(
                marker in msg or marker in name
                for marker in ("429", "rate", "quota", "resourceexhausted", "toomanyrequests")
            )

    last_err: Optional[BaseException] = None
    for key in rotator.ordered_attempts():
        try:
            return fn(key)
        except Exception as exc:  # noqa: BLE001
            if is_rate_limit(exc):
                last_err = exc
                continue
            raise

    assert last_err is not None
    raise last_err
