#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# TIA-ARCHITECT-CORE SPACE REPAIR SCRIPT (v25.0.OMNI)
# ═══════════════════════════════════════════════════════════════════
# Purpose: Deploy Python 3.13 compatible requirements.txt to fix crashing Space
# Target: DJ-Goanna-Coding/TIA-ARCHITECT-CORE HuggingFace Space
# Issue: ModuleNotFoundError: No module named 'pkg_resources' (exit code 1)
# Fix: Upgrade pandas to 2.2+, numpy to 2.0+, add setuptools>=75.0.0
# ═══════════════════════════════════════════════════════════════════

set -e

echo "🧠 TIA-ARCHITECT-CORE SPACE REPAIR SEQUENCE INITIATED"
echo "═══════════════════════════════════════════════════════════════════"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEMPLATE_DIR="$REPO_ROOT/tia-architect-core-templates"
TIA_CORE_REPO="${TIA_CORE_REPO:-$HOME/TIA-ARCHITECT-CORE}"
GITHUB_ORG="DJ-Goana-Coding"
HF_ORG="DJ-Goanna-Coding"

echo "📂 Configuration:"
echo "   Template Dir: $TEMPLATE_DIR"
echo "   Target Repo:  $TIA_CORE_REPO"
echo "   GitHub Org:   $GITHUB_ORG (Single-N)"
echo "   HF Org:       $HF_ORG (Double-N)"
echo ""

# Check if template exists
if [ ! -f "$TEMPLATE_DIR/requirements.txt" ]; then
    echo "❌ ERROR: Template requirements.txt not found at $TEMPLATE_DIR"
    echo "   Expected: $TEMPLATE_DIR/requirements.txt"
    exit 1
fi

# Verify template has required packages
echo "🔍 Verifying template contains required packages..."
if ! grep -q "setuptools>=75.0.0" "$TEMPLATE_DIR/requirements.txt"; then
    echo "❌ ERROR: Template missing setuptools>=75.0.0"
    exit 1
fi

if ! grep -q "streamlit>=1.42.0" "$TEMPLATE_DIR/requirements.txt"; then
    echo "❌ ERROR: Template missing streamlit>=1.42.0"
    exit 1
fi

if ! grep -q "pandas>=2.2.0" "$TEMPLATE_DIR/requirements.txt"; then
    echo "❌ ERROR: Template missing pandas>=2.2.0 (Python 3.13 compatible)"
    exit 1
fi

if ! grep -q "numpy>=2.0.0" "$TEMPLATE_DIR/requirements.txt"; then
    echo "❌ ERROR: Template missing numpy>=2.0.0 (Python 3.13 compatible)"
    exit 1
fi

echo "✅ Template verified: Contains setuptools, streamlit, pandas>=2.2.0, numpy>=2.0.0"
echo ""

# Check if TIA-ARCHITECT-CORE repo exists
if [ ! -d "$TIA_CORE_REPO" ]; then
    echo "📥 TIA-ARCHITECT-CORE repository not found. Cloning..."
    
    # Determine where to clone
    TIA_CORE_PARENT="$(dirname "$TIA_CORE_REPO")"
    mkdir -p "$TIA_CORE_PARENT"
    
    echo "   Cloning from: https://github.com/$GITHUB_ORG/TIA-ARCHITECT-CORE"
    echo "   Into: $TIA_CORE_REPO"
    
    git clone "https://github.com/$GITHUB_ORG/TIA-ARCHITECT-CORE" "$TIA_CORE_REPO"
    
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: Failed to clone TIA-ARCHITECT-CORE repository"
        echo "   Please clone it manually or set TIA_CORE_REPO environment variable"
        exit 1
    fi
    
    echo "✅ Repository cloned successfully"
else
    echo "✅ TIA-ARCHITECT-CORE repository found at $TIA_CORE_REPO"
fi

# Navigate to TIA-ARCHITECT-CORE repo
cd "$TIA_CORE_REPO"
echo ""
echo "📁 Working directory: $(pwd)"

# Ensure we're on the main branch
echo "🔄 Ensuring main branch is up to date..."
git fetch origin
git checkout main
git pull origin main

# Backup existing requirements.txt if it exists
if [ -f "requirements.txt" ]; then
    BACKUP_FILE="requirements.txt.backup.$(date +%Y%m%d_%H%M%S)"
    echo "💾 Backing up existing requirements.txt → $BACKUP_FILE"
    cp requirements.txt "$BACKUP_FILE"
fi

# Copy template requirements.txt
echo "📋 Deploying Python 3.13 compatible requirements.txt..."
cp "$TEMPLATE_DIR/requirements.txt" requirements.txt

# Show what changed
echo ""
echo "📊 Requirements.txt deployed. Key packages:"
grep -E "(streamlit|setuptools|pandas|numpy)" requirements.txt | head -6
echo ""

# Commit the changes
echo "💾 Committing changes..."
git add requirements.txt

# Check if there are changes to commit
if git diff --cached --quiet; then
    echo "ℹ️  No changes detected. requirements.txt already up to date."
    echo "✅ TIA-ARCHITECT-CORE Space repair complete (no changes needed)"
    exit 0
fi

git commit -m "🔧 STAINLESS WELD: Fix Space crash - Add setuptools & upgrade to Python 3.13 compatible versions

- Add setuptools>=75.0.0 to fix ModuleNotFoundError: 'pkg_resources'
- Upgrade streamlit to >=1.42.0
- Upgrade pandas to >=2.2.0 (Python 3.13 compatible)
- Upgrade numpy to >=2.0.0 (Python 3.13 compatible)
- All dependencies now compatible with Python 3.13

Resolves: Space build failure (exit code 1)
Template: tia-architect-core-templates/requirements.txt
Architect: v25.0.OMNI"

echo "✅ Changes committed locally"
echo ""

# Push to GitHub
echo "⬆️  Pushing to GitHub ($GITHUB_ORG/TIA-ARCHITECT-CORE)..."
git push origin main

if [ $? -ne 0 ]; then
    echo "❌ ERROR: Failed to push to GitHub"
    echo "   Please push manually: cd $TIA_CORE_REPO && git push origin main"
    exit 1
fi

echo "✅ Pushed to GitHub successfully"
echo ""

# Optional: Push to HuggingFace if remote exists
if git remote | grep -q "^hf$"; then
    echo "⬆️  HuggingFace remote found. Pushing to HF Space..."
    git push --force hf main
    
    if [ $? -eq 0 ]; then
        echo "✅ Pushed to HuggingFace Space successfully"
    else
        echo "⚠️  Warning: Failed to push to HuggingFace Space"
        echo "   Space will sync automatically from GitHub"
    fi
else
    echo "ℹ️  No HuggingFace remote configured (normal for GitHub-only repos)"
    echo "   HuggingFace Space will auto-sync from GitHub"
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ TIA-ARCHITECT-CORE SPACE REPAIR COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo "   1. Monitor HuggingFace Space rebuild:"
echo "      https://huggingface.co/spaces/$HF_ORG/TIA-ARCHITECT-CORE/logs"
echo ""
echo "   2. Expected in build logs:"
echo "      ✅ Successfully installed setuptools-75.x.x"
echo "      ✅ Successfully installed pandas-2.2.x"
echo "      ✅ Successfully installed numpy-2.x.x"
echo "      ✅ Successfully installed streamlit-1.4x.x"
echo "      ✅ Running on local URL: http://0.0.0.0:7860"
echo ""
echo "   3. Once build succeeds, access the Space:"
echo "      https://huggingface.co/spaces/$HF_ORG/TIA-ARCHITECT-CORE"
echo ""
echo "   4. Verify all tabs load without errors"
echo ""
echo "🔧 Repair template applied from: $TEMPLATE_DIR/requirements.txt"
echo "🛰️  Target repository: $TIA_CORE_REPO"
echo "📡 GitHub commit pushed to: $GITHUB_ORG/TIA-ARCHITECT-CORE"
echo ""
echo "Weld. Pulse. Ignite. 🔥"
echo ""
