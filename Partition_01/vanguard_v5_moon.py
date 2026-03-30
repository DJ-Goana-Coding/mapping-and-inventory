import requests, time, hmac, hashlib, os

# --- 🏛️ CITADEL V5.2: MOON-WALKER (ACCUMULATION) ---
# TARGETS: ISO20022, AI, AND TOP 30
WAR_CHEST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "LTCUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT", "XLMUSDT", "TIAUSDT", "XDCUSDT", "ALGOUSDT", "HBARUSDT",
    "ICPUSDT", "VETUSDT", "NEARUSDT", "FILUSDT", "OPUSDT", "INJUSDT", "RNDRUSDT", "STXUSDT", "KASUSDT", "MXUSDT", "QNTUSDT"
]
# FORBIDDEN TO SELL (THE MOON LIST)
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT", "QNTUSDT", "KASUSDT"]
BASE_TRADE_USD = 6.00 

LIVE_TRADING = True
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

def get_balance():
    if not API_KEY: return {}
    ts = str(int(time.time() * 1000))
    sig = hmac.new(SECRET_KEY.encode(), f"timestamp={ts}".encode(), hashlib.sha256).hexdigest()
    url = f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={sig}"
    try:
        res = requests.get(url, headers={"X-MEXC-APIKEY": API_KEY}).json()
        return {b['asset']: b['free'] for b in res['balances'] if float(b['free']) > 0}
    except: return {}

def ask_oracle(symbol, p, c):
    # Pure Execution Bot Prompt (Cold/Clinical)
    prompt = f"Trader ID: 0xRoyce. Asset: {symbol} P: {p} C: {c}%. If C < -1.5 BUY. If C > 3.0 SELL. Else HOLD. ONE WORD ONLY."
    try:
        res = requests.post("http://localhost:11434/api/generate", 
                            json={"model": "llama3.2:1b-instruct-q8_0", "prompt": prompt, "stream": False}, 
                            timeout=10)
        return res.json().get('response', '').strip().upper()
    except: return "WAIT"

def execute(coin, side):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={BASE_TRADE_USD}&timestamp={ts}"
    sig = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={sig}", headers={"X-MEXC-APIKEY": API_KEY})
        return "🔥 SUCCESS" if r.status_code == 200 else f"ERR_{r.status_code}"
    except: return "NET_FAIL"

def main():
    while True:
        bal = get_balance()
        usdt = float(bal.get('USDT', 0))
        os.system('clear')
        print(f"🏛️  MOON-WALKER V5.2 | 💰 USDT: ${usdt:.2f} | 🛡️ RESTRICTED: XRP, XLM, HBAR")
        print("-" * 65)
        
        for coin in WAR_CHEST:
            try:
                res = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={coin}").json()
                p, c = float(res['lastPrice']), float(res['priceChangePercent'])
                vote = ask_oracle(coin, p, c)
                
                action = "BUY" if "BUY" in vote else "SELL" if "SELL" in vote else "HOLD"
                status = "SCANNING"
                
                if action == "BUY" and usdt >= BASE_TRADE_USD:
                    status = execute(coin, "BUY")
                elif action == "SELL" and coin not in RESTRICTED and float(bal.get(coin.replace('USDT',''), 0)) > 0:
                    status = execute(coin, "SELL")
                elif action == "SELL" and coin in RESTRICTED:
                    status = "🛡️ LOCKED" # Will not sellrestricted bank coins
                
                print(f"🎯 {coin[:4]:<5}: ${p:<9.4f} | {vote:<10} | {status}")
            except: continue
        time.sleep(5)

if __name__ == "__main__":
    main()
