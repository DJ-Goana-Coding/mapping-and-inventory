import os
import json

def coordinate_armada():
    ark = os.path.expanduser("~/ARK_CORE")
    
    # 1. Gather Intelligence from all sectors
    pulse_log = os.path.join(ark, "Partition_01/vanguard_pulse.log")
    scout_log = os.path.join(ark, "Partition_01/trade_proposals.log") # Shared scout/weld log
    
    report = {
        "master_status": "OPTIMIZED",
        "active_nodes": 46,
        "recommendation": "STAY VIGILANT"
    }
    
    if os.path.exists(pulse_log):
        with open(pulse_log, 'r') as f:
            last_p = json.loads(f.readlines()[-1])
            # Master logic: If BTC is volatile, tell the Swarm to tighten spreads
            if last_p['btc'] > 70000:
                report['recommendation'] = "SWARM: AGGRESSIVE HARVEST MODE"
            elif last_p['btc'] < 60000:
                report['recommendation'] = "PIONEER: ACCUMULATION DEFENSE"
                
    print(f"[MASTER-AGENT] Logic synchronized. Strategy: {report['recommendation']}")
    return report

if __name__ == "__main__":
    coordinate_armada()
