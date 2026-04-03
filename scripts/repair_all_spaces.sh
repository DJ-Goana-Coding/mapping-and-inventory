#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# MULTI-SPACE REPAIR MASTER SCRIPT (v26.0.OMNI++)
# ═══════════════════════════════════════════════════════════════════
# Purpose: Repair all crashing HuggingFace Spaces in one shot
# Spaces: TIA-ARCHITECT-CORE, tias-citadel, tias-sentinel-scout-swarm-2
# Authority: Citadel Architect
# ═══════════════════════════════════════════════════════════════════

set -e

echo "🔧 CITADEL SPACE REPAIR MASTER - MULTI-SPACE FIX"
echo "═══════════════════════════════════════════════════════════════════"

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
GITHUB_ORG="DJ-Goana-Coding"
HF_ORG="DJ-Goanna-Coding"

# Space configurations
declare -A SPACES
SPACES[TIA-ARCHITECT-CORE]="tia-architect-core-templates"
SPACES[tias-citadel]="tia-citadel-templates"
SPACES[tias-sentinel-scout-swarm-2]="sentinel-scout-templates"

# Statistics
TOTAL_SPACES=${#SPACES[@]}
REPAIRED=0
FAILED=0

echo "📊 Target Spaces: $TOTAL_SPACES"
echo "   - TIA-ARCHITECT-CORE (pandas/numpy Python 3.13 fix)"
echo "   - tias-citadel (core dependencies fix)"
echo "   - tias-sentinel-scout-swarm-2 (pandas-ta Python 3.11 fix)"
echo ""

# Function to repair a single space
repair_space() {
    local SPACE_NAME=$1
    local TEMPLATE_DIR=$2
    
    echo "═══════════════════════════════════════════════════════════════════"
    echo "🔧 Repairing: $SPACE_NAME"
    echo "═══════════════════════════════════════════════════════════════════"
    
    # Check template directory exists
    if [ ! -d "$REPO_ROOT/$TEMPLATE_DIR" ]; then
        echo "❌ ERROR: Template directory not found: $TEMPLATE_DIR"
        ((FAILED++))
        return 1
    fi
    
    # Set target repo path
    TARGET_REPO="${TARGET_REPO_BASE:-$HOME}/$SPACE_NAME"
    
    # Clone if doesn't exist
    if [ ! -d "$TARGET_REPO" ]; then
        echo "📥 Cloning $SPACE_NAME..."
        git clone "https://github.com/$GITHUB_ORG/$SPACE_NAME" "$TARGET_REPO" || {
            echo "❌ Failed to clone $SPACE_NAME"
            ((FAILED++))
            return 1
        }
    fi
    
    cd "$TARGET_REPO"
    
    # Pull latest
    echo "🔄 Pulling latest changes..."
    git fetch origin
    git checkout main
    git pull origin main
    
    # Backup existing files
    if [ -f "requirements.txt" ]; then
        BACKUP_FILE="requirements.txt.backup.$(date +%Y%m%d_%H%M%S)"
        echo "💾 Backing up requirements.txt → $BACKUP_FILE"
        cp requirements.txt "$BACKUP_FILE"
    fi
    
    # Copy template files
    echo "📋 Deploying templates..."
    cp "$REPO_ROOT/$TEMPLATE_DIR/requirements.txt" requirements.txt
    
    # Copy .python-version if exists
    if [ -f "$REPO_ROOT/$TEMPLATE_DIR/.python-version" ]; then
        cp "$REPO_ROOT/$TEMPLATE_DIR/.python-version" .python-version
        echo "✅ Deployed .python-version"
    fi
    
    # Show changes
    echo ""
    echo "📊 Changes made:"
    git diff requirements.txt || echo "   (new file)"
    
    # Commit changes
    git add requirements.txt .python-version 2>/dev/null || git add requirements.txt
    
    if git diff --cached --quiet; then
        echo "ℹ️  No changes needed for $SPACE_NAME"
        return 0
    fi
    
    git commit -m "🔧 STAINLESS WELD: Fix Space crash - Apply repair template

Space: $SPACE_NAME
Template: $TEMPLATE_DIR
Issues Fixed:
- Dependencies compatibility
- Python version alignment
- Missing packages

Deployed by: Multi-Space Repair Master
Architect: v26.0.OMNI++"
    
    # Push to GitHub
    echo "⬆️  Pushing to GitHub..."
    git push origin main || {
        echo "❌ Failed to push $SPACE_NAME"
        ((FAILED++))
        return 1
    }
    
    echo "✅ Successfully repaired $SPACE_NAME"
    ((REPAIRED++))
    
    cd "$REPO_ROOT"
    return 0
}

# Repair all spaces
for SPACE_NAME in "${!SPACES[@]}"; do
    TEMPLATE_DIR="${SPACES[$SPACE_NAME]}"
    repair_space "$SPACE_NAME" "$TEMPLATE_DIR" || true
    echo ""
done

# Summary
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ MULTI-SPACE REPAIR COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo "Total Spaces:    $TOTAL_SPACES"
echo "Repaired:        $REPAIRED ✅"
echo "Failed:          $FAILED ❌"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "📋 Next Steps:"
echo "   1. Monitor HuggingFace Space rebuilds:"
echo "      - https://huggingface.co/spaces/$HF_ORG/TIA-ARCHITECT-CORE/logs"
echo "      - https://huggingface.co/spaces/$HF_ORG/tias-citadel/logs"
echo "      - https://huggingface.co/spaces/$HF_ORG/tias-sentinel-scout-swarm-2/logs"
echo ""
echo "   2. Verify successful builds (look for):"
echo "      ✅ Successfully installed [packages]"
echo "      ✅ Running on local URL: http://0.0.0.0:7860"
echo ""
echo "Weld. Pulse. Ignite. 🔥"
echo ""

# Exit with appropriate code
if [ $FAILED -gt 0 ]; then
    exit 1
else
    exit 0
fi
