# 🚗 Trading Bot Deployment Guide v25.5.OMNI

**Authority:** Citadel Architect  
**Purpose:** Complete guide for deploying trading bots from vacuum → garage → live trading

---

## 📊 Overview

This system routes trading strategies and bots from ingestion to deployment with:
- **MEXC:** Live order execution with API secrets
- **Binance:** Real-time price data (public API only, NO trading)
- **Web3:** Blockchain integrations (ETH, BSC, Polygon, Arbitrum, Solana, Base)

---

## 🏗️ Architecture

```
Substrate Ingestion → Persona Filing → Trading Deployment → Live Trading
        ↓                    ↓                  ↓                ↓
Local/GDrive         Node_02 (Pioneer)   Trading Garages    MEXC Trading
                                              ↓                ↓
                                        Garage Alpha      Binance Prices
                                        Garage Beta       Web3 Chains
                                        Garage Omega      DeFi Protocols
```

---

## ⚡ Quick Start

### 1. Run Complete Ingestion + Deployment

```bash
cd /data/mapping-and-inventory
./handshake_quickstart.sh all
```

This executes:
1. KNOCK protocol → GDrive airlock
2. Local filesystem vacuum (hundreds of GB)
3. GDrive vacuum (~20+ GB)
4. Persona filing (Node_02 for trading data)
5. **Trading bot deployment to garages**

### 2. Activate Trading Garage

```bash
python3 scripts/activate_trading_garage.py
```

This generates:
- `trading_config.json` - Main configuration
- `.env.template` - Environment variable template
- `activate_bots.py` - Bot activation script
- `README.md` - Garage documentation

### 3. Configure Secrets

```bash
cd Trading_Garages/Trading_Garage_Alpha/configs/
cp .env.template .env.local
nano .env.local
```

**Add your credentials:**
```bash
MEXC_API_KEY=your_mexc_api_key
MEXC_API_SECRET=your_mexc_api_secret
TRADING_WALLET_PRIVATE_KEY=your_wallet_key  # Optional for Web3
```

### 4. Verify Configuration

```bash
python3 activate_bots.py
```

Expected output:
```
✅ MEXC credentials loaded
✅ Binance public API configured (price data only)
✅ Web3 wallet configured
Web3 Networks:
  ✅ ETHEREUM: https://eth.llamarpc.com
  ✅ BSC: https://bsc-dataseed.binance.org
  ✅ POLYGON: https://polygon-rpc.com
  ...
```

---

## 📁 Directory Structure

```
Trading_Garages/
├── GARAGE_INDEX.json                    # Master garage index
├── DEPLOYMENT_MANIFEST.json             # Deployment statistics
├── TRADING_GARAGE_GUIDE.md             # General garage guide
│
├── Trading_Garage_Alpha/               # Active trading bots
│   ├── README.md                       # Garage-specific guide
│   ├── MANIFEST.json                   # Bot manifest
│   ├── configs/                        # Configuration files
│   │   ├── trading_config.json        # Main config
│   │   ├── .env.template              # Secret template
│   │   ├── .env.local                 # Your secrets (gitignored)
│   │   ├── activate_bots.py           # Activation script
│   │   └── .gitignore                 # Protect secrets
│   ├── repos/                          # Deployed bot repos
│   │   ├── omega_trader/
│   │   ├── vanguard_trader/
│   │   └── pioneer_trader/
│   └── data/                           # Trading data
│       ├── logs/
│       ├── performance/
│       └── ledgers/
│
├── Trading_Garage_Beta/                # Backtesting tools
│   ├── repos/
│   └── configs/
│
└── Trading_Garage_Omega/               # Exchange connectors
    ├── repos/
    └── configs/
```

---

## 🔧 Exchange Configuration

### MEXC (Live Trading)

**Purpose:** Order execution  
**Features:** Spot, Futures, Margin  
**Endpoints:**
- REST: `https://api.mexc.com`
- WebSocket: `wss://wbs.mexc.com/ws`

**Rate Limits:**
- Orders: 10/second
- Requests: 1200/minute

**Required Environment Variables:**
```bash
MEXC_API_KEY=your_key
MEXC_API_SECRET=your_secret
```

**API Permissions:**
- ✅ Read account info
- ✅ Spot trading
- ✅ Futures trading (optional)
- ❌ Withdrawals (recommended disabled)

### Binance (Price Data Only)

**Purpose:** Real-time market data  
**Features:** Price feeds, orderbooks, klines, ticker  
**Endpoints:**
- REST: `https://api.binance.com`
- WebSocket: `wss://stream.binance.com:9443`

**Rate Limits:**
- Requests: 1200/minute
- Weight: 6000/minute

**Important:** 
- Public API only
- NO trading operations
- NO API keys needed
- Read-only price data

---

## 🌐 Web3 Integration

### Supported Networks

| Network  | Chain ID | RPC Endpoint                    | Explorer           |
|----------|----------|---------------------------------|--------------------|
| Ethereum | 1        | https://eth.llamarpc.com        | etherscan.io       |
| BSC      | 56       | https://bsc-dataseed.binance.org| bscscan.com        |
| Polygon  | 137      | https://polygon-rpc.com         | polygonscan.com    |
| Arbitrum | 42161    | https://arb1.arbitrum.io/rpc    | arbiscan.io        |
| Solana   | -        | https://api.mainnet-beta.solana.com | explorer.solana.com |
| Base     | 8453     | https://mainnet.base.org        | basescan.org       |

### DeFi Protocols

**Uniswap V3:**
- Networks: Ethereum, Polygon, Arbitrum, Base
- Features: Swap, liquidity, price oracles

**PancakeSwap:**
- Networks: BSC
- Features: Swap, liquidity, farms

**Raydium:**
- Networks: Solana
- Features: Swap, liquidity

### Wallet Configuration

```bash
TRADING_WALLET_PRIVATE_KEY=your_private_key
```

**Security:**
- Use dedicated trading wallet (not main wallet)
- Start with small test amounts
- Keep private key in environment variable only
- Consider hardware wallet for large amounts

---

## 🎯 Trading Workflow

### 1. Data Flow

```
Binance (Price) → Bot Logic → MEXC (Execute)
        ↓              ↓              ↓
  Real-time      Strategy      Order Sent
    Prices       Decision       to MEXC
```

### 2. Bot Execution

**Example: Omega Trader**

```bash
cd Trading_Garages/Trading_Garage_Alpha/repos/omega_trader/
python3 omega_trader.py --mode=paper  # Test first
python3 omega_trader.py --mode=live   # Live trading
```

### 3. Monitoring

**View logs:**
```bash
tail -f Trading_Garages/Trading_Garage_Alpha/data/logs/trading_*.log
```

**Check balance:**
```bash
python3 repos/omega_trader/check_balance.py
```

**Performance metrics:**
```bash
cat data/performance/metrics.json | jq .
```

---

## ⚙️ Configuration Files

### trading_config.json

Main configuration file with all settings:

```json
{
  "trading_mode": "LIVE",
  "exchanges": {
    "mexc": {
      "enabled": true,
      "purpose": "LIVE_TRADING",
      "features": ["spot", "futures"]
    },
    "binance": {
      "enabled": true,
      "purpose": "PRICE_FEED_ONLY"
    }
  },
  "web3": {
    "enabled": true,
    "networks": {
      "ethereum": { "enabled": true },
      "bsc": { "enabled": true },
      ...
    }
  },
  "risk_management": {
    "max_position_size_usd": 1000,
    "max_total_exposure_usd": 5000,
    "stop_loss_percentage": 2.0,
    "emergency_stop": {
      "max_daily_loss_usd": 500
    }
  }
}
```

### Risk Management

**Default limits (ADJUST BEFORE LIVE TRADING):**
- Max position: $1,000
- Max exposure: $5,000
- Stop loss: 2%
- Take profit: 5%
- Max daily trades: 50
- Emergency stop: $500 daily loss

**To adjust:**
```bash
nano configs/trading_config.json
# Edit "risk_management" section
```

---

## 🛡️ Security Checklist

### MEXC Account
- [ ] Enable 2FA (Google Authenticator)
- [ ] Set IP whitelist in API settings
- [ ] Enable withdrawal whitelist
- [ ] Limit API permissions (no withdrawals)
- [ ] Use read-only API for monitoring
- [ ] Start with spot trading only

### Environment Variables
- [ ] Never commit `.env.local` to git
- [ ] Use separate keys for test vs production
- [ ] Rotate API keys monthly
- [ ] Monitor API key usage in dashboard
- [ ] Set low withdrawal limits

### Web3 Wallet
- [ ] Use dedicated trading wallet
- [ ] Start with small test amounts ($10-50)
- [ ] Keep private key encrypted
- [ ] Consider hardware wallet for >$1000
- [ ] Test transactions on testnet first

---

## 📈 Trading Modes

### Paper Trading (Recommended Start)

```json
{
  "features": {
    "auto_trading": false,
    "paper_trading_mode": true
  }
}
```

**Behavior:**
- Simulates trades without real orders
- Uses real market data from Binance
- Logs all simulated trades
- Tests strategy logic safely

### Live Trading (Production)

```json
{
  "features": {
    "auto_trading": true,
    "paper_trading_mode": false
  }
}
```

**Behavior:**
- Executes real orders on MEXC
- Uses real capital
- Incurs trading fees
- Can result in profits or losses

**Transition:**
1. Test thoroughly in paper mode (1-2 weeks)
2. Review paper trading performance
3. Start with minimum position sizes
4. Gradually increase after confidence

---

## 🔍 Monitoring & Logging

### Real-time Logs

```bash
# Trading activity
tail -f data/logs/trading_$(date +%Y%m%d).log

# Error logs
tail -f data/logs/errors_$(date +%Y%m%d).log

# Performance logs
tail -f data/logs/performance_$(date +%Y%m%d).log
```

### Performance Metrics

```bash
# View daily performance
cat data/performance/daily_$(date +%Y%m%d).json | jq .

# View all-time performance
cat data/performance/summary.json | jq .
```

### Balance Checks

```bash
# MEXC balance
python3 repos/omega_trader/check_balance.py --exchange=mexc

# Web3 wallet balance
python3 repos/omega_trader/check_balance.py --chain=ethereum
```

---

## 🚨 Troubleshooting

### "MEXC credentials not found"
**Solution:**
```bash
cd Trading_Garages/Trading_Garage_Alpha/configs/
cp .env.template .env.local
nano .env.local  # Add credentials
```

### "Binance rate limit exceeded"
**Solution:**
- Add delays between requests
- Use WebSocket for real-time data
- Implement exponential backoff
- Consider premium Binance API

### "Order rejected by MEXC"
**Solution:**
- Check API permissions
- Verify account balance
- Check IP whitelist
- Review order size limits
- Check MEXC maintenance schedule

### "Web3 RPC connection failed"
**Solution:**
- Try fallback RPCs in config
- Use premium RPC (Infura, Alchemy)
- Check network is not congested
- Verify RPC endpoint is online

### "Bot stops unexpectedly"
**Solution:**
- Check logs: `tail -f data/logs/errors_*.log`
- Verify API keys are valid
- Check network connectivity
- Review exception handling in bot code

---

## 📚 Additional Scripts

### Deploy Trading Bots

```bash
# Deploy from ingestion to garages
python3 scripts/trading_bot_deployment_router.py
```

### Activate Garage

```bash
# Generate configuration files
python3 scripts/activate_trading_garage.py
```

### Collect Bots from Repos

```bash
# Clone trading repos to garage
python3 scripts/trading_garage_collector.py
```

---

## 🎯 Common Use Cases

### 1. DCA Bot (Dollar Cost Averaging)

```bash
cd repos/dca_bot/
python3 dca_bot.py --pair=BTC/USDT --amount=100 --interval=daily
```

### 2. Grid Trading

```bash
cd repos/grid_trader/
python3 grid_trader.py --pair=ETH/USDT --grids=10 --range=5%
```

### 3. Arbitrage Bot

```bash
cd repos/arbitrage_bot/
python3 arbitrage_bot.py --exchanges=mexc,binance --min-profit=0.5%
```

### 4. Web3 Sniping

```bash
cd repos/web3_sniper/
python3 sniper.py --chain=ethereum --dex=uniswap --token=0x...
```

---

## 📖 Related Documentation

- [CITADEL_OMEGA_ARCHITECTURE.md](../../CITADEL_OMEGA_ARCHITECTURE.md)
- [TRADING_GARAGE_GUIDE.md](Trading_Garages/TRADING_GARAGE_GUIDE.md)
- [PROTOCOL_HANDSHAKE_GUIDE.md](PROTOCOL_HANDSHAKE_GUIDE.md)
- Individual bot READMEs in `repos/*/`

---

## ⚠️ Disclaimer

**Important:** Trading cryptocurrencies involves substantial risk of loss. This system is provided for educational and automation purposes only. Always:

- Start with paper trading
- Test thoroughly before live trading
- Never trade with more than you can afford to lose
- Understand the risks of automated trading
- Review and adjust risk management settings
- Monitor bots regularly
- Keep API keys secure

The Citadel Architect provides tools, but trading decisions and risk are solely yours.

---

**🦎 Weld. Pulse. Trade.**

*Status: Trading Garage System Operational*  
*Authority: Citadel Architect v25.5.OMNI*
