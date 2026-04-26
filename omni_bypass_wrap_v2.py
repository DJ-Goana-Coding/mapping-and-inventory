import os

# Mapping local folder names to their intent
# Format: "local_folder_name": "display_name_for_logs"
NATIONS = {
    "mapping-and-inventory": "Mapping & Inventory",
    "citadel-vortex": "Citadel Vortex",
    "CITADEL_AGENTIC_SWARM": "Agentic Swarm",
    "VANGUARD_TITAN": "Vanguard Titan",
    "perimeter-scout": "Perimeter Scout"
}

home_dir = os.path.expanduser("~")

for folder, name in NATIONS.items():
    target_path = os.path.join(home_dir, folder, "app.py")
    
    # If app.py doesn't exist, create a base one so we can push it
    if not os.path.exists(target_path):
        print(f"🛠️  CREATING NEW app.py for {name}...")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w') as f:
            f.write("# Project Genesis Base Node\n")

    with open(target_path, 'r') as f:
        content = f.read()

    if "FastAPI()" in content:
        print(f"✅ {name} already wrapped.")
    else:
        wrapper_top = "from fastapi import FastAPI\nimport uvicorn\nimport os\n\napp = FastAPI()\n\n"
        wrapper_bottom = f"\n\n@app.get('/')\ndef health_check():\n    return {{'status': 'SUCCESS', 'message': 'TIA Node: {name} Active'}}\n\nif __name__ == '__main__':\n    port = int(os.environ.get('PORT', 7860))\n    uvicorn.run(app, host='0.0.0.0', port=port)\n"
        
        with open(target_path, 'w') as f:
            f.write(wrapper_top + content + wrapper_bottom)
        print(f"💎 WELD COMPLETE: {name}/app.py wrapped.")
