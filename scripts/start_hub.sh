#!/usr/bin/env bash
# scripts/start_hub.sh — Launch FastAPI sidecar (main_api.py) and the
# Streamlit faceplate (app.py) together inside the HF Space container.
#
# Streamlit owns port 7860 (HF Space user-facing port).
# FastAPI sidecar owns port 10000 (the SOVEREIGN_HUD_ALIGNMENT v26.59
# "PORT_RESONANCE_WELD" frequency required for the Vercel Command Deck
# to recognize the node). Override with API_PORT if needed.
#
# Both processes share the same data/vector_store/ FAISS index. If either
# child exits, the container exits so HF Spaces will restart it.

set -euo pipefail

API_PORT="${API_PORT:-10000}"
UI_PORT="${UI_PORT:-7860}"

echo "════════════════════════════════════════════════════════════"
echo "🏛  MASTER HUB BOOT — multi-process weld"
echo "    FastAPI sidecar : 0.0.0.0:${API_PORT} (main_api:app)"
echo "    Streamlit HUD   : 0.0.0.0:${UI_PORT} (app.py)"
echo "════════════════════════════════════════════════════════════"

# Best-effort warm-up: build the FAISS index on first boot if missing.
# Failure here is non-fatal — the sidecar will rebuild on first /v1/ingest.
if [ ! -f "data/vector_store/harvest.index" ]; then
  echo "[start_hub] No FAISS index found. Attempting initial reindex..."
  python -m services.rag_hub --reindex || \
    echo "[start_hub] WARN: initial reindex failed; sidecar will rebuild on demand."
fi

# Launch the FastAPI sidecar in the background.
uvicorn main_api:app \
  --host 0.0.0.0 \
  --port "${API_PORT}" \
  --workers 1 \
  --log-level info &
API_PID=$!

# Trap signals so both children get cleaned up together.
cleanup() {
  echo "[start_hub] Shutting down (PID API=${API_PID})..."
  if kill -0 "${API_PID}" 2>/dev/null; then
    kill "${API_PID}" || true
  fi
  wait "${API_PID}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Launch Streamlit in the foreground; if it exits, the container exits.
exec streamlit run app.py \
  --server.port="${UI_PORT}" \
  --server.address=0.0.0.0 \
  --server.headless=true \
  --browser.gatherUsageStats=false
