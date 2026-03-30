import os
import json
import datetime

def execute_sovereign_order(asset, action, amount):
    # This is the 'Hand of the Architect'
    order_id = f"ARK-{int(datetime.datetime.now().timestamp())}"
    
    execution_report = {
        "order_id": order_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "asset": asset.upper(),
        "action": action.upper(),
        "amount": amount,
        "status": "SIMULATED_SUCCESS" # Set to 'LIVE' once MEXC-Uplink is fully keyed
    }
    
    # Save to the Trade Ledger (The history TIA reads)
    ledger_path = os.path.expanduser("~/ARK_CORE/Partition_01/trade_ledger.json")
    
    history = []
    if os.path.exists(ledger_path):
        with open(ledger_path, 'r') as f:
            history = json.load(f)
            
    history.append(execution_report)
    
    with open(ledger_path, 'w') as f:
        json.dump(history, f, indent=4)
        
    print(f"[VANGUARD-LIVE] {action} Order for {amount} {asset} executed. ID: {order_id}")
    return execution_report

if __name__ == "__main__":
    # Example: If T.I.A. signals a Buy for XRP
    execute_sovereign_order("XRP", "BUY", 100)
