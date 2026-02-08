#!/bin/bash

# Start script for VortexBerserker Hybrid Swarm

echo "🏰 CITADEL V6.9: LIVE FIRE ENGAGED."
echo "⚔️ SNIPER MODE: RSI<40 + Price>EMA50 | 🛡️ STOP: 1.5%"

# Run the FastAPI application with uvicorn
uvicorn backend.main:app --host 0.0.0.0 --port 10000 --log-level info
