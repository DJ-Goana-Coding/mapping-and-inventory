import os
import zipfile
import shutil
import json

# Paths
DOWNLOADS = os.path.expanduser("~/storage/downloads")
LORE_DIR = os.path.expanduser("~/13th_Zone_Lore")
CORE_DIR = os.path.expanduser("~/Core_Systems")

def type_effect(text):
    print(text)

def setup():
    for d in [LORE_DIR, CORE_DIR]:
        if not os.path.exists(d): os.makedirs(d)

def harvest_local():
    type_effect("\033[96m[+] INITIATING LOCAL ASSET ASSIMILATION...\033[0m")
    
    for item in os.listdir(DOWNLOADS):
        path = os.path.join(DOWNLOADS, item)
        
        # 1. EXTRACT ZIP GENETICS (Zips containing 'CITADEL' or 'GENESIS')
        if item.endswith(".zip"):
            print(f"\033[38;5;214m[ZIP] Opening Archive: {item}\033[0m")
            try:
                with zipfile.ZipFile(path, 'r') as z:
                    for zfile in z.namelist():
                        if zfile.endswith((".py", ".sh")):
                            z.extract(zfile, CORE_DIR)
                        if zfile.endswith((".md", ".json", ".txt")):
                            z.extract(zfile, LORE_DIR)
            except: pass

        # 2. SECURE THE MASTER KEYS (.env files)
        elif "env" in item.lower() or "vault" in item.lower():
            print(f"\033[92m[KEY] Securing Vault Asset: {item}\033[0m")
            shutil.copy(path, os.path.join(LORE_DIR, item))

        # 3. CONSOLIDATE LOGIC & LORE (.md, .json, .pdf)
        elif item.endswith((".md", ".json", ".pdf", ".txt")):
            print(f"\033[90m[LORE] Moving: {item}\033[0m")
            shutil.copy(path, os.path.join(LORE_DIR, item))

    type_effect("\n\033[96m[✓] LOCAL HARVEST COMPLETE. LORE FOLDER IS PRIMED.\033[0m")

if __name__ == "__main__":
    setup()
    harvest_local()
