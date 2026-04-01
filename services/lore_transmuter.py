import os
import time
from google import genai
from datetime import datetime

def transmute_signal_to_lore():
    # 🧬 DUAL-CORE FAILOVER
    keys = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_2")]
    keys = [k for k in keys if k] # Filter out empty keys
    
    if not keys: return "❌ Missing Neural Signal (No API Keys found)."
    
    staging_dir = os.path.expanduser("~/ARK_CORE/Partition_46/WASHING_HARVEST_STAGING")
    
    for key_index, api_key in enumerate(keys):
        for attempt in range(2): # Try each key twice
            try:
                client = genai.Client(api_key=api_key)
                response = client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents="Chronicle the 144-Grid. Australian cyberpunk tone. The Citadel is rising."
                )
                
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"Lore_{ts}_DualCore.txt"
                with open(os.path.join(staging_dir, filename), "w") as shard:
                    shard.write(response.text)
                return f"✨ LORE SECURED (Core {key_index+1}): {filename}"
                
            except Exception as e:
                if "429" in str(e):
                    print(f"⏳ Core {key_index+1} Rate Limited. Switching/Waiting...")
                    time.sleep(20)
                    continue
                return f"❌ AI Error: {str(e)[:50]}"
                
    return "⏳ TOTAL BRAIN OVERHEAT: Both Cores at capacity. Wait 5 mins."
