import json
import os

def generate_manifest():
    root = os.path.expanduser("~/ARK_CORE")
    inventory_path = os.path.join(root, "master_inventory.json")
    if os.path.exists(inventory_path):
        print(f"[LIBRARIAN] Manifest confirmed via master_inventory.json")
        return True
    return False

if __name__ == "__main__":
    generate_manifest()
