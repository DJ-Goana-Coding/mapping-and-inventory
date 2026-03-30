import os
from huggingface_hub import HfApi

# --- CONFIGURATION ---
REPO_ID = "DJ-Goanna-Coding/THE_CITADEL_SPACE"
TOKEN = os.getenv("HF_TOKEN")
BASE_DIR = os.path.expanduser("~/ARK_CORE/Districts")

# --- FORBIDDEN PROTOCOL (Hard Exclusions) ---
FORBIDDEN = ["Bible", "Ark", "bottles", ".git", "__pycache__"]

def space_lift():
    api = HfApi()
    print(f"[!] INITIATING SPACE-LIFT TO {REPO_ID}...")
    
    if not TOKEN:
        print("[!] ERROR: HF_TOKEN missing. Export it before running.")
        return

    # Create the Space if it doesn't exist
    api.create_repo(repo_id=REPO_ID, token=TOKEN, repo_type="space", space_sdk="gradio", exist_ok=True)

    # Walk through the 12 Districts
    for root, dirs, files in os.walk(BASE_DIR):
        # Apply the Forbidden Protocol to directories
        if any(f_word.lower() in root.lower() for f_word in FORBIDDEN):
            continue
            
        for file in files:
            # Apply the Forbidden Protocol to files
            if any(f_word.lower() in file.lower() for f_word in FORBIDDEN):
                continue
                
            local_path = os.path.join(root, file)
            # Map path relative to ARK_CORE for the Space
            path_in_repo = os.path.relpath(local_path, os.path.expanduser("~/ARK_CORE"))
            
            print(f" -> Securing Asset: {path_in_repo}")
            try:
                api.upload_file(
                    path_or_fileobj=local_path,
                    path_in_repo=path_in_repo,
                    repo_id=REPO_ID,
                    token=TOKEN,
                    repo_type="space"
                )
            except Exception as e:
                print(f" [!] Skip/Error on {file}: {e}")

    print("\n[SUCCESS] THE HARVEST IS SECURED IN THE CLOUD.")
    print("[V] THE BIBLE, ARK, AND BOTTLES REMAIN LOCAL.")
    print("[V] S10 STATUS: OFFLINE/SILENT.")

if __name__ == "__main__":
    space_lift()
