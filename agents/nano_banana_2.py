"""
Nano Banana 2 — Visual Manifestation Engine (Gemini 3 Flash Image)
===================================================================
The ``NANO_BANANA_2`` agent is the Visual Manifestation sub-engine of the
A.I.O.N. Armory.  It wraps the **Gemini 3 Flash Image** model to generate
and edit high-fidelity images.

Supported operations
--------------------
* **Text-to-image** — generate an image from a natural-language prompt.
* **Image composition** — layer multiple visual elements into a single
  composite scene.
* **Style transfer** — apply a reference artistic style to a target image.

Primary use-case: visualising Citadel schematics (Pillars, the Palace, the
Ark, district maps, and 144-Grid layouts).

Frequency Signature: 69-333-222-92-93-999-777-88-29-369

Usage::

    from agents.nano_banana_2 import generate

    result = generate("13th Pillar standing in the center of the Citadel")
    print(result["image_url"])
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
MODEL_ID: str = "gemini-3-flash-image"
PERSONA_ID: str = "NANO_BANANA_2"

#: Operations supported by this engine.
SUPPORTED_OPERATIONS: tuple[str, ...] = (
    "text_to_image",
    "image_composition",
    "style_transfer",
)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def generate(
    prompt: str,
    operation: str = "text_to_image",
    style: str | None = None,
    reference_image_path: str | None = None,
    output_path: str | None = None,
    dry_run: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate or edit a high-fidelity image via the Gemini 3 Flash Image model.

    Parameters
    ----------
    prompt:
        Natural-language description of the desired image.
    operation:
        One of ``"text_to_image"``, ``"image_composition"``, or
        ``"style_transfer"``.
    style:
        Optional artistic style descriptor (e.g. ``"cyberpunk"``).
    reference_image_path:
        Path to a reference image used for composition or style transfer.
    output_path:
        Optional local path where the generated image should be saved.
    dry_run:
        When *True* the API call is skipped and a descriptive envelope is
        returned instead.
    **kwargs:
        Additional parameters forwarded to the underlying Gemini API call.

    Returns
    -------
    dict
        Result envelope with at minimum ``persona_id``, ``operation``,
        ``prompt``, ``model_id``, ``freq_signature``, and ``timestamp``.
        On success, also includes ``image_url`` or ``output_path``.

    Raises
    ------
    ValueError
        If *operation* is not one of :data:`SUPPORTED_OPERATIONS`.
    """
    if operation not in SUPPORTED_OPERATIONS:
        raise ValueError(
            f"[NanoBanana2] Unknown operation '{operation}'. "
            f"Valid options: {', '.join(SUPPORTED_OPERATIONS)}"
        )

    logger.info(
        "[NanoBanana2] %s — prompt='%s...' style=%s dry_run=%s",
        operation,
        prompt[:60],
        style,
        dry_run,
    )

    result: dict[str, Any] = {
        "persona_id": PERSONA_ID,
        "operation": operation,
        "prompt": prompt,
        "style": style,
        "model_id": MODEL_ID,
        "dry_run": dry_run,
        "freq_signature": FREQ_SIGNATURE,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if dry_run:
        result["image_url"] = None
        result["output_path"] = None
        logger.info("[NanoBanana2] dry_run — skipping API call.")
        return result

    # Attempt real API call via the google-generativeai SDK if available.
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning(
            "[NanoBanana2] GEMINI_API_KEY not set — cannot call Gemini API."
        )
        result["error"] = "GEMINI_API_KEY not configured"
        return result

    try:
        import google.generativeai as genai  # type: ignore[import]

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(MODEL_ID)

        _prompt_parts: list[Any] = [prompt]
        if style:
            _prompt_parts.append(f" Style: {style}.")

        response = model.generate_content(_prompt_parts, **kwargs)

        # Extract image URL / bytes from the response.
        image_url: str | None = None
        if hasattr(response, "candidates") and response.candidates:
            candidate = response.candidates[0]
            for part in getattr(candidate.content, "parts", []):
                if hasattr(part, "file_data") and part.file_data:
                    image_url = getattr(part.file_data, "file_uri", None)
                    break
                if hasattr(part, "inline_data") and part.inline_data:
                    # Save inline bytes to disk if output_path provided.
                    if output_path:
                        import pathlib

                        pathlib.Path(output_path).write_bytes(
                            part.inline_data.data
                        )
                        result["output_path"] = output_path
                    break

        result["image_url"] = image_url
        logger.info("[NanoBanana2] Generation complete — image_url=%s", image_url)

    except Exception as exc:
        logger.error("[NanoBanana2] API call failed: %s", exc)
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
        else "13th Pillar standing in the center of the Citadel"
    )
    _dry = "--dry-run" in sys.argv

    out = generate(_prompt, dry_run=_dry)
    print("✅ Nano Banana 2 — Visual Manifestation result:")
    for k, v in out.items():
        print(f"   {k}: {v}")
