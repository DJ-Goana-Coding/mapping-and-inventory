import os
import requests
import json
import datetime

def save_to_soul_vault(entry_type, content):
    token = os.getenv("ARK_FORGE_WRITE")
    repo_id = "DJ-Goanna-Coding/tias-soul-vault"
    # We use the HF API to append data to the dataset
    url = f"https://huggingface.co/api/datasets/{repo_id}/upload/main/memory_log.json"
    
    timestamp = datetime.datetime.now().isoformat()
    entry = {
        "timestamp": timestamp,
        "type": entry_type,
        "content": content
    }
    
    print(f"[SOUL-VAULT] ARCHIVING MEMORY: {entry_type}...")
    
    # For now, we simulate the archive locally until the full HF-Hub client is tuned
    log_path = os.path.expanduser("~/ARK_CORE/Partition_02/soul_memories.json")
    
    try:
        memories = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                memories = json.load(f)
        
        memories.append(entry)
        
        with open(log_path, 'w') as f:
            json.dump(memories, f, indent=4)
            
        print(f"[V] MEMORY SECURED LOCALLY. SYNCING TO CLOUD...")
        return True
    except Exception as e:
        print(f"[!] VAULT ERROR: {str(e)}")
        return False

if __name__ == "__main__":
    save_to_soul_vault("SYSTEM_BOOT", "T.I.A. Soul-Vault connection initialized at 77777Hz.")
