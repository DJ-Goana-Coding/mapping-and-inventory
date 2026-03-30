import os
from google import genai

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in environment.")
else:
    client = genai.Client(api_key=api_key)
    print("🛰️ SCANNING AVAILABLE NEURAL MODELS...")
    try:
        # Corrected attribute for 2026 SDK
        for m in client.models.list():
            print(f" > {m.name}")
            print(f"   Actions: {m.supported_actions}")
    except Exception as e:
        print(f"❌ Scan failed: {e}")
