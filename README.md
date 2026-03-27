# 🏛️ Mapping & Inventory - T.I.A. Command Center

**Status:** UNIFIED HANDSHAKE PROTOCOL ACTIVE

## Overview

This repository serves as the **Master Overseer** for Commander DJ-Goana-Coding's entire trading infrastructure. It integrates with the [`pioneer-trader`](https://github.com/DJ-Goana-Coding/pioneer-trader) repository to provide unified visibility across all systems.

## Architecture

- **The Brain (This Repo):** Maps infrastructure, monitors health, generates reports
- **The Muscle ([pioneer-trader](https://github.com/DJ-Goana-Coding/pioneer-trader)):** Executes trades via 7-slot Vortex engine
- **The Bridge (`bridge_protocol.py`):** Real-time synchronization between repos

## Features

### 🌉 Grand Handshake Protocol
- **Live Telemetry Bridge:** Fetches real-time status from Pioneer Trader
- **Retry Logic:** 3 attempts with exponential backoff for resilience
- **Caching:** Falls back to cached data when Pioneer Trader is unreachable
- **Shadow Archive:** Persists telemetry data for offline access

### 📊 Unified Inventory Report
- **Google Drive Districts:** Maps all Citadel folders and architecture
- **Hugging Face Spaces:** Tracks all deployed T.I.A. instances
- **Live Fleet Status:** Real-time 7-slot Vortex engine telemetry
  - Wallet balance and total equity
  - Individual slot status (SCALP vs GRID)
  - Entry prices, current prices, P&L
  - Peak prices and stop losses

### 🚀 FastAPI Backend
- `/` - System status and architecture overview
- `/health` - Health check for monitoring
- `/telemetry` - Local vortex engine telemetry
- `/sync` - Manually trigger Pioneer Trader sync
- `/fleet-status` - Combined local + remote fleet status
- `/start` & `/stop` - Control local trading engine

## Environment Variables

```bash
# Required for Pioneer Trader integration
PIONEER_TRADER_URL=https://your-render-app.onrender.com
PIONEER_AUTH_TOKEN=your_secret_token

# Required for Google Drive scanning
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Optional for Hugging Face integration
HUGGINGFACE_TOKEN=hf_xxxxxxxxxxxxx

# Shadow archive path (default: /app/shadow_archive)
SHADOW_ARCHIVE_PATH=/app/shadow_archive

# Optional for local MEXC trading
MEXC_API_KEY=your_mexc_api_key
MEXC_SECRET_KEY=your_mexc_secret_key
```

## Quick Start

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DJ-Goana-Coding/mapping-and-inventory.git
   cd mapping-and-inventory
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables:**
   ```bash
   export PIONEER_TRADER_URL="https://your-pioneer-instance.onrender.com"
   export PIONEER_AUTH_TOKEN="your_secret_token"
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
   ```

4. **Test the handshake:**
   ```bash
   python test_handshake.py
   ```

5. **Run inventory engine:**
   ```bash
   python inventory_engine.py
   ```

6. **Start the API server:**
   ```bash
   uvicorn backend.main:app --host 0.0.0.0 --port 8000
   ```

### Docker Deployment

1. **Build the image:**
   ```bash
   docker build -t mapping-inventory .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     -p 8000:8000 \
     -e PIONEER_TRADER_URL="https://your-pioneer-instance.onrender.com" \
     -e PIONEER_AUTH_TOKEN="your_secret_token" \
     -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
     -v /path/to/credentials.json:/app/credentials.json \
     mapping-inventory
   ```

### Render Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set environment variables in Render dashboard
4. Deploy using the Dockerfile

## Testing

### Test Pioneer Trader Integration
```bash
python test_handshake.py
```

This will:
- Verify environment variables are set
- Test connection to Pioneer Trader
- Fetch live telemetry
- Sync to shadow archive
- Display slot details

### Manual Sync via API
```bash
curl -X POST http://localhost:8000/sync
```

### Check Fleet Status
```bash
curl http://localhost:8000/fleet-status
```

## File Structure

```
mapping-and-inventory/
├── backend/
│   ├── main.py              # FastAPI application
│   └── services/
│       └── vortex.py        # Local trading engine
├── bridge_protocol.py       # Pioneer Trader integration
├── inventory_engine.py      # Inventory report generator
├── test_handshake.py       # Integration test script
├── Dockerfile              # Container configuration
├── start.sh                # Startup script
├── requirements.txt        # Python dependencies
└── INVENTORY_REPORT.md     # Generated unified report
```

## Error Handling

The system is designed to degrade gracefully:

- **Pioneer Trader Offline:** Uses cached data from shadow archive
- **Network Timeout:** Retries with exponential backoff
- **Authentication Failure:** Logs error but continues with other components
- **Missing Credentials:** Skips optional integrations (HuggingFace, Google Drive)

All errors are logged with `[T.I.A.]` prefix for forensic continuity.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│         MAPPING & INVENTORY (The Brain)                 │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌───────────────┐  │
│  │   Google    │  │  Hugging     │  │   Pioneer     │  │
│  │   Drive     │  │   Face       │  │   Bridge      │  │
│  │   Scanner   │  │   Scanner    │  │   Protocol    │  │
│  └─────────────┘  └──────────────┘  └───────┬───────┘  │
│         │                │                   │          │
│         └────────────────┴───────────────────┘          │
│                          │                              │
│                  ┌───────▼────────┐                     │
│                  │  Unified Report │                     │
│                  │  Generator      │                     │
│                  └────────────────┘                     │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │        FastAPI Backend (Port 8000)                │  │
│  │  /health  /telemetry  /sync  /fleet-status       │  │
│  └──────────────────────────────────────────────────┘  │
└──────────────────────────┬───────────────────────────────┘
                           │
                           │ HTTPS + Auth Token
                           │
┌──────────────────────────▼───────────────────────────────┐
│      PIONEER TRADER (The Muscle)                         │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │   VortexBerserker 7-Slot Engine                   │  │
│  │   - 4 SCALP Slots (Piranha)                       │  │
│  │   - 3 GRID Slots (Trailing)                       │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  Endpoint: /telemetry (Returns live slot status)        │
└──────────────────────────────────────────────────────────┘
```

## Success Criteria

The system successfully achieves:

✅ **Auto-sync** with Pioneer Trader on startup and via API  
✅ **Display live fleet status** in INVENTORY_REPORT.md with all 7 slots  
✅ **Cache telemetry** in shadow archive for offline resilience  
✅ **Provide API endpoints** for manual sync and unified fleet status  
✅ **Degrade gracefully** when Pioneer Trader is unreachable  
✅ **Log all operations** with `[T.I.A.]` signature  

## License

This is a private trading infrastructure repository for DJ-Goana-Coding.

## Support

For issues or questions, please open an issue on GitHub or contact DJ-Goana-Coding.

---

**Commander DJ-Goana-Coding** | **T.I.A. Command Center** | **Node 08 - The Bridge**