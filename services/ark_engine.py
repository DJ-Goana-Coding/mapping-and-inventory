import subprocess
def run_sync():
    print("[ARK] INITIALIZING AUTONOMOUS SYNC...")
    subprocess.run(["python3", "services/manifest_generator.py"])
    subprocess.run(["git", "add", "."])
    subprocess.run(["git", "commit", "-m", "ark: sovereign inventory update"], capture_output=True)
    subprocess.run(["git", "push", "origin", "main"])
    subprocess.run(["git", "push", "mapping", "main"])
    print("[SUCCESS] ARK AND MAPPING VAULTS SYNCHRONIZED.")
if __name__ == "__main__": run_sync()
