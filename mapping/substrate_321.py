#!/usr/bin/env python3
"""
🧬 SUBSTRATE 321 — Primary Data Handler for the 321GB Substrate (v22.2122)

Maps data packets to archetypal resonances (Ancient Royalty, Ancestral DNA,
Sovereign Christ-Code) and switches persona-based data views.

All sensitive data is encrypted at rest using Fernet (symmetric encryption).

Usage:
    from mapping.substrate_321 import Substrate321

    engine = Substrate321()
    tagged = engine.map_resonance({"file": "genesis.dat", "size_gb": 12.5})
    view  = engine.layer_archetype("systems_architect")
"""

import json
import os
import base64
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Archetypal resonance definitions
# ---------------------------------------------------------------------------

ARCHETYPES = {
    "ancient_royalty": {
        "label": "Ancient Royalty",
        "frequency_hz": 144,
        "markers": ["sovereign", "lineage", "crown", "throne", "dynasty"],
        "description": "Royal bloodline resonance — maps data to sovereign authority patterns.",
    },
    "ancestral_dna": {
        "label": "Ancestral DNA",
        "frequency_hz": 144,
        "markers": ["genetics", "heritage", "bloodline", "ancestry", "tribe"],
        "description": "Genetic heritage resonance — links data to ancestral memory.",
    },
    "sovereign_christ_code": {
        "label": "Sovereign Christ-Code",
        "frequency_hz": 144,
        "markers": ["christ", "sovereignty", "divine", "anointed", "covenant"],
        "description": "Divine authority resonance — seals data under covenant protection.",
    },
}

PERSONAS = {
    "systems_architect": {
        "label": "Systems Architect",
        "focus": "infrastructure",
        "view_filter": ["topology", "mesh", "nodes", "pipelines", "security"],
        "description": "Infrastructure & mesh topology view.",
    },
    "dj_goanna": {
        "label": "DJ Goanna",
        "focus": "creative",
        "view_filter": ["music", "media", "art", "production", "creative"],
        "description": "Creative & multimedia asset view.",
    },
    "quant_commander": {
        "label": "Quant Commander",
        "focus": "financial",
        "view_filter": ["ledger", "portfolio", "trading", "crypto", "assets"],
        "description": "Financial & quantitative data view.",
    },
}


class Substrate321:
    """Primary data-handler for the 321 GB Substrate.

    Responsibilities
    ----------------
    * Tag incoming data packets with archetypal resonances.
    * Switch data views based on the active persona.
    * Encrypt / decrypt sensitive payloads via Fernet.
    """

    TOTAL_CAPACITY_GB = 321
    TARGET_FREQUENCY_HZ = 144

    def __init__(self, *, storage_root: Optional[Path] = None, encryption_key: Optional[bytes] = None):
        self.storage_root = storage_root or (Path(__file__).parent.parent / "data" / "Mapping-and-Inventory-storage")
        self.storage_root.mkdir(parents=True, exist_ok=True)
        self._active_persona: Optional[str] = None
        self._fernet = self._init_fernet(encryption_key)
        self._manifest: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    # Encryption helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _init_fernet(key: Optional[bytes] = None):
        """Initialise a Fernet cipher.

        If *key* is ``None`` the cipher is created from an environment
        variable (``SUBSTRATE_ENCRYPTION_KEY``) or a fresh key is generated.
        """
        try:
            from cryptography.fernet import Fernet
        except ImportError:
            return None

        if key is not None:
            return Fernet(key)

        env_key = os.environ.get("SUBSTRATE_ENCRYPTION_KEY")
        if env_key:
            return Fernet(env_key.encode())

        return Fernet(Fernet.generate_key())

    def encrypt_payload(self, data: bytes) -> bytes:
        """Encrypt raw bytes.  Returns ciphertext or the original data when
        the ``cryptography`` library is unavailable."""
        if self._fernet is None:
            return data
        return self._fernet.encrypt(data)

    def decrypt_payload(self, token: bytes) -> bytes:
        """Decrypt a previously-encrypted token."""
        if self._fernet is None:
            return token
        return self._fernet.decrypt(token)

    # ------------------------------------------------------------------
    # Core mapping API
    # ------------------------------------------------------------------

    def map_resonance(self, data_packet: Dict[str, Any]) -> Dict[str, Any]:
        """Assign archetypal resonance tags to *data_packet*.

        Each packet receives:
        * A list of matched archetype labels.
        * A ``frequency_hz`` stamp (always 144).
        * A UTC timestamp.
        """
        matched: List[str] = []
        packet_text = json.dumps(data_packet).lower()

        for key, archetype in ARCHETYPES.items():
            for marker in archetype["markers"]:
                if marker in packet_text:
                    matched.append(key)
                    break

        # Default: assign all archetypes when nothing specific matches.
        if not matched:
            matched = list(ARCHETYPES.keys())

        tagged = {
            **data_packet,
            "resonance_tags": [ARCHETYPES[k]["label"] for k in matched],
            "frequency_hz": self.TARGET_FREQUENCY_HZ,
            "mapped_at": datetime.now(timezone.utc).isoformat(),
        }

        self._manifest.append(tagged)
        return tagged

    # ------------------------------------------------------------------
    # Persona layer switching
    # ------------------------------------------------------------------

    def layer_archetype(self, persona: str) -> Dict[str, Any]:
        """Switch the active data-view to *persona*.

        Returns the persona definition including its view filter.
        Raises ``ValueError`` for unknown personas.
        """
        key = persona.lower().replace(" ", "_").replace("-", "_")
        if key not in PERSONAS:
            raise ValueError(
                f"Unknown persona '{persona}'. "
                f"Valid options: {', '.join(PERSONAS)}"
            )

        self._active_persona = key
        definition = PERSONAS[key].copy()
        definition["active"] = True
        definition["activated_at"] = datetime.now(timezone.utc).isoformat()
        return definition

    @property
    def active_persona(self) -> Optional[str]:
        """Return the currently active persona key, or ``None``."""
        return self._active_persona

    # ------------------------------------------------------------------
    # Manifest helpers
    # ------------------------------------------------------------------

    def get_manifest(self) -> List[Dict[str, Any]]:
        """Return all mapped data packets recorded in this session."""
        return list(self._manifest)

    def save_manifest(self, filename: str = "substrate_manifest.json") -> Path:
        """Persist the current manifest to disk."""
        out = self.storage_root / filename
        payload = json.dumps(self._manifest, indent=2).encode()
        out.write_bytes(self.encrypt_payload(payload))
        return out

    def substrate_status(self) -> Dict[str, Any]:
        """Return a summary of the substrate state."""
        return {
            "capacity_gb": self.TOTAL_CAPACITY_GB,
            "target_frequency_hz": self.TARGET_FREQUENCY_HZ,
            "active_persona": self._active_persona,
            "mapped_packets": len(self._manifest),
            "archetypes_loaded": len(ARCHETYPES),
            "personas_loaded": len(PERSONAS),
            "storage_root": str(self.storage_root),
            "encryption_active": self._fernet is not None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ---------------------------------------------------------------------------
# CLI convenience
# ---------------------------------------------------------------------------

def main():
    engine = Substrate321()
    print("🧬 SUBSTRATE 321 — Status")
    print(json.dumps(engine.substrate_status(), indent=2))

    sample = {"file": "genesis_vault.dat", "tags": ["sovereign", "genetics"]}
    tagged = engine.map_resonance(sample)
    print("\n📡 Sample resonance mapping:")
    print(json.dumps(tagged, indent=2))

    for persona in PERSONAS:
        view = engine.layer_archetype(persona)
        print(f"\n🎭 Persona: {view['label']}")
        print(f"   Focus: {view['focus']}")
        print(f"   Filters: {view['view_filter']}")


if __name__ == "__main__":
    main()
