# 🛡️ TRADING SAFETY INFRASTRUCTURE - Operator Manual

**Version:** 1.0.0  
**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Production-Ready with Safety Guardrails

---

## ⚠️ CRITICAL: READ BEFORE LIVE TRADING

This system implements comprehensive safety infrastructure to prevent catastrophic trading losses. **NEVER** bypass these safety systems.

### Safety Systems Overview

1. **Circuit Breaker** - Automatically halts trading on dangerous conditions
2. **Credential Manager** - Securely manages API keys and validates connectivity
3. **Risk Monitor** - Tracks risk levels and generates alerts
4. **Performance Monitor** - Tracks P&L, win rate, and trading metrics
5. **Health Monitor** - Checks trader uptime and API connectivity
6. **Recovery Agent** - Handles failures and operator notifications

---

## 📋 Quick Start Guide

### Step 1: Set Environment Variables

All secrets must be in environment variables or GitHub Secrets. **NEVER** hardcode credentials.

```bash
# MEXC Trading Credentials (REQUIRED for live trading)
export MEXC_API_KEY="your_mexc_api_key"
export MEXC_API_SECRET="your_mexc_secret_key"

# Trading Capital (Default: $1000)
export TRADING_CAPITAL="1000.0"

# Live Trading Enable (Default: false)
export LIVE_TRADING_ENABLED="false"  # Set to "true" for live trading

# Circuit Breaker Reset Code (for manual resets)
export CIRCUIT_BREAKER_RESET_CODE="RESET_AUTHORIZED"

# Optional: Web3 Wallet Credentials
export TRADING_WALLET_ADDRESS="0x..."
export TRADING_WALLET_PRIVATE_KEY="..."
```

### Step 2: Validate Credentials

Before live trading, validate your credentials:

```bash
cd /home/runner/work/mapping-and-inventory/mapping-and-inventory
python3 scripts/trading_safety/credential_manager.py
```

Expected output:
```
🔐 Credential Manager Test

MEXC Load: ✅ MEXC credentials loaded successfully
MEXC Validate: ✅ MEXC credentials validated successfully
MEXC Balance: $1234.56 USDT
```

### Step 3: Initialize Circuit Breaker

Test the circuit breaker system:

```bash
python3 scripts/trading_safety/circuit_breaker.py
```

Expected output:
```
🛡️  Circuit Breaker System Test

Status: NORMAL
Capital: $1000.00
Daily Loss: $0.00 (0.00%)
Active Positions: 0

✅ Circuit breaker initialized successfully
```

### Step 4: Test Safe Trader (Paper Mode)

Always test in paper mode first:

```bash
# Ensure LIVE_TRADING_ENABLED=false
export LIVE_TRADING_ENABLED="false"

python3 scripts/trading_safety/safe_trader.py
```

This will execute a simulated trade and show you the system works.

### Step 5: Enable Live Trading (CAREFULLY)

Only after successful paper trading:

```bash
# Enable live trading
export LIVE_TRADING_ENABLED="true"

# Start with ONE trader on ONE strategy
python3 Districts/D04_OMEGA_TRADER/vanguard_live_trader_v2.py
```

---

## 🔧 Circuit Breaker Configuration

Default safety limits (configured in `data/trading_safety/circuit_breaker_config.json`):

### Loss Limits
- **Max trade loss:** 2% of capital per trade
- **Max daily loss:** 10% of capital per day
- **Max weekly loss:** 20% of capital per week
- **Emergency shutdown:** 25% total capital loss

### Position Limits
- **Max position size:** 10% of capital per position
- **Max total exposure:** 50% of capital
- **Max simultaneous positions:** 5 trades at once

### Rapid Loss Protection
- **Max consecutive losses:** 3 in a row
- **Max losses per hour:** 5 losses in 1 hour

### To Modify Limits

Edit `data/trading_safety/circuit_breaker_config.json`:

```json
{
  "max_trade_loss_percent": 2.0,
  "max_daily_loss_percent": 10.0,
  "max_position_size_percent": 10.0,
  "max_simultaneous_positions": 5,
  "emergency_loss_percent": 25.0
}
```

---

## 🚨 Circuit Breaker Trips

### What Happens When Circuit Breaker Trips

1. **All trading immediately halts**
2. **Alert is logged** to `data/trading_safety/circuit_breaker_log.json`
3. **Status changes to TRIPPED**
4. **Operator notification sent**

### How to Reset Circuit Breaker

Circuit breaker trips require manual operator reset:

```python
from scripts.trading_safety.circuit_breaker import CircuitBreaker

breaker = CircuitBreaker()
success, msg = breaker.reset("RESET_AUTHORIZED")  # Use your reset code
print(msg)
```

Or set the reset code and run:

```bash
export CIRCUIT_BREAKER_RESET_CODE="RESET_AUTHORIZED"
python3 -c "from scripts.trading_safety.circuit_breaker import CircuitBreaker; cb=CircuitBreaker(); print(cb.reset('RESET_AUTHORIZED'))"
```

---

## 📊 Monitoring & Alerts

### Check System Status

```bash
python3 scripts/trading_safety/trading_monitors.py
```

This runs all monitoring agents:
- Health Monitor
- Performance Monitor
- Risk Monitor  
- Recovery Agent

### Monitoring Reports Location

All monitoring data is saved to `data/trading_monitoring/`:

```
data/trading_monitoring/
├── health_status.json          # Trader health checks
├── performance_metrics.json    # Trading performance
├── risk_alerts.json            # Risk alerts
├── recovery_log.json           # Recovery actions
├── trade_history.json          # Complete trade history
└── monitoring_report.json      # Full monitoring report
```

### Risk Levels

- **LOW:** Normal trading conditions
- **MEDIUM:** Warning - elevated risk detected
- **HIGH:** Critical - immediate attention required

### Common Alerts

1. **CAPITAL_LOSS** - Capital loss exceeds thresholds
2. **CONSECUTIVE_LOSSES** - Multiple losing trades in a row
3. **LOW_WIN_RATE** - Win rate below 40%
4. **HIGH_DRAWDOWN** - Excessive drawdown detected

---

## 🎯 Trading Strategies

Available strategies from `data/trading_strategies/strategy_library.json`:

### Low Risk (Recommended for Start)
- **Moving Average Crossover** - Golden/death cross
- **Simple Arbitrage** - Price differences between exchanges

### Medium Risk
- **RSI Mean Reversion** - Buy oversold, sell overbought
- **MACD Crossover** - Trade MACD signals

### High Risk (Avoid Until Proven)
- **LSTM Price Prediction** - ML-based price forecasting
- **Sentiment Trading** - Social sentiment-based trading

### Strategy Assignment

Strategies are assigned in trader code:

```python
from scripts.trading_safety.safe_trader import SafeTrader

trader = SafeTrader("trader_01")

trade_result = trader.execute_trade({
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.001,
    "price": 50000.0,
    "strategy": "MA_CROSSOVER"  # Strategy name
})
```

---

## 🔄 Gradual Rollout Protocol

**NEVER enable all traders at once.** Follow this protocol:

### Week 1: Single Strategy Test
1. Enable ONE trader
2. Run ONE strategy (MA Crossover recommended)
3. Trade ONE asset (BTCUSDT or ETHUSDT)
4. Micro position size (1-2% of capital)
5. Monitor 24-48 hours continuously

### Week 2: Validation
1. If profitable and stable, add SECOND strategy
2. Still single trader, single asset
3. Increase position size to 5% max
4. Monitor for another 48 hours

### Month 2: Scaling
1. If consistently profitable, add second asset
2. Enable second trader
3. Increase to normal position sizing (10% max)
4. Continue monitoring

### Red Flags - STOP IMMEDIATELY
- Win rate < 40% after 20+ trades
- Total capital loss > 15%
- More than 3 consecutive losses
- Any circuit breaker trip

---

## 🛠️ Updating Existing Traders

All existing traders should be updated to use `SafeTrader`:

### Before (Unsafe)
```python
# OLD - Direct trading without safety
execute_trade(symbol, side, quantity)
```

### After (Safe)
```python
# NEW - With full safety infrastructure
from scripts.trading_safety.safe_trader import SafeTrader

trader = SafeTrader("trader_id")
result = trader.execute_trade({
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.001,
    "price": 50000.0,
    "strategy": "MA_CROSSOVER"
})
```

---

## 📈 Performance Metrics

Track these metrics in `data/trading_monitoring/performance_metrics.json`:

- **Total Trades:** Number of trades executed
- **Win Rate:** Percentage of profitable trades
- **Total P&L:** Cumulative profit/loss
- **Average Win:** Average profit per winning trade
- **Average Loss:** Average loss per losing trade
- **Profit Factor:** Gross profit / Gross loss
- **Max Drawdown:** Largest peak-to-trough decline
- **Sharpe Ratio:** Risk-adjusted returns (higher is better)

### Minimum Performance Standards

Before scaling up, ensure:
- Win rate > 50%
- Profit factor > 1.5
- Max drawdown < 15%
- Sharpe ratio > 1.0

---

## 🚀 GitHub Actions Workflow

Automated monitoring via GitHub Actions (runs every 6 hours):

```yaml
name: Trading Safety Monitor
on:
  schedule:
    - cron: "0 */6 * * *"  # Every 6 hours
  workflow_dispatch:  # Manual trigger

jobs:
  monitor:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Run Safety Monitors
        env:
          MEXC_API_KEY: ${{ secrets.MEXC_API_KEY }}
          MEXC_API_SECRET: ${{ secrets.MEXC_API_SECRET }}
          TRADING_CAPITAL: ${{ secrets.TRADING_CAPITAL }}
        run: |
          python3 scripts/trading_safety/trading_monitors.py
      
      - name: Check Circuit Breaker
        run: |
          python3 scripts/trading_safety/circuit_breaker.py
      
      - name: Commit Monitoring Reports
        run: |
          git config user.name "Trading Monitor"
          git add data/trading_monitoring/
          git commit -m "Update trading monitoring reports" || true
          git push || true
```

---

## ⚠️ Emergency Procedures

### Emergency Shutdown

If something goes wrong:

```bash
# 1. Set live trading to false
export LIVE_TRADING_ENABLED="false"

# 2. Kill all trader processes
pkill -f "trader"

# 3. Check circuit breaker status
python3 scripts/trading_safety/circuit_breaker.py

# 4. Review logs
cat data/trading_safety/circuit_breaker_log.json
cat data/trading_monitoring/risk_alerts.json
```

### Data Recovery

All critical data is in `data/trading_safety/` and `data/trading_monitoring/`:

```bash
# Backup all trading data
cp -r data/trading_safety/ backup_$(date +%Y%m%d)/
cp -r data/trading_monitoring/ backup_$(date +%Y%m%d)/
```

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue:** "MEXC credentials not found"  
**Solution:** Ensure `MEXC_API_KEY` and `MEXC_API_SECRET` environment variables are set

**Issue:** "Circuit breaker TRIPPED"  
**Solution:** Review trip reason, address the issue, then manually reset with authorization code

**Issue:** "Trade BLOCKED"  
**Solution:** Check circuit breaker status - likely hit a safety limit

### Logs Location

- Circuit breaker: `data/trading_safety/circuit_breaker_log.json`
- Credentials: `data/trading_safety/credential_audit.json`
- Monitoring: `data/trading_monitoring/monitoring_report.json`
- Risk alerts: `data/trading_monitoring/risk_alerts.json`
- Trade history: `data/trading_monitoring/trade_history.json`

---

## ✅ Pre-Flight Checklist

Before enabling live trading:

- [ ] MEXC API credentials validated
- [ ] Circuit breaker initialized and status is NORMAL
- [ ] Trading capital configured correctly
- [ ] Tested in paper mode successfully for 7+ days
- [ ] Win rate > 50% in paper trading
- [ ] Monitoring agents running
- [ ] Risk alerts configured
- [ ] Emergency shutdown procedure tested
- [ ] Backup of all configuration files
- [ ] Operator manual read and understood
- [ ] Starting with SINGLE strategy on SINGLE asset
- [ ] Position size < 5% of capital for first week
- [ ] Continuous monitoring plan in place

---

## 🎯 Success Criteria

Before scaling to full live trading:

**Week 1:**
- [ ] 0 circuit breaker trips
- [ ] 0 credential failures
- [ ] Win rate > 45%
- [ ] Max drawdown < 5%

**Month 1:**
- [ ] Win rate > 50%
- [ ] Profit factor > 1.5
- [ ] Max drawdown < 10%
- [ ] Total P&L > 0

**Month 3:**
- [ ] Consistent profitability
- [ ] Win rate > 55%
- [ ] Sharpe ratio > 1.0
- [ ] Ready to scale

---

## 📚 Additional Resources

- **Circuit Breaker Code:** `scripts/trading_safety/circuit_breaker.py`
- **Credential Manager:** `scripts/trading_safety/credential_manager.py`
- **Safe Trader:** `scripts/trading_safety/safe_trader.py`
- **Monitoring Agents:** `scripts/trading_safety/trading_monitors.py`
- **Strategy Library:** `data/trading_strategies/strategy_library.json`

---

**Remember:** The goal is sustainable, profitable trading - not reckless speed. Safety systems exist to protect capital. Never bypass them.

**Citadel Architect v25.0.OMNI+**  
*Cloud-First Authority. Forever Learning. Zero Tolerance for Recklessness.*
