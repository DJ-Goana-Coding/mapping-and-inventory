"""
'No Lemon' Path Sanitizer
=========================
Scrubs local Windows drive paths and usernames from strings before any data
is mirrored to cloud storage or logged to external systems.

Rules applied (in order)
------------------------
1. Replace Windows absolute paths (``C:\\…``, ``D:\\…`` etc.) with a
   ``<LOCAL_PATH>`` placeholder.
2. Replace Unix-style ``/home/<username>`` and ``/Users/<username>`` prefixes
   with ``<LOCAL_PATH>``.
3. Remove the value of the ``USERNAME``, ``USER``, and ``LOGNAME``
   environment variables wherever they appear in the string.
4. Remove the value of ``os.path.expanduser("~")`` if it appears.

Usage::

    from utils.path_sanitizer import sanitize

    safe = sanitize("Loaded model from C:\\\\Citadel\\\\Vault\\\\model.gguf")
    # → "Loaded model from <LOCAL_PATH>"
"""
from __future__ import annotations

import os
import re

# ---------------------------------------------------------------------------
# Compiled regex patterns
# ---------------------------------------------------------------------------

# Windows absolute paths: letter colon backslash (or forward-slash after the colon)
_WINDOWS_PATH_RE = re.compile(
    r"[A-Za-z]:[/\\][^\s,;\"']*",
    re.IGNORECASE,
)

# Unix /home/<user>/... or /Users/<user>/...
_UNIX_HOME_RE = re.compile(
    r"(?:/home/|/Users/)[^\s/,;\"']+(?:/[^\s,;\"']*)?",
    re.IGNORECASE,
)

_LOCAL_PATH_PLACEHOLDER = "<LOCAL_PATH>"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def sanitize(text: str) -> str:
    """
    Return a copy of *text* with local file system paths and usernames removed.

    Parameters
    ----------
    text:
        Arbitrary string that may contain Windows or Unix local paths.

    Returns
    -------
    str
        Sanitized string safe for cloud mirroring and external logging.
    """
    result = text

    # 1 — Windows paths
    result = _WINDOWS_PATH_RE.sub(_LOCAL_PATH_PLACEHOLDER, result)

    # 2 — Unix /home and /Users paths
    result = _UNIX_HOME_RE.sub(_LOCAL_PATH_PLACEHOLDER, result)

    # 3 — Literal username values from the environment
    for env_key in ("USERNAME", "USER", "LOGNAME"):
        username = os.environ.get(env_key, "").strip()
        if username:
            # Use word-boundary matching to avoid replacing substrings
            # (e.g. username 'test' must not alter 'testing')
            result = re.sub(
                r"(?<![A-Za-z0-9_])" + re.escape(username) + r"(?![A-Za-z0-9_])",
                "<USERNAME>",
                result,
            )

    # 4 — Expanded home directory string (e.g. ``/home/runner`` on Linux)
    home = os.path.expanduser("~")
    if home and home != "~":
        # Match the home path only when followed by a path separator or end-of-string
        # to avoid truncating longer paths that merely share a common prefix.
        result = re.sub(
            re.escape(home) + r"(?=[/\\]|$)",
            _LOCAL_PATH_PLACEHOLDER,
            result,
        )

    return result


def sanitize_dict(data: dict) -> dict:
    """
    Recursively sanitize all string values in *data*.

    Modifies a *copy* of the dict; the original is not changed.
    """
    result: dict = {}
    for key, value in data.items():
        if isinstance(value, str):
            result[key] = sanitize(value)
        elif isinstance(value, dict):
            result[key] = sanitize_dict(value)
        elif isinstance(value, list):
            result[key] = sanitize_list(value)
        else:
            result[key] = value
    return result


def sanitize_list(items: list) -> list:
    """Recursively sanitize all string values in *items*."""
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(sanitize(item))
        elif isinstance(item, dict):
            result.append(sanitize_dict(item))
        elif isinstance(item, list):
            result.append(sanitize_list(item))
        else:
            result.append(item)
    return result
