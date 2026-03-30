import json
import os

def hunt_for_gold():
    ark = os.path.expanduser("~/ARK_CORE/Partition_01")
    atlas_path = os.path.join(ark, "universal_atlas.json")
    local_path = os.path.join(ark, "local_index.json")
    
    matches = []
    
    # 1. Search GitHub
    if os.path.exists(atlas_path):
        with open(atlas_path, 'r') as f:
            for item in json.load(f):
                if any(x in item['path'].lower() for x in ['modal', 'capability']):
                    matches.append(f"GITHUB: [{item['repo']}/{item['branch']}] -> {item['path']}")
                    
    # 2. Search Local/Drive
    if os.path.exists(local_path):
        with open(local_path, 'r') as f:
            for item in json.load(f):
                if any(x in item['filename'].lower() for x in ['modal', 'capability']):
                    matches.append(f"LOCAL: {item['location']}")
                    
    print(f"--- THE LIBRARIAN'S FINDINGS: {len(matches)} ASSETS ---")
    for m in matches[:20]:
        print(m)

if __name__ == "__main__":
    hunt_for_gold()
