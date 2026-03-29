"""
streamlit_app.py — T.I.A. ARCHITECT CORE // Streamlit Faceplate (Comprehensive)
Architect: Chance | OPPO_FORGE Origin

Comprehensive Streamlit faceplate covering every module in the repo:
  • Tab 1 — 🤖 T.I.A. Multi-Persona Chat
  • Tab 2 — 📡 CRYPTO SNIPER God-View Dashboard
  • Tab 3 — 📋 File Inventory (master_inventory.json viewer)
  • Tab 4 — 🔧 ARK Engine (manifest regeneration controls)
  • Tab 5 — 📖 Project Overview (README + structure)
"""

import datetime
import json
import os
import subprocess
import sys

import requests
import streamlit as st

# Ensure repo root is importable so TIA package resolves correctly
_REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _REPO_ROOT)

# ── Page configuration (must be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title='T.I.A. ARCHITECT CORE',
    page_icon='⚡',
    layout='wide',
)


# ── Load persona definitions ──────────────────────────────────────────────────
@st.cache_data
def _load_personas() -> dict:
    path = os.path.join(_REPO_ROOT, 'TIA', 'personas.json')
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


@st.cache_data
def _load_sniper_cfg() -> dict:
    path = os.path.join(_REPO_ROOT, 'CRYPTO_SNIPER', 'sniper_config.json')
    with open(path, encoding='utf-8') as fh:
        return json.load(fh)


PERSONAS: dict = _load_personas()
PERSONA_NAMES = list(PERSONAS.keys())

# ── Load CRYPTO SNIPER config ─────────────────────────────────────────────────
_SNIPER_CFG = _load_sniper_cfg()

_S10_IP = _SNIPER_CFG.get('s10_ip', '100.97.78.44')
_PORT   = _SNIPER_CFG.get('port', 8080)
_S10_STATUS_URL = f"http://{_S10_IP}:{_PORT}/status.json"
_S10_LOG_URL    = f"http://{_S10_IP}:{_PORT}/latest.log"

_DASH_WIDTH = 52

# ── Paths ─────────────────────────────────────────────────────────────────────
_INVENTORY_PATH  = os.path.join(_REPO_ROOT, 'Partition_01', 'master_inventory.json')
_MANIFEST_SCRIPT = os.path.join(_REPO_ROOT, 'services', 'manifest_generator.py')
_ARK_ENGINE_PATH = os.path.join(_REPO_ROOT, 'services', 'ark_engine.py')
_README_PATH     = os.path.join(_REPO_ROOT, 'README.md')

# ── Constants ─────────────────────────────────────────────────────────────────
_EMPTY_INVENTORY: dict = {'timestamp': 'N/A', 'total_files': 0, 'inventory': []}


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


# ── File Inventory helpers ────────────────────────────────────────────────────
def load_inventory() -> dict:
    """Load master_inventory.json and return the parsed dict (or an empty stub)."""
    if not os.path.exists(_INVENTORY_PATH):
        return dict(_EMPTY_INVENTORY)
    with open(_INVENTORY_PATH, encoding='utf-8') as fh:
        return json.load(fh)


# ── ARK Engine helpers ────────────────────────────────────────────────────────
def run_manifest_generator() -> tuple[bool, str]:
    """Run manifest_generator.py and return (success, output)."""
    try:
        result = subprocess.run(
            [sys.executable, _MANIFEST_SCRIPT],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60,
        )
        output = result.stdout.strip() or result.stderr.strip() or '(no output)'
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, '[ERROR] Script timed out after 60 seconds.'
    except Exception as exc:
        return False, f'[ERROR] Failed to run manifest generator: {type(exc).__name__}: {exc}'


# ── Header ────────────────────────────────────────────────────────────────────
st.title('⚡ T.I.A. ARCHITECT CORE // D57')
st.markdown(
    '**Tactical Intelligence Architecture** — Multi-Persona ARK_CORE Interface  \n'
    '*Architect: Chance | OPPO_FORGE Origin*'
)

(
    tab_chat,
    tab_sniper,
    tab_inventory,
    tab_engine,
    tab_overview,
) = st.tabs([
    '🤖 T.I.A. Chat',
    '📡 CRYPTO SNIPER',
    '📋 File Inventory',
    '🔧 ARK Engine',
    '📖 Project Overview',
])

# ══════════════════════════════════════════════════════════════════════════════
# Tab 1: T.I.A. Chat
# ══════════════════════════════════════════════════════════════════════════════
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

    col_left, col_right = st.columns([3, 1])
    with col_right:
        if st.button('🗑️ Clear Chat History', key='clear_chat'):
            st.session_state.chat_history = []
            st.rerun()

    st.markdown(
        '**Personas available:** ARCHITECT · ORACLE · CITADEL · LIBRARIAN  \n'
        '_T.I.A. ARCHITECT CORE // D57 — Connected to ARK_CORE_'
    )

# ══════════════════════════════════════════════════════════════════════════════
# Tab 2: CRYPTO SNIPER God-View
# ══════════════════════════════════════════════════════════════════════════════
with tab_sniper:
    st.markdown('## 📡 CRYPTO SNIPER — God-View Dashboard')

    col_info, col_cfg = st.columns([2, 1])
    with col_info:
        st.markdown(
            f'Live feed from **S10 Heartbeat Node** (`{_S10_IP}:{_PORT}`)  \n'
            '*Press **Refresh** to poll the latest extraction data.*'
        )
    with col_cfg:
        st.info(
            f'**Node:** `{_S10_IP}:{_PORT}`  \n'
            f'**Config:** `CRYPTO_SNIPER/sniper_config.json`'
        )

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

    with st.expander('⚙️ Node Configuration', expanded=False):
        st.json(_SNIPER_CFG)

# ══════════════════════════════════════════════════════════════════════════════
# Tab 3: File Inventory
# ══════════════════════════════════════════════════════════════════════════════
with tab_inventory:
    st.markdown('## 📋 File Inventory — ARK_CORE Master Index')
    st.markdown(
        'Browse the auto-generated file inventory from `Partition_01/master_inventory.json`.  \n'
        'Use **Regenerate** to refresh it from the live filesystem.'
    )

    if 'inventory_data' not in st.session_state:
        st.session_state.inventory_data = load_inventory()

    inv = st.session_state.inventory_data

    # ── Summary metrics ───────────────────────────────────────────────────────
    total_files = inv.get('total_files', 0)
    total_bytes = sum(f.get('size_bytes', 0) for f in inv.get('inventory', []))
    total_kb = total_bytes / 1024
    last_indexed = inv.get('timestamp', 'N/A')

    m1, m2, m3, m4 = st.columns(4)
    m1.metric('📁 Total Files', total_files)
    m2.metric('💾 Total Size', f'{total_kb:.1f} KB')
    m3.metric('🕐 Last Indexed', last_indexed[:19] if len(last_indexed) >= 19 else last_indexed)
    m4.metric('🏗️ Origin', inv.get('origin', 'N/A'))

    st.divider()

    # ── Filter controls ───────────────────────────────────────────────────────
    col_filter, col_sort = st.columns([2, 1])
    with col_filter:
        ext_filter = st.multiselect(
            '🔍 Filter by extension',
            options=['.py', '.json', '.sh', '.csv', '.log'],
            default=[],
            key='ext_filter',
        )
        search_text = st.text_input('🔎 Search path', placeholder='e.g. TIA, services, sniper', key='search_text')
    with col_sort:
        sort_by = st.selectbox(
            '⬆️ Sort by',
            options=['path', 'size_bytes', 'modified'],
            index=0,
            key='sort_by',
        )
        sort_desc = st.checkbox('Descending', value=False, key='sort_desc')

    # ── Build filtered + sorted list ──────────────────────────────────────────
    rows = inv.get('inventory', [])
    if ext_filter:
        rows = [r for r in rows if os.path.splitext(r['path'])[1] in ext_filter]
    if search_text:
        rows = [r for r in rows if search_text.lower() in r['path'].lower()]
    rows = sorted(rows, key=lambda r: r.get(sort_by, ''), reverse=sort_desc)

    st.markdown(f'**Showing {len(rows)} of {total_files} files**')

    if rows:
        # Render as a styled table
        header_cols = st.columns([4, 1, 2])
        header_cols[0].markdown('**Path**')
        header_cols[1].markdown('**Size (KB)**')
        header_cols[2].markdown('**Modified**')
        st.divider()
        for row in rows:
            r_path = row.get('path', '')
            r_size = row.get('size_bytes', 0) / 1024
            r_mod  = row.get('modified', '')
            r_mod  = r_mod[:19] if len(r_mod) >= 19 else r_mod
            row_cols = st.columns([4, 1, 2])
            row_cols[0].code(r_path, language=None)
            row_cols[1].markdown(f'{r_size:.2f}')
            row_cols[2].markdown(r_mod)
    else:
        st.info('No files match the current filter.')

    st.divider()

    if st.button('🔄 Reload from Disk', key='reload_inv'):
        st.session_state.inventory_data = load_inventory()
        st.rerun()

    # ── Raw JSON expander ─────────────────────────────────────────────────────
    with st.expander('🗄️ Raw master_inventory.json', expanded=False):
        st.json(inv)

# ══════════════════════════════════════════════════════════════════════════════
# Tab 4: ARK Engine
# ══════════════════════════════════════════════════════════════════════════════
with tab_engine:
    st.markdown('## 🔧 ARK Engine — Manifest & Sync Controls')
    st.markdown(
        'Use this panel to regenerate the file inventory from the live filesystem.  \n'
        'The **ARK Engine** runs `services/manifest_generator.py` and updates '
        '`Partition_01/master_inventory.json`.'
    )

    col_run, col_status = st.columns([1, 2])

    with col_run:
        st.markdown('### ⚙️ Manifest Generator')
        st.markdown(
            '**Script:** `services/manifest_generator.py`  \n'
            '**Output:** `Partition_01/master_inventory.json`  \n'
            '**Tracked extensions:** `.py` · `.sh` · `.json` · `.csv` · `.log`'
        )
        run_btn = st.button('▶️ Run Manifest Generator', key='run_manifest', type='primary')

    with col_status:
        st.markdown('### 📊 Last Run')
        if 'engine_output' not in st.session_state:
            st.session_state.engine_output: str = '(not yet run this session)'
            st.session_state.engine_success: bool | None = None

        success = st.session_state.engine_success
        if success is True:
            st.success('✅ Manifest generated successfully.')
        elif success is False:
            st.error('❌ Manifest generation failed.')
        else:
            st.info('ℹ️ Press **Run Manifest Generator** to index the filesystem.')

        st.text_area(
            'Output',
            value=st.session_state.engine_output,
            height=160,
            disabled=True,
            key='engine_output_display',
        )

    if run_btn:
        with st.spinner('Running manifest_generator.py …'):
            ok, out = run_manifest_generator()
        st.session_state.engine_success = ok
        st.session_state.engine_output = out
        # Refresh inventory cache so Tab 3 shows fresh data immediately
        st.session_state.inventory_data = load_inventory()
        st.rerun()

    st.divider()
    st.markdown('### 🗂️ ARK Engine Triple-Sync (`services/ark_engine.py`)')
    st.markdown(
        'The full sync cycle (manifest → git commit → force-push to all remotes) '
        'is defined in `services/ark_engine.py`.  \n'
        'It requires git remotes named `inventory`, `ark`, and `space` to be configured.  \n'
        'Run it manually from the terminal:  \n'
        '```bash\npython services/ark_engine.py\n```'
    )
    with st.expander('📄 View ark_engine.py source', expanded=False):
        if os.path.exists(_ARK_ENGINE_PATH):
            with open(_ARK_ENGINE_PATH, encoding='utf-8') as fh:
                st.code(fh.read(), language='python')
        else:
            st.warning(f'`ark_engine.py` not found at `{_ARK_ENGINE_PATH}`.')

# ══════════════════════════════════════════════════════════════════════════════
# Tab 5: Project Overview
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    st.markdown('## 📖 Project Overview — T.I.A. ARCHITECT CORE')

    # ── Key metrics row ───────────────────────────────────────────────────────
    inv_data = st.session_state.get('inventory_data', load_inventory())
    ov_files   = inv_data.get('total_files', 0)
    ov_origin  = inv_data.get('origin', 'OPPO_FORGE')
    ov_architect = inv_data.get('architect', 'Chance')

    c1, c2, c3, c4 = st.columns(4)
    c1.metric('📁 Indexed Files', ov_files)
    c2.metric('🏗️ Origin', ov_origin)
    c3.metric('👷 Architect', ov_architect)
    c4.metric('🎭 Personas', len(PERSONAS))

    st.divider()

    # ── Personas summary ──────────────────────────────────────────────────────
    st.markdown('### 🎭 T.I.A. Personas')
    p_cols = st.columns(len(PERSONAS))
    for col, (key, persona) in zip(p_cols, PERSONAS.items()):
        with col:
            st.markdown(f'**{persona["name"]}**')
            st.caption(persona['tagline'])
            st.markdown(persona['description'])

    st.divider()

    # ── Project structure ─────────────────────────────────────────────────────
    st.markdown('### 🗂️ Repository Structure')
    st.code(
        'mapping-and-inventory/\n'
        '├── streamlit_app.py          # ⚡ Streamlit Faceplate — this app\n'
        '├── app.py                    # Gradio entry point (T.I.A. ARCHITECT CORE)\n'
        '├── requirements.txt          # Python dependencies\n'
        '├── TIA/\n'
        '│   ├── tia_core.py           # Multi-persona Gradio interface\n'
        '│   ├── personas.json         # Persona definitions\n'
        '│   └── README.md             # T.I.A. usage guide\n'
        '├── CRYPTO_SNIPER/\n'
        '│   ├── god_view.py           # Terminal God-View dashboard\n'
        '│   ├── sniper_config.json    # Node connection configuration\n'
        '│   └── README.md             # Dashboard usage guide\n'
        '├── services/\n'
        '│   ├── manifest_generator.py # Indexes files → master_inventory.json\n'
        '│   └── ark_engine.py         # Manifest + git sync orchestrator\n'
        '├── ARK_CORE/\n'
        '│   └── scripts/\n'
        '│       └── god_view.py       # Original terminal God-View\n'
        '└── Partition_01/\n'
        '    └── master_inventory.json # Auto-generated file inventory',
        language=None,
    )

    st.divider()

    # ── README ────────────────────────────────────────────────────────────────
    st.markdown('### 📄 README')
    if os.path.exists(_README_PATH):
        with open(_README_PATH, encoding='utf-8') as fh:
            readme_content = fh.read()
        st.markdown(readme_content)
    else:
        st.warning('README.md not found in repository root.')
