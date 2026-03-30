import requests
import json
import os

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_OWNER = "DJ-Goanna-Coding"

def swarm_github_kingdom():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}
    print(f"[!] LIBRARIAN-OMEGA: SWARMING ALL REPOS FOR {REPO_OWNER}...")
    
    repos_url = f"https://api.github.com/users/{REPO_OWNER}/repos"
    repos_res = requests.get(repos_url, headers=headers)
    if repos_res.status_code != 200:
        return "Error: Access Denied. Check GITHUB_TOKEN."
    
    repos = [r['name'] for r in repos_res.json()]
    universal_atlas = []

    for repo in repos:
        print(f" -> Swarming Repo: {repo}...")
        branches_url = f"https://api.github.com/repos/{REPO_OWNER}/{repo}/branches"
        branches_res = requests.get(branches_url, headers=headers)
        if branches_res.status_code == 200:
            branches = [b['name'] for b in branches_res.json()]
            for branch in branches:
                tree_url = f"https://api.github.com/repos/{REPO_OWNER}/{repo}/git/trees/{branch}?recursive=1"
                tree_res = requests.get(tree_url, headers=headers)
                if tree_res.status_code == 200:
                    for item in tree_res.json().get('tree', []):
                        if item['type'] == 'blob':
                            universal_atlas.append({
                                "repo": repo, "branch": branch, "path": item['path'],
                                "url": f"https://github.com/DJ-Goanna-Coding/{repo}/blob/{branch}/{item['path']}"
                            })
    
    output_path = os.path.expanduser("~/ARK_CORE/Partition_01/universal_atlas.json")
    with open(output_path, 'w') as f:
        json.dump(universal_atlas, f, indent=4)
    print(f"[SUCCESS] {len(universal_atlas)} files indexed.")

if __name__ == "__main__":
    swarm_github_kingdom()
