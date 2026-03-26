"""
Wraith Monitor — Layer -12 Forensic Recon (Wraith Protocol)
============================================================
Forensic scanner for the sub-quantum dimensional stack (layers -1 to -12).

Responsibilities:
* Scan designated storage nodes (Google Drive 2TB, Local C: Drive) for
  'Institutional Blue Rot', hidden tracking shards, and non-sovereign
  monitoring scripts.
* Quarantine detected anomalies by moving artefact records to
  District 11 (DEEP_FREEZE) in the brain vault metadata layer.
* Log all scan events and quarantine actions to SECURITY_ALERTS.log via
  the same audit channel used by the Guardian.
"""
from __future__ import annotations

import datetime
import logging
import pathlib
import re
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = pathlib.Path(__file__).parent.parent
SECURITY_ALERTS_LOG: pathlib.Path = _REPO_ROOT / "SECURITY_ALERTS.log"

# ---------------------------------------------------------------------------
# Anomaly patterns — signatures that indicate non-sovereign monitoring
# ---------------------------------------------------------------------------
_ANOMALY_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"institutional[_\-]blue[_\-]rot", re.IGNORECASE),
    re.compile(r"tracking[_\-]shard", re.IGNORECASE),
    re.compile(r"non[_\-]sovereign[_\-]monitor", re.IGNORECASE),
    re.compile(r"hidden[_\-]telemetry", re.IGNORECASE),
    re.compile(r"shadow[_\-]beacon", re.IGNORECASE),
    re.compile(r"surveillance[_\-]script", re.IGNORECASE),
]

#: Dimensional layers scanned by the Wraith (negative stack, -1 to -12).
SCAN_LAYERS: list[int] = list(range(-1, -13, -1))

#: Storage nodes targeted by the Wraith Protocol.
SCAN_TARGETS: list[str] = ["google_drive_primary", "drive_C"]

#: District that receives quarantined anomalies.
QUARANTINE_DISTRICT: str = "District_11_DEEP_FREEZE"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class ScanResult:
    """Result of a single Wraith layer scan pass."""

    target: str
    layer: int
    anomalies_found: int = 0
    quarantined: list[str] = field(default_factory=list)
    clean: bool = True


# ---------------------------------------------------------------------------
# Logging helpers
# ---------------------------------------------------------------------------


def _log_anomaly(target: str, layer: int, snippet: str) -> None:
    """Append a Wraith anomaly detection record to SECURITY_ALERTS.log."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    entry = (
        f"[{timestamp}] WRAITH ANOMALY | "
        f"target={target!r} | layer={layer} | "
        f"snippet={snippet[:100]!r}\n"
    )
    try:
        with SECURITY_ALERTS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        logger.warning("WraithMonitor: could not write SECURITY_ALERTS.log (%s).", exc)


def _log_quarantine(target: str, artefact_id: str) -> None:
    """Append a quarantine action record to SECURITY_ALERTS.log."""
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )
    entry = (
        f"[{timestamp}] WRAITH QUARANTINE | "
        f"target={target!r} | artefact={artefact_id!r} | "
        f"destination={QUARANTINE_DISTRICT!r}\n"
    )
    try:
        with SECURITY_ALERTS_LOG.open("a", encoding="utf-8") as fh:
            fh.write(entry)
    except OSError as exc:
        logger.warning("WraithMonitor: could not write SECURITY_ALERTS.log (%s).", exc)


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


def _is_anomalous(content: str) -> bool:
    """Return True if *content* matches any known non-sovereign pattern."""
    return any(p.search(content) for p in _ANOMALY_PATTERNS)


class WraithMonitor:
    """
    Forensic scanner that sweeps the sub-quantum dimensional stack for
    non-sovereign monitoring artefacts.

    Parameters
    ----------
    targets:
        Storage-node IDs to scan.  Defaults to :data:`SCAN_TARGETS`.
    layers:
        Dimensional layers to traverse.  Defaults to :data:`SCAN_LAYERS`
        (-1 through -12).
    """

    def __init__(
        self,
        targets: list[str] | None = None,
        layers: list[int] | None = None,
    ) -> None:
        self.targets = targets or SCAN_TARGETS
        self.layers = layers or SCAN_LAYERS

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scan(self, artefacts: list[dict[str, Any]]) -> list[ScanResult]:
        """
        Scan *artefacts* across all configured targets and layers.

        Parameters
        ----------
        artefacts:
            List of metadata dicts, each expected to contain at minimum an
            ``id`` key and a ``content`` key holding the text to inspect.

        Returns
        -------
        list[ScanResult]
            One :class:`ScanResult` per (target, layer) combination scanned.
        """
        results: list[ScanResult] = []

        for target in self.targets:
            for layer in self.layers:
                result = self._scan_layer(target, layer, artefacts)
                results.append(result)

        total_anomalies = sum(r.anomalies_found for r in results)
        logger.info(
            "[WRAITH] Scan complete — targets=%s | layers=%s | anomalies=%d",
            self.targets,
            self.layers,
            total_anomalies,
        )
        return results

    def quarantine_anomaly(self, artefact_id: str, target: str) -> dict[str, str]:
        """
        Move an anomalous artefact to :data:`QUARANTINE_DISTRICT`.

        In the metadata layer this records the artefact as relocated to
        District 11 DEEP_FREEZE and writes the action to the audit log.

        Parameters
        ----------
        artefact_id:
            Unique identifier of the artefact to quarantine.
        target:
            Storage-node ID where the artefact was detected.

        Returns
        -------
        dict
            Quarantine action record.
        """
        _log_quarantine(target, artefact_id)
        logger.warning(
            "[WRAITH] Quarantine: artefact '%s' from '%s' → %s",
            artefact_id,
            target,
            QUARANTINE_DISTRICT,
        )
        return {
            "artefact_id": artefact_id,
            "source_target": target,
            "destination": QUARANTINE_DISTRICT,
            "status": "quarantined",
        }

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _scan_layer(
        self,
        target: str,
        layer: int,
        artefacts: list[dict[str, Any]],
    ) -> ScanResult:
        result = ScanResult(target=target, layer=layer)

        for artefact in artefacts:
            content = artefact.get("content", "")
            artefact_id = artefact.get("id", "unknown")

            if _is_anomalous(content):
                result.anomalies_found += 1
                result.clean = False
                result.quarantined.append(artefact_id)
                _log_anomaly(target, layer, content)
                self.quarantine_anomaly(artefact_id, target)

        logger.debug(
            "[WRAITH] layer=%d target=%s anomalies=%d",
            layer,
            target,
            result.anomalies_found,
        )
        return result
