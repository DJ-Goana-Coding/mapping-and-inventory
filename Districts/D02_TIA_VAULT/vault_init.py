import os
import json
import datetime

def init_soul_vault():
    vault_path = os.path.expanduser("~/ARK_CORE/Nodes/Node_09_Soul_Vault/meaning_ledger.json")
    
    initial_ledger = {
        "system_birth": datetime.datetime.now().isoformat(),
        "framework": "V19-G",
        "jurisdiction": "Tier 1 (Universal)",
        "redistribution_protocol": "5-Vector Banking",
        "vector_targets": {
            "CASH": 0.35,
            "BLUE_CHIP": 0.20,
            "ISO_20022": 0.20,
            "AI_PROTOCOL": 0.20,
            "SPECULATIVE": 0.05
        },
        "memory_state": "Forever Learning Active",
        "entries": []
    }
    
    if not os.path.exists(vault_path):
        with open(vault_path, 'w') as f:
            json.dump(initial_ledger, f, indent=4)
        print("[V] SOUL VAULT INITIALIZED: Meaning Ledger created.")
    else:
        print("[!] SOUL VAULT DETECTED: Ledger already exists.")

if __name__ == "__main__":
    init_soul_vault()
