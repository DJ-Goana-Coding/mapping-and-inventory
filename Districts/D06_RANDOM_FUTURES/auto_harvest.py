import os
import json
from services.tech_indicators import get_market_physics
from Partition_01.vanguard_live_trader import execute_sovereign_order

def run_auto_harvest_check():
    print("[!] AUTO-HARVEST: INITIATING SCAN...")
    
    physics = get_market_physics()
    rsi = physics.get('xrp_rsi', 50)
    
    # Define your Harvest Parameters
    # RSI < 30: Buy (Accumulate)
    # RSI > 70: Sell (Harvest)
    
    if rsi < 30:
        print(f"[SIGNAL] RSI IS {rsi:.2f}: OVERSOLD. TRIGGERING ACCUMULATION.")
        execute_sovereign_order("XRP", "BUY", 50)
        return "ACCUMULATION TRIGGERED"
    elif rsi > 70:
        print(f"[SIGNAL] RSI IS {rsi:.2f}: OVERBOUGHT. TRIGGERING HARVEST.")
        execute_sovereign_order("XRP", "SELL", 50)
        return "HARVEST TRIGGERED"
    
    print(f"[STATUS] RSI IS {rsi:.2f}: NEUTRAL. STANDING BY.")
    return "NEUTRAL - STANDING BY"

if __name__ == "__main__":
    run_auto_harvest_check()
