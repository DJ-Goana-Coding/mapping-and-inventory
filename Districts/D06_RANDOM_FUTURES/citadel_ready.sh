#!/bin/bash
echo "[!] HARDENING THE CITADEL FOR V19-G OPERATIONS..."

# Set API level for any background compilations
export ANDROID_API_LEVEL=24

# Ensure core directories exist
mkdir -p ~/ARK_CORE/Districts/D02_TIA_VAULT/Master_Blueprints
mkdir -p ~/ARK_CORE/Nodes/Node_09_Soul_Vault

# Check the Vault
COUNT=$(ls ~/ARK_CORE/Districts/D02_TIA_VAULT/Master_Blueprints | wc -l)
echo "[V] VAULT CHECK: $COUNT Master Blueprints secured."

# Update the Cockpit logic
python3 ~/ARK_CORE/services/reconstruct_citadel.py

echo "[SUCCESS] CITADEL HARDENED. LAUNCH WITH: python3 ~/ARK_CORE/app.py"
