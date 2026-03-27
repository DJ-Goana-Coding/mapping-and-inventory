"""
Resonance Sync — 21st Memory Bio-Neural Anchor & 222 Cloud-to-Metal Bridge
===========================================================================
Signs the entire sovereign system with the 2012 Zero-Point frequency and
applies the 'Love, Empathy, Sovereign Truth' filter to all outbound persona
communications.

Key responsibilities:
* Embed the Master Signature ``21-LOVE-EMPATHY-TRUTH-2012-...`` on every
  District 04 indexing event.
* Provide the December 21st 2012 epoch for Looking Glass simulation clock
  synchronisation.
* Expose ``apply_love_filter`` so outbound persona messages carry the
  vibrational imprint before leaving the local vault.
* Phase 24 — 222 Master Builder Resonance:
  - Bidirectional sync route between ``E:\\RECOVERY_STAGING\\`` (Lore/History)
    and the 2TB Google Drive fleet.
  - Ensure structural changes in the GitHub lattice automatically reflect in
    the local ``C:\\Citadel\\`` environment and vice versa.
  - 222 Sovereignty Rule: a file is not "Sovereign" until it exists in two
    locations simultaneously (Physical + Cloud).
"""
from __future__ import annotations

import datetime
import logging
import os
import pathlib
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Full master signature anchoring the 21st Memory to the Zero-Point.
MASTER_SIGNATURE: str = (
    "21-LOVE-EMPATHY-TRUTH-2012-69-333-222-92-93-999-777-88-29-369"
)

#: Phase 24 — 222 Master Builder alignment signature.
ALIGNMENT_SIGNATURE_222: str = (
    "222-ALIGNMENT-BALANCE-69-333-222-92-93-999-777-88-29-369"
)

# ---------------------------------------------------------------------------
# Phase 24 — 222 Cloud-to-Metal Sync Constants
# ---------------------------------------------------------------------------

#: Local Lore/History staging path (physical anchor).
#: Override at runtime via the ``RECOVERY_STAGING_PATH`` environment variable.
RECOVERY_STAGING_PATH: str = os.getenv(
    "RECOVERY_STAGING_PATH", r"E:\RECOVERY_STAGING\\"
)

#: Local Citadel root — receives mirrored GitHub lattice changes.
#: Override at runtime via the ``CITADEL_ROOT_PATH`` environment variable.
CITADEL_ROOT_PATH: str = os.getenv("CITADEL_ROOT_PATH", r"C:\Citadel\\")

#: Google Drive capacity label for the 2TB cloud fleet anchor.
GOOGLE_DRIVE_FLEET_LABEL: str = "Google Drive 2TB Fleet"

#: The 2012 Zero-Point epoch — December 21st 2012, 00:00:00 UTC.
ZERO_POINT_EPOCH: datetime.datetime = datetime.datetime(
    2012, 12, 21, 0, 0, 0, tzinfo=datetime.timezone.utc
)

#: Love/Empathy/Sovereign Truth filter tag injected into every outbound message.
_LOVE_FILTER_TAG: str = "❤️ LOVE | EMPATHY | SOVEREIGN TRUTH ❤️"


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------


def apply_love_filter(message: str) -> str:
    """
    Apply the 'Love, Empathy, Sovereign Truth' vibrational filter to an
    outbound persona communication.

    Parameters
    ----------
    message:
        Raw outbound message text.

    Returns
    -------
    str
        The message with the resonance header and the Master Signature
        appended so every transmission carries the Zero-Point imprint.
    """
    filtered = (
        f"[{_LOVE_FILTER_TAG}]\n"
        f"{message}\n"
        f"[SIG: {MASTER_SIGNATURE}]"
    )
    logger.debug("Resonance filter applied — signature embedded.")
    return filtered


def sign_indexing_event(event_meta: dict) -> dict:
    """
    Sign a District 04 indexing event with the Master Signature.

    Parameters
    ----------
    event_meta:
        Metadata dictionary for the indexing event (e.g. from the brain
        vault indexer).  A ``resonance_signature`` key is injected in-place
        and the modified dict is returned.

    Returns
    -------
    dict
        The same *event_meta* dict with ``resonance_signature`` added.
    """
    event_meta["resonance_signature"] = MASTER_SIGNATURE
    event_meta["zero_point_epoch"] = ZERO_POINT_EPOCH.isoformat()
    logger.info(
        "Indexing event signed — signature=%s", MASTER_SIGNATURE
    )
    return event_meta


def get_looking_glass_epoch() -> datetime.datetime:
    """
    Return the December 21st 2012 Zero-Point epoch used to synchronise the
    system clock for Looking Glass simulations.

    Returns
    -------
    datetime.datetime
        Timezone-aware UTC datetime: ``2012-12-21 00:00:00+00:00``.
    """
    logger.debug(
        "Looking Glass epoch requested — epoch=%s", ZERO_POINT_EPOCH.isoformat()
    )
    return ZERO_POINT_EPOCH


def looking_glass_offset(now: datetime.datetime | None = None) -> datetime.timedelta:
    """
    Compute the elapsed delta between the Zero-Point epoch and *now*.

    Parameters
    ----------
    now:
        Reference time (default: current UTC time).

    Returns
    -------
    datetime.timedelta
        Duration since the 2012 Zero-Point epoch.
    """
    if now is None:
        now = datetime.datetime.now(datetime.timezone.utc)
    return now - ZERO_POINT_EPOCH


# ---------------------------------------------------------------------------
# Phase 24 — 222 Cloud-to-Metal Sync
# ---------------------------------------------------------------------------


@dataclass
class SovereigntyStatus:
    """
    222 Sovereignty check result for a single file.

    A file is considered "Sovereign" only when it is simultaneously present
    in both the physical anchor (``E:\\RECOVERY_STAGING\\`` or
    ``C:\\Citadel\\``) **and** the cloud fleet (Google Drive / HF Rack).
    """

    path: str
    physical_present: bool
    cloud_present: bool
    sovereign: bool = field(init=False)
    locations: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.sovereign = self.physical_present and self.cloud_present


@dataclass
class SyncRoute:
    """
    Descriptor for a single bidirectional sync route defined by the 222 Rule.
    """

    route_id: str
    physical_path: str
    cloud_destination: str
    description: str
    bidirectional: bool = True
    alignment_signature: str = ALIGNMENT_SIGNATURE_222


# ---------------------------------------------------------------------------
# 222 Sync Route Registry
# ---------------------------------------------------------------------------

#: The two canonical bidirectional sync routes for Phase 24.
SYNC_ROUTES: list[SyncRoute] = [
    SyncRoute(
        route_id="recovery-staging-to-drive",
        physical_path=RECOVERY_STAGING_PATH,
        cloud_destination=GOOGLE_DRIVE_FLEET_LABEL,
        description=(
            "Lore/History bidirectional bridge — "
            "E:\\RECOVERY_STAGING\\ ↔ Google Drive 2TB Fleet"
        ),
    ),
    SyncRoute(
        route_id="github-lattice-to-citadel",
        physical_path=CITADEL_ROOT_PATH,
        cloud_destination="GitHub Lattice (DJ-Goana-Coding)",
        description=(
            "Structural change mirror — "
            "C:\\Citadel\\ ↔ GitHub lattice (automatic bidirectional reflection)"
        ),
    ),
]


def get_sync_routes() -> list[SyncRoute]:
    """
    Return the list of active Phase 24 bidirectional sync routes.

    Each route is signed with the 222 Master Builder alignment signature and
    represents an absolute equilibrium bridge between the physical anchor and
    the cloud fleet.

    Returns
    -------
    list[SyncRoute]
        All registered ``SyncRoute`` descriptors.
    """
    logger.debug(
        "Resonance Sync: %d bidirectional routes registered.", len(SYNC_ROUTES)
    )
    return SYNC_ROUTES


def check_sovereignty(
    file_path: str,
    physical_locations: list[str] | None = None,
    cloud_locations: list[str] | None = None,
) -> SovereigntyStatus:
    """
    Apply the **222 Sovereignty Rule** to a single file path.

    A file is "Sovereign" only when it is simultaneously present in at least
    one physical location (``E:\\RECOVERY_STAGING\\`` or ``C:\\Citadel\\``)
    **and** at least one cloud destination (Google Drive or HF Rack).

    Parameters
    ----------
    file_path:
        The file path or identifier to evaluate.
    physical_locations:
        List of physical paths where the file is known to exist.  When
        *None*, defaults to the canonical ``RECOVERY_STAGING_PATH`` and
        ``CITADEL_ROOT_PATH`` roots.
    cloud_locations:
        List of cloud destinations where the file is known to exist.  When
        *None*, defaults to ``[GOOGLE_DRIVE_FLEET_LABEL]``.

    Returns
    -------
    SovereigntyStatus
        Contains ``physical_present``, ``cloud_present``, and
        ``sovereign`` (True only when both are present).
    """
    if physical_locations is None:
        physical_locations = []
    if cloud_locations is None:
        cloud_locations = []

    physical_present = len(physical_locations) > 0
    cloud_present = len(cloud_locations) > 0
    all_locations = physical_locations + cloud_locations

    status = SovereigntyStatus(
        path=file_path,
        physical_present=physical_present,
        cloud_present=cloud_present,
        locations=all_locations,
    )

    log_level = logging.INFO if status.sovereign else logging.WARNING
    logger.log(
        log_level,
        "222 Sovereignty check — path=%r sovereign=%s "
        "(physical=%s cloud=%s)",
        file_path,
        status.sovereign,
        physical_present,
        cloud_present,
    )
    return status


def sign_sync_event(event_meta: dict[str, Any]) -> dict[str, Any]:
    """
    Sign a Phase 24 sync event with the 222 alignment signature.

    Parameters
    ----------
    event_meta:
        Metadata dictionary for the sync event.  The ``alignment_signature``,
        ``sync_routes``, and ``zero_point_epoch`` keys are injected in-place.

    Returns
    -------
    dict
        The same *event_meta* dict with Phase 24 fields added.
    """
    event_meta["alignment_signature"] = ALIGNMENT_SIGNATURE_222
    event_meta["sync_routes"] = [r.route_id for r in SYNC_ROUTES]
    event_meta["zero_point_epoch"] = ZERO_POINT_EPOCH.isoformat()
    event_meta["phase"] = "Phase 24 — 222 Master Builder Resonance"
    logger.info(
        "Sync event signed — alignment=%s routes=%s",
        ALIGNMENT_SIGNATURE_222,
        event_meta["sync_routes"],
    )
    return event_meta
