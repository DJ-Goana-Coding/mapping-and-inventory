"""
upgrade_dependencies.py — Phase 23 Medic Sweep
================================================
Automated dependency-upgrade script for the mapping-and-inventory Hub.

Parses ``requirements.txt``, attempts to upgrade each package to its latest
stable PyPI release using ``pip install --upgrade``, and rolls back to the
previous pinned version if the upgrade breaks the V23 architecture test suite
(currently defined as a successful ``python -c "import <pkg>"`` smoke-test).

Rollback failures and flagged packages are written to ``medic_audit.log`` at
the repository root.

Usage::

    python tasks/upgrade_dependencies.py [--dry-run]

sovereignty_layer : Phase 23 — Lattice Purification & Omniscient Sync
last_purified_date: 2026-03-26
"""
from __future__ import annotations

import logging
import os
import pathlib
import re
import subprocess
import sys
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = pathlib.Path(__file__).parent.parent
_REQUIREMENTS_FILE = _REPO_ROOT / "requirements.txt"
_AUDIT_LOG = _REPO_ROOT / "medic_audit.log"

# Regex to parse a requirements line like ``package==1.2.3`` or ``package>=1.0``
_REQ_LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z0-9_.\-]+)"
    r"(?:\[(?P<extras>[^\]]+)\])?"
    r"(?P<spec>[=<>!~][=<>!~0-9.a-zA-Z.*]+)?\s*$"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_requirements(path: pathlib.Path) -> list[dict[str, str]]:
    """Return a list of dicts with ``name``, ``extras``, and ``pinned`` keys."""
    pkgs = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        m = _REQ_LINE_RE.match(stripped)
        if m:
            pkgs.append(
                {
                    "name": m.group("name"),
                    "extras": m.group("extras") or "",
                    "pinned": (m.group("spec") or "").replace("==", ""),
                    "raw": stripped,
                }
            )
    return pkgs


def _pip(*args: str) -> subprocess.CompletedProcess:
    """Run ``pip`` with the given *args* and return the completed process."""
    return subprocess.run(
        [sys.executable, "-m", "pip", *args],
        capture_output=True,
        text=True,
    )


def _smoke_test(package_name: str) -> bool:
    """Return ``True`` if ``import <package_name>`` succeeds."""
    import_name = package_name.replace("-", "_").split(".")[0]
    result = subprocess.run(
        [sys.executable, "-c", f"import {import_name}"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def _append_audit(entry: dict[str, Any]) -> None:
    """Append a JSON audit entry to ``medic_audit.log``."""
    with _AUDIT_LOG.open("a", encoding="utf-8") as fh:
        import json

        fh.write(json.dumps(entry) + "\n")


# ---------------------------------------------------------------------------
# Core upgrade logic
# ---------------------------------------------------------------------------


def upgrade_package(pkg: dict[str, str], *, dry_run: bool = False) -> dict[str, Any]:
    """
    Attempt to upgrade *pkg* to its latest PyPI version.

    Returns a result dict with ``status`` (``"upgraded"``, ``"rolled_back"``,
    ``"unchanged"``, or ``"error"``), ``previous_version``, and
    ``new_version``.
    """
    name = pkg["name"]
    install_target = f"{name}[{pkg['extras']}]" if pkg["extras"] else name
    previous_version = pkg["pinned"]

    logger.info("[Medic] Checking upgrade for '%s' (current: %s)", name, previous_version or "unpinned")

    if dry_run:
        # In dry-run mode just query the latest version without installing
        result = _pip("index", "versions", name)
        latest = ""
        if result.returncode == 0:
            first_line = result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""
            m = re.search(r"\(([^)]+)\)", first_line)
            if m:
                latest = m.group(1)
        return {
            "package": name,
            "status": "dry_run",
            "previous_version": previous_version,
            "new_version": latest,
        }

    # Install latest
    upgrade_result = _pip("install", "--upgrade", "--quiet", install_target)
    if upgrade_result.returncode != 0:
        logger.warning("[Medic] Upgrade failed for '%s': %s", name, upgrade_result.stderr[:200])
        _append_audit(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "package": name,
                "status": "error",
                "detail": upgrade_result.stderr[:400],
            }
        )
        return {"package": name, "status": "error", "previous_version": previous_version, "new_version": None}

    # Smoke-test the upgraded package
    if not _smoke_test(name):
        logger.warning("[Medic] Smoke-test failed for '%s'. Rolling back.", name)
        if previous_version:
            rollback_result = _pip("install", "--quiet", f"{install_target}=={previous_version}")
            rollback_ok = rollback_result.returncode == 0
        else:
            rollback_ok = False
        _append_audit(
            {
                "timestamp": datetime.now(UTC).isoformat(),
                "package": name,
                "status": "rolled_back",
                "previous_version": previous_version,
                "rollback_ok": rollback_ok,
            }
        )
        return {
            "package": name,
            "status": "rolled_back",
            "previous_version": previous_version,
            "new_version": None,
        }

    # Determine installed version after upgrade
    show_result = _pip("show", name)
    new_version = previous_version
    for line in show_result.stdout.splitlines():
        if line.startswith("Version:"):
            new_version = line.split(":", 1)[1].strip()
            break

    status = "upgraded" if new_version != previous_version else "unchanged"
    if status == "upgraded":
        logger.info("[Medic] '%s' upgraded %s → %s", name, previous_version, new_version)
    else:
        logger.debug("[Medic] '%s' already at latest (%s).", name, new_version)

    return {
        "package": name,
        "status": status,
        "previous_version": previous_version,
        "new_version": new_version,
    }


def run_medic_sweep(*, dry_run: bool = False) -> list[dict[str, Any]]:
    """
    Execute the Medic Sweep across all packages in ``requirements.txt``.

    Parameters
    ----------
    dry_run:
        When ``True``, report what *would* change without installing anything.

    Returns
    -------
    list[dict]
        Per-package upgrade results.
    """
    packages = _parse_requirements(_REQUIREMENTS_FILE)
    logger.info(
        "[Medic] Starting Medic Sweep on %d packages (dry_run=%s).",
        len(packages),
        dry_run,
    )
    results = []
    for pkg in packages:
        result = upgrade_package(pkg, dry_run=dry_run)
        results.append(result)

    upgraded = [r for r in results if r["status"] == "upgraded"]
    rolled_back = [r for r in results if r["status"] == "rolled_back"]
    errors = [r for r in results if r["status"] == "error"]

    logger.info(
        "[Medic] Sweep complete — upgraded=%d, rolled_back=%d, errors=%d.",
        len(upgraded),
        len(rolled_back),
        len(errors),
    )
    if rolled_back or errors:
        logger.warning("[Medic] See %s for details.", _AUDIT_LOG)
    return results


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _dry = "--dry-run" in sys.argv
    results = run_medic_sweep(dry_run=_dry)

    # Pretty summary
    print("\n=== Medic Sweep Report ===")
    col = {"upgraded": "⬆", "rolled_back": "⏪", "unchanged": "✓", "dry_run": "🔍", "error": "✗"}
    for r in results:
        icon = col.get(r["status"], "?")
        prev = r.get("previous_version") or "unpinned"
        new = r.get("new_version") or "-"
        print(f"  {icon}  {r['package']:<35} {prev:<15} → {new}")

    if os.path.exists(_AUDIT_LOG):
        print(f"\n  [Medic] Audit log: {_AUDIT_LOG}")
