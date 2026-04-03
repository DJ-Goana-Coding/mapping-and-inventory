#!/bin/bash
"""
🏰 CITADEL AWAKENING - Quick Start Script
Q.G.T.N.L. Command Citadel - One-Command Activation

Usage: ./wake_citadel.sh [mode]
Modes: full, scouts, sentinels, dashboard
"""

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║               🏰 CITADEL AWAKENING PROTOCOL 🏰                     ║
║                                                                    ║
║           "Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"  ║
║                   Let's wake the citadel up!                       ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

# Get mode
MODE=${1:-full}

echo -e "${GREEN}🚀 Initiating Citadel Awakening - Mode: $MODE${NC}\n"

# Create required directories
echo "📁 Creating directories..."
mkdir -p data/logs data/discoveries data/monitoring

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

case $MODE in
  full)
    echo -e "\n${YELLOW}🏰 FULL AWAKENING MODE${NC}"
    echo "Deploying all workers..."
    python scripts/citadel_awakening.py
    ;;
  
  scouts)
    echo -e "\n${YELLOW}🔍 SCOUTS MODE${NC}"
    echo "Deploying discovery scouts..."
    python scripts/domain_scout.py &
    python scripts/spiritual_network_mapper.py &
    python scripts/web_scout.py &
    wait
    ;;
  
  sentinels)
    echo -e "\n${YELLOW}🛡️ SENTINELS MODE${NC}"
    echo "Deploying security sentinels..."
    python scripts/security_sentinel.py
    ;;
  
  dashboard)
    echo -e "\n${YELLOW}🎮 COMMAND CENTER MODE${NC}"
    echo "Launching Command Center dashboard..."
    streamlit run command_center.py
    ;;
  
  *)
    echo "❌ Unknown mode: $MODE"
    echo "Usage: ./wake_citadel.sh [full|scouts|sentinels|dashboard]"
    exit 1
    ;;
esac

echo -e "\n${GREEN}✅ Citadel Awakening Complete!${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "📊 Check data/monitoring/ for results"
echo "📝 Check data/logs/ for detailed logs"
echo "🎮 Run './wake_citadel.sh dashboard' to see Command Center"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
