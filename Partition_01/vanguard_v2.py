import requests
import time
import hmac
import hashlib
import os

# --- 🏛️ CITADEL FRAMEWORK: VANGUARD V2.1 ---
NODE_NAME = "Vanguard Hub (Node 01)"
WAR_CHEST = ["TIAUSDT", "XDCUSDT", "ALGOUSDT", "SOLUSDT", "ADAUSDT", "LINKUSDT"]
BASE_TRADE_USD = 7.00 

# Tactical Path Pivot: Using Internal Storage Bridge if SD is locked
LOCAL_VAULT = "/sdcard/Documents/vanguard_audit.csv"

LIVE_TRADING = False 
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

# Create local audit trail with Permission Fail-Safe
try:
    os.makedirs(os.path.dirname(LOCAL_VAULT), exist_ok=True)
    if not os.path.exists(LOCAL_VAULT):
        with open(LOCAL_VAULT, "w") as f:
            f.write("timestamp,symbol,price,strategy,decision,status\n")
except PermissionError:
    print("⚠️ SD Card Locked. Pivoting to local Termux storage...")
    LOCAL_VAULT = "vanguard_audit_emergency.csv"

def get_mexc_data(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=5).json()
        return {"p": float(res['lastPrice']), "c": float(res['priceChangePercent']), "v": float(res['quoteVolume'])}
    except: return None

def ask_oracle(symbol, data):
    prompt = f"Asset: {symbol} | Price: ${data['p']} | Change: {data['c']}% | Output: 'STRATEGY | BUY/SELL/HOLD'"
    payload = {"model": "0xroyce/plutus:latest", "prompt": prompt, "stream": False}
    try:
        res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        resp = res.json().get('response', '').strip().upper()
        if "BUY" in resp: return resp, "BUY"
        elif "SELL" in resp: return resp, "SELL"
        else: return resp, "HOLD"
    except: return "AION_TIMEOUT", "HOLD"

def main_vanguard():
    while True:
        os.system('clear')
        print(f"🏛️ CITADEL VANGUARD: ACTIVE")
        print(f"💾 AUDIT PATH: {LOCAL_VAULT}")
        print("-" * 60)
        for coin in WAR_CHEST:
            data = get_mexc_data(coin)
            if not data: continue
            vote_str, action = ask_oracle(coin, data)
            print(f"🎯 {coin[:4]}: ${data['p']:<8.4f} | {vote_str[:25]:<25}")
            with open(LOCAL_VAULT, "a") as f:
                f.write(f"{time.time()},{coin},{data['p']},{vote_str},{action},SAFETY\n")
        print("-" * 60)
        time.sleep(60)

if __name__ == "__main__":
    main_vanguard()
