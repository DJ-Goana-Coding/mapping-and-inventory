import os

def read_blueprints():
    vault_path = os.path.expanduser("~/ARK_CORE/Districts/D02_TIA_VAULT/Master_Blueprints")
    blueprints = ["omega_trader.py", "omega_scout.py"]
    
    print("--- DECONSTRUCTING OMEGA KINETIC LOGIC ---")
    
    for bp in blueprints:
        path = os.path.join(vault_path, bp)
        if os.path.exists(path):
            print(f"\n[FILE: {bp}]")
            with open(path, 'r') as f:
                print(f.read())
        else:
            print(f"[!] {bp} not found in Vault.")

if __name__ == "__main__":
    read_blueprints()
