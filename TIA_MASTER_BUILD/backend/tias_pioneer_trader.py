import json
import os
import datetime

def pioneer_harvest_analysis():
    log_path = os.path.expanduser("~/ARK_CORE/Partition_01/vanguard_pulse.log")
    if not os.path.exists(log_path):
        return "[!] PIONEER: No Pulse log found. The harvest is blind."

    with open(log_path, 'r') as f:
        data = [json.loads(line) for line in f.readlines()]

    if len(data) < 10:
        return "[!] PIONEER: Gathering more soil data (need 10+ pulses for macro analysis)."

    # Simple Moving Average for XRP
    prices = [entry['xrp'] for entry in data[-10:]]
    avg_price = sum(prices) / len(prices)
    current_price = prices[-1]

    print(f"[PIONEER-TRADER] Macro Avg: ${avg_price:.4f} | Current: ${current_price:.4f}")

    if current_price < avg_price * 0.98:
        return "PIONEER SIGNAL: UNDERVALUED. Recommend Stacking/Accumulation."
    elif current_price > avg_price * 1.05:
        return "PIONEER SIGNAL: HARVEST READY. Recommend trimming for USDT/Silver."
    
    return "PIONEER STATUS: Holding course. The crop is maturing."

if __name__ == "__main__":
    print(pioneer_harvest_analysis())
