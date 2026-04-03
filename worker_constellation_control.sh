#!/bin/bash
# 🎛️ WORKER CONSTELLATION MASTER CONTROL
# Authority: Citadel Architect v25.0.OMNI+

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$SCRIPT_DIR/data/worker_logs"
mkdir -p "$LOG_DIR"

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/master.log"
}

# Worker Control Functions
start_discovery_workers() {
    log "🔍 Starting discovery workers..."
    python scripts/domain_scout.py &
    python scripts/spiritual_network_mapper.py &
    python scripts/harvest_github_trending.py &
    wait
    log "✅ Discovery workers complete"
}

start_sync_workers() {
    log "🔄 Starting sync workers..."
    ./global_sync.sh
    log "✅ Sync workers complete"
}

start_monitoring_workers() {
    log "👁️ Starting monitoring workers..."
    python scripts/security_sentinel.py &
    python scripts/autonomous_health_monitor.py &
    wait
    log "✅ Monitoring workers complete"
}

run_forever_learning_cycle() {
    log "🔄 Starting Forever Learning Cycle..."
    start_sync_workers
    start_monitoring_workers
    log "✅ Forever Learning Cycle complete"
}

# Command Dispatcher
case "${1:-help}" in
    discovery)
        start_discovery_workers
        ;;
    sync)
        start_sync_workers
        ;;
    monitoring)
        start_monitoring_workers
        ;;
    forever-learning)
        run_forever_learning_cycle
        ;;
    all)
        log "🚀 Starting all workers..."
        start_discovery_workers
        start_sync_workers
        start_monitoring_workers
        log "✅ All workers complete"
        ;;
    status)
        log "📊 Worker Status:"
        ps aux | grep -E "python|bash" | grep -E "scripts|global_sync"
        ;;
    help|*)
        echo "Worker Constellation Master Control"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  discovery          - Run discovery workers"
        echo "  sync              - Run sync workers"
        echo "  monitoring        - Run monitoring workers"
        echo "  forever-learning  - Run Forever Learning Cycle"
        echo "  all               - Run all workers"
        echo "  status            - Show worker status"
        echo "  help              - Show this help"
        ;;
esac
