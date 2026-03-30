import requests, time, hmac, hashlib, os

# --- 🏛️ TITAN MASTER V11 (500 XRP MISSION) ---
WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "AVAXUSDT", "DOGEUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "LTCUSDT", "BCHUSDT", "TRXUSDT", "UNIUSDT", "XLMUSDT", "TIAUSDT", "XDCUSDT", "ALGOUSDT", "HBARUSDT", "ICPUSDT", "VETUSDT", "NEARUSDT", "FILUSDT", "OPUSDT", "INJUSDT", "RNDRUSDT", "STXUSDT", "KASUSDT", "MXUSDT", "QNTUSDT"]
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT", "QNTUSDT"]
STANDARD_BUY, MOON_BUY = 7.00, 12.00 

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

def get_bal():
    ts = str(int(time.time() * 1000))
    sig = hmac.new(SECRET_KEY.encode(), f"timestamp={ts}".encode(), hashlib.sha256).hexdigest()
    try:
        r = requests.get(f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={sig}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=5).json()
        return {b['asset']: b['free'] for b in r['balances'] if float(b['free']) > 0}
    except: return {}

def fire(coin, side, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    sig = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()
    requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={sig}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)

while True:
    try:
        bal = get_bal()
        usdt, xrp = float(bal.get('USDT', 0)), float(bal.get('XRP', 0))
        os.system('clear')
        print(f"🏛️ TITAN V11 | 💰 USDT: ${usdt:.2f} | 💎 XRP: {xrp:.2f}/500")
        print(f"📡 SCANNING TOP 30 | 🛡️ MOON-LOCK: ACTIVE")
        print("-" * 55)

        for coin in WAR_CHEST:
            res = requests.get(f"https://api.mexc.com/api/v3/ticker/24hr?symbol={coin}", timeout=2).json()
            p, c = float(res['lastPrice']), float(res['priceChangePercent'])
            status = "SCAN"

            if c < -1.0 and usdt >= MOON_BUY:
                qty = MOON_BUY if coin in RESTRICTED else STANDARD_BUY
                fire(coin, "BUY", qty)
                status = f"🔥 BOUGHT ${qty}"
            elif c > 3.0 and coin not in RESTRICTED:
                fire(coin, "SELL", STANDARD_BUY)
                status = "💰 PROFIT"
            print(f"🎯 {coin[:4]:<5}: ${p:<9.4f} | {c:>6.2f}% | {status}")
        
        if xrp >= 500: print("\n🏆 500 XRP SECURED!"); break
        time.sleep(2)
    except: continue
