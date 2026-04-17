#!/usr/bin/env python3
"""
🌱 GENESIS ALIGNMENT — Substrate-to-Trading Integration (v22.2124)

Wires the Ancestral DNA (Ancient Royalty) metadata directly into the
trading command module.  Provides:

  • Archetypal trade-scoring via ``map_resonance()``
  • Signal detection (configurable threshold-based spike detector)
  • Persona switching — switches to DJ Goanna when a stabilisation
    event is detected

Usage:
    from core.genesis_alignment import GenesisAlignment
    from mapping.substrate_321 import Substrate321

    substrate = Substrate321()
    aligner   = GenesisAlignment(substrate=substrate)

    score  = aligner.score_trade({"instrument": "XRP", "direction": "buy"})
    signal = aligner.detect_signal({"malice_level": 8.5})
    if signal["spike_detected"]:
        aligner.switch_to_stabilization_persona()
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from mapping.substrate_321 import Substrate321, ARCHETYPES, PERSONAS

# ---------------------------------------------------------------------------
# Archetype trade-weight map
# ---------------------------------------------------------------------------

# Each archetype label carries a relative weighting applied to trade scoring.
ARCHETYPE_WEIGHTS: Dict[str, float] = {
    "Ancient Royalty": 1.5,
    "Ancestral DNA": 1.3,
    "Sovereign Christ-Code": 1.2,
}

# Default signal threshold above which a stabilisation persona switch fires.
DEFAULT_SIGNAL_THRESHOLD = 7.0

# Persona used for stabilisation broadcasts.
STABILIZATION_PERSONA = "dj_goanna"


class GenesisAlignment:
    """Integrates the 321GB Substrate with the trading command module.

    Responsibilities
    ----------------
    * Score trade proposals against current archetypal resonances.
    * Detect elevated signal levels and trigger persona switches.
    * Switch the substrate view to the DJ Goanna stabilisation persona
      when a signal spike is detected.
    """

    def __init__(
        self,
        *,
        substrate: Optional[Substrate321] = None,
        signal_threshold: float = DEFAULT_SIGNAL_THRESHOLD,
        output_dir: Optional[Path] = None,
    ):
        self._substrate = substrate or Substrate321()
        self._signal_threshold = signal_threshold
        self.output_dir = output_dir or (Path(__file__).parent.parent / "data" / "genesis_alignment")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._trade_log: List[Dict[str, Any]] = []
        self._signal_log: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Trade scoring
    # ------------------------------------------------------------------

    def score_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score a trade proposal against the substrate's archetypal resonances.

        The score is the sum of weights for each archetype tag returned by
        ``map_resonance``.  A higher score indicates stronger ancestral
        alignment.

        Parameters
        ----------
        trade_data:
            Arbitrary dict describing the trade (instrument, direction, etc.)

        Returns
        -------
        Dict containing the original trade data plus ``resonance_tags``,
        ``alignment_score``, and ``frequency_hz``.
        """
        tagged = self._substrate.map_resonance(trade_data)
        score = sum(
            ARCHETYPE_WEIGHTS.get(tag, 1.0) for tag in tagged.get("resonance_tags", [])
        )

        result: Dict[str, Any] = {
            **tagged,
            "alignment_score": round(score, 4),
            "archetype_weights": ARCHETYPE_WEIGHTS,
            "scored_at": datetime.now(timezone.utc).isoformat(),
        }
        self._trade_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Signal detection
    # ------------------------------------------------------------------

    def detect_signal(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Check whether any metric in *metrics* exceeds the signal threshold.

        A ``spike_detected`` flag is set to ``True`` when any numeric value
        in *metrics* is at or above ``self._signal_threshold``.

        Parameters
        ----------
        metrics:
            Dict of named numeric readings (e.g. ``{"malice_level": 8.5}``).
        """
        spike_fields = {
            k: v
            for k, v in metrics.items()
            if isinstance(v, (int, float)) and v >= self._signal_threshold
        }
        spike_detected = bool(spike_fields)

        result: Dict[str, Any] = {
            "metrics": metrics,
            "signal_threshold": self._signal_threshold,
            "spike_fields": spike_fields,
            "spike_detected": spike_detected,
            "detected_at": datetime.now(timezone.utc).isoformat(),
        }
        self._signal_log.append(result)
        return result

    # ------------------------------------------------------------------
    # Persona switching
    # ------------------------------------------------------------------

    def switch_to_stabilization_persona(self) -> Dict[str, Any]:
        """Switch the substrate to the DJ Goanna stabilisation persona.

        Called automatically when a signal spike is detected; can also be
        invoked directly.

        Returns the persona definition including its view filter.
        """
        view = self._substrate.layer_archetype(STABILIZATION_PERSONA)
        view["stabilization_broadcast"] = True
        view["broadcast_frequency_hz"] = 144
        view["activated_at"] = datetime.now(timezone.utc).isoformat()
        return view

    def active_persona(self) -> Optional[str]:
        """Return the substrate's currently active persona key."""
        return self._substrate.active_persona

    # ------------------------------------------------------------------
    # Logs / status
    # ------------------------------------------------------------------

    def trade_log(self) -> List[Dict[str, Any]]:
        """Return all scored trade records from this session."""
        return list(self._trade_log)

    def signal_log(self) -> List[Dict[str, Any]]:
        """Return all signal detection records from this session."""
        return list(self._signal_log)

    def status(self) -> Dict[str, Any]:
        """Return a summary of the alignment engine state."""
        return {
            "signal_threshold": self._signal_threshold,
            "active_persona": self.active_persona(),
            "trades_scored": len(self._trade_log),
            "signals_checked": len(self._signal_log),
            "stabilization_persona": STABILIZATION_PERSONA,
            "archetype_weights": ARCHETYPE_WEIGHTS,
            "output_dir": str(self.output_dir),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def save(self, filename: str = "genesis_alignment.json") -> Path:
        """Persist trade and signal logs to disk."""
        payload = {
            "version": "v22.2124",
            "trade_log": self._trade_log,
            "signal_log": self._signal_log,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
        out = self.output_dir / filename
        out.write_text(json.dumps(payload, indent=2))
        return out


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    substrate = Substrate321()
    aligner = GenesisAlignment(substrate=substrate)

    trade = {"instrument": "XRP", "direction": "buy", "tags": ["sovereign"]}
    result = aligner.score_trade(trade)
    print("🌱 GENESIS ALIGNMENT — Trade Score")
    print(json.dumps({k: result[k] for k in ("alignment_score", "resonance_tags", "frequency_hz")}, indent=2))

    signal = aligner.detect_signal({"malice_level": 8.5, "noise_floor": 2.0})
    print("\n📡 Signal Detection:")
    print(json.dumps({k: signal[k] for k in ("spike_detected", "spike_fields")}, indent=2))

    if signal["spike_detected"]:
        persona = aligner.switch_to_stabilization_persona()
        print(f"\n🎵 Stabilisation: switched to '{persona['label']}'")


if __name__ == "__main__":
    main()
