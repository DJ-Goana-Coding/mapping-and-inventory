#!/bin/bash
################################################################################
# CITADEL_OMEGA Connection Verification Script
# Verifies the connection infrastructure between CITADEL_OMEGA and mapping-and-inventory
################################################################################

set -e

echo "════════════════════════════════════════════════════════════════════════════"
echo "🔍 CITADEL_OMEGA Connection Verification"
echo "════════════════════════════════════════════════════════════════════════════"
echo ""

REPO_ROOT="/home/runner/work/mapping-and-inventory/mapping-and-inventory"
cd "$REPO_ROOT"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SUCCESS=0
WARNINGS=0
FAILURES=0

check_pass() {
    echo -e "  ${GREEN}✅ $1${NC}"
    SUCCESS=$((SUCCESS + 1))
}

check_warn() {
    echo -e "  ${YELLOW}⚠️  $1${NC}"
    WARNINGS=$((WARNINGS + 1))
}

check_fail() {
    echo -e "  ${RED}❌ $1${NC}"
    FAILURES=$((FAILURES + 1))
}

echo "📋 Checking mapping-and-inventory infrastructure..."
echo ""

# Check 1: Agent configuration exists
echo "1️⃣  Checking agent configuration..."
if [ -f ".github/agents/citadel-omega.agent.md" ]; then
    check_pass "CITADEL_OMEGA agent configuration exists"
    
    # Verify content
    if grep -q "CITADEL_OMEGA Trading Intelligence Hub" ".github/agents/citadel-omega.agent.md"; then
        check_pass "Agent identity correctly configured"
    else
        check_warn "Agent configuration may be incomplete"
    fi
else
    check_fail "CITADEL_OMEGA agent configuration NOT found"
fi
echo ""

# Check 2: Workflow templates exist
echo "2️⃣  Checking workflow templates..."
if [ -f ".github/workflow-templates/spoke-to-hub-sync.yml" ]; then
    check_pass "Hub sync workflow template exists"
else
    check_fail "Hub sync workflow template NOT found"
fi

if [ -f ".github/workflow-templates/push-to-huggingface.yml" ]; then
    check_pass "HuggingFace push workflow template exists"
else
    check_fail "HuggingFace push workflow template NOT found"
fi
echo ""

# Check 3: Hub receiver workflow
echo "3️⃣  Checking hub receiver workflow..."
if [ -f ".github/workflows/spoke_sync_receiver.yml" ]; then
    check_pass "Spoke sync receiver workflow exists"
    
    # Verify it handles repository_dispatch
    if grep -q "repository_dispatch" ".github/workflows/spoke_sync_receiver.yml"; then
        check_pass "Receiver configured for repository_dispatch"
    else
        check_warn "Receiver may not handle repository_dispatch"
    fi
else
    check_fail "Spoke sync receiver workflow NOT found"
fi
echo ""

# Check 4: Data directories
echo "4️⃣  Checking data directories..."
if [ -d "data/spoke_artifacts" ]; then
    check_pass "Spoke artifacts directory exists"
else
    check_warn "Spoke artifacts directory NOT found (will be created on first sync)"
    mkdir -p data/spoke_artifacts
fi

if [ -d "data/spoke_artifacts/CITADEL_OMEGA" ]; then
    check_pass "CITADEL_OMEGA artifacts directory exists"
    
    # Check for artifacts
    artifact_count=$(ls -1 data/spoke_artifacts/CITADEL_OMEGA 2>/dev/null | wc -l)
    if [ "$artifact_count" -gt 0 ]; then
        check_pass "Found $artifact_count artifacts synced from CITADEL_OMEGA"
    else
        check_warn "No artifacts synced yet from CITADEL_OMEGA"
    fi
else
    check_warn "CITADEL_OMEGA artifacts directory NOT found (will be created on first sync)"
fi
echo ""

# Check 5: Registry files
echo "5️⃣  Checking registry files..."
if [ -f "data/spoke_sync_registry.json" ]; then
    check_pass "Spoke sync registry exists"
    
    # Check if CITADEL_OMEGA is registered
    if grep -q "CITADEL_OMEGA" "data/spoke_sync_registry.json"; then
        check_pass "CITADEL_OMEGA is registered in sync registry"
    else
        check_warn "CITADEL_OMEGA not yet registered (will be added on first sync)"
    fi
else
    check_warn "Spoke sync registry NOT found (will be created on first sync)"
fi

if [ -f "repo_bridge_registry.json" ]; then
    check_pass "Repository bridge registry exists"
    
    # Check if CITADEL_OMEGA is in registry
    if grep -q "CITADEL_OMEGA" "repo_bridge_registry.json"; then
        check_pass "CITADEL_OMEGA is in bridge registry"
    else
        check_warn "CITADEL_OMEGA not in bridge registry (run discover_all_repos.py)"
    fi
else
    check_warn "Repository bridge registry NOT found (run discover_all_repos.py)"
fi
echo ""

# Check 6: Documentation
echo "6️⃣  Checking documentation..."
if [ -f "CITADEL_OMEGA_CONNECTION_GUIDE.md" ]; then
    check_pass "CITADEL_OMEGA connection guide exists"
else
    check_warn "CITADEL_OMEGA connection guide NOT found"
fi

if [ -f "REPOSITORY_CONNECTION_GUIDE.md" ]; then
    check_pass "General repository connection guide exists"
else
    check_warn "General repository connection guide NOT found"
fi
echo ""

# Check 7: Deployment scripts
echo "7️⃣  Checking deployment scripts..."
if [ -f "scripts/deploy_workflows_to_spokes.py" ]; then
    check_pass "Workflow deployment script exists"
else
    check_fail "Workflow deployment script NOT found"
fi

if [ -f "scripts/discover_all_repos.py" ]; then
    check_pass "Repository discovery script exists"
else
    check_fail "Repository discovery script NOT found"
fi
echo ""

# Summary
echo "════════════════════════════════════════════════════════════════════════════"
echo "📊 Verification Summary"
echo "════════════════════════════════════════════════════════════════════════════"
echo -e "  ${GREEN}✅ Passed:  $SUCCESS${NC}"
echo -e "  ${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo -e "  ${RED}❌ Failed:  $FAILURES${NC}"
echo ""

if [ $FAILURES -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! Connection infrastructure is ready.${NC}"
    exit 0
elif [ $FAILURES -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Infrastructure is mostly ready, but there are warnings.${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Run: export GITHUB_TOKEN=your_token"
    echo "  2. Run: python scripts/discover_all_repos.py"
    echo "  3. Run: python scripts/deploy_workflows_to_spokes.py --repos CITADEL_OMEGA"
    exit 0
else
    echo -e "${RED}❌ Some critical checks failed. Fix issues before proceeding.${NC}"
    exit 1
fi
