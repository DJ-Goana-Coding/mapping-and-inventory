import hashlib
import os
import json

def generate_genesis_signature():
    ark_path = os.path.expanduser("~/ARK_CORE")
    hash_master = hashlib.sha256()
    
    print("[!] GENESIS: CALCULATING ARK SIGNATURE...")
    
    # Walk through the Ark and hash the filenames and sizes
    for root, dirs, files in os.walk(ark_path):
        for names in sorted(files):
            filepath = os.path.join(root, names)
            # We hash the metadata to keep it fast
            hash_master.update(names.encode())
            hash_master.update(str(os.path.getsize(filepath)).encode())
            
    genesis_sig = hash_master.hexdigest()
    
    log_path = os.path.expanduser("~/ARK_CORE/Partition_46/genesis_seal.json")
    with open(log_path, 'w') as f:
        json.dump({"signature": genesis_sig, "nodes": 55}, f, indent=4)
        
    print(f"[V] GENESIS SEALED: {genesis_sig[:16]}...")
    return genesis_sig

if __name__ == "__main__":
    generate_genesis_signature()
