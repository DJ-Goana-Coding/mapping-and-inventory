import asyncio, requests, time, hmac, hashlib, os, json, re, math

# --- ⚙️ CITADEL CONFIGURATION ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "TIAUSDT", "LINKUSDT", "HBARUSDT", "XLMUSDT"]
SAFE_ASSETS = ["XRP", "HBAR", "XLM", "USDT"]
TRADE_QTY = 12.00 

GDRIVE_PATH = "/data/data/com.termux/files/home/storage/shared/ArkFleet"
os.makedirs(GDRIVE_PATH, exist_ok=True)
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"
MEMORY_FILE = f"{GDRIVE_PATH}/swarm_memory.json"

class SovereignSwarm:
    def __init__(self):
        self.balances = {"USDT": 0.0}
        self.market = {c: {"price": 0.0, "change": 0.0, "history": []} for c in WAR_CHEST}
        self.inventory = {c: 0 for c in WAR_CHEST}
        self.buy_prices = {c: [] for c in WAR_CHEST}
        self.strikes = []
        self.logs = ["⛓️ Bridging 1TB Racks...", "🏠 Garage Node Linked.", "🗡️ V38: Sovereign Unification."]
        self.start_worth = 0.0
        self.current_worth = 0.0
        self.ai_status = "INITIALIZING"

swarm = SovereignSwarm()

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
            icon = "🔥 BUY" if side == "BUY" else "💰 SOLD"
            msg = f"{time.strftime('%H:%M:%S')} | {icon} {coin} | @{price}"
            swarm.strikes.append(msg)
            if len(swarm.strikes) > 6: swarm.strikes.pop(0)
            with open(LEDGER_FILE, 'a') as f: f.write(f"{msg}\n")
            return True
    except: pass
    return False

def t_i_a_consult(prompt, mode="phi"):
    """TIA Logic: Multi-Brain Routing (Airgap HF Space)"""
    headers = {"Authorization": f"Bearer {HMT_ACCESS}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{HMT_URL}/api/inference", headers=headers, 
                         json={"query": prompt, "model_route": mode}, timeout=2.0)
        clean = re.sub('<[^<]+?>', '', r.text).upper()
        swarm.ai_status = f"{mode.upper()}: {clean[:10]}"
        return "BUY" if "BUY" in clean else "HOLD"
    except:
        swarm.ai_status = "KINETIC_OVERRIDE"
        return "BUY" # Fallback to Kinetic Strike

# --- 👁️ ORACLE: AGGREGATE SENSOR ---
async def oracle_node():
    while True:
        try:
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
                        if len(swarm.market[c]['history']) > 25: swarm.market[c]['history'].pop(0)
            
            # Worth Sync
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                current_total = 0.0
                for b in r_bal.json().get('balances', []):
                    asset = b['asset']
                    qty = float(b['free'])
                    if asset == "USDT": 
                        swarm.balances['USDT'] = qty
                        current_total += qty
                    elif f"{asset}USDT" in swarm.market:
                        p = swarm.market[f"{asset}USDT"]['price']
                        current_total += (qty * p)
                if swarm.start_total_value == 0: swarm.start_total_value = current_total
                swarm.current_worth = current_total
        except: pass
        await asyncio.sleep(3)

# --- 🗡️ A.I.O.N: THE STRIKE ENGINE ---
async def aion_kinetic_node():
    while True:
        try:
            u = swarm.balances['USDT']
            for c in WAR_CHEST:
                # 🐟 PIRANHA: Dynamic Bite
                h = swarm.market[c]['history']
                if len(h) < 5: continue
                avg_v = sum(abs((h[i]-h[i-1])/h[i-1]*100) for i in range(1, len(h)))/len(h)
                trigger = max(-0.09, -(avg_v * 2.8))
                diff = swarm.market[c]['change']

                if diff < trigger and u >= TRADE_QTY and swarm.inventory[c] < 2:
                    log(f"🗡️ KINETIC: {c} ({diff:.2f}%)")
                    if t_i_a_consult(f"Strike {c} at {diff}%?", "phi") == "BUY":
                        if await asyncio.to_thread(fire_strike, c, "BUY", TRADE_QTY):
                            swarm.inventory[c] += 1
                            swarm.buy_prices[c].append(swarm.market[c]['price'])

                # 🌾 HARVESTER: Profit Lock
                if swarm.inventory[c] > 0:
                    for entry in list(swarm.buy_prices[c]):
                        if entry == 0: continue
                        pnl = ((swarm.market[c]['price'] - entry) / entry) * 100
                        if pnl >= 1.25 or pnl <= -2.50:
                            log(f"🌾 HARVEST: {c} ({pnl:+.2f}%)")
                            if await asyncio.to_thread(fire_strike, c, "SELL", 9999, False):
                                swarm.inventory[c] -= 1
                                swarm.buy_prices[c].remove(entry)
        except: pass
        await asyncio.sleep(4)

async def dashboard():
    while True:
        os.system('clear')
        u, pnl = swarm.balances['USDT'], (swarm.current_worth - swarm.start_total_value)
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE CITADEL V38: SOVEREIGN UNIFICATION (1TB-G)        ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WAR CHEST: ${u:<8.2f} | 📈 SESSION PnL: ${pnl:+.2f}          ║")
        print(f"║ 🧠 BRAIN: {swarm.ai_status:<16} | 🛡️ STATUS: KINETIC           ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ ⚔️  STRIKE LEDGER (PERSISTENT HISTORY)                     ║")
        if not swarm.strikes: print(f"║    -- AWAITING NEXT KINETIC TRIGGER --                    ║")
        for s in swarm.strikes: print(f"║ 🔥 {s:<55} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for l in swarm.logs: print(f"║ {l:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for c in ["XRPUSDT", "TIAUSDT", "LINKUSDT", "ADAUSDT", "SOLUSDT"]:
            d = swarm.market[c]
            print(f"║ 🎯 {c[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}% | INV: {swarm.inventory[c]} ║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        await asyncio.sleep(1)

async def main():
    # Sync Existing Inventory on Startup
    log("🔄 Scanning MEXC for Ghost Inventory...")
    ts = str(int(time.time() * 1000))
    r = requests.get(f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY})
    if r.status_code == 200:
        for b in r.json().get('balances', []):
            asset = b['asset']
            qty = float(b['free'])
            symbol = f"{asset}USDT"
            if symbol in WAR_CHEST and qty * 1.4 > 2.0:
                swarm.inventory[symbol] = 1
                swarm.buy_prices[symbol] = [0.0]
    
    # Load Ledger History
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r') as f:
            lines = f.readlines()
            swarm.strikes = [l.strip() for l in lines[-6:]]

    await asyncio.gather(oracle_node(), aion_kinetic_node(), dashboard())

if __name__ == "__main__":
    swarm.start_total_value = 0 # Will be set by oracle
    asyncio.run(main())
