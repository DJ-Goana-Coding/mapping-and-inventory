import requests
import time
import hmac
import hashlib
import os

# --- 🏛️ CITADEL VANGUARD V3.1: FAST-EXECUTION ---
WAR_CHEST = ["TIAUSDT", "XDCUSDT", "ALGOUSDT", "ADAUSDT"]
BASE_TRADE_USD = 6.00 
LOCAL_VAULT = "/sdcard/Documents/vanguard_audit.csv"

# ⚠️ THE FINAL SAFETY: Set to True for Live MEXC Execution
LIVE_TRADING = True 

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

def get_mexc_data(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/24hr?symbol={symbol}"
        res = requests.get(url, timeout=5).json()
        return {"p": float(res['lastPrice']), "c": float(res['priceChangePercent'])}
    except: return None

def ask_oracle(symbol, data):
    # Using the 1B model for high-speed scalping logic
    prompt = f"Asset: {symbol} Price: ${data['p']} Change: {data['c']}%. Act as a scalper. If price is up, SELL. If down, BUY. Else HOLD. Output ONE WORD ONLY."
    payload = {"model": "llama3.2:1b-instruct-q8_0", "prompt": prompt, "stream": False}
    try:
        res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
        resp = res.json().get('response', '').strip().upper()
        return resp, ("BUY" if "BUY" in resp else "SELL" if "SELL" in resp else "HOLD")
    except: return "WAIT", "HOLD"

def execute_order(symbol, side):
    if not LIVE_TRADING or not API_KEY or not SECRET_KEY: return "SAFETY"
    ts = str(int(time.time() * 1000))
    params = f"symbol={symbol}&side={side}&type=MARKET&quoteOrderQty={BASE_TRADE_USD}&timestamp={ts}"
    signature = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()
    headers = {"X-MEXC-APIKEY": API_KEY, "Content-Type": "application/json"}
    url = f"https://api.mexc.com/api/v3/order?{params}&signature={signature}"
    try:
        r = requests.post(url, headers=headers)
        return "🔥 SUCCESS" if r.status_code == 200 else f"ERR_{r.status_code}"
    except: return "NET_ERR"

def main_vanguard():
    while True:
        os.system('clear')
        print(f"🏛️ CITADEL VANGUARD V3.1: LIVE-FIRE")
        print(f"🧠 ORACLE: Llama-3.2-1B (High-Speed)")
        print(f"🔥 TRADING: {'ON' if LIVE_TRADING else 'OFF'}")
        print("-" * 60)
        for coin in WAR_CHEST:
            data = get_mexc_data(coin)
            if not data: continue
            vote, action = ask_oracle(coin, data)
            status = execute_order(coin, action) if action != "HOLD" else "SCANNING"
            print(f"🎯 {coin[:4]}: ${data['p']:<8.4f} | {vote:<10} | {status}")
            with open(LOCAL_VAULT, "a") as f:
                f.write(f"{time.time()},{coin},{data['p']},{vote},{action},{status}\n")
        time.sleep(60)

if __name__ == "__main__":
    main_vanguard()
