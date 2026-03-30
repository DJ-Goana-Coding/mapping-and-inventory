import os

def forge_the_fleet():
    ark = os.path.expanduser("~/ARK_CORE")
    
    # The exact nodes you built on Hugging Face
    nodes = {
        "Partition_01": ["vanguard_titan.py", "genesis.py", "phalanx.py", "aion.py", "oracle.py"],
        "Partition_02": ["tia_architect.py", "fleet_watcher.py", "cgal_core.py"],
        "Partition_03": ["omega_bots.py", "omega_scout.py", "omega_trader.py", "omega_archive.py"],
        "Partition_04": ["tias_sentinel_swarm.py", "tias_pioneer_trader.py", "harvestmoon.py"]
    }

    print("[!] INITIATING THE FLEET FORGE...")
    count = 0
    
    for partition, files in nodes.items():
        part_path = os.path.join(ark, partition)
        os.makedirs(part_path, exist_ok=True)
        
        for file in files:
            file_path = os.path.join(part_path, file)
            # Only create if it doesn't exist so we don't overwrite your work
            if not os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    name = file.replace('.py', '').upper()
                    f.write(f'# {name} CORE LOGIC\n')
                    f.write(f'import json\n\n')
                    f.write(f'def {name.lower()}_boot():\n')
                    f.write(f'    print("[{name}] NODE ONLINE. Awaiting Dataset Uplink.")\n\n')
                    f.write(f'if __name__ == "__main__":\n')
                    f.write(f'    {name.lower()}_boot()\n')
                count += 1

    print(f"[V] FLEET FORGE COMPLETE. {count} NEW SOVEREIGN NODES MANUFACTURED.")

if __name__ == "__main__":
    forge_the_fleet()
