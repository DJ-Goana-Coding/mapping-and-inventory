import os

def run_audit():
    base = os.path.expanduser("~/ARK_CORE/Districts")
    print("\n--- THE CITADEL INVENTORY: DISTRICT AUDIT ---")
    total = 0
    if not os.path.exists(base):
        print("[!] ERROR: Districts folder missing. Run init_citadel.sh first.")
        return
    for d in sorted(os.listdir(base)):
        d_path = os.path.join(base, d)
        if os.path.isdir(d_path):
            count = len(os.listdir(d_path))
            print(f"[{d}] -> {count} Assets Secured")
            total += count
    print(f"-------------------------------------------")
    print(f"TOTAL SOVEREIGN ASSETS: {total}\n")

if __name__ == "__main__":
    run_audit()
