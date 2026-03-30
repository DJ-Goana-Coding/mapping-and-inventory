import requests
import json
import datetime
import os

def get_crypto_pulse():
    # Primary targets for the 144-Grid
    targets = ["ripple", "cardano", "bitcoin"]
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(targets)}&vs_currencies=usd"
    
    print(f"[PULSE] {datetime.datetime.now().strftime('%H:%M:%S')} - FETCHING GRID DATA...")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        # Formatting for the 144-Grid Display
        pulse_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "xrp": data['ripple']['usd'],
            "ada": data['cardano']['usd'],
            "btc": data['bitcoin']['usd']
        }
        
        print(f"--- VANGUARD PULSE ---")
        print(f"XRP: ${pulse_data['xrp']}")
        print(f"ADA: ${pulse_data['ada']}")
        print(f"BTC: ${pulse_data['btc']}")
        print(f"-----------------------")
        
        # Save to a log file for T.I.A. to analyze
        log_path = os.path.expanduser("~/ARK_CORE/Partition_01/vanguard_pulse.log")
        with open(log_path, "a") as f:
            f.write(json.dumps(pulse_data) + "\n")
            
        return pulse_data

    except Exception as e:
        print(f"[!] PULSE ERROR: {str(e)}")
        return None

if __name__ == "__main__":
    get_crypto_pulse()
