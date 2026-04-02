#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# CITADEL_AUDIT.SH — Stainless Architecture Diagnostic Tool
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Verify the "Stainless" ARK_CORE architecture is correctly configured
# Author: Architect Chance
# Version: 26.64.OMNI
# ═══════════════════════════════════════════════════════════════════════════

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Status tracking
PASS_COUNT=0
FAIL_COUNT=0
WARN_COUNT=0

# Helper functions
print_header() {
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}$1${NC}"
    echo -e "${PURPLE}═══════════════════════════════════════════════════════════════${NC}"
}

print_pass() {
    echo -e "${GREEN}✅ PASS:${NC} $1"
    ((PASS_COUNT++))
}

print_fail() {
    echo -e "${RED}❌ FAIL:${NC} $1"
    ((FAIL_COUNT++))
}

print_warn() {
    echo -e "${YELLOW}⚠️  WARN:${NC} $1"
    ((WARN_COUNT++))
}

print_info() {
    echo -e "${BLUE}ℹ️  INFO:${NC} $1"
}

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 1: DIRECTORY STRUCTURE VERIFICATION
# ═══════════════════════════════════════════════════════════════════════════

print_header "🏗️  SECTION 1: DIRECTORY STRUCTURE VERIFICATION"

# Check for required directories
REQUIRED_DIRS=(
    ".github/workflows"
    "Partition_01"
    "Partition_02"
    "Research"
    "Research/GDrive"
    "Research/Oppo"
    "Research/S10"
    "Research/Laptop"
    "S10_CITADEL_OMEGA_INTEL"
    "services"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$dir" ]; then
        print_pass "Directory exists: $dir"
    else
        print_fail "Missing directory: $dir"
    fi
done

# Check for key files
KEY_FILES=(
    "app.py"
    "master_inventory.json"
    "citadel_audit.sh"
    "worker_status.json"
    ".github/workflows/tia_citadel_deep_scan.yml"
)

for file in "${KEY_FILES[@]}"; do
    if [ -f "$file" ]; then
        print_pass "File exists: $file"
    else
        if [ "$file" == "worker_status.json" ]; then
            print_warn "File missing (will be created): $file"
        else
            print_fail "Missing file: $file"
        fi
    fi
done

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 2: ABSOLUTE PATH DETECTION (DIRTY WELDS)
# ═══════════════════════════════════════════════════════════════════════════

print_header "🔍 SECTION 2: ABSOLUTE PATH DETECTION (DIRTY WELDS)"

print_info "Scanning for absolute paths in Python and shell scripts..."

# Search for common absolute path patterns
DIRTY_PATHS=$(grep -r -n "/data/" --include="*.py" --include="*.sh" . 2>/dev/null || true)

if [ -z "$DIRTY_PATHS" ]; then
    print_pass "No '/data/' absolute paths found (Stainless!)"
else
    print_fail "Found absolute '/data/' paths:"
    echo "$DIRTY_PATHS"
fi

# Check for other absolute paths (excluding .git and comments)
SUSPICIOUS_PATHS=$(grep -r -E "^[^#]*['\"]/(home|root|mnt|media)" --include="*.py" --include="*.sh" . 2>/dev/null | grep -v ".git" | grep -v "^#" || true)

if [ -z "$SUSPICIOUS_PATHS" ]; then
    print_pass "No suspicious absolute paths found"
else
    print_warn "Found potentially problematic absolute paths:"
    echo "$SUSPICIOUS_PATHS" | head -10
fi

# Verify relative path usage
RELATIVE_PATHS=$(grep -r -E "\./Research/|~/ARK_CORE/" --include="*.py" --include="*.sh" . 2>/dev/null | wc -l)
if [ "$RELATIVE_PATHS" -gt 0 ]; then
    print_pass "Found $RELATIVE_PATHS references using relative paths"
else
    print_info "No relative path references found (may need to add more)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 3: RCLONE CONNECTIVITY TEST
# ═══════════════════════════════════════════════════════════════════════════

print_header "📡 SECTION 3: RCLONE CONNECTIVITY TEST"

# Check if rclone is installed
if command -v rclone &> /dev/null; then
    print_pass "rclone is installed"
    RCLONE_VERSION=$(rclone --version | head -1)
    print_info "Version: $RCLONE_VERSION"
else
    print_fail "rclone is NOT installed"
fi

# Check for rclone config
if [ -f ~/.config/rclone/rclone.conf ]; then
    print_pass "rclone config file exists: ~/.config/rclone/rclone.conf"
    
    # Check if gdrive remote is configured
    if rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
        print_pass "gdrive remote is configured"
        
        # Test connection (optional, can be slow)
        if [ "${SKIP_REMOTE_TEST:-0}" == "0" ]; then
            print_info "Testing gdrive connection (set SKIP_REMOTE_TEST=1 to skip)..."
            if timeout 30 rclone lsd gdrive: --max-depth 1 &> /dev/null; then
                print_pass "gdrive connection successful"
            else
                print_warn "gdrive connection test timed out or failed"
            fi
        else
            print_info "Skipping remote connection test (SKIP_REMOTE_TEST=1)"
        fi
    else
        print_fail "gdrive remote NOT configured in rclone"
    fi
elif [ -n "$RCLONE_CONFIG_DATA" ]; then
    print_pass "RCLONE_CONFIG_DATA environment variable is set"
else
    print_fail "No rclone configuration found"
fi

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 4: GITHUB SECRETS VALIDATION
# ═══════════════════════════════════════════════════════════════════════════

print_header "🔐 SECTION 4: GITHUB SECRETS VALIDATION"

# Check environment variables (secrets)
SECRETS=(
    "RCLONE_CONFIG_DATA"
    "GEMINI_API_KEY"
    "HF_TOKEN"
    "GITHUB_TOKEN"
)

for secret in "${SECRETS[@]}"; do
    if [ -n "${!secret}" ]; then
        print_pass "Secret set: $secret"
    else
        if [ "$secret" == "GOOGLE_SHEETS_CREDENTIALS" ]; then
            print_warn "Secret not set: $secret (needed for Reporter Worker)"
        else
            print_info "Secret not set: $secret"
        fi
    fi
done

# Check for GOOGLE_SHEETS_CREDENTIALS (needed for Reporter Worker)
if [ -n "$GOOGLE_SHEETS_CREDENTIALS" ]; then
    print_pass "GOOGLE_SHEETS_CREDENTIALS is set (Reporter Worker ready)"
else
    print_warn "GOOGLE_SHEETS_CREDENTIALS not set (Reporter Worker will not function)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 5: WORKER STATUS CHECK
# ═══════════════════════════════════════════════════════════════════════════

print_header "🤖 SECTION 5: WORKER STATUS CHECK"

# Check for worker scripts
WORKER_SCRIPTS=(
    "services/worker_archivist.py"
    "services/worker_reporter.py"
    "services/worker_hive_master.py"
    "services/worker_bridge.py"
)

for worker in "${WORKER_SCRIPTS[@]}"; do
    if [ -f "$worker" ]; then
        print_pass "Worker script exists: $worker"
    else
        print_warn "Worker script missing: $worker (needs implementation)"
    fi
done

# Check worker_status.json
if [ -f "worker_status.json" ]; then
    print_pass "worker_status.json exists"
    
    # Validate JSON
    if python3 -c "import json; json.load(open('worker_status.json'))" 2>/dev/null; then
        print_pass "worker_status.json is valid JSON"
    else
        print_fail "worker_status.json is invalid JSON"
    fi
else
    print_warn "worker_status.json does not exist (will be created)"
fi

# ═══════════════════════════════════════════════════════════════════════════
# SECTION 6: SYSTEM SUMMARY
# ═══════════════════════════════════════════════════════════════════════════

print_header "📊 SECTION 6: SYSTEM SUMMARY"

echo ""
echo -e "${CYAN}Repository Status:${NC}"
echo -e "  Location: $(pwd)"
echo -e "  Branch: $(git branch --show-current 2>/dev/null || echo 'N/A')"
echo -e "  Last commit: $(git log -1 --oneline 2>/dev/null || echo 'N/A')"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# FINAL SCORE
# ═══════════════════════════════════════════════════════════════════════════

print_header "🎯 FINAL AUDIT RESULTS"

TOTAL=$((PASS_COUNT + FAIL_COUNT + WARN_COUNT))
echo -e "${GREEN}✅ PASSED: $PASS_COUNT${NC}"
echo -e "${RED}❌ FAILED: $FAIL_COUNT${NC}"
echo -e "${YELLOW}⚠️  WARNINGS: $WARN_COUNT${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "   TOTAL CHECKS: $TOTAL"
echo ""

if [ $FAIL_COUNT -eq 0 ]; then
    if [ $WARN_COUNT -eq 0 ]; then
        echo -e "${GREEN}🏆 CITADEL STATUS: STAINLESS (100% OPERATIONAL)${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚙️  CITADEL STATUS: OPERATIONAL (with warnings)${NC}"
        exit 0
    fi
else
    echo -e "${RED}🔧 CITADEL STATUS: NEEDS ATTENTION${NC}"
    exit 1
fi
