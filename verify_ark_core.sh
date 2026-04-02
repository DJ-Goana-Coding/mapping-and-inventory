#!/bin/bash
# ARK_CORE System Verification Test
# Quick verification that all fixes are in place
# 543 1010 222 777 ❤️‍🔥

echo "🏰 ARK_CORE System Verification"
echo "================================"
echo ""

PASS=0
FAIL=0

# Test 1: Check relative paths in gdrive_connector.py
echo "Test 1: Verifying relative paths in services/gdrive_connector.py"
if grep -q "./Research/Genesis" services/gdrive_connector.py && \
   ! grep -q "/data/Research" services/gdrive_connector.py; then
    echo "   ✅ PASS - Using relative paths"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - Absolute paths detected"
    FAIL=$((FAIL+1))
fi

# Test 2: Check relative paths in src/streamlit_app.py
echo "Test 2: Verifying relative paths in src/streamlit_app.py"
if grep -q "./Research/Genesis" src/streamlit_app.py && \
   ! grep -q "/data/Research" src/streamlit_app.py; then
    echo "   ✅ PASS - Using relative paths"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - Absolute paths detected"
    FAIL=$((FAIL+1))
fi

# Test 3: Verify vault.py exists and is executable as module
echo "Test 3: Verifying vault.py functionality"
if python3 Partition_01/vault.py stats > /dev/null 2>&1; then
    echo "   ✅ PASS - vault.py is functional"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - vault.py has errors"
    FAIL=$((FAIL+1))
fi

# Test 4: Check directory structure
echo "Test 4: Verifying directory structure"
DIRS_OK=true
for dir in "Research/GDrive" "Research/Oppo" "Research/S10" "Research/Laptop" "S10_CITADEL_OMEGA_INTEL"; do
    if [ ! -d "$dir" ]; then
        DIRS_OK=false
        break
    fi
done

if $DIRS_OK; then
    echo "   ✅ PASS - All required directories exist"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - Missing directories"
    FAIL=$((FAIL+1))
fi

# Test 5: Check oppo_node.py port configuration
echo "Test 5: Verifying oppo_node.py port configuration"
if grep -q "PORT = 7860" Partition_01/oppo_node.py; then
    echo "   ✅ PASS - Port 7860 configured"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - Port not correctly configured"
    FAIL=$((FAIL+1))
fi

# Test 6: Verify workflow has commit step
echo "Test 6: Verifying workflow commits intelligence map"
if grep -q "Commit Intelligence Map" .github/workflows/tia_citadel_deep_scan.yml; then
    echo "   ✅ PASS - Workflow configured to commit map"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - Workflow missing commit step"
    FAIL=$((FAIL+1))
fi

# Test 7: Check documentation exists
echo "Test 7: Verifying documentation"
if [ -f "ARK_CORE_MANIFESTO.md" ] && [ -f "citadel_audit.sh" ]; then
    echo "   ✅ PASS - Documentation complete"
    PASS=$((PASS+1))
else
    echo "   ❌ FAIL - Missing documentation"
    FAIL=$((FAIL+1))
fi

# Summary
echo ""
echo "================================"
echo "Results: ${PASS} PASS, ${FAIL} FAIL"
echo "================================"

if [ $FAIL -eq 0 ]; then
    echo "✅ ALL TESTS PASSED - SYSTEM IS STAINLESS"
    exit 0
else
    echo "❌ SOME TESTS FAILED - REVIEW NEEDED"
    exit 1
fi
