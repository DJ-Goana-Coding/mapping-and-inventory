import requests
import time
import hmac
import hashlib
import os

# --- CITADEL CONFIG ---
NODE_NAME = "Citadel Commander (Node 01)"
TARGET_COINS = ["XRPUSDT", "SOLUSDT", "ADAUSDT"]
BASE_TRADE_USD = 7.00 # $10.50 AUD Freedom Ladder Base

# ⚠️ THE SAFETY CATCH: Change to True ONLY when ready to fire live orders
LIVE_TRADING_ENABLED = False 

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')

def get_price(symbol):
    """Scout Agent: Fetches live price."""
    url = f"https://api.mexc.com/api/v3/ticker/price?symbol={symbol}"
    return float(requests.get(url, timeout=5).json()['price'])

def ask_oracle(symbol, price):
    """Oracle Agent: Consults local Plutus model."""
    prompt = f"The crypto {symbol} is currently priced at ${price}. Acting as a quantitative trading AI, output EXACTLY ONE WORD: either BUY, SELL, or HOLD."
    payload = {
        "model": "0xroyce/plutus:latest",
        "prompt": prompt,
        "stream": False
    }
    try:
        res = requests.post("http://localhost:11434/api/generate", json=payload, timeout=120)
        decision = res.json().get('response', '').strip().upper()
        
        if "BUY" in decision: return "BUY"
        elif "SELL" in decision: return "SELL"
        else: return "HOLD"
    except Exception as e:
        return f"ERR_OLLAMA"

def execute_trade(symbol, side, quote_qty):
    """Execution Agent: Signs and sends the order to MEXC."""
    if not LIVE_TRADING_ENABLED or not API_KEY or not SECRET_KEY:
        return "SAFETY_ON"

    timestamp = str(int(time.time() * 1000))
    query_string = f"symbol={symbol}&side={side}&type=MARKET&quoteOrderQty={quote_qty}&timestamp={timestamp}"
    
    # Cryptographic Signature (Bare-metal, no ccxt required)
    signature = hmac.new(SECRET_KEY.encode('utf-8'), query_string.encode('utf-8'), hashlib.sha256).hexdigest()
    
    url = f"https://api.mexc.com/api/v3/order?{query_string}&signature={signature}"
    headers = {
        "X-MEXC-APIKEY": API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        res = requests.post(url, headers=headers)
        if res.status_code == 200:
            return "SUCCESS"
        return f"FAILED: {res.json()}"
    except Exception as e:
        return f"NETWORK_ERR"

def swarm_loop():
    while True:
        os.system('clear')
        print(f"🏛️ CITADEL MULTI-AGENT ENGINE: ACTIVE")
        print(f"🧠 ORACLE: 0xroyce/plutus:latest (Localhost)")
        print(f"🔑 MEXC API: {'✅ LOADED' if API_KEY else '⚠️ MISSING'}")
        print(f"⚠️ LIVE TRADING: {'🔥 ARMED' if LIVE_TRADING_ENABLED else '🛑 SAFETY CATCH ON'}")
        print("-" * 45)
        
        for symbol in TARGET_COINS:
            try:
                # 1. Scout 
                price = get_price(symbol)
                
                # 2. Oracle
                decision = ask_oracle(symbol, price)
                
                # 3. Execution
                status = "PASS"
                if decision in ["BUY", "SELL"]:
                    status = execute_trade(symbol, decision, BASE_TRADE_USD)
                
                # Mobile Cockpit Output (Strict UI)
                print(f"🎯 {symbol[:3]}: ${price:<7.4f} | VOTE: {decision:<4} | EXEC: {status}")
                
            except Exception as e:
                print(f"⚠️ {symbol} Scan Error: Retrying...")
        
        print("-" * 45)
        print(f"⏳ Cycle Complete. Awaiting next phase...")
        time.sleep(60)

if __name__ == "__main__":
    try:
        swarm_loop()
    except KeyboardInterrupt:
        print("\n🛑 Citadel Engine Shutdown.")
