import os
import json

def heal_the_ark():
    ark = os.path.expanduser("~/ARK_CORE")
    critical_files = {
        "Partition_01/vanguard_pulse.log": "",
        "Partition_01/trade_ledger.json": "[]",
        "Partition_01/grid_map.json": "{}",
        "Partition_46/citadel_genetics.json": "[]"
    }
    
    repairs = 0
    print("[!] SENTINEL DEBUGGER: INITIATING AUTO-HEAL...")
    
    for relative_path, default_content in critical_files.items():
        full_path = os.path.join(ark, relative_path)
        
        # Check if file exists and has content
        if not os.path.exists(full_path) or os.path.getsize(full_path) == 0:
            print(f"[REPAIR] Restoring critical node: {relative_path}")
            with open(full_path, 'w') as f:
                f.write(default_content)
            repairs += 1
            
    if repairs == 0:
        return "[V] SYSTEM STAINLESS: No logic rot detected."
    return f"[V] AUTO-HEAL COMPLETE: {repairs} nodes restored."

if __name__ == "__main__":
    print(heal_the_ark())
