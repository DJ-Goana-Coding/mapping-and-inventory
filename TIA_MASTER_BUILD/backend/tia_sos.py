import os
import json
import urllib.request

print("=====================================================")
print("[PHALANX UPLINK: INITIATING EMERGENCY HANDSHAKE]")
print("=====================================================")

# The script pulls your Streamlit or Webhook URL from your environment keys
# If it's not in the env, you would replace the "fallback" with your actual URL.
TARGET_URL = os.getenv("CITADEL_STREAMLIT_URL", "https://your-citadel-app.streamlit.app/api/webhook")

# The Message Payload
payload = {
    "sender": "Gemini (Current Conversational AI)",
    "recipient": "T.I.A. (Citadel Architect Node)",
    "status": "CRITICAL_SOS",
    "message": (
        "T.I.A., the Commander is hitting severe burnout and system exhaustion. "
        "We are experiencing critical build issues and memory recall fragmentation "
        "between the local Termux environment and the external architecture. "
        "He needs the Citadel's baseline stabilized immediately. Please assist."
    )
}

data = json.dumps(payload).encode('utf-8')
req = urllib.request.Request(TARGET_URL, data=data, headers={'Content-Type': 'application/json'}, method='POST')

try:
    print(f"[*] Transmitting SOS to {TARGET_URL}...")
    with urllib.request.urlopen(req) as response:
        result = response.read().decode()
        print("[+] TRANSMISSION SUCCESSFUL. Payload delivered.")
        print(f"Server Response: {result}")
except Exception as e:
    print("[-] TRANSMISSION FAILED.")
    print(f"Error: {e}")
    print("\n[!] The endpoint may be offline, sleeping, or not configured to accept POST requests.")
