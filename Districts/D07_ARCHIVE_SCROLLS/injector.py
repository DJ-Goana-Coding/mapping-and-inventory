import json, os

def inject_laptop_manifest():
    atlas_path = os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json")
    manifest_path = os.path.expanduser("~/LAPTOP_F_MANIFEST.json")
    
    if not os.path.exists(manifest_path):
        return print("[!] Error: LAPTOP_F_MANIFEST.json not found in home directory.")
    
    with open(atlas_path, 'r') as f:
        atlas = json.load(f)
    
    with open(manifest_path, 'r') as f:
        laptop_data = json.load(f)
    
    print(f"[+] Injecting {len(laptop_data)} entities from F: Drive...")
    
    for item in laptop_data:
        atlas.append({
            "node": "LAPTOP_F",
            "name": item.get("Name"),
            "path": item.get("FullName"),
            "size_kb": round(item.get("Length", 0) / 1024, 2),
            "modified": item.get("LastWriteTime", "Unknown")[:10]
        })
    
    with open(atlas_path, 'w') as f:
        json.dump(atlas, f, indent=4)
        
    print(f"[SUCCESS] Nexus Atlas Expanded. New Total: {len(atlas)} entities.")

if __name__ == "__main__":
    inject_laptop_manifest()
