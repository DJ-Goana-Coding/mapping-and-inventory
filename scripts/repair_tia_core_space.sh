#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# TIA-ARCHITECT-CORE Space Repair Script (Manual Implementation)
# ═══════════════════════════════════════════════════════════════════
# Purpose: Apply Python 3.13 compatible requirements.txt to fix Space
# Target: DJ-Goana-Coding/TIA-ARCHITECT-CORE
# Issue: Invalid streamlit version, numpy compilation timeout
# Fix: Apply tia-architect-core-templates/requirements.txt
# ═══════════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "═══════════════════════════════════════════════════════════════════"
echo "🔧 TIA-ARCHITECT-CORE SPACE REPAIR SCRIPT"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Configuration
GITHUB_ORG="DJ-Goana-Coding"
TARGET_REPO="TIA-ARCHITECT-CORE"
TEMPLATE_DIR="tia-architect-core-templates"
WORK_DIR="/tmp/tia-core-repair"

# Verify we're in mapping-and-inventory repo
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo -e "${RED}❌ ERROR: Must run from mapping-and-inventory repository${NC}"
    echo "   Template directory not found: $TEMPLATE_DIR"
    exit 1
fi

# Verify template exists
TEMPLATE_FILE="$TEMPLATE_DIR/requirements.txt"
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}❌ ERROR: Template not found at $TEMPLATE_FILE${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Verifying template...${NC}"
# Check for required packages
for pkg in "setuptools>=75.0.0" "streamlit>=1.42.0" "pandas>=2.2.0" "numpy>=2.0.0"; do
    if ! grep -q "$pkg" "$TEMPLATE_FILE"; then
        echo -e "${RED}❌ ERROR: Template missing $pkg${NC}"
        exit 1
    fi
done
echo -e "${GREEN}✅ Template verified${NC}"
echo ""

# Display key packages
echo "📦 Key packages in template:"
grep -E "(streamlit|setuptools|pandas|numpy|requests)" "$TEMPLATE_FILE" | head -6
echo ""

# Create work directory
echo -e "${BLUE}📁 Creating work directory...${NC}"
rm -rf "$WORK_DIR"
mkdir -p "$WORK_DIR"
cd "$WORK_DIR"

# Clone TIA-ARCHITECT-CORE repository
echo -e "${BLUE}📥 Cloning $TARGET_REPO repository...${NC}"
if [ -n "$GITHUB_TOKEN" ]; then
    # Use GITHUB_TOKEN if available (for GitHub Actions)
    git clone "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_ORG}/${TARGET_REPO}.git"
elif [ -n "$GH_PAT" ]; then
    # Use GH_PAT if available
    git clone "https://${GH_PAT}@github.com/${GITHUB_ORG}/${TARGET_REPO}.git"
else
    # Try without auth (will work if user is authenticated via gh)
    git clone "https://github.com/${GITHUB_ORG}/${TARGET_REPO}.git"
fi

cd "$TARGET_REPO"

# Configure git
git config user.name "Citadel Architect"
git config user.email "architect@citadel.mesh"

# Backup existing requirements.txt if it exists
if [ -f requirements.txt ]; then
    BACKUP_FILE="requirements.txt.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${YELLOW}💾 Backing up existing requirements.txt to $BACKUP_FILE${NC}"
    cp requirements.txt "$BACKUP_FILE"
    git add "$BACKUP_FILE"
    echo ""
else
    echo -e "${YELLOW}ℹ️  No existing requirements.txt found${NC}"
    echo ""
fi

# Get absolute path to template
TEMPLATE_PATH="$(cd ../.. && pwd)/$TEMPLATE_FILE"

# Copy template
echo -e "${BLUE}📋 Deploying Python 3.13 compatible template...${NC}"
cp "$TEMPLATE_PATH" requirements.txt

echo -e "${GREEN}✅ Template deployed${NC}"
echo ""

# Show preview of new requirements
echo "📊 New requirements.txt preview:"
head -20 requirements.txt
echo "..."
echo ""

# Show diff if there was an existing file
if [ -f "$BACKUP_FILE" ]; then
    echo "🔍 Changes from previous version:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    diff "$BACKUP_FILE" requirements.txt || true
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
fi

# Stage changes
git add requirements.txt

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo -e "${GREEN}ℹ️  No changes needed - requirements.txt already up to date${NC}"
    echo ""
    exit 0
fi

# Commit changes
echo -e "${BLUE}💾 Committing changes...${NC}"
git commit -m "🔧 STAINLESS WELD: Fix Space build - Python 3.13 compatible dependencies

Root Cause:
- streamlit==1.56.0 (invalid version, doesn't exist in PyPI)
- numpy==1.26.4 (compiling from source, timing out on Python 3.13)
- Missing setuptools causing pkg_resources errors
- Build paused after 15+ minutes of numpy compilation

Fix Applied:
- ✅ streamlit>=1.42.0 (valid version with range)
- ✅ numpy>=2.0.0 (prebuilt wheels, Python 3.13 optimized)
- ✅ pandas>=2.2.0 (Python 3.13 compatible)
- ✅ requests>=2.32.0 (updated from 2.31.0)
- ✅ setuptools>=75.0.0 (explicit declaration)

Expected Outcome:
- Build time: ~2 minutes (was timing out at 15+ minutes)
- All packages install from wheels (no compilation)
- Space becomes operational

Resolves: HuggingFace Space build failure (commit SHA: 942f3e9)
Template: mapping-and-inventory/tia-architect-core-templates/requirements.txt
Deployed by: Citadel Architect repair script
Authority: GitHub > HF Spaces (Core Directive #1)"

echo -e "${GREEN}✅ Changes committed${NC}"
echo ""

# Push changes
echo -e "${BLUE}⬆️  Pushing to GitHub...${NC}"
git push origin main

echo -e "${GREEN}✅ Changes pushed to GitHub${NC}"
echo ""

# Clean up
cd /
rm -rf "$WORK_DIR"

# Success summary
echo "═══════════════════════════════════════════════════════════════════"
echo -e "${GREEN}✅ TIA-ARCHITECT-CORE SPACE REPAIR COMPLETE${NC}"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo ""
echo "   1. Monitor HuggingFace Space rebuild:"
echo "      https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs"
echo ""
echo "   2. Expected in build logs:"
echo "      ✅ Successfully installed setuptools-75.x.x"
echo "      ✅ Successfully installed streamlit-1.4x.x"
echo "      ✅ Successfully installed pandas-2.2.x"
echo "      ✅ Successfully installed numpy-2.x.x (wheel, not tar.gz)"
echo "      ✅ Running on local URL: http://0.0.0.0:7860"
echo ""
echo "   3. Verify Space accessibility:"
echo "      https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE"
echo ""
echo "   4. Build time comparison:"
echo "      Before: 31s cache + 15+ min numpy compilation (timeout)"
echo "      After:  31s cache + 90s pip install = ~2 minutes total"
echo ""
echo "🔧 Template: tia-architect-core-templates/requirements.txt"
echo "📡 Repository: DJ-Goana-Coding/TIA-ARCHITECT-CORE"
echo "🔗 Double-N Rift: GitHub (DJ-Goana-Coding) → HF (DJ-Goanna-Coding)"
echo ""
echo "Weld. Pulse. Ignite. 🔥"
echo ""
