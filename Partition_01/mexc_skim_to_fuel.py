import hmac, hashlib, time, json, urllib.request, os

# 1. Load Keys
with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

def trade(symbol, side, qty):
    ts = int(time.time() * 1000)
    query = f"symbol={symbol}&side={side}&type=MARKET&quantity={qty}&timestamp={ts}"
    sig = hmac.new(env['MEXC_SECRET'].encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"https://api.mexc.com/api/v3/order?{query}&signature={sig}"
    req = urllib.request.Request(url, method='POST')
    req.add_header("X-MEXC-APIKEY", env['MEXC_KEY'])
    return json.loads(urllib.request.urlopen(req).read().decode())

# 2. Skim 36 XRP into USDT Fuel
try:
    print("\n[🏛️ SKIMMER ACTIVATED]")
    print("Executing Market Sell: 36 XRP...")
    order = trade("XRPUSDT", "SELL", 36)
    if 'orderId' in order:
        print(f"SUCCESS: $50.00 SEED GENERATED. OrderID: {order['orderId']}")
    else:
        print(f"SKIM FAILED: {order}")
except Exception as e:
    print(f"ERROR: {e}")
