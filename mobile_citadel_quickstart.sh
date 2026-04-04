#!/bin/bash
# 🚐 MOBILE CITADEL QUICKSTART
# Deploy and test Mobile Citadel Command Center

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MOBILE_DIR="$SCRIPT_DIR/scripts/mobile_citadel"

echo "🚐 MOBILE CITADEL COMMAND CENTER - QUICKSTART"
echo "=============================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo ""
echo "📱 1. Checking system requirements..."
python3 --version
echo "✅ Python available"

# Make scripts executable
echo ""
echo "🔧 2. Setting up scripts..."
chmod +x "$MOBILE_DIR"/*.py
echo "✅ Scripts configured"

# Initialize vehicle storage
echo ""
echo "💾 3. Initializing vehicle storage..."
export VEHICLE_STORAGE_PATH="/tmp/vehicle-storage"
python3 "$MOBILE_DIR/vehicle_storage_manager.py" init

# Check connectivity
echo ""
echo "🌐 4. Checking connectivity..."
python3 "$MOBILE_DIR/connectivity_detector.py" || echo "  (Offline is OK - this demonstrates offline mode)"

# Show equipment checklist
echo ""
echo "📋 5. Equipment checklist status..."
python3 "$MOBILE_DIR/equipment_tracker.py" report

# Show sync queue
echo ""
echo "📦 6. Sync queue status..."
python3 "$MOBILE_DIR/sync_queue_manager.py" stats

# Run daily routine
echo ""
echo "🌅 7. Running daily routine..."
python3 "$MOBILE_DIR/bridge_agent_mobile.py" daily

echo ""
echo "=============================================="
echo "✅ Mobile Citadel Quickstart Complete!"
echo ""
echo "📚 Available Commands:"
echo "  • Connectivity check:  python3 scripts/mobile_citadel/connectivity_detector.py"
echo "  • Sync queue:         python3 scripts/mobile_citadel/sync_queue_manager.py [stats|add|next|clear]"
echo "  • Vehicle storage:    python3 scripts/mobile_citadel/vehicle_storage_manager.py [init|report|health]"
echo "  • Equipment tracker:  python3 scripts/mobile_citadel/equipment_tracker.py [report|budget|update]"
echo "  • Bridge agent:       python3 scripts/mobile_citadel/bridge_agent_mobile.py [status|sync|daily|report]"
echo ""
echo "🎯 Next Steps:"
echo "  1. Update equipment tracker as you acquire items"
echo "  2. Initialize vehicle storage on actual vehicle device"
echo "  3. Run daily routine each day to maintain operations"
echo "  4. Monitor sync queue for pending operations"
echo ""
