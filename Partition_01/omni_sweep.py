import os
import json

# Target directories from your ls -la output
TARGET_DIRS = [".", "memory_shards", "The_12_Spaces", "Tia_Core", "Trinity_Oppo_Vault", "Toolbox"]

def type_effect(text):
    print(text)

def analyze_json(filepath):
    """Safely peeks inside JSON files to see if they hold vectors/RAG logic."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        keys = []
        if isinstance(data, dict):
            keys = list(data.keys())
        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            keys = list(data[0].keys())
            
        indicators = ["vector", "embedding", "chunk", "metadata", "score", "memory", "strategy"]
        found_tags = [k for k in keys if any(ind in k.lower() for ind in indicators)]
        
        return len(data), found_tags
    except Exception:
        return 0, []

def analyze_md(filepath):
    """Checks MD files for structural RAG headers or lore formatting."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            size = len(content)
            # Check if it looks like a Master Ledger or Bible of Build
            if "# " in content or "## " in content or "Prompt:" in content:
                return size, True
            return size, False
    except:
        return 0, False

def run_sweep():
    os.system('clear' if os.name == 'posix' else 'cls')
    type_effect("\033[96m\033[1m>>> INITIATING 13TH ZONE OMNI-SWEEP (JSON/MD)...\033[0m\n")
    
    found_assets = {"json": [], "md": []}

    for d in TARGET_DIRS:
        if not os.path.exists(d): continue
        
        for item in os.listdir(d):
            filepath = os.path.join(d, item)
            
            if os.path.isfile(filepath):
                if item.endswith(".json"):
                    size, tags = analyze_json(filepath)
                    found_assets["json"].append({"path": filepath, "entries": size, "tags": tags})
                elif item.endswith(".md"):
                    size, has_structure = analyze_md(filepath)
                    found_assets["md"].append({"path": filepath, "size": size, "structured": has_structure})

    # --- PRINT RESULTS ---
    print("\033[38;5;214m[+] .JSON ASSETS (MEMORY & VECTORS):\033[0m")
    for asset in found_assets["json"]:
        tag_str = f" | \033[92mTags: {', '.join(asset['tags'])}\033[0m" if asset['tags'] else ""
        print(f"  └─ {asset['path']} (Size/Entries: {asset['entries']}){tag_str}")

    print("\n\033[38;5;214m[+] .MD ASSETS (LORE & LEDGERS):\033[0m")
    if not found_assets["md"]:
        print("  └─ [No Markdown files found in scanned directories]")
    for asset in found_assets["md"]:
        struct_str = " | \033[92m[Structured Lore]\033[0m" if asset['structured'] else ""
        print(f"  └─ {asset['path']} (Chars: {asset['size']}){struct_str}")
        
    print("\n\033[96m\033[1m[✓] SWEEP COMPLETE. AWAITING COMMANDER'S REVIEW.\033[0m")

if __name__ == "__main__":
    run_sweep()
