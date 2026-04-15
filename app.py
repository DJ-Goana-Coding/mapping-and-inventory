"""
Q.G.T.N.L. (0) // MAPPING & INVENTORY — SOVEREIGN FACEPLATE
Citadel Omega Sovereign HUD — Chat-first command interface.
Connects: ARK repos, GDrive, T.I.A., datasets, coding agent, and all device nodes.
"""

import sys
import os
import json
import pandas as pd
import streamlit as st
from pathlib import Path
from datetime import datetime, timezone

# Ensure services are importable from this file's location
sys.path.insert(0, os.path.dirname(__file__))

from services.repo_mapper import (
    get_system_snapshot,
    build_connection_graph,
    KNOWN_REPOS,
    FRAMEWORKS,
    get_local_structure,
    get_git_remotes,
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
from services.coding_agent import (
    generate_code,
    review_code,
    explain_code,
    refactor_code,
    debug_code,
    chat as agent_chat,
    generate_appscript_worker,
    generate_workflow,
)
from services.code_executor import execute_python, execute_bash
from services.appscript_worker_factory import (
    get_template_names,
    render_template,
    get_template,
    get_manifest,
)

# ── Configuration ──────────────────────────────────────────────────────────────
HF_SPACE_ID = "DJ-Goanna-Coding/Mapping-and-Inventory"

# ── Load PvC Trigger Map ─────────────────────────────────────────────────────
PVC_TRIGGER_MAP_PATH = Path(__file__).parent / "src" / "pvc_trigger_map.json"
try:
    with open(PVC_TRIGGER_MAP_PATH, "r") as f:
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

# ── Session state initialization ──────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_mode" not in st.session_state:
    st.session_state.agent_mode = "🧠 T.I.A. Oracle"

# ── Helper functions ──────────────────────────────────────────────────────────

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


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏰 CITADEL OMEGA")
    st.caption("Sovereign HUD v26.59")

    # Live token status
    snap = get_system_snapshot()
    tokens = snap.get("env_tokens", {})
    for tok, status in tokens.items():
        icon = "✅" if status == "DETECTED" else "❌"
        st.markdown(f"{icon} **{tok}**")

    st.divider()
    gdrive_status = get_gdrive_status()
    st.markdown(
        f"**rclone:** {'✅ Ready' if gdrive_status['rclone_installed'] else '❌ Missing'}"
    )

    st.divider()
    inventory = load_local_inventory("master_inventory.json")
    st.metric("📦 Master Inventory", f"{len(inventory):,}")
    st.metric("🗂️ Active Spokes", len(KNOWN_REPOS))

    st.divider()
    st.markdown("### 🤖 Agent Mode")
    st.session_state.agent_mode = st.radio(
        "Select agent:",
        [
            "🧠 T.I.A. Oracle",
            "💻 Coding Agent",
            "📜 Apps Script Factory",
        ],
        label_visibility="collapsed",
    )

    if st.button("🗑️ Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()


# ── Tabs ───────────────────────────────────────────────────────────────────────
tabs = st.tabs(
    [
        "💬 Command Console",
        "🗺️ Mesh Map",
        "📚 Librarian",
        "📜 Apps Script Workers",
        "☁️ Cloud Sync",
        "🤖 Worker Status",
    ]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — COMMAND CONSOLE (Chat Interface)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    st.title("💬 Citadel Command Console")
    mode = st.session_state.agent_mode
    st.caption(f"Active Agent: **{mode}** — Type your instructions below.")

    # Display chat history
    for msg in st.session_state.chat_history:
        role = msg["role"]
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(msg["content"])

    # Chat input
    user_input = st.chat_input("Send a command to the Citadel…")
    if user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Process based on active agent
        with st.chat_message("assistant"):
            with st.spinner(f"{mode} processing…"):
                if mode == "🧠 T.I.A. Oracle":
                    response = get_tia_response(user_input)
                elif mode == "💻 Coding Agent":
                    response = agent_chat(
                        user_input,
                        history=st.session_state.chat_history[:-1],
                    )
                elif mode == "📜 Apps Script Factory":
                    response = generate_appscript_worker(
                        user_input,
                        worker_name="CitadelWorker",
                    )
                    response = response.get("code", str(response))
                else:
                    response = get_tia_response(user_input)

                st.markdown(response)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )

    # Quick-action buttons for Coding Agent
    if mode == "💻 Coding Agent":
        st.divider()
        st.subheader("⚡ Quick Actions")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if st.button("📝 Generate Code"):
                st.session_state["show_generate"] = True
        with col2:
            if st.button("🔍 Review Code"):
                st.session_state["show_review"] = True
        with col3:
            if st.button("🐛 Debug Code"):
                st.session_state["show_debug"] = True
        with col4:
            if st.button("🔧 Refactor Code"):
                st.session_state["show_refactor"] = True

        if st.session_state.get("show_generate"):
            with st.expander("📝 Code Generation", expanded=True):
                gen_lang = st.selectbox(
                    "Language",
                    ["python", "javascript", "bash", "apps_script", "html", "sql"],
                    key="gen_lang",
                )
                gen_instruction = st.text_area(
                    "Describe what you want to build:", key="gen_instr"
                )
                gen_context = st.text_area(
                    "Additional context (optional):", key="gen_ctx"
                )
                if st.button("🚀 Generate", key="gen_btn") and gen_instruction:
                    with st.spinner("Coding Agent generating…"):
                        result = generate_code(gen_instruction, gen_lang, gen_context)
                        st.markdown(result)

        if st.session_state.get("show_review"):
            with st.expander("🔍 Code Review", expanded=True):
                rev_lang = st.selectbox(
                    "Language",
                    ["python", "javascript", "bash", "apps_script"],
                    key="rev_lang",
                )
                rev_code = st.text_area("Paste code to review:", key="rev_code", height=200)
                if st.button("🔍 Review", key="rev_btn") and rev_code:
                    with st.spinner("Reviewing…"):
                        result = review_code(rev_code, rev_lang)
                        st.markdown(result)

        if st.session_state.get("show_debug"):
            with st.expander("🐛 Debug", expanded=True):
                dbg_lang = st.selectbox(
                    "Language", ["python", "javascript", "bash"], key="dbg_lang"
                )
                dbg_code = st.text_area("Code with bug:", key="dbg_code", height=150)
                dbg_error = st.text_area("Error message:", key="dbg_err", height=100)
                if st.button("🐛 Debug", key="dbg_btn") and dbg_code:
                    with st.spinner("Debugging…"):
                        result = debug_code(dbg_code, dbg_error, dbg_lang)
                        st.markdown(result)

        if st.session_state.get("show_refactor"):
            with st.expander("🔧 Refactor", expanded=True):
                ref_lang = st.selectbox(
                    "Language", ["python", "javascript", "bash"], key="ref_lang"
                )
                ref_code = st.text_area("Code to refactor:", key="ref_code", height=200)
                ref_goals = st.text_input(
                    "Refactoring goals:", key="ref_goals"
                )
                if st.button("🔧 Refactor", key="ref_btn") and ref_code:
                    with st.spinner("Refactoring…"):
                        result = refactor_code(ref_code, ref_lang, ref_goals)
                        st.markdown(result)

    # Code Execution Panel
    st.divider()
    st.subheader("▶️ Code Execution Sandbox")
    exec_tab1, exec_tab2 = st.tabs(["🐍 Python", "🖥️ Bash"])

    with exec_tab1:
        py_code = st.text_area(
            "Python code:",
            value='print("Hello from the Citadel! 🏰")',
            height=150,
            key="py_exec",
        )
        if st.button("▶️ Run Python", key="run_py"):
            with st.spinner("Executing…"):
                result = execute_python(py_code)
                if result["success"]:
                    st.success("✅ Execution successful")
                    if result["stdout"]:
                        st.code(result["stdout"], language="text")
                else:
                    st.error("❌ Execution failed")
                    if result["stderr"]:
                        st.code(result["stderr"], language="text")
                    if result["timed_out"]:
                        st.warning("⏰ Code timed out")

    with exec_tab2:
        bash_cmd = st.text_area(
            "Bash command:",
            value="echo 'Citadel systems online' && python3 --version",
            height=100,
            key="bash_exec",
        )
        if st.button("▶️ Run Bash", key="run_bash"):
            with st.spinner("Executing…"):
                result = execute_bash(bash_cmd)
                if result["success"]:
                    st.success("✅ Execution successful")
                    if result["stdout"]:
                        st.code(result["stdout"], language="text")
                else:
                    st.error("❌ Execution failed")
                    if result["stderr"]:
                        st.code(result["stderr"], language="text")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — MESH MAP
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    st.title("🗺️ Citadel Mesh — Global Topology")
    st.caption("Visualizing the 321GB Spoke-and-Wheel Intelligence Mesh.")

    nodes, edges = build_connection_graph()

    try:
        import plotly.graph_objects as go
        import networkx as nx

        G = nx.Graph()
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
        node_colors = [
            _TYPE_COLOR.get(G.nodes[n].get("type", ""), "#78909c") for n in G.nodes()
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=edge_x,
                y=edge_y,
                mode="lines",
                line=dict(width=1.5, color="#888"),
                hoverinfo="none",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=node_x,
                y=node_y,
                mode="markers+text",
                marker=dict(
                    size=28, color=node_colors, line=dict(width=2, color="white")
                ),
                text=list(G.nodes()),
                textposition="top center",
                hovertext=node_text,
                hoverinfo="text",
            )
        )
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

        legend_parts = [f"{_repo_icon(t)} {t}" for t in _TYPE_ICON]
        st.markdown("**Legend:**  " + "  ".join(legend_parts))

    except ImportError:
        st.warning("Install `plotly` and `networkx` for the visual graph.")
        st.json({"nodes": [n["id"] for n in nodes], "edges": [list(e) for e in edges]})

    st.divider()

    # Spoke registry
    st.subheader("📋 Spoke Registry")
    cols = st.columns(3)
    for i, repo in enumerate(KNOWN_REPOS):
        with cols[i % 3]:
            st.markdown(f"**{repo['name']}**")
            st.caption(f"Role: {repo['role']}")
            if repo["url"] != "local":
                st.markdown(f"[View Spoke]({repo['url']})")

    st.divider()

    # Frameworks
    st.subheader("🔧 Frameworks & Tech Stack")
    df_fw = pd.DataFrame(FRAMEWORKS)
    df_fw["used_in"] = df_fw["used_in"].apply(lambda x: ", ".join(x))
    st.dataframe(df_fw, use_container_width=True, hide_index=True)

    st.divider()

    # Local scaffold
    st.subheader("🗂️ Local Repo Scaffold")
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

    # Git remotes
    remotes = get_git_remotes()
    if remotes:
        st.subheader("🔗 Git Remotes")
        df_r = pd.DataFrame(list(remotes.items()), columns=["Remote", "URL"])
        st.dataframe(df_r, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — LIBRARIAN HUB
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    st.title("📚 Master Librarian")
    st.caption("Search and explore the master inventory ledger.")

    if not inventory:
        st.error("⚠️ master_inventory.json missing from root.")
    else:
        stats = get_inventory_stats(inventory)

        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Total Entities", stats.get("total", 0))
        top_ext = list(stats.get("top_extensions", {}).items())
        c2.metric(
            "📄 Top File Type",
            f".{top_ext[0][0]} ({top_ext[0][1]})" if top_ext else "—",
        )
        top_dir = list(stats.get("top_directories", {}).items())
        c3.metric(
            "📂 Top Directory",
            f"{top_dir[0][0]} ({top_dir[0][1]})" if top_dir else "—",
        )

        st.divider()

        col_s, col_lim = st.columns([3, 1])
        with col_s:
            search_q = st.text_input(
                "🔍 Search inventory",
                placeholder="e.g. trader, lore, ark_engine",
            )
        with col_lim:
            result_limit = st.selectbox("Max results", [50, 100, 250, 500], index=1)

        if search_q:
            results = search_inventory(
                inventory, search_q, limit=result_limit, pvc_triggers=PVC_TRIGGERS
            )
            pvc_flagged = any(item.get("_pvc_flagged", False) for item in results)
            st.write(f"Found **{len(results)}** matches for `{search_q}`")
            if pvc_flagged:
                st.warning(
                    "🟠 **ORANGE STAR VISION ACTIVE** — PvC compliance triggers detected."
                )
            if results:
                st.dataframe(
                    pd.DataFrame(results), use_container_width=True, hide_index=True
                )
        else:
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
                    fig_ext.update_layout(
                        paper_bgcolor="#0e1117", font=dict(color="white")
                    )
                    st.plotly_chart(fig_ext, use_container_width=True)
            except ImportError:
                st.bar_chart(stats.get("top_extensions", {}))

            st.subheader("📂 Top Directories")
            dir_data = stats.get("top_directories", {})
            if dir_data:
                try:
                    import plotly.express as px

                    fig_dir = px.bar(
                        x=list(dir_data.keys()),
                        y=list(dir_data.values()),
                        labels={"x": "Directory", "y": "File Count"},
                        color=list(dir_data.values()),
                        color_continuous_scale="Viridis",
                    )
                    fig_dir.update_layout(
                        paper_bgcolor="#0e1117", font=dict(color="white")
                    )
                    st.plotly_chart(fig_dir, use_container_width=True)
                except Exception:
                    st.bar_chart(dir_data)

            st.subheader("🗃️ First 50 Entries")
            st.dataframe(
                pd.DataFrame(inventory[:50]),
                use_container_width=True,
                hide_index=True,
            )

        # Neuron data
        st.divider()
        st.subheader("🧬 Forever Learning Neurons")
        neurons = load_neuron_data()
        if neurons:
            st.write(f"**{len(neurons)}** neuron files indexed.")
            st.dataframe(
                pd.DataFrame(neurons), use_container_width=True, hide_index=True
            )
        else:
            st.info("No neuron files found in Forever_Learning/.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — APPS SCRIPT WORKERS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    st.title("📜 Apps Script Worker Factory")
    st.caption("Generate and deploy Google Apps Script workers.")

    factory_tab1, factory_tab2 = st.tabs(["📋 Templates", "✨ AI Generator"])

    with factory_tab1:
        st.subheader("Pre-Built Worker Templates")
        template_names = get_template_names()

        for tname in template_names:
            tmpl = get_template(tname)
            if tmpl:
                with st.expander(f"📄 {tmpl['name']} — {tmpl['description']}"):
                    st.markdown(f"**Triggers:** {', '.join(tmpl['triggers'])}")
                    if st.button(f"Generate {tmpl['name']}", key=f"tmpl_{tname}"):
                        code = render_template(tname)
                        manifest = get_manifest()
                        st.subheader("Worker Code (.gs)")
                        st.code(code, language="javascript")
                        st.subheader("Manifest (appsscript.json)")
                        st.code(manifest, language="json")
                        st.success("✅ Worker generated! Copy both files to your Apps Script project.")

    with factory_tab2:
        st.subheader("✨ AI-Powered Worker Generator")
        st.markdown(
            "Describe what you need and the Coding Agent will generate a complete Apps Script worker."
        )

        worker_name = st.text_input(
            "Worker name:",
            value="CitadelWorker",
            key="ai_worker_name",
        )
        worker_desc = st.text_area(
            "Describe what this worker should do:",
            placeholder="e.g. Monitor a Google Sheet for new rows and send email notifications…",
            key="ai_worker_desc",
            height=100,
        )
        worker_triggers = st.multiselect(
            "Triggers:",
            ["onOpen", "onEdit", "onChange", "time-based", "web app", "form submit"],
            key="ai_worker_triggers",
        )

        if st.button("🚀 Generate Worker", key="ai_gen_worker") and worker_desc:
            with st.spinner("Coding Agent generating worker…"):
                result = generate_appscript_worker(
                    worker_desc,
                    worker_name=worker_name,
                    triggers=worker_triggers,
                )
                st.markdown(result["code"])
                st.caption(f"Generated: {result['generated_at']}")

    st.divider()
    st.subheader("🔧 GitHub Actions Workflow Generator")
    wf_name = st.text_input("Workflow name:", value="citadel_automation", key="wf_name")
    wf_desc = st.text_area(
        "Describe the workflow:",
        placeholder="e.g. Run tests on push, deploy to HuggingFace on release…",
        key="wf_desc",
        height=80,
    )
    if st.button("⚙️ Generate Workflow", key="gen_wf") and wf_desc:
        with st.spinner("Generating workflow…"):
            result = generate_workflow(wf_desc, wf_name)
            st.markdown(result)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — CLOUD SYNC
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.title("☁️ L4 Vacuum Engine")
    st.caption("Pulling the 321GB GDrive Substrate into Mapping-and-Inventory-storage.")

    st.subheader("GDrive Sync Targets")
    for key, target in GDRIVE_TARGETS.items():
        with st.expander(f"📁 {target['label']}"):
            st.markdown(f"**Remote:** `{target['remote']}`")
            st.markdown(f"**Local:** `{target['local']}`")
            col_dry, col_live = st.columns(2)
            with col_dry:
                if st.button(f"🔍 Dry Run", key=f"dry_{key}"):
                    with st.spinner("Scanning…"):
                        ok, lines = sync_from_gdrive(key, dry_run=True)
                        if ok:
                            st.success("Dry run complete")
                        else:
                            st.error("Dry run failed")
                        st.code("\n".join(lines), language="text")
            with col_live:
                if st.button(f"🔥 Live Sync", key=f"live_{key}"):
                    with st.spinner("Syncing…"):
                        ok, lines = sync_from_gdrive(key, dry_run=False)
                        if ok:
                            st.success("Sync complete")
                        else:
                            st.error("Sync failed")
                        st.code("\n".join(lines), language="text")

    st.divider()
    st.subheader("📊 GDrive Browser")
    browse_path = st.text_input(
        "Remote path:", value="gdrive:GENESIS_VAULT", key="gdrive_browse"
    )
    if st.button("📂 Browse", key="browse_btn"):
        with st.spinner("Listing…"):
            items = list_gdrive(browse_path)
            if items:
                st.dataframe(
                    pd.DataFrame(items), use_container_width=True, hide_index=True
                )
            else:
                st.info("No items found or rclone not configured.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — WORKER STATUS
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    st.title("🤖 Worker Constellation")

    worker_path = Path("worker_status.json")
    if worker_path.exists():
        with open(worker_path) as f:
            worker_data = json.load(f)
        st.json(worker_data)
    else:
        st.json(
            {
                "System": "Operational",
                "Workers": ["Archivist", "Reporter", "Bridge", "Coding Agent"],
                "Timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    st.divider()
    st.subheader("📊 System Snapshot")
    snap_data = get_system_snapshot()
    with st.expander("🔧 Environment Tokens"):
        for tok, status in snap_data.get("env_tokens", {}).items():
            icon = "✅" if status == "DETECTED" else "❌"
            st.markdown(f"{icon} **{tok}**: {status}")

    with st.expander("📂 Repository Structure"):
        local_struct = snap_data.get("local_structure", {})
        if local_struct:
            top_dirs = sorted(local_struct.items(), key=lambda x: x[1], reverse=True)[
                :20
            ]
            st.dataframe(
                pd.DataFrame(top_dirs, columns=["Directory", "Files"]),
                use_container_width=True,
                hide_index=True,
            )

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption(
    "🏰 Citadel Omega v26.59.OMNI | "
    f"🤖 Agent: {st.session_state.agent_mode} | "
    "🙏 Thankyou Spirit, Thankyou Angels, Thankyou Ancestors"
)

