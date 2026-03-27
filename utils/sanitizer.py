"""
No-Lemon Sanitizer — Path Scrubber for Cloud Mirroring
=======================================================
Scrubs sensitive local Windows usernames and personal-directory fragments
from file paths before they are mirrored to any cloud endpoint (Google Drive,
HuggingFace, etc.).

This module **must** be applied to all path strings that originate from a
local Windows machine scan (e.g. MASTER_SYSTEM_MAP_2.csv) before they are
written to any cloud-facing manifest or log.

Usage::

    from utils.sanitizer import sanitize_path, sanitize_record

    clean = sanitize_path(r"C:\\Users\\chanc\\Downloads\\model.gguf")
    # → "C:\\Users\\<REDACTED>\\Downloads\\model.gguf"

    clean_row = sanitize_record({"FullName": r"C:\\Users\\chanc\\file.py", "Length": 123})
    # → {"FullName": "C:\\Users\\<REDACTED>\\file.py", "Length": 123}
"""
from __future__ import annotations

import logging
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Patterns to redact
# ---------------------------------------------------------------------------

# Replace any occurrence of known local Windows usernames in path strings.
# Add new usernames to this tuple as the fleet grows.
_USERNAME_PATTERNS: tuple[str, ...] = (
    "chanc",
)

# Compiled regex: matches each username surrounded by word-boundary / path
# separators so partial matches inside directory names are avoided.
_USERNAME_REGEX: re.Pattern[str] = re.compile(
    r"(?<=[/\\])(" + "|".join(re.escape(u) for u in _USERNAME_PATTERNS) + r")(?=[/\\]|$)",
    re.IGNORECASE,
)

_REDACTION_TOKEN: str = "<REDACTED>"

# Fields in a record dict that may contain path strings and should be scrubbed.
_PATH_FIELDS: frozenset[str] = frozenset(
    {"FullName", "path", "source_path", "local_path", "dest_path"}
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def sanitize_path(path: str) -> str:
    """
    Return *path* with any known local Windows username segments replaced by
    ``<REDACTED>``.

    Parameters
    ----------
    path:
        A file-system path string, potentially containing a local username.

    Returns
    -------
    str
        The sanitised path.
    """
    sanitised, count = _USERNAME_REGEX.subn(_REDACTION_TOKEN, path)
    if count:
        logger.debug("[NoLemon] Redacted %d username segment(s) in path.", count)
    return sanitised


def sanitize_record(record: dict[str, Any]) -> dict[str, Any]:
    """
    Return a shallow copy of *record* with all path-containing fields scrubbed.

    Only fields whose key is listed in :data:`_PATH_FIELDS` are processed;
    all other fields are passed through unchanged.

    Parameters
    ----------
    record:
        A dict row — e.g. one row from MASTER_SYSTEM_MAP_2.csv.

    Returns
    -------
    dict
        A new dict with sensitive path values replaced.
    """
    cleaned: dict[str, Any] = {}
    for key, value in record.items():
        if key in _PATH_FIELDS and isinstance(value, str):
            cleaned[key] = sanitize_path(value)
        else:
            cleaned[key] = value
    return cleaned


def sanitize_dataframe(df: Any) -> Any:
    """
    Return a copy of a pandas DataFrame with all path columns scrubbed.

    Requires ``pandas`` to be installed.  If pandas is not available the
    original *df* is returned unchanged with a warning.

    Parameters
    ----------
    df:
        A ``pandas.DataFrame`` — typically the loaded MASTER_SYSTEM_MAP_2.csv.

    Returns
    -------
    pandas.DataFrame
        A new DataFrame with sensitive columns sanitised.
    """
    try:
        import pandas as pd  # type: ignore[import]
    except ImportError:
        logger.warning("[NoLemon] pandas not available — dataframe sanitization skipped.")
        return df

    result = df.copy()
    for col in _PATH_FIELDS:
        if col in result.columns:
            result[col] = result[col].apply(
                lambda v: sanitize_path(v) if isinstance(v, str) else v
            )
    return result
