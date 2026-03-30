import json
import os

def calculate_gains():
    ledger_path = os.path.expanduser("~/ARK_CORE/Partition_01/trade_ledger.json")
    pulse_path = os.path.expanduser("~/ARK_CORE/Partition_01/vanguard_pulse.log")
    
    if not os.path.exists(ledger_path) or not os.path.exists(pulse_path):
        return "[!] TREASURY: Data incomplete. Run Pulse and Live-Trader first."

    # Get latest prices
    with open(pulse_path, 'r') as f:
        last_pulse = json.loads(f.readlines()[-1])
    
    # Get trade history
    with open(ledger_path, 'r') as f:
        history = json.load(f)

    report = "--- TREASURY PROFIT REPORT ---\n"
    total_pl = 0
    
    for trade in history:
        asset = trade['asset'].lower()
        if asset in last_pulse:
            current_price = last_pulse[asset]
            entry_price = 1.30 # Standardizing for this build; can be dynamic
            qty = trade['amount']
            pl = (current_price - entry_price) * qty
            total_pl += pl
            report += f"{asset.upper()}: Entry $1.30 | Now ${current_price} | P/L: ${pl:.2f}\n"

    report += f"------------------------------\nTOTAL GRID GAIN: ${total_pl:.2f}"
    print(report)
    return report

if __name__ == "__main__":
    calculate_gains()
