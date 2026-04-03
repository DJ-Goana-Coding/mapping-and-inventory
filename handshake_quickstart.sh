#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════
# HANDSHAKE QUICKSTART: One-Command Protocol Execution
# ═══════════════════════════════════════════════════════════════════════════
# Purpose: Execute the complete handshake and ingestion protocol
# Usage: ./handshake_quickstart.sh [knock|local|gdrive|vacuum|file|all]
# ═══════════════════════════════════════════════════════════════════════════

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODE="${1:-all}"

echo "═══════════════════════════════════════════════════════════════════════════"
echo "🦎 HANDSHAKE QUICKSTART v25.5.OMNI"
echo "═══════════════════════════════════════════════════════════════════════════"
echo "Mode: $MODE"
echo "Target: Local filesystem (hundreds of GB) + GDrive (~20+ GB)"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""

# ═══════════════════════════════════════════════════════════════════════════
# KNOCK PROTOCOL
# ═══════════════════════════════════════════════════════════════════════════

if [[ "$MODE" == "knock" ]] || [[ "$MODE" == "all" ]]; then
    echo "🚪 Phase 1: KNOCK Protocol"
    echo "───────────────────────────────────────────────────────────────────────────"
    
    if [[ -f "$SCRIPT_DIR/scripts/knock_signal.sh" ]]; then
        bash "$SCRIPT_DIR/scripts/knock_signal.sh"
    else
        echo "❌ Error: knock_signal.sh not found"
        exit 1
    fi
    
    echo ""
    echo "✅ KNOCK complete. Waiting 5 seconds before vacuum..."
    sleep 5
fi

# ═══════════════════════════════════════════════════════════════════════════
# LOCAL FILESYSTEM VACUUM
# ═══════════════════════════════════════════════════════════════════════════

if [[ "$MODE" == "local" ]] || [[ "$MODE" == "vacuum" ]] || [[ "$MODE" == "all" ]]; then
    echo "💻 Phase 2a: Local Filesystem Vacuum (hundreds of GB)"
    echo "───────────────────────────────────────────────────────────────────────────"
    
    if [[ -f "$SCRIPT_DIR/scripts/local_filesystem_vacuum.sh" ]]; then
        bash "$SCRIPT_DIR/scripts/local_filesystem_vacuum.sh"
    else
        echo "❌ Error: local_filesystem_vacuum.sh not found"
        exit 1
    fi
    
    echo ""
    echo "✅ Local vacuum complete."
fi

# ═══════════════════════════════════════════════════════════════════════════
# GDRIVE VACUUM
# ═══════════════════════════════════════════════════════════════════════════

if [[ "$MODE" == "gdrive" ]] || [[ "$MODE" == "vacuum" ]] || [[ "$MODE" == "all" ]]; then
    echo "☁️ Phase 2b: GDrive Vacuum (~20+ GB)"
    echo "───────────────────────────────────────────────────────────────────────────"
    
    if [[ -f "$SCRIPT_DIR/scripts/global_vacuum.sh" ]]; then
        bash "$SCRIPT_DIR/scripts/global_vacuum.sh"
    else
        echo "❌ Error: global_vacuum.sh not found"
        exit 1
    fi
    
    echo ""
    echo "✅ GDrive vacuum complete. Waiting 10 seconds before filing..."
    sleep 10
fi

# ═══════════════════════════════════════════════════════════════════════════
# PERSONA FILING
# ═══════════════════════════════════════════════════════════════════════════

if [[ "$MODE" == "file" ]] || [[ "$MODE" == "all" ]]; then
    echo "🗂️ Phase 3: Persona Filing (Local + GDrive)"
    echo "───────────────────────────────────────────────────────────────────────────"
    
    if [[ -f "$SCRIPT_DIR/scripts/persona_filing_router.py" ]]; then
        # File local ingestion
        echo "  → Filing local filesystem data..."
        python3 "$SCRIPT_DIR/scripts/persona_filing_router.py" /data/local_ingestion /data/datasets
        
        echo ""
        echo "  → Filing GDrive data..."
        python3 "$SCRIPT_DIR/scripts/persona_filing_router.py" /data/total_ingestion /data/datasets
    else
        echo "❌ Error: persona_filing_router.py not found"
        exit 1
    fi
    
    echo ""
    echo "✅ Filing complete for both local and GDrive."
fi

# ═══════════════════════════════════════════════════════════════════════════
# COMPLETION
# ═══════════════════════════════════════════════════════════════════════════

echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "✅ HANDSHAKE PROTOCOL COMPLETE"
echo "═══════════════════════════════════════════════════════════════════════════"
echo ""
echo "📊 Status Summary:"
echo "  ✅ KNOCK signal sent to GDrive"
echo "  ✅ Local filesystem vacuum complete (hundreds of GB)"
echo "  ✅ GDrive substrate vacuum complete (~20+ GB)"
echo "  ✅ Data filed to persona datasets"
echo ""
echo "🎯 Next Steps:"
echo "  1. Trigger Forever Learning cycle in TIA-ARCHITECT-CORE"
echo "  2. Update master_intelligence_map.txt"
echo "  3. Run Oracle Sync workflow"
echo "  4. Verify T.I.A. HUD shows updated data"
echo ""
echo "═══════════════════════════════════════════════════════════════════════════"
echo "🦎 Weld. Pulse. Ignite."
echo "═══════════════════════════════════════════════════════════════════════════"
