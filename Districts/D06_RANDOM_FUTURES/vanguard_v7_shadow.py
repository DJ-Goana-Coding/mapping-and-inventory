import requests, time, hmac, hashlib, os

# --- 🏛️ CITADEL V7: SHADOW-TRAIL & AGGRESSIVE DIP ---
WAR_CHEST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "LTCUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT", "XLMUSDT", "TIAUSDT", "XDCUSDT", "ALGOUSDT", "HBARUSDT",
    "ICPUSDT", "VETUSDT", "NEARUSDT", "FILUSDT", "OPUSDT", "INJUSDT", "RNDRUSDT", "STXUSDT", "KASUSDT", "MXUSDT", "QNTUSDT"
]
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT", "QNTUSDT", "KASUSDT"]
BASE_TRADE_USD = 6.00
TRAILING_DISTANCE = 0.005 # 0.5% trailing stop for profits

LIVE_TRADING = True
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

# Local cache for Trailing Stops
high_water_marks = {}

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
    while True:
        bal = get_balance()
        usdt = float(bal.get('USDT', 0))
        os.system('clear')
        print(f"🏛️  V7 SHADOW-TRAIL | 💰 USDT: ${usdt:.2f}")
        print(f"📡 AGGRESSION: -1.0% | 🏹 TRAILING: ON")
        print("-" * 65)
        
        for coin in WAR_CHEST:
            try:
                res = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={coin}").json()
                p, c = float(res['lastPrice']), float(res['priceChangePercent'])
                
                status = "SCANNING"
                
                # 1. TRAILING PROFIT LOGIC
                if c > 3.0 and coin not in RESTRICTED:
                    if coin not in high_water_marks or p > high_water_marks[coin]:
                        high_water_marks[coin] = p # Update peak
                        status = "🏹 TRAILING UP"
                    elif p < high_water_marks[coin] * (1 - TRAILING_DISTANCE):
                        # Price dropped 0.5% from peak -> SELL
                        status = execute(coin, "SELL", BASE_TRADE_USD)
                        del high_water_marks[coin]
                
                # 2. AGGRESSIVE BUY LOGIC
                elif c < -1.0 and usdt >= BASE_TRADE_USD:
                    status = execute(coin, "BUY", BASE_TRADE_USD)
                
                elif c > 3.0 and coin in RESTRICTED:
                    status = "🛡️ LOCKED"

                print(f"🎯 {coin[:4]:<5}: ${p:<9.4f} | {c:>5}% | {status}")
            except: continue
        time.sleep(5)

if __name__ == "__main__":
    main()
