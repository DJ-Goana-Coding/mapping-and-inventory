#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# LOCAL FILESYSTEM VACUUM: Computer Substrate Ingestion (v25.5.OMNI)
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Scan and ingest local computer filesystem (hundreds of GB)
# Authority: Complements GDrive vacuum for complete substrate coverage
# ═══════════════════════════════════════════════════════════════════════════

set -e

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

INGESTION_ROOT="/data/local_ingestion"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${INGESTION_ROOT}/local_vacuum_${TIMESTAMP}.log"

# Scan roots - adjust based on your system
# For Linux/Termux: /storage/emulated/0, /sdcard, /data/data
# For Windows: C:\Users\YourName, D:\
# For macOS: /Users/yourname

SCAN_ROOTS=(
    "/storage/emulated/0"        # Android primary storage
    "/sdcard"                     # Android SD card symlink
    "$HOME"                       # User home directory
    "/data/data/com.termux"       # Termux app data (if applicable)
    "/external_sd"                # External SD card (if mounted)
)

# Create ingestion directories
mkdir -p "${INGESTION_ROOT}"/{code,documents,media,models,data,config,archives}
mkdir -p "${INGESTION_ROOT}/logs"

# Redirect all output to log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "═══════════════════════════════════════════════════════════════════════════"
echo "💻 LOCAL FILESYSTEM VACUUM v25.5.OMNI"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Timestamp: $(date)"
echo "Target: ${INGESTION_ROOT}"
echo "Scanning: Local computer filesystem (hundreds of GB)"
echo "═══════════════════════════════════════════════════════════════════════════"

# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

copy_files() {
    local source="$1"
    local dest="$2"
    local pattern="$3"
    local description="$4"
    
    echo "  Scanning: $description"
    
    find "$source" -type f \( $pattern \) \
        -not -path "*/.*" \
        -not -path "*/.git/*" \
        -not -path "*/node_modules/*" \
        -not -path "*/__pycache__/*" \
        -not -path "*/venv/*" \
        -not -path "*/.venv/*" \
        -exec cp --parents {} "$dest" \; 2>/dev/null || true
}

scan_directory() {
    local scan_root="$1"
    
    if [[ ! -d "$scan_root" ]]; then
        echo "⚠️  Skipping non-existent path: $scan_root"
        return
    fi
    
    echo ""
    echo "📁 Scanning: $scan_root"
    echo "───────────────────────────────────────────────────────────────────────────"
    
    # Calculate total size
    local total_size=$(du -sh "$scan_root" 2>/dev/null | cut -f1 || echo "unknown")
    echo "  Total size: $total_size"
    
    # Code files
    echo "  → Code files..."
    copy_files "$scan_root" "${INGESTION_ROOT}/code" \
        "-name '*.py' -o -name '*.js' -o -name '*.gs' -o -name '*.sh' -o -name '*.bash' -o -name '*.ps1' -o -name '*.java' -o -name '*.cpp' -o -name '*.c' -o -name '*.go' -o -name '*.rs'" \
        "Source code"
    
    # Documents
    echo "  → Documents..."
    copy_files "$scan_root" "${INGESTION_ROOT}/documents" \
        "-name '*.md' -o -name '*.txt' -o -name '*.pdf' -o -name '*.doc' -o -name '*.docx' -o -name '*.xlsx' -o -name '*.csv'" \
        "Documents and data files"
    
    # Configuration files
    echo "  → Configuration files..."
    copy_files "$scan_root" "${INGESTION_ROOT}/config" \
        "-name '*.json' -o -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o -name '*.ini' -o -name '*.conf' -o -name '*.config'" \
        "Configuration files"
    
    # Media files (with size limit)
    echo "  → Media files (under 500MB)..."
    find "$scan_root" -type f \
        \( -name '*.mp3' -o -name '*.wav' -o -name '*.flac' -o -name '*.ogg' -o -name '*.m4a' \
        -o -name '*.mp4' -o -name '*.avi' -o -name '*.mkv' -o -name '*.mov' \
        -o -name '*.jpg' -o -name '*.jpeg' -o -name '*.png' -o -name '*.gif' -o -name '*.svg' -o -name '*.webp' \) \
        -size -500M \
        -not -path "*/.*" \
        -exec cp --parents {} "${INGESTION_ROOT}/media" \; 2>/dev/null || true
    
    # ML Models and checkpoints (with size limit)
    echo "  → ML models (under 2GB)..."
    find "$scan_root" -type f \
        \( -name '*.safetensors' -o -name '*.ckpt' -o -name '*.pt' -o -name '*.pth' -o -name '*.bin' -o -name '*.onnx' -o -name '*.tflite' \) \
        -size -2G \
        -not -path "*/.*" \
        -exec cp --parents {} "${INGESTION_ROOT}/models" \; 2>/dev/null || true
    
    # Archives (with size limit)
    echo "  → Archives (under 1GB)..."
    find "$scan_root" -type f \
        \( -name '*.zip' -o -name '*.tar' -o -name '*.tar.gz' -o -name '*.tgz' -o -name '*.7z' -o -name '*.rar' \) \
        -size -1G \
        -not -path "*/.*" \
        -exec cp --parents {} "${INGESTION_ROOT}/archives" \; 2>/dev/null || true
    
    echo "✅ Scan complete: $scan_root"
}

# ═══════════════════════════════════════════════════════════════════════════
# MAIN SCANNING LOOP
# ═══════════════════════════════════════════════════════════════════════════

for scan_root in "${SCAN_ROOTS[@]}"; do
    scan_directory "$scan_root"
done

# ═══════════════════════════════════════════════════════════════════════════
# INTELLIGENT DISCOVERY: Find Important Directories
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "🔍 INTELLIGENT DISCOVERY: Locating key directories"
echo "───────────────────────────────────────────────────────────────────────────"

# Common project/code directories
for scan_root in "${SCAN_ROOTS[@]}"; do
    if [[ -d "$scan_root" ]]; then
        echo "  Searching for repositories in $scan_root..."
        
        # Find git repositories
        find "$scan_root" -type d -name ".git" 2>/dev/null | while read -r git_dir; do
            repo_dir=$(dirname "$git_dir")
            echo "    📦 Found repo: $repo_dir"
            
            # Copy entire repo (excluding .git directory)
            rsync -a --exclude='.git' --exclude='node_modules' --exclude='venv' \
                "$repo_dir/" "${INGESTION_ROOT}/code/repos/$(basename $repo_dir)/" 2>/dev/null || true
        done
        
        # Find common project directories
        find "$scan_root" -maxdepth 3 -type d \
            \( -name "Projects" -o -name "Code" -o -name "Development" -o -name "Repos" -o -name "GitHub" \) \
            2>/dev/null | while read -r project_dir; do
            echo "    📁 Found project dir: $project_dir"
        done
    fi
done

echo "✅ Intelligent discovery complete"

# ═══════════════════════════════════════════════════════════════════════════
# SPECIALIZED SCANS
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "🎯 SPECIALIZED SCANS"
echo "───────────────────────────────────────────────────────────────────────────"

# Trading data
echo "  → Trading data and ledgers..."
for scan_root in "${SCAN_ROOTS[@]}"; do
    [[ -d "$scan_root" ]] && find "$scan_root" -type f \
        \( -iname '*trade*' -o -iname '*ledger*' -o -iname '*transaction*' -o -iname '*wallet*' \) \
        \( -name '*.csv' -o -name '*.json' -o -name '*.xlsx' \) \
        -not -path "*/.*" \
        -exec cp --parents {} "${INGESTION_ROOT}/data/trading" \; 2>/dev/null || true
done

# Apps Script and automation
echo "  → Apps Script and automation tools..."
for scan_root in "${SCAN_ROOTS[@]}"; do
    [[ -d "$scan_root" ]] && find "$scan_root" -type f \
        \( -name '*.gs' -o -iname '*apps*script*' -o -iname '*automation*' \) \
        -not -path "*/.*" \
        -exec cp --parents {} "${INGESTION_ROOT}/data/workers" \; 2>/dev/null || true
done

# Stories and lore
echo "  → Stories, lore, and narratives..."
for scan_root in "${SCAN_ROOTS[@]}"; do
    [[ -d "$scan_root" ]] && find "$scan_root" -type f \
        \( -iname '*story*' -o -iname '*lore*' -o -iname '*narrative*' -o -iname '*mythos*' -o -iname '*legend*' \) \
        \( -name '*.md' -o -name '*.txt' -o -name '*.pdf' \) \
        -not -path "*/.*" \
        -exec cp --parents {} "${INGESTION_ROOT}/data/lore" \; 2>/dev/null || true
done

echo "✅ Specialized scans complete"

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION REPORT
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ LOCAL FILESYSTEM VACUUM COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Timestamp: $(date)"
echo "Log File: ${LOG_FILE}"
echo ""
echo "📊 Ingestion Summary:"
echo "───────────────────────────────────────────────────────────────────────────"

# Generate size report
du -sh "${INGESTION_ROOT}"/* 2>/dev/null | sort -h || echo "Storage report complete"

echo ""
echo "📈 File Counts:"
find "${INGESTION_ROOT}/code" -type f 2>/dev/null | wc -l | xargs echo "  Code files:"
find "${INGESTION_ROOT}/documents" -type f 2>/dev/null | wc -l | xargs echo "  Documents:"
find "${INGESTION_ROOT}/media" -type f 2>/dev/null | wc -l | xargs echo "  Media files:"
find "${INGESTION_ROOT}/models" -type f 2>/dev/null | wc -l | xargs echo "  ML models:"
find "${INGESTION_ROOT}/config" -type f 2>/dev/null | wc -l | xargs echo "  Config files:"
find "${INGESTION_ROOT}/archives" -type f 2>/dev/null | wc -l | xargs echo "  Archives:"

echo ""
echo "🎯 Next Steps:"
echo "  1. Run persona_filing_router.py on local ingestion"
echo "  2. Merge with GDrive ingestion results"
echo "  3. Trigger Forever Learning cycle"
echo "  4. Update master_inventory.json"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🦎 Weld. Pulse. Ignite."
echo "═══════════════════════════════════════════════════════════════════════════"
