import os
import time
import requests
import json

# The S10 (localhost-3) IP from your mesh
S10_IP = "100.97.78.44"
URL = f"http://{S10_IP}:8080/status.json"
LOG_URL = f"http://{S10_IP}:8080/latest.log"

def render_dashboard():
    os.system('clear')
    print("="*50)
    print("       CITADEL OMEGA // GOD-VIEW DASHBOARD       ")
    print(f"       RESONANCE: 333Hz // GRID: 144-ACTIVE      ")
    print("="*50)
    
    try:
        # Fetch the Ark Balance from the S10
        response = requests.get(URL, timeout=5)
        data = response.json()
        
        print(f"\n[ARK STATUS]      : {data['status']}")
        print(f"[TOTAL STRIKES]   : {data['total_extractions']}")
        print(f"[VAULTED USDT]    : {data['vaulted_usdt']} USDT")
        print(f"[LAST SYNC]       : {data['last_sync']}")
        
        # Fetch the Latest Execution log
        log_res = requests.get(LOG_URL, timeout=5)
        latest_strike = log_res.text.strip().split('\n')[-1]
        print(f"\n[LATEST STRIKE]   : {latest_strike}")
        
    except Exception as e:
        print(f"\n[!] SHROUD DISCONNECTED: {e}")
        print("[ADVICE] Check S10 'Heartbeat Server' status.")
    
    print("\n" + "="*50)
    print("Monitoring 14-Space Swarm... (Ctrl+C to exit)")

if __name__ == "__main__":
    while True:
        render_dashboard()
        time.sleep(30) # 333Hz Stable Refresh Rate
