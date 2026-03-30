import os
import json
from datetime import datetime

# --- Q.G.T.N.L. (0) // SIGNAL PROBE V61.6 ---
# Added: Auto-Tagging Logic (#GRID, #PROBE)

NEURON_DIR = os.path.expanduser("~/ARK_CORE/Forever_Learning")

def drop_probe():
    print("🛰️ INITIATING SPATIAL GRID PROBE...")
    if not os.path.exists(NEURON_DIR): os.makedirs(NEURON_DIR)

    loc = input("Location: ") or "Unknown"
    lat = input("Lat: ") or "0.0"
    lon = input("Lon: ") or "0.0"
    res = input("Resonance: ") or "0.00"
    note = input("Note: ") or "No notes."

    neuron_data = {
        "type": "144-Grid Trace", "location": loc, "lat": float(lat),
        "lon": float(lon), "resonance": float(res), "note": note,
        "timestamp": datetime.now().isoformat(), "status": "SECURED"
    }

    filename = f"spatial_neuron_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(os.path.join(NEURON_DIR, filename), "w") as f:
        json.dump(neuron_data, f, indent=4)
    
    log_path = os.path.expanduser("~/ARK_CORE/Partition_01/aetheric_log.txt")
    with open(log_path, "a") as log:
        ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log.write(f"[{ts}] #PROBE #GRID: {note} in {loc} ({res}Hz) | RESULT: {filename} SECURED\n")

    print(f"\n✨ NEURON SECURED: {filename}")

if __name__ == "__main__":
    drop_probe()
