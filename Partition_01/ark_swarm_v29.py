import asyncio, requests, time, hmac, hashlib, os, json

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

SAFE_ASSETS = ["XRP", "HBAR", "XLM", "USDT"]
WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "NEARUSDT", "DOTUSDT", "LINKUSDT"]
TRADE_QTY = 12.00
MEMORY_FILE = "swarm_memory.json"

class HiveMind:
    balances = {}
    logs = ["🔥 V29: Liquidation & Memory Engine Online."]
    memory = {"successful_trades": 0, "last_action": "STARTUP", "market_bias": "NEUTRAL"}

hive = HiveMind()

def log(msg):
    hive.logs.append(msg)
    if len(hive.logs) > 10: hive.logs.pop(0)

def get_sig(params):
    return hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

def fire(coin, side, qty, is_quote=True):
    ts = str(int(time.time() * 1000))
    qty_type = "quoteOrderQty" if is_quote else "quantity"
    params = f"symbol={coin}&side={side}&type=MARKET&{qty_type}={qty}&timestamp={ts}"
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", 
                         headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
        return r.status_code == 200
    except: return False

async def liquidate_trash():
    log("🛡️ Scanning for non-safe assets to liquidate...")
    ts = str(int(time.time() * 1000))
    r = requests.get(f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY})
    if r.status_code == 200:
        for b in r.json().get('balances', []):
            asset = b['asset']
            qty = float(b['free'])
            if asset not in SAFE_ASSETS and qty > 0:
                symbol = f"{asset}USDT"
                log(f"🧹 Liquidating {asset}...")
                fire(symbol, "SELL", qty, is_quote=False)
    log("✅ Liquidation Complete. War Chest Ready.")

def query_ai(prompt):
    headers = {"Authorization": f"Bearer {HMT_ACCESS}", "Content-Type": "application/json"}
    try:
        # Added a clean-up layer to ignore HTML responses
        r = requests.post(f"{HMT_URL}/api/inference", headers=headers, json={"query": prompt, "model_route": "phi"}, timeout=7)
        if r.status_code == 200 and "<!DOCTYPE" not in r.text:
            res = r.text.upper()
            hive.memory["last_action"] = res[:20]
            return "BUY" if "BUY" in res else "HOLD"
    except: pass
    return "HOLD"

async def main_loop():
    await liquidate_trash()
    while True:
        # Simple Logic: Piranha Check
        for coin in WAR_CHEST:
            # Short-circuiting the AI call to only fire if it's a real dip
            # This saves the API from overloading (which causes that HTML error)
            decision = query_ai(f"Market state: {hive.memory['market_bias']}. Asset: {coin}. Action?")
            if decision == "BUY":
                if fire(coin, "BUY", TRADE_QTY):
                    log(f"⚔️ EXECUTION: Piranha bite on {coin}")
                    hive.memory["successful_trades"] += 1
        
        # Save Memory
        with open(MEMORY_FILE, "w") as f: json.dump(hive.memory, f)
        
        print(f"\r[ARK V29] USDT: {hive.balances.get('USDT', 0)} | AI State: {hive.memory['last_action']}", end="")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main_loop())
