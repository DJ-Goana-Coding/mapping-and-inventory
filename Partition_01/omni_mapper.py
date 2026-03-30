import os, re

print("=====================================================")
print("[PHALANX OMNI-MAPPER: EXTRACTING CITADEL ARCHITECTURE]")
print("=====================================================")

# The core files we identified in the previous recon
target_files = [
    "citadel_master_bridge.py",
    "dj_goanna.py",
    "ms_genesis.py",
    "citadel_agentic_swarm.py",
    "citadel_mobile.py",
    "titan_master.py"
]

home = os.path.expanduser("~")

for file_name in target_files:
    path = os.path.join(home, file_name)
    if not os.path.exists(path):
        continue

    print(f"\n[+] Mapping Node: {file_name}")
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Extract Dependencies
        imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_\.]+)', content, re.MULTILINE)
        if imports:
            print(f"    - Dependencies : {', '.join(set(imports))}")

        # Extract Classes (The Structure)
        classes = re.findall(r'^class\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
        if classes:
            print(f"    - Logic Modules: {', '.join(classes)}")

        # Extract Functions (The Actions)
        functions = re.findall(r'^ *def\s+([a-zA-Z0-9_]+)', content, re.MULTILINE)
        if functions:
            print(f"    - Functions    : {', '.join(functions)}")

        # Extract Network Targets (Where is it trying to talk?)
        # We look for URLs or specific API keywords, NOT the keys themselves
        urls = re.findall(r'https://[a-zA-Z0-9\-\.]+\.com|https://[a-zA-Z0-9\-\.]+\.co', content)
        hf_mentions = re.findall(r'HuggingFace|InferenceClient|API_URL|HMT-76', content, re.IGNORECASE)
        
        targets = set(urls + hf_mentions)
        if targets:
            print(f"    - Net-Targets  : {', '.join(targets)}")

    except Exception as e:
        print(f"    - Error reading node: {e}")

print("\n=====================================================")
print("[MAP COMPLETE] Paste this output back to the Commander.")
print("=====================================================")
