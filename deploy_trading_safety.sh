#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# TRADING SAFETY DEPLOYMENT SCRIPT
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Deploy and test trading safety infrastructure
# Authority: Citadel Architect v25.0.OMNI+
# ═══════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
echo -e "${BLUE}"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "  TRADING SAFETY INFRASTRUCTURE - DEPLOYMENT"
echo "  Version: 1.0.0"
echo "  Authority: Citadel Architect v25.0.OMNI+"
echo "═══════════════════════════════════════════════════════════════════════════"
echo -e "${NC}"

# Check if running from correct directory
if [ ! -f "scripts/trading_safety/safe_trader.py" ]; then
    echo -e "${RED}❌ Error: Must run from repository root${NC}"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Function to check environment variable
check_env_var() {
    local var_name=$1
    local required=$2
    
    if [ -z "${!var_name}" ]; then
        if [ "$required" = "true" ]; then
            echo -e "${RED}❌ Required: $var_name${NC}"
            return 1
        else
            echo -e "${YELLOW}⚠️  Optional: $var_name (not set)${NC}"
            return 0
        fi
    else
        # Don't print actual value for security
        echo -e "${GREEN}✅ Found: $var_name${NC}"
        return 0
    fi
}

echo -e "\n${BLUE}1. Checking Environment Variables...${NC}"
echo "───────────────────────────────────────────────────────────────────────────"

check_env_var "MEXC_API_KEY" "false"
check_env_var "MEXC_API_SECRET" "false"
check_env_var "TRADING_CAPITAL" "false"
check_env_var "LIVE_TRADING_ENABLED" "false"
check_env_var "CIRCUIT_BREAKER_RESET_CODE" "false"

echo ""

# Check LIVE_TRADING_ENABLED status
LIVE_MODE=$(echo "${LIVE_TRADING_ENABLED:-false}" | tr '[:upper:]' '[:lower:]')
if [ "$LIVE_MODE" = "true" ]; then
    echo -e "${RED}🔴 LIVE TRADING MODE ENABLED${NC}"
    echo -e "${RED}   This will execute REAL trades with REAL money!${NC}"
else
    echo -e "${GREEN}🟢 PAPER TRADING MODE (Simulation Only)${NC}"
fi

echo ""
echo -e "${BLUE}2. Creating Required Directories...${NC}"
echo "───────────────────────────────────────────────────────────────────────────"

mkdir -p data/trading_safety
mkdir -p data/trading_monitoring

echo -e "${GREEN}✅ Directories created${NC}"

echo ""
echo -e "${BLUE}3. Testing Circuit Breaker...${NC}"
echo "───────────────────────────────────────────────────────────────────────────"

python3 scripts/trading_safety/circuit_breaker.py

echo ""
echo -e "${BLUE}4. Testing Credential Manager...${NC}"
echo "───────────────────────────────────────────────────────────────────────────"

if [ -n "$MEXC_API_KEY" ] && [ -n "$MEXC_API_SECRET" ]; then
    python3 scripts/trading_safety/credential_manager.py
else
    echo -e "${YELLOW}⚠️  Skipping credential test (MEXC credentials not configured)${NC}"
    echo "   To enable: export MEXC_API_KEY=your_key MEXC_API_SECRET=your_secret"
fi

echo ""
echo -e "${BLUE}5. Testing Safe Trader...${NC}"
echo "───────────────────────────────────────────────────────────────────────────"

# Force paper mode for testing
export LIVE_TRADING_ENABLED="false"
python3 scripts/trading_safety/safe_trader.py

echo ""
echo -e "${BLUE}6. Testing Monitoring Agents...${NC}"
echo "───────────────────────────────────────────────────────────────────────────"

python3 scripts/trading_safety/trading_monitors.py

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}  ✅ DEPLOYMENT COMPLETE${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo ""

if [ -z "$MEXC_API_KEY" ] || [ -z "$MEXC_API_SECRET" ]; then
    echo -e "${YELLOW}1. Configure MEXC API Credentials:${NC}"
    echo "   export MEXC_API_KEY=\"your_api_key\""
    echo "   export MEXC_API_SECRET=\"your_api_secret\""
    echo ""
fi

echo -e "${YELLOW}2. Test in Paper Mode (RECOMMENDED - 7 days minimum):${NC}"
echo "   export LIVE_TRADING_ENABLED=\"false\""
echo "   python3 Districts/D04_OMEGA_TRADER/vanguard_live_trader_v2.py"
echo ""

echo -e "${YELLOW}3. Review Performance:${NC}"
echo "   - Check: data/trading_monitoring/performance_metrics.json"
echo "   - Require: Win rate > 50%, Profit factor > 1.5"
echo ""

echo -e "${YELLOW}4. Enable Live Trading (ONLY if paper trading successful):${NC}"
echo "   export LIVE_TRADING_ENABLED=\"true\""
echo "   python3 Districts/D04_OMEGA_TRADER/vanguard_live_trader_v2.py"
echo ""

echo -e "${BLUE}📚 Documentation:${NC}"
echo "   - Operator Manual: TRADING_SAFETY_OPERATOR_MANUAL.md"
echo "   - Circuit Breaker: scripts/trading_safety/circuit_breaker.py"
echo "   - Safe Trader: scripts/trading_safety/safe_trader.py"
echo ""

echo -e "${BLUE}🔍 Monitoring:${NC}"
echo "   - GitHub Actions: .github/workflows/trading_safety_monitor.yml"
echo "   - Reports: data/trading_monitoring/"
echo "   - Logs: data/trading_safety/"
echo ""

echo -e "${RED}⚠️  REMEMBER:${NC}"
echo -e "${RED}   - Start with paper trading for AT LEAST 7 days${NC}"
echo -e "${RED}   - Begin with ONE strategy on ONE asset${NC}"
echo -e "${RED}   - Use micro positions (1-2% of capital)${NC}"
echo -e "${RED}   - NEVER bypass the safety systems${NC}"
echo ""

echo -e "${GREEN}═══════════════════════════════════════════════════════════════════════════${NC}"
