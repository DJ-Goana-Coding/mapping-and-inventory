import os
from datetime import datetime

from .gemini_rotator import generate_content, get_rotator


def transmute_signal_to_lore():
    # 🧬 ROUND-ROBIN MANIFOLD with 429 / ResourceExhausted failover
    rotator = get_rotator()
    if not rotator:
        return "❌ Missing Neural Signal (No API Keys found)."

    staging_dir = os.path.expanduser("~/ARK_CORE/Partition_46/WASHING_HARVEST_STAGING")

    try:
        response = generate_content(
            model='gemini-2.0-flash',
            contents="Chronicle the 144-Grid. Australian cyberpunk tone. The Citadel is rising.",
            rotator=rotator,
        )
    except Exception as e:  # noqa: BLE001
        if "429" in str(e) or "ResourceExhausted" in str(e):
            return "⏳ TOTAL BRAIN OVERHEAT: All Cores at capacity. Wait 5 mins."
        return f"❌ AI Error: {str(e)[:50]}"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Lore_{ts}_DualCore.txt"
    with open(os.path.join(staging_dir, filename), "w") as shard:
        shard.write(response.text)
    return f"✨ LORE SECURED: {filename}"
