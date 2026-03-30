import hmac, hashlib, time, json, urllib.request, os

with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

def call(method, path, params=""):
    ts = int(time.time() * 1000)
    query = f"{params}&timestamp={ts}" if params else f"timestamp={ts}"
    sig = hmac.new(env['MEXC_SECRET'].encode(), query.encode(), hashlib.sha256).hexdigest()
    req = urllib.request.Request(f"https://api.mexc.com{path}?{query}&signature={sig}", method=method)
    req.add_header("X-MEXC-APIKEY", env['MEXC_KEY'])
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode())
    except Exception as e:
        if hasattr(e, 'read'): print(f"API Error: {e.read().decode()}")
        return None

def get_price(symbol):
    try:
        url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
        res = json.loads(urllib.request.urlopen(url).read().decode())
        return float(res['price'])
    except: return 0.0

# 1. Audit Current Values
print("\n[ 🏛️ INITIATING PRECISION HARVEST ]")
acc = call("GET", "/api/v3/account")
target_total = 50.0
fleet_value = 0.0
skimmable = []

for b in acc['balances']:
    qty = float(b['free'])
    asset = b['asset']
    if qty > 0 and asset != 'USDT':
        price = get_price(f"{asset}USDT")
        val = qty * price
        if val > 5:
            fleet_value += val
            skimmable.append({'asset': asset, 'val': val, 'qty': qty, 'price': price})

# 2. Execute Proportional Slices with Truncation
for coin in skimmable:
    weight = coin['val'] / fleet_value
    slice_usd = target_total * weight
    slice_qty = slice_usd / coin['price']
    
    # PRECISION SHIELD: Truncate to 2 decimal places (Standard for Alts)
    final_qty = float(int(slice_qty * 100) / 100.0)
    
    if final_qty > 0:
        symbol = f"{coin['asset']}USDT"
        print(f"Skimming {final_qty} {coin['asset']} (~${final_qty * coin['price']:.2f})")
        call("POST", "/api/v3/order", f"symbol={symbol}&side=SELL&type=MARKET&quantity={final_qty}")

print("\n[ ✅ HARVEST COMPLETE: AMMO READY ]")
