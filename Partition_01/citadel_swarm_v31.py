import asyncio, requests, time, hmac, hashlib, os, json, math

# --- ⚙️ FLEET PARAMETERS ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

SAFE_ASSETS = ["XRP", "HBAR", "XLM", "USDT"]
WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "TRXUSDT", "LINKUSDT", "TIAUSDT"]
TRADE_QTY = 12.00
BASE_LOSS_LIMIT = -2.0 
HARVEST_TARGET = 1.5

GDRIVE_PATH = "/data/data/com.termux/files/home/storage/shared/ArkFleet"
os.makedirs(GDRIVE_PATH, exist_ok=True)
STATE_FILE = f"{GDRIVE_PATH}/market_state.json"
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"
MEMORY_FILE = f"{GDRIVE_PATH}/swarm_memory.json"

class HiveMind:
    market_data = {coin: {'price': 0.0, 'change': 0.0, 'history': []} for coin in WAR_CHEST}
    balances = {'USDT': 0.0}
    buy_prices = {} 
    logs = ["🕸️ V31 Sovereign Swarm Online."]
    memory = {"wins": 0, "fails": 0, "mood": "NEUTRAL", "last_ai_thought": "STARTUP"}

hive = HiveMind()

def log(msg):
    hive.logs.append(msg)
    if len(hive.logs) > 8: hive.logs.pop(0)

def get_sig(params):
    return hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

def fire(coin, side, qty, is_quote=True):
    ts = str(int(time.time() * 1000))
    q_type = "quoteOrderQty" if is_quote else "quantity"
    params = f"symbol={coin}&side={side}&type=MARKET&{q_type}={qty}&timestamp={ts}"
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", 
                         headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
        if r.status_code == 200:
            with open(LEDGER_FILE, 'a') as f: f.write(f"{time.ctime()},{coin},{side},{qty}\n")
            return True
    except: return False

def query_citadel_ai(prompt, model="phi"):
    """The Airgapped Thinking Process"""
    headers = {"Authorization": f"Bearer {HMT_ACCESS}", "Content-Type": "application/json"}
    context = f"Status: {hive.memory['wins']}W/{hive.memory['fails']}L. Mood: {hive.memory['mood']}. "
    try:
        r = requests.post(f"{HMT_URL}/api/inference", headers=headers, json={"query": context + prompt, "model_route": model}, timeout=7)
        if r.status_code == 200 and "<!DOCTYPE" not in r.text:
            thought = r.text.strip().upper()
            hive.memory["last_ai_thought"] = thought[:25]
            return "BUY" if "BUY" in thought else "HOLD"
    except: pass
    return "HOLD"

# --- 👁️ ORACLE: DATA AGGREGATION ---
async def oracle_node():
    while True:
        try:
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                for b in r_bal.json().get('balances', []):
                    if b['asset'] == 'USDT': hive.balances['USDT'] = float(b['free'])

            r_all = await asyncio.to_thread(requests.get, "https://api.mexc.com/api/v3/ticker/price", timeout=3)
            if r_all.status_code == 200:
                p_map = {i['symbol']: float(i['price']) for i in r_all.json()}
                for coin in WAR_CHEST:
                    p = p_map.get(coin, 0.0)
                    if p == 0.0: continue
                    old = hive.market_data[coin]['price']
                    hive.market_data[coin]['price'] = p
                    hive.market_data[coin]['change'] = ((p - old) / old * 100) if old > 0 else 0.0
                    hive.market_data[coin]['history'].append(p)
                    if len(hive.market_data[coin]['history']) > 20: hive.market_data[coin]['history'].pop(0)

            with open(STATE_FILE, "w") as f: json.dump({"market": hive.market_data, "wallet": hive.balances}, f)
        except: pass
        await asyncio.sleep(3)

# --- 🏹 PIRANHA: ADAPTIVE SNIPER ---
async def piranha_node():
    while True:
        try:
            if hive.balances['USDT'] >= TRADE_QTY:
                for coin in WAR_CHEST:
                    h = hive.market_data[coin]['history']
                    if len(h) < 10: continue
                    # Pulse Calculation
                    pulse = sum(abs((h[i]-h[i-1])/h[i-1]*100) for i in range(1, len(h)))/len(h)
                    trigger = max(-0.15, -(pulse * 2.5))
                    diff = hive.market_data[coin]['change']
                    
                    if diff < trigger:
                        log(f"🐟 PIRANHA: {coin} Trigger {diff:.2f}%")
                        if await asyncio.to_thread(query_citadel_ai, f"Bite {coin}?", "phi") == "BUY":
                            if await asyncio.to_thread(fire, coin, "BUY", TRADE_QTY):
                                hive.buy_prices[coin] = hive.market_data[coin]['price']
                                hive.memory["wins"] += 1
                                log(f"⚔️ AION: Piranha Strike {coin}")
        except: pass
        await asyncio.sleep(5)

# --- 🌾 HARVESTER: PROFIT SWEEPER ---
async def harvester_node():
    while True:
        try:
            for coin in list(hive.buy_prices.keys()):
                curr = hive.market_data[coin]['price']
                entry = hive.buy_prices[coin]
                pnl = ((curr - entry) / entry) * 100
                
                if pnl >= HARVEST_TARGET:
                    log(f"🌾 HARVEST: Sweeping {coin} (+{pnl:.2f}%)")
                    if await asyncio.to_thread(fire, coin, "SELL", TRADE_QTY):
                        del hive.buy_prices[coin]
                elif pnl <= BASE_LOSS_LIMIT and coin not in SAFE_ASSETS:
                    log(f"🛡️ SENTRY: Cutting {coin} ({pnl:.2f}%)")
                    if await asyncio.to_thread(fire, coin, "SELL", TRADE_QTY):
                        del hive.buy_prices[coin]
                        hive.memory["fails"] += 1
        except: pass
        await asyncio.sleep(5)

# --- 🖥️ DASHBOARD: ALIEN COCKPIT ---
async def dashboard_node():
    while True:
        os.system('clear')
        u = hive.balances.get('USDT', 0.0)
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE CITADEL V31: SOVEREIGN SWARM                      ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WALLET: ${u:.2f} | 🧠 AI: {hive.memory['last_ai_thought']}          ║")
        print(f"║ 📊 SCORE: {hive.memory['wins']}W / {hive.memory['fails']}L | ☁️ G-DRIVE: SYNCED              ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for m in hive.logs: print(f"║ {m:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for c in WAR_CHEST[:6]:
            d = hive.market_data[c]
            print(f"║ 🎯 {c[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}%{' ' * 23}║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        with open(MEMORY_FILE, "w") as f: json.dump(hive.memory, f)
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(oracle_node(), piranha_node(), harvester_node(), dashboard_node())

if __name__ == "__main__": asyncio.run(main())
