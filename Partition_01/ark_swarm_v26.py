import asyncio, requests, time, hmac, hashlib, os, json, math

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')
CITADEL_PAT = os.environ.get('CITADEL_ACCESS')

# THE TOP 30 WAR CHEST
WAR_CHEST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", 
    "AVAXUSDT", "TRXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "SHIBUSDT", "NEARUSDT", 
    "LTCUSDT", "BCHUSDT", "UNIUSDT", "APTUSDT", "XLMUSDT", "SUIUSDT", "ARBUSDT", 
    "OPUSDT", "FILUSDT", "INJUSDT", "RNDRUSDT", "GRTUSDT", "VETUSDT", "HBARUSDT", 
    "TIAUSDT", "ALGOUSDT"
]
RESTRICTED = ["XRPUSDT"] # Never auto-sell the core XRP stack
TRADE_QTY = 12.00
TARGET_XRP = 500.00
SENTRY_LOSS_LIMIT = -2.0 

GDRIVE_PATH = "/data/data/com.termux/files/home/storage/shared/ArkFleet"
try: os.makedirs(GDRIVE_PATH, exist_ok=True)
except: pass
STATE_FILE = f"{GDRIVE_PATH}/market_state.json"
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"

class HiveMind:
    market_data = {coin: {'price': 0.0, 'change': 0.0, 'history': []} for coin in WAR_CHEST}
    balances = {'USDT': 0.0, 'XRP': 0.0}
    buy_prices = {} 
    logs = ["🕸️ V26 Top-30 Swarm Initialized."]

hive = HiveMind()

def log(msg):
    hive.logs.append(msg)
    if len(hive.logs) > 8: hive.logs.pop(0)

def get_sig(params):
    return hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

def fire(coin, side, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
        if r.status_code == 200:
            try: open(LEDGER_FILE, 'a').write(f"{time.ctime()},{coin},{side},{qty},SWARM_EXECUTION\n")
            except: pass
            return True
    except: pass
    return False

def query_airgap_ai(prompt, model="phi"):
    if not HMT_ACCESS: return "HOLD"
    headers = {"Authorization": f"Bearer {HMT_ACCESS}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{HMT_URL}/api/inference", headers=headers, json={"query": prompt, "model_route": model}, timeout=4)
        if r.status_code == 200 and "BUY" in r.text.upper(): return "BUY"
    except: pass
    return "HOLD"

# 1. 👁️ ORACLE NODE (Bulk Fetch Optimization)
async def oracle_node():
    while True:
        try:
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                hive.balances = {b['asset']: float(b['free']) for b in r_bal.json().get('balances', []) if float(b['free']) > 0}

            # Pull ALL MEXC prices in one call to save bandwidth
            r_all = await asyncio.to_thread(requests.get, "https://api.mexc.com/api/v3/ticker/price", timeout=3)
            if r_all.status_code == 200:
                price_dict = {item['symbol']: float(item['price']) for item in r_all.json()}
                
                for coin in WAR_CHEST:
                    p = price_dict.get(coin, 0.0)
                    if p == 0.0: continue
                    old_p = hive.market_data[coin]['price']
                    diff = ((p - old_p) / old_p * 100) if old_p > 0 else 0.0
                    
                    hive.market_data[coin]['price'] = p
                    hive.market_data[coin]['change'] = diff
                    hive.market_data[coin]['history'].append(p)
                    if len(hive.market_data[coin]['history']) > 15: hive.market_data[coin]['history'].pop(0)

            try: await asyncio.to_thread(lambda: open(STATE_FILE, "w").write(json.dumps({"timestamp": time.time(), "balances": hive.balances, "market": hive.market_data})))
            except: pass
        except: pass
        await asyncio.sleep(3)

# 2. 🏹 HUNTER NODE 
async def hunter_node():
    while True:
        try:
            usdt = hive.balances.get('USDT', 0.0)
            for coin in WAR_CHEST:
                diff = hive.market_data[coin]['change']
                if diff < -0.50 and usdt >= TRADE_QTY:
                    log(f"🏹 HUNTER: Dip on {coin}. Routing to Phi...")
                    if await asyncio.to_thread(query_airgap_ai, f"{coin} crashed {diff}%. BUY/HOLD?", "phi") == "BUY":
                        if await asyncio.to_thread(fire, coin, "BUY", TRADE_QTY):
                            hive.buy_prices[coin] = hive.market_data[coin]['price']
                            log(f"⚔️ AION: Phi Strike on {coin}")
        except: pass
        await asyncio.sleep(4)

# 3. ⚓ ADMIRAL NODE 
async def admiral_node():
    while True:
        try:
            usdt = hive.balances.get('USDT', 0.0)
            for coin in WAR_CHEST:
                hist = hive.market_data[coin]['history']
                if len(hist) >= 10 and usdt >= TRADE_QTY:
                    mean = sum(hist) / len(hist)
                    std_dev = math.sqrt(sum((x - mean) ** 2 for x in hist) / len(hist))
                    if hist[-1] > hist[0] and std_dev < (mean * 0.005):
                        log(f"⚓ ADMIRAL: Stability on {coin}. Routing to MoE 128...")
                        if await asyncio.to_thread(query_airgap_ai, f"Asset {coin} steady. Confirm BUY?", "moe") == "BUY":
                            if await asyncio.to_thread(fire, coin, "BUY", TRADE_QTY):
                                hive.buy_prices[coin] = hist[-1]
                                log(f"⚔️ AION: MoE Strike on {coin}")
        except: pass
        await asyncio.sleep(30) 

# 4. 🛡️ SENTRY NODE
async def sentry_node():
    while True:
        try:
            for coin in list(hive.buy_prices.keys()):
                curr_p = hive.market_data[coin]['price']
                entry_p = hive.buy_prices[coin]
                loss_pct = ((curr_p - entry_p) / entry_p) * 100
                if loss_pct <= SENTRY_LOSS_LIMIT and coin not in RESTRICTED:
                    log(f"🛡️ SENTRY: Breach on {coin} ({loss_pct:.2f}%). Liquidating.")
                    if await asyncio.to_thread(fire, coin, "SELL", TRADE_QTY):
                        del hive.buy_prices[coin]
                        log(f"⚔️ AION: Sentry Cleared {coin}")
        except: pass
        await asyncio.sleep(5)

# 5. 🖥️ DASHBOARD NODE
async def dashboard_node():
    while True:
        os.system('clear')
        usdt, xrp = hive.balances.get('USDT', 0.0), hive.balances.get('XRP', 0.0)
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE ARK FLEET: V26 TOP-30 MULTI-SWARM                  ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WALLET: ${usdt:.2f} | 💎 XRP: {xrp:.2f}/{TARGET_XRP}                  ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for msg in hive.logs: print(f"║ {msg[:55]:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        
        # Display Top 8 so screen doesn't break, but all 30 are trading
        display_coins = WAR_CHEST[:8]
        for coin in display_coins:
            d = hive.market_data[coin]
            print(f"║ 🎯 {coin[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}%{' ' * 23}║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        print(f"Tracking 30 assets silently in background. Target: Top 30 Cap.")
        if xrp >= TARGET_XRP: break
        await asyncio.sleep(1)

async def main():
    log("✅ Initiating Top-30 Asynchronous Swarm...")
    await asyncio.gather(oracle_node(), hunter_node(), admiral_node(), sentry_node(), dashboard_node())

if __name__ == "__main__": asyncio.run(main())
