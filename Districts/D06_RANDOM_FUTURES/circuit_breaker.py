import json
import os

def check_volatility_threshold(threshold=10.0):
    pulse_path = os.path.expanduser("~/ARK_CORE/Partition_01/vanguard_pulse.log")
    state_path = os.path.expanduser("~/ARK_CORE/Partition_01/system_state.json")
    
    if not os.path.exists(pulse_path):
        return "PULSE OFFLINE"

    with open(pulse_path, 'r') as f:
        lines = f.readlines()
        if len(lines) < 2:
            return "GATHERING DATA"
            
        now = json.loads(lines[-1])
        prev = json.loads(lines[-2])
        
    # Calculate % change for XRP
    change = ((now['xrp'] - prev['xrp']) / prev['xrp']) * 100
    
    status = "STABLE"
    if abs(change) >= threshold:
        status = "CRITICAL VOLATILITY - SYSTEM LOCKED"
        with open(state_path, 'w') as f:
            json.dump({"mode": "LOCKED", "reason": f"Volatility {change:.2f}%"}, f)
            
    print(f"[CIRCUIT-BREAKER] XRP Change: {change:.2f}% | Status: {status}")
    return status

if __name__ == "__main__":
    check_volatility_threshold()
