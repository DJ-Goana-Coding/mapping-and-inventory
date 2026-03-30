import json
import os

def generate_reclamation_report():
    atlas_path = os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json")
    if not os.path.exists(atlas_path):
        return "Atlas not found."

    with open(atlas_path, 'r') as f:
        atlas = json.load(f)

    # Keywords we are hunting for
    keywords = ['modal', 'capability', 'logic', 'mexc', 'bot']
    report = {}

    for item in atlas:
        for key in keywords:
            if key in item['path'].lower():
                if key not in report: report[key] = []
                report[key].append(f"[{item['branch']}] {item['path']}")

    print("--- THE ORACLE'S LOST GOLD: RECLAMATION REPORT ---")
    for key, matches in report.items():
        print(f"\nFOUND {len(matches)} ASSETS FOR '{key.upper()}':")
        for m in matches[:5]: # Show top 5 for each
            print(f"  -> {m}")
            
    return report

if __name__ == "__main__":
    generate_reclamation_report()
