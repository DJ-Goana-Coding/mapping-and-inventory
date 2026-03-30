import requests, time, hmac, hashlib, os

# --- 🏛️ CITADEL V6: TREASURY & WEIGHTED RE-ENTRY ---
WAR_CHEST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "LTCUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT", "XLMUSDT", "TIAUSDT", "XDCUSDT", "ALGOUSDT", "HBARUSDT",
    "ICPUSDT", "VETUSDT", "NEARUSDT", "FILUSDT", "OPUSDT", "INJUSDT", "RNDRUSDT", "STXUSDT", "KASUSDT", "MXUSDT", "QNTUSDT"
]
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT", "QNTUSDT", "KASUSDT"]
BASE_TRADE_USD = 6.00 

# WEIGHTS: 80% XRP, 12% HBAR, 8% XLM
ACCUM_WEIGHTS = {"XRPUSDT": 0.80, "HBARUSDT": 0.12, "XLMUSDT": 0.08}

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

def execute(coin, side, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    sig = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={sig}", headers={"X-MEXC-APIKEY": API_KEY})
        return "🔥 SUCCESS" if r.status_code == 200 else f"ERR_{r.status_code}"
    except: return "NET_FAIL"

def main():
    session_profit = 0.0
    while True:
        bal = get_balance()
        usdt = float(bal.get('USDT', 0))
        os.system('clear')
        print(f"🏛️  CITADEL V6 TREASURY | 💰 USDT: ${usdt:.2f}")
        print(f"📈 SESSION ACCUMULATION POOL: ${session_profit * 0.5:.4f}")
        print("-" * 65)
        
        for coin in WAR_CHEST:
            try:
                res = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={coin}").json()
                p, c = float(res['lastPrice']), float(res['priceChangePercent'])
                
                # Logic Gate
                action = "HOLD"
                if c < -1.5: action = "BUY"
                elif c > 3.0 and coin not in RESTRICTED: action = "SELL"
                
                status = "SCANNING"
                if action == "SELL" and float(bal.get(coin.replace('USDT',''), 0)) > 0:
                    status = execute(coin, "SELL", BASE_TRADE_USD)
                    if "SUCCESS" in status: session_profit += 1.00 # Placeholder for profit tracking
                
                elif action == "BUY" and usdt >= BASE_TRADE_USD:
                    # Apply Weighted Buying logic if profit exists, otherwise use Base Trade
                    buy_amount = BASE_TRADE_USD
                    if coin in ACCUM_WEIGHTS and session_profit > 0:
                        buy_amount += (session_profit * 0.5 * ACCUM_WEIGHTS[coin])
                    
                    status = execute(coin, "BUY", buy_amount)
                
                elif action == "SELL" and coin in RESTRICTED:
                    status = "🛡️ LOCKED"
                
                print(f"🎯 {coin[:4]:<5}: ${p:<9.4f} | {action:<10} | {status}")
            except: continue
        time.sleep(5)

if __name__ == "__main__":
    main()
