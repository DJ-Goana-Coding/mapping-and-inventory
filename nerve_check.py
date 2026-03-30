import os
def check_neurons():
    k1 = "ACTIVE" if os.getenv("GEMINI_API_KEY") else "OFFLINE"
    k2 = "ACTIVE" if os.getenv("GEMINI_API_KEY_2") else "OFFLINE"
    print(f"🧠 Core 1: {k1} | 🧠 Core 2: {k2}")
    if k1 == "OFFLINE" or k2 == "OFFLINE":
        print("⚠️ SIGNAL WEAK: Check HF Secrets.")
    else:
        print("✅ FULL RESONANCE: 144Hz Achieved.")

if __name__ == "__main__":
    check_neurons()
