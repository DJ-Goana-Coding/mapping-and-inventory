import os
import json

def index_local_and_drive():
    # ADJUST THIS PATH to where your Google Drive is synced/mounted
    search_paths = [os.path.expanduser("~"), "/sdcard/Download"] 
    local_index = []
    
    print("[!] LIBRARIAN: SCANNING LOCAL AND SYNCED DRIVE STORAGE...")
    
    extensions = ('.py', '.json', '.js', '.txt', '.sh', '.md')
    
    for start_path in search_paths:
        for root, dirs, files in os.walk(start_path):
            if any(x in root for x in ['.git', '.cache', 'node_modules']): continue
            for file in files:
                if file.endswith(extensions):
                    local_index.append({
                        "filename": file,
                        "location": os.path.join(root, file)
                    })
                    
    with open(os.path.expanduser("~/ARK_CORE/Partition_01/local_index.json"), 'w') as f:
        json.dump(local_index, f, indent=4)
        
    print(f"[V] LOCAL INDEX SECURED: {len(local_index)} files found.")

if __name__ == "__main__":
    index_local_and_drive()
