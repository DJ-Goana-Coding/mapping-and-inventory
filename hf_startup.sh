#!/bin/bash
# 🏛️ CITADEL HF SPACE STARTUP PROTOCOL
# Executes on HuggingFace Space initialization
# Authority: Core Directive #4, #16 (Pull-over-Push)

set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏛️ CITADEL SURVEYOR - HF SPACE STARTUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📅 Startup Time: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Configuration
GITHUB_REPO="https://github.com/DJ-Goana-Coding/mapping-and-inventory"
GITHUB_BRANCH="${GITHUB_BRANCH:-main}"
REPO_DIR="${REPO_DIR:-/home/user/app}"

# 1. Git Configuration
echo "🔧 Configuring Git..."
git config --global user.email "hf-space@citadel.ai"
git config --global user.name "Citadel Surveyor HF Space"
git config --global pull.rebase false

# 2. Verify GitHub Connection
echo "📡 Verifying GitHub connection..."
if ! git ls-remote "$GITHUB_REPO" &>/dev/null; then
  echo "⚠️ WARNING: Cannot reach GitHub repository"
  echo "   Repository: $GITHUB_REPO"
  echo "   Proceeding with existing files..."
else
  echo "✅ GitHub repository accessible"
fi

# 3. Pull Latest from GitHub (if in a git repository)
if [ -d ".git" ]; then
  echo "📥 Pulling latest from GitHub ($GITHUB_BRANCH)..."
  
  # Ensure we have the remote configured
  if ! git remote get-url origin &>/dev/null; then
    echo "🔗 Adding GitHub remote..."
    git remote add origin "$GITHUB_REPO"
  fi
  
  # Fetch and reset to match GitHub
  echo "🔄 Syncing with GitHub..."
  git fetch origin "$GITHUB_BRANCH" --depth=1 || echo "⚠️ Fetch failed, using local files"
  
  # Only reset if fetch succeeded
  if git rev-parse origin/$GITHUB_BRANCH &>/dev/null; then
    git reset --hard origin/$GITHUB_BRANCH
    echo "✅ Repository synchronized with GitHub"
  else
    echo "⚠️ Using local repository state"
  fi
else
  echo "ℹ️ Not a git repository, skipping git pull"
  echo "   (HF Spaces may auto-sync via built-in mechanism)"
fi

# 4. Verify Critical Files
echo "🔍 Verifying repository integrity..."
CRITICAL_FILES=("app.py" "requirements.txt")
MISSING_FILES=()

for file in "${CRITICAL_FILES[@]}"; do
  if [ ! -f "$file" ]; then
    MISSING_FILES+=("$file")
  fi
done

if [ ${#MISSING_FILES[@]} -gt 0 ]; then
  echo "⚠️ WARNING: Missing critical files:"
  for file in "${MISSING_FILES[@]}"; do
    echo "   - $file"
  done
  echo ""
  echo "🔧 Attempting recovery..."
  
  # Try to pull specific files from GitHub
  for file in "${MISSING_FILES[@]}"; do
    echo "📥 Fetching $file from GitHub..."
    curl -f -o "$file" \
      "https://raw.githubusercontent.com/DJ-Goana-Coding/mapping-and-inventory/main/$file" \
      2>/dev/null && echo "   ✅ Retrieved $file" || echo "   ❌ Failed to retrieve $file"
  done
else
  echo "✅ All critical files present"
fi

# 5. Install Dependencies
echo "📦 Installing dependencies..."
if [ -f "requirements.txt" ]; then
  echo "   Installing from requirements.txt..."
  pip install -r requirements.txt --no-cache-dir --quiet || {
    echo "⚠️ Some dependencies failed to install"
    echo "   Continuing anyway..."
  }
  echo "✅ Dependencies installed"
else
  echo "⚠️ No requirements.txt found"
fi

# 6. Initialize Citadel Services
echo "🏛️ Initializing Citadel services..."

# Create necessary directories
mkdir -p data/{spiritual_intelligence,tarot_readings,models,workers,datasets,Mapping-and-Inventory-storage}
mkdir -p Districts/{D01,D02,D03,D04,D05,D06,D07,D08,D09,D10,D11,D12}

# Verify Python environment
python3 --version || python --version
echo "✅ Python environment ready"

# 7. Environment Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ENVIRONMENT SUMMARY"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔗 GitHub Source:  $GITHUB_REPO"
echo "🌿 Branch:         $GITHUB_BRANCH"
echo "📂 Working Dir:    $(pwd)"
echo "🐍 Python:         $(python3 --version 2>&1 || python --version 2>&1)"
echo "📦 Pip:            $(pip --version 2>&1 | cut -d' ' -f1-2)"
echo "💾 Disk Usage:     $(df -h . | tail -1 | awk '{print $5 " used"}')"
echo "🕐 Startup Time:   $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ STARTUP COMPLETE - Citadel Surveyor ready to serve"
echo "🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
