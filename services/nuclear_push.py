import os, subprocess
def execute_push():
    gh = os.getenv("GITHUB_TOKEN")
    hf = os.getenv("HF_TOKEN")
    user = "DJ-Goanna-Coding"
    if not gh or not hf: return "[-] Error: Tokens missing from environment."
    
    os.chdir(os.path.expanduser("~/ARK_CORE"))
    subprocess.run(["git", "add", "."], capture_output=True)
    subprocess.run(["git", "commit", "-m", "ark: v32 omni-sync"], capture_output=True)
    
    # Absolute injection URLs
    remotes = {
        "origin": f"https://{gh}@github.com/{user}/ARK_CORE.git",
        "hf": f"https://{user}:{hf}@huggingface.co/spaces/{user}/TIA-ARCHITECT-CORE"
    }
    
    results = []
    for name, url in remotes.items():
        subprocess.run(["git", "remote", "set-url", name, url], capture_output=True)
        push = subprocess.run(["git", "push", name, "main", "--force"], capture_output=True)
        results.append(f"[+] {name.upper()} Sync: SUCCESS" if push.returncode == 0 else f"[-] {name.upper()} Sync: FAILED")
    return "\n".join(results)

if __name__ == "__main__":
    print(execute_push())
