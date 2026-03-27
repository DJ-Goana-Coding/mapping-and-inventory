"""
Harvester — Drive Scanner
==========================
Python replacement for the legacy ``Harvester_Drive_Scanner.bat`` batch script.

Scans one or more storage nodes for model files (``*.gguf``, ``*.onnx``,
``*.safetensors``, ``*.bin``) and produces a structured inventory report.
Results are logged and optionally written to a JSON report file.

Authentication / paths
----------------------
All scan roots are supplied via the ``HARVESTER_ROOTS`` environment variable
(path-separator-delimited list of absolute paths — ``:`` on Unix, ``;`` on
Windows, i.e. ``os.pathsep``) or passed directly to :func:`scan`.
**No local Windows paths are hard-coded.**

Usage::

    import asyncio
    from agents.harvester import scan

    report = asyncio.run(scan())
    print(report)
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import pathlib
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Model-file extensions to harvest
# ---------------------------------------------------------------------------

HARVEST_EXTENSIONS: frozenset[str] = frozenset(
    {".gguf", ".onnx", ".safetensors", ".bin", ".pt", ".pth"}
)

# ---------------------------------------------------------------------------
# Report output path (relative to repo root)
# ---------------------------------------------------------------------------

_REPO_ROOT = pathlib.Path(__file__).parent.parent
DEFAULT_REPORT_PATH: pathlib.Path = _REPO_ROOT / "District_04_OUTPUT_HARVEST" / "harvester_report.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _resolve_roots() -> list[pathlib.Path]:
    """
    Resolve scan-root directories from the ``HARVESTER_ROOTS`` environment
    variable (colon-separated absolute paths).
    """
    raw = os.environ.get("HARVESTER_ROOTS", "")
    roots: list[pathlib.Path] = []
    for part in raw.split(os.pathsep):  # os.pathsep: ':' on Unix, ';' on Windows
        part = part.strip()
        if part:
            root_path = pathlib.Path(part)
            if root_path.exists():
                roots.append(root_path)
            else:
                logger.warning("[Harvester] Root path not found, skipping: %s", root_path)
    return roots


def _scan_root(root: pathlib.Path) -> list[dict[str, Any]]:
    """
    Walk *root* and collect metadata for every model file found.

    Returns a list of file-info dicts with ``path``, ``name``, ``suffix``,
    ``size_bytes``, and ``modified_utc``.
    """
    entries: list[dict[str, Any]] = []
    try:
        for filepath in root.rglob("*"):
            if not filepath.is_file():
                continue
            if filepath.suffix.lower() not in HARVEST_EXTENSIONS:
                continue
            try:
                stat = filepath.stat()
                entries.append(
                    {
                        "path": str(filepath),
                        "name": filepath.name,
                        "suffix": filepath.suffix.lower(),
                        "size_bytes": stat.st_size,
                        "modified_utc": datetime.fromtimestamp(
                            stat.st_mtime, tz=timezone.utc
                        ).isoformat(),
                    }
                )
            except OSError as exc:
                logger.warning("[Harvester] Could not stat '%s': %s", filepath, exc)
    except PermissionError as exc:
        logger.warning("[Harvester] Permission denied scanning '%s': %s", root, exc)
    return entries


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def scan(
    roots: list[str | pathlib.Path] | None = None,
    *,
    report_path: str | pathlib.Path | None = DEFAULT_REPORT_PATH,
    sanitize_paths: bool = True,
) -> dict[str, Any]:
    """
    Scan *roots* for model files and produce an inventory report.

    Parameters
    ----------
    roots:
        Directories to scan.  When ``None``, resolved from ``HARVESTER_ROOTS``
        env var.
    report_path:
        File to write the JSON report to.  Pass ``None`` to skip writing.
    sanitize_paths:
        When ``True`` (default), scrub local paths from the report before
        writing via the 'No Lemon' sanitizer.

    Returns
    -------
    dict
        Report with ``scanned_roots``, ``total_files``, ``total_size_bytes``,
        ``files`` list, and ``generated_utc`` timestamp.
    """
    if roots is None:
        resolved = _resolve_roots()
    else:
        resolved = [pathlib.Path(r) for r in roots]

    logger.info("[Harvester] Starting scan on %d root(s).", len(resolved))

    loop = asyncio.get_event_loop()
    all_entries: list[dict[str, Any]] = []

    for root in resolved:
        entries = await loop.run_in_executor(None, _scan_root, root)
        all_entries.extend(entries)
        logger.info(
            "[Harvester] Scanned '%s' — %d model file(s) found.", root, len(entries)
        )

    report: dict[str, Any] = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "scanned_roots": [str(r) for r in resolved],
        "total_files": len(all_entries),
        "total_size_bytes": sum(e["size_bytes"] for e in all_entries),
        "files": all_entries,
    }

    if sanitize_paths:
        try:
            from utils.path_sanitizer import sanitize_dict

            report = sanitize_dict(report)
        except ImportError:
            logger.warning("[Harvester] path_sanitizer not available — paths not scrubbed.")

    logger.info(
        "[Harvester] Scan complete — %d file(s), %.2f MB total.",
        report["total_files"],
        report["total_size_bytes"] / (1024 * 1024),
    )

    if report_path is not None:
        rp = pathlib.Path(report_path)
        rp.parent.mkdir(parents=True, exist_ok=True)
        with rp.open("w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        logger.info("[Harvester] Report written to %s.", rp)

    return report


if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _roots = [a for a in sys.argv[1:] if not a.startswith("--")] or None
    _report = asyncio.run(scan(roots=_roots))
    print(
        f"✅ Harvest complete — {_report['total_files']} file(s), "
        f"{_report['total_size_bytes'] / (1024 * 1024):.2f} MB"
    )
