import os
import sys
import subprocess
from datetime import datetime

# --- Q.G.T.N.L. (0) // ARK_ENGINE V62.5 ---
# Stabilized Datetime & GenAI Reporting

ROOT = os.path.expanduser("~/ARK_CORE")
sys.path.append(ROOT)

from services.washing_harvest import wash
from services.profit_sentry import watch_markets
from services.lore_transmuter import transmute_signal_to_lore

def _run(cmd):
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except Exception as e:
        print(f"[!] Git Ops: {e}")

def weld():
    print("🚀 INITIATING STABILIZED LIBRARIAN-WELD...")
    
    try: wash()
    except Exception: pass

    try: watch_markets()
    except Exception: pass

    print("🔮 TRANSMUTING FIELD DATA TO SAGA...")
    report = transmute_signal_to_lore()
    print(f"   >> {report}")

    # Manifest and Sync
    manifest_script = os.path.join(ROOT, "services/manifest_gen.py")
    if os.path.exists(manifest_script):
        subprocess.run(["python3", manifest_script])
    
    os.chdir(ROOT)
    _run(["git", "add", "."])
    ts_msg = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    _run(["git", "commit", "-m", f"[WELD] V62.5 Stabilized | {ts_msg}"])
    
    for remote in ["inventory", "ark", "space"]:
        print(f"[!] BROADCASTING TO: {remote.upper()}...")
        subprocess.run(["git", "push", remote, "main", "--force"])
    
    print("--- WELD COMPLETE: THE TOROID IS BALANCED ---")

if __name__ == "__main__":
    weld()
