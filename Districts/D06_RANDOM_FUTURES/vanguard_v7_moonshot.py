import requests, time, hmac, hashlib, os

# --- 🏛️ CITADEL V7.2: MOON-SHOT ACCUMULATION (AGGRESSIVE) ---
WAR_CHEST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT",
    "LTCUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT", "XLMUSDT", "TIAUSDT", "XDCUSDT", "ALGOUSDT", "HBARUSDT",
    "ICPUSDT", "VETUSDT", "NEARUSDT", "FILUSDT", "OPUSDT", "INJUSDT", "RNDRUSDT", "STXUSDT", "KASUSDT", "MXUSDT", "QNTUSDT"
]
# FORBIDDEN TO SELL
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT", "QNTUSDT", "KASUSDT"]

# TACTICAL SIZING
STANDARD_TRADE = 7.00 # $10.50 AUD
MOON_TRADE = 12.00    # $18.00 AUD (Aggressive build for XRP/HBAR/XLM)

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
    while True:
        bal = get_balance()
        usdt = float(bal.get('USDT', 0))
        os.system('clear')
        print(f"🏛️  V7.2 MOON-SHOT | 💰 USDT: ${usdt:.2f} | 🛡️ MOON-LOCK: ACTIVE")
        print("-" * 65)
        
        for coin in WAR_CHEST:
            try:
                res = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={coin}").json()
                p, c = float(res['lastPrice']), float(res['priceChangePercent'])
                status = "SCANNING"
                
                # AGGRESSIVE BUY ON -1.0% DIP
                if c < -1.0 and usdt >= MOON_TRADE:
                    qty = MOON_TRADE if coin in RESTRICTED else STANDARD_TRADE
                    status = execute(coin, "BUY", qty)
                
                # PROFIT SELL ON +3.0% SPIKE (EXCEPT RESTRICTED)
                elif c > 3.0 and coin not in RESTRICTED:
                    status = execute(coin, "SELL", STANDARD_TRADE)
                
                # THE IRON BANK PROTECTION
                elif c > 3.0 and coin in RESTRICTED:
                    status = "🛡️ LOCKED"

                print(f"🎯 {coin[:4]:<5}: ${p:<9.4f} | {c:>6.2f}% | {status}")
            except: continue
        time.sleep(5)

if __name__ == "__main__":
    main()
