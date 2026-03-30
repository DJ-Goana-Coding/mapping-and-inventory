import urllib.request, json

WALLET = "F6BWLmY3NJgq6pNSZqoBkEnY12YawZGxUYUPCBzmWjXA"
RPC = "https://api.mainnet-beta.solana.com"

def ping_chain(payload):
    req = urllib.request.Request(RPC, data=json.dumps(payload).encode(), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        return None

def scan_radar():
    print(f"\n[+] OMEGA-TRADER: Scanning Solana Mainnet for {WALLET[:8]}...")
    print("--- 📡 WEB3 DECENTRALIZED BALANCES ---")
    
    # Ping 1: Get Native SOL Balance
    sol_payload = {"jsonrpc":"2.0", "id":1, "method":"getBalance", "params":[WALLET]}
    sol_res = ping_chain(sol_payload)
    if sol_res and 'result' in sol_res:
        sol_bal = sol_res['result']['value'] / 1e9
        print(f"[SOL] Native Solana Balance: {sol_bal:.4f} SOL")
        
    # Ping 2: Get All SPL Tokens (UGOR, USDC, etc.)
    tok_payload = {
        "jsonrpc":"2.0", "id":2, "method":"getTokenAccountsByOwner",
        "params":[WALLET, {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"}, {"encoding": "jsonParsed"}]
    }
    tok_res = ping_chain(tok_payload)
    
    if tok_res and 'result' in tok_res:
        accounts = tok_res['result']['value']
        for acc in accounts:
            info = acc['account']['data']['parsed']['info']
            mint = info['mint']
            amt = float(info['tokenAmount']['uiAmount'])
            
            if amt > 0:
                if mint == "UGoRwdj9SK78V6Pq9YMz9BvmNuJTLNqPZyS5WnGd8uW":
                    print(f"[UGOR] Official Oil Reserve: {amt:,.2f} UGOR")
                else:
                    print(f"[TOKEN: {mint[:4]}...{mint[-4:]}] Balance: {amt:,.2f}")
    
    print("--------------------------------------\n")

if __name__ == "__main__":
    scan_radar()
