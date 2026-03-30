import os
import subprocess

OUTPUT_FILE = "deep_intel_log.txt"
# Target files that might contain the Watchdog or Genetics logic
FILES_TO_CHECK = ["fleet_watcher.sh", "genesis_swarm.py", "ms_genesis.py"]

def type_effect(text):
    print(text)

def run_recon():
    os.system('clear' if os.name == 'posix' else 'cls')
    type_effect("\033[96m\033[1m>>> INITIATING 13TH ZONE DEEP RECON...\033[0m")
    
    with open(OUTPUT_FILE, "w") as outfile:
        outfile.write("### OMEGA GOD MODE: DEEP INTEL & MODEL SWEEP ###\n\n")
        
        # --- 1. FILE INSPECTION ---
        outfile.write("=========================================\n")
        outfile.write("--- CORE LOGIC INSPECTION ---\n")
        outfile.write("=========================================\n\n")
        
        for file in FILES_TO_CHECK:
            if os.path.exists(file):
                type_effect(f"\033[38;5;214m[+] Extracting Intel: {file}\033[0m")
                outfile.write(f"--- START OF {file.upper()} ---\n")
                try:
                    with open(file, "r") as infile:
                        # Read file contents
                        outfile.write(infile.read())
                except Exception as e:
                    outfile.write(f"[ERROR READING FILE]: {e}\n")
                outfile.write(f"\n--- END OF {file.upper()} ---\n\n")
            else:
                type_effect(f"\033[91m[-] Missing Node: {file}\033[0m")

        # --- 2. LOCAL MODELS & QUANTS SWEEP ---
        type_effect(f"\033[38;5;214m[+] Sweeping Local LLMs & Ollama Models...\033[0m")
        outfile.write("=========================================\n")
        outfile.write("--- LOCAL AI MODELS & QUANTS ---\n")
        outfile.write("=========================================\n\n")
        
        # Check local-llms directory
        outfile.write(">>> CONTENTS OF 'local-llms' DIRECTORY:\n")
        try:
            local_llms = subprocess.check_output("ls -lh local-llms", shell=True, text=True)
            outfile.write(local_llms if local_llms else "[Directory is empty]\n")
        except Exception as e:
            outfile.write(f"Could not read local-llms: {e}\n")
            
        outfile.write("\n>>> OLLAMA INSTALLED MODELS (ollama list):\n")
        try:
            # Try to ask the Ollama daemon what it has loaded
            ollama_list = subprocess.check_output("ollama list", shell=True, text=True, stderr=subprocess.STDOUT)
            outfile.write(ollama_list)
        except Exception as e:
            outfile.write("Ollama daemon appears offline. Checking raw manifest folders...\n")
            try:
                raw_ollama = subprocess.check_output("ls -la ~/.ollama/models/manifests/registry.ollama.ai/library 2>/dev/null", shell=True, text=True)
                outfile.write(raw_ollama if raw_ollama else "[No standard Ollama library models found in path]\n")
            except:
                outfile.write("[Could not manually parse Ollama directories]\n")

    type_effect(f"\n\033[92m[✓] RECON COMPLETE. INTEL COMPILED TO: {OUTPUT_FILE}\033[0m")

if __name__ == "__main__":
    run_recon()
