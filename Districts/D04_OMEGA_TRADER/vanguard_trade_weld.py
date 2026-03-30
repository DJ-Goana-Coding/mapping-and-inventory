import json
import os
import datetime

def propose_trade(asset, current_price):
    # Sovereign Trade Logic
    # Example: If XRP is under $1.30, it might be a 'Buy'. If over $1.50, a 'Sell'.
    targets = {
        "xrp": {"buy_below": 1.20, "sell_above": 1.50},
        "ada": {"buy_below": 0.20, "sell_above": 0.30}
    }
    
    status = "HOLD"
    if asset in targets:
        if current_price <= targets[asset]["buy_below"]:
            status = "SIGNAL: BUY/ACCUMULATE"
        elif current_price >= targets[asset]["sell_above"]:
            status = "SIGNAL: SELL/HARVEST"
            
    trade_proposal = {
        "timestamp": datetime.datetime.now().isoformat(),
        "asset": asset,
        "price": current_price,
        "action": status
    }
    
    # Log the proposal for T.I.A. to review
    log_path = os.path.expanduser("~/ARK_CORE/Partition_01/trade_proposals.log")
    with open(log_path, "a") as f:
        f.write(json.dumps(trade_proposal) + "\n")
        
    print(f"[VANGUARD-WELD] {asset.upper()} at ${current_price}: {status}")
    return trade_proposal

if __name__ == "__main__":
    # Test with the last XRP price we saw ($1.34)
    propose_trade("xrp", 1.34)
