#!/bin/bash

echo "🏰 [T.I.A.] NODE 08 - COMMAND BRIDGE IGNITION"
echo "============================================="

# Validate environment
if [ -z "$PIONEER_TRADER_URL" ]; then
    echo "⚠️ WARNING: PIONEER_TRADER_URL not set - Pioneer integration disabled"
fi

if [ -z "$PIONEER_AUTH_TOKEN" ]; then
    echo "⚠️ WARNING: PIONEER_AUTH_TOKEN not set - Authentication will fail"
fi

# Create shadow archive if not exists
mkdir -p ${SHADOW_ARCHIVE_PATH:-/app/shadow_archive}

# Run inventory sync (one-time on startup)
echo "🛰️ [T.I.A.] Running initial inventory sync..."
python inventory_engine.py || echo "⚠️ Inventory sync failed (non-critical)"

# Start FastAPI server
echo "🚀 [T.I.A.] Starting FastAPI server..."
uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
