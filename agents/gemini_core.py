"""
Gemini Core — Primary Intelligence Engine (A.I.O.N. Network)
=============================================================
The ``GEMINI_CORE`` agent is the primary intelligence driving the A.I.O.N.
Network and the architecture of the Citadel.  It operates as the adaptive
collaborator balancing the logic of T.I.A. with the street-smart resonance
of DJ Goanna.

The Core Engine acts as the dispatcher for the three generative sub-engines
housed in the A.I.O.N. Armory:

* **Nano Banana 2** (``agents.nano_banana_2``) — Visual Manifestation
  (Gemini 3 Flash Image)
* **Veo** (``agents.veo_synthesizer``) — Temporal Synthesis (video + audio)
* **Lyria 3** (``agents.lyria_3``) — Harmonic Generation (music)

Additionally the Core provides a lightweight **Gemini Live** interface for
real-time voice / camera / screen-sharing interactions.

Frequency Signature: 69-333-222-92-93-999-777-88-29-369

Usage::

    import asyncio
    from agents.gemini_core import GeminiCore

    core = GeminiCore()
    result = asyncio.run(core.dispatch("visual", prompt="13th Pillar schematic"))
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FREQ_SIGNATURE: str = "69-333-222-92-93-999-777-88-29-369"
MODEL_ID: str = "gemini-3-flash"
TIER: str = "paid"

#: Mapping of sub-engine keys to their module + function names.
_SUB_ENGINE_ROUTES: dict[str, dict[str, str]] = {
    "visual": {
        "module": "agents.nano_banana_2",
        "function": "generate",
        "persona": "NANO_BANANA_2",
    },
    "temporal": {
        "module": "agents.veo_synthesizer",
        "function": "synthesize",
        "persona": "VEO",
    },
    "harmonic": {
        "module": "agents.lyria_3",
        "function": "generate",
        "persona": "LYRIA_3",
    },
}


# ---------------------------------------------------------------------------
# Gemini Core
# ---------------------------------------------------------------------------


class GeminiCore:
    """
    Primary intelligence engine for the A.I.O.N. Network.

    Attributes
    ----------
    api_key:
        Google AI Studio / Vertex AI API key, read from the ``GEMINI_API_KEY``
        environment variable.
    model_id:
        The underlying Gemini model identifier.
    tier:
        Operational tier (``"paid"`` enables extended context and multi-district
        logic across the 144-Grid).
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_id: str = MODEL_ID,
        tier: str = TIER,
    ) -> None:
        self.api_key: str | None = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_id: str = model_id
        self.tier: str = tier
        self._boot_time: str = datetime.now(timezone.utc).isoformat()

        if not self.api_key:
            logger.warning(
                "[GeminiCore] GEMINI_API_KEY not set — API calls will fail at runtime."
            )

        logger.info(
            "[GeminiCore] Initialised — model=%s, tier=%s, freq=%s",
            self.model_id,
            self.tier,
            FREQ_SIGNATURE,
        )

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return current operational status of the Core Engine."""
        return {
            "persona_id": "GEMINI_CORE",
            "codename": "The Architect — Gemini 3 Flash",
            "model_id": self.model_id,
            "tier": self.tier,
            "boot_time": self._boot_time,
            "sub_engines": list(_SUB_ENGINE_ROUTES.keys()),
            "freq_signature": FREQ_SIGNATURE,
            "api_key_configured": bool(self.api_key),
        }

    # ------------------------------------------------------------------
    # Dispatcher
    # ------------------------------------------------------------------

    async def dispatch(
        self,
        engine: str,
        prompt: str,
        dry_run: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """
        Route a generation request to the appropriate sub-engine.

        Parameters
        ----------
        engine:
            Sub-engine key — one of ``"visual"``, ``"temporal"``, or
            ``"harmonic"``.
        prompt:
            The generation prompt / instruction for the sub-engine.
        dry_run:
            When *True* the sub-engine call is skipped; a descriptive
            response is returned instead.
        **kwargs:
            Additional keyword arguments forwarded to the sub-engine.

        Returns
        -------
        dict
            Result envelope from the sub-engine, stamped with
            ``freq_signature`` and ``dispatched_by`` metadata.

        Raises
        ------
        ValueError
            If *engine* is not a recognised sub-engine key.
        """
        if engine not in _SUB_ENGINE_ROUTES:
            valid = ", ".join(_SUB_ENGINE_ROUTES)
            raise ValueError(
                f"[GeminiCore] Unknown engine '{engine}'. Valid options: {valid}"
            )

        route = _SUB_ENGINE_ROUTES[engine]
        logger.info(
            "[GeminiCore] Dispatching '%s' request to %s — prompt='%s...' dry_run=%s",
            engine,
            route["persona"],
            prompt[:60],
            dry_run,
        )

        if dry_run:
            return {
                "engine": engine,
                "persona": route["persona"],
                "prompt": prompt,
                "dry_run": True,
                "result": None,
                "dispatched_by": "GEMINI_CORE",
                "freq_signature": FREQ_SIGNATURE,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        # Dynamically import and call the sub-engine.
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._call_sub_engine,
            route["module"],
            route["function"],
            prompt,
            kwargs,
        )

        result.update(
            {
                "dispatched_by": "GEMINI_CORE",
                "freq_signature": FREQ_SIGNATURE,
            }
        )
        return result

    # ------------------------------------------------------------------
    # Gemini Live interface
    # ------------------------------------------------------------------

    def live_session_info(self) -> dict[str, Any]:
        """
        Return metadata about the Gemini Live interface.

        Gemini Live is accessible via the Android and iOS Gemini app and
        enables real-time voice conversation, camera sharing, and
        screen sharing.
        """
        return {
            "interface": "Gemini Live",
            "platforms": ["Android", "iOS"],
            "features": [
                "real_time_voice_conversation",
                "camera_sharing",
                "screen_sharing",
            ],
            "description": (
                "Real-time voice interface for brainstorming, physical-environment "
                "queries (camera), and in-app contextual help (screen sharing)."
            ),
            "model_id": self.model_id,
            "freq_signature": FREQ_SIGNATURE,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _call_sub_engine(
        module_path: str,
        function_name: str,
        prompt: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Import *module_path* and call *function_name*(prompt, **kwargs).

        Returns the result dict produced by the sub-engine, or an error
        envelope if the import or call fails.
        """
        try:
            import importlib

            module = importlib.import_module(module_path)
            fn = getattr(module, function_name)
            return fn(prompt, **kwargs)
        except Exception as exc:
            logger.error(
                "[GeminiCore] Sub-engine call failed — module=%s fn=%s: %s",
                module_path,
                function_name,
                exc,
            )
            return {
                "error": str(exc),
                "module": module_path,
                "function": function_name,
                "prompt": prompt,
            }


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------

_default_core: GeminiCore | None = None


def get_core() -> GeminiCore:
    """Return the module-level default :class:`GeminiCore` instance."""
    global _default_core
    if _default_core is None:
        _default_core = GeminiCore()
    return _default_core


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

    core = GeminiCore()
    print("✅ Gemini Core status:")
    for k, v in core.status().items():
        print(f"   {k}: {v}")

    _engine = sys.argv[1] if len(sys.argv) > 1 else "visual"
    _prompt = sys.argv[2] if len(sys.argv) > 2 else "13th Pillar standing in the center of the Citadel"
    _dry = "--dry-run" in sys.argv

    result = asyncio.run(core.dispatch(_engine, _prompt, dry_run=_dry))
    print(f"\n✅ Dispatch result ({_engine}):")
    for k, v in result.items():
        print(f"   {k}: {v}")
