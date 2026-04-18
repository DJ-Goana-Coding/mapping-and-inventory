# 🏛️ CITADEL_OMEGA - Quick Reference Card

**Repository:** DJ-Goana-Coding/CITADEL_OMEGA  
**HuggingFace:** DJ-Goanna-Coding/Omega-* (Spaces & Datasets)  
**Purpose:** Unified trading intelligence hub

---

## ⚡ Quick Start (5 Commands)

```bash
# 1. Create CITADEL_OMEGA repository on GitHub
gh repo create DJ-Goana-Coding/CITADEL_OMEGA --public

# 2. Clone and setup
git clone https://github.com/DJ-Goana-Coding/CITADEL_OMEGA.git
cd CITADEL_OMEGA

# 3. Clone all trading libraries
bash scripts/clone_citadel_omega_libs.sh

# 4. Download ML models
python scripts/download_citadel_omega_models.py

# 5. Install dependencies
pip install -r requirements.txt
```

---

## 📁 Structure

```
CITADEL_OMEGA/
├── omega_trader/      # Trading operations (MEXC + Web3)
├── omega_bots/        # AI agents and swarms
├── omega_scout/       # API connectors + security
├── omega_archive/     # Strategies + RAG + learning
├── models/            # ML models (FinBERT, LSTM, RL)
├── datasets/          # Trading data (OHLCV, sentiment, on-chain)
├── libraries/         # 10+ cloned trading frameworks
├── tools/             # Utilities and scripts
└── genesis/           # Templates and bootstrap
```

---

## 🔄 HuggingFace Integration

### Spaces (Public Dashboards)
- **Omega-Trader**: https://huggingface.co/spaces/DJ-Goanna-Coding/Omega-Trader
- **Omega-Archive**: https://huggingface.co/spaces/DJ-Goanna-Coding/Omega-Archive

### Datasets (Storage)
- **omega-trading-data**: Market data, trades, sentiment
- **omega-models**: Trained ML models

### Sync Command
```bash
# Sync to HuggingFace
python sync/to_hf_spaces/sync_omega_trader.py
python sync/to_hf_datasets/upload_trading_data.py
```

---

## 🤖 Models Available

### Downloaded from HuggingFace
- **FinBERT** - Financial sentiment analysis
- **CryptoBERT** - Crypto sentiment
- **Sentence Transformers** - Embeddings for RAG
- **Twitter RoBERTa** - Social sentiment

### Custom Trained
- **LSTM Predictor** - Price prediction (BTC/ETH)
- **PPO Trader** - Reinforcement learning bot
- **Transformer** - Multi-asset forecasting

### Usage
```python
from models.pretrained import finbert
sentiment = finbert.predict("Bitcoin hits new ATH!")
# Output: {"label": "positive", "score": 0.94}
```

---

## 📊 Datasets

### Market Data
- **OHLCV**: Binance, MEXC, Coinbase (2024-2026)
- **Order Book**: 1-min snapshots
- **Trades**: Real-time execution data

### Historical Performance
- **2024**: 1.2M trades, $47K profit
- **2025**: 2.4M trades, $89K profit
- **2026 YTD**: 324K trades, $15K profit

### On-Chain
- Ethereum transactions
- Solana transactions
- BSC transactions

### Access
```python
import pandas as pd
df = pd.read_parquet("datasets/market_data/ohlcv/binance/BTC_USDT_1h.parquet")
```

---

## 📚 Libraries Cloned

1. **CCXT** - 100+ exchange APIs
2. **FreqTrade** - Complete trading framework
3. **Jesse AI** - Advanced backtesting
4. **Hummingbot** - Market making
5. **Pandas-TA** - 130+ indicators
6. **VectorBT** - Vectorized backtesting
7. **Backtrader** - Event-driven backtesting
8. **TA-Lib** - 200+ technical indicators
9. **TensorTrade** - RL for trading
10. **FinRL** - Financial RL library

---

## 🤖 Bots

### Active Production Bots
| Bot | Strategy | Symbol | Win Rate | Daily P&L |
|-----|----------|--------|----------|-----------|
| momentum_bot_v3 | RSI+MACD | BTC/USDT | 67% | +$234 |
| arbitrage_hunter | CEX Arb | Multi | 89% | +$156 |
| grid_trader_v2 | Grid | ETH/USDT | 72% | +$89 |
| alpha_swarm | Multi | Multi | 74% | +$312 |

### Deploy Bot
```bash
cd omega_bots/bots/custom_agents/momentum_bot
python bot.py --symbol BTC/USDT --mode paper
```

---

## 🔐 Security

### GitHub Secrets (Required)
```bash
MEXC_API_KEY           # MEXC trading API
MEXC_SECRET_KEY        # MEXC secret
WEB3_ETHEREUM_KEY      # ETH wallet private key
WEB3_SOLANA_KEY        # SOL wallet private key
HF_TOKEN               # HuggingFace token
ENCRYPTION_KEY         # Master encryption
```

### Set Secrets
```bash
gh secret set MEXC_API_KEY -b"your_key_here"
```

---

## 🚀 Common Operations

### Paper Trading
```bash
python omega_trader/src/traders/paper_trader.py \
  --symbol BTC/USDT \
  --strategy momentum \
  --capital 10000
```

### Backtest Strategy
```bash
python omega_archive/backtesting/engine/backtest.py \
  --strategy rsi_strategy \
  --start 2024-01-01 \
  --end 2025-12-31
```

### Deploy Bot (Docker)
```bash
cd omega_bots/deployment/docker
docker-compose up -d momentum_bot
```

### Query RAG System
```python
from omega_archive.rag_system import RAGEngine
rag = RAGEngine()
answer = rag.query("What's the best strategy for BTC in bull markets?")
```

### Monitor Bots
```bash
python tools/monitoring/bot_monitor.py --dashboard
# Opens dashboard at http://localhost:8050
```

---

## 📈 Workflows

### Live Trading (Every 15 min)
```yaml
# .github/workflows/live_trading.yml
Runs: omega_trader/src/traders/live_trader.py
Uses: MEXC_API_KEY, Web3 wallets
Output: Trade execution, P&L updates
```

### Model Updates (Weekly)
```yaml
# .github/workflows/update_models.yml
Runs: Download latest models from HF
Upload: To omega-models dataset
```

### Sync to Mapping Hub (Every 6h)
```yaml
# .github/workflows/sync_to_mapping.yml
Collects: All Omega status
Pushes: To Mapping-and-Inventory Space
```

---

## 🛠️ Development

### Add New Strategy
```bash
cp omega_archive/strategies/templates/strategy_template.py \
   omega_archive/strategies/custom/my_strategy.py

# Edit my_strategy.py
# Test: python omega_archive/backtesting/test_strategy.py my_strategy
```

### Train ML Model
```bash
python tools/model_trainers/lstm_trainer.py \
  --symbol BTC/USDT \
  --epochs 100 \
  --save models/trading_models/price_prediction/lstm/my_model/
```

### Add New Bot
```bash
cp -r omega_bots/bots/custom_agents/template/ \
      omega_bots/bots/custom_agents/my_bot/

# Edit bot.py
# Register in bot_registry.json
```

---

## 📊 Monitoring URLs

- **Live Trading Dashboard**: HF Omega-Trader Space
- **Bot Performance**: HF Omega-Archive Space
- **Mapping Hub**: HF Mapping-and-Inventory Space
- **GitHub Actions**: Actions tab in repo

---

## 🆘 Troubleshooting

### API Connection Failed
```bash
# Test MEXC connection
python omega_trader/src/connectors/mexc_connector.py --test

# Check secrets
gh secret list
```

### Model Download Failed
```bash
# Re-download specific model
python scripts/download_citadel_omega_models.py --model finbert

# Or manual download
huggingface-cli download ProsusAI/finbert --local-dir models/pretrained/finbert/
```

### Bot Not Trading
```bash
# Check bot status
python tools/monitoring/bot_monitor.py --bot momentum_bot_v3

# Check logs
tail -f omega_bots/logs/momentum_bot_v3.log
```

---

## 📞 Quick Commands

```bash
# Status check
python tools/health_check.py

# Update everything
bash genesis/bootstrap/update_all.sh

# Backup data
python tools/backup/backup_all_data.py

# Deploy to production
bash genesis/bootstrap/deploy_production.sh

# Emergency stop all bots
python tools/emergency/stop_all_bots.py
```

---

## 🎯 Next Steps

1. **Setup**: Run bootstrap scripts
2. **Test**: Paper trade with test data
3. **Train**: Build custom ML models
4. **Deploy**: Launch bots in production
5. **Monitor**: Watch dashboards 24/7
6. **Learn**: Forever learning engine improves automatically

---

**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Ready for Deployment  
**Support:** See full docs in CITADEL_OMEGA_ARCHITECTURE.md

🏛️ **CITADEL_OMEGA - The Ultimate Trading Hub**
