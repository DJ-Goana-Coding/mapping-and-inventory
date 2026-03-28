"""
ARK_CORE/scripts/god_view.py — Original GOD-VIEW Dashboard
Architect: Chance | OPPO_FORGE Origin

Polls the S10 Heartbeat Server for real-time extraction and vault data.
Configuration is loaded from CRYPTO_SNIPER/sniper_config.json so the IP
and port are never hard-coded.
"""

import json
import os
import time

import requests

# ── Load config ───────────────────────────────────────────────────────────────
# Resolve relative to the repo root (two levels up from this script)
_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_CONFIG_PATH = os.path.join(_REPO_ROOT, 'CRYPTO_SNIPER', 'sniper_config.json')

with open(_CONFIG_PATH, encoding='utf-8') as _f:
    _CFG = json.load(_f)

S10_IP = _CFG.get('s10_ip', '100.97.78.44')
PORT = _CFG.get('port', 8080)
REFRESH = _CFG.get('refresh_seconds', 30)
URL = f"http://{S10_IP}:{PORT}/status.json"
LOG_URL = f"http://{S10_IP}:{PORT}/latest.log"


# ── Dashboard renderer ────────────────────────────────────────────────────────
def render_dashboard() -> None:
    """Clear the terminal and print the latest GOD-VIEW status."""
    os.system('clear')
    print('=' * 50)
    print('       CITADEL OMEGA // GOD-VIEW DASHBOARD       ')
    print('       RESONANCE: 333Hz // GRID: 144-ACTIVE      ')
    print('=' * 50)

    try:
        response = requests.get(URL, timeout=5)
        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise ValueError(f'S10 status endpoint returned invalid JSON: {exc}') from exc

        print(f"\n[ARK STATUS]      : {data.get('status', 'N/A')}")
        print(f"[TOTAL STRIKES]   : {data.get('total_extractions', 'N/A')}")
        print(f"[VAULTED USDT]    : {data.get('vaulted_usdt', 'N/A')} USDT")
        print(f"[LAST SYNC]       : {data.get('last_sync', 'N/A')}")

        try:
            log_text = requests.get(LOG_URL, timeout=5).text.strip()
            latest_strike = log_text.split('\n')[-1] if log_text else '(no log data)'
        except requests.exceptions.RequestException as exc:
            latest_strike = f'(log unavailable: {type(exc).__name__})'

        print(f"\n[LATEST STRIKE]   : {latest_strike}")

    except Exception as exc:
        print(f"\n[!] SHROUD DISCONNECTED: {type(exc).__name__}: {exc}")
        print("[ADVICE] Check S10 'Heartbeat Server' status and sniper_config.json.")

    print('\n' + '=' * 50)
    print(f"Monitoring 14-Space Swarm... refresh every {REFRESH}s  (Ctrl+C to exit)")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    while True:
        render_dashboard()
        time.sleep(REFRESH)
