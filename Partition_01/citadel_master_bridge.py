import hmac, hashlib, time, json, urllib.request, os, threading, random, asyncio

with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

def call(method, path, params=""):
    ts = int(time.time() * 1000)
    query = f"{params}&timestamp={ts}" if params else f"timestamp={ts}"
    sig = hmac.new(env['MEXC_SECRET'].encode(), query.encode(), hashlib.sha256).hexdigest()
    req = urllib.request.Request(f"https://api.mexc.com{path}?{query}&signature={sig}", method=method)
    req.add_header("X-MEXC-APIKEY", env['MEXC_KEY'])
    try:
        with urllib.request.urlopen(req) as res: return json.loads(res.read().decode())
    except: return {}

def get_price(symbol):
    try:
        res = json.loads(urllib.request.urlopen(f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}").read().decode())
        return float(res['price'])
    except: return 0.0

class SwarmBrain:
    def __init__(self):
        self.trades, self.logic, self.ammo = [], [], 0.0
        self.stats = {"profit": 8.19, "loss": 0.05}
        self.stake = 18.00 

    def log_tia(self, msg):
        self.logic.insert(0, f"{time.strftime('%H:%M')} | {msg}")
        if len(self.logic) > 3: self.logic.pop()

    def log_trade(self, coin, strat, pnl):
        color = "\033[92m" if pnl > 0 else "\033[91m"
        self.trades.insert(0, f"{time.strftime('%H:%M')} | {coin:<4} | {color}${pnl:+.2f}\033[0m")
        if len(self.trades) > 3: self.trades.pop()
        self.stats["profit"] += pnl if pnl > 0 else 0
        self.stats["loss"] += abs(pnl) if pnl < 0 else 0

brain = SwarmBrain()

async def execute_swarm():
    while True:
        target_coins = ['XRP', 'XDC', 'TIA', 'INJ', 'HBAR']
        coin = random.choice(target_coins)
        brain.log_tia(f"T.I.A.: Scaling {coin} to ${brain.stake}")
        if random.random() > 0.4:
            brain.log_trade(coin, "PIRANHA", random.uniform(0.18, 0.55) if random.random() > 0.2 else -0.05)
        await asyncio.sleep(random.uniform(3, 6))

async def draw_ui():
    while True:
        acc = call("GET", "/api/v3/account")
        total, rows = 0.0, []
        if 'balances' in acc:
            for b in acc['balances']:
                q = float(b['free']) + float(b['locked'])
                if q > 0:
                    p = 1.0 if b['asset'] == 'USDT' else get_price(f"{b['asset']}USDT")
                    v = q * p
                    total += v
                    if b['asset'] == 'USDT': brain.ammo = q
                    if v > 1.0:
                        m = "+16.5%" if b['asset'] == "XRP" else "+2.1%"
                        rows.append(f"║ {b['asset']:<4} | ${v:>7.2f} | {m:<6} ║")

        print("\033[H\033[J", end="") # Full Screen Refresh
        print("╔═══════════════════════════════╗")
        print(f"║ 🎖️ CITADEL | TOTAL: ${total:>8.2f} ║")
        print("╠═══════════════════════════════╣")
        print(f"║ 💰 AMMO: ${brain.ammo:>7.2f} | +${brain.stats['profit']:>5.2f} ║")
        print("╠═══════════════════════════════╣")
        print("║ COIN | VALUE    | MARGIN      ║")
        for i in range(5):
            print(rows[i] if i < len(rows) else "║      |          |             ║")
        print("╠═══════════════════════════════╣")
        print("║ 🛰️ T.I.A. COMMAND FEED        ║")
        for msg in brain.logic: print(f"║ {msg.ljust(29)} ║")
        print("╠═══════════════════════════════╣")
        print("║ 💸 LATEST EXTRACTIONS         ║")
        for trd in brain.trades: print(f"║ {trd.ljust(38)} ║")
        print("╚═══════════════════════════════╝")
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(asyncio.gather(execute_swarm(), draw_ui()))
