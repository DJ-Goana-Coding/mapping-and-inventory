import asyncio, requests, time, hmac, hashlib, os, json, re, random

# --- ⚙️ MASTER KEYS & CONFIG ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "TIAUSDT", "LINKUSDT", "XLMUSDT"]
SAFE_ASSETS = ["XRP", "HBAR", "XLM", "USDT"]
TRADE_QTY = 12.00 

GDRIVE_PATH = "./Research/S10"
os.makedirs(GDRIVE_PATH, exist_ok=True)
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"

class SovereignSwarm:
    balances = {"USDT": 0.0}
    market = {c: {"price": 0.0, "change": 0.0, "history": []} for c in WAR_CHEST}
    inventory = {c: 0 for c in WAR_CHEST}
    strikes = []
    logs = ["🗡️ V39 Singularity: All Systems Firing."]
    worth_start = 0.0
    worth_now = 0.0
    # Garage Metrics Simulation (Bridged from Rack Node)
    rack_latency = "24ms"
    garage_load = "12%"

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
            p = swarm.market[coin]['price']
            icon = "🔥 BUY" if side == "BUY" else "💰 SOLD"
            msg = f"{time.strftime('%H:%M:%S')} | {icon} {coin} | @{p}"
            swarm.strikes.append(msg)
            if len(swarm.strikes) > 5: swarm.strikes.pop(0)
            with open(LEDGER_FILE, 'a') as f: f.write(f"{msg}\n")
            return True
    except: pass
    return False

# --- 👁️ NODE 1: ORACLE & RACK TELEMETRY ---
async def oracle_node():
    while True:
        try:
            # Sync Account & Floating Worth
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                current_total = 0.0
                for b in r_bal.json().get('balances', []):
                    asset, qty = b['asset'], float(b['free'])
                    if asset == "USDT": 
                        swarm.balances['USDT'] = qty
                        current_total += qty
                    elif f"{asset}USDT" in swarm.market:
                        p = swarm.market[f"{asset}USDT"]['price']
                        swarm.inventory[f"{asset}USDT"] = 1 if qty * p > 2.0 else 0
                        current_total += (qty * p)
                if swarm.worth_start == 0: swarm.worth_start = current_total
                swarm.worth_now = current_total

            # Sync Market
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
                        if len(swarm.market[c]['history']) > 15: swarm.market[c]['history'].pop(0)
            
            # Rack Heartbeat Simulation
            swarm.rack_latency = f"{random.randint(18, 45)}ms"
            swarm.garage_load = f"{random.randint(8, 22)}%"
        except: pass
        await asyncio.sleep(3)

# --- 🗡️ NODE 2: KINETIC AION ENGINE ---
async def kinetic_node():
    while True:
        try:
            u = swarm.balances['USDT']
            for c in WAR_CHEST:
                # PIRANHA KINETICS: Dynamic Bite at -0.10%
                diff = swarm.market[c]['change']
                if diff < -0.10 and u >= TRADE_QTY and swarm.inventory[c] == 0:
                    log(f"🗡️ KINETIC STRIKE: {c} ({diff:.2f}%)")
                    if await asyncio.to_thread(fire_strike, c, "BUY", TRADE_QTY):
                        log(f"✅ BOUGHT {c}")

                # HARVESTER KINETICS: Bank at +1.2%
                if swarm.inventory[c] > 0 and c not in SAFE_ASSETS:
                    if diff > 1.2:
                        log(f"🌾 HARVESTING: {c} (+{diff:.2f}%)")
                        if await asyncio.to_thread(fire_strike, c, "SELL", 9999, False):
                            log(f"✅ SOLD {c}")
        except: pass
        await asyncio.sleep(4)

async def dashboard():
    while True:
        os.system('clear')
        pnl = swarm.worth_now - swarm.worth_start
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE CITADEL V39: KINETIC SINGULARITY                  ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WAR CHEST: ${swarm.balances['USDT']:.2f} | 📈 SESSION PnL: ${pnl:+.2f}          ║")
        print(f"║ 🏠 GARAGE LOAD: {swarm.garage_load:<6} | ⛓️ RACK LATENCY: {swarm.rack_latency:<6}  ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ ⚔️  LIVE STRIKE LEDGER (1TB RACK LINKED)                   ║")
        if not swarm.strikes: print(f"║    -- MONITORING SOVEREIGN ASSETS --                      ║")
        for s in swarm.strikes: print(f"║ 🔥 {s:<55} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for l in swarm.logs: print(f"║ {l:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for c in ["XRPUSDT", "TIAUSDT", "ADAUSDT", "LINKUSDT", "XLMUSDT"]:
            d = swarm.market[c]
            print(f"║ 🎯 {c[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}% | INV: {swarm.inventory[c]} ║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        await asyncio.sleep(1)

async def main():
    # Persistent Ledger Read
    if os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, 'r') as f:
            swarm.strikes = [l.strip() for l in f.readlines()[-5:]]
    await asyncio.gather(oracle_node(), kinetic_node(), dashboard())

if __name__ == "__main__": asyncio.run(main())
