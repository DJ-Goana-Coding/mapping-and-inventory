import json
import os

def calculate_rsi(prices, periods=14):
    if len(prices) < periods:
        return 50.0  # Neutral if not enough data
    
    gains = []
    losses = []
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        gains.append(max(0, change))
        losses.append(max(0, -change))
        
    avg_gain = sum(gains[-periods:]) / periods
    avg_loss = sum(losses[-periods:]) / periods
    
    if avg_loss == 0: return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - (100.0 / (1.0 + rs))

def get_market_physics():
    pulse_path = os.path.expanduser("~/ARK_CORE/Partition_01/vanguard_pulse.log")
    if not os.path.exists(pulse_path):
        return {"error": "No data"}

    with open(pulse_path, 'r') as f:
        data = [json.loads(line) for line in f.readlines()]
    
    xrp_prices = [d['xrp'] for d in data]
    
    physics = {
        "xrp_rsi": calculate_rsi(xrp_prices),
        "xrp_ma_5": sum(xrp_prices[-5:]) / 5 if len(xrp_prices) >= 5 else xrp_prices[-1],
        "status": "CALCULATED"
    }
    return physics

if __name__ == "__main__":
    print(f"[TECH-WELD] Physics Report: {get_market_physics()}")
