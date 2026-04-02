import requests, time, hmac, hashlib, os, json

# --- ⚙️ V23 FLEET CONFIGURATION ---
API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HF_KEY = os.environ.get('HF_API_KEY')

WAR_CHEST = ["XRPUSDT", "SOLUSDT", "BTCUSDT", "ETHUSDT", "TIAUSDT", "XLMUSDT", "HBARUSDT", "ADAUSDT"]
RESTRICTED = ["XRPUSDT", "XLMUSDT", "HBARUSDT"]
TRADE_QTY = 12.00
TARGET_XRP = 500.00
BASE_USDT_CAP = 70.00 # Level-Up target baseline

# --- ☁️ G-DRIVE BRIDGE (S10 UPLINK) ---
GDRIVE_PATH = "./Research/S10"
os.makedirs(GDRIVE_PATH, exist_ok=True)
STATE_FILE = f"{GDRIVE_PATH}/market_state.json"
SIGNAL_FILE = f"{GDRIVE_PATH}/ai_signal.json"
AUDIT_FILE = f"{GDRIVE_PATH}/fleet_ledger.csv"
VAULT_FILE = f"{GDRIVE_PATH}/fleet_vault.json"

# Memory tracking
PRICE_MEM = {}
SYSTEM_LOG = ["🕸️ Ark Fleet V23 Architect Initializing..."]

# Load or initialize the Vault
if os.path.exists(VAULT_FILE):
    with open(VAULT_FILE, "r") as f: vault = json.load(f)
else:
    vault = {"cash_reserve": 0.0, "level": 1, "target_cap": 80.00}

def log(msg):
    SYSTEM_LOG.append(msg)
    if len(SYSTEM_LOG) > 8: SYSTEM_LOG.pop(0)

def get_sig(params):
    return hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

def fire(coin, side, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
    return r.status_code == 200

# --- 🧠 TIA: HUGGING FACE Llama-3.2 INFERENCE ---
def query_hf_ai(coin, drop_pct):
    if not HF_KEY: return "HOLD"
    prompt = f"The crypto asset {coin} just dropped by {drop_pct}% in the last 5 seconds. Respond with only the word BUY to scalp the bounce, or HOLD to wait."
    headers = {"Authorization": f"Bearer {HF_KEY}", "Content-Type": "application/json"}
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 5, "temperature": 0.1}}
    try:
        r = requests.post("https://api-inference.huggingface.co/models/meta-llama/Llama-3.2-1B-Instruct", headers=headers, json=payload, timeout=3)
        if r.status_code == 200 and "BUY" in r.text.upper(): return "BUY"
    except: pass
    return "HOLD"

log("✅ Tri-Core Systems Online. Engaging V23 Master Loop.")

# --- ♾️ THE V23 MASTER LOOP ---
while True:
    try:
        # 1. ORACLE: Fetch Balances
        ts = str(int(time.time() * 1000))
        r_bal = requests.get(f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3).json()
        balances = {b['asset']: float(b['free']) for b in r_bal.get('balances', []) if float(b['free']) > 0}
        usdt, xrp = balances.get('USDT', 0.0), balances.get('XRP', 0.0)

        # Level-Up Vault Logic
        if usdt >= vault["target_cap"]:
            skim = usdt - BASE_USDT_CAP
            vault["cash_reserve"] += skim
            vault["level"] += 1
            vault["target_cap"] += 5.00
            with open(VAULT_FILE, "w") as f: json.dump(vault, f)
            log(f"🏦 LEVEL UP! Vault Skimmed: ${skim:.2f} | New Target: ${vault['target_cap']:.2f}")

        # 2. ORACLE: Fetch Prices & Micro-Volatility
        market_data = {}
        for coin in WAR_CHEST:
            r_price = requests.get(f"https://api.mexc.com/api/v3/ticker/price?symbol={coin}", timeout=2).json()
            p = float(r_price['price'])
            if coin not in PRICE_MEM: PRICE_MEM[coin] = p
            
            diff = ((p - PRICE_MEM[coin]) / PRICE_MEM[coin]) * 100
            market_data[coin] = {'price': p, 'change': diff}
            PRICE_MEM[coin] = p 

            # 3. TIA LOCAL HOOK
            if diff < -0.50 and usdt >= TRADE_QTY:
                log(f"🧠 TIA: {coin} Flash Dip ({diff:.2f}%). Querying AI...")
                if query_hf_ai(coin, diff) == "BUY":
                    if fire(coin, "BUY", TRADE_QTY):
                        log(f"⚔️ AION: HF AI Confirmed. Executed BUY on {coin}")
                        with open(AUDIT_FILE, "a") as f: f.write(f"{time.ctime()},BUY,{coin},{TRADE_QTY},LOCAL_HF_AI\n")

        # 4. UPLINK: Send State to S10 via G-Drive
        state_payload = {"timestamp": time.time(), "balances": balances, "market": market_data, "vault": vault}
        with open(STATE_FILE, "w") as f: json.dump(state_payload, f)
        s10_status = "📡 S10 Uplink: Awaiting Commands..."

        # 5. AION EXECUTION: Check G-Drive for S10 Overrides
        if os.path.exists(SIGNAL_FILE):
            with open(SIGNAL_FILE, "r") as f: ai_signal = json.load(f)
            if not ai_signal.get("executed") and (time.time() - ai_signal.get("timestamp", 0) < 30):
                coin, side = ai_signal['coin'], ai_signal['action']
                if fire(coin, side, TRADE_QTY):
                    s10_status = f"⚔️ S10 OVERRIDE: {side} {coin}"
                    log(s10_status)
                    ai_signal["executed"] = True
                    with open(SIGNAL_FILE, "w") as f: json.dump(ai_signal, f)
                    with open(AUDIT_FILE, "a") as f: f.write(f"{time.ctime()},{side},{coin},{TRADE_QTY},S10_REMOTE_AI\n")

        # 6. DASHBOARD RENDER
        os.system('clear')
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE ARK FLEET: V23 ARCHITECT                           ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WALLET: ${usdt:.2f} | 💎 XRP: {xrp:.2f}/{TARGET_XRP}                  ║")
        print(f"║ 🏦 VAULT (Lvl {vault['level']}): ${vault['cash_reserve']:.2f} | Next Skim Target: ${vault['target_cap']:.2f}    ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ ☁️ G-DRIVE: ACTIVE | 🧠 LOCAL HF: ACTIVE                  ║")
        print(f"║ {s10_status:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for msg in SYSTEM_LOG: print(f"║ {msg:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for coin in WAR_CHEST:
            data = market_data.get(coin, {'price': 0, 'change': 0})
            print(f"║ 🎯 {coin[:4]:<5}: ${data['price']:<9.4f} | Micro-Vol: {data['change']:>6.3f}%{' ' * 16}║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        
        if xrp >= TARGET_XRP: print("\n🏆 500 XRP VAULT SECURED. MISSION COMPLETE."); break
        time.sleep(3) 
    except Exception as e:
        time.sleep(3); continue
