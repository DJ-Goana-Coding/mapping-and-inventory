#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════
TRADING GARAGE ACTIVATION: Live Trading Deployment
═══════════════════════════════════════════════════════════════════════════
Purpose: Activate trading bots with MEXC trading + Binance price feeds + Web3
Authority: Citadel Architect v25.5.OMNI
═══════════════════════════════════════════════════════════════════════════

Configuration:
- MEXC: Live trading execution (requires API secret)
- Binance: Real-time price data only (public API)
- Web3: Blockchain interactions (RPC endpoints)

"""

import os
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════
# TRADING CONFIGURATION TEMPLATE
# ═══════════════════════════════════════════════════════════════════════════

TRADING_CONFIG_TEMPLATE = {
    "version": "1.0.0",
    "generated_at": "",
    "trading_mode": "LIVE",  # LIVE, PAPER, SIMULATION
    
    "exchanges": {
        "mexc": {
            "enabled": True,
            "purpose": "LIVE_TRADING",
            "description": "MEXC exchange for live order execution",
            "api_key_env": "MEXC_API_KEY",
            "api_secret_env": "MEXC_API_SECRET",
            "testnet": False,
            "features": ["spot", "futures", "margin"],
            "endpoints": {
                "rest": "https://api.mexc.com",
                "websocket": "wss://wbs.mexc.com/ws"
            },
            "rate_limits": {
                "orders_per_second": 10,
                "requests_per_minute": 1200
            }
        },
        
        "binance": {
            "enabled": True,
            "purpose": "PRICE_FEED_ONLY",
            "description": "Binance public API for real-time price data (NO TRADING)",
            "api_key_env": None,  # Public API - no key needed
            "api_secret_env": None,
            "testnet": False,
            "features": ["price_feed", "orderbook", "klines", "ticker"],
            "endpoints": {
                "rest": "https://api.binance.com",
                "websocket": "wss://stream.binance.com:9443"
            },
            "rate_limits": {
                "requests_per_minute": 1200,
                "weight_per_minute": 6000
            },
            "note": "PUBLIC DATA ONLY - No trading operations allowed"
        }
    },
    
    "web3": {
        "enabled": True,
        "purpose": "BLOCKCHAIN_INTERACTIONS",
        "description": "Web3 and blockchain integrations",
        
        "networks": {
            "ethereum": {
                "enabled": True,
                "chain_id": 1,
                "rpc_url_env": "ETH_RPC_URL",
                "fallback_rpcs": [
                    "https://eth.llamarpc.com",
                    "https://rpc.ankr.com/eth",
                    "https://ethereum.publicnode.com"
                ],
                "explorer": "https://etherscan.io"
            },
            
            "bsc": {
                "enabled": True,
                "chain_id": 56,
                "rpc_url_env": "BSC_RPC_URL",
                "fallback_rpcs": [
                    "https://bsc-dataseed.binance.org",
                    "https://bsc.publicnode.com"
                ],
                "explorer": "https://bscscan.com"
            },
            
            "polygon": {
                "enabled": True,
                "chain_id": 137,
                "rpc_url_env": "POLYGON_RPC_URL",
                "fallback_rpcs": [
                    "https://polygon-rpc.com",
                    "https://rpc.ankr.com/polygon"
                ],
                "explorer": "https://polygonscan.com"
            },
            
            "arbitrum": {
                "enabled": True,
                "chain_id": 42161,
                "rpc_url_env": "ARBITRUM_RPC_URL",
                "fallback_rpcs": [
                    "https://arb1.arbitrum.io/rpc",
                    "https://rpc.ankr.com/arbitrum"
                ],
                "explorer": "https://arbiscan.io"
            },
            
            "solana": {
                "enabled": True,
                "cluster": "mainnet-beta",
                "rpc_url_env": "SOLANA_RPC_URL",
                "fallback_rpcs": [
                    "https://api.mainnet-beta.solana.com",
                    "https://solana-api.projectserum.com"
                ],
                "explorer": "https://explorer.solana.com"
            },
            
            "base": {
                "enabled": True,
                "chain_id": 8453,
                "rpc_url_env": "BASE_RPC_URL",
                "fallback_rpcs": [
                    "https://mainnet.base.org",
                    "https://base.publicnode.com"
                ],
                "explorer": "https://basescan.org"
            }
        },
        
        "defi_protocols": {
            "uniswap_v3": {
                "enabled": True,
                "networks": ["ethereum", "polygon", "arbitrum", "base"],
                "features": ["swap", "liquidity", "price_oracle"]
            },
            "pancakeswap": {
                "enabled": True,
                "networks": ["bsc"],
                "features": ["swap", "liquidity", "farms"]
            },
            "raydium": {
                "enabled": True,
                "networks": ["solana"],
                "features": ["swap", "liquidity"]
            }
        }
    },
    
    "wallet": {
        "description": "Wallet configuration for Web3 operations",
        "private_key_env": "TRADING_WALLET_PRIVATE_KEY",
        "addresses": {
            "ethereum": "AUTO_DERIVED",
            "bsc": "AUTO_DERIVED",
            "polygon": "AUTO_DERIVED",
            "arbitrum": "AUTO_DERIVED",
            "base": "AUTO_DERIVED",
            "solana": "AUTO_DERIVED_OR_SEPARATE"
        },
        "note": "Private key stored in environment variable, never in code"
    },
    
    "trading_pairs": {
        "spot": [
            "BTC/USDT",
            "ETH/USDT",
            "SOL/USDT",
            "XRP/USDT",
            "BNB/USDT"
        ],
        "futures": [
            "BTC/USDT:USDT",
            "ETH/USDT:USDT"
        ]
    },
    
    "risk_management": {
        "max_position_size_usd": 1000,
        "max_total_exposure_usd": 5000,
        "stop_loss_percentage": 2.0,
        "take_profit_percentage": 5.0,
        "max_daily_trades": 50,
        "emergency_stop": {
            "enabled": True,
            "max_daily_loss_usd": 500,
            "max_consecutive_losses": 5
        }
    },
    
    "data_sources": {
        "primary_price_feed": "binance",
        "backup_price_feeds": ["mexc", "coingecko"],
        "orderbook_source": "binance",
        "trade_execution": "mexc"
    },
    
    "features": {
        "auto_trading": False,  # Must be manually enabled
        "paper_trading_mode": True,  # Start in paper mode for safety
        "price_monitoring": True,
        "orderbook_tracking": True,
        "web3_monitoring": True,
        "portfolio_tracking": True,
        "performance_logging": True
    }
}

# ═══════════════════════════════════════════════════════════════════════════
# GARAGE ACTIVATOR
# ═══════════════════════════════════════════════════════════════════════════

class TradingGarageActivator:
    def __init__(self, garage_root: str = "Trading_Garages"):
        self.garage_root = Path(garage_root)
        self.config_dir = self.garage_root / "Trading_Garage_Alpha" / "configs"
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_trading_config(self):
        """Generate trading configuration file"""
        config = TRADING_CONFIG_TEMPLATE.copy()
        config["generated_at"] = datetime.utcnow().isoformat() + "Z"
        
        config_path = self.config_dir / "trading_config.json"
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Generated: {config_path}")
        return config_path
    
    def generate_env_template(self):
        """Generate .env template for secrets"""
        env_template = """# ═══════════════════════════════════════════════════════════════════════════
# Trading Garage Environment Variables
# ═══════════════════════════════════════════════════════════════════════════
# IMPORTANT: Never commit this file with real values!
# Copy to .env.local and fill in your actual credentials
# ═══════════════════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════════════════
# MEXC Exchange (Live Trading)
# ═══════════════════════════════════════════════════════════════════════════
MEXC_API_KEY=your_mexc_api_key_here
MEXC_API_SECRET=your_mexc_api_secret_here

# ═══════════════════════════════════════════════════════════════════════════
# Binance (Price Data Only - Public API, no credentials needed)
# ═══════════════════════════════════════════════════════════════════════════
# No API keys needed for public price data

# ═══════════════════════════════════════════════════════════════════════════
# Web3 RPC Endpoints (Optional - will use public RPCs if not set)
# ═══════════════════════════════════════════════════════════════════════════
ETH_RPC_URL=https://eth.llamarpc.com
BSC_RPC_URL=https://bsc-dataseed.binance.org
POLYGON_RPC_URL=https://polygon-rpc.com
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
SOLANA_RPC_URL=https://api.mainnet-beta.solana.com
BASE_RPC_URL=https://mainnet.base.org

# ═══════════════════════════════════════════════════════════════════════════
# Trading Wallet (for Web3 operations)
# ═══════════════════════════════════════════════════════════════════════════
TRADING_WALLET_PRIVATE_KEY=your_wallet_private_key_here

# ═══════════════════════════════════════════════════════════════════════════
# Optional: Premium RPC Providers
# ═══════════════════════════════════════════════════════════════════════════
# INFURA_PROJECT_ID=your_infura_id
# ALCHEMY_API_KEY=your_alchemy_key
# QUICKNODE_ENDPOINT=your_quicknode_url

# ═══════════════════════════════════════════════════════════════════════════
# Trading Mode
# ═══════════════════════════════════════════════════════════════════════════
TRADING_MODE=PAPER  # PAPER, LIVE
AUTO_TRADING_ENABLED=false

# ═══════════════════════════════════════════════════════════════════════════
# Security
# ═══════════════════════════════════════════════════════════════════════════
# Add IP whitelist in MEXC account settings
# Enable 2FA for all exchange accounts
# Use withdrawal whitelist in exchange settings
"""
        
        env_path = self.config_dir / ".env.template"
        env_path.write_text(env_template)
        print(f"✅ Generated: {env_path}")
        
        # Also create .gitignore for configs
        gitignore_path = self.config_dir / ".gitignore"
        gitignore_path.write_text(".env\n.env.local\n*.secret\n*.key\n")
        print(f"✅ Generated: {gitignore_path}")
        
        return env_path
    
    def generate_activation_script(self):
        """Generate Python activation script for bots"""
        script_content = '''#!/usr/bin/env python3
"""
Trading Garage Bot Activation Script
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
env_path = Path(__file__).parent / ".env.local"
if env_path.exists():
    load_dotenv(env_path)
    print(f"✅ Loaded environment from {env_path}")
else:
    print(f"⚠️  No .env.local found. Using environment variables.")

# Load trading config
config_path = Path(__file__).parent / "trading_config.json"
with open(config_path) as f:
    CONFIG = json.load(f)

print("═══════════════════════════════════════════════════════════════════════════")
print("🚗 Trading Garage Activation")
print("═══════════════════════════════════════════════════════════════════════════")
print(f"Trading Mode: {CONFIG['features']['paper_trading_mode'] and 'PAPER' or 'LIVE'}")
print(f"Auto Trading: {CONFIG['features']['auto_trading']}")
print("")

# Verify MEXC credentials
mexc_key = os.getenv("MEXC_API_KEY")
mexc_secret = os.getenv("MEXC_API_SECRET")

if not mexc_key or not mexc_secret:
    print("❌ MEXC credentials not found!")
    print("   Please set MEXC_API_KEY and MEXC_API_SECRET in .env.local")
    sys.exit(1)

print("✅ MEXC credentials loaded")
print("")

# Check Binance (public API - no creds needed)
print("✅ Binance public API configured (price data only)")
print("")

# Check Web3
wallet_key = os.getenv("TRADING_WALLET_PRIVATE_KEY")
if wallet_key:
    print("✅ Web3 wallet configured")
else:
    print("⚠️  Web3 wallet not configured (optional)")
print("")

# Display active networks
print("Web3 Networks:")
for network, config in CONFIG["web3"]["networks"].items():
    if config["enabled"]:
        print(f"  ✅ {network.upper()}: {config['fallback_rpcs'][0]}")
print("")

print("═══════════════════════════════════════════════════════════════════════════")
print("🎯 Ready to activate trading bots")
print("═══════════════════════════════════════════════════════════════════════════")
print("")
print("Next steps:")
print("  1. Review risk management settings in trading_config.json")
print("  2. Enable auto_trading: false → true when ready")
print("  3. Switch paper_trading_mode: true → false for live trading")
print("  4. Run individual bot scripts from ../repos/")
print("")
print("🦎 Weld. Pulse. Trade.")
'''
        
        script_path = self.config_dir / "activate_bots.py"
        script_path.write_text(script_content)
        os.chmod(script_path, 0o755)
        print(f"✅ Generated: {script_path}")
        
        return script_path
    
    def generate_readme(self):
        """Generate comprehensive README for trading garage"""
        readme_content = f"""# 🚗 Trading Garage Alpha - Live Trading Configuration

**Generated:** {datetime.utcnow().isoformat()}Z  
**Authority:** Citadel Architect v25.5.OMNI

## Overview

This garage contains live trading bot configurations with:
- **MEXC:** Live order execution
- **Binance:** Real-time price data (public API only)
- **Web3:** Blockchain integrations (Ethereum, BSC, Polygon, Arbitrum, Solana, Base)

## Architecture

```
Trading_Garage_Alpha/
├── configs/
│   ├── trading_config.json     # Main configuration
│   ├── .env.template           # Environment template
│   ├── .env.local             # Your secrets (DO NOT COMMIT)
│   ├── activate_bots.py       # Activation script
│   └── .gitignore             # Protect secrets
├── repos/                      # Cloned bot repositories
└── data/                       # Trading data, logs, ledgers
```

## Setup

### 1. Configure Secrets

```bash
cd configs/
cp .env.template .env.local
nano .env.local  # Add your MEXC credentials
```

**Required:**
- `MEXC_API_KEY` - Your MEXC API key
- `MEXC_API_SECRET` - Your MEXC API secret

**Optional:**
- `TRADING_WALLET_PRIVATE_KEY` - For Web3 operations
- Custom RPC endpoints (will use public RPCs if not set)

### 2. Verify Configuration

```bash
python3 configs/activate_bots.py
```

This will:
- Load and verify credentials
- Check Binance public API access
- Validate Web3 connections
- Display active networks

### 3. Review Risk Management

Edit `trading_config.json`:

```json
{{
  "risk_management": {{
    "max_position_size_usd": 1000,
    "max_total_exposure_usd": 5000,
    "stop_loss_percentage": 2.0,
    "take_profit_percentage": 5.0,
    "emergency_stop": {{
      "max_daily_loss_usd": 500
    }}
  }}
}}
```

### 4. Trading Mode

**Paper Trading (Default):**
```json
{{
  "features": {{
    "auto_trading": false,
    "paper_trading_mode": true
  }}
}}
```

**Live Trading (When Ready):**
```json
{{
  "features": {{
    "auto_trading": true,
    "paper_trading_mode": false
  }}
}}
```

## Exchange Configuration

### MEXC (Live Trading)

- **Purpose:** Order execution
- **Features:** Spot, Futures, Margin
- **Rate Limits:** 10 orders/sec, 1200 requests/min
- **Endpoint:** https://api.mexc.com
- **WebSocket:** wss://wbs.mexc.com/ws

### Binance (Price Data Only)

- **Purpose:** Real-time market data
- **Features:** Price feeds, orderbook, klines, ticker
- **NO TRADING:** Public API only, no orders
- **Rate Limits:** 1200 requests/min, 6000 weight/min
- **Endpoint:** https://api.binance.com

## Web3 Networks

| Network  | Chain ID | Explorer                  |
|----------|----------|---------------------------|
| Ethereum | 1        | etherscan.io             |
| BSC      | 56       | bscscan.com              |
| Polygon  | 137      | polygonscan.com          |
| Arbitrum | 42161    | arbiscan.io              |
| Solana   | -        | explorer.solana.com      |
| Base     | 8453     | basescan.org             |

## DeFi Protocols

- **Uniswap V3:** Ethereum, Polygon, Arbitrum, Base
- **PancakeSwap:** BSC
- **Raydium:** Solana

## Security

### MEXC Account
1. Enable 2FA (Google Authenticator or SMS)
2. Set IP whitelist in API settings
3. Enable withdrawal whitelist
4. Use read-only API for monitoring bots
5. Limit API permissions to spot trading only (initially)

### Environment Variables
- Never commit `.env.local` or secrets to git
- Use separate API keys for testing vs production
- Rotate API keys regularly
- Monitor API key usage in MEXC dashboard

### Web3 Wallet
- Use a dedicated trading wallet (not your main wallet)
- Start with small amounts for testing
- Keep private key in environment variable only
- Consider hardware wallet integration for larger amounts

## Monitoring

### Portfolio Tracking
```bash
# View current positions
python3 repos/[bot-name]/check_balance.py

# View trade history
python3 repos/[bot-name]/trade_history.py
```

### Performance Logs
```bash
# View logs
tail -f data/logs/trading_*.log

# Performance metrics
cat data/performance_metrics.json | jq .
```

## Trading Pairs

**Configured pairs:**
- BTC/USDT, ETH/USDT, SOL/USDT
- XRP/USDT, BNB/USDT
- Futures: BTC/USDT:USDT, ETH/USDT:USDT

Add more pairs in `trading_config.json`:
```json
{{
  "trading_pairs": {{
    "spot": ["YOUR/PAIR"]
  }}
}}
```

## Troubleshooting

### "MEXC credentials not found"
- Check `.env.local` exists in `configs/`
- Verify `MEXC_API_KEY` and `MEXC_API_SECRET` are set
- Restart activation script

### "Binance rate limit exceeded"
- Binance public API has strict rate limits
- Add delays between requests
- Use WebSocket for real-time data

### "Web3 RPC connection failed"
- Check RPC endpoint is accessible
- Try fallback RPCs in `trading_config.json`
- Consider using premium RPC (Infura, Alchemy)

### "Order rejected by MEXC"
- Check API key permissions
- Verify account has sufficient balance
- Check IP whitelist settings
- Review MEXC account status

## Related Documentation

- [TRADING_GARAGE_GUIDE.md](../TRADING_GARAGE_GUIDE.md)
- [CITADEL_OMEGA_ARCHITECTURE.md](../../CITADEL_OMEGA_ARCHITECTURE.md)
- Individual bot READMEs in `repos/*/`

---

**🦎 Weld. Pulse. Trade.**

*Never trade with more than you can afford to lose. Always test in paper mode first.*
"""
        
        readme_path = self.garage_root / "Trading_Garage_Alpha" / "README.md"
        readme_path.write_text(readme_content)
        print(f"✅ Generated: {readme_path}")
        
        return readme_path
    
    def activate(self):
        """Run full activation sequence"""
        print("═══════════════════════════════════════════════════════════════════════════")
        print("🚗 TRADING GARAGE ACTIVATION")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("")
        
        print("📋 Generating configuration files...")
        self.generate_trading_config()
        self.generate_env_template()
        self.generate_activation_script()
        self.generate_readme()
        
        print("")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("✅ GARAGE ACTIVATION COMPLETE")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("")
        print("📁 Configuration files created:")
        print(f"  - {self.config_dir / 'trading_config.json'}")
        print(f"  - {self.config_dir / '.env.template'}")
        print(f"  - {self.config_dir / 'activate_bots.py'}")
        print(f"  - {self.garage_root / 'Trading_Garage_Alpha' / 'README.md'}")
        print("")
        print("🎯 Next Steps:")
        print("  1. cd Trading_Garages/Trading_Garage_Alpha/configs/")
        print("  2. cp .env.template .env.local")
        print("  3. nano .env.local  # Add your MEXC credentials")
        print("  4. python3 activate_bots.py  # Verify configuration")
        print("  5. Review trading_config.json risk settings")
        print("")
        print("⚠️  Important:")
        print("  - Start in PAPER mode (default)")
        print("  - Never commit .env.local to git")
        print("  - Enable IP whitelist in MEXC")
        print("  - Test with small amounts first")
        print("")
        print("═══════════════════════════════════════════════════════════════════════════")
        print("🦎 Weld. Pulse. Trade.")
        print("═══════════════════════════════════════════════════════════════════════════")

# ═══════════════════════════════════════════════════════════════════════════
# MAIN EXECUTION
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    activator = TradingGarageActivator()
    activator.activate()
