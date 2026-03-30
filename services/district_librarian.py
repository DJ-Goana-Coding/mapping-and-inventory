import os, shutil

TAXONOMY = {
    "D01_COMMAND_INPUT": ["run", "engine", "input"],
    "D02_TIA_VAULT": ["tia", "vault", "app.py", "blueprint"],
    "D03_VORTEX_ENGINE": ["vortex", "grid", "144", "resonance"],
    "D04_OMEGA_TRADER": ["trade", "trader", "execution"],
    "D05_OPEN_SOURCE_BIN": ["phi", "qwen", "external"],
    "D07_ARCHIVE_SCROLLS": ["log", "history", "ledger"],
    "D08_SECURITY_AUTH": ["key", "token", "auth"],
    "D09_MEDIA_CODING": ["audio", "image", "lore", "vibe"],
    "D10_LEGAL_STACK": ["legal", "jurisdiction", "1986"],
    "D11_PERSONA_MODULES": ["goanna", "jarl", "persona"],
    "D12_ORACLE_ETHICS": ["safety", "ethics", "guardrail"]
}

def swarm_and_sort():
    base = os.path.expanduser("~/ARK_CORE")
    dist = os.path.join(base, "Districts")
    print("[!] LIBRARIAN: COMMENCING FORENSIC SORTING...")

    for root, dirs, files in os.walk(base):
        if "Districts" in root or "Nodes" in root: continue
        for f in files:
            if f.startswith('.') or f == "district_librarian.py": continue
            src = os.path.join(root, f)
            target = "D06_RANDOM_FUTURES"
            for d, keys in TAXONOMY.items():
                if any(k in f.lower() for k in keys):
                    target = d
                    break
            dst_dir = os.path.join(dist, target)
            if not os.path.exists(dst_dir): os.makedirs(dst_dir)
            try:
                shutil.move(src, os.path.join(dst_dir, f))
                print(f" -> Reclaimed {f} to {target}")
            except Exception as e: print(f" [!] Skip {f}: {e}")

if __name__ == "__main__": swarm_and_sort()
