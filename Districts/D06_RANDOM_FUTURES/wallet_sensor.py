import json
import os
import datetime

def get_multi_wallet_status():
    ledger_path = os.path.expanduser("~/ARK_CORE/Partition_01/wallet_ledger.json")
    
    # The 'Triple-Metal' Reserve
    # These are placeholders; the MEXC-Uplink will eventually fill these live.
    default_reserve = {
        "xrp": {"balance": 1000.0, "type": "Silver"},
        "btc": {"balance": 0.05, "type": "Gold"},
        "ada": {"balance": 5000.0, "type": "Copper"},
        "usdt": {"balance": 500.0, "type": "Fuel"}
    }
    
    if not os.path.exists(ledger_path):
        with open(ledger_path, 'w') as f:
            json.dump(default_reserve, f, indent=4)
        return default_reserve
        
    with open(ledger_path, 'r') as f:
        return json.load(f)

def update_wallet_balance(asset, amount):
    ledger = get_multi_wallet_status()
    asset = asset.lower()
    if asset in ledger:
        ledger[asset]['balance'] = amount
        ledger[asset]['last_sync'] = datetime.datetime.now().isoformat()
        
    with open(os.path.expanduser("~/ARK_CORE/Partition_01/wallet_ledger.json"), 'w') as f:
        json.dump(ledger, f, indent=4)
    return ledger

if __name__ == "__main__":
    print(f"[WALLET-UPLINK] Current Reserves: {get_multi_wallet_status()}")
