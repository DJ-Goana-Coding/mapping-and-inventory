# 🔒 Sovereign Sync Protocol - Google Drive Integration

## Overview
The Sovereign Sync Protocol enables secure, API-rate-limited synchronization between Google Drive (`CITADEL-BOT` folder) and the `mapping-and-inventory` bridge service, providing mobile command authority with cryptographic verification.

## Features

### 1. **Authenticated Panic Protocol** 🚨
- Real-time panic signal detection from mobile devices
- SHA256 cryptographic signature verification
- Timestamp-based replay attack prevention (5-minute expiry)
- API-safe 30-second check interval
- Security breach logging to Drive

### 2. **Fleet Manifest Synchronization** 📡
- Automatic pull of `fleet_manifest.json` from Drive
- MD5 hash-based change detection
- 60-second sync interval (API-optimized)
- Local registry caching

### 3. **Hourly Position Backups** 💾
- Automatic backup of active trading positions
- Upload to Drive recovery folder every hour
- Version-tracked backup data
- Disaster recovery capability

## Architecture

### Directory Structure
```
mapping-and-inventory/
├── utils/
│   └── drive_auth.py         # Google Drive authentication
├── tasks/
│   └── backup_scheduler.py   # Hourly backup task
├── registry/
│   └── fleet_manifest.json   # Synced fleet configuration
└── bridge_protocol.py        # Main sync protocol
```

### Google Drive Folder Structure
```
CITADEL-BOT/
├── fleet_manifest.json       # Fleet configuration
├── panic.json               # Emergency panic signal (created by Commander)
├── recovery/
│   └── positions_backup.json # Hourly position backups
└── security_logs/
    └── breach_log_YYYYMMDD.json # Security breach attempts
```

## Setup

### 1. Google Service Account Setup
1. Create a Google Cloud project
2. Enable Google Drive API
3. Create a Service Account
4. Generate JSON credentials
5. Share `CITADEL-BOT` folder with service account email

### 2. Environment Variables
Set these in your deployment environment (e.g., Hugging Face Secrets):

```bash
# Base64-encoded Google Service Account JSON
GOOGLE_CREDENTIALS_B64="<base64-encoded-service-account-json>"

# High-entropy secret for panic signal verification
AEGIS_COMMANDER_TOKEN="<your-secure-random-token>"
```

**To encode your credentials:**
```bash
cat service-account.json | base64 -w 0
```

### 3. Dependencies
Already included in `requirements.txt`:
- `google-auth==2.23.0`
- `google-auth-oauthlib==1.1.0`
- `google-auth-httplib2==0.1.1`
- `google-api-python-client==2.100.0`

## Usage

### Checking for Panic Signals
```python
from bridge_protocol import check_panic_signal

if check_panic_signal():
    # Execute emergency liquidation
    print("🚨 PANIC MODE ACTIVATED")
    # Your emergency response code here
```

### Syncing Fleet Manifest
```python
from bridge_protocol import sync_fleet_manifest

manifest = sync_fleet_manifest()
if manifest:
    print(f"📡 New configuration: {manifest['fleet_version']}")
    # Apply new configuration
```

### Backing Up Positions
```python
from bridge_protocol import backup_active_positions

positions = {
    "BTC/USDT": {"entry": 50000, "pnl": 2.5},
    "ETH/USDT": {"entry": 3000, "pnl": 1.2}
}

backup_active_positions(positions)
```

### Hourly Backup Task (Async)
```python
import asyncio
from tasks.backup_scheduler import hourly_backup_task

def get_current_positions():
    # Return your active positions
    return {...}

# Start background task
asyncio.create_task(hourly_backup_task(get_current_positions))
```

## Panic Signal Format

To trigger emergency liquidation, upload this JSON to `CITADEL-BOT/panic.json`:

```json
{
  "timestamp": 1738368000,
  "signature": "<SHA256(AEGIS_COMMANDER_TOKEN + timestamp)>",
  "reason": "Market crash detected"
}
```

**Generate signature (Python):**
```python
import time
import hashlib

token = "your-AEGIS_COMMANDER_TOKEN"
timestamp = int(time.time())
signature = hashlib.sha256(f"{token}{timestamp}".encode()).hexdigest()

panic_signal = {
    "timestamp": timestamp,
    "signature": signature,
    "reason": "Market crash detected"
}
```

## Security Features

### 1. Cryptographic Verification
- SHA256 signatures prevent unauthorized panic signals
- Only signals signed with correct `AEGIS_COMMANDER_TOKEN` are accepted

### 2. Replay Attack Prevention
- Panic signals expire after 5 minutes
- Prevents reuse of old/intercepted signals

### 3. Security Breach Logging
- Invalid signatures logged to Drive
- Daily log files for audit trail
- Automatic breach detection and logging

### 4. API Rate Limiting
- Panic check: 30 seconds (120 requests/hour)
- Manifest sync: 60 seconds (60 requests/hour)
- Well within Google Drive API quota (1000 requests/100 seconds)

## Testing

Run comprehensive test suite:
```bash
python test_drive_sync.py
```

Tests include:
- ✅ Base64 credential decoding
- ✅ CITADEL-BOT folder discovery
- ✅ File download and JSON parsing
- ✅ Panic signal signature verification
- ✅ Timestamp expiry checking
- ✅ Fleet manifest synchronization
- ✅ API rate limiting

## API Quota Management

Google Drive API quotas (free tier):
- **1000 queries per 100 seconds** per user
- **10,000 queries per day** per user

Our usage:
- Panic checks: **2 requests/minute** = ~2,880/day
- Manifest sync: **1 request/minute** = ~1,440/day
- Hourly backups: **24 requests/day**
- **Total: ~4,344 requests/day** (well under 10,000 limit)

## Troubleshooting

### "GOOGLE_CREDENTIALS_B64 not found"
- Verify environment variable is set
- Check base64 encoding is correct (no newlines)

### "CITADEL-BOT folder not found"
- Ensure folder exists in Google Drive
- Share folder with service account email
- Check folder name is exactly "CITADEL-BOT"

### "AEGIS_COMMANDER_TOKEN not configured"
- Set environment variable in deployment settings
- Use high-entropy random string (min 32 characters)

### "Expired panic signal"
- Panic signals expire after 5 minutes
- Generate new signal with current timestamp

## License
Part of the DJ-Goana-Coding mapping-and-inventory project.
