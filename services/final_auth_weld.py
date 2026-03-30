import os, subprocess, json

def hunt_and_weld():
    user = "DJ-Goanna-Coding"
    # 1. THE SEARCH: Environment -> Vault -> Local Config
    gh_token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    hf_token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_TOKEN")

    vault_p = os.path.expanduser("~/ARK_CORE/Partition_01/credentials.json")
    if (not gh_token or not hf_token) and os.path.exists(vault_p):
        with open(vault_p, 'r') as f:
            creds = json.load(f)
            gh_token = gh_token or creds.get("GITHUB_TOKEN")
            hf_token = hf_token or creds.get("HF_TOKEN")

    if not gh_token:
        print("[!] ORACLE: Token signal low. Attempting Termux environment pull...")
        # Emergency pull from bash env if not exported
        try:
            gh_token = subprocess.check_output("echo $GITHUB_TOKEN", shell=True).decode().strip()
            hf_token = subprocess.check_output("echo $HF_TOKEN", shell=True).decode().strip()
        except: pass

    # 2. THE WELD
    if gh_token and len(gh_token) > 10:
        remotes = {
            "origin": f"https://{gh_token}@github.com/{user}/ARK_CORE.git",
            "mapping": f"https://{gh_token}@github.com/{user}/mapping-and-inventory.git",
            "hf": f"https://{user}:{hf_token}@huggingface.co/spaces/{user}/ARK_CORE"
        }
        os.chdir(os.path.expanduser("~/ARK_CORE"))
        for name, url in remotes.items():
            subprocess.run(["git", "remote", "remove", name], capture_output=True)
            subprocess.run(["git", "remote", "add", name, url], capture_output=True)
        print(f"[SUCCESS] {user}: Tokens found and welded to the Skyhook.")
    else:
        print("[!] CRITICAL: Tokens still not found. Ensure they are exported in Termux.")

if __name__ == "__main__":
    hunt_and_weld()
