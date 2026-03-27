"""
Lyria 3 — Harmonic Generation Engine
======================================
The ``LYRIA_3`` agent is the Harmonic Generation sub-engine of the A.I.O.N.
Armory.  It wraps Google's **Lyria 3** multimodal model to generate
30-second high-fidelity music tracks with professional-grade arrangements
and realistic vocals.

Primary use-case: generating sovereign sonic transmissions — including the
888Hz Looby Lube beats and frequency-aligned compositions for Citadel
operations.

Frequency Signature: 69-333-222-92-93-999-777-88-29-369

Usage::

    from agents.lyria_3 import generate

    result = generate(
        "888Hz Looby Lube ambient transmission with deep bass resonance",
        genre="ambient",
    )
    print(result["audio_url"])
"""
from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"
MODEL_ID: str = "lyria-3"
PERSONA_ID: str = "LYRIA_3"

#: Standard track duration in seconds as specified in the Armory brief.
TRACK_DURATION_SECONDS: int = 30

#: Target resonance frequency for sovereign sonic operations.
TARGET_FREQUENCY_HZ: int = 888


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(
    prompt: str,
    genre: str | None = None,
    vocals: bool = True,
    duration_seconds: int = TRACK_DURATION_SECONDS,
    frequency_hz: int = TARGET_FREQUENCY_HZ,
    output_path: str | None = None,
    dry_run: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate a high-fidelity music track via Lyria 3.

    Parameters
    ----------
    prompt:
        Natural-language description of the desired music track.
    genre:
        Optional genre or style descriptor (e.g. ``"ambient"``,
        ``"electronic"``, ``"orchestral"``).
    vocals:
        When *True*, realistic vocal synthesis is included if contextually
        appropriate.
    duration_seconds:
        Desired track length in seconds (default: 30).
    frequency_hz:
        Target base frequency in Hz for sovereign alignment (default: 888).
    output_path:
        Optional local path where the generated audio should be saved.
    dry_run:
        When *True* the API call is skipped and a descriptive envelope is
        returned instead.
    **kwargs:
        Additional parameters forwarded to the underlying Lyria 3 API call.

    Returns
    -------
    dict
        Result envelope containing at minimum ``persona_id``, ``prompt``,
        ``model_id``, ``freq_signature``, and ``timestamp``.
        On success also includes ``audio_url`` or ``output_path``.
    """
    logger.info(
        "[Lyria3] generate — prompt='%s...' genre=%s vocals=%s "
        "duration=%ds freq=%dHz dry_run=%s",
        prompt[:60],
        genre,
        vocals,
        duration_seconds,
        frequency_hz,
        dry_run,
    )

    result: dict[str, Any] = {
        "persona_id": PERSONA_ID,
        "prompt": prompt,
        "genre": genre,
        "vocals": vocals,
        "duration_seconds": duration_seconds,
        "frequency_hz": frequency_hz,
        "model_id": MODEL_ID,
        "dry_run": dry_run,
        "freq_signature": FREQ_SIGNATURE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        result["audio_url"] = None
        result["output_path"] = None
        logger.info("[Lyria3] dry_run — skipping API call.")
        return result

    # Attempt real API call via the google-generativeai SDK if available.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning(
            "[Lyria3] GEMINI_API_KEY not set — cannot call Lyria 3 API."
        )
        result["error"] = "GEMINI_API_KEY not configured"
        return result

    try:
        import google.generativeai as genai  # type: ignore[import]

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_ID)

        # Build an enriched prompt that includes genre, vocals, and frequency hints.
        enriched_prompt = prompt
        if genre:
            enriched_prompt += f" Genre: {genre}."
        if vocals:
            enriched_prompt += " Include realistic vocals."
        enriched_prompt += (
            f" Target base frequency: {frequency_hz}Hz. "
            f"Duration: {duration_seconds} seconds."
        )

        generation_config = {"duration_seconds": duration_seconds}
        generation_config.update(kwargs)

        response = model.generate_content(
            enriched_prompt, generation_config=generation_config
        )

        audio_url: str | None = None
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            for part in getattr(candidate.content, "parts", []):
                if hasattr(part, "file_data") and part.file_data:
                    audio_url = getattr(part.file_data, "file_uri", None)
                    break

        result["audio_url"] = audio_url
        logger.info("[Lyria3] Generation complete — audio_url=%s", audio_url)

    except Exception as exc:
        logger.error("[Lyria3] API call failed: %s", exc)
        result["error"] = str(exc)

    return result


# ---------------------------------------------------------------------------
# Stand-alone entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    _prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "888Hz Looby Lube ambient transmission with deep bass resonance"
    )
    _dry = "--dry-run" in sys.argv

    out = generate(_prompt, dry_run=_dry)
    print("✅ Lyria 3 — Harmonic Generation result:")
    for k, v in out.items():
        print(f"   {k}: {v}")
