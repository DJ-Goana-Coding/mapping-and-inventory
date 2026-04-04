#!/bin/bash
#
# 🔧 AUTONOMOUS REPAIR SYSTEM - Quick Start
# One-command deployment for complete repo repair automation
#

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "================================="
echo "🔧 AUTONOMOUS REPAIR SYSTEM"
echo "================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    exit 1
fi

echo -e "${BLUE}🐍 Python 3: $(python3 --version)${NC}"

# Install dependencies
echo ""
echo -e "${YELLOW}📦 Installing dependencies...${NC}"
pip install -q requests

# Parse mode
MODE=${1:-full}

case $MODE in
    scan)
        echo -e "${GREEN}🔍 Running repository health scan...${NC}"
        python3 scripts/broken_repo_scanner.py
        ;;
    
    repair)
        echo -e "${GREEN}🔧 Running full repair cycle...${NC}"
        python3 scripts/repo_repair_orchestrator.py
        ;;
    
    full)
        echo -e "${GREEN}🚀 Running complete autonomous repair system...${NC}"
        echo ""
        
        # Step 1: Scan
        echo -e "${BLUE}Step 1/3: Scanning repositories...${NC}"
        python3 scripts/broken_repo_scanner.py
        
        echo ""
        
        # Step 2: Repair
        echo -e "${BLUE}Step 2/3: Repairing broken repos...${NC}"
        python3 scripts/repo_repair_orchestrator.py
        
        echo ""
        
        # Step 3: Report
        echo -e "${BLUE}Step 3/3: Generating final report...${NC}"
        
        # Find latest repair session
        LATEST_SESSION=$(ls -t data/repairs/session_*.json 2>/dev/null | head -1)
        if [ -f "$LATEST_SESSION" ]; then
            echo -e "${GREEN}✅ Repair session complete!${NC}"
            echo ""
            echo "Session data: $LATEST_SESSION"
            
            # Extract key metrics
            REPOS_SCANNED=$(jq -r '.repos_scanned | length' "$LATEST_SESSION")
            REPOS_BROKEN=$(jq -r '.repos_broken | length' "$LATEST_SESSION")
            PROBLEMS_FIXED=$(jq -r '.problems_fixed' "$LATEST_SESSION")
            
            echo ""
            echo "📊 Summary:"
            echo "  - Repositories scanned: $REPOS_SCANNED"
            echo "  - Broken repos found: $REPOS_BROKEN"
            echo "  - Problems fixed: $PROBLEMS_FIXED"
        fi
        ;;
    
    status)
        echo -e "${GREEN}📊 Checking repair system status...${NC}"
        echo ""
        
        # Check for recent scans
        SCAN_COUNT=$(ls data/monitoring/health_scan_*.json 2>/dev/null | wc -l)
        echo "Health scans performed: $SCAN_COUNT"
        
        # Check for repair sessions
        SESSION_COUNT=$(ls data/repairs/session_*.json 2>/dev/null | wc -l)
        echo "Repair sessions: $SESSION_COUNT"
        
        # Check for repair catalog
        REPAIR_COUNT=$(ls data/repairs/repair_catalog/*.json 2>/dev/null | wc -l)
        echo "Repairs documented: $REPAIR_COUNT"
        
        # Check for parts catalog
        PARTS_COUNT=$(ls data/repairs/parts_catalog/*.json 2>/dev/null | wc -l)
        echo "Parts stored: $PARTS_COUNT"
        ;;
    
    *)
        echo -e "${YELLOW}Usage: $0 [scan|repair|full|status]${NC}"
        echo ""
        echo "Modes:"
        echo "  scan   - Scan all repos for health issues"
        echo "  repair - Run full repair cycle"
        echo "  full   - Complete scan + repair + report (default)"
        echo "  status - Check system status"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done!${NC}"
