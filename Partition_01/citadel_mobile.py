import hmac, hashlib, time, json, urllib.request, os, asyncio

# 1. AUTH LOAD
with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

def mexc_call(method, path, params=""):
    ts = int(time.time() * 1000)
    query = f"{params}&timestamp={ts}" if params else f"timestamp={ts}"
    sig = hmac.new(env['MEXC_SECRET'].encode(), query.encode(), hashlib.sha256).hexdigest()
    req = urllib.request.Request(f"https://api.mexc.com{path}?{query}&signature={sig}", method=method)
    req.add_header("X-MEXC-APIKEY", env['MEXC_KEY'])
    try:
        with urllib.request.urlopen(req) as res: return json.loads(res.read().decode())
    except: return {}

async def call_local_brain(model, prompt):
    """TALKS TO YOUR SPECIFIC LOCAL MODELS"""
    data = {"model": model, "prompt": prompt, "stream": False}
    try:
        req = urllib.request.Request("http://localhost:11434/api/generate", data=json.dumps(data).encode(), method="POST")
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())['response']
    except: return "BRAIN_OFFLINE"

class CitadelHive:
    def __init__(self):
        self.logs = []
    def log(self, msg):
        self.logs.insert(0, f"{time.strftime('%H:%M:%S')} {msg}")
        if len(self.logs) > 8: self.logs.pop()

hive = CitadelHive()

async def stack_monitor():
    # YOUR ACTUAL STACKS
    targets = ["PHI", "QUANTS", "QWE", "TIA", "XRP"]
    last_prices = {}
    while True:
        for coin in targets:
            try:
                p_res = json.loads(urllib.request.urlopen(f"https://api.mexc.com/api/v3/ticker/price?symbol={coin}USDT").read().decode())
                price = float(p_res['price'])
                if coin in last_prices:
                    change = ((price - last_prices[coin]) / last_prices[coin]) * 100
                    if abs(change) >= 0.25:
                        # CALL THE ORACLE (DeepSeek-R1:8b)
                        decision = await call_local_brain("deepseek-r1:8b", f"{coin} moved {change:.2f}%. Strategy: 4-Stack Hive. BUY or WAIT?")
                        hive.log(f"🧠 {coin}: {decision[:25]}...")
                        
                        # EXECUTION (ARMED)
                        side = "BUY" if "BUY" in decision.upper() else "SELL" if "SELL" in decision.upper() else None
                        if side:
                            mexc_call("POST", "/api/v3/order", f"symbol={coin}USDT&side={side}&type=MARKET&quoteOrderQty=22")
                            hive.log(f"🔥 EXEC: {side} {coin} @ {price}")
                last_prices[coin] = price
            except: continue
        await asyncio.sleep(2)

async def draw_ui():
    while True:
        acc = mexc_call("GET", "/api/v3/account")
        usdt = next((float(b['free']) for b in acc.get('balances', []) if b['asset'] == 'USDT'), 0.0)
        print("\033[H\033[J", end="")
        print(f"╔═══════════════════════════════╗\n║ CITADEL HIVE │ AMMO: ${usdt:>8.2f} ║\n╠═══════════════════════════════╣")
        for l in hive.logs: print(f"║ {l.ljust(29)} ║")
        if not hive.logs: print(f"║ SCANNING PHI/QUANTS/QWE...    ║")
        print("╚═══════════════════════════════╝")
        await asyncio.sleep(2)

async def main():
    await asyncio.gather(stack_monitor(), draw_ui())

if __name__ == "__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: pass
