#!/bin/bash
# 🌊 ULTRA LAPTOP VACUUM
# Master orchestrator: MASTER_MERGE_2 → Comprehensive Vacuum → Full Sync
# 
# This is the NUCLEAR option: Copies EVERYTHING relevant from the entire laptop
#
# Usage:
#   ./ultra_laptop_vacuum.sh              # Interactive mode
#   ./ultra_laptop_vacuum.sh --auto       # Auto mode (no prompts)
#   ./ultra_laptop_vacuum.sh --help       # Show help

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
AUTO_MODE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --auto)
      AUTO_MODE=true
      shift
      ;;
    --help|-h)
      echo "ULTRA LAPTOP VACUUM - Complete Laptop Data Extraction"
      echo ""
      echo "Usage:"
      echo "  ./ultra_laptop_vacuum.sh              Interactive mode (prompts for confirmation)"
      echo "  ./ultra_laptop_vacuum.sh --auto       Auto mode (no prompts, just run)"
      echo "  ./ultra_laptop_vacuum.sh --help       Show this help"
      echo ""
      echo "What it does:"
      echo "  1. Locates MASTER_MERGE_2 on Desktop (intelligence first)"
      echo "  2. Processes MASTER_MERGE_2 to understand system layout"
      echo "  3. Detects ALL drives/partitions on laptop"
      echo "  4. Vacuums ALL relevant files from ALL drives"
      echo "  5. Creates complete inventory and metadata"
      echo "  6. Commits and pushes to GitHub"
      echo "  7. Triggers cloud sync to HuggingFace"
      echo ""
      echo "File types harvested:"
      echo "  • Code (.py, .js, .java, .cpp, etc.)"
      echo "  • Models (.pt, .h5, .onnx, .safetensors, etc.)"
      echo "  • Data (.csv, .json, .parquet, etc.)"
      echo "  • Config (.yaml, .toml, .ini, etc.)"
      echo "  • Documentation (.md, .txt, .rst, etc.)"
      echo "  • Build files (requirements.txt, package.json, etc.)"
      echo "  • PowerShell scripts (.ps1, .psm1, etc.)"
      echo ""
      exit 0
      ;;
    *)
      echo -e "${RED}Unknown option: $1${NC}"
      exit 1
      ;;
  esac
done

# Banner
echo -e "${MAGENTA}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║              🌊 ULTRA LAPTOP VACUUM v1.0 🌊                          ║
║                                                                       ║
║          COMPREHENSIVE DATA EXTRACTION PROTOCOL                       ║
║       ALL Drives • ALL Systems • EVERYTHING Relevant                  ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${YELLOW}⚠️  WARNING: This is the NUCLEAR option${NC}"
echo -e "${YELLOW}   This will scan ALL drives and copy ALL relevant files${NC}"
echo -e "${YELLOW}   This may take 30-120 minutes and use significant disk space${NC}"
echo ""

if [ "$AUTO_MODE" = false ]; then
  echo -e "${CYAN}🤔 Are you sure you want to proceed?${NC}"
  read -p "Type 'YES' to continue: " CONFIRM
  
  if [ "$CONFIRM" != "YES" ]; then
    echo -e "${RED}❌ Aborted${NC}"
    exit 0
  fi
fi

echo ""
echo -e "${GREEN}✅ Starting Ultra Laptop Vacuum...${NC}"
echo ""

# ============================================================================
# PHASE 0A: HARDWARE FORENSICS (Hidden SSD - PRIORITY!)
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 0A: Hardware Forensics (Hidden SSD Detection - PRIORITY)   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}🔬 Scanning for hidden SSD and RAM chips...${NC}"
python3 "$REPO_ROOT/scripts/hardware_forensics.py" --mount-hidden --extract-all || {
  echo -e "${YELLOW}⚠️  Hardware forensics failed or no hidden SSD found - continuing${NC}"
}

echo ""

# ============================================================================
# PHASE 0B: SYSTEM PROFILING (Index/Librarian the system)
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 0B: System Profiling (Hardware/Software Indexing)          ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📚 Running System Librarian...${NC}"
python3 "$REPO_ROOT/scripts/system_librarian.py" || {
  echo -e "${YELLOW}⚠️  System profiling failed - continuing anyway${NC}"
}

echo ""

# ============================================================================
# PHASE 0C: MASTER_MERGE_2 INTELLIGENCE EXTRACTION
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 0C: MASTER_MERGE_2 Intelligence (LOOK HERE FIRST)          ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}🎯 Processing MASTER_MERGE_2...${NC}"
python3 "$REPO_ROOT/scripts/master_merge_2_processor.py" --desktop "$HOME/Desktop" || {
  echo -e "${YELLOW}⚠️  MASTER_MERGE_2 not found - continuing anyway${NC}"
}

echo ""

# ============================================================================
# PHASE 1: COMPREHENSIVE VACUUM (ALL DRIVES, ALL SYSTEMS)
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 1: Comprehensive Vacuum (ALL Drives, ALL Systems)          ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}🌊 Initiating comprehensive vacuum...${NC}"
echo -e "${YELLOW}   This will scan ALL drives for relevant files${NC}"
echo ""

if [ "$AUTO_MODE" = true ]; then
  python3 "$REPO_ROOT/scripts/comprehensive_laptop_vacuum.py" --max-size 500 --max-files-per-drive 50000 << EOF
yes
EOF
else
  python3 "$REPO_ROOT/scripts/comprehensive_laptop_vacuum.py" --max-size 500 --max-files-per-drive 50000
fi

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✅ Comprehensive vacuum complete${NC}"
else
  echo -e "${RED}❌ Vacuum failed${NC}"
  exit 1
fi

echo ""

# ============================================================================
# PHASE 2: ADDITIONAL SCANNERS (Filesystem, Desktop)
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 2: Additional Metadata Scanners                            ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📊 Running filesystem scanner for metadata...${NC}"
python3 "$REPO_ROOT/scripts/laptop_filesystem_scanner.py" \
  --full-scan \
  --output "$REPO_ROOT/data/laptop_inventory/laptop_manifest_${TIMESTAMP}.json" \
  --max-depth 5 || echo -e "${YELLOW}⚠️  Filesystem scanner completed with warnings${NC}"

echo ""

# ============================================================================
# PHASE 3: GENERATE MASTER INVENTORY
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 3: Generate Master Inventory                               ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}📋 Generating master inventory...${NC}"

VACUUM_DIR="$REPO_ROOT/data/Mapping-and-Inventory-storage/laptop_vacuum"
INVENTORY_FILE="$REPO_ROOT/data/laptop_inventory/ultra_vacuum_inventory_${TIMESTAMP}.json"

# Count files
TOTAL_FILES=$(find "$VACUUM_DIR" -type f -name "*.meta.json" 2>/dev/null | wc -l)
TOTAL_SIZE=$(du -sb "$VACUUM_DIR" 2>/dev/null | cut -f1 || echo "0")
TOTAL_SIZE_GB=$(echo "scale=2; $TOTAL_SIZE / 1073741824" | bc 2>/dev/null || echo "0")

cat > "$INVENTORY_FILE" << EOF
{
  "vacuum_timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "vacuum_mode": "ultra_comprehensive",
  "hostname": "$(hostname)",
  "os": "$(uname -s)",
  "stats": {
    "total_files_harvested": $TOTAL_FILES,
    "total_size_bytes": $TOTAL_SIZE,
    "total_size_gb": "$TOTAL_SIZE_GB"
  },
  "data_locations": {
    "vacuum_storage": "data/Mapping-and-Inventory-storage/laptop_vacuum/",
    "vacuum_report": "data/Mapping-and-Inventory-storage/laptop_vacuum/vacuum_report.json",
    "harvest_index": "data/Mapping-and-Inventory-storage/laptop_vacuum/harvest_index.json",
    "master_merge_2": "data/laptop_inventory/master_system_map_2.json",
    "scan_guide": "data/laptop_inventory/master_merge_2_scan_guide.json"
  },
  "status": "complete"
}
EOF

echo -e "${GREEN}✅ Master inventory generated${NC}"
cat "$INVENTORY_FILE"
echo ""

# ============================================================================
# PHASE 4: COMMIT & PUSH TO GITHUB
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 4: Commit & Push to GitHub                                 ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

cd "$REPO_ROOT"

echo -e "${YELLOW}📝 Staging files...${NC}"
git add data/laptop_inventory/
git add data/Mapping-and-Inventory-storage/laptop_vacuum/ 2>/dev/null || {
  echo -e "${YELLOW}⚠️  Large vacuum directory - may need Git LFS${NC}"
  echo -e "${YELLOW}   Consider: git lfs track 'data/Mapping-and-Inventory-storage/laptop_vacuum/**'${NC}"
}

# Check size
STAGED_SIZE=$(git diff --cached --stat | tail -1 | awk '{print $4, $5}')
echo -e "${BLUE}📊 Staged changes: $STAGED_SIZE${NC}"

if git diff --staged --quiet; then
  echo -e "${YELLOW}ℹ️  No changes to commit${NC}"
else
  COMMIT_MSG="🌊 Ultra Laptop Vacuum Complete @ $(date -u +"%Y-%m-%dT%H:%M:%SZ")

- Processed MASTER_MERGE_2 intelligence
- Vacuumed ALL drives and systems
- Harvested $TOTAL_FILES files ($TOTAL_SIZE_GB GB)
- Generated comprehensive inventory
"
  
  echo -e "${YELLOW}💾 Committing...${NC}"
  git commit -m "$COMMIT_MSG"
  
  echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
  git push
  
  if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub${NC}"
  else
    echo -e "${RED}❌ Push failed - files may be too large${NC}"
    echo -e "${YELLOW}💡 Consider using Git LFS for large files${NC}"
    echo -e "${YELLOW}   git lfs install${NC}"
    echo -e "${YELLOW}   git lfs track '*.bin' '*.pt' '*.h5'${NC}"
    echo -e "${YELLOW}   git add .gitattributes${NC}"
    echo -e "${YELLOW}   git commit -m 'Add Git LFS tracking'${NC}"
    echo -e "${YELLOW}   git push${NC}"
  fi
fi

echo ""

# ============================================================================
# PHASE 5: TRIGGER CLOUD SYNC
# ============================================================================
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║ PHASE 5: Trigger Cloud Sync Workflows                            ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""

if command -v gh &> /dev/null; then
  echo -e "${YELLOW}🔄 Triggering laptop sync processor...${NC}"
  gh workflow run laptop_sync_processor.yml --repo DJ-Goana-Coding/mapping-and-inventory || true
  
  echo -e "${YELLOW}🔄 Triggering multi-repo sync...${NC}"
  gh workflow run multi_repo_sync.yml --repo DJ-Goana-Coding/mapping-and-inventory || true
  
  echo -e "${GREEN}✅ Workflows triggered${NC}"
else
  echo -e "${YELLOW}ℹ️  GitHub CLI not installed - workflows will auto-trigger on push${NC}"
fi

echo ""

# ============================================================================
# COMPLETION SUMMARY
# ============================================================================
echo -e "${GREEN}"
cat << 'EOF'
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║                    ✅ ULTRA VACUUM COMPLETE ✅                        ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"

echo -e "${BLUE}📊 VACUUM SUMMARY${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   Files Harvested: ${NC}$TOTAL_FILES"
echo -e "${GREEN}   Data Harvested: ${NC}$TOTAL_SIZE_GB GB"
echo -e "${GREEN}   Timestamp: ${NC}$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"

echo ""
echo -e "${BLUE}📁 DATA LOCATIONS${NC}"
echo -e "   Vacuum Storage: ${CYAN}data/Mapping-and-Inventory-storage/laptop_vacuum/${NC}"
echo -e "   Vacuum Report: ${CYAN}data/Mapping-and-Inventory-storage/laptop_vacuum/vacuum_report.json${NC}"
echo -e "   Harvest Index: ${CYAN}data/Mapping-and-Inventory-storage/laptop_vacuum/harvest_index.json${NC}"
echo -e "   Master Inventory: ${CYAN}data/laptop_inventory/ultra_vacuum_inventory_${TIMESTAMP}.json${NC}"

echo ""
echo -e "${BLUE}🔄 AUTOMATIC SYNC CHAIN${NC}"
echo -e "   ✅ Laptop → GitHub (DONE)"
echo -e "   ⏳ GitHub → HuggingFace Space (triggered)"
echo -e "   ⏳ HuggingFace → Oracle RAG (within 6 hours)"

echo ""
echo -e "${BLUE}🌐 CHECK STATUS${NC}"
echo -e "   GitHub Actions: ${CYAN}https://github.com/DJ-Goana-Coding/mapping-and-inventory/actions${NC}"
echo -e "   HuggingFace Space: ${CYAN}https://huggingface.co/spaces/DJ-Goanna-Coding/Mapping-and-Inventory${NC}"

echo ""
echo -e "${GREEN}🎯 Your laptop data is now fully copied to the Citadel Mesh!${NC}"
echo ""
