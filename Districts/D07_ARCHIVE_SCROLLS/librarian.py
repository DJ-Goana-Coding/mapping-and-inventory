import os, json, datetime

# --- THE NEXUS MASTER REQUISITION ---
TARGETS = {
    "CORE_OPPO": "~/ARK_CORE",
    "PIONEER_TRADER": "~/pioneer-trader",
    "S10_GHOST": "~/S10_SYNC",
    "LAPTOP_F_GHOST": "~/LAPTOP_F_SYNC",
    "RECOVERY": "~/RECOVERY_STAGING"
}

def scan_nexus():
    print("\n⚡ [NEXUS POINT: OMNI-SCAN INITIATED]")
    atlas = []
    
    for label, path in TARGETS.items():
        full_path = os.path.expanduser(path)
        if not os.path.exists(full_path):
            print(f"[!] Link Offline: {label}")
            continue
            
        print(f"[+] Syncing Node: {label}")
        for root, dirs, files in os.walk(full_path):
            if '.git' in dirs: dirs.remove('.git')
            for file in files:
                if file.endswith(('.py', '.txt', '.json', '.sh', '.md', '.csv', '.bat')):
                    try:
                        f_path = os.path.join(root, file)
                        atlas.append({
                            "node": label,
                            "name": file,
                            "path": f_path,
                            "size_kb": round(os.path.getsize(f_path) / 1024, 2),
                            "modified": datetime.datetime.fromtimestamp(os.path.getmtime(f_path)).strftime('%Y-%m-%d')
                        })
                    except: continue

    with open(os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json"), 'w') as f:
        json.dump(atlas, f, indent=4)
    print(f"\n[SUCCESS] Nexus Atlas Sealed: {len(atlas)} entities unified.\n")

if __name__ == "__main__":
    scan_nexus()
