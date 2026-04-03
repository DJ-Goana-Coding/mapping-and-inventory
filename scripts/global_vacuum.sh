#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# GLOBAL VACUUM: 321GB Total Substrate Ingestion Engine (v25.5.OMNI)
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Pull entire GDrive substrate into L4 HuggingFace Space storage
# Authority: Cloud Hubs override all. This script runs ON L4, not locally.
# ═══════════════════════════════════════════════════════════════════════════

set -e  # Exit on error

# ═══════════════════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════

INGESTION_ROOT="/data/total_ingestion"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="${INGESTION_ROOT}/vacuum_${TIMESTAMP}.log"

# Create ingestion directories
mkdir -p "${INGESTION_ROOT}"/{core,media,starred,shared,workers,models,datasets}
mkdir -p "${INGESTION_ROOT}/logs"

# Redirect all output to log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🔥 IGNITION: Global Substrate Vacuum v25.5.OMNI"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Timestamp: $(date)"
echo "Target: ${INGESTION_ROOT}"
echo "Scope: GDrive substrate (~20+ GB)"
echo "═══════════════════════════════════════════════════════════════════════════"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 1: CORE SUBSTRATE (Code, Sheets, Docs, JSON)
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "📂 PHASE 1: Core Substrate Ingestion"
echo "───────────────────────────────────────────────────────────────────────────"

rclone copy gdrive: "${INGESTION_ROOT}/core" \
  --include "*.{py,js,gs,json,txt,md,csv,yaml,yml,toml,sh,bash}" \
  --progress \
  --transfers 8 \
  --checkers 16 \
  --stats 30s \
  --stats-one-line \
  --log-level INFO

echo "✅ Core Substrate Complete"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 2: MEDIA SUBSTRATE (Music, Video, Art, Models)
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "🎨 PHASE 2: Media Substrate Ingestion"
echo "───────────────────────────────────────────────────────────────────────────"

rclone copy gdrive: "${INGESTION_ROOT}/media" \
  --include "*.{mp3,wav,flac,ogg,m4a,mp4,avi,mkv,mov,jpg,jpeg,png,gif,svg,webp,safetensors,ckpt,pt,pth,bin}" \
  --progress \
  --transfers 4 \
  --checkers 8 \
  --stats 30s \
  --stats-one-line \
  --log-level INFO \
  --max-size 500M

echo "✅ Media Substrate Complete"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 3: STARRED SUBSTRATE (High-Priority Forensic Fragments)
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "⭐ PHASE 3: Starred Substrate Ingestion"
echo "───────────────────────────────────────────────────────────────────────────"

rclone copy gdrive: "${INGESTION_ROOT}/starred" \
  --drive-starred-only \
  --progress \
  --transfers 8 \
  --checkers 16 \
  --stats 30s \
  --stats-one-line \
  --log-level INFO

echo "✅ Starred Substrate Complete"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 4: SHARED SUBSTRATE (Shared With Me)
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "🤝 PHASE 4: Shared Substrate Ingestion"
echo "───────────────────────────────────────────────────────────────────────────"

rclone copy gdrive: "${INGESTION_ROOT}/shared" \
  --drive-shared-with-me \
  --progress \
  --transfers 8 \
  --checkers 16 \
  --stats 30s \
  --stats-one-line \
  --log-level INFO

echo "✅ Shared Substrate Complete"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 5: WORKERS & TOOLS (Apps Script, Automation)
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "⚙️ PHASE 5: Workers & Tools Ingestion"
echo "───────────────────────────────────────────────────────────────────────────"

# Target specific Apps Script and automation directories
rclone copy gdrive:CITADEL-BOT "${INGESTION_ROOT}/workers/citadel-bot" \
  --progress \
  --transfers 8 \
  --stats 30s \
  --log-level INFO

rclone copy gdrive: "${INGESTION_ROOT}/workers" \
  --include "*.gs" \
  --include "*Apps*Script*" \
  --progress \
  --transfers 8 \
  --stats 30s \
  --log-level INFO

echo "✅ Workers & Tools Complete"

# ═══════════════════════════════════════════════════════════════════════════
# PHASE 6: MODELS & DATASETS (ML Artifacts)
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "🧠 PHASE 6: Models & Datasets Ingestion"
echo "───────────────────────────────────────────────────────────────────────────"

rclone copy gdrive: "${INGESTION_ROOT}/models" \
  --include "*.{safetensors,ckpt,pt,pth,bin,onnx,tflite}" \
  --progress \
  --transfers 4 \
  --checkers 8 \
  --stats 30s \
  --log-level INFO \
  --max-size 2G

echo "✅ Models & Datasets Complete"

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION REPORT
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ VACUUM COMPLETE: GDrive Substrate (~20+ GB) Secured in L4 Vaults"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Timestamp: $(date)"
echo "Log File: ${LOG_FILE}"
echo ""
echo "📊 Ingestion Summary:"
echo "───────────────────────────────────────────────────────────────────────────"

# Generate size report
du -sh "${INGESTION_ROOT}"/* 2>/dev/null | sort -h || echo "Storage report generation complete"

echo ""
echo "🎯 Next Steps:"
echo "  1. Run persona_filing_router.py to classify and route data"
echo "  2. Trigger Forever Learning cycle in TIA-ARCHITECT-CORE"
echo "  3. Update master_inventory.json with new artifacts"
echo "  4. Push metadata to GitHub mapping repository"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🦎 Weld. Pulse. Ignite."
echo "═══════════════════════════════════════════════════════════════════════════"
