import os, shutil, subprocess
from datetime import datetime

# REPLACE THESE WITH YOUR ACTUAL DETAILS
USER = "YOUR_GITHUB_USERNAME"
TOKEN = "YOUR_GITHUB_TOKEN"
REPO = "CITADEL_OMEGA"

HOME = os.path.expanduser("~")
REPO_PATH = os.path.join(HOME, REPO)
LORE_SOURCE = os.path.join(HOME, "13th_Zone_Lore")

def run(cmd):
    subprocess.run(cmd, shell=True)

def vacuum_to_cloud():
    print("🚀 INITIATING CITADEL_OMEGA VACCUM...")
    if not os.path.exists(REPO_PATH):
        os.chdir(HOME)
        run(f"git clone https://{USER}:{TOKEN}@github.com/{USER}/{REPO}.git")
    
    # 1. Vacuum Lore
    target_lore = os.path.join(REPO_PATH, "Lore/13th_Zone")
    os.makedirs(target_lore, exist_ok=True)
    if os.path.exists(LORE_SOURCE):
        for f in os.listdir(LORE_SOURCE):
            shutil.copy2(os.path.join(LORE_SOURCE, f), target_lore)
            
    # 2. Vacuum Local Logic
    target_logic = os.path.join(REPO_PATH, "Logic/Swarm")
    os.makedirs(target_logic, exist_ok=True)
    for f in os.listdir(HOME):
        if f.endswith(".py") and f != "citadel_vacuum.py":
            shutil.copy2(os.path.join(HOME, f), target_logic)

    # 3. Secure Push
    os.chdir(REPO_PATH)
    run("git add .")
    run(f'git commit -m "Omni-Vacuum Sync: {datetime.now().strftime("%Y-%m-%d")}"')
    run("git push origin main")
    print("✅ CITADEL_OMEGA UPDATED.")

if __name__ == "__main__": vacuum_to_cloud()
