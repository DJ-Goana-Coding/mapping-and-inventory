# 🧪 Trading Spare Parts Lab - Quick Start Card

**Location:** `Trading_Garages/Trading_Garage_SpareParts/`  
**Purpose:** Mix-and-match trading components and test with live crypto APIs

---

## ⚡ 30-Second Start

```bash
cd Trading_Garages/Trading_Garage_SpareParts/

# Test live crypto APIs (no secrets!)
python sandboxes/api_sandbox.py

# Build a trading strategy
python sandboxes/strategy_sandbox.py
```

---

## 🔌 Live Crypto APIs - NO SECRETS REQUIRED!

### Get Bitcoin Price (Right Now!)

```python
from api_templates.binance_public_api import BinancePublicAPI

api = BinancePublicAPI()
btc = api.get_ticker_price("BTCUSDT")
eth = api.get_ticker_price("ETHUSDT")

print(f"BTC: ${btc:,.2f}")
print(f"ETH: ${eth:,.2f}")
```

### Compare Prices Across Exchanges

```python
from api_templates.generic_crypto_api import GenericCryptoAPI

api = GenericCryptoAPI()
prices = api.compare_prices("BTCUSDT")

for exchange, price in prices.items():
    print(f"{exchange}: ${price:,.2f}")
```

### Find Arbitrage Opportunities

```python
arb = api.find_arbitrage("BTCUSDT", min_diff_percent=0.5)
if arb:
    print(f"Buy from {arb['buy_from']} @ ${arb['buy_price']}")
    print(f"Sell to {arb['sell_to']} @ ${arb['sell_price']}")
    print(f"Profit: {arb['profit_percent']:.2f}%")
```

---

## 🎯 Build Trading Strategies

### Example 1: MA Crossover

```python
from sandboxes.strategy_sandbox import Strategy, MovingAverage, CrossoverSignal

strategy = Strategy("MA Crossover")
strategy.add_indicator(MovingAverage(5))
strategy.add_indicator(MovingAverage(20))
strategy.add_signal(CrossoverSignal("MA(5)", "MA(20)"))

results = strategy.backtest(prices)
print(f"Win Rate: {results['win_rate']}%")
```

### Example 2: RSI Strategy

```python
from sandboxes.strategy_sandbox import Strategy, RSI

strategy = Strategy("RSI")
strategy.add_indicator(RSI(14))
# Signals generated automatically (oversold/overbought)

results = strategy.backtest(prices)
```

---

## 🧪 Interactive Testing

### API Sandbox

```bash
python sandboxes/api_sandbox.py

# Interactive commands:
api> price BTCUSDT      # Get BTC price
api> compare ETHUSDT    # Compare ETH across exchanges
api> book BTCUSDT       # Show order book
```

### Strategy Sandbox

```bash
python sandboxes/strategy_sandbox.py

# Runs 3 example strategies:
# 1. Simple MA Crossover
# 2. RSI Strategy
# 3. Combined MA + RSI
```

---

## 📁 What's Available

```
Trading_Garage_SpareParts/
├── api_templates/
│   ├── binance_public_api.py    ✅ Live BTC/ETH/crypto prices
│   └── generic_crypto_api.py    ✅ Multi-exchange, arbitrage
│
├── sandboxes/
│   ├── api_sandbox.py           ✅ Interactive API testing
│   └── strategy_sandbox.py      ✅ Strategy builder
│
├── strategy_templates/          📦 (ready for your strategies)
├── notebooks/                   📦 (ready for your notebooks)
├── components/                  📦 (ready for your components)
└── examples/                    📦 (ready for your examples)
```

---

## 🎨 Mix & Match Workflow

1. **Get Live Data** → Use API templates (no auth needed!)
2. **Build Strategy** → Mix indicators + signals
3. **Test in Sandbox** → Validate logic
4. **Backtest** → Run on historical data
5. **Deploy** → Move to production garage

---

## 🔐 Security

**NO SECRETS IN THIS GARAGE!**

- ✅ Public API endpoints only (no authentication)
- ✅ Test/demo data
- ✅ Paper trading (simulated)

For real trading → Move to Alpha/Beta/Omega garages

---

## 📚 Full Documentation

See `EXPERIMENTATION_GUIDE.md` for complete details on:
- All available APIs
- Strategy building
- Component library
- Testing frameworks
- Optimization tools

---

## 🆘 Quick Help

**Get live BTC price:**
```bash
python api_templates/binance_public_api.py
```

**Test a strategy:**
```bash
python sandboxes/strategy_sandbox.py
```

**Interactive API testing:**
```bash
python sandboxes/api_sandbox.py
```

---

## 🚀 Next Steps

1. Run `python sandboxes/api_sandbox.py` to see live crypto data
2. Run `python sandboxes/strategy_sandbox.py` to see example strategies
3. Read `EXPERIMENTATION_GUIDE.md` for full capabilities
4. Build your own strategy and test it!
5. When ready, deploy to production garages

---

**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Experimentation Lab Active

🧪 **Mix. Match. Test. Trade.**
