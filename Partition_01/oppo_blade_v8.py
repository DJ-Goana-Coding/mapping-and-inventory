import time, hmac, hashlib, os, requests

# --- ⚔️ OPPO EXECUTION BLADE (V8) ---
SIGNAL_PATH = "citadel_signal.txt"
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT", "QNTUSDT", "KASUSDT"]
STANDARD_TRADE, MOON_TRADE = 7.00, 12.00 

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

def fire_order(coin, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side=BUY&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    sig = hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={sig}", headers={"X-MEXC-APIKEY": API_KEY})
        return r.status_code == 200
    except: return False

print("⚔️ BLADE ACTIVE. LISTENING TO S10+ SCOUT...")

while True:
    if os.path.exists(SIGNAL_PATH):
        with open(SIGNAL_PATH, "r") as f:
            data = f.read().split(",")
        coin, price = data[1], data[2]
        qty = MOON_TRADE if coin in RESTRICTED else STANDARD_TRADE
        
        if fire_order(coin, qty):
            print(f"🔥 SUCCESS: Bought {qty} USD of {coin} at ${price}")
        os.remove(SIGNAL_PATH)
    time.sleep(1)
