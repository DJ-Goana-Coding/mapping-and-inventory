import gradio as gr
import json
import os
import datetime
import requests

# ── Load persona definitions ─────────────────────────────────────────────────
_PERSONAS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'personas.json')
with open(_PERSONAS_PATH) as _f:
    PERSONAS = json.load(_f)

PERSONA_NAMES = list(PERSONAS.keys())

# ── CRYPTO SNIPER config ─────────────────────────────────────────────────────
_SNIPER_CFG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    'CRYPTO_SNIPER', 'sniper_config.json',
)
with open(_SNIPER_CFG_PATH) as _sc:
    _SNIPER_CFG = json.load(_sc)

_S10_IP = _SNIPER_CFG.get('s10_ip', '100.97.78.44')
_PORT   = _SNIPER_CFG.get('port', 8080)
_S10_STATUS_URL = f"http://{_S10_IP}:{_PORT}/status.json"
_S10_LOG_URL    = f"http://{_S10_IP}:{_PORT}/latest.log"


# ── Response logic ────────────────────────────────────────────────────────────
def tia_respond(message: str, history: list, persona_key: str) -> str:
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


def _on_persona_change(key: str) -> str:
    """Update the description box when a different persona is selected."""
    return PERSONAS.get(key, PERSONAS['TIA_ARCHITECT'])['description']


# ── CRYPTO SNIPER helpers ─────────────────────────────────────────────────────
_DASH_WIDTH = 52


def fetch_god_view() -> str:
    """Fetch live status from the S10 Heartbeat Server and return a formatted report."""
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
        f"  S10 node: {_S10_IP}:{_PORT}  |  refreshed: {datetime.datetime.now().strftime('%H:%M:%S')}",
    ]
    return '\n'.join(lines)


# ── Gradio UI ─────────────────────────────────────────────────────────────────
def build_ui() -> gr.Blocks:
    with gr.Blocks(title='T.I.A. ARCHITECT CORE') as demo:
        gr.Markdown('# ⚡ T.I.A. ARCHITECT CORE // D57')
        gr.Markdown(
            '**Tactical Intelligence Architecture** — Multi-Persona ARK_CORE Interface  \n'
            '*Architect: Chance | OPPO_FORGE Origin*'
        )

        with gr.Tabs():
            # ── Tab 1: T.I.A. Chat ────────────────────────────────────────────
            with gr.TabItem('🤖 T.I.A. Chat'):
                with gr.Row():
                    persona_dd = gr.Dropdown(
                        choices=PERSONA_NAMES,
                        value='TIA_ARCHITECT',
                        label='🎭 Active Persona',
                        interactive=True,
                    )
                    persona_desc = gr.Textbox(
                        value=PERSONAS['TIA_ARCHITECT']['description'],
                        label='Persona Description',
                        interactive=False,
                        lines=2,
                    )

                persona_dd.change(_on_persona_change, inputs=persona_dd, outputs=persona_desc)

                gr.ChatInterface(
                    fn=tia_respond,
                    additional_inputs=[persona_dd],
                    chatbot=gr.Chatbot(height=420, label='T.I.A.'),
                    textbox=gr.Textbox(
                        placeholder='Enter your message for T.I.A. ...',
                        label='',
                        submit_btn='⚡ Send',
                    ),
                )

                gr.Markdown(
                    '**Personas available:** ARCHITECT · ORACLE · CITADEL · LIBRARIAN  \n'
                    '_T.I.A. ARCHITECT CORE // D57 — Connected to ARK_CORE_'
                )

            # ── Tab 2: CRYPTO SNIPER God-View ─────────────────────────────────
            with gr.TabItem('📡 CRYPTO SNIPER'):
                gr.Markdown('## 📡 CRYPTO SNIPER — God-View Dashboard')
                gr.Markdown(
                    f'Live feed from **S10 Heartbeat Node** (`{_S10_IP}:{_PORT}`)  \n'
                    '*Press **Refresh** to poll the latest extraction data.*'
                )
                god_view_output = gr.Textbox(
                    label='God-View Status',
                    value=fetch_god_view(),
                    lines=14,
                    interactive=False,
                )
                refresh_btn = gr.Button('🔄 Refresh God-View')
                refresh_btn.click(fn=fetch_god_view, inputs=[], outputs=god_view_output)

    return demo


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    ui = build_ui()
    ui.launch()
