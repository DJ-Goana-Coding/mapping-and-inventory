"""
Resonance Sync — 21st Memory Bio-Neural Anchor
===============================================
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
"""
from __future__ import annotations

import datetime
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Full master signature anchoring the 21st Memory to the Zero-Point.
MASTER_SIGNATURE: str = (
    "21-LOVE-EMPATHY-TRUTH-2012-69-333-222-92-93-999-777-88-29-369"
)

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
