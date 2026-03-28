"""
streamlit_app.py — T.I.A. ARCHITECT CORE // Streamlit Faceplate
Architect: Chance | OPPO_FORGE Origin

Provides a Streamlit-based interface covering:
  • T.I.A. Multi-Persona Chat
  • CRYPTO SNIPER God-View Dashboard
"""

import sys
import os
import datetime

import streamlit as st

# Ensure repo root is importable so TIA package resolves correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
import requests

# ── Load persona definitions ──────────────────────────────────────────────────
_PERSONAS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'TIA', 'personas.json')
with open(_PERSONAS_PATH) as _f:
    PERSONAS: dict = json.load(_f)

PERSONA_NAMES = list(PERSONAS.keys())

# ── Load CRYPTO SNIPER config ─────────────────────────────────────────────────
_SNIPER_CFG_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'CRYPTO_SNIPER', 'sniper_config.json',
)
with open(_SNIPER_CFG_PATH) as _sc:
    _SNIPER_CFG = json.load(_sc)

_S10_IP = _SNIPER_CFG.get('s10_ip', '100.97.78.44')
_PORT   = _SNIPER_CFG.get('port', 8080)
_S10_STATUS_URL = f"http://{_S10_IP}:{_PORT}/status.json"
_S10_LOG_URL    = f"http://{_S10_IP}:{_PORT}/latest.log"

_DASH_WIDTH = 52


# ── Response logic ────────────────────────────────────────────────────────────
def tia_respond(message: str, persona_key: str) -> str:
    """Generate a T.I.A. response using the selected persona."""
    persona = PERSONAS.get(persona_key, PERSONAS['TIA_ARCHITECT'])
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return (
        f"[{persona['prefix']} | {timestamp}]\n"
        f"Persona: {persona['name']}  |  {persona['tagline']}\n"
        f"{'━' * 48}\n"
        f"Analyzing ({persona['style']}): {message}\n"
        f"\n— {persona['signature']}"
    )


# ── CRYPTO SNIPER helpers ─────────────────────────────────────────────────────
def fetch_god_view() -> str:
    """Fetch live status from the S10 Heartbeat Server and return a formatted report."""
    refreshed_at = datetime.datetime.now().strftime('%H:%M:%S')
    lines = [
        '═' * _DASH_WIDTH,
        '     CITADEL OMEGA // GOD-VIEW DASHBOARD     ',
        '     RESONANCE: 333Hz // GRID: 144-ACTIVE    ',
        '═' * _DASH_WIDTH,
    ]
    try:
        status_resp = requests.get(_S10_STATUS_URL, timeout=5)
        try:
            status = status_resp.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise ValueError(f'S10 status endpoint returned invalid JSON: {exc}') from exc
        lines += [
            f"  ARK STATUS      : {status.get('status', 'N/A')}",
            f"  TOTAL STRIKES   : {status.get('total_extractions', 'N/A')}",
            f"  VAULTED USDT    : {status.get('vaulted_usdt', 'N/A')} USDT",
            f"  LAST SYNC       : {status.get('last_sync', 'N/A')}",
        ]
        try:
            log_text = requests.get(_S10_LOG_URL, timeout=5).text.strip()
            latest = log_text.split('\n')[-1] if log_text else '(no log data)'
        except requests.exceptions.RequestException as exc:
            latest = f'(log unavailable: {type(exc).__name__})'
        lines.append(f"  LATEST STRIKE   : {latest}")
    except Exception as exc:
        lines += [
            f"  [!] SHROUD DISCONNECTED: {type(exc).__name__}: {exc}",
            '  [ADVICE] Verify S10 Heartbeat Server and sniper_config.json.',
        ]
    lines += [
        '═' * _DASH_WIDTH,
        f"  S10 node: {_S10_IP}:{_PORT}  |  refreshed: {refreshed_at}",
    ]
    return '\n'.join(lines)


# ── Page configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title='T.I.A. ARCHITECT CORE',
    page_icon='⚡',
    layout='wide',
)

st.title('⚡ T.I.A. ARCHITECT CORE // D57')
st.markdown(
    '**Tactical Intelligence Architecture** — Multi-Persona ARK_CORE Interface  \n'
    '*Architect: Chance | OPPO_FORGE Origin*'
)

tab_chat, tab_sniper = st.tabs(['🤖 T.I.A. Chat', '📡 CRYPTO SNIPER'])

# ── Tab 1: T.I.A. Chat ────────────────────────────────────────────────────────
with tab_chat:
    col_dd, col_desc = st.columns([1, 2])
    with col_dd:
        persona_key = st.selectbox(
            '🎭 Active Persona',
            options=PERSONA_NAMES,
            index=0,
        )
    with col_desc:
        st.text_area(
            'Persona Description',
            value=PERSONAS[persona_key]['description'],
            height=80,
            disabled=True,
        )

    # Initialise chat history in session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history: list[dict] = []

    for entry in st.session_state.chat_history:
        with st.chat_message(entry['role']):
            st.markdown(entry['content'])

    user_input = st.chat_input('Enter your message for T.I.A. ...')
    if user_input:
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        with st.chat_message('user'):
            st.markdown(user_input)

        response = tia_respond(user_input, persona_key)
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
        with st.chat_message('assistant'):
            st.markdown(f'```\n{response}\n```')

    st.markdown(
        '**Personas available:** ARCHITECT · ORACLE · CITADEL · LIBRARIAN  \n'
        '_T.I.A. ARCHITECT CORE // D57 — Connected to ARK_CORE_'
    )

# ── Tab 2: CRYPTO SNIPER God-View ─────────────────────────────────────────────
with tab_sniper:
    st.markdown('## 📡 CRYPTO SNIPER — God-View Dashboard')
    st.markdown(
        f'Live feed from **S10 Heartbeat Node** (`{_S10_IP}:{_PORT}`)  \n'
        '*Press **Refresh** to poll the latest extraction data.*'
    )

    # Initialise god-view text in session state
    if 'god_view_text' not in st.session_state:
        st.session_state.god_view_text: str = fetch_god_view()

    st.text_area(
        'God-View Status',
        value=st.session_state.god_view_text,
        height=320,
        disabled=True,
        key='god_view_display',
    )

    if st.button('🔄 Refresh God-View'):
        st.session_state.god_view_text = fetch_god_view()
        st.rerun()
