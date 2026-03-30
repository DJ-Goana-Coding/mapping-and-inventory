import urllib.request
import json
import time
import os

# --- ⚙️ MASTER CONDUCTOR CONFIG ---
# Direct JSON hooks into global commodity futures (No API Keys Required)
METALS = {
    "SILVER": {
        "ticker": "SI=F", 
        "desc": "PRIMARY REFLECTOR (High Priority Storage)", 
        "color": "\033[97m", # White/Silver
        "volatility_trigger": 1.50 # Alert if Silver swings more than 1.5%
    },
    "COPPER": {
        "ticker": "HG=F", 
        "desc": "THERMAL CONDUCTOR (Grid Wiring)", 
        "color": "\033[38;5;208m", # Copper/Orange
        "volatility_trigger": 2.00
    },
    "GOLD": {
        "ticker": "GC=F", 
        "desc": "BASE ANCHOR (Transparent Gold)", 
        "color": "\033[38;5;214m", # Gold
        "volatility_trigger": 1.00
    }
}

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def fetch_spot_price(ticker):
    """Bypasses yfinance library by hitting the raw JSON data-stream directly."""
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=2d"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            meta = data['chart']['result'][0]['meta']
            current = meta['regularMarketPrice']
            prev = meta['previousClose']
            change_pct = ((current - prev) / prev) * 100
            return current, change_pct
    except Exception as e:
        return 0.0, 0.0

def run_tracker():
    while True:
        clear_screen()
        print("\033[96m\033[1m╔═══════════════════════════════════════════════════════════╗\033[0m")
        print("\033[96m\033[1m║ ⚖️  THE 13TH ZONE: PRECIOUS METALS CONDUCTOR HUB          ║\033[0m")
        print("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")
        
        alerts = []
        
        for name, data in METALS.items():
            price, change = fetch_spot_price(data['ticker'])
            color = data['color']
            reset = "\033[0m"
            
            # Format the change indicator
            if change > 0:
                trend = f"\033[92m+{change:.2f}%\033[0m"
            elif change < 0:
                trend = f"\033[91m{change:.2f}%\033[0m"
            else:
                trend = f" {change:.2f}%"

            print(f"\033[96m\033[1m║\033[0m {color}{name:<8}{reset} | ${price:>8.2f} | Tick: {trend:>16} \033[96m\033[1m║\033[0m")
            print(f"\033[96m\033[1m║\033[0m   └─ {data['desc']:<51} \033[96m\033[1m║\033[0m")
            
            # Deep Scan Logic for Silver specifically
            if name == "SILVER" and abs(change) >= data['volatility_trigger']:
                alerts.append(f"⚠️ SILVER VOLATILITY DETECTED: Monitor physical premiums closely.")
            elif abs(change) >= data['volatility_trigger']:
                alerts.append(f"⚡ {name} shifting rapidly ({change:.2f}%).")

        print("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")
        print("\033[96m\033[1m║ 🛰️ T.I.A. MATERIAL ANALYSIS                               ║\033[0m")
        
        if alerts:
            for alert in alerts:
                print(f"\033[96m\033[1m║\033[0m \033[93m{alert:<55}\033[0m \033[96m\033[1m║\033[0m")
        else:
            print("\033[96m\033[1m║\033[0m \033[90mConductors are stable. Market is absorbing the voltage. \033[0m \033[96m\033[1m║\033[0m")
            
        print("\033[96m\033[1m╚═══════════════════════════════════════════════════════════╝\033[0m")
        print("\033[90m(Refreshing in 60 seconds. Press CTRL+C to return to OS...)\033[0m")
        
        try:
            time.sleep(60)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    run_tracker()
