import os, subprocess, json

def map_system():
    report = {
        "timestamp": str(os.popen("date").read().strip()),
        "root_folders": {},
        "git_remotes": {},
        "env_tokens": {}
    }

    # 1. Map Folders
    target_dirs = ["~/ARK_CORE", "~/ARK_CORE/services", "~/ARK_CORE/Partition_01", "~/ARK_CORE/Forever_Learning"]
    for d in target_dirs:
        path = os.path.expanduser(d)
        if os.path.exists(path):
            files = os.listdir(path)
            report["root_folders"][d] = {"status": "ACTIVE", "file_count": len(files)}
        else:
            report["root_folders"][d] = {"status": "MISSING"}

    # 2. Map Git Remotes
    try:
        os.chdir(os.path.expanduser("~/ARK_CORE"))
        remotes = subprocess.check_output(["git", "remote", "-v"]).decode().split("\n")
        for r in remotes:
            if r: report["git_remotes"][r.split()[0]] = r.split()[1]
    except: report["git_remotes"] = "NO_GIT_REPO_FOUND"

    # 3. Check for Embedded Keys
    report["env_tokens"]["GITHUB_TOKEN"] = "DETECTED" if os.getenv("GITHUB_TOKEN") else "MISSING"
    report["env_tokens"]["HF_TOKEN"] = "DETECTED" if os.getenv("HF_TOKEN") else "MISSING"

    # 4. Save Report
    with open(os.path.expanduser("~/ARK_CORE/discovery_report.json"), 'w') as f:
        json.dump(report, f, indent=4)
    
    return "[SUCCESS] System Map Created: ~/ARK_CORE/discovery_report.json"

if __name__ == "__main__":
    print(map_system())
