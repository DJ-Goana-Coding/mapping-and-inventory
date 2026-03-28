# CRYPTO_SNIPER — GOD-VIEW Dashboard

Live monitoring dashboard for the ARK_CORE cryptocurrency extraction and vault system.

## Files

| File | Description |
|------|-------------|
| `god_view.py` | Real-time dashboard polling the ARK node every 30 seconds |
| `sniper_config.json` | Node connection configuration template |

## Usage

### Configure the node endpoint

Copy and edit the config file:

```bash
cp CRYPTO_SNIPER/sniper_config.json CRYPTO_SNIPER/sniper_config.local.json
# Edit sniper_config.local.json with your actual S10 IP
```

### Launch the GOD-VIEW dashboard

```bash
python CRYPTO_SNIPER/god_view.py
```

Press `Ctrl+C` to exit.

## Dashboard Readings

| Field | Meaning |
|-------|---------|
| `ARK STATUS` | Node operational status |
| `TOTAL STRIKES` | Cumulative extraction events |
| `VAULTED USDT` | Total USDT secured in vault |
| `LAST SYNC` | Timestamp of last node heartbeat |
| `LATEST STRIKE` | Most recent extraction log entry |

## Requirements

```
requests
```

---

*Architect: Chance | CITADEL OMEGA // GRID: 144-ACTIVE*
