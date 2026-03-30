import json
import os

def scout_grid_gaps():
    pulse_path = os.path.expanduser("~/ARK_CORE/Partition_01/vanguard_pulse.log")
    if not os.path.exists(pulse_path):
        return "[!] SCOUT: Pulse log missing. Cannot scout."
    
    with open(pulse_path, 'r') as f:
        data = [json.loads(line) for line in f.readlines()]
    
    if len(data) < 2:
        return "[!] SCOUT: Insufficient data for gap analysis."
    
    # Calculate volatility between last two pulses
    last = data[-1]
    prev = data[-2]
    
    diff = abs(last['xrp'] - prev['xrp'])
    print(f"[OMEGA-SCOUT] XRP Delta: ${diff:.4f}")
    
    if diff > 0.01:
        return f"VOLATILITY DETECTED: XRP moved ${diff:.4f}. Signal sent to Trader."
    return "STABLE: No significant gaps detected."

if __name__ == "__main__":
    print(scout_grid_gaps())
