#!/usr/bin/env python3
"""
Generate INVENTORY.json - District asset registry
This is a placeholder that can be customized per District
"""
import os
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

def generate_inventory(root_path="."):
    """Generate inventory of files and assets."""
    inventory = {
        "generated": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "repository": os.environ.get('GITHUB_REPOSITORY', 'Unknown'),
        "commit": os.environ.get('GITHUB_SHA', 'Unknown'),
        "branch": os.environ.get('GITHUB_REF_NAME', 'Unknown'),
        "files": [],
        "directories": [],
        "stats": {
            "total_files": 0,
            "total_size": 0,
            "by_extension": {}
        }
    }
    
    exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'rag_store'}
    exclude_files = {'.DS_Store', 'Thumbs.db'}
    
    total_size = 0
    extensions = {}
    
    for root, dirs, files in os.walk(root_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        # Record directories
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            rel_path = os.path.relpath(dir_path, root_path)
            inventory["directories"].append({
                "path": rel_path,
                "name": dir_name
            })
        
        # Record files
        for file_name in files:
            if file_name in exclude_files or file_name.startswith('.'):
                continue
                
            file_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(file_path, root_path)
            
            try:
                file_size = os.path.getsize(file_path)
                total_size += file_size
                
                ext = Path(file_name).suffix or 'no_extension'
                extensions[ext] = extensions.get(ext, 0) + 1
                
                inventory["files"].append({
                    "path": rel_path,
                    "name": file_name,
                    "size": file_size,
                    "extension": ext
                })
            except OSError:
                pass
    
    inventory["stats"]["total_files"] = len(inventory["files"])
    inventory["stats"]["total_size"] = total_size
    inventory["stats"]["by_extension"] = extensions
    
    return json.dumps(inventory, indent=2)

if __name__ == "__main__":
    print(generate_inventory())
