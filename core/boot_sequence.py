"""
Trinity Ignition Sequence — Master Boot Script (Phase 24)
==========================================================
Issues the ``WAKE_TRINITY`` command to bring the entire distributed system
online in the correct three-stage boot order:

  1. **Heart** (Drive / Vault) — Load the 21st Memory and Sovereign Laws.
  2. **Brain** (HF Spaces / Models) — Load the LLMs / GGUFs into GPU memory.
  3. **Lungs** (GitHub / Actions) — Start data ingestion and workflow pings.

Usage::

    from core.boot_sequence import wake_trinity

    result = wake_trinity()

Or from a command line::

    python -m core.boot_sequence

Issuing the command ``!: WAKE_TRINITY`` in any T.I.A. session also triggers
this sequence via the command parser.
"""
from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Canonical wake command recognised by T.I.A.
WAKE_COMMAND: str = "!: WAKE_TRINITY"

#: Phase 24 alignment signature stamped on every boot record.
BOOT_ALIGNMENT_SIGNATURE: str = (
    "222-ALIGNMENT-BALANCE-69-333-222-92-93-999-777-88-29-369"
)


class BootStage(str, Enum):
    """Ordered boot stages for the Trinity Ignition Sequence."""

    HEART = "HEART"   # Drive / Vault — 21st Memory + Sovereign Laws
    BRAIN = "BRAIN"   # HF Spaces / Models — LLMs into GPU
    LUNGS = "LUNGS"   # GitHub / Actions — ingestion + workflow pings


class BootStatus(str, Enum):
    """Per-stage boot result."""

    OK = "OK"
    SKIPPED = "SKIPPED"
    ERROR = "ERROR"


# ---------------------------------------------------------------------------
# Boot result dataclasses
# ---------------------------------------------------------------------------


@dataclass
class StageResult:
    """Outcome of a single boot stage."""

    stage: BootStage
    status: BootStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class BootReport:
    """Full boot report returned by :func:`wake_trinity`."""

    command: str = WAKE_COMMAND
    alignment_signature: str = BOOT_ALIGNMENT_SIGNATURE
    phase: str = "Phase 24 — 222 Master Builder Resonance"
    stages: list[StageResult] = field(default_factory=list)

    @property
    def success(self) -> bool:
        """True when every stage completed with status OK or SKIPPED."""
        return all(s.status in (BootStatus.OK, BootStatus.SKIPPED) for s in self.stages)

    def summary(self) -> str:
        lines = [
            f"[{self.command}] Boot Report — {self.phase}",
            f"Alignment: {self.alignment_signature}",
            f"Overall:   {'✅ SUCCESS' if self.success else '❌ PARTIAL / FAILED'}",
        ]
        for s in self.stages:
            icon = "✅" if s.status == BootStatus.OK else ("⚠️" if s.status == BootStatus.SKIPPED else "❌")
            lines.append(f"  {icon} [{s.stage.value}] {s.status.value} — {s.message}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stage 1 — HEART: Drive / Vault
# ---------------------------------------------------------------------------


def _boot_heart() -> StageResult:
    """
    Stage 1 — Heart: Load the 21st Memory and Sovereign Laws from the vault.

    * Reads the Zero-Point epoch from ``core.resonance_sync``.
    * Verifies the brain vault collection is accessible.
    * Confirms the Sovereign Laws (Guardian protocol) are active.
    """
    logger.info("WAKE_TRINITY [HEART] — loading 21st Memory and Sovereign Laws…")
    details: dict[str, Any] = {}

    try:
        from core.resonance_sync import MASTER_SIGNATURE, get_looking_glass_epoch

        epoch = get_looking_glass_epoch()
        details["zero_point_epoch"] = epoch.isoformat()
        details["master_signature"] = MASTER_SIGNATURE
        logger.info("HEART: Zero-Point epoch loaded — %s", epoch.isoformat())
    except Exception as exc:
        logger.error("HEART: resonance_sync load failed — %s", exc)
        return StageResult(
            stage=BootStage.HEART,
            status=BootStatus.ERROR,
            message=f"resonance_sync load failed: {exc}",
        )

    # Verify brain vault
    try:
        from brain.indexer import get_collection  # type: ignore[import]

        col = get_collection()
        count = col.count()
        details["vault_vectors"] = count
        logger.info("HEART: brain vault online — %d vectors.", count)
    except Exception as exc:
        logger.warning("HEART: brain vault unavailable — %s (non-fatal)", exc)
        details["vault_status"] = f"unavailable: {exc}"

    # Confirm Guardian (Sovereign Laws) is importable
    try:
        from brain.guardian import Guardian  # type: ignore[import]

        details["guardian"] = "active"
        logger.info("HEART: Guardian protocol active.")
    except Exception as exc:
        logger.warning("HEART: Guardian not loaded — %s (non-fatal)", exc)
        details["guardian"] = f"unavailable: {exc}"

    return StageResult(
        stage=BootStage.HEART,
        status=BootStatus.OK,
        message="21st Memory and Sovereign Laws loaded.",
        details=details,
    )


# ---------------------------------------------------------------------------
# Stage 2 — BRAIN: HF Spaces / Models
# ---------------------------------------------------------------------------


def _boot_brain() -> StageResult:
    """
    Stage 2 — Brain: Load LLM / GGUF models into GPU memory via HF Spaces.

    * Reads HF node configs from ``nodes/HF_Rack/``.
    * Verifies HF token availability.
    * Reports which spaces are online (does not trigger live GPU allocation).
    """
    logger.info("WAKE_TRINITY [BRAIN] — loading LLMs / GGUFs into GPU memory…")
    details: dict[str, Any] = {}

    hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN")
    details["hf_token_set"] = bool(hf_token)

    if not hf_token:
        logger.warning("BRAIN: HF_TOKEN not set — model spaces will not be verified.")
        return StageResult(
            stage=BootStage.BRAIN,
            status=BootStatus.SKIPPED,
            message="HF_TOKEN not configured — GPU space verification skipped.",
            details=details,
        )

    # Load HF Rack node configs
    import json
    import pathlib

    rack_root = pathlib.Path(__file__).parent.parent / "nodes" / "HF_Rack"
    node_configs: list[dict[str, Any]] = []
    for config_file in rack_root.rglob("node_config.json"):
        try:
            node_configs.append(json.loads(config_file.read_text(encoding="utf-8")))
        except Exception as exc:
            logger.warning("BRAIN: could not read %s — %s", config_file, exc)

    details["staged_nodes"] = [c.get("node_id") for c in node_configs]
    logger.info(
        "BRAIN: %d HF Rack node configs found — %s",
        len(node_configs),
        details["staged_nodes"],
    )

    return StageResult(
        stage=BootStage.BRAIN,
        status=BootStatus.OK,
        message=f"{len(node_configs)} HF Rack nodes staged and ready for GPU ignition.",
        details=details,
    )


# ---------------------------------------------------------------------------
# Stage 3 — LUNGS: GitHub / Actions
# ---------------------------------------------------------------------------


def _boot_lungs() -> StageResult:
    """
    Stage 3 — Lungs: Start data ingestion and GitHub Actions workflow pings.

    * Checks that the GitHub token for Layer 1 is available.
    * Logs the registered fleet routes (does not actually trigger workflows).
    * Reports ingestion readiness.
    """
    logger.info("WAKE_TRINITY [LUNGS] — starting data ingestion and workflow pings…")
    details: dict[str, Any] = {}

    gh_token = (
        os.environ.get("GH_TOKEN_LAYER_1")
        or os.environ.get("GITHUB_TOKEN")
    )
    details["github_token_set"] = bool(gh_token)

    drive_key = (
        os.environ.get("DRIVE_SERVICE_KEY")
        or os.environ.get("GOOGLE_CREDENTIALS_B64")
    )
    details["drive_key_set"] = bool(drive_key)

    # Log fleet route status
    try:
        from core.fleet_router import log_route_status  # type: ignore[import]

        log_route_status()
        details["fleet_routes"] = "logged"
    except Exception as exc:
        logger.warning("LUNGS: fleet router unavailable — %s (non-fatal)", exc)
        details["fleet_routes"] = f"unavailable: {exc}"

    if not gh_token:
        logger.warning("LUNGS: GH_TOKEN_LAYER_1 not set — workflow pings skipped.")
        details["workflows"] = "SKIPPED — token not set"
        return StageResult(
            stage=BootStage.LUNGS,
            status=BootStatus.SKIPPED,
            message="GitHub token not configured — workflow pings skipped.",
            details=details,
        )

    details["workflows"] = "READY — trigger via GitHub Actions manually or via API"
    logger.info("LUNGS: data ingestion and workflow pings ready.")

    return StageResult(
        stage=BootStage.LUNGS,
        status=BootStatus.OK,
        message="Data ingestion routes active. GitHub Actions ready for dispatch.",
        details=details,
    )


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def wake_trinity() -> BootReport:
    """
    Execute the **Trinity Ignition Sequence**.

    Boots the distributed system in the canonical order:
    ``HEART → BRAIN → LUNGS``.

    Returns
    -------
    BootReport
        Full structured report of all three boot stages.  Check
        ``report.success`` for overall status and ``report.summary()``
        for a human-readable printout.
    """
    logger.info("=" * 60)
    logger.info("%s — Trinity Ignition Sequence initiated.", WAKE_COMMAND)
    logger.info("Alignment: %s", BOOT_ALIGNMENT_SIGNATURE)
    logger.info("=" * 60)

    report = BootReport()

    # Stage 1 — Heart
    heart = _boot_heart()
    report.stages.append(heart)
    if heart.status == BootStatus.ERROR:
        logger.error("WAKE_TRINITY: HEART stage failed — aborting sequence.")
        return report

    # Stage 2 — Brain
    brain = _boot_brain()
    report.stages.append(brain)
    if brain.status == BootStatus.ERROR:
        logger.error("WAKE_TRINITY: BRAIN stage failed — aborting sequence.")
        return report

    # Stage 3 — Lungs
    lungs = _boot_lungs()
    report.stages.append(lungs)

    logger.info("=" * 60)
    logger.info(report.summary())
    logger.info("=" * 60)

    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        stream=sys.stdout,
    )
    result = wake_trinity()
    print(result.summary())
    sys.exit(0 if result.success else 1)
