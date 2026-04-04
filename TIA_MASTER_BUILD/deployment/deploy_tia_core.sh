#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
# 🔥 TIA-ARCHITECT-CORE FULL DEPLOYMENT SCRIPT
# ═══════════════════════════════════════════════════════════════════
# Purpose: Deploy complete package to TIA-ARCHITECT-CORE repository
# Usage: ./deploy_tia_core.sh
# ═══════════════════════════════════════════════════════════════════

set -e

echo "═══════════════════════════════════════════════════════════════════"
echo "🔥 TIA-ARCHITECT-CORE FULL DEPLOYMENT"
echo "═══════════════════════════════════════════════════════════════════"
echo ""

# Configuration
MAPPING_REPO="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATE_DIR="$MAPPING_REPO/tia-architect-core-templates"
DEPLOY_DIR="/tmp/TIA-ARCHITECT-CORE-deploy"

# Check if template directory exists
if [ ! -d "$TEMPLATE_DIR" ]; then
    echo "❌ ERROR: Template directory not found at $TEMPLATE_DIR"
    exit 1
fi

echo "✅ Found template directory: $TEMPLATE_DIR"
echo ""

# Clone TIA-ARCHITECT-CORE
echo "📥 Cloning TIA-ARCHITECT-CORE repository..."
rm -rf "$DEPLOY_DIR"
git clone https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE "$DEPLOY_DIR"

if [ ! -d "$DEPLOY_DIR" ]; then
    echo "❌ ERROR: Failed to clone repository"
    exit 1
fi

cd "$DEPLOY_DIR"
echo "✅ Repository cloned to $DEPLOY_DIR"
echo ""

# Create backup
echo "💾 Creating backup of existing files..."
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

[ -f app.py ] && cp app.py "$BACKUP_DIR/" && echo "  ✅ Backed up app.py"
[ -f requirements.txt ] && cp requirements.txt "$BACKUP_DIR/" && echo "  ✅ Backed up requirements.txt"
[ -d scripts ] && cp -r scripts "$BACKUP_DIR/" && echo "  ✅ Backed up scripts/"
[ -d workers ] && cp -r workers "$BACKUP_DIR/" && echo "  ✅ Backed up workers/"
[ -d data ] && cp -r data "$BACKUP_DIR/" && echo "  ✅ Backed up data/"

echo ""

# Deploy Core Application
echo "📋 Deploying Core Application..."
cp "$TEMPLATE_DIR/app.py" app.py
cp "$TEMPLATE_DIR/requirements.txt" requirements.txt
cp "$TEMPLATE_DIR/DEPLOYMENT_GUIDE.md" DEPLOYMENT_GUIDE.md
echo "  ✅ app.py"
echo "  ✅ requirements.txt"
echo "  ✅ DEPLOYMENT_GUIDE.md"
echo ""

# Deploy Models & Downloaders
echo "🤖 Deploying Models & Downloaders..."
mkdir -p scripts data/models
cp "$TEMPLATE_DIR/scripts"/*.py scripts/
cp "$TEMPLATE_DIR/data/models/models_manifest.json" data/models/
echo "  ✅ download_frontier_models_2026.py"
echo "  ✅ download_citadel_omega_models.py"
echo "  ✅ models_manifest.json"
echo ""

# Deploy Workers & Tools
echo "⚙️ Deploying Workers & Tools..."
mkdir -p workers data/workers
cp -r "$TEMPLATE_DIR/workers"/* workers/
cp "$TEMPLATE_DIR/data/workers/workers_manifest.json" data/workers/
echo "  ✅ apps_script_toolbox.py"
echo "  ✅ worker_watchdog.py"
echo "  ✅ self_healing_worker.py"
echo "  ✅ workers_manifest.json"
echo ""

# Generate README if doesn't exist
if [ ! -f README.md ]; then
    echo "📝 Creating README.md..."
    cat > README.md << 'READMEEOF'
# 🧠 TIA-ARCHITECT-CORE

**T.I.A. - The Intelligence Architect**  
Central Reasoning Hub for Q.G.T.N.L. Citadel Mesh

## Features

- **RAG Intelligence** - Vector search & synthesis
- **Model Management** - Deploy & monitor AI models
- **Worker Orchestration** - Coordinate automation workers
- **Knowledge Mesh** - Connect all Citadel nodes

## Quick Start

This Space runs automatically on HuggingFace.

### Local Development

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Documentation

- `DEPLOYMENT_GUIDE.md` - Full deployment instructions
- `workers/README.md` - Apps Script workers documentation
- `scripts/` - Model downloaders and utilities

## Links

- **GitHub:** [DJ-Goana-Coding/TIA-ARCHITECT-CORE](https://github.com/DJ-Goana-Coding/TIA-ARCHITECT-CORE)
- **Mapping Hub:** [DJ-Goana-Coding/mapping-and-inventory](https://github.com/DJ-Goana-Coding/mapping-and-inventory)

---

**Version:** 25.0.OMNI++  
**Architect:** Citadel v25.0
READMEEOF
    echo "  ✅ README.md created"
    echo ""
fi

# Show deployment summary
echo "═══════════════════════════════════════════════════════════════════"
echo "📊 DEPLOYMENT SUMMARY"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "📁 Deployed Files:"
tree -L 2 -I '.git|backup*' 2>/dev/null || find . -maxdepth 2 -type f -name "*.py" -o -name "*.md" -o -name "*.txt" -o -name "*.json" | grep -v ".git" | grep -v "backup"
echo ""
echo "📊 Statistics:"
echo "  - Python files: $(find . -name '*.py' -type f | grep -v ".git" | wc -l)"
echo "  - Scripts: $(find scripts -name '*.py' 2>/dev/null | wc -l || echo 0)"
echo "  - Workers: $(find workers -name '*.py' 2>/dev/null | wc -l || echo 0)"
echo ""

# Git configuration
git config user.name "Citadel Architect"
git config user.email "architect@citadel.mesh"

# Commit changes
echo "💾 Committing changes..."
git add .

if git diff --cached --quiet; then
    echo "ℹ️  No changes to commit (already up to date)"
else
    git commit -m "🔥 FULL DEPLOYMENT: Complete package (UI + Models + Workers + Tools)

📦 Deployment Details:
- Streamlit app with 5-tab interface (Dashboard, Models, Workers, KB, Tools)
- Python 3.13 compatible dependencies  
- Frontier models downloader (Gemma 4, Qwen 3.5, DeepSeek V4, Phi-4, Ministral)
- CITADEL Omega models (FinBERT, CryptoBERT, Sentence Transformers)
- Apps Script workers for Google Sheets integration
- Worker watchdog & self-healing systems
- Complete manifests & documentation

🔧 Template Source: DJ-Goana-Coding/mapping-and-inventory
📡 Deployed by: deploy_tia_core.sh
🧠 Architect: v25.0.OMNI++"
    
    echo "✅ Changes committed"
fi

echo ""

# Push to GitHub
echo "⬆️ Pushing to GitHub..."
if git push origin main; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ Push failed. You may need to push manually."
    echo ""
    echo "To push manually:"
    echo "  cd $DEPLOY_DIR"
    echo "  git push origin main"
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "✅ DEPLOYMENT COMPLETE"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "🎯 Next Steps:"
echo ""
echo "1. Monitor HuggingFace Space rebuild:"
echo "   https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE/logs"
echo ""
echo "2. Expected build time: 3-5 minutes"
echo ""
echo "3. Access the Space after build completes:"
echo "   https://huggingface.co/spaces/DJ-Goanna-Coding/TIA-ARCHITECT-CORE"
echo ""
echo "4. Test all features:"
echo "   - ✅ Dashboard tab"
echo "   - ✅ Models registry & downloader"
echo "   - ✅ Workers constellation"
echo "   - ✅ Knowledge Base (RAG)"
echo "   - ✅ Tools & utilities"
echo ""
echo "🔥 Deployment deployed successfully!"
echo "📋 Logs saved to: $DEPLOY_DIR"
echo "═══════════════════════════════════════════════════════════════════"
