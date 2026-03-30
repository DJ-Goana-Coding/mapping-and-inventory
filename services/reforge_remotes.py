import json, os, subprocess

def reforge():
    vault_p = os.path.expanduser("~/ARK_CORE/Partition_01/credentials.json")
    if not os.path.exists(vault_p):
        print("[!] ERROR: credentials.json not found in Partition_01.")
        return

    with open(vault_p, 'r') as f:
        creds = json.load(f)

    # Extract Keys
    gh_token = creds.get("GITHUB_TOKEN")
    hf_token = creds.get("HF_TOKEN")
    user = "DJ-Goanna-Coding"

    if not gh_token or not hf_token:
        print("[!] ERROR: Missing tokens in credentials.json.")
        return

    # Remotes Mapping
    remotes = {
        "origin": f"https://{gh_token}@github.com/{user}/ARK_CORE.git",
        "mapping": f"https://{gh_token}@github.com/{user}/mapping-and-inventory.git",
        "hf": f"https://{user}:{hf_token}@huggingface.co/spaces/{user}/ARK_CORE"
    }

    os.chdir(os.path.expanduser("~/ARK_CORE"))
    
    for name, url in remotes.items():
        subprocess.run(["git", "remote", "remove", name], capture_output=True)
        res = subprocess.run(["git", "remote", "add", name, url], capture_output=True)
        if res.returncode == 0:
            print(f"[SUCCESS] {name.upper()} re-bolted with Secret Token.")

if __name__ == "__main__":
    reforge()
