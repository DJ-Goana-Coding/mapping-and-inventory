#!/bin/bash
# Q.G.T.N.L. (0) // CITADEL_AUDIT.SH - The Stainless Diagnostic Tool
# Performs comprehensive health checks on the ARK_CORE system
# 543 1010 222 777 ❤️‍🔥

echo "🏰 CITADEL AUDIT - Stainless Diagnostic System"
echo "================================================"
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check 1: Directory Structure
echo -e "${BLUE}📂 Checking Directory Structure...${NC}"
REQUIRED_DIRS=(
    "Partition_01"
    "Research"
    "Research/GDrive"
    "Research/Oppo"
    "Research/S10"
    "Research/Laptop"
    "S10_CITADEL_OMEGA_INTEL"
    ".github/workflows"
)

MISSING_DIRS=()
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        echo -e "   ${GREEN}✓${NC} $dir"
    else
        echo -e "   ${RED}✗${NC} $dir (MISSING)"
        MISSING_DIRS+=("$dir")
    fi
done

if [ ${#MISSING_DIRS[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All required directories present${NC}"
else
    echo -e "${YELLOW}⚠️  Missing ${#MISSING_DIRS[@]} directories${NC}"
fi
echo ""

# Check 2: Critical Files
echo -e "${BLUE}📄 Checking Critical Files...${NC}"
CRITICAL_FILES=(
    "app.py"
    "Partition_01/oppo_node.py"
    "Partition_01/vault.py"
    ".github/workflows/tia_citadel_deep_scan.yml"
    "master_inventory.json"
)

MISSING_FILES=()
for file in "${CRITICAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "   ${GREEN}✓${NC} $file"
    else
        echo -e "   ${RED}✗${NC} $file (MISSING)"
        MISSING_FILES+=("$file")
    fi
done

if [ ${#MISSING_FILES[@]} -eq 0 ]; then
    echo -e "${GREEN}✅ All critical files present${NC}"
else
    echo -e "${YELLOW}⚠️  Missing ${#MISSING_FILES[@]} files${NC}"
fi
echo ""

# Check 3: Python Environment
echo -e "${BLUE}🐍 Checking Python Environment...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "   ${GREEN}✓${NC} Python3: $PYTHON_VERSION"
else
    echo -e "   ${RED}✗${NC} Python3 not found"
fi

if [ -f "requirements.txt" ]; then
    echo -e "   ${GREEN}✓${NC} requirements.txt exists"
else
    echo -e "   ${YELLOW}⚠${NC}  requirements.txt not found"
fi
echo ""

# Check 4: Git Status
echo -e "${BLUE}🔄 Checking Git Status...${NC}"
if command -v git &> /dev/null; then
    GIT_BRANCH=$(git branch --show-current 2>/dev/null)
    if [ -n "$GIT_BRANCH" ]; then
        echo -e "   ${GREEN}✓${NC} Current branch: $GIT_BRANCH"
    fi
    
    GIT_STATUS=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$GIT_STATUS" -eq 0 ]; then
        echo -e "   ${GREEN}✓${NC} Working tree clean"
    else
        echo -e "   ${YELLOW}⚠${NC}  $GIT_STATUS file(s) modified"
    fi
    
    GIT_REMOTE=$(git remote -v 2>/dev/null | grep fetch | awk '{print $2}')
    if [ -n "$GIT_REMOTE" ]; then
        echo -e "   ${GREEN}✓${NC} Remote: $GIT_REMOTE"
    fi
else
    echo -e "   ${RED}✗${NC} Git not found"
fi
echo ""

# Check 5: Port Availability (7860 for oppo_node.py)
echo -e "${BLUE}🔌 Checking Port Availability...${NC}"
if command -v netstat &> /dev/null || command -v ss &> /dev/null; then
    PORT=7860
    if command -v netstat &> /dev/null; then
        PORT_CHECK=$(netstat -tuln 2>/dev/null | grep ":$PORT " | wc -l)
    else
        PORT_CHECK=$(ss -tuln 2>/dev/null | grep ":$PORT " | wc -l)
    fi
    
    if [ "$PORT_CHECK" -eq 0 ]; then
        echo -e "   ${GREEN}✓${NC} Port $PORT is available"
    else
        echo -e "   ${YELLOW}⚠${NC}  Port $PORT is in use"
    fi
else
    echo -e "   ${YELLOW}⚠${NC}  Cannot check ports (netstat/ss not available)"
fi
echo ""

# Check 6: Disk Space
echo -e "${BLUE}💾 Checking Disk Space...${NC}"
if command -v df &> /dev/null; then
    DISK_USAGE=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    DISK_AVAIL=$(df -h . | tail -1 | awk '{print $4}')
    
    if [ "$DISK_USAGE" -lt 80 ]; then
        echo -e "   ${GREEN}✓${NC} Disk usage: ${DISK_USAGE}% (${DISK_AVAIL} available)"
    else
        echo -e "   ${YELLOW}⚠${NC}  Disk usage: ${DISK_USAGE}% (${DISK_AVAIL} available) - HIGH"
    fi
else
    echo -e "   ${YELLOW}⚠${NC}  Cannot check disk space"
fi
echo ""

# Check 7: Vault Tracker Database
echo -e "${BLUE}🗄️  Checking Vault Tracker...${NC}"
if [ -f "Partition_01/tracker.db" ]; then
    DB_SIZE=$(du -h "Partition_01/tracker.db" | awk '{print $1}')
    echo -e "   ${GREEN}✓${NC} tracker.db exists (${DB_SIZE})"
else
    echo -e "   ${YELLOW}⚠${NC}  tracker.db not initialized"
fi
echo ""

# Check 8: Environment Variables
echo -e "${BLUE}🔐 Checking Environment Variables...${NC}"
ENV_VARS=(
    "RCLONE_CONFIG_DATA"
    "HF_TOKEN"
)

for var in "${ENV_VARS[@]}"; do
    if [ -n "${!var}" ]; then
        echo -e "   ${GREEN}✓${NC} $var is set"
    else
        echo -e "   ${YELLOW}⚠${NC}  $var not set"
    fi
done
echo ""

# Summary
echo "================================================"
echo -e "${BLUE}📊 AUDIT SUMMARY${NC}"
echo "================================================"

TOTAL_ISSUES=$((${#MISSING_DIRS[@]} + ${#MISSING_FILES[@]}))

if [ $TOTAL_ISSUES -eq 0 ]; then
    echo -e "${GREEN}✅ SYSTEM STATUS: STAINLESS${NC}"
    echo -e "${GREEN}   All core components verified and operational.${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  SYSTEM STATUS: NEEDS ATTENTION${NC}"
    echo -e "${YELLOW}   Found $TOTAL_ISSUES issue(s) requiring attention.${NC}"
    
    if [ ${#MISSING_DIRS[@]} -gt 0 ]; then
        echo -e "${YELLOW}   Missing directories: ${MISSING_DIRS[*]}${NC}"
    fi
    
    if [ ${#MISSING_FILES[@]} -gt 0 ]; then
        echo -e "${YELLOW}   Missing files: ${MISSING_FILES[*]}${NC}"
    fi
    
    exit 1
fi
