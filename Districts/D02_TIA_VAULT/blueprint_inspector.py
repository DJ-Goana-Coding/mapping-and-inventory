import os

def inspect_reclaimed_gold():
    vault_path = os.path.expanduser("~/ARK_CORE/Districts/D02_TIA_VAULT/Master_Blueprints")
    
    if not os.path.exists(vault_path):
        print("[!] ERROR: Vault not found.")
        return

    blueprints = os.listdir(vault_path)
    print(f"--- THE 6 MASTER BLUEPRINTS OF THE CITADEL ---")
    
    for i, file in enumerate(blueprints, 1):
        size = os.path.getsize(os.path.join(vault_path, file))
        print(f"  {i}. {file} ({size} bytes) -> RECLAIMED")

if __name__ == "__main__":
    inspect_reclaimed_gold()
