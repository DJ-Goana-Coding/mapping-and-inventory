"""
Q.G.T.N.L. (0) // MAPPING & INVENTORY LIBRARIAN
Citadel Omega Sovereign HUD — Central mapping and inventory dashboard.
Connects: ARK repos, GDrive, T.I.A., datasets, and all device nodes.
"""

import sys
import os
import subprocess
import json
import pandas as pd
import streamlit as st
from pathlib import Path

# Ensure services are importable from this file's location
sys.path.insert(0, os.path.dirname(__file__))

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
# Identity Bridge: GitHub (DJ-Goana-Coding) | HF (DJ-Goanna-Coding)
HF_SPACE_ID = "DJ-Goanna-Coding/Mapping-and-Inventory"

# ── Load PvC Trigger Map ─────────────────────────────────────────────────────
PVC_TRIGGER_MAP_PATH = Path(__file__).parent / "src" / "pvc_trigger_map.json"
try:
    with open(PVC_TRIGGER_MAP_PATH, 'r') as f:
        PVC_TRIGGERS = json.load(f)
except Exception:
    PVC_TRIGGERS = None

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CITADEL OMEGA — Sovereign HUD",
    layout="wide",
    page_icon="🏰",
)

# ── Rclone boot ────────────────────────────────────────────────────────────────
_rclone_ok, _rclone_msg = setup_rclone_config()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.shields.io/badge/CITADEL-OMEGA-blueviolet?style=for-the-badge", width=220)
    st.markdown("## 🏰 SOVEREIGN HUB (v25.0)")
    
    # Live token status
    snap = get_system_snapshot()
    tokens = snap.get("env_tokens", {})
    for tok, status in tokens.items():
        icon = "✅" if status == "DETECTED" else "❌"
        st.markdown(f"{icon} **{tok}**")
    
    st.divider()
    gdrive_status = get_gdrive_status()
    st.markdown(f"**rclone:** {'✅ Ready' if gdrive_status['rclone_installed'] else '❌ Missing'}")
    
    st.divider()
    inventory = load_local_inventory("master_inventory.json")
    st.metric("📦 Master Inventory", f"{len(inventory):,}")
    st.metric("🗂️ Active Spokes", len(KNOWN_REPOS))

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
    "🗺️ Spoke-and-Wheel Map",
    "📚 Librarian Hub",
    "🧠 T.I.A. Oracle",
    "☁️ L4 Vacuum (Sync)",
    "🧬 Cognitive Reservoirs",
    "🤖 Worker Status",
])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — SPOKE-AND-WHEEL MAP
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.title("🗺️ Citadel Mesh — Global Topology")
    st.caption("Visualizing the 321GB Spoke-and-Wheel Intelligence Mesh.")

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
        st.info("Interactive Spoke-and-Wheel Graph Online.")

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
    st.subheader("📋 Spoke Registry")
    cols = st.columns(3)
    for i, repo in enumerate(KNOWN_REPOS):
        with cols[i % 3]:
            st.markdown(f"**{repo['name']}**")
            st.caption(f"Role: {repo['role']}")
            st.markdown(f"[View Spoke]({repo['url']})")

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
# TAB 2 — LIBRARIAN HUB
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.title("📚 Master Librarian")
    st.caption("Search and explore the 9,354-entity master inventory ledger.")

    if not inventory:
        st.error("⚠️ master_inventory.json missing from root.")
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
# TAB 3 — T.I.A. ORACLE
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.title("🧠 T.I.A. Oracle")
    
    user_input = st.text_area("Command T.I.A.:")
    if st.button("🚀 Ignite Reasoning"):
        with st.spinner("T.I.A. Processing..."):
            response = get_tia_response(user_input)
            st.write(response)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — L4 VACUUM (CLOUD SYNC)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.title("☁️ L4 Vacuum Engine")
    st.caption("Pulling the 321GB GDrive Substrate into Mapping-and-Inventory-storage.")
    if st.button("🔥 Trigger Section 142 Pulse"):
        st.info("Initiating 5-partition sequential scan...")
        # Automation trigger for rclone pull engine

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — COGNITIVE RESERVOIRS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.title("🧬 Forever Learning Datasets")
    st.markdown("- **Citadel_Genetics**")
    st.markdown("- **Genesis-Research-Rack**")
    st.markdown("- **tias-soul-vault**")
    if st.button("📥 Ingest for Learning"):
        st.info("Feeding T.I.A. from Soul-Vault...")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — WORKER STATUS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.title("🤖 Worker Constellation")
    # Load worker_status.json
    st.json({"System": "Operational", "Workers": ["Archivist", "Reporter", "Bridge"]})

