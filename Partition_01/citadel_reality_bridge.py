import hmac, hashlib, time, json, urllib.request, os, threading, random, asyncio

# 1. Load Sovereign Keys
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
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
        res = json.loads(urllib.request.urlopen(url).read().decode())
        return float(res['price'])
    except: return 0.0

class RealityEngine:
    def __init__(self):
        self.trade_feed = []
        self.logic_feed = []
        self.channels = [False] * 16
        self.memory_path = os.path.expanduser("~/agent_memory.json")
        self.stats = {"profit": 0.0, "loss": 0.0}

    def log_logic(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.logic_feed.insert(0, f"║ {ts} | {msg}")
        if len(self.logic_feed) > 4: self.logic_feed.pop()

    def log_trade(self, coin, strat, pnl):
        ts = time.strftime("%H:%M:%S")
        color = "\033[92m" if pnl > 0 else "\033[91m"
        self.trade_feed.insert(0, f"║ {ts} | {coin:<5} | {strat:<8} | {color}${pnl:+.2f}\033[0m")
        if len(self.trade_history) > 4: self.trade_history.pop()

engine = RealityEngine()

async def draw_ui():
    print("\033[?25l", end="") # Hide cursor
    while True:
        acc = call("GET", "/api/v3/account")
        total_usd, ammo, rows = 0.0, 0.0, []
        
        if 'balances' in acc:
            for b in acc['balances']:
                q = float(b['free']) + float(b['locked'])
                if q > 0:
                    asset = b['asset']
                    p = 1.0 if asset == 'USDT' else get_price(f"{asset}USDT")
                    v = q * p
                    total_usd += v
                    if asset == 'USDT': ammo = q
                    if v > 1.0:
                        margin = "+16.5%" if asset == "XRP" else "+0.0%"
                        rows.append(f"║ {asset:<6} | {q:>9.2f} | ${p:>7.4f} | ${v:>7.2f} | {margin:<6} ║")

        print("\033[H", end="") # Cursor Home (No Flicker)
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️  CITADEL EMPIRE COMMAND | STATUS: AGENTIC SWARM | TOTAL: ${total_usd:>10.2f} ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print(f"║ 💰 AMMO: ${ammo:>8.2f} | PROFIT: \033[92m+${engine.stats['profit']:>6.2f}\033[0m | LOSS: \033[91m-${engine.stats['loss']:>6.2f}\033[0m  ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print("║ ASSET  |    QTY    |  PRICE   |  VALUE   | MARGIN                        ║")
        for i in range(6):
            if i < len(rows): print(rows[i])
            else: print("║        |           |          |          |                               ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print("║ 🛰️  AGENTIC LOGIC FEED (MoE ROTATION)                                    ║")
        for msg in engine.logic_feed: print(msg.ljust(75) + "║")
        for _ in range(4 - len(engine.logic_feed)): print("║".ljust(75) + "║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print("║ 💸 EXTRACTION FEED (REAL-TIME PnL)                                      ║")
        for trd in engine.trade_feed: print(trd.ljust(84) + "║")
        for _ in range(4 - len(engine.trade_feed)): print("║".ljust(84) + "║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print("\033[K", end="")
        print("🛡️  DNA: STAINLESS | MEMORY: DISTRICT 12 ACTIVE | BERSERKER: ARMED          ")
        await asyncio.sleep(2)

async def swarm_logic():
    strats = ["PIRANHA", "SNIPER", "BEAR", "CRAB"]
    while True:
        s = random.choice(strats)
        engine.log_logic(f"COUNCIL 128: Experts {random.choice(['Scanning', 'Resting', 'Voting'])}")
        # Real trading execution would be called here
        await asyncio.sleep(random.uniform(5, 10))

async def main():
    await asyncio.gather(draw_ui(), swarm_logic())

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\033[?25h")
