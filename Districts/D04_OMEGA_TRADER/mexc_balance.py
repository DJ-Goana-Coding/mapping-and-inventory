import urllib.request, json, time, hmac, hashlib, os

def get_keys():
    path = os.path.expanduser("~/ARK_CORE/Districts/D02_TIA_VAULT/mexc_keys.json")
    if not os.path.exists(path): return None, None
    with open(path, 'r') as f:
        data = json.load(f)
        return data.get("api_key"), data.get("secret_key")

def check_balance():
    api_key, secret_key = get_keys()
    if not api_key:
        return print("[!] Vault locked or empty. Run vault_init.py first.")
        
    print("\n[+] OMEGA-TRADER: Pinging MEXC Vault via Secure API...")
    
    base_url = "https://api.mexc.com"
    endpoint = "/api/v3/account"
    timestamp = str(int(time.time() * 1000))
    query_string = f"recvWindow=5000&timestamp={timestamp}"
    
    # Forge the cryptographic signature MEXC requires
    signature = hmac.new(secret_key.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    url = f"{base_url}{endpoint}?{query_string}&signature={signature}"
    
    req = urllib.request.Request(url, headers={'X-MEXC-APIKEY': api_key, 'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            balances = data.get('balances', [])
            
            print("--- 💰 LIVE WALLET BALANCES ---")
            found = False
            for b in balances:
                asset = b['asset']
                free = float(b['free'])
                if free > 0 and asset in ['USDT', 'XRP']:
                    print(f"[{asset}] Available: {free:.4f}")
                    found = True
            if not found:
                print("[!] No free USDT or XRP found in this wallet.")
            print("-------------------------------\n")
            
    except urllib.error.HTTPError as e:
        print(f"[!] MEXC API Error: Code {e.code}")
        print(f"[!] Details: {e.read().decode()}")
    except Exception as e:
        print(f"[!] Network Error: {e}")

if __name__ == "__main__":
    check_balance()
