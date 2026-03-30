import os, subprocess, json
def perform_total_recon():
    report = {
        "architect": "Chance",
        "timestamp": str(os.popen("date").read().strip()),
        "env_secrets": {
            "GITHUB_TOKEN": "DETECTED" if os.getenv("GITHUB_TOKEN") else "MISSING",
            "HF_TOKEN": "DETECTED" if os.getenv("HF_TOKEN") else "MISSING"
        },
        "structure": [d for d in os.listdir(os.path.expanduser("~/ARK_CORE"))]
    }
    with open(os.path.expanduser("~/ARK_CORE/omni_map.json"), "w") as f:
        json.dump(report, f, indent=4)
    return "[SUCCESS] Recon Complete. Omni-Map Updated."

if __name__ == "__main__":
    print(perform_total_recon())
