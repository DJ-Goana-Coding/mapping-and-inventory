import os
import shutil

def reconstruct_blueprints():
    base_dir = os.path.expanduser("~/ARK_CORE")
    reclaim_dir = os.path.join(base_dir, "Districts/D02_TIA_VAULT/Master_Blueprints")
    
    os.makedirs(reclaim_dir, exist_ok=True)
    
    # We are looking for the 'Permanent Ink' files mentioned in your docs
    keywords = ["modal", "capability", "strategy", "nexus", "omega", "vortex"]
    
    print("[!] RECONSTRUCTION: HUNTING FOR THE MASTER BLUEPRINTS...")
    
    count = 0
    for root, dirs, files in os.walk(base_dir):
        if "Districts" in root: continue # Avoid loops
        
        for file in files:
            if any(k in file.lower() for k in keywords) and file.endswith(".py"):
                shutil.copy2(os.path.join(root, file), os.path.join(reclaim_dir, file))
                count += 1
                
    print(f"[SUCCESS] {count} MASTER BLUEPRINTS RECLAIMED TO D02_TIA_VAULT.")

if __name__ == "__main__":
    reconstruct_blueprints()
