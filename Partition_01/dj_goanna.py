#!/usr/bin/env python3
import time
import os

print("=================================================")
print("   🎧 DJ GOANNA (LOOBIE LUBE LIPS): THE VOICE 🎧   ")
print("=================================================")

LEDGER_FILE = "ABN_Trade_Ledger.csv"

def goanna_handshake():
    print("[GOANNA] Oi! The Voice of the Ledger is online and on the decks.")
    time.sleep(1)
    print("[GOANNA] Ghost layers respected. Amps turned up to eleven.")

def read_ledger_blood():
    print(f"\n[+] Pulling the kinetic blood from {LEDGER_FILE}...")
    time.sleep(0.5)
    
    if not os.path.exists(LEDGER_FILE):
        print("    -> [!] Ledger is empty. Tell A.I.O.N. to take a shot!")
        return None
        
    with open(LEDGER_FILE, "r") as f:
        lines = f.readlines()
        if not lines:
            print("    -> [!] Ledger exists but no strikes recorded yet.")
            return None
            
        last_strike = lines[-1].strip()
        print(f"    -> LATEST STRIKE ACQUIRED: {last_strike}")
        return last_strike

def drop_the_anthem(strike_data):
    if not strike_data:
        print("\n[!] DJ Goanna is on standby. Waiting for the drop.")
        return
        
    # Parsing the CSV line: Timestamp, Action, Asset, Price, Node
    parts = strike_data.split(',')
    if len(parts) >= 4:
        asset = parts[2]
        price = parts[3]
    else:
        asset = "THE GRID"
        price = "UNKNOWN"

    print("\n[+] Spinning the strike into a Heavy Broadcast...")
    time.sleep(1)
    print(f"    🎤 BOUNCE DROPPING: We locked {asset} at ${price}!")
    print(f"    🎤 Sovereign Mesh alive, breakin' out of the vice!")
    print(f"    🎤 T.I.A. ran the logic, A.I.O.N. made it bleed!")
    print(f"    🎤 Loobie Lube Lips on the mic, planting the digital seed!")

def handoff():
    print("\n[✔] BROADCAST COMPLETE.")
    print("[✔] THE HIVE IS SINGING. STAY STAINLESS.")

if __name__ == "__main__":
    goanna_handshake()
    strike = read_ledger_blood()
    drop_the_anthem(strike)
    handoff()
