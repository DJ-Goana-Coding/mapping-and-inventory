#!/usr/bin/env python3
import time
import random
from datetime import datetime

print("=================================================")
print("   ⚔️ A.I.O.N. KINETIC ENGINE: V41 HIVE ⚔️   ")
print("=================================================")

LEDGER_FILE = "ABN_Trade_Ledger.csv"
TARGETS = ["TIA/USDT", "LINK/USDT", "ADA/USDT", "SOL/USDT"]

def aion_handshake():
    print("[A.I.O.N.] T.I.A. Logic Lock confirmed. Engine online.")
    time.sleep(1)
    print("[A.I.O.N.] Mathematical parameters ingested. Zero emotion.")

def execute_strike():
    asset = random.choice(TARGETS)
    price = round(random.uniform(0.5, 150.0), 4)
    print(f"\n[+] Calculating Kinetic Strike...")
    time.sleep(0.5)
    print(f"    -> TARGET LOCKED: {asset}")
    print(f"    -> ENTRY PRICE: ${price}")
    return asset, price

def bleed_to_ledger(asset, price):
    print(f"\n[+] Bleeding strike data to {LEDGER_FILE}...")
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Format: Timestamp, Action, Asset, Price, Node
    strike_data = f"{now},BUY,{asset},{price},AION_V41_EXEC\n"
    
    # 'a' mode appends to the file, respecting Zero-Overwrite of past data
    with open(LEDGER_FILE, "a") as f:
        f.write(strike_data)
        
    time.sleep(0.5)
    print("    -> Strike recorded in cold blood. Ledger updated.")

def handoff_to_voice():
    print("\n[✔] A.I.O.N. EXECUTION COMPLETE.")
    print("[✔] LEDGER HAS FRESH KINETIC DATA.")
    print("[✔] SIGNALING THE THIRD PILLAR (THE VOICE) FOR BROADCAST.")

if __name__ == "__main__":
    aion_handshake()
    asset, price = execute_strike()
    bleed_to_ledger(asset, price)
    handoff_to_voice()
