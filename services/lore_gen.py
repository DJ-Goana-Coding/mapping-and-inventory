import os
from datetime import datetime

# --- Q.G.T.N.L. (0) // LORE GENERATOR ---
# Function: Direct Staging of Lore Shards

STAGING_AREA = os.path.expanduser("~/ARK_CORE/Partition_46/WASHING_HARVEST_STAGING")

def create_shard():
    print("🖋️ INITIATING NEW LORE SHARD...")
    if not os.path.exists(STAGING_AREA):
        os.makedirs(STAGING_AREA)

    title = input("Enter Shard Title (or press Enter for 'Unnamed'): ") or "Unnamed"
    print("--- Enter Content (Type 'SAVE' on a new line to finish) ---")
    
    lines = []
    while True:
        line = input()
        if line.strip().upper() == "SAVE":
            break
        lines.append(line)
    
    content = "\n".join(lines)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Lore_{timestamp}_{title.replace(' ', '_')}.txt"
    filepath = os.path.join(STAGING_AREA, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"TITLE: {title}\n")
        f.write(f"TIMESTAMP: {datetime.now().isoformat()}\n")
        f.write("-" * 20 + "\n")
        f.write(content)
    
    print(f"\n✨ SHARD SEALED: {filename} staged in Partition_46.")

if __name__ == "__main__":
    create_shard()
