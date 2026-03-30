import requests
import json
import os

# --- Q.G.T.N.L. (0) // MARKET SENSOR ENGINE ---
# Targets: BTC, ETH, Silver (XAG), Copper (HG)

def get_market_pulse():
    pulse = {}
    try:
        # 1. Crypto Pulse (via CoinGecko)
        crypto_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
        c_res = requests.get(crypto_url).json()
        pulse['BTC'] = f"${c_res['bitcoin']['usd']:,}"
        pulse['ETH'] = f"${c_res['ethereum']['usd']:,}"
        
        # 2. Metal Pulse (Placeholder for live Commodities API)
        # Note: Professional Metal APIs usually require a key. 
        # We will set placeholders that you can update in the Vault.
        pulse['SILVER'] = "$31.45 (Staged)"
        pulse['COPPER'] = "$4.12 (Staged)"
        
        return pulse
    except Exception as e:
        return {"Error": "Aether-Link Interrupted"}

if __name__ == "__main__":
    print(f"Current Pulse: {get_market_pulse()}")
