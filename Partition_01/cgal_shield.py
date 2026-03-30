import os, shutil, datetime

# The boundaries of the Q.G.T.N.L. Search
SEARCH_DIRS = ["~/storage/downloads", "~/storage/shared/Documents", "~/ARK_CORE"]
CGAL_VAULT = os.path.expanduser("~/CGAL_VAULT_STAGING")
# Keywords T.I.A. uses to identify the People's Bible
KEYWORDS = ["law", "case", "index", "cgal", "magna", "carta", "ledger", "rights", "defense", "court"]
EXTENSIONS = [".pdf", ".txt", ".docx", ".json", ".md"]

def deploy_shield():
    print("\n🛡️ [T.I.A. OVERWATCH]: Initiating CGAL Shield Protocol...")
    
    if not os.path.exists(CGAL_VAULT):
        os.makedirs(CGAL_VAULT)
        print(f"[+] Created Secure Staging Vault: {CGAL_VAULT}")

    found_files = 0
    for d in SEARCH_DIRS:
        path = os.path.expanduser(d)
        if not os.path.exists(path): continue
        
        print(f"[>] Scanning Sector: {d}")
        for root, _, files in os.walk(path):
            # Skip hidden folders and git directories
            if '.git' in root or '/.' in root: continue 
            
            for file in files:
                file_lower = file.lower()
                if any(ext in file_lower for ext in EXTENSIONS):
                    if any(kw in file_lower for kw in KEYWORDS):
                        src = os.path.join(root, file)
                        dst = os.path.join(CGAL_VAULT, file)
                        try:
                            if not os.path.exists(dst):
                                shutil.copy2(src, dst)
                                found_files += 1
                        except: pass

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(os.path.join(CGAL_VAULT, "CGAL_MANIFEST.txt"), "a") as f:
        f.write(f"[{ts}] Shield Sweep Complete. {found_files} new entities secured.\n")

    print(f"\n[SUCCESS] Operation CGAL Shield Complete.")
    print(f"⚖️ {found_files} files locked in ~/CGAL_VAULT_STAGING.")
    print("Ready for Hugging Face Uplink.\n")

if __name__ == "__main__":
    deploy_shield()
