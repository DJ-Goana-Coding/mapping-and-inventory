import hmac, hashlib, time, json, urllib.request, os

# 1. Load Keys
with open(os.path.expanduser('~/.mexc_auth'), 'r') as f:
    env = {l.split('=')[0].split(' ')[-1]: l.split('=')[1].strip().replace('"', '') for l in f if '=' in l}

KEY = env['MEXC_KEY']
SECRET = env['MEXC_SECRET']

# 2. Build Request
timestamp = int(time.time() * 1000)
query = f"timestamp={timestamp}"
signature = hmac.new(SECRET.encode(), query.encode(), hashlib.sha256).hexdigest()
url = f"https://api.mexc.com/api/v3/account?{query}&signature={signature}"

# 3. Execute
req = urllib.request.Request(url)
req.add_header("X-MEXC-APIKEY", KEY)

try:
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
        usdt = 0
        for b in data.get('balances', []):
            if b['asset'] == 'USDT':
                usdt = float(b['free'])
        print(f"\n[STAINLESS BRIDGE ACTIVE]")
        print(f"LIVE USDT BALANCE: ${usdt:.2f}")
except Exception as e:
    print(f"Connection Failed: {e}")
