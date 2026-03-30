import asyncio, requests, time, hmac, hashlib, os, json, re

# --- ⚙️ MASTER KEYS & CONFIG ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

WAR_CHEST = ["BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", "AVAXUSDT", "TIAUSDT", "LINKUSDT"]
SAFE_ASSETS = ["XRP", "HBAR", "XLM", "USDT"]
TRADE_QTY = 12.00 

GDRIVE_PATH = "/data/data/com.termux/files/home/storage/shared/ArkFleet"
os.makedirs(GDRIVE_PATH, exist_ok=True)
LEDGER_FILE = f"{GDRIVE_PATH}/ABN_Trade_Ledger.csv"
STATE_FILE = f"{GDRIVE_PATH}/market_state.json"

class Swarm:
    balances = {"USDT": 0.0}
    market = {c: {"price": 0.0, "change": 0.0, "history": []} for c in WAR_CHEST}
    buy_prices = {}
    strikes = []
    logs = ["🗡️ V35: TOTAL WAR MODE - Kinetic Striking Active."]

swarm = Swarm()

def log(m):
    swarm.logs.append(m)
    if len(swarm.logs) > 6: swarm.logs.pop(0)

def get_sig(p):
    return hmac.new(SECRET_KEY.encode(), p.encode(), hashlib.sha256).hexdigest()

def fire_strike(coin, side, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", 
                         headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
        if r.status_code == 200:
            res = r.json()
            entry_price = swarm.market[coin]['price']
            msg = f"{time.strftime('%H:%M:%S')} | {side} {coin} | @{entry_price}"
            swarm.strikes.append(msg)
            if len(swarm.strikes) > 5: swarm.strikes.pop(0)
            with open(LEDGER_FILE, 'a') as f: f.write(f"{msg}\n")
            return True
        else:
            log(f"⚠️ MEXC REJECT: {r.text[:30]}")
    except: pass
    return False

# --- 👁️ ORACLE: HIGH SPEED SYNC ---
async def oracle_node():
    while True:
        try:
            ts = str(int(time.time() * 1000))
            # Sync Balances
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                for b in r_bal.json().get('balances', []):
                    if b['asset'] == 'USDT': swarm.balances['USDT'] = float(b['free'])
            
            # Sync Prices
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
            
            # G-Drive Uplink
            with open(STATE_FILE, "w") as f: json.dump({"balances": swarm.balances, "market": swarm.market}, f)
        except: pass
        await asyncio.sleep(3)

# --- 🗡️ A.I.O.N: KINETIC STRIKE NODE ---
async def kinetic_node():
    while True:
        try:
            u = swarm.balances['USDT']
            for c in WAR_CHEST:
                if u < TRADE_QTY: break
                
                # PIRANHA KINETICS: No AI permission needed
                diff = swarm.market[c]['change']
                if diff < -0.10: # Aggressive saturday threshold
                    log(f"🗡️ STRIKING: {c} ({diff:.3f}%)")
                    if await asyncio.to_thread(fire_strike, c, "BUY", TRADE_QTY):
                        swarm.buy_prices[c] = swarm.market[c]['price']
                        log(f"✅ STRIKE SUCCESS: {c}")

                # HARVESTER KINETICS
                if c in swarm.buy_prices:
                    pnl = ((swarm.market[c]['price'] - swarm.buy_prices[c]) / swarm.buy_prices[c]) * 100
                    if pnl >= 1.2:
                        log(f"🌾 HARVESTING: {c} (+{pnl:.2f}%)")
                        if await asyncio.to_thread(fire_strike, c, "SELL", TRADE_QTY):
                            del swarm.buy_prices[c]
        except: pass
        await asyncio.sleep(4)

async def dashboard():
    while True:
        os.system('clear')
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE CITADEL V35: TOTAL WAR (KINETIC MODE)             ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WAR CHEST: ${swarm.balances['USDT']:.2f} | 🗡️ MODE: KINETIC            ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ ⚔️  LIVE STRIKE LEDGER (REAL-TIME)                         ║")
        if not swarm.strikes: print(f"║    -- WAITING FOR NEXT KINETIC STRIKE --                  ║")
        for s in swarm.strikes: print(f"║ 🔥 {s:<55} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for l in swarm.logs: print(f"║ {l:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for c in WAR_CHEST[:5]:
            d = swarm.market[c]
            print(f"║ 🎯 {c[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}%{' ' * 23}║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(oracle_node(), kinetic_node(), dashboard())

if __name__ == "__main__": asyncio.run(main())
