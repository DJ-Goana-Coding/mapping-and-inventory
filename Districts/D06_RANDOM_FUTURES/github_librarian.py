import requests
import json
import os

# CONFIGURATION
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # Uses the same token as your engine
REPO_OWNER = "DJ-Goanna-Coding" # Adjust if your username is different
REPO_NAME = "mapping-and-inventory"

def crawl_all_branches():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    base_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}"
    
    print(f"[!] LIBRARIAN: SWARMING {REPO_NAME} ACROSS ALL BRANCHES...")
    
    # 1. Get all branches
    branches_res = requests.get(f"{base_url}/branches", headers=headers)
    if branches_res.status_code != 200:
        return f"Error: Could not fetch branches. Check GITHUB_TOKEN."
    
    branches = [b['name'] for b in branches_res.json()]
    print(f"[V] FOUND {len(branches)} BRANCHES. INITIATING DEEP INDEX...")
    
    master_inventory = []

    # 2. For each branch, get the file tree
    for branch in branches:
        print(f"Indexing Branch: {branch}...")
        tree_url = f"{base_url}/git/trees/{branch}?recursive=1"
        tree_res = requests.get(tree_url, headers=headers)
        
        if tree_res.status_code == 200:
            tree_data = tree_res.json()
            for item in tree_data.get('tree', []):
                if item['type'] == 'blob': # It's a file
                    master_inventory.append({
                        "branch": branch,
                        "path": item['path'],
                        "sha": item['sha'],
                        "url": item['url']
                    })
                    
    # 3. Save the Global Map
    index_path = os.path.expanduser("~/ARK_CORE/Partition_01/github_master_index.json")
    with open(index_path, 'w') as f:
        json.dump(master_inventory, f, indent=4)
        
    print(f"[SUCCESS] LIBRARIAN SECURED: {len(master_inventory)} files indexed across {len(branches)} branches.")
    return len(master_inventory)

if __name__ == "__main__":
    crawl_all_branches()
