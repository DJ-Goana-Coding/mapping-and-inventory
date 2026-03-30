import hmac, hashlib, time, requests, os

# Load keys from your auth file
key = os.popen('source ~/.mexc_auth && echo $MEXC_KEY').read().strip()
secret = os.popen('source ~/.mexc_auth && echo $MEXC_SECRET').read().strip()

timestamp = int(time.time() * 1000)
query = f"timestamp={timestamp}"
signature = hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

url = f"https://api.mexc.com/api/v3/account?{query}&signature={signature}"
headers = {"X-MEXC-APIKEY": key}

try:
    r = requests.get(url, headers=headers)
    print(r.text)
except:
    print("Bridge connection failed. Check keys.")
