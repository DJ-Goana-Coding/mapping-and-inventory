import os
import time

def sentinel_perimeter_check():
    ark_path = os.path.expanduser("~/ARK_CORE")
    partitions = [f"Partition_{str(i).zfill(2)}" for i in range(1, 47)]
    
    print("[SENTINEL-SWARM] INITIATING PERIMETER SCAN...")
    
    missing_parts = []
    for part in partitions:
        if not os.path.exists(os.path.join(ark_path, part)):
            missing_parts.append(part)
            
    if missing_parts:
        return f"[!] SECURITY ALERT: Partitions missing: {', '.join(missing_parts)}"
    
    return "[V] PERIMETER SECURE: All 46 Partitions verified and stainless."

if __name__ == "__main__":
    print(sentinel_perimeter_check())
