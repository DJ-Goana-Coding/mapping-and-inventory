import os
import shutil

# --- Q.G.T.N.L. (0) // WASHING HARVEST ENGINE V60.31 ---
# Fixed: Loop-Avoidance Logic

EXCLUSIONS = ["Bible", "Ark", "bottles", "S10_OFFLINE"]
TARGET_ROOT = os.path.expanduser("~/ARK_CORE")
STAGING_AREA = os.path.join(TARGET_ROOT, "Partition_46/WASHING_HARVEST_STAGING")

def wash():
    print("🧼 RE-INITIATING STABILIZED WASHING HARVEST...")
    if not os.path.exists(STAGING_AREA):
        os.makedirs(STAGING_AREA)

    indexed_count = 0
    for dirpath, dirs, files in os.walk(TARGET_ROOT):
        # 1. LOOP AVOIDANCE: Skip the staging area itself
        if STAGING_AREA in dirpath:
            continue
            
        # 2. S10 PROTECTION: Hard skip any S10 tethered data
        if "S10" in dirpath:
            continue
            
        for f in files:
            # 3. THE HOLY SHROUD: Filter exclusions
            if any(x.lower() in f.lower() for x in EXCLUSIONS):
                continue
            
            # 4. TARGET SELECTION: Logs, News, and Recriminations
            if f.endswith(('.log', '.txt')) or "news" in f.lower():
                src = os.path.join(dirpath, f)
                dst = os.path.join(STAGING_AREA, f)
                
                # Check if it's already there to avoid redundant work
                if not os.path.exists(dst) or os.path.getmtime(src) > os.path.getmtime(dst):
                    shutil.copy2(src, dst)
                    indexed_count += 1

    print(f"✨ STABILIZED WASH COMPLETE: {indexed_count} NEW/UPDATED FILES STAGED.")

if __name__ == "__main__":
    wash()
