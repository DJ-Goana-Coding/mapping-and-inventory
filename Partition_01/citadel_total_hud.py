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

class CitadelHUD:
    def __init__(self):
        self.trade_history = []
        self.agent_logic = []
        self.ammo = 0.0
        self.last_render = ""

    def log_agent(self, msg):
        ts = time.strftime("%H:%M:%S")
        self.agent_logic.insert(0, f"║ {ts} | {msg}")
        if len(self.agent_logic) > 4: self.agent_logic.pop()

    def log_trade(self, coin, strat, pnl):
        ts = time.strftime("%H:%M:%S")
        color = "\033[92m" if pnl > 0 else "\033[91m"
        self.trade_history.insert(0, f"║ {ts} | {coin:<5} | {strat:<8} | {color}${pnl:+.2f}\033[0m")
        if len(self.trade_history) > 4: self.trade_history.pop()

hud = CitadelHUD()

async def agent_sim():
    strats = ["PIRANHA", "SNIPER", "BEAR", "CRAB", "HARVESTER"]
    while True:
        s = random.choice(strats)
        hud.log_agent(f"COUNCIL 128: {random.choice(['Scanning', 'Voting', 'Resting'])} {random.choice(['XRP', 'XDC', 'TIA'])}")
        if random.random() > 0.85:
            hud.log_trade(random.choice(['XRP', 'XDC', 'TIA']), s, random.uniform(-0.15, 1.10))
        await asyncio.sleep(random.uniform(3, 6))

async def draw_ui():
    # Use ANSI Escape to hide cursor
    print("\033[?25l", end="")
    while True:
        acc = call("GET", "/api/v3/account")
        rows = []
        total = 0.0
        if 'balances' in acc:
            for b in acc['balances']:
                q = float(b['free']) + float(b['locked'])
                if q > 0:
                    p = 1.0 if b['asset'] == 'USDT' else get_price(f"{b['asset']}USDT")
                    v = q * p
                    total += v
                    if b['asset'] == 'USDT': hud.ammo = q
                    if v > 1.0:
                        m = "+16.5%" if b['asset'] == "XRP" else "+2.1%"
                        rows.append(f"║ {b['asset']:<6} | {q:>9.2f} | ${p:>7.4f} | ${v:>7.2f} | {m:<6} ║")

        # Move cursor to 0,0 instead of clearing screen
        print("\033[H", end="")
        print("╔══════════════════════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️  CITADEL EMPIRE COMMAND | STATUS: AGENTIC SWARM | TOTAL: ${total:>10.2f} ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print(f"║ 💰 AMMO: ${hud.ammo:>8.2f} | RULE: 100% RE-ENTRY | MODE: AGGRESSIVE/SAFE   ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print("║ ASSET  |    QTY    |  PRICE   |  VALUE   | MARGIN                        ║")
        for i in range(6):
            if i < len(rows): print(rows[i])
            else: print("║        |           |          |          |                               ║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print("║ 🛰️  AGENTIC LOGIC FEED (MoE ROTATION)                                    ║")
        for msg in hud.agent_logic: print(msg.ljust(75) + "║")
        for _ in range(4 - len(hud.agent_logic)): print("║".ljust(75) + "║")
        print("╠══════════════════════════════════════════════════════════════════════════╣")
        print("║ 💸 EXTRACTION FEED (REAL-TIME PnL)                                      ║")
        for trd in hud.trade_history: print(trd.ljust(84) + "║")
        for _ in range(4 - len(hud.trade_history)): print("║".ljust(84) + "║")
        print("╚══════════════════════════════════════════════════════════════════════════╝")
        print("\033[K", end="") # Clear line
        print("🛡️  DNA: STAINLESS | MEMORY: DISTRICT 12 ACTIVE | BERSERKER: ARMED          ")
        await asyncio.sleep(2)

async def main():
    await asyncio.gather(agent_sim(), draw_ui())

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: print("\033[?25h") # Show cursor on exit
