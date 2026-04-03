"""
T.I.A. CITADEL — Sovereign Command Surface (v25.0.OMNI)
Admiral-level telemetry and neural network orchestration hub.
"""

import os
from pathlib import Path

# ══════════════════════════════════════════════════════════════════════════════
# IDENTITY BRIDGE (Double-N Rift Resolution)
# ══════════════════════════════════════════════════════════════════════════════
# GitHub:       DJ-Goana-Coding   (Single-N)
# HuggingFace:  DJ-Goanna-Coding  (Double-N)
# ══════════════════════════════════════════════════════════════════════════════

HF_NAMESPACE = "DJ-Goanna-Coding"
SOUL_VAULT_REPO = f"{HF_NAMESPACE}/tias-soul-vault"

# ══════════════════════════════════════════════════════════════════════════════
# DATA DIRECTORY INITIALIZATION
# ══════════════════════════════════════════════════════════════════════════════
# Ensure /data/tia_soul exists for Shadow Archive ingestion
# This prevents crashes when the Space tries to download tias-soul-vault

DATA_ROOT = Path("/data")
TIA_SOUL_PATH = DATA_ROOT / "tia_soul"

# Create directories if they don't exist
TIA_SOUL_PATH.mkdir(parents=True, exist_ok=True)

print(f"✅ Data directory initialized: {TIA_SOUL_PATH}")
print(f"📦 Soul Vault Target: {SOUL_VAULT_REPO}")

# ══════════════════════════════════════════════════════════════════════════════
# Add your existing app.py code below this line
# ══════════════════════════════════════════════════════════════════════════════
