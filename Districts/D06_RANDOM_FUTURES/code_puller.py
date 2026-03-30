import requests
import os
import json

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def pull_code_from_atlas(query):
    # 1. Load the Atlas
    atlas_path = os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json")
    if not os.path.exists(atlas_path):
        return "Librarian: Universal Atlas not found. Run librarian_omega.py first."

    with open(atlas_path, 'r') as f:
        atlas = json.load(f)

    # 2. Find the match
    match = next((item for item in atlas if query.lower() in item['path'].lower()), None)
    
    if not match:
        return f"Librarian: No code found matching '{query}'."

    # 3. Pull from GitHub
    print(f"[!] PULLING: {match['path']} from [{match['branch']}]...")
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    res = requests.get(match['url'].replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/"), headers=headers)
    
    if res.status_code == 200:
        return res.text
    return f"Error pulling code: {res.status_code}"

if __name__ == "__main__":
    # Test pull
    print(pull_code_from_atlas("mexc"))
