"""
Q.G.T.N.L. (0) // MAPPING & INVENTORY LIBRARIAN
Citadel Omega Sovereign HUD — Central mapping and inventory dashboard.
Connects: ARK repos, GDrive, T.I.A., datasets, and all device nodes.
"""
import sys
import os
import subprocess
from pathlib import Path

# Ensure services are importable from this file's location
sys.path.insert(0, os.path.dirname(__file__))

import json
import pandas as pd
import streamlit as st

from services.repo_mapper import (
    get_system_snapshot,
    build_connection_graph,
    KNOWN_REPOS,
    FRAMEWORKS,
)
from services.gdrive_connector import (
    setup_rclone_config,
    get_gdrive_status,
    sync_from_gdrive,
    list_gdrive,
    GDRIVE_TARGETS,
)
from services.tia_connector import get_tia_response, tia_analyze_repo
from services.dataset_connector import (
    load_local_inventory,
    search_inventory,
    load_neuron_data,
    get_dataset_summary,
    get_inventory_stats,
)

# ── Configuration ──────────────────────────────────────────────────────────────
HF_SPACE_ID = "DJ-Goana-Coding/Mapping-and-Inventory"

# ── Load PvC Trigger Map for Orange Star Vision ───────────────────────────────
PVC_TRIGGER_MAP_PATH = Path(__file__).parent / "src" / "pvc_trigger_map.json"
try:
    with open(PVC_TRIGGER_MAP_PATH, 'r') as f:
        PVC_TRIGGERS = json.load(f)
except Exception as e:
    print(f"⚠️  Could not load PvC trigger map: {e}")
    PVC_TRIGGERS = None

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CITADEL OMEGA — Mapping & Inventory",
    layout="wide",
    page_icon="🏰",
)

# ── Rclone boot ────────────────────────────────────────────────────────────────
_rclone_ok, _rclone_msg = setup_rclone_config()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.svg", width=180)
    st.image("https://img.shields.io/badge/CITADEL-OMEGA-blueviolet?style=for-the-badge", width=220)
    st.markdown("## 🏰 SOVEREIGN HUD")

    # Live token status
    snap = get_system_snapshot()
    tokens = snap.get("env_tokens", {})
    for tok, status in tokens.items():
        icon = "✅" if status == "DETECTED" else "❌"
        st.markdown(f"{icon} **{tok}**")

    st.divider()
    gdrive_status = get_gdrive_status()
    st.markdown(f"**rclone:** {'✅ Installed' if gdrive_status['rclone_installed'] else '❌ Missing'}")
    st.markdown(f"**GDrive Config:** {'✅ Ready' if gdrive_status['config_file_exists'] or gdrive_status['env_key_present'] else '⚠️ Not configured'}")

    st.divider()
    inventory = load_local_inventory("master_inventory.json")
    st.metric("📦 Inventory Entities", len(inventory))
    st.metric("🗂️ Known Repos / Nodes", len(KNOWN_REPOS))
    st.metric("🔧 Frameworks Tracked", len(FRAMEWORKS))

# ── Helper functions ────────────────────────────────────────────────────────

_TYPE_ICON = {
    "GitHub Repo": "🐙",
    "HuggingFace Space": "🤗",
    "Device Node": "📱",
    "Cloud Storage": "☁️",
}
_TYPE_COLOR = {
    "GitHub Repo": "#4f8ef7",
    "HuggingFace Space": "#ff7043",
    "Device Node": "#66bb6a",
    "Cloud Storage": "#ab47bc",
    "Node": "#78909c",
}

def _repo_icon(repo_type: str) -> str:
    return _TYPE_ICON.get(repo_type, "🔷")


# ── Modal dialog definitions ────────────────────────────────────────────────


@st.dialog("🔷 Repo / Node Detail")
def _modal_repo_detail(repo: dict):
    st.markdown(f"## {_repo_icon(repo['type'])} {repo['name']}")
    st.markdown(f"**Type:** {repo['type']}")
    st.markdown(f"**Role:** {repo['role']}")
    st.markdown(f"**Framework:** {repo['framework']}")
    if repo["url"] != "local":
        st.markdown(f"**URL:** [{repo['url']}]({repo['url']})")
    st.markdown(f"**Connections:** {', '.join(repo['connected_to'])}")
    st.divider()
    if st.button("🧠 Ask T.I.A. about this node", key="tia_repo_modal"):
        with st.spinner("T.I.A. processing…"):
            resp = get_tia_response(
                f"Describe the role of '{repo['name']}' ({repo['type']}, framework: {repo['framework']}) "
                f"in the Citadel Omega system. Connected to: {', '.join(repo['connected_to'])}."
            )
        st.info(resp)


@st.dialog("📄 Inventory Item Detail")
def _modal_item_detail(item: dict):
    for k, v in item.items():
        st.markdown(f"**{k}:** `{v}`")
    st.divider()
    if st.button("🧠 Ask T.I.A. about this item", key="tia_item_modal"):
        with st.spinner("T.I.A. processing…"):
            tia_resp = get_tia_response(
                f"Tell me about this inventory item and its role in the system: {json.dumps(item)}"
            )
        st.info(tia_resp)


@st.dialog("📦 Dataset Detail")
def _modal_dataset_detail(ds_item: dict, inv: list):
    st.markdown(f"## 📦 {ds_item['name']}")
    st.markdown(f"**Type:** {ds_item['type']}")
    st.markdown(f"**Path/URL:** `{ds_item['path']}`")
    st.markdown(f"**Description:** {ds_item['description']}")
    st.markdown(f"**Status:** {ds_item['status']}")
    st.divider()
    if ds_item["type"] == "local" and ds_item["path"] == "master_inventory.json":
        if inv:
            st.write(f"📋 Showing first 20 of {len(inv)} entries:")
            st.dataframe(pd.DataFrame(inv[:20]), use_container_width=True, hide_index=True)
        else:
            st.info("Inventory not loaded.")
    elif ds_item["type"] == "local" and ds_item["path"] == "Forever_Learning":
        neurons_data = load_neuron_data()
        if neurons_data:
            st.write(f"📋 {len(neurons_data)} neuron files found:")
            st.dataframe(pd.DataFrame(neurons_data), use_container_width=True, hide_index=True)
        else:
            st.info("No neuron files found.")
    elif ds_item["type"] == "local" and ds_item["path"] == "Archive_Vault":
        archive_path = os.path.join(os.getcwd(), "Archive_Vault", "master_backup.json")
        if os.path.exists(archive_path):
            with open(archive_path) as f:
                backup_data = json.load(f)
            if isinstance(backup_data, list):
                st.dataframe(pd.DataFrame(backup_data[:20]), use_container_width=True, hide_index=True)
            else:
                st.json(backup_data)
        else:
            st.info("Archive vault file not found locally.")
    elif ds_item["type"] in ("gdrive", "huggingface"):
        st.info(f"Remote dataset — use the Cloud Sync tab to pull data, or visit {ds_item['path']}")


tabs = st.tabs([
    "🗺️ System Map",
    "📚 Librarian",
    "📦 Datasets",
    "🧠 T.I.A. Oracle",
    "☁️ Cloud Sync",
    "🤗 HF Space",
    "🤖 Worker Status",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SYSTEM MAP
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.title("🗺️ System Map — Repos, Spaces & Connections")
    st.caption("Visual scaffold of all connected repositories, device nodes, cloud stores, and frameworks.")

    # ── Connection graph ──────────────────────────────────────────────────────
    nodes, edges = build_connection_graph()

    try:
        import plotly.graph_objects as go
        import networkx as nx

        G = nx.Graph()
        type_colors = _TYPE_COLOR
        for n in nodes:
            G.add_node(n["id"], **n)
        for src, dst in edges:
            G.add_edge(src, dst)

        pos = nx.spring_layout(G, seed=42, k=2.5)

        edge_x, edge_y = [], []
        for src, dst in G.edges():
            x0, y0 = pos[src]
            x1, y1 = pos[dst]
            edge_x += [x0, x1, None]
            edge_y += [y0, y1, None]

        node_x = [pos[n][0] for n in G.nodes()]
        node_y = [pos[n][1] for n in G.nodes()]
        node_text = [
            f"<b>{G.nodes[n]['label']}</b><br>"
            f"Type: {G.nodes[n].get('type','')}<br>"
            f"Role: {G.nodes[n].get('role','')}<br>"
            f"Framework: {G.nodes[n].get('framework','')}"
            for n in G.nodes()
        ]
        node_colors = [type_colors.get(G.nodes[n].get("type", ""), "#78909c") for n in G.nodes()]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            mode="lines",
            line=dict(width=1.5, color="#888"),
            hoverinfo="none",
        ))
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode="markers+text",
            marker=dict(size=28, color=node_colors, line=dict(width=2, color="white")),
            text=list(G.nodes()),
            textposition="top center",
            hovertext=node_text,
            hoverinfo="text",
        ))
        fig.update_layout(
            title="Citadel Omega Connection Graph",
            showlegend=False,
            height=520,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="#0e1117",
            plot_bgcolor="#0e1117",
            font=dict(color="white"),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Legend
        legend_parts = [
            f"{_repo_icon(t)} {t}"
            for t in _TYPE_ICON
        ]
        st.markdown("**Legend:**  " + "  ".join(legend_parts))

    except ImportError:
        st.warning("Install `plotly` and `networkx` for the visual graph (see requirements.txt).")
        st.json({"nodes": [n["id"] for n in nodes], "edges": [list(e) for e in edges]})

    st.divider()

    # ── Repo / Node cards ─────────────────────────────────────────────────────
    st.subheader("📋 Repo & Node Registry")
    cols = st.columns(3)
    for i, repo in enumerate(KNOWN_REPOS):
        with cols[i % 3]:
            with st.expander(f"{_repo_icon(repo['type'])} {repo['name']}", expanded=False):
                st.markdown(f"**Type:** {repo['type']}")
                st.markdown(f"**Role:** {repo['role']}")
                st.markdown(f"**Framework:** {repo['framework']}")
                if repo["url"] != "local":
                    st.markdown(f"**URL:** [{repo['url']}]({repo['url']})")
                st.markdown(f"**Connections:** {', '.join(repo['connected_to'])}")
                if st.button("🔎 Full Details + T.I.A.", key=f"repo_modal_{i}"):
                    _modal_repo_detail(repo)

    st.divider()

    # ── Frameworks table ──────────────────────────────────────────────────────
    st.subheader("🔧 Frameworks & Tech Stack")
    df_fw = pd.DataFrame(FRAMEWORKS)
    df_fw["used_in"] = df_fw["used_in"].apply(lambda x: ", ".join(x))
    st.dataframe(df_fw, use_container_width=True, hide_index=True)

    st.divider()

    # ── Local scaffold ────────────────────────────────────────────────────────
    st.subheader("🗂️ Local Repo Scaffold")
    from services.repo_mapper import get_local_structure
    structure = get_local_structure()
    scaffold_data = [
        {"directory": k, "files": v["file_count"], "subdirs": len(v["dirs"])}
        for k, v in structure.items()
        if k != "."
    ]
    if scaffold_data:
        st.dataframe(
            pd.DataFrame(scaffold_data).sort_values("files", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

    # ── Git remotes ───────────────────────────────────────────────────────────
    from services.repo_mapper import get_git_remotes
    remotes = get_git_remotes()
    if remotes:
        st.subheader("🔗 Git Remotes")
        df_r = pd.DataFrame(list(remotes.items()), columns=["Remote", "URL"])
        st.dataframe(df_r, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — LIBRARIAN
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.title("📚 Librarian — Master Inventory")
    st.caption("Search and explore the 9,354-entity master inventory ledger.")

    if not inventory:
        st.error("⚠️ master_inventory.json not found. Ensure it is in the repo root.")
    else:
        stats = get_inventory_stats(inventory)

        # ── Stats row ─────────────────────────────────────────────────────────
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Total Entities", stats.get("total", 0))
        top_ext = list(stats.get("top_extensions", {}).items())
        c2.metric("📄 Top File Type", f".{top_ext[0][0]} ({top_ext[0][1]})" if top_ext else "—")
        top_dir = list(stats.get("top_directories", {}).items())
        c3.metric("📂 Top Directory", f"{top_dir[0][0]} ({top_dir[0][1]})" if top_dir else "—")

        st.divider()

        # ── Search ────────────────────────────────────────────────────────────
        col_s, col_lim = st.columns([3, 1])
        with col_s:
            search_q = st.text_input("🔍 Search inventory (name, path, type…)", placeholder="e.g. trader, lore, ark_engine")
        with col_lim:
            result_limit = st.selectbox("Max results", [50, 100, 250, 500], index=1)

        if search_q:
            results = search_inventory(inventory, search_q, limit=result_limit, pvc_triggers=PVC_TRIGGERS)
            
            # Check if Orange Star Vision was triggered
            pvc_flagged = any(item.get("_pvc_flagged", False) for item in results)
            
            st.write(f"Found **{len(results)}** matches for `{search_q}`")
            
            if pvc_flagged:
                st.warning("🟠 **ORANGE STAR VISION ACTIVE** - PvC compliance triggers detected in search results. Cross-referencing with Section 44 legislative framework...")
            
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # ── Item detail modal ──────────────────────────────────────────
                st.subheader("🔎 Item Detail")
                item_names = [str(r.get("name", i)) for i, r in enumerate(results[:50])]
                selected_name = st.selectbox("Select an item to inspect:", item_names)
                if selected_name:
                    idx = item_names.index(selected_name)
                    item = results[idx]
                    if st.button("📄 Open Item Modal", key="open_item_modal"):
                        _modal_item_detail(item)
        else:
            # Default: show first 50 and stats charts
            st.subheader("📊 File Type Distribution")
            try:
                import plotly.express as px
                ext_data = stats.get("top_extensions", {})
                if ext_data:
                    fig_ext = px.pie(
                        values=list(ext_data.values()),
                        names=[f".{k}" for k in ext_data.keys()],
                        title="Top File Extensions",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                    )
                    fig_ext.update_layout(paper_bgcolor="#0e1117", font=dict(color="white"))
                    st.plotly_chart(fig_ext, use_container_width=True)
            except ImportError:
                st.bar_chart(stats.get("top_extensions", {}))

            st.subheader("📂 Top Directories")
            dir_data = stats.get("top_directories", {})
            if dir_data:
                try:
                    fig_dir = px.bar(
                        x=list(dir_data.keys()),
                        y=list(dir_data.values()),
                        labels={"x": "Directory", "y": "File Count"},
                        color=list(dir_data.values()),
                        color_continuous_scale="Viridis",
                    )
                    fig_dir.update_layout(paper_bgcolor="#0e1117", font=dict(color="white"))
                    st.plotly_chart(fig_dir, use_container_width=True)
                except Exception:
                    st.bar_chart(dir_data)

            st.subheader("🗃️ First 50 Entries")
            st.dataframe(pd.DataFrame(inventory[:50]), use_container_width=True, hide_index=True)

        # ── Neuron data ────────────────────────────────────────────────────────
        st.divider()
        st.subheader("🧬 Forever Learning Neurons")
        neurons = load_neuron_data()
        if neurons:
            st.write(f"**{len(neurons)}** neuron files indexed.")
            df_n = pd.DataFrame(neurons)
            st.dataframe(df_n, use_container_width=True, hide_index=True)
        else:
            st.info("No neuron files found in Forever_Learning/.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — DATASETS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.title("📦 Datasets — Connected Libraries")
    st.caption("All datasets, vaults, and libraries connected to the Citadel Omega stack.")

    ds_summary = get_dataset_summary()
    df_ds = pd.DataFrame(ds_summary)
    st.dataframe(df_ds[["name", "type", "description", "status"]], use_container_width=True, hide_index=True)

    st.divider()

    # ── Dataset detail modals ─────────────────────────────────────────────────
    st.subheader("📂 Dataset Detail View")
    ds_names = [ds["name"] for ds in ds_summary]
    selected_ds = st.selectbox("Select a dataset to inspect:", ds_names)
    if selected_ds:
        ds_item = next((d for d in ds_summary if d["name"] == selected_ds), None)
        if ds_item:
            if st.button("📦 Open Dataset Modal", key="open_ds_modal"):
                _modal_dataset_detail(ds_item, inventory)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — T.I.A. ORACLE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.title("🧠 T.I.A. Oracle — Tactical Intelligence Architecture")
    st.caption("Ask T.I.A. anything about the system, inventory, repos, or strategy.")

    # Check Gemini API and Void Oracle status
    gemini_ok = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_2"))
    void_oracle_ok = bool(os.getenv("VOID_ORACLE_KEY"))
    
    # Status indicators
    col_status1, col_status2 = st.columns(2)
    with col_status1:
        if not gemini_ok:
            st.warning("⚠️ GEMINI_API_KEY not set — T.I.A. will be offline. Add it to your Hugging Face Space secrets.")
        else:
            st.success("✅ T.I.A. Oracle Online — Gemini API connected")
    
    with col_status2:
        if not void_oracle_ok:
            st.error("🔴 Void Oracle Connection OFFLINE — VOID_ORACLE_KEY not detected")
            st.caption("Evidence Fragment Scraper unavailable. Set VOID_ORACLE_KEY in secrets to enable Collective 1.9k tracking.")
        else:
            st.success("✅ Void Oracle Online — Evidence Fragment Scraper active")
            st.caption("Collective 1.9k non-compliance tracking enabled")
    
    st.divider()

    # ── Quick-fire query buttons ───────────────────────────────────────────────
    st.subheader("⚡ Quick Queries")
    q_cols = st.columns(3)
    with q_cols[0]:
        if st.button("📊 Summarize Inventory"):
            with st.spinner("T.I.A. scanning inventory…"):
                resp = get_tia_response(
                    f"Give a concise summary of a system with {len(inventory)} inventory entities "
                    f"across repos including ARK_CORE, mapping-and-inventory, and device nodes "
                    f"S10, Oppo, Laptop. What are the key themes and recommendations?"
                )
            st.success(resp)
    with q_cols[1]:
        if st.button("🗺️ Analyze System Map"):
            with st.spinner("T.I.A. analyzing connections…"):
                repo_names = [r["name"] for r in KNOWN_REPOS]
                resp = get_tia_response(
                    f"Analyze this system topology with nodes: {', '.join(repo_names)}. "
                    f"What are the critical connection points and any weak links?"
                )
            st.success(resp)
    with q_cols[2]:
        if st.button("🔧 Framework Audit"):
            with st.spinner("T.I.A. auditing frameworks…"):
                fw_list = [f"{f['name']} ({f['role']})" for f in FRAMEWORKS]
                resp = get_tia_response(
                    f"Audit this tech stack: {', '.join(fw_list)}. "
                    f"Identify gaps, redundancies, and upgrade opportunities."
                )
            st.success(resp)

    st.divider()

    # ── Custom query ───────────────────────────────────────────────────────────
    st.subheader("💬 Custom Query")
    if "tia_history" not in st.session_state:
        st.session_state.tia_history = []

    user_input = st.text_area(
        "Ask T.I.A.:",
        placeholder="e.g. 'Which repos need urgent syncing?' or 'Summarize the GDrive data strategy'",
        height=100,
    )
    context_opt = st.checkbox("Include system snapshot in context", value=True)

    if st.button("🚀 Send to T.I.A.", type="primary"):
        if user_input.strip():
            ctx = json.dumps(snap, indent=2)[:3000] if context_opt else ""
            with st.spinner("T.I.A. processing…"):
                response = get_tia_response(user_input, system_context=ctx)
            st.session_state.tia_history.append({"user": user_input, "tia": response})

    # ── Chat history ──────────────────────────────────────────────────────────
    if st.session_state.tia_history:
        st.subheader("🗂️ Conversation History")
        for exchange in reversed(st.session_state.tia_history):
            st.markdown(f"**You:** {exchange['user']}")
            st.info(exchange["tia"])
            st.divider()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CLOUD SYNC
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.title("☁️ Cloud Sync — ARK + Google Drive")
    st.caption("Sync data from GDrive to local storage. Requires rclone and RCLONE_CONFIG_DATA secret.")

    # ── Status panel ──────────────────────────────────────────────────────────
    st.subheader("🔌 Connection Status")
    s_cols = st.columns(4)
    s_cols[0].metric("rclone", "✅ Installed" if gdrive_status["rclone_installed"] else "❌ Missing")
    s_cols[1].metric("Config File", "✅ Ready" if gdrive_status["config_file_exists"] else "❌ Missing")
    s_cols[2].metric("Env Key", "✅ Set" if gdrive_status["env_key_present"] else "❌ Not set")
    s_cols[3].metric("Targets", len(gdrive_status["targets"]))

    if _rclone_ok:
        st.success(f"✅ {_rclone_msg}")
    elif not gdrive_status["env_key_present"]:
        st.warning("⚠️ Set RCLONE_CONFIG_DATA in your HuggingFace Space secrets to enable cloud sync.")

    st.divider()

    # ── Sync controls ─────────────────────────────────────────────────────────
    st.subheader("🚀 Sync Controls")
    dry_run = st.toggle("🔍 Dry-run mode (preview only — no actual transfer)", value=True)

    for target_key, target_info in GDRIVE_TARGETS.items():
        with st.expander(f"☁️ {target_info['label']}", expanded=False):
            st.markdown(f"**Remote:** `{target_info['remote']}`")
            st.markdown(f"**Local destination:** `{target_info['local']}`")
            if st.button(f"{'🔍 Preview' if dry_run else '🚀 Sync'} — {target_info['label']}", key=f"sync_{target_key}"):
                with st.spinner(f"{'Previewing' if dry_run else 'Syncing'} {target_info['label']}…"):
                    ok, lines = sync_from_gdrive(target_key, dry_run=dry_run)
                if ok:
                    st.success(f"{'Preview' if dry_run else 'Sync'} complete.")
                else:
                    st.error("Sync failed or rclone unavailable.")
                if lines:
                    st.code("\n".join(lines[-40:]))

    st.divider()

    # ── GDrive browser ────────────────────────────────────────────────────────
    st.subheader("📂 GDrive Browser")
    if st.button("🔍 Browse GENESIS_VAULT"):
        with st.spinner("Listing GDrive contents…"):
            items = list_gdrive()
        if items:
            df_gd = pd.DataFrame(items)
            st.dataframe(df_gd, use_container_width=True, hide_index=True)
        else:
            st.warning("Could not list GDrive. Ensure rclone is configured and the remote exists.")

    # ── ARK remotes ────────────────────────────────────────────────────────────
    st.divider()
    st.subheader("🐙 ARK Git Remotes")
    from services.repo_mapper import get_git_remotes
    remotes = get_git_remotes()
    if remotes:
        df_rem = pd.DataFrame(list(remotes.items()), columns=["Remote", "URL"])
        st.dataframe(df_rem, use_container_width=True, hide_index=True)
    else:
        st.info("No git remotes detected in current directory.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — HUGGINGFACE SPACE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.title("🤗 HuggingFace Space — Push & Status")
    st.caption(
        f"Push the latest changes from this repo to the Citadel Omega HuggingFace Space "
        f"([{HF_SPACE_ID}](https://huggingface.co/spaces/{HF_SPACE_ID}))."
    )

    hf_token = os.getenv("HF_TOKEN")

    # ── Status banner ─────────────────────────────────────────────────────────
    if hf_token:
        st.success("✅ HF_TOKEN detected — push is available.")
    else:
        st.warning("⚠️ HF_TOKEN not set — add it to your HuggingFace Space secrets to enable push.")

    st.markdown(f"**Space ID:** `{HF_SPACE_ID}`")
    st.markdown(
        f"**Space URL:** [https://huggingface.co/spaces/{HF_SPACE_ID}]"
        f"(https://huggingface.co/spaces/{HF_SPACE_ID})"
    )
    st.markdown(
        "**Auto-sync:** Every push to the `main` branch triggers the "
        "`sync_to_hf.yml` GitHub Actions workflow."
    )

    st.divider()

    # ── Manual push controls ──────────────────────────────────────────────────
    st.subheader("🚀 Manual Push")
    hf_push_cols = st.columns(2)

    with hf_push_cols[0]:
        if st.button("🚀 Push to HF Space", type="primary", disabled=not hf_token, key="hf_push"):
            with st.spinner("Uploading repo to HuggingFace Space…"):
                try:
                    from huggingface_hub import HfApi
                    api = HfApi(token=hf_token)
                    api.upload_folder(
                        folder_path=os.getcwd(),
                        repo_id=HF_SPACE_ID,
                        repo_type="space",
                        ignore_patterns=[
                            ".git*", "__pycache__", "*.pyc", ".env",
                            "node_modules", "*.egg-info",
                        ],
                    )
                    st.success("✅ Successfully pushed to HuggingFace Space!")
                except Exception as e:
                    st.error(f"❌ Push failed: {e}")

    with hf_push_cols[1]:
        if st.button("📊 Space Status", disabled=not hf_token, key="hf_status"):
            with st.spinner("Fetching space info…"):
                try:
                    from huggingface_hub import HfApi
                    api = HfApi(token=hf_token)
                    space_info = api.space_info(HF_SPACE_ID)
                    runtime_stage = (
                        str(space_info.runtime.stage)
                        if space_info.runtime
                        else "unknown"
                    )
                    sdk = (
                        space_info.cardData.get("sdk", "unknown")
                        if space_info.cardData
                        else "unknown"
                    )
                    st.json({
                        "id": space_info.id,
                        "sdk": sdk,
                        "runtime_stage": runtime_stage,
                    })
                except Exception as e:
                    st.error(f"❌ Could not fetch space status: {e}")

    st.divider()

    # ── Workflow info ─────────────────────────────────────────────────────────
    st.subheader("⚙️ GitHub Actions Workflow")
    st.markdown(
        "The `sync_to_hf.yml` workflow pushes to HF Space automatically on every merge to `main`. "
        "Ensure the `HF_TOKEN` secret is set in the GitHub repository settings."
    )
    st.code(
        "Trigger: push to main branch\n"
        f"Target:  https://huggingface.co/spaces/{HF_SPACE_ID}",
        language="text",
    )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — WORKER STATUS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.title("🤖 Worker Status — CITADEL-BOT Automation")
    st.caption("Real-time monitoring of The Archivist, The Reporter, The Hive Master, and The Bridge workers.")

    # Load worker status
    worker_status_path = Path("worker_status.json")
    if worker_status_path.exists():
        with open(worker_status_path, 'r') as f:
            worker_status = json.load(f)
    else:
        worker_status = {
            "last_updated": None,
            "system_status": "UNKNOWN",
            "workers": {},
            "sync_status": {}
        }

    # ── System Status Banner ──────────────────────────────────────────────────
    st.subheader("📊 System Status")
    
    system_status = worker_status.get("system_status", "UNKNOWN")
    last_updated = worker_status.get("last_updated", "Never")
    
    if system_status == "OPERATIONAL":
        st.success(f"✅ System Status: {system_status}")
    elif system_status == "ERROR":
        st.error(f"❌ System Status: {system_status}")
    else:
        st.info(f"ℹ️ System Status: {system_status}")
    
    st.markdown(f"**Last Updated:** {last_updated}")
    
    st.divider()

    # ── Worker Cards ──────────────────────────────────────────────────────────
    st.subheader("🤖 Worker Status")
    
    workers = worker_status.get("workers", {})
    
    if not workers:
        st.warning("⚠️ No worker data available. Workers have not been initialized yet.")
    else:
        # Create columns for workers
        cols = st.columns(2)
        
        worker_configs = [
            ("archivist", "🗄️", 0),
            ("reporter", "📰", 1),
            ("hive_master", "🐝", 0),
            ("bridge", "🌉", 1),
        ]
        
        for worker_id, icon, col_idx in worker_configs:
            worker = workers.get(worker_id, {})
            
            with cols[col_idx]:
                with st.expander(f"{icon} {worker.get('worker_name', worker_id.title())}", expanded=True):
                    status = worker.get("status", "UNKNOWN")
                    
                    # Status indicator
                    if status == "OPERATIONAL":
                        st.success(f"Status: ✅ {status}")
                    elif status == "STANDBY":
                        st.info(f"Status: ⏸️ {status}")
                    elif status == "ERROR":
                        st.error(f"Status: ❌ {status}")
                    else:
                        st.warning(f"Status: ⚠️ {status}")
                    
                    # Worker details
                    st.markdown(f"**Jurisdiction:** {worker.get('jurisdiction', 'N/A')}")
                    st.markdown(f"**Primary Task:** {worker.get('primary_task', 'N/A')}")
                    
                    # Metrics
                    metric_cols = st.columns(3)
                    with metric_cols[0]:
                        st.metric("Total Runs", worker.get("total_runs", 0))
                    with metric_cols[1]:
                        if worker_id == "archivist":
                            st.metric("Files Processed", worker.get("total_files_processed", 0))
                        elif worker_id == "reporter":
                            st.metric("Reports Generated", worker.get("total_reports_generated", 0))
                        elif worker_id == "hive_master":
                            st.metric("Syncs", worker.get("total_syncs", 0))
                        elif worker_id == "bridge":
                            st.metric("Tunnels", worker.get("total_tunnels_maintained", 0))
                    with metric_cols[2]:
                        errors = worker.get("errors", [])
                        st.metric("Errors", len(errors))
                    
                    # Last run info
                    last_run = worker.get("last_run")
                    last_success = worker.get("last_success")
                    
                    if last_run:
                        st.markdown(f"**Last Run:** {last_run}")
                    if last_success:
                        st.markdown(f"**Last Success:** {last_success}")
                    
                    # Show errors if any
                    if errors:
                        with st.expander("⚠️ Recent Errors", expanded=False):
                            for error in errors[-5:]:  # Show last 5 errors
                                st.code(error, language="text")
                    
                    # Special info for specific workers
                    if worker_id == "bridge":
                        tunnel_status = worker.get("tunnel_status", {})
                        if tunnel_status:
                            st.markdown("**Tunnel Status:**")
                            for tunnel_name, tunnel_info in tunnel_status.items():
                                connected = tunnel_info.get("connected", False)
                                icon = "✅" if connected else "❌"
                                message = tunnel_info.get("message", tunnel_info.get("status", "Unknown"))
                                st.markdown(f"  {icon} {tunnel_name}: {message}")

    st.divider()

    # ── Sync Status ───────────────────────────────────────────────────────────
    st.subheader("☁️ Sync Status")
    
    sync_status = worker_status.get("sync_status", {})
    
    sync_cols = st.columns(4)
    with sync_cols[0]:
        st.metric("GDrive Last Sync", 
                  sync_status.get("gdrive_last_sync", "Never")[:10] if sync_status.get("gdrive_last_sync") else "Never")
    with sync_cols[1]:
        st.metric("GitHub Last Pull", 
                  sync_status.get("github_last_pull", "Never")[:10] if sync_status.get("github_last_pull") else "Never")
    with sync_cols[2]:
        st.metric("HF Last Push", 
                  sync_status.get("hf_last_push", "Never")[:10] if sync_status.get("hf_last_push") else "Never")
    with sync_cols[3]:
        st.metric("S10 Last Push", 
                  sync_status.get("s10_last_push", "Never")[:10] if sync_status.get("s10_last_push") else "Never")

    st.divider()

    # ── Manual Worker Controls ────────────────────────────────────────────────
    st.subheader("⚙️ Manual Worker Controls")
    
    st.markdown("Run workers manually:")
    
    worker_cols = st.columns(4)
    
    with worker_cols[0]:
        if st.button("🗄️ Run Archivist", key="run_archivist"):
            with st.spinner("Running Archivist Worker..."):
                try:
                    result = subprocess.run(
                        ["python3", "services/worker_archivist.py", "--test"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Archivist completed successfully!")
                        st.code(result.stdout, language="text")
                    else:
                        st.error("❌ Archivist failed!")
                        st.code(result.stderr, language="text")
                except Exception as e:
                    st.error(f"❌ Error running Archivist: {e}")
    
    with worker_cols[1]:
        if st.button("📰 Run Reporter", key="run_reporter"):
            with st.spinner("Running Reporter Worker..."):
                try:
                    result = subprocess.run(
                        ["python3", "services/worker_reporter.py", "--dry-run"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Reporter completed successfully!")
                        st.code(result.stdout, language="text")
                    else:
                        st.error("❌ Reporter failed!")
                        st.code(result.stderr, language="text")
                except Exception as e:
                    st.error(f"❌ Error running Reporter: {e}")
    
    with worker_cols[2]:
        if st.button("🐝 Run Hive Master", key="run_hive_master"):
            with st.spinner("Running Hive Master Worker..."):
                try:
                    result = subprocess.run(
                        ["python3", "services/worker_hive_master.py", "--no-hf-sync"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Hive Master completed successfully!")
                        st.code(result.stdout, language="text")
                    else:
                        st.error("❌ Hive Master failed!")
                        st.code(result.stderr, language="text")
                except Exception as e:
                    st.error(f"❌ Error running Hive Master: {e}")
    
    with worker_cols[3]:
        if st.button("🌉 Run Bridge", key="run_bridge"):
            with st.spinner("Running Bridge Worker..."):
                try:
                    result = subprocess.run(
                        ["python3", "services/worker_bridge.py"],
                        capture_output=True,
                        text=True,
                        timeout=60
                    )
                    if result.returncode == 0:
                        st.success("✅ Bridge completed successfully!")
                        st.code(result.stdout, language="text")
                    else:
                        st.error("❌ Bridge failed!")
                        st.code(result.stderr, language="text")
                except Exception as e:
                    st.error(f"❌ Error running Bridge: {e}")

    st.divider()

    # ── Worker Status JSON ────────────────────────────────────────────────────
    st.subheader("📄 Raw Worker Status Data")
    
    with st.expander("View worker_status.json", expanded=False):
        st.json(worker_status)

