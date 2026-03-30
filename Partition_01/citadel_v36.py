import asyncio, requests, time, hmac, hashlib, os, json, re, math

# --- ⚙️ MASTER CONFIG ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "TIAUSDT", "LINKUSDT", "HBARUSDT", "XLMUSDT"]
SAFE_ASSETS = ["XRP", "HBAR", "XLM", "USDT"]
TRADE_QTY = 12.00 
MAX_INVENTORY_PER_COIN = 3 # Avellaneda-Stoikov limit: Don't hold more than 3 units of one coin

GDRIVE_PATH = "/data/data/com.termux/files/home/storage/shared/ArkFleet"
os.makedirs(GDRIVE_PATH, exist_ok=True)
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"
STATE_FILE = f"{GDRIVE_PATH}/market_state.json"

class Swarm:
    balances = {"USDT": 0.0}
    market = {c: {"price": 0.0, "change": 0.0, "history": []} for c in WAR_CHEST}
    inventory = {c: 0 for c in WAR_CHEST} # Tracks current active trades
    buy_prices = {c: [] for c in WAR_CHEST}
    strikes = []
    logs = ["🗡️ V36: ETERNAL SWARM - Self-Healing Enabled."]

swarm = Swarm()

def log(m):
    swarm.logs.append(m)
    if len(swarm.logs) > 6: swarm.logs.pop(0)

def get_sig(p):
    return hmac.new(SECRET_KEY.encode(), p.encode(), hashlib.sha256).hexdigest()

def fire_strike(coin, side, qty, is_quote=True):
    ts = str(int(time.time() * 1000))
    q_type = "quoteOrderQty" if is_quote else "quantity"
    params = f"symbol={coin}&side={side}&type=MARKET&{q_type}={qty}&timestamp={ts}"
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", 
                         headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
        if r.status_code == 200:
            price = swarm.market[coin]['price']
            msg = f"{time.strftime('%H:%M:%S')} | {side} {coin} | @{price}"
            swarm.strikes.append(msg)
            if len(swarm.strikes) > 5: swarm.strikes.pop(0)
            with open(LEDGER_FILE, 'a') as f: f.write(f"{msg}\n")
            return True
    except: pass
    return False

# --- 👁️ NODE 1: ORACLE (DATA SYNC) ---
async def oracle_node():
    while True:
        try:
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                for b in r_bal.json().get('balances', []):
                    if b['asset'] == 'USDT': swarm.balances['USDT'] = float(b['free'])
            
            r_all = await asyncio.to_thread(requests.get, "https://api.mexc.com/api/v3/ticker/price", timeout=3)
            if r_all.status_code == 200:
                p_map = {i['symbol']: float(i['price']) for i in r_all.json()}
                for c in WAR_CHEST:
                    p = p_map.get(c, 0.0)
                    if p > 0:
                        old = swarm.market[c]['price']
                        swarm.market[c]['price'] = p
                        swarm.market[c]['change'] = ((p-old)/old*100) if old>0 else 0.0
                        swarm.market[c]['history'].append(p)
                        if len(swarm.market[c]['history']) > 20: swarm.market[c]['history'].pop(0)
            
            with open(STATE_FILE, "w") as f: json.dump({"market": swarm.market, "wallet": swarm.balances}, f)
        except Exception as e:
            log(f"🛠️ Oracle Healing: {str(e)[:20]}")
        await asyncio.sleep(3)

# --- 🗡️ NODE 2: KINETIC EXECUTION ---
async def kinetic_node():
    while True:
        try:
            u = swarm.balances['USDT']
            for c in WAR_CHEST:
                if u < TRADE_QTY: break
                
                # INVENTORY MANAGEMENT (Avellaneda-Stoikov Logic)
                if swarm.inventory[c] >= MAX_INVENTORY_PER_COIN: continue
                
                # PIRANHA BITE (Adaptive Trigger)
                h = swarm.market[c]['history']
                if len(h) < 5: continue
                avg_vol = sum(abs((h[i]-h[i-1])/h[i-1]*100) for i in range(1, len(h)))/len(h)
                trigger = max(-0.11, -(avg_vol * 2.5))
                diff = swarm.market[c]['change']

                if diff < trigger:
                    log(f"🗡️ STRIKE: {c} ({diff:.2f}%)")
                    if await asyncio.to_thread(fire_strike, c, "BUY", TRADE_QTY):
                        swarm.inventory[c] += 1
                        swarm.buy_prices[c].append(swarm.market[c]['price'])
                        log(f"✅ BOUGHT: {c} (Inv: {swarm.inventory[c]})")

                # HARVESTER SWEEP (Profit Exit)
                if swarm.inventory[c] > 0:
                    for entry in list(swarm.buy_prices[c]):
                        pnl = ((swarm.market[c]['price'] - entry) / entry) * 100
                        if pnl >= 1.3:
                            log(f"🌾 HARVEST: {c} (+{pnl:.2f}%)")
                            if await asyncio.to_thread(fire_strike, c, "SELL", TRADE_QTY):
                                swarm.inventory[c] -= 1
                                swarm.buy_prices[c].remove(entry)
                        elif pnl <= -2.5 and c not in SAFE_ASSETS:
                            log(f"🛡️ SENTRY: {c} Exit (-2.5%)")
                            if await asyncio.to_thread(fire_strike, c, "SELL", TRADE_QTY):
                                swarm.inventory[c] -= 1
                                swarm.buy_prices[c].remove(entry)
        except Exception as e:
            log(f"🛠️ Kinetic Healing: {str(e)[:20]}")
        await asyncio.sleep(4)

# --- 🖥️ NODE 3: COCKPIT UI ---
async def dashboard():
    while True:
        os.system('clear')
        u = swarm.balances.get('USDT', 0.0)
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE CITADEL V36: ETERNAL SWARM (MASTER)               ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WAR CHEST: ${u:<8.2f} | 🛡️ STATUS: SELF-HEALING         ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ ⚔️  LIVE STRIKE LEDGER                                     ║")
        if not swarm.strikes: print(f"║    -- MONITORING TOP 12 WAR CHEST --                      ║")
        for s in swarm.strikes: print(f"║ 🔥 {s:<55} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for l in swarm.logs: print(f"║ {l:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        # Displaying Inventory Load
        for c in ["XRPUSDT", "SOLUSDT", "BTCUSDT", "ETHUSDT", "LINKUSDT", "TIAUSDT"]:
            d = swarm.market[c]
            inv = swarm.inventory[c]
            print(f"║ 🎯 {c[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}% | INV: {inv} ║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(oracle_node(), kinetic_node(), dashboard())

if __name__ == "__main__":
    asyncio.run(main())
