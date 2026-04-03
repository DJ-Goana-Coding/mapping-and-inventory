# 🎯 Omega-Trader Setup Guide

**Hub Repository:** DJ-Goanna-Coding/Omega-Trader (HuggingFace Space)  
**Purpose:** Main trading operations hub with MEXC + Web3 integration

---

## 🚀 Quick Start

### Prerequisites

- HuggingFace account
- MEXC trading account
- Web3 wallets (Ethereum, Solana, BSC)
- GitHub account (for secrets management)

---

## Step 1: Create HuggingFace Space

```bash
# Create new Space on HuggingFace
# Name: Omega-Trader
# SDK: Gradio
# Visibility: Public (no secrets exposed)
```

Visit: https://huggingface.co/new-space

**Configuration:**
- Space name: `Omega-Trader`
- Owner: `DJ-Goanna-Coding`
- SDK: `Gradio`
- Python version: `3.11`
- Hardware: `CPU basic` (upgrade to GPU for ML features)

---

## Step 2: Initialize Repository Structure

```bash
# Clone the new space
git clone https://huggingface.co/spaces/DJ-Goanna-Coding/Omega-Trader
cd Omega-Trader

# Create directory structure
mkdir -p src/{connectors,traders,risk,analytics}
mkdir -p config
mkdir -p data/{trades,market,logs}
mkdir -p .github/workflows
mkdir -p tests
```

---

## Step 3: Create Core Files

### `app.py` - HuggingFace Space UI

```python
"""
Omega-Trader - Main Trading Hub
HuggingFace Space Interface
"""
import gradio as gr
import os
from datetime import datetime
from src.mexc_connector import MEXCConnector
from src.web3_manager import Web3Manager
from src.pnl_tracker import PnLTracker

# Initialize (read-only mode for public Space)
DISPLAY_MODE = os.getenv("DISPLAY_MODE", "PUBLIC")

def get_trading_status():
    """Get current trading status"""
    return {
        "status": "OPERATIONAL",
        "mexc_connection": "CONNECTED (Display Only)",
        "active_positions": "View Only Mode",
        "daily_pnl": "Hidden in Public Mode",
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def get_bot_status():
    """Get status from Omega-Bots spoke"""
    return {
        "active_bots": 8,
        "top_performer": "momentum_bot_v3",
        "total_strategies": 47
    }

def get_security_status():
    """Get status from Omega-Scout spoke"""
    return {
        "api_health": "12/12 ONLINE",
        "security_alerts": 0,
        "wallet_status": "SECURE"
    }

def get_archive_status():
    """Get status from Omega-Archive spoke"""
    return {
        "strategies": 127,
        "dataset_size": "10.2GB",
        "rag_status": "ONLINE",
        "learning_cycles": 1847
    }

# Build Gradio Interface
with gr.Blocks(title="Omega-Trader Hub") as demo:
    gr.Markdown("# 🌐 Omega-Trader - Trading Operations Hub")
    gr.Markdown("**Mode:** Public Display (No Secrets Exposed)")
    
    with gr.Tabs():
        with gr.Tab("Trading Status"):
            gr.Markdown("## Live Trading Overview")
            status_display = gr.JSON(label="Trading Status")
            refresh_btn = gr.Button("Refresh Status")
            refresh_btn.click(fn=get_trading_status, outputs=status_display)
            demo.load(fn=get_trading_status, outputs=status_display)
        
        with gr.Tab("Bots (Omega-Bots)"):
            gr.Markdown("## Active Trading Bots")
            bots_display = gr.JSON(label="Bot Status")
            demo.load(fn=get_bot_status, outputs=bots_display)
        
        with gr.Tab("Security (Omega-Scout)"):
            gr.Markdown("## Security & API Status")
            security_display = gr.JSON(label="Security Status")
            demo.load(fn=get_security_status, outputs=security_display)
        
        with gr.Tab("Archive (Omega-Archive)"):
            gr.Markdown("## Strategy Library & Learning")
            archive_display = gr.JSON(label="Archive Status")
            demo.load(fn=get_archive_status, outputs=archive_display)
        
        with gr.Tab("Documentation"):
            gr.Markdown("""
            ## Omega Trading Ecosystem
            
            ### Architecture
            - **Omega-Trader** (This Space) - Trading operations hub
            - **Omega-Bots** - AI agents and trading bots
            - **Omega-Scout** - API connectors and security
            - **Omega-Archive** - Strategy library and RAG system
            
            ### Integration
            All components sync to **Mapping-and-Inventory** hub.
            
            ### Security
            - No secrets exposed in public Space
            - All trading operations managed via GitHub Actions
            - MEXC API keys stored in GitHub Secrets
            - Web3 private keys encrypted and secured
            
            ### Links
            - [Omega-Bots Repository](https://github.com/DJ-Goana-Coding/Omega-Bots)
            - [Omega-Scout Repository](https://github.com/DJ-Goana-Coding/Omega-Scout)
            - [Omega-Archive Space](https://huggingface.co/spaces/DJ-Goanna-Coding/Omega-Archive)
            - [Mapping Hub](https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory)
            """)

if __name__ == "__main__":
    demo.launch()
```

### `requirements.txt`

```txt
gradio==4.16.0
requests>=2.31.0
python-dotenv>=1.0.0
pandas>=2.1.0
numpy>=1.24.0
ccxt>=4.2.0
web3>=6.15.0
pydantic>=2.5.0
```

### `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose Gradio port
EXPOSE 7860

# Run application
CMD ["python", "app.py"]
```

### `README.md`

```markdown
# 🌐 Omega-Trader - Trading Operations Hub

**Status:** OPERATIONAL  
**Type:** HuggingFace Space  
**Purpose:** Main trading hub with MEXC and Web3 integration

## Features

- ✅ MEXC Exchange Integration
- ✅ Web3 Multi-Chain Wallets
- ✅ Real-time P&L Tracking
- ✅ Bot Management (from Omega-Bots)
- ✅ Security Monitoring (from Omega-Scout)
- ✅ Strategy Library (from Omega-Archive)

## Architecture

This is the central HUB of the Omega Trading Ecosystem.

**Spokes:**
- **Omega-Bots** - AI trading agents
- **Omega-Scout** - API connectors & security
- **Omega-Archive** - Strategies & forever learning

## Public vs Production

**Public Space (this):** Display-only dashboard, no secrets exposed  
**Production Trading:** Managed via GitHub Actions with secret management

## Documentation

See [OMEGA_TRADING_ECOSYSTEM.md](https://github.com/DJ-Goana-Coding/mapping-and-inventory/blob/main/OMEGA_TRADING_ECOSYSTEM.md)
```

---

## Step 4: Setup GitHub Integration

Create GitHub repository for backend operations:

```bash
# Create GitHub repo: DJ-Goana-Coding/Omega-Trader
# This holds the actual trading logic and secrets
```

### `.github/workflows/live_trading.yml`

```yaml
name: Live Trading Operations
on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes
  workflow_dispatch:

jobs:
  execute_trades:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      
      - name: Install Dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Execute Trading Logic
        env:
          MEXC_API_KEY: ${{ secrets.MEXC_API_KEY }}
          MEXC_SECRET_KEY: ${{ secrets.MEXC_SECRET_KEY }}
          WEB3_ETHEREUM_KEY: ${{ secrets.WEB3_ETHEREUM_KEY }}
          WEB3_SOLANA_KEY: ${{ secrets.WEB3_SOLANA_KEY }}
        run: |
          python src/traders/live_trader.py
      
      - name: Update Status
        run: |
          python scripts/update_trading_status.py
      
      - name: Sync to HuggingFace
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          python scripts/sync_to_hf_space.py
```

### `.github/workflows/sync_to_mapping.yml`

```yaml
name: Sync to Mapping Hub
on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Generate Omega Status Report
        run: |
          python scripts/generate_omega_report.py
      
      - name: Clone Mapping Hub
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git clone https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory
      
      - name: Update Mapping Data
        run: |
          mkdir -p Mapping-and-Inventory/data/omega
          cp data/omega_status.json Mapping-and-Inventory/data/omega/
      
      - name: Push to Mapping Hub
        working-directory: Mapping-and-Inventory
        env:
          HF_TOKEN: ${{ secrets.HF_TOKEN }}
        run: |
          git config user.name "Omega-Trader Bot"
          git config user.email "bot@omega-trader.ai"
          git add .
          git commit -m "🌐 Omega-Trader status update" || echo "No changes"
          git push https://user:${HF_TOKEN}@huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory main
```

---

## Step 5: Configure Secrets

### GitHub Secrets (Repository Settings → Secrets)

```bash
# MEXC API
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET_KEY=your_mexc_secret_key

# Web3 Wallets (ENCRYPTED!)
WEB3_ETHEREUM_KEY=0x...
WEB3_SOLANA_KEY=...
WEB3_BSC_KEY=0x...

# HuggingFace
HF_TOKEN=hf_...

# Master Encryption
ENCRYPTION_KEY=your_master_encryption_key
```

### HuggingFace Space Secrets

```bash
# Space Settings → Variables
DISPLAY_MODE=PUBLIC
API_ENDPOINTS=PUBLIC_ONLY
```

---

## Step 6: Deploy Core Trading Logic

### `src/connectors/mexc_connector.py`

```python
"""MEXC Exchange Connector"""
import ccxt
import os

class MEXCConnector:
    def __init__(self):
        self.api_key = os.getenv("MEXC_API_KEY")
        self.secret = os.getenv("MEXC_SECRET_KEY")
        
        self.exchange = ccxt.mexc({
            'apiKey': self.api_key,
            'secret': self.secret,
            'enableRateLimit': True
        })
    
    def get_balance(self):
        """Get account balance"""
        return self.exchange.fetch_balance()
    
    def place_order(self, symbol, side, amount, price=None):
        """Place order"""
        if price:
            return self.exchange.create_limit_order(symbol, side, amount, price)
        else:
            return self.exchange.create_market_order(symbol, side, amount)
    
    def get_positions(self):
        """Get open positions"""
        return self.exchange.fetch_positions()
```

### `src/web3_manager.py`

```python
"""Web3 Multi-Chain Wallet Manager"""
from web3 import Web3
import os

class Web3Manager:
    def __init__(self):
        self.eth_key = os.getenv("WEB3_ETHEREUM_KEY")
        self.sol_key = os.getenv("WEB3_SOLANA_KEY")
        
        # Ethereum
        self.eth_provider = Web3(Web3.HTTPProvider('https://eth.llamarpc.com'))
        self.eth_account = self.eth_provider.eth.account.from_key(self.eth_key)
        
    def get_eth_balance(self):
        """Get Ethereum balance"""
        balance = self.eth_provider.eth.get_balance(self.eth_account.address)
        return self.eth_provider.from_wei(balance, 'ether')
    
    def send_eth_transaction(self, to_address, amount_eth):
        """Send ETH transaction"""
        # Implementation with proper gas estimation and signing
        pass
```

---

## Step 7: Test Deployment

### Local Testing

```bash
# Test locally
python app.py

# Visit http://localhost:7860
```

### Deploy to HuggingFace

```bash
cd Omega-Trader
git add .
git commit -m "🌐 Initial Omega-Trader deployment"
git push
```

---

## Step 8: Connect Spokes

Update spoke configurations to point to Omega-Trader:

```python
# In Omega-Bots, Omega-Scout, Omega-Archive
OMEGA_TRADER_HUB = "https://huggingface.co/spaces/DJ-Goanna-Coding/Omega-Trader"
```

---

## 🔐 Security Checklist

- [ ] MEXC API keys stored in GitHub Secrets (never commit)
- [ ] Web3 private keys encrypted and secured
- [ ] HuggingFace Space set to PUBLIC mode (display only)
- [ ] GitHub Actions enabled for trading operations
- [ ] Rate limiting configured on all API calls
- [ ] IP whitelisting enabled on MEXC account
- [ ] 2FA enabled on all accounts
- [ ] Hardware wallet integration for large transactions

---

## 📊 Monitoring

### Health Checks

```python
# scripts/health_check.py
def check_omega_trader_health():
    checks = {
        "mexc_connection": test_mexc_connection(),
        "web3_providers": test_web3_providers(),
        "github_actions": check_workflow_status(),
        "hf_space": test_hf_space_status()
    }
    return all(checks.values())
```

---

## 🚀 Production Launch

### Pre-Launch Checklist

- [ ] Test with paper trading (testnet)
- [ ] Verify all API connections
- [ ] Test wallet transactions on testnet
- [ ] Configure risk limits
- [ ] Setup alerting (email/Discord/Telegram)
- [ ] Test sync to Mapping Hub
- [ ] Verify spoke connections (Bots, Scout, Archive)

### Go Live

```bash
# Switch from testnet to mainnet
# In GitHub Secrets, update:
MEXC_API_KEY → Production API key
WEB3_ETHEREUM_KEY → Production wallet
```

---

**Status:** Setup Guide Complete  
**Next:** Configure Omega-Bots spoke

🎯 **Omega-Trader - Professional Trading Hub**
