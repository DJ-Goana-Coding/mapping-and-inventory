"""
Q.G.T.N.L. (0) // MAPPING & INVENTORY LIBRARIAN
Citadel Omega Sovereign HUD — Central mapping and inventory dashboard.
Connects: ARK repos, GDrive, T.I.A., datasets, and all device nodes.
"""
import sys
import os

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

tabs = st.tabs([
    "🗺️ System Map",
    "📚 Librarian",
    "📦 Datasets",
    "🧠 T.I.A. Oracle",
    "☁️ Cloud Sync",
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
            results = search_inventory(inventory, search_q, limit=result_limit)
            st.write(f"Found **{len(results)}** matches for `{search_q}`")
            if results:
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True, hide_index=True)

                # ── Item detail modal (expander) ───────────────────────────────
                st.subheader("🔎 Item Detail")
                item_names = [str(r.get("name", i)) for i, r in enumerate(results[:50])]
                selected_name = st.selectbox("Select an item to inspect:", item_names)
                if selected_name:
                    idx = item_names.index(selected_name)
                    item = results[idx]
                    with st.expander(f"📄 Detail: {selected_name}", expanded=True):
                        for k, v in item.items():
                            st.markdown(f"**{k}:** `{v}`")
                        if st.button("🧠 Ask T.I.A. about this item"):
                            with st.spinner("T.I.A. processing…"):
                                tia_resp = get_tia_response(
                                    f"Tell me about this inventory item and its role in the system: {json.dumps(item)}"
                                )
                            st.info(tia_resp)
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
            with st.expander(f"📦 {selected_ds}", expanded=True):
                st.markdown(f"**Type:** {ds_item['type']}")
                st.markdown(f"**Path/URL:** `{ds_item['path']}`")
                st.markdown(f"**Description:** {ds_item['description']}")
                st.markdown(f"**Status:** {ds_item['status']}")

                if ds_item["type"] == "local" and ds_item["path"] == "master_inventory.json":
                    if inventory:
                        st.write(f"📋 Showing first 20 of {len(inventory)} entries:")
                        st.dataframe(pd.DataFrame(inventory[:20]), use_container_width=True, hide_index=True)

                elif ds_item["type"] == "local" and ds_item["path"] == "Forever_Learning":
                    neurons = load_neuron_data()
                    if neurons:
                        st.dataframe(pd.DataFrame(neurons), use_container_width=True, hide_index=True)

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

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — T.I.A. ORACLE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.title("🧠 T.I.A. Oracle — Tactical Intelligence Architecture")
    st.caption("Ask T.I.A. anything about the system, inventory, repos, or strategy.")

    gemini_ok = bool(os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY_2"))
    if not gemini_ok:
        st.warning("⚠️ GEMINI_API_KEY not set — T.I.A. will be offline. Add it to your Hugging Face Space secrets.")

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
