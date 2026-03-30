import hmac, hashlib, time, json, urllib.request, os

# 1. Load Keys
with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

def mexc_request(method, path, params=""):
    ts = int(time.time() * 1000)
    query = f"{params}&timestamp={ts}" if params else f"timestamp={ts}"
    sig = hmac.new(env['MEXC_SECRET'].encode(), query.encode(), hashlib.sha256).hexdigest()
    url = f"https://api.mexc.com{path}?{query}&signature={sig}"
    req = urllib.request.Request(url, method=method)
    req.add_header("X-MEXC-APIKEY", env['MEXC_KEY'])
    try:
        with urllib.request.urlopen(req) as res: return json.loads(res.read().decode())
    except Exception as e: return {"error": str(e)}

def market_buy(symbol, usdt_amount):
    """ACTUAL EXECUTION: This sends a REAL order to MEXC"""
    print(f"ATTEMPTING REAL BUY: {symbol} for ${usdt_amount} USDT")
    params = f"symbol={symbol}USDT&side=BUY&type=MARKET&quoteOrderQty={usdt_amount}"
    return mexc_request("POST", "/api/v3/order", params)

def get_balance():
    return mexc_request("GET", "/api/v3/account")

# --- ACTUAL COMMANDS ---
if __name__ == "__main__":
    # Check current ammo before firing
    acc = get_balance()
    print(f"CURRENT BALANCE SYNC: {json.dumps(acc.get('balances', []), indent=2)}")
    
    # UNCOMMENT THE LINE BELOW TO FIRE A REAL $22 BUY ON TIA
    # response = market_buy("TIA", 22)
    # print(f"ORDER RESPONSE: {response}")
