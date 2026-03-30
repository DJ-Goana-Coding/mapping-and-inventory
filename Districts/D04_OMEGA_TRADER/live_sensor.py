import urllib.request, json, os

def get_live_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=XRPUSDT"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode())
            price = float(data['price'])
            print(f"\n[+] LIVE OMEGA-SENSOR: XRP is currently at ${price:.4f}")
            return price
    except Exception as e:
        print(f"[!] Sensor Offline: {e}")
        return None

def check_grid(current_price):
    path = os.path.expanduser("~/ARK_CORE/Districts/D03_VORTEX_ENGINE/active_grid.json")
    if not os.path.exists(path):
        print("[!] No active grid found in D03. Run vortex_calc.py first.")
        return

    with open(path, 'r') as f:
        grid = json.load(f)
        
    print(f"\n--- GRID COMPARISON (Base: ${grid['base']}) ---")
    for level in grid['grid_144']:
        diff = abs(current_price - level['price'])
        if diff < 0.005:  # If price is within half a cent of the target
            print(f"*** [!] URGENT: Price is near {level['node']} ({level['action']} @ ${level['price']})! ***")
        else:
            print(f"[{level['node']}] Target: ${level['price']} | Action: {level['action']}")
            
if __name__ == "__main__":
    price = get_live_price()
    if price: check_grid(price)
