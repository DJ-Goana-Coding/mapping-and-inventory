import os
import requests
import json
from services.district_librarian import TAXONOMY

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def reclaim_and_file(query):
    atlas_path = os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json")
    if not os.path.exists(atlas_path): return "Error: Atlas missing."

    with open(atlas_path, 'r') as f:
        atlas = json.load(f)

    # Find the most relevant match
    match = next((i for i in atlas if query.lower() in i['path'].lower()), None)
    if not match: return "No match found in Atlas."

    # Pull the code
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    raw_url = match['url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    res = requests.get(raw_url, headers=headers)

    if res.status_code == 200:
        content = res.text
        filename = os.path.basename(match['path'])
        
        # Determine District
        target_district = "D06_RANDOM_FUTURES" # Default
        for district, keywords in TAXONOMY.items():
            if any(k in filename.lower() for k in keywords):
                target_district = district
                break
        
        dest_path = os.path.expanduser(f"~/ARK_CORE/Districts/{target_district}/{filename}")
        with open(dest_path, 'w') as f:
            f.write(content)
            
        return f"SUCCESS: {filename} reclaimed from {match['branch']} to {target_district}."
    return f"FAILED: {res.status_code}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(reclaim_and_file(sys.argv[1]))
