import os
import json
import datetime

def mirror_to_cloud_vault():
    ark = os.path.expanduser("~/ARK_CORE")
    vault_log = os.path.join(ark, "Partition_01/cloud_mirror_log.json")
    
    # Files to Mirror
    sources = {
        "trades": "Partition_01/trade_ledger.json",
        "profits": "Partition_01/grid_map.json",
        "pulse": "Partition_01/vanguard_pulse.log"
    }
    
    mirror_data = {
        "sync_time": datetime.datetime.now().isoformat(),
        "payload": {}
    }
    
    print("[!] INITIATING VAULT MIRROR...")
    
    for key, path in sources.items():
        full_path = os.path.join(ark, path)
        if os.path.exists(full_path):
            # We take the last 5 entries to keep the mirror light but relevant
            with open(full_path, 'r') as f:
                try:
                    lines = f.readlines()
                    mirror_data["payload"][key] = lines[-5:]
                except:
                    mirror_data["payload"][key] = "Error reading source"

    # Save the mirror package locally; ark_engine will push it to the grid
    with open(vault_log, 'w') as f:
        json.dump(mirror_data, f, indent=4)
        
    print(f"[V] VAULT MIRROR PACKAGE SECURED: Prepared for Triple-Sync.")
    return True

if __name__ == "__main__":
    mirror_to_cloud_vault()
