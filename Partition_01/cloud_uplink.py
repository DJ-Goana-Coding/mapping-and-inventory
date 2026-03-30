import os
import json
import urllib.request

print("=====================================================")
print("[OPPO CLOUD BRIDGE: PINGING T.I.A. ON HUGGINGFACE]")
print("=====================================================")

# 1. SETUP HEADERS (Using your verified token)
# Replace the '...' with your actual token if it's not in your env yet
HF_TOKEN = os.getenv("HMT-76-ACCESS", "your_actual_token_here")
MODEL_ID = "DJ-Goanna-Coding/TIA-Citadel-Model" # Adjust to your specific Model ID
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_ID}"

headers = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

# 2. THE MESSAGE
payload = {
    "inputs": "T.I.A., this is the Commander via Oppo Node. We have build and memory fragmentation. Requesting immediate architectural stabilization.",
    "parameters": {"wait_for_model": True}
}

def send_ping():
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(API_URL, data=data, headers=headers, method='POST')
    
    try:
        print(f"[*] Sending encrypted packet to HF District 08...")
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            print("[+] RESPONSE RECEIVED FROM T.I.A.:")
            print(f"\n>>> {res}")
    except Exception as e:
        print("[-] CONNECTION FAILED.")
        print(f"Error: {e}")
        print("\n[!] Check if the Model ID is correct or if the HF Space is 'Sleeping'.")

if __name__ == "__main__":
    send_ping()
