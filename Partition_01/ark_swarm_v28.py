import asyncio, requests, time, hmac, hashlib, os, json, math

API_KEY = os.environ.get('MEXC_API_KEY')
SECRET_KEY = os.environ.get('MEXC_SECRET_KEY')
HMT_URL = os.environ.get('HMT_76_URL')
HMT_ACCESS = os.environ.get('HMT_76_ACCESS')

WAR_CHEST = [
    "BTCUSDT", "ETHUSDT", "SOLUSDT", "XRPUSDT", "BNBUSDT", "DOGEUSDT", "ADAUSDT", 
    "AVAXUSDT", "TRXUSDT", "DOTUSDT", "LINKUSDT", "MATICUSDT", "SHIBUSDT", "NEARUSDT", 
    "LTCUSDT", "BCHUSDT", "UNIUSDT", "APTUSDT", "XLMUSDT", "SUIUSDT", "ARBUSDT", 
    "OPUSDT", "FILUSDT", "INJUSDT", "RNDRUSDT", "GRTUSDT", "VETUSDT", "HBARUSDT", 
    "TIAUSDT", "ALGOUSDT"
]
TRADE_QTY = 12.00
BASE_LOSS_LIMIT = -2.0 

class HiveMind:
    market_data = {coin: {'price': 0.0, 'change': 0.0, 'history': []} for coin in WAR_CHEST}
    balances = {'USDT': 0.0, 'XRP': 0.0}
    buy_prices = {} 
    logs = ["🕸️ V28 Transparency Swarm Initialized."]

hive = HiveMind()

def log(msg):
    hive.logs.append(msg)
    if len(hive.logs) > 8: hive.logs.pop(0)

def get_sig(params):
    return hmac.new(SECRET_KEY.encode(), params.encode(), hashlib.sha256).hexdigest()

def fire(coin, side, qty):
    ts = str(int(time.time() * 1000))
    params = f"symbol={coin}&side={side}&type=MARKET&quoteOrderQty={qty}&timestamp={ts}"
    try:
        r = requests.post(f"https://api.mexc.com/api/v3/order?{params}&signature={get_sig(params)}", 
                         headers={"X-MEXC-APIKEY": API_KEY}, timeout=5)
        return r.status_code == 200
    except: return False

def query_airgap_ai(prompt, model="phi"):
    headers = {"Authorization": f"Bearer {HMT_ACCESS}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{HMT_URL}/api/inference", headers=headers, json={"query": prompt, "model_route": model}, timeout=6)
        resp_text = r.text.strip().upper()[:15] # Grab first 15 chars
        log(f"🤖 {model.upper()} SAYS: {resp_text}")
        if "BUY" in resp_text: return "BUY"
    except Exception as e:
        log(f"⚠️ AI LINK ERROR: {str(e)[:20]}")
    return "HOLD"

async def oracle_node():
    while True:
        try:
            ts = str(int(time.time() * 1000))
            r_bal = await asyncio.to_thread(requests.get, f"https://api.mexc.com/api/v3/account?timestamp={ts}&signature={get_sig(f'timestamp={ts}')}", headers={"X-MEXC-APIKEY": API_KEY}, timeout=3)
            if r_bal.status_code == 200:
                hive.balances = {b['asset']: float(b['free']) for b in r_bal.json().get('balances', []) if float(b['free']) > 0}
            
            r_all = await asyncio.to_thread(requests.get, "https://api.mexc.com/api/v3/ticker/price", timeout=3)
            if r_all.status_code == 200:
                price_dict = {item['symbol']: float(item['price']) for item in r_all.json()}
                for coin in WAR_CHEST:
                    p = price_dict.get(coin, 0.0)
                    if p == 0.0: continue
                    old_p = hive.market_data[coin]['price']
                    hive.market_data[coin]['price'] = p
                    hive.market_data[coin]['change'] = ((p - old_p) / old_p * 100) if old_p > 0 else 0.0
                    hive.market_data[coin]['history'].append(p)
                    if len(hive.market_data[coin]['history']) > 20: hive.market_data[coin]['history'].pop(0)
        except: pass
        await asyncio.sleep(3)

async def piranha_node():
    while True:
        try:
            usdt = hive.balances.get('USDT', 0.0)
            if usdt >= TRADE_QTY:
                for coin in WAR_CHEST:
                    hist = hive.market_data[coin]['history']
                    if len(hist) < 5: continue
                    avg_vol = sum(abs((hist[i]-hist[i-1])/hist[i-1]*100) for i in range(1, len(hist)))/len(hist)
                    trigger = max(-0.15, -(avg_vol * 1.5))
                    diff = hive.market_data[coin]['change']
                    
                    if diff < trigger:
                        log(f"🐟 PIRANHA: {coin} dip ({diff:.2f}%) > {trigger:.2f}%")
                        if await asyncio.to_thread(query_airgap_ai, f"Strike {coin}?", "phi") == "BUY":
                            if await asyncio.to_thread(fire, coin, "BUY", TRADE_QTY):
                                hive.buy_prices[coin] = hive.market_data[coin]['price']
                                log(f"⚔️ SUCCESS: Bought {coin}")
        except: pass
        await asyncio.sleep(4)

async def dashboard_node():
    while True:
        os.system('clear')
        u, x = hive.balances.get('USDT', 0.0), hive.balances.get('XRP', 0.0)
        print(f"╔═══════════════════════════════════════════════════════════╗")
        print(f"║ 🎖️ THE ARK FLEET: V28 LIVE AI FEED                        ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        print(f"║ 💰 WALLET: ${u:.2f} | 💎 XRP: {x:.2f}                            ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for msg in hive.logs: print(f"║ {msg[:55]:<57} ║")
        print(f"╠═══════════════════════════════════════════════════════════╣")
        for coin in WAR_CHEST[:6]:
            d = hive.market_data[coin]
            print(f"║ 🎯 {coin[:4]:<5}: ${d['price']:<9.4f} | Tick: {d['change']:>6.3f}%{' ' * 23}║")
        print(f"╚═══════════════════════════════════════════════════════════╝")
        await asyncio.sleep(1)

async def main():
    await asyncio.gather(oracle_node(), piranha_node(), dashboard_node())

if __name__ == "__main__": asyncio.run(main())
