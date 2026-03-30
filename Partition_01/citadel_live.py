import hmac, hashlib, time, json, urllib.request, os, asyncio

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
    except: return {"error": "API_FAIL"}

def get_live_price(symbol):
    if symbol == "USDT": return 1.0
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}USDT"
        with urllib.request.urlopen(url) as res:
            data = json.loads(res.read().decode())
            return float(data.get('price', 0))
    except: return 0.0

async def draw_ui():
    print("\033[?25l", end="") # Hide cursor
    while True:
        acc = mexc_call("GET", "/api/v3/account")
        total, rows = 0.0, []
        
        if 'balances' in acc:
            # Sort balances by value
            for b in acc['balances']:
                q = float(b['free']) + float(b['locked'])
                if q > 0.0001:
                    asset = b['asset']
                    price = get_live_price(asset)
                    val = q * price
                    if val > 0.50: # Only show assets worth more than 50 cents
                        total += val
                        rows.append(f"║ {asset:<4} │ {q:>8.2f} │ ${val:>7.1f} ║")

        print("\033[H\033[J", end="") # Clear and Home
        print("╔═══════════════════════════════╗")
        print(f"║ 🎖️ CITADEL LIVE │ TOTAL: ${total:>7.2f} ║")
        print("╠═══════════════════════════════╣")
        print("║ ASSET │ QUANTITY │ VALUE      ║")
        for r in sorted(rows, key=lambda x: float(x.split('$')[1].split(' ')[0]), reverse=True):
            print(r)
        print("╠═══════════════════════════════╣")
        print("║ [!] BRIDGE: STAINLESS         ║")
        print("║ [!] READY FOR $22.00 TRADE    ║")
        print("╚═══════════════════════════════╝")
        await asyncio.sleep(2)

if __name__ == "__main__":
    try: asyncio.run(draw_ui())
    except KeyboardInterrupt: print("\033[?25h")
