#!/bin/bash
# 💻 LAPTOP SYNC ORCHESTRATOR
# One-command laptop data copy to Citadel Mesh
# 
# Usage:
#   ./laptop_sync_orchestrator.sh              # Quick scan (metadata only)
#   ./laptop_sync_orchestrator.sh --full       # Full harvest (includes files)
#   ./laptop_sync_orchestrator.sh --help       # Show help

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Banner
echo -e "${CYAN}"
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║           💻 LAPTOP SYNC ORCHESTRATOR v1.0                    ║"
echo "║           Citadel Mesh Data Copy Protocol                     ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="$REPO_ROOT/data/laptop_inventory"
STORAGE_DIR="$REPO_ROOT/data/Mapping-and-Inventory-storage/laptop"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")

# Parse arguments
FULL_HARVEST=false
SHOW_HELP=false

while [[ $# -gt 0 ]]; do
  case $1 in
    --full)
      FULL_HARVEST=true
      shift
      ;;
    --help|-h)
      SHOW_HELP=true
      shift
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

if [ "$SHOW_HELP" = true ]; then
  echo "LAPTOP SYNC ORCHESTRATOR"
  echo ""
  echo "Usage:"
  echo "  ./laptop_sync_orchestrator.sh              Quick scan (metadata only)"
  echo "  ./laptop_sync_orchestrator.sh --full       Full harvest (metadata + files)"
  echo "  ./laptop_sync_orchestrator.sh --help       Show this help"
  echo ""
  echo "Quick scan:"
  echo "  - Scans filesystem for files and directories"
  echo "  - Scans Desktop for MASTER_MERGE_2 artifacts"
  echo "  - Generates JSON manifests"
  echo "  - Pushes to GitHub"
  echo ""
  echo "Full harvest:"
  echo "  - Performs quick scan"
  echo "  - Harvests actual file contents"
  echo "  - Stores in Mapping-and-Inventory-storage"
  echo "  - Pushes everything to GitHub"
  echo ""
  exit 0
fi

# Create directories
mkdir -p "$DATA_DIR"
mkdir -p "$STORAGE_DIR"

echo -e "${BLUE}📂 Repository: ${NC}$REPO_ROOT"
echo -e "${BLUE}📊 Data Directory: ${NC}$DATA_DIR"
echo ""

# ============================================================================
# PHASE 0: MASTER_MERGE_2 PRIORITY PROCESSOR (LOOK HERE FIRST!)
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 0: MASTER_MERGE_2 Priority Discovery                    ║${NC}"
echo -e "${CYAN}║ (Looking at MASTER_MERGE_2 FIRST - it shows where to look)    ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ -f "$REPO_ROOT/scripts/master_merge_2_processor.py" ]; then
  echo -e "${YELLOW}🎯 Processing MASTER_MERGE_2 (Priority Intelligence)...${NC}"
  python3 "$REPO_ROOT/scripts/master_merge_2_processor.py" --desktop "$HOME/Desktop"
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ MASTER_MERGE_2 processed - using it as scan guide${NC}"
  else
    echo -e "${YELLOW}⚠️  MASTER_MERGE_2 not found - continuing with standard scan${NC}"
  fi
else
  echo -e "${YELLOW}⚠️  master_merge_2_processor.py not found${NC}"
fi

echo ""

# ============================================================================
# PHASE 1: FILESYSTEM SCAN
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 1: Filesystem Scan                                      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if [ ! -f "$REPO_ROOT/scripts/laptop_filesystem_scanner.py" ]; then
  echo -e "${RED}❌ Error: laptop_filesystem_scanner.py not found${NC}"
  exit 1
fi

echo -e "${YELLOW}🔍 Scanning filesystem...${NC}"
python3 "$REPO_ROOT/scripts/laptop_filesystem_scanner.py" \
  --full-scan \
  --output "$DATA_DIR/laptop_manifest_${TIMESTAMP}.json" \
  --max-depth 5

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Filesystem scan complete${NC}"
  # Create symlink to latest
  ln -sf "laptop_manifest_${TIMESTAMP}.json" "$DATA_DIR/laptop_manifest_latest.json"
else
  echo -e "${RED}❌ Filesystem scan failed${NC}"
  exit 1
fi

echo ""

# ============================================================================
# PHASE 2: GUIDED SCANNING (using MASTER_MERGE_2 intelligence)
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 2: Guided Scanning (using MASTER_MERGE_2 guide)         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if we have MASTER_MERGE_2 scan guide
if [ -f "$DATA_DIR/master_merge_2_scan_guide.json" ]; then
  echo -e "${GREEN}✅ Using MASTER_MERGE_2 scan guide for targeted scanning${NC}"
  echo -e "${YELLOW}   Guide: $DATA_DIR/master_merge_2_scan_guide.json${NC}"
  
  # Show priority targets
  if command -v jq &> /dev/null; then
    echo ""
    echo -e "${BLUE}📂 Priority Directories:${NC}"
    cat "$DATA_DIR/master_merge_2_scan_guide.json" | jq -r '.priority_directories[:5][]' 2>/dev/null | while read dir; do
      echo -e "   • $dir"
    done
    
    echo ""
    echo -e "${BLUE}📄 Priority Extensions:${NC}"
    cat "$DATA_DIR/master_merge_2_scan_guide.json" | jq -r '.priority_extensions[:5][]' 2>/dev/null | while read ext; do
      echo -e "   • $ext"
    done
  fi
else
  echo -e "${YELLOW}⚠️  MASTER_MERGE_2 scan guide not found - using standard scan${NC}"
fi

echo ""

# ============================================================================
# PHASE 3: FULL HARVEST (Optional)
# ============================================================================
if [ "$FULL_HARVEST" = true ]; then
  echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
  echo -e "${CYAN}║ PHASE 3: Full File Harvest                                    ║${NC}"
  echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
  echo ""
  
  if [ ! -f "$REPO_ROOT/vamguard_templates/workers/laptop_harvester.py" ]; then
    echo -e "${RED}❌ Error: laptop_harvester.py not found${NC}"
  else
    echo -e "${YELLOW}📦 Harvesting file contents...${NC}"
    echo -e "${YELLOW}   Source: $HOME${NC}"
    
    export LAPTOP_SOURCE_PATH="$HOME"
    python3 "$REPO_ROOT/vamguard_templates/workers/laptop_harvester.py"
    
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✅ File harvest complete${NC}"
    else
      echo -e "${YELLOW}⚠️  File harvest completed with warnings${NC}"
    fi
  fi
  
  echo ""
fi

# ============================================================================
# PHASE 4: GENERATE SUMMARY
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 4: Generate Summary Report                              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

SUMMARY_FILE="$DATA_DIR/laptop_sync_summary_${TIMESTAMP}.json"

# Count files
MANIFEST_FILES=$(ls -1 "$DATA_DIR"/laptop_manifest_*.json 2>/dev/null | wc -l)
DESKTOP_FILES=$(ls -1 "$DATA_DIR"/laptop_desktop_scan_*.json 2>/dev/null | wc -l)
HARVESTED_FILES=$(find "$STORAGE_DIR" -type f -name "*.meta.json" 2>/dev/null | wc -l)

cat > "$SUMMARY_FILE" << EOF
{
  "sync_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "hostname": "$(hostname)",
  "sync_mode": "$([ "$FULL_HARVEST" = true ] && echo "full" || echo "quick")",
  "artifacts_generated": {
    "filesystem_manifests": $MANIFEST_FILES,
    "desktop_scans": $DESKTOP_FILES,
    "harvested_files": $HARVESTED_FILES
  },
  "data_locations": {
    "manifests": "data/laptop_inventory/",
    "harvested_files": "data/Mapping-and-Inventory-storage/laptop/",
    "latest_manifest": "data/laptop_inventory/laptop_manifest_latest.json",
    "latest_desktop_scan": "data/laptop_inventory/laptop_desktop_scan_latest.json"
  },
  "status": "complete"
}
EOF

echo -e "${GREEN}✅ Summary generated: $SUMMARY_FILE${NC}"
ln -sf "laptop_sync_summary_${TIMESTAMP}.json" "$DATA_DIR/laptop_sync_summary_latest.json"

# Display summary
echo ""
echo -e "${BLUE}📊 SYNC SUMMARY${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
cat "$SUMMARY_FILE"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""

# ============================================================================
# PHASE 5: GIT COMMIT & PUSH
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 5: Commit & Push to GitHub                              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$REPO_ROOT"

# Check if in git repo
if [ ! -d ".git" ]; then
  echo -e "${RED}❌ Error: Not in a git repository${NC}"
  exit 1
fi

# Stage files
echo -e "${YELLOW}📝 Staging files...${NC}"
git add data/laptop_inventory/
if [ "$FULL_HARVEST" = true ]; then
  git add data/Mapping-and-Inventory-storage/laptop/
fi

# Check if there are changes
if git diff --staged --quiet; then
  echo -e "${YELLOW}ℹ️  No changes to commit${NC}"
else
  # Commit
  COMMIT_MSG="💻 Laptop Sync: $([ "$FULL_HARVEST" = true ] && echo "Full Harvest" || echo "Quick Scan") @ $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  echo -e "${YELLOW}💾 Committing: ${NC}$COMMIT_MSG"
  git commit -m "$COMMIT_MSG"
  
  # Push
  echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
  git push
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
  else
    echo -e "${RED}❌ Push failed${NC}"
    exit 1
  fi
fi

echo ""

# ============================================================================
# PHASE 6: TRIGGER WORKFLOWS
# ============================================================================
echo -e "${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 6: Trigger Cloud Sync Workflows                         ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if command -v gh &> /dev/null; then
  echo -e "${YELLOW}🔄 Triggering multi-repo sync workflow...${NC}"
  gh workflow run multi_repo_sync.yml --repo DJ-Goana-Coding/mapping-and-inventory || echo -e "${YELLOW}⚠️  Workflow trigger skipped (may not exist or no permissions)${NC}"
  
  echo -e "${YELLOW}🔄 Triggering laptop harvest workflow...${NC}"
  gh workflow run laptop_harvest.yml --repo DJ-Goana-Coding/mapping-and-inventory || echo -e "${YELLOW}⚠️  Workflow trigger skipped (may not exist or no permissions)${NC}"
else
  echo -e "${YELLOW}ℹ️  GitHub CLI (gh) not installed - skipping workflow triggers${NC}"
  echo -e "${YELLOW}   Workflows will auto-trigger on push${NC}"
fi

echo ""

# ============================================================================
# COMPLETION
# ============================================================================
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                    ✅ SYNC COMPLETE                            ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📡 Next Steps:${NC}"
echo -e "   1. GitHub Actions workflows will process your data"
echo -e "   2. Data will sync to HuggingFace Space (DJ-Goanna-Coding/Mapping-and-Inventory)"
echo -e "   3. Oracle will ingest into RAG store within 6 hours"
echo -e "   4. Check workflow status: ${CYAN}https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions${NC}"
echo ""
echo -e "${BLUE}📊 Generated Artifacts:${NC}"
echo -e "   • Filesystem Manifest: ${CYAN}data/laptop_inventory/laptop_manifest_latest.json${NC}"
if [ -f "$DATA_DIR/laptop_desktop_scan_latest.json" ]; then
  echo -e "   • Desktop Scan: ${CYAN}data/laptop_inventory/laptop_desktop_scan_latest.json${NC}"
fi
if [ "$FULL_HARVEST" = true ]; then
  echo -e "   • Harvested Files: ${CYAN}data/Mapping-and-Inventory-storage/laptop/${NC}"
fi
echo -e "   • Summary: ${CYAN}data/laptop_inventory/laptop_sync_summary_latest.json${NC}"
echo ""
echo -e "${GREEN}🎯 Laptop data successfully copied to Citadel Mesh!${NC}"
echo ""
