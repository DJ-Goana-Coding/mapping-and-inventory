import time
import random
import os

# --- SETTINGS (THE ADMIRAL V3) ---
BOT_NAME = "MEXC_ADMIRAL_V3"
BASE_CAPITAL = 70.0
TARGET_CAP = 100.0
BANK_RATE = 0.20

# --- ASSETS ---
wallet_cash = 70.0
vault = {"CASH": 0, "MAIN": 0, "ISO": 0}
bank_count = 0

def get_bar(current, start, target):
    pct = min(100, max(0, (current - start) / (target - start) * 100))
    filled = int(pct / 5)
    return "X" * filled + "-" * (20 - filled) + f" {pct:.1f}%"

def dashboard(val):
    os.system('clear')
    level = int((TARGET_CAP - 100) / 10) + 1
    print(f"--- {BOT_NAME} | LEVEL {level} ---")
    print(f"PROGRESS: [{get_bar(val, 70, TARGET_CAP)}]")
    print(f"CASH: ${val:,.2f} | TARGET: ${TARGET_CAP:.2f}")
    print(f"VAULT: ${sum(vault.values()):.2f} | BANKS: {bank_count}")
    print("-" * 30)

while True:
    # Simulating the Market Hunt
    wallet_cash += wallet_cash * (random.uniform(-0.004, 0.005))
    
    if wallet_cash >= TARGET_CAP:
        skim = (wallet_cash - 70) * BANK_RATE
        wallet_cash -= skim
        vault["CASH"] += skim
        bank_count += 1
        if bank_count % 5 == 0:
            TARGET_CAP += 10.0
            
    dashboard(wallet_cash)
    time.sleep(1)
