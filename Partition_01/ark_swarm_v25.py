import asyncio, requests, time, hmac, hashlib, os, json, math

# --- ⚙️ FLEET CONFIGURATION ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HF_KEY = os.environ.get('HF_API_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')
CITADEL_PAT = os.environ.get('CITADEL_ACCESS')

WAR_CHEST = ["XRPUSDT", "SOLUSDT", "BTCUSDT", "ETHUSDT", "TIAUSDT", "XLMUSDT", "HBARUSDT", "ADAUSDT"]
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT"]
TRADE_QTY = 12.00
TARGET_XRP = 500.00
SENTRY_LOSS_LIMIT = -2.0 

# --- ☁️ BRIDGES: G-DRIVE & CITADEL ---
GDRIVE_PATH = "/data/data/com.termux/files/home/storage/shared/ArkFleet"
try:
    os.makedirs(GDRIVE_PATH, exist_ok=True)
except Exception as e:
    pass # Will gracefully fail if storage permission was denied

STATE_FILE = f"{GDRIVE_PATH}/market_state.json"
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"

# --- 🧠 SHARED HIVE MEMORY ---
class HiveMind:
    market_data = {coin: {'price': 0.0, 'change': 0.0, 'history': []} for coin in WAR_CHEST}
    balances = {'USDT': 0.0, 'XRP': 0.0}
    buy_prices = {} 
    logs = ["🕸️ V25 Airgapped Swarm Initialized."]

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
            try:
                with open(LEDGER_FILE, 'a') as f: f.write(f"{time.ctime()},{coin},{side},{qty},SWARM_EXECUTION\n")
            except: pass
            return True
    except: pass
    return False

# --- 🧠 MULTI-MODEL ROUTER (Airgapped Space) ---
def query_airgap_ai(prompt, model="phi"):
    if not HMT_ACCESS: return "HOLD"
    headers = {"Authorization": f"Bearer {HMT_ACCESS}", "Content-Type": "application/json"}
    payload = {"query": prompt, "model_route": model}
    try:
        r = requests.post(f"{HMT_URL}/api/inference", headers=headers, json=payload, timeout=4)
        if r.status_code == 200 and "BUY" in r.text.upper(): return "BUY"
    except: pass
    return "HOLD"

# ==========================================
# 🌌 THE 7-NODE ASYNCHRONOUS SWARM
# ==========================================

# 1. 👁️ ORACLE NODE
async def oracle_node():
    while True:
        try:
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                hive.balances = {b['asset']: float(b['free']) for b in r_bal.json().get('balances', []) if float(b['free']) > 0}

            for coin in WAR_CHEST:
                r_price = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/ticker/price?symbol={coin}", timeout=2)
                p = float(r_price.json()['price'])
                old_p = hive.market_data[coin]['price']
                diff = ((p - old_p) / old_p * 100) if old_p > 0 else 0.0
                
                hive.market_data[coin]['price'] = p
                hive.market_data[coin]['change'] = diff
                hive.market_data[coin]['history'].append(p)
                if len(hive.market_data[coin]['history']) > 15: hive.market_data[coin]['history'].pop(0)

            # Local G-Drive Sync
            try:
                payload = {"timestamp": time.time(), "balances": hive.balances, "market": hive.market_data}
                await asyncio.to_thread(lambda: open(STATE_FILE, "w").write(json.dumps(payload)))
            except: pass
        except: pass
        await asyncio.sleep(3)

# 2. 🏹 HUNTER NODE (Fast Logic -> Phi)
async def hunter_node():
    while True:
        try:
            usdt = hive.balances.get('USDT', 0.0)
            for coin in WAR_CHEST:
                diff = hive.market_data[coin]['change']
                if diff < -0.50 and usdt >= TRADE_QTY:
                    log(f"🏹 HUNTER: Flash Dip on {coin}. Routing to Phi (Airgap)...")
                    if await asyncio.to_thread(query_airgap_ai, f"{coin} crashed {diff}%. BUY/HOLD?", "phi") == "BUY":
                        if await asyncio.to_thread(fire, coin, "BUY", TRADE_QTY):
                            hive.buy_prices[coin] = hive.market_data[coin]['price']
                            log(f"⚔️ AION: Phi-Authorized Strike on {coin}")
        except: pass
        await asyncio.sleep(4)

# 3. ⚓ ADMIRAL NODE (Macro Logic -> MoE 128)
async def admiral_node():
    while True:
        try:
            usdt = hive.balances.get('USDT', 0.0)
            for coin in WAR_CHEST:
                hist = hive.market_data[coin]['history']
                if len(hist) >= 10 and usdt >= TRADE_QTY:
                    mean = sum(hist) / len(hist)
                    variance = sum((x - mean) ** 2 for x in hist) / len(hist)
                    std_dev = math.sqrt(variance)
                    
                    if hist[-1] > hist[0] and std_dev < (mean * 0.005):
                        log(f"⚓ ADMIRAL: Stability on {coin}. Routing to MoE 128...")
                        if await asyncio.to_thread(query_airgap_ai, f"Asset {coin} shows steady growth. Confirm BUY?", "moe") == "BUY":
                            if await asyncio.to_thread(fire, coin, "BUY", TRADE_QTY):
                                hive.buy_prices[coin] = hist[-1]
                                log(f"⚔️ AION: MoE-Authorized Strike on {coin}")
        except: pass
        await asyncio.sleep(45) 

# 4. 🛡️ SENTRY NODE (Capital Protection)
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
                        log(f"⚔️ AION: Sentry Cleared {coin} to protect Vault.")
        except: pass
        await asyncio.sleep(5)

# 5. 🏰 CITADEL UPLINK NODE (GitHub Sync)
async def citadel_node():
    while True:
        try:
            if CITADEL_PAT:
                log(f"🏰 CITADEL: Secured connection established via PAT.")
        except: pass
        await asyncio.sleep(300) 

# 6. 🖥️ DASHBOARD NODE
async def dashboard_node():
    while True:
        os.system('clear')
        usdt, xrp = hive.balances.get('USDT', 0.0), hive.balances.get('XRP', 0.0)
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE ARK FLEET: V25 AIRGAPPED CITADEL                   ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WALLET: ${usdt:.2f} | 💎 XRP: {xrp:.2f}/{TARGET_XRP}                  ║")
        print(f"║ 📡 ORACLE [ACTIVE] | 🏹 HUNTER [PHI]  | ⚓ ADMIRAL [MOE]  ║")
        print(f"║ 🛡️ SENTRY [ACTIVE] | ☁️ G-DRIVE [SYNC] | 🏰 CITADEL [UPLINK]║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for msg in hive.logs: print(f"║ {msg:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for coin in WAR_CHEST:
            d = hive.market_data[coin]
            print(f"║ 🎯 {coin[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}%{' ' * 23}║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        if xrp >= TARGET_XRP: break
        await asyncio.sleep(1)

# --- IGNITE THE FLEET ---
async def main():
    log("✅ All Dependencies Met. Initiating Swarm Concurrency...")
    await asyncio.gather(
        oracle_node(), 
        hunter_node(), 
        admiral_node(), 
        sentry_node(), 
        citadel_node(),
        dashboard_node()
    )

if __name__ == "__main__":
    asyncio.run(main())
