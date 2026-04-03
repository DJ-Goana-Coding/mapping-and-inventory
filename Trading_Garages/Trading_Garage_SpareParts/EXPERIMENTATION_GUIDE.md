# 🧪 Trading Experimentation Lab - Complete Guide

**Purpose:** Complete trading development environment with APIs, strategies, and testing tools

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Test real-time crypto APIs (no secrets!)
python sandboxes/api_sandbox.py

# 2. Build and test a strategy
python sandboxes/strategy_sandbox.py

# 3. Explore components
ls -R components/
```

---

## 📦 What's Inside

### 🔌 API Templates (No Secrets Required!)

All API templates use **public endpoints only** - no API keys needed for testing!

```
api_templates/
├── binance_public_api.py      # Binance market data
├── generic_crypto_api.py      # Multi-exchange support
└── ... (more coming)
```

**Example - Get Live BTC Price:**
```python
from api_templates.binance_public_api import BinancePublicAPI

api = BinancePublicAPI()
price = api.get_ticker_price("BTCUSDT")
print(f"BTC: ${price:,.2f}")
```

**Supported Data (No Auth):**
- ✅ Real-time prices
- ✅ 24-hour statistics
- ✅ Order books
- ✅ Recent trades
- ✅ Historical candles (OHLCV)
- ✅ Exchange info

### 🎯 Strategy Templates

Reusable building blocks for creating trading strategies:

```
strategy_templates/
├── indicators/
│   ├── moving_average.py
│   ├── rsi.py
│   ├── macd.py
│   └── bollinger_bands.py
├── signals/
│   ├── crossover.py
│   ├── breakout.py
│   └── divergence.py
└── risk_management/
    ├── stop_loss.py
    ├── take_profit.py
    └── position_sizing.py
```

**Example - Build Strategy:**
```python
from strategy_templates import Strategy, MovingAverage, RSI

strategy = Strategy("My Strategy")
strategy.add_indicator(MovingAverage(20))
strategy.add_indicator(RSI(14))
results = strategy.backtest(historical_data)
```

### 🧪 Sandboxes

Interactive testing environments:

```
sandboxes/
├── api_sandbox.py           # Test crypto APIs
├── strategy_sandbox.py      # Build/test strategies
├── backtest_sandbox.py      # Historical testing
└── paper_trade_sandbox.py   # Live paper trading
```

**Run API Sandbox:**
```bash
cd sandboxes/
python api_sandbox.py

# Interactive mode - try commands:
api> price BTCUSDT
api> compare ETHUSDT
api> book BTCUSDT
```

**Run Strategy Sandbox:**
```bash
python strategy_sandbox.py

# See 3 example strategies:
# 1. MA Crossover
# 2. RSI Strategy
# 3. Combined MA + RSI
```

### 📓 Notebooks

Jupyter/Colab notebooks for interactive development:

```
notebooks/
├── trading_playground.ipynb     # Interactive strategy builder
├── api_testing.ipynb            # API exploration
├── backtest_lab.ipynb          # Strategy backtesting
├── indicator_explorer.ipynb    # Technical indicators
└── risk_calculator.ipynb       # Position sizing
```

**Launch Notebook:**
```bash
cd notebooks/
jupyter notebook trading_playground.ipynb
```

### 🔧 Components

Modular code pieces for mix-and-match:

```
components/
├── indicators/      # Technical indicators
├── signals/         # Signal generators
├── strategies/      # Complete strategies
├── backtesting/     # Testing engines
├── risk/            # Risk management
└── utils/           # Utilities
```

### 📚 Examples

Working examples and demos:

```
examples/
├── simple_ma_strategy.py
├── rsi_strategy.py
├── arbitrage_detector.py
├── paper_trader.py
└── live_price_monitor.py
```

---

## 🎨 Mix & Match Workflow

### Step 1: Choose Components

```python
# Pick indicators
from components.indicators import MovingAverage, RSI, MACD

# Pick signal generators
from components.signals import CrossoverSignal, RSISignal

# Pick risk management
from components.risk import StopLoss, TakeProfit
```

### Step 2: Build Strategy

```python
strategy = Strategy("My Custom Strategy")

# Add indicators
strategy.add_indicator(MovingAverage(20))
strategy.add_indicator(RSI(14))

# Add signals
strategy.add_signal(CrossoverSignal("MA(5)", "MA(20)"))
strategy.add_signal(RSISignal(oversold=30, overbought=70))

# Add risk management
strategy.add_risk(StopLoss(percent=2))
strategy.add_risk(TakeProfit(percent=5))
```

### Step 3: Test in Sandbox

```python
# Quick test with mock data
results = strategy.test(mock_data)

# Or backtest with real historical data
from api_templates.binance_public_api import BinancePublicAPI

api = BinancePublicAPI()
historical = api.get_klines("BTCUSDT", "1h", limit=1000)
results = strategy.backtest(historical)
```

### Step 4: Paper Trade

```python
# Test with live data (no real money)
from sandboxes.paper_trade_sandbox import PaperTrader

trader = PaperTrader(initial_balance=10000)
trader.run_strategy(strategy, symbol="BTCUSDT")
```

### Step 5: Deploy to Production

Once tested and optimized, move to production garages:
- **Alpha** - Active production bots
- **Beta** - Monitored beta testing
- **Omega** - Live exchange connections

---

## 🔐 Security & Secrets

### Spare Parts Garage = NO SECRETS!

This garage uses:
- ✅ Public API endpoints (no auth)
- ✅ Test/demo data only
- ✅ Paper trading (simulated)
- ✅ Sandbox environments

### For Real Trading:

Move to production garages and use:
- 🔒 Secret management (GitHub Secrets, env vars)
- 🔒 API key authentication
- 🔒 Wallet security
- 🔒 Production monitoring

**Never commit secrets to Spare Parts garage!**

---

## 📊 Available APIs (Public Endpoints)

### Binance Public API

```python
from api_templates.binance_public_api import BinancePublicAPI

api = BinancePublicAPI()

# Get price
price = api.get_ticker_price("BTCUSDT")

# Get 24h stats
stats = api.get_24h_ticker("BTCUSDT")

# Get order book
book = api.get_orderbook("BTCUSDT", limit=10)

# Get recent trades
trades = api.get_recent_trades("BTCUSDT")

# Get historical candles
candles = api.get_klines("BTCUSDT", "1h", limit=100)
```

### Generic Multi-Exchange API

```python
from api_templates.generic_crypto_api import GenericCryptoAPI

# Compare prices across exchanges
api = GenericCryptoAPI()
prices = api.compare_prices("BTCUSDT")

for exchange, price in prices.items():
    print(f"{exchange}: ${price}")

# Find arbitrage opportunities
arb = api.find_arbitrage("BTCUSDT", min_diff_percent=0.5)
if arb:
    print(f"Buy from {arb['buy_from']}, sell to {arb['sell_to']}")
    print(f"Profit: {arb['profit_percent']}%")
```

---

## 🧪 Testing Frameworks

### Backtesting

```python
from components.backtesting import Backtester

backtester = Backtester()
backtester.load_data("BTCUSDT", start="2024-01-01", end="2024-12-31")
results = backtester.run(strategy)

print(f"Total Return: {results['return']}%")
print(f"Win Rate: {results['win_rate']}%")
print(f"Sharpe Ratio: {results['sharpe']}")
```

### Paper Trading

```python
from sandboxes.paper_trade_sandbox import PaperTrader

trader = PaperTrader(initial_balance=10000)
trader.set_strategy(strategy)
trader.start()  # Runs with live data, simulated execution
```

### Strategy Optimization

```python
from components.optimization import GridSearch

optimizer = GridSearch(strategy)
optimizer.add_param("ma_period", [10, 20, 30, 50])
optimizer.add_param("rsi_period", [7, 14, 21])

best_params = optimizer.find_best(historical_data)
print(f"Best parameters: {best_params}")
```

---

## 🎯 Example Strategies

### 1. Simple MA Crossover

```python
strategy = Strategy("MA Crossover")
strategy.add_indicator(MovingAverage(5))
strategy.add_indicator(MovingAverage(20))
strategy.add_signal(CrossoverSignal("MA(5)", "MA(20)"))
```

### 2. RSI Mean Reversion

```python
strategy = Strategy("RSI Mean Reversion")
strategy.add_indicator(RSI(14))
strategy.add_signal(RSISignal(oversold=30, overbought=70))
strategy.add_risk(StopLoss(2))
```

### 3. Multi-Timeframe

```python
strategy = Strategy("Multi-Timeframe")
strategy.add_indicator(MovingAverage(20, timeframe="1h"))
strategy.add_indicator(MovingAverage(50, timeframe="4h"))
strategy.add_indicator(RSI(14, timeframe="1h"))
strategy.add_signal(MultiTimeframeSignal())
```

### 4. Arbitrage Bot

```python
from examples.arbitrage_detector import ArbitrageStrategy

strategy = ArbitrageStrategy()
strategy.add_exchange("binance")
strategy.add_exchange("coinbase")
strategy.set_min_profit(0.5)  # 0.5% minimum
opportunities = strategy.scan()
```

---

## 🛠️ Adding Your Own Components

### Create Custom Indicator

```python
# components/indicators/my_indicator.py
class MyIndicator:
    def __init__(self, period):
        self.period = period
    
    def calculate(self, prices):
        # Your calculation logic
        return result
```

### Create Custom Signal

```python
# components/signals/my_signal.py
class MySignal:
    def generate(self, prices, indicators):
        signals = []
        for i in range(len(prices)):
            # Your signal logic
            if condition:
                signals.append("BUY")
            else:
                signals.append("HOLD")
        return signals
```

### Create Custom Strategy

```python
# strategy_templates/my_strategy.py
from components import Strategy, MovingAverage, RSI

class MyStrategy(Strategy):
    def __init__(self):
        super().__init__("My Strategy")
        self.add_indicator(MovingAverage(20))
        self.add_indicator(RSI(14))
        # Your custom logic
```

---

## 📈 Next Steps

1. **Explore** - Browse all components and examples
2. **Test** - Run sandboxes and notebooks
3. **Build** - Create your own strategies
4. **Backtest** - Validate with historical data
5. **Paper Trade** - Test with live data (no risk)
6. **Optimize** - Fine-tune parameters
7. **Deploy** - Move to production garages

---

## 🆘 Troubleshooting

### API Errors

**Problem:** Connection timeout  
**Solution:** Check internet connection, try different exchange

**Problem:** Symbol not found  
**Solution:** Verify symbol format (e.g., "BTCUSDT" not "BTC-USD")

### Strategy Errors

**Problem:** Not enough data for indicators  
**Solution:** Increase historical data limit or reduce indicator period

**Problem:** Backtest shows no trades  
**Solution:** Check signal conditions, adjust parameters

### Sandbox Issues

**Problem:** Module not found  
**Solution:** Run from correct directory or adjust `sys.path`

---

## 📚 Resources

- Binance API Docs: https://binance-docs.github.io/apidocs/
- Technical Indicators: https://www.investopedia.com/
- Python Trading Libraries: pandas, numpy, ta-lib

---

**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Experimentation Lab Active  
**Version:** 1.0.0

🧪 **Build. Test. Learn. Trade.**
