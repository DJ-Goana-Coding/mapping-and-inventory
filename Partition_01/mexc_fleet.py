import hmac, hashlib, time, json, urllib.request, os

with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

def call(path, params=""):
    ts = int(time.time() * 1000)
    query = f"{params}&timestamp={ts}" if params else f"timestamp={ts}"
    sig = hmac.new(env['MEXC_SECRET'].encode(), query.encode(), hashlib.sha256).hexdigest()
    req = urllib.request.Request(f"https://api.mexc.com{path}?{query}&signature={sig}")
    req.add_header("X-MEXC-APIKEY", env['MEXC_KEY'])
    return json.loads(urllib.request.urlopen(req).read().decode())

def get_price(symbol):
    try:
        res = json.loads(urllib.request.urlopen(f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}").read().decode())
        return float(res['price'])
    except: return 0

# The Banking Strategy Coins
bank_coins = ['XRP', 'XLM', 'XDC', 'TIA', 'INJ', 'HBAR', 'DOGE', 'IOTX']
account = call("/api/v3/account")
total_usd = 0

print(f"\n[ 🏛️ THE BANKING FLEET ]")
for b in account['balances']:
    asset = b['asset']
    qty = float(b['free'])
    if qty > 0:
        price = 1.0 if asset == 'USDT' else get_price(f"{asset}USDT")
        value = qty * price
        total_usd += value
        if asset in bank_coins or value > 1:
            print(f"{asset}: {qty:.2f} | Value: ${value:.2f}")

print(f"\nTOTAL FLEET VALUE: ${total_usd:.2f}")
