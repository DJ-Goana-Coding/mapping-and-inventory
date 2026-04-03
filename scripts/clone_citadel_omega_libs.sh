#!/bin/bash
# CITADEL_OMEGA - Clone All Trading Libraries
# Author: Citadel Architect v25.0.OMNI+

set -e

echo "=============================================="
echo "🏛️  CITADEL_OMEGA - Library Cloner"
echo "=============================================="
echo ""

# Check if we're in the right directory
if [ ! -d "CITADEL_OMEGA" ]; then
    echo "⚠️  Warning: CITADEL_OMEGA directory not found"
    echo "Creating CITADEL_OMEGA structure..."
    mkdir -p CITADEL_OMEGA/libraries
fi

cd CITADEL_OMEGA/libraries || mkdir -p libraries && cd libraries

echo "📦 Cloning Essential Trading Libraries..."
echo ""

# 1. CCXT - Universal Exchange Library
echo "1/10 Cloning CCXT..."
if [ ! -d "ccxt" ]; then
    git clone https://github.com/ccxt/ccxt.git ccxt
    echo "✅ CCXT cloned"
else
    echo "⏭️  CCXT already exists, pulling latest..."
    cd ccxt && git pull && cd ..
fi
echo ""

# 2. TA-Lib Python Wrapper
echo "2/10 Cloning TA-Lib..."
if [ ! -d "ta-lib" ]; then
    git clone https://github.com/mrjbq7/ta-lib.git ta-lib
    echo "✅ TA-Lib cloned"
else
    echo "⏭️  TA-Lib already exists"
fi
echo ""

# 3. FreqTrade
echo "3/10 Cloning FreqTrade..."
if [ ! -d "freqtrade" ]; then
    git clone https://github.com/freqtrade/freqtrade.git freqtrade
    echo "✅ FreqTrade cloned"
else
    echo "⏭️  FreqTrade already exists, pulling latest..."
    cd freqtrade && git pull && cd ..
fi
echo ""

# 4. Jesse AI
echo "4/10 Cloning Jesse AI..."
if [ ! -d "jesse-ai" ]; then
    git clone https://github.com/jesse-ai/jesse.git jesse-ai
    echo "✅ Jesse AI cloned"
else
    echo "⏭️  Jesse AI already exists"
fi
echo ""

# 5. Hummingbot
echo "5/10 Cloning Hummingbot..."
if [ ! -d "hummingbot" ]; then
    git clone https://github.com/hummingbot/hummingbot.git hummingbot
    echo "✅ Hummingbot cloned"
else
    echo "⏭️  Hummingbot already exists, pulling latest..."
    cd hummingbot && git pull && cd ..
fi
echo ""

# 6. Pandas-TA
echo "6/10 Cloning Pandas-TA..."
if [ ! -d "pandas-ta" ]; then
    git clone https://github.com/twopirllc/pandas-ta.git pandas-ta
    echo "✅ Pandas-TA cloned"
else
    echo "⏭️  Pandas-TA already exists"
fi
echo ""

# 7. VectorBT
echo "7/10 Cloning VectorBT..."
if [ ! -d "vectorbt" ]; then
    git clone https://github.com/polakowo/vectorbt.git vectorbt
    echo "✅ VectorBT cloned"
else
    echo "⏭️  VectorBT already exists"
fi
echo ""

# 8. Backtrader
echo "8/10 Cloning Backtrader..."
if [ ! -d "backtrader" ]; then
    git clone https://github.com/mementum/backtrader.git backtrader
    echo "✅ Backtrader cloned"
else
    echo "⏭️  Backtrader already exists"
fi
echo ""

# 9. Catalyst
echo "9/10 Cloning Catalyst..."
if [ ! -d "catalyst" ]; then
    git clone https://github.com/enigmampc/catalyst.git catalyst
    echo "✅ Catalyst cloned"
else
    echo "⏭️  Catalyst already exists"
fi
echo ""

# 10. Zipline
echo "10/10 Cloning Zipline..."
if [ ! -d "zipline" ]; then
    git clone https://github.com/quantopian/zipline.git zipline
    echo "✅ Zipline cloned"
else
    echo "⏭️  Zipline already exists"
fi
echo ""

# Additional useful libraries
echo "📦 Cloning Additional Libraries..."
echo ""

# Technical Analysis
if [ ! -d "ta" ]; then
    git clone https://github.com/bukosabino/ta.git ta
    echo "✅ TA (Technical Analysis) cloned"
fi

# TensorTrade (RL for Trading)
if [ ! -d "tensortrade" ]; then
    git clone https://github.com/tensortrade-org/tensortrade.git tensortrade
    echo "✅ TensorTrade cloned"
fi

# FinRL (Financial Reinforcement Learning)
if [ ! -d "finrl" ]; then
    git clone https://github.com/AI4Finance-Foundation/FinRL.git finrl
    echo "✅ FinRL cloned"
fi

# Crypto Data Download
if [ ! -d "crypto-data-download" ]; then
    git clone https://github.com/Draichi/crypto-data-download.git crypto-data-download
    echo "✅ Crypto Data Download cloned"
fi

echo ""
echo "=============================================="
echo "✅ Library Cloning Complete!"
echo "=============================================="
echo ""
echo "📊 Summary:"
echo "  • Core Trading: CCXT, FreqTrade, Jesse, Hummingbot"
echo "  • Technical Analysis: TA-Lib, Pandas-TA, TA"
echo "  • Backtesting: Backtrader, VectorBT, Zipline, Catalyst"
echo "  • AI/ML: TensorTrade, FinRL"
echo "  • Data: Crypto Data Download"
echo ""
echo "🎯 Next Steps:"
echo "  1. Run: bash genesis/bootstrap/download_all_models.sh"
echo "  2. Run: bash genesis/bootstrap/setup_citadel_omega.sh"
echo "  3. Install dependencies: pip install -r requirements.txt"
echo ""
