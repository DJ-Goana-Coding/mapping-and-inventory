#!/bin/bash
# ARK_CORE // CITADEL_AUDIT.SH
# Stainless Diagnostic Tool for Oppo/S10 synchronization
# Version: V26.59.OMNI

set -e

echo "🏰 =============================================="
echo "   CITADEL STAINLESS DIAGNOSTIC TOOL"
echo "   ARK_CORE Architecture Audit"
echo "   Version: V26.59.OMNI"
echo "============================================== 🏰"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check directory existence
check_directory() {
    local dir=$1
    local label=$2
    
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✅${NC} $label: $dir"
        file_count=$(find "$dir" -type f 2>/dev/null | wc -l)
        echo "   └─ Files: $file_count"
    else
        echo -e "${RED}❌${NC} $label: $dir ${RED}(MISSING)${NC}"
    fi
}

# Function to check file existence
check_file() {
    local file=$1
    local label=$2
    
    if [ -f "$file" ]; then
        size=$(du -h "$file" 2>/dev/null | cut -f1)
        echo -e "${GREEN}✅${NC} $label: $file (Size: $size)"
    else
        echo -e "${YELLOW}⚠️${NC}  $label: $file ${YELLOW}(NOT FOUND)${NC}"
    fi
}

# Function to check for absolute paths
check_absolute_paths() {
    echo -e "\n${BLUE}🔍 SCANNING FOR ABSOLUTE PATHS (/data/)...${NC}"
    
    matches=$(grep -r "/data/" --include="*.py" --include="*.sh" --include="*.yml" --include="*.yaml" \
              --exclude-dir=".git" --exclude-dir="__pycache__" \
              . 2>/dev/null | wc -l)
    
    if [ "$matches" -eq 0 ]; then
        echo -e "${GREEN}✅${NC} No absolute paths found - STAINLESS COMPLIANT"
    else
        echo -e "${RED}❌${NC} Found $matches absolute path references - NEEDS FIXING"
        echo -e "${YELLOW}Run this to see them:${NC}"
        echo "grep -r '/data/' --include='*.py' --include='*.sh' --include='*.yml' ."
    fi
}

# 1. Check Directory Structure
echo -e "${BLUE}📂 DIRECTORY STRUCTURE AUDIT${NC}"
echo "────────────────────────────────────────────────"
check_directory ".github/workflows" "Titan's Brain"
check_directory "Partition_01" "Oppo District"
check_directory "Partition_02" "S10 District"
check_directory "Research" "Cargo Bays"
check_directory "Research/GDrive" "GDrive Cargo"
check_directory "Research/Oppo" "Oppo Cargo"
check_directory "Research/S10" "S10 Cargo"
check_directory "Research/Laptop" "Laptop Cargo"
check_directory "S10_CITADEL_OMEGA_INTEL" "Forensic District"

# 2. Check Critical Files
echo -e "\n${BLUE}📄 CRITICAL FILES AUDIT${NC}"
echo "────────────────────────────────────────────────"
check_file "Partition_01/oppo_node.py" "Oppo Node Script"
check_file "Partition_01/vault.py" "Vault Archive Logic"
check_file "Partition_02/s10_uplink.py" "S10 Uplink Script"
check_file "Partition_02/forensic_ingest.py" "Forensic Ingest Script"
check_file "app.py" "Streamlit Faceplate"
check_file "master_inventory.json" "Master Inventory"
check_file "master_intelligence_map.txt" "Intelligence Map"
check_file ".github/workflows/tia_citadel_deep_scan.yml" "Titan Workflow"

# 3. Check for Absolute Paths
check_absolute_paths

# 4. Check Git Status
echo -e "\n${BLUE}🔧 GIT STATUS${NC}"
echo "────────────────────────────────────────────────"
if git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${GREEN}✅${NC} Git repository detected"
    
    current_branch=$(git branch --show-current)
    echo "   └─ Current branch: $current_branch"
    
    # Check for uncommitted changes
    if git diff-index --quiet HEAD -- 2>/dev/null; then
        echo -e "${GREEN}✅${NC} No uncommitted changes"
    else
        echo -e "${YELLOW}⚠️${NC}  Uncommitted changes detected"
    fi
    
    # Check remotes
    remotes=$(git remote -v | head -2)
    if [ -n "$remotes" ]; then
        echo -e "${GREEN}✅${NC} Git remotes configured:"
        echo "$remotes" | sed 's/^/   /'
    fi
else
    echo -e "${RED}❌${NC} Not a git repository"
fi

# 5. Check Python Environment
echo -e "\n${BLUE}🐍 PYTHON ENVIRONMENT${NC}"
echo "────────────────────────────────────────────────"
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version 2>&1)
    echo -e "${GREEN}✅${NC} Python: $python_version"
else
    echo -e "${RED}❌${NC} Python3 not found"
fi

# 6. Check Rclone
echo -e "\n${BLUE}☁️  RCLONE STATUS${NC}"
echo "────────────────────────────────────────────────"
if command -v rclone &> /dev/null; then
    rclone_version=$(rclone version 2>&1 | head -1)
    echo -e "${GREEN}✅${NC} Rclone: $rclone_version"
    
    # Check for config
    if [ -f "$HOME/.config/rclone/rclone.conf" ]; then
        echo -e "${GREEN}✅${NC} Rclone config file exists"
    elif [ -n "$RCLONE_CONFIG_DATA" ]; then
        echo -e "${GREEN}✅${NC} RCLONE_CONFIG_DATA environment variable set"
    else
        echo -e "${YELLOW}⚠️${NC}  No rclone config detected"
    fi
else
    echo -e "${YELLOW}⚠️${NC}  Rclone not installed"
fi

# 7. Device Detection
echo -e "\n${BLUE}📱 DEVICE DETECTION${NC}"
echo "────────────────────────────────────────────────"
if [ -d "/data/data/com.termux" ]; then
    echo -e "${GREEN}✅${NC} Termux environment detected (Oppo/S10)"
    termux_version=$(termux-info 2>/dev/null | grep "TERMUX_VERSION" || echo "Version unknown")
    echo "   └─ $termux_version"
elif [ -f "/.dockerenv" ]; then
    echo -e "${BLUE}🐳${NC} Docker environment detected"
elif [ -n "$GITHUB_ACTIONS" ]; then
    echo -e "${BLUE}🔧${NC} GitHub Actions environment detected"
else
    echo -e "${BLUE}💻${NC} Standard Linux/Unix environment"
fi

# 8. Summary
echo -e "\n${BLUE}📊 AUDIT SUMMARY${NC}"
echo "════════════════════════════════════════════════"
echo "Audit completed at: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "Review the results above and address any issues marked with ❌ or ⚠️"
echo ""
echo "For full path compliance check, run:"
echo "  grep -r '/data/' --include='*.py' --include='*.sh' ."
echo ""
echo "🏰 CITADEL STAINLESS AUDIT COMPLETE 🏰"
