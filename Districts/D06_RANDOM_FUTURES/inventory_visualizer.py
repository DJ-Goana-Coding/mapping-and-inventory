import os
import json

def generate_grid_map():
    ark_path = os.path.expanduser("~/ARK_CORE")
    grid_report = {}
    
    print("[!] GENERATING 144-GRID VISUAL MAP...")
    
    for i in range(1, 47):
        part_name = f"Partition_{str(i).zfill(2)}"
        part_path = os.path.join(ark_path, part_name)
        
        if os.path.exists(part_path):
            files = [f for f in os.listdir(part_path) if os.path.isfile(os.path.join(part_path, f))]
            grid_report[part_name] = {
                "count": len(files),
                "assets": files
            }
    
    output_path = os.path.join(ark_path, "Partition_01/grid_map.json")
    with open(output_path, 'w') as f:
        json.dump(grid_report, f, indent=4)
        
    return f"[V] MAP GENERATED: {len(grid_report)} Partitions Indexed."

if __name__ == "__main__":
    print(generate_grid_map())
