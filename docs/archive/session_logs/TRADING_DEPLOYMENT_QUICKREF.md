# 🚗 Trading Bot Deployment Quickref v25.5.OMNI

## ⚡ ONE-COMMAND DEPLOYMENT

```bash
# Complete ingestion + trading deployment
cd /data/mapping-and-inventory
./handshake_quickstart.sh all
```

This runs:
1. 🚪 KNOCK → GDrive
2. 💻 Local scan (hundreds of GB)
3. ☁️ GDrive scan (~20+ GB)
4. 🗂️ Persona filing
5. **🚗 Trading bot deployment**

---

## 🎯 GARAGE ACTIVATION

### Step 1: Generate Config

```bash
python3 scripts/activate_trading_garage.py
```

### Step 2: Add Secrets

```bash
cd Trading_Garages/Trading_Garage_Alpha/configs/
cp .env.template .env.local
nano .env.local
```

**Required:**
```bash
MEXC_API_KEY=your_key
MEXC_API_SECRET=your_secret
```

**Optional (Web3):**
```bash
TRADING_WALLET_PRIVATE_KEY=your_wallet_key
```

### Step 3: Verify

```bash
python3 activate_bots.py
```

---

## 📊 EXCHANGE CONFIGURATION

### MEXC (Live Trading)
- **Purpose:** Order execution
- **Features:** Spot, Futures, Margin
- **Endpoint:** https://api.mexc.com
- **Rate Limits:** 10 orders/sec

### Binance (Price Data)
- **Purpose:** Real-time prices ONLY
- **NO TRADING:** Public API
- **Endpoint:** https://api.binance.com
- **NO API Keys:** Public data

---

## 🌐 WEB3 NETWORKS

| Network  | Chain ID | RPC                              |
|----------|----------|----------------------------------|
| Ethereum | 1        | https://eth.llamarpc.com         |
| BSC      | 56       | https://bsc-dataseed.binance.org |
| Polygon  | 137      | https://polygon-rpc.com          |
| Arbitrum | 42161    | https://arb1.arbitrum.io/rpc     |
| Solana   | -        | https://api.mainnet-beta.solana.com |
| Base     | 8453     | https://mainnet.base.org         |

**DeFi:** Uniswap V3, PancakeSwap, Raydium

---

## 🛡️ SECURITY CHECKLIST

### MEXC
- [ ] Enable 2FA
- [ ] Set IP whitelist
- [ ] Disable withdrawals
- [ ] Start spot-only

### Secrets
- [ ] Never commit .env.local
- [ ] Use separate test keys
- [ ] Rotate keys monthly

### Web3
- [ ] Dedicated trading wallet
- [ ] Start with small amounts
- [ ] Test on testnet first

---

## 🎯 TRADING MODES

### Paper (Default)
```json
{
  "auto_trading": false,
  "paper_trading_mode": true
}
```

### Live (Production)
```json
{
  "auto_trading": true,
  "paper_trading_mode": false
}
```

**File:** `configs/trading_config.json`

---

## 📂 DIRECTORY STRUCTURE

```
Trading_Garages/
└── Trading_Garage_Alpha/
    ├── configs/
    │   ├── trading_config.json    # Main config
    │   ├── .env.local            # Your secrets
    │   └── activate_bots.py      # Activation
    ├── repos/                     # Bot repositories
    │   ├── omega_trader/
    │   ├── vanguard_trader/
    │   └── pioneer_trader/
    └── data/                      # Logs, performance
        ├── logs/
        └── performance/
```

---

## 🚀 RUN BOTS

### Paper Mode (Test)

```bash
cd Trading_Garages/Trading_Garage_Alpha/repos/omega_trader/
python3 omega_trader.py --mode=paper
```

### Live Mode (Real)

```bash
python3 omega_trader.py --mode=live
```

---

## 📊 MONITORING

### Logs

```bash
# Trading activity
tail -f data/logs/trading_*.log

# Errors
tail -f data/logs/errors_*.log
```

### Balance

```bash
# MEXC balance
python3 repos/omega_trader/check_balance.py --exchange=mexc

# Web3 balance
python3 repos/omega_trader/check_balance.py --chain=ethereum
```

### Performance

```bash
cat data/performance/summary.json | jq .
```

---

## ⚙️ RISK MANAGEMENT

**Defaults (ADJUST BEFORE LIVE):**
```json
{
  "max_position_size_usd": 1000,
  "max_total_exposure_usd": 5000,
  "stop_loss_percentage": 2.0,
  "take_profit_percentage": 5.0,
  "emergency_stop": {
    "max_daily_loss_usd": 500
  }
}
```

**Edit:** `configs/trading_config.json`

---

## 🚨 TROUBLESHOOTING

### MEXC Credentials Error
```bash
cd configs/
cp .env.template .env.local
nano .env.local  # Add keys
```

### Binance Rate Limit
- Use WebSocket for real-time data
- Add delays between requests

### Order Rejected
- Check API permissions
- Verify balance
- Check IP whitelist

### Web3 RPC Failed
- Try fallback RPCs
- Use premium provider (Infura/Alchemy)

---

## 📋 WORKFLOW

```
1. Vacuum     → Ingest all files
2. File       → Route to personas
3. Deploy     → Send to garages
4. Activate   → Generate config
5. Configure  → Add secrets
6. Test       → Paper mode
7. Live       → Real trading
```

---

## 📚 COMMANDS CHEAT SHEET

```bash
# Full deployment
./handshake_quickstart.sh all

# Activate garage
python3 scripts/activate_trading_garage.py

# Deploy bots only
python3 scripts/trading_bot_deployment_router.py

# Verify config
cd Trading_Garages/Trading_Garage_Alpha/configs/
python3 activate_bots.py

# View logs
tail -f data/logs/trading_*.log

# Check balance
python3 repos/*/check_balance.py
```

---

## 🎯 TRADING PAIRS

**Spot:**
- BTC/USDT, ETH/USDT
- SOL/USDT, XRP/USDT
- BNB/USDT

**Futures:**
- BTC/USDT:USDT
- ETH/USDT:USDT

**Edit:** `configs/trading_config.json`

---

## ⚠️ IMPORTANT

- **Start in paper mode** (simulated trades)
- **Test thoroughly** (1-2 weeks minimum)
- **Start small** ($10-50 positions)
- **Monitor regularly** (check logs daily)
- **Never risk more** than you can lose

---

## 📖 FULL DOCS

- [TRADING_BOT_DEPLOYMENT_GUIDE.md](TRADING_BOT_DEPLOYMENT_GUIDE.md)
- [CITADEL_OMEGA_ARCHITECTURE.md](CITADEL_OMEGA_ARCHITECTURE.md)
- Individual bot READMEs in repos/

---

**🦎 Weld. Pulse. Trade.**

*The Citadel Architect has armed all trading systems.*
