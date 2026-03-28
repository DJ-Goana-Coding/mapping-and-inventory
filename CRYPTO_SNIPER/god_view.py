import os
import time
import json
import requests

# ── Load config ───────────────────────────────────────────────────────────────
_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sniper_config.json')
with open(_CONFIG_PATH) as _f:
    _CFG = json.load(_f)

S10_IP = _CFG.get('s10_ip', '100.97.78.44')
PORT   = _CFG.get('port', 8080)
URL    = f"http://{S10_IP}:{PORT}/status.json"
LOG_URL = f"http://{S10_IP}:{PORT}/latest.log"
REFRESH = _CFG.get('refresh_seconds', 30)


# ── Dashboard renderer ────────────────────────────────────────────────────────
def render_dashboard() -> None:
    os.system('clear')
    print('=' * 50)
    print('       CITADEL OMEGA // GOD-VIEW DASHBOARD       ')
    print('       RESONANCE: 333Hz // GRID: 144-ACTIVE      ')
    print('=' * 50)

    try:
        response = requests.get(URL, timeout=5)
        data = response.json()

        print(f"\n[ARK STATUS]      : {data['status']}")
        print(f"[TOTAL STRIKES]   : {data['total_extractions']}")
        print(f"[VAULTED USDT]    : {data['vaulted_usdt']} USDT")
        print(f"[LAST SYNC]       : {data['last_sync']}")

        log_res = requests.get(LOG_URL, timeout=5)
        latest_strike = log_res.text.strip().split('\n')[-1]
        print(f"\n[LATEST STRIKE]   : {latest_strike}")

    except Exception as e:
        print(f"\n[!] SHROUD DISCONNECTED: {e}")
        print("[ADVICE] Check S10 'Heartbeat Server' status and sniper_config.json.")

    print('\n' + '=' * 50)
    print(f"Monitoring 14-Space Swarm... refresh every {REFRESH}s  (Ctrl+C to exit)")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    while True:
        render_dashboard()
        time.sleep(REFRESH)
