import os
import time
import requests
from huggingface_hub import HfApi

AUTH_FILE = os.path.expanduser("~/.nexus_auth")

TARGET_FILES = [
    "ABN_Trade_Ledger.csv",
    "swarm_memory.json"
]

def type_effect(text):
    print(text)
    time.sleep(0.05)

def get_saved_tokens():
    tokens = {"HF_TOKEN": None, "GH_TOKEN": None}
    if os.path.exists(AUTH_FILE):
        with open(AUTH_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    key, val = line.strip().split("=", 1)
                    tokens[key] = val.replace('"', '')
    return tokens

def auto_discover_identities(tokens):
    identities = {"HF_USER": None, "GH_USER": None}
    
    if tokens["HF_TOKEN"]:
        try:
            res = requests.get("https://huggingface.co/api/whoami-v2", headers={"Authorization": f"Bearer {tokens['HF_TOKEN']}"})
            if res.status_code == 200:
                identities["HF_USER"] = res.json().get("name")
        except: pass

    if tokens["GH_TOKEN"]:
        try:
            res = requests.get("https://api.github.com/user", headers={"Authorization": f"token {tokens['GH_TOKEN']}"})
            if res.status_code == 200:
                identities["GH_USER"] = res.json().get("login")
        except: pass
        
    return identities

def push_to_huggingface(filepath, token, username):
    filename = os.path.basename(filepath)
    repo_id = f"{username}/Citadel_Genetics"
    
    print(f"\033[38;5;214m[+] Pushing {filename} to HF: {repo_id}...\033[0m")
    try:
        api = HfApi()
        api.upload_file(
            path_or_fileobj=filepath,
            path_in_repo=filename,
            repo_id=repo_id,
            repo_type="dataset",
            token=token
        )
        print(f"\033[92m[✓] {filename} successfully committed to Private Vault.\033[0m")
    except Exception as e:
        print(f"\033[91m[-] HF Uplink Error: {e}\033[0m")

def run_uplink():
    os.system('clear' if os.name == 'posix' else 'cls')
    type_effect("\033[96m\033[1m╔═══════════════════════════════════════════════════════════╗\033[0m")
    type_effect("\033[96m\033[1m║ 📡 THE NEXUS UPLINK: AUTO-AUTH & DECENTRALIZED BACKUP     ║\033[0m")
    type_effect("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")
    
    tokens = get_saved_tokens()
    identities = auto_discover_identities(tokens)

    if not identities["HF_USER"]:
        print("\033[91m[!] Aborting: Could not resolve Hugging Face identity. Check ~/.nexus_auth\033[0m")
        return

    print(f"\033[92m[✓] Uplink Locked to: {identities['HF_USER']}\033[0m")
    print("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")

    for file in TARGET_FILES:
        if os.path.exists(file):
            print(f"\033[96m\033[1m║\033[0m Targeting Local Asset: \033[1m{file}\033[0m")
            push_to_huggingface(file, tokens["HF_TOKEN"], identities["HF_USER"])
            print("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")
        else:
            # We create an empty dummy file if it doesn't exist just to establish the pipeline
            print(f"\033[93m[!] {file} missing. Generating Genesis seed...\033[0m")
            with open(file, "w") as f:
                f.write("INIT_SEQUENCE_START\n")
            push_to_huggingface(file, tokens["HF_TOKEN"], identities["HF_USER"])
            print("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")

    print("\033[96m\033[1m║ 🛡️ UPLINK COMPLETE. GENETICS ARE IMMORTAL.               ║\033[0m")
    print("\033[96m\033[1m╚═══════════════════════════════════════════════════════════╝\033[0m")

if __name__ == "__main__":
    run_uplink()
