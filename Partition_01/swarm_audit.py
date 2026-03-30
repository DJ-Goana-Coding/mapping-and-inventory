import os
import time

# The core engine files we need to inspect the Swarm's logic
TARGET_FILES = [
    "citadel_master_bridge.py",
    "citadel_v40.py",
    "ark_swarm_v29.py",
    "mexc_skim_to_fuel.py"
]

OUTPUT_FILE = "omega_audit_log.txt"

def type_effect(text):
    print(text)
    time.sleep(0.1)

def audit_swarm():
    os.system('clear' if os.name == 'posix' else 'cls')
    type_effect("\033[96m\033[1m>>> INITIATING 13TH ZONE SWARM AUDIT...\033[0m")
    
    with open(OUTPUT_FILE, "w") as outfile:
        outfile.write("### OMEGA GOD MODE: SWARM AUDIT LOG ###\n\n")
        
        for file in TARGET_FILES:
            if os.path.exists(file):
                type_effect(f"\033[38;5;214m[+] Extracting Intel: {file}\033[0m")
                outfile.write(f"=========================================\n")
                outfile.write(f"--- START OF {file.upper()} ---\n")
                outfile.write(f"=========================================\n\n")
                
                with open(file, "r") as infile:
                    outfile.write(infile.read())
                    
                outfile.write(f"\n--- END OF {file.upper()} ---\n\n")
            else:
                type_effect(f"\033[91m[-] Missing Node: {file} not found.\033[0m")
                
    type_effect(f"\n\033[92m[✓] AUDIT COMPLETE. INTEL COMPILED TO: {OUTPUT_FILE}\033[0m")

if __name__ == "__main__":
    audit_swarm()
