#!/bin/bash
# OMEGA-OMNI Quick Start Script
# One-command execution of the entire protocol

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
MODE="${1:-full_cycle}"
INTENSITY="${2:-moderate}"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
EXECUTION_ID="omega-omni-$(date +%Y%m%d-%H%M%S)"

# Banner
echo -e "${MAGENTA}"
cat << "EOF"
═══════════════════════════════════════════════════════════════════
   ██████╗ ███╗   ███╗███████╗ ██████╗  █████╗       ██████╗ ███╗   ███╗███╗   ██╗██╗
  ██╔═══██╗████╗ ████║██╔════╝██╔════╝ ██╔══██╗     ██╔═══██╗████╗ ████║████╗  ██║██║
  ██║   ██║██╔████╔██║█████╗  ██║  ███╗███████║     ██║   ██║██╔████╔██║██╔██╗ ██║██║
  ██║   ██║██║╚██╔╝██║██╔══╝  ██║   ██║██╔══██║     ██║   ██║██║╚██╔╝██║██║╚██╗██║██║
  ╚██████╔╝██║ ╚═╝ ██║███████╗╚██████╔╝██║  ██║     ╚██████╔╝██║ ╚═╝ ██║██║ ╚████║██║
   ╚═════╝ ╚═╝     ╚═╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝      ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝
═══════════════════════════════════════════════════════════════════
  Comprehensive Discovery, Repair, and Integration Protocol v1.0
═══════════════════════════════════════════════════════════════════
EOF
echo -e "${NC}"

echo -e "${CYAN}Execution Configuration:${NC}"
echo -e "  ${YELLOW}Execution ID:${NC} $EXECUTION_ID"
echo -e "  ${YELLOW}Timestamp:${NC}    $TIMESTAMP"
echo -e "  ${YELLOW}Mode:${NC}         $MODE"
echo -e "  ${YELLOW}Intensity:${NC}    $INTENSITY"
echo ""

# Check Python installation
echo -e "${BLUE}[1/7] Checking prerequisites...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION detected"

# Create necessary directories
echo -e "${BLUE}[2/7] Creating directory structure...${NC}"
mkdir -p data/{discoveries,solutions,swarms,testing,shopping,monitoring,logs}
echo -e "${GREEN}✓${NC} Directory structure ready"

# Install dependencies
echo -e "${BLUE}[3/7] Installing dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet requests beautifulsoup4 lxml
echo -e "${GREEN}✓${NC} Dependencies installed"

# Phase 1: Discovery
if [[ "$MODE" == "full_cycle" || "$MODE" == "discovery_only" ]]; then
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}[4/7] PHASE 1: Omni-Dimensional Discovery${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    python3 scripts/omega_omni_discovery_engine.py
    echo -e "${GREEN}✓${NC} Discovery complete"
fi

# Phase 2: Solutions
if [[ "$MODE" == "full_cycle" || "$MODE" == "solutions_only" ]]; then
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}[5/7] PHASE 2: Multi-Solution Generation${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    python3 scripts/multi_solution_generator.py
    echo -e "${GREEN}✓${NC} Solutions generated"
fi

# Phase 3: Swarms
if [[ "$MODE" == "full_cycle" || "$MODE" == "swarms_only" ]]; then
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}[6/7] PHASE 3: Agentic Swarm Deployment${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    python3 scripts/agentic_swarm_orchestrator.py
    echo -e "${GREEN}✓${NC} Swarms deployed"
fi

# Phase 4: Testing
if [[ "$MODE" == "full_cycle" || "$MODE" == "testing_only" ]]; then
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}[7/7] PHASE 4: Continuous Stress Testing${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    python3 scripts/continuous_stress_test_engine.py
    echo -e "${GREEN}✓${NC} Testing complete"
fi

# Phase 5: Shopping
if [[ "$MODE" == "full_cycle" || "$MODE" == "shopping_only" ]]; then
    echo ""
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}[8/7] PHASE 5: Agent Shopping Expedition${NC}"
    echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
    python3 scripts/agent_shopping_expedition.py
    echo -e "${GREEN}✓${NC} Shopping complete"
fi

# Generate execution summary
echo ""
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}EXECUTION SUMMARY${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"

# Create master index
cat > data/omega-omni-master-index.json << EOF
{
  "execution_id": "$EXECUTION_ID",
  "timestamp": "$TIMESTAMP",
  "mode": "$MODE",
  "intensity": "$INTENSITY",
  "protocol_version": "OMEGA-OMNI v1.0",
  "status": "COMPLETED",
  "artifacts": {
    "discoveries": "data/discoveries/",
    "solutions": "data/solutions/",
    "swarms": "data/swarms/",
    "testing": "data/testing/",
    "shopping": "data/shopping/"
  }
}
EOF

# Count results
DISCOVERY_COUNT=$(find data/discoveries -type f -name "*.json" 2>/dev/null | wc -l)
SOLUTION_COUNT=$(find data/solutions -type f -name "*.json" 2>/dev/null | wc -l)
SWARM_COUNT=$(find data/swarms -type f -name "*.json" 2>/dev/null | wc -l)
TEST_COUNT=$(find data/testing -type f -name "*.json" 2>/dev/null | wc -l)
SHOPPING_COUNT=$(find data/shopping -type f -name "*.json" 2>/dev/null | wc -l)

echo ""
echo -e "${YELLOW}Artifacts Generated:${NC}"
echo -e "  ${GREEN}✓${NC} Discoveries: $DISCOVERY_COUNT files in data/discoveries/"
echo -e "  ${GREEN}✓${NC} Solutions:   $SOLUTION_COUNT files in data/solutions/"
echo -e "  ${GREEN}✓${NC} Swarms:      $SWARM_COUNT files in data/swarms/"
echo -e "  ${GREEN}✓${NC} Testing:     $TEST_COUNT files in data/testing/"
echo -e "  ${GREEN}✓${NC} Shopping:    $SHOPPING_COUNT files in data/shopping/"

echo ""
echo -e "${YELLOW}Quick Access:${NC}"
echo -e "  ${CYAN}Master Index:${NC}     data/omega-omni-master-index.json"
echo -e "  ${CYAN}Latest Discovery:${NC} $(ls -t data/discoveries/*.json 2>/dev/null | head -1 || echo 'None')"
echo -e "  ${CYAN}Latest Solutions:${NC} $(ls -t data/solutions/*.json 2>/dev/null | head -1 || echo 'None')"
echo -e "  ${CYAN}Swarm Config:${NC}     $(ls -t data/swarms/*.json 2>/dev/null | head -1 || echo 'None')"

echo ""
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ OMEGA-OMNI PROTOCOL EXECUTION COMPLETE${NC}"
echo -e "${MAGENTA}═══════════════════════════════════════════════════════════════════${NC}"

# Usage reminder
echo ""
echo -e "${CYAN}Next Steps:${NC}"
echo "  1. Review artifacts in data/ directories"
echo "  2. Implement high-priority solutions from data/solutions/"
echo "  3. Activate agent swarms for continuous operation"
echo "  4. Monitor test results and fix any issues"
echo "  5. Utilize resources from data/shopping/"
echo ""
echo -e "${YELLOW}Full Documentation:${NC} OMEGA_OMNI_MASTER_GUIDE.md"
echo ""
