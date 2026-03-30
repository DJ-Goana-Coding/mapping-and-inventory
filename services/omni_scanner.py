import os, subprocess, json

def run_recon():
    report = {
        "architect": "Chance",
        "timestamp": str(os.popen("date").read().strip()),
        "nodes": {
            "OPPO_TERMUX": os.path.expanduser("~"),
            "ARK_CORE": os.path.expanduser("~/ARK_CORE"),
            "UBUNTU_ROOT": "/data/data/com.termux/files/usr/lib" # Typical Termux/Ubuntu path
        },
        "tokens": {
            "GITHUB_TOKEN": "DETECTED" if os.environ.get("GITHUB_TOKEN") else "MISSING",
            "HF_TOKEN": "DETECTED" if os.environ.get("HF_TOKEN") else "MISSING"
        },
        "remotes": {},
        "file_structure": []
    }

    # 1. Map Git Remotes
    try:
        os.chdir(report["nodes"]["ARK_CORE"])
        remotes = subprocess.check_output(["git", "remote", "-v"]).decode().split("\n")
        for r in remotes:
            if r:
                name = r.split()[0]
                url = r.split()[1]
                report["remotes"][name] = url
    except:
        report["remotes"] = "NO_GIT_REPO_FOUND"

    # 2. Map Key Directories
    for root, dirs, files in os.walk(report["nodes"]["ARK_CORE"]):
        if ".git" in root: continue
        report["file_structure"].append(root)

    # 3. Final Export
    with open(os.path.join(report["nodes"]["ARK_CORE"], "omni_map.json"), "w") as f:
        json.dump(report, f, indent=4)
    
    return f"[SUCCESS] Recon Complete. {len(report['file_structure'])} folders mapped into omni_map.json."

if __name__ == "__main__":
    print(run_recon())
