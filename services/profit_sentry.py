import os
from services.market_sensor import get_market_pulse
from datetime import datetime

# --- Q.G.T.N.L. (0) // PROFIT SENTRY V61.6 ---
# Added: Auto-Tagging Logic (#PROFIT, #ALERT)

TARGETS = {"BTC": 75000.00, "SILVER": 32.00}

def watch_markets():
    print("🔭 PROFIT SENTRY SCANNING PADDOCK...")
    pulse = get_market_pulse()
    log_path = os.path.expanduser("~/ARK_CORE/Partition_01/aetheric_log.txt")
    alerts = []
    
    if 'BTC' in pulse:
        btc_price = float(pulse['BTC'].replace('$', '').replace(',', ''))
        if btc_price >= TARGETS["BTC"]:
            alerts.append(f"#ALERT #PROFIT: BTC hit {pulse['BTC']} (Target: {TARGETS['BTC']})")

    if 'SILVER' in pulse:
        silver_price = float(pulse['SILVER'].split(' ')[0].replace('$', ''))
        if silver_price >= TARGETS["SILVER"]:
            alerts.append(f"#ALERT #PROFIT: SILVER hit {pulse['SILVER']} (Target: {TARGETS['SILVER']})")

    if alerts:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a") as f:
            for a in alerts:
                f.write(f"[{ts}] [PROFIT-SENTRY] {a}\n")
        print(f"🚨 {len(alerts)} ALERTS LOGGED.")
    else:
        print("✅ #STABLE: No targets breached.")

if __name__ == "__main__":
    watch_markets()
