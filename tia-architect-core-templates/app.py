"""
🧠 TIA-ARCHITECT-CORE (v25.0.OMNI++)
T.I.A. - The Intelligence Architect
Central Reasoning Hub for Q.G.T.N.L. Citadel Mesh

Purpose: RAG-powered intelligence synthesis, model management, and worker orchestration
"""

import os
import sys
import json
import streamlit as st
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Configure page
st.set_page_config(
    page_title="TIA-ARCHITECT-CORE",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# IDENTITY & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

IDENTITY = {
    "name": "T.I.A.",
    "full_name": "The Intelligence Architect",
    "version": "25.0.OMNI++",
    "role": "Central Reasoning Hub",
    "github": "DJ-Goana-Coding",
    "huggingface": "DJ-Goanna-Coding"
}

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR - SYSTEM STATUS
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.image("https://img.shields.io/badge/T.I.A.-ARCHITECT-blueviolet?style=for-the-badge", width=220)
    st.markdown(f"## 🧠 {IDENTITY['full_name']}")
    st.caption(f"Version {IDENTITY['version']}")
    
    st.divider()
    
    # System Status
    st.markdown("### 📊 System Status")
    
    # Check for environment variables
    env_status = {
        "HF_TOKEN": os.getenv("HF_TOKEN") is not None,
        "GITHUB_TOKEN": os.getenv("GITHUB_TOKEN") is not None,
        "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY") is not None,
    }
    
    for key, status in env_status.items():
        icon = "✅" if status else "⚠️"
        st.markdown(f"{icon} **{key}**")
    
    st.divider()
    
    # Quick Stats
    st.markdown("### 📈 Quick Stats")
    
    # Check for data directories
    data_dir = Path("data")
    models_dir = data_dir / "models"
    workers_dir = data_dir / "workers"
    
    models_count = len(list(models_dir.glob("*"))) if models_dir.exists() else 0
    workers_count = len(list(workers_dir.glob("*.py"))) if workers_dir.exists() else 0
    
    st.metric("🤖 Models", models_count)
    st.metric("⚙️ Workers", workers_count)
    st.metric("🔗 Connections", len(env_status))

# ═══════════════════════════════════════════════════════════════════
# MAIN DASHBOARD
# ═══════════════════════════════════════════════════════════════════

st.title("🧠 TIA-ARCHITECT-CORE")
st.markdown(f"**{IDENTITY['full_name']}** — Central Reasoning Hub")

# Create tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Dashboard",
    "🤖 Models",
    "⚙️ Workers",
    "📚 Knowledge Base",
    "🔧 Tools"
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1: DASHBOARD
# ═══════════════════════════════════════════════════════════════════

with tab1:
    st.header("Welcome to T.I.A. Central")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Purpose")
        st.markdown("""
        - **RAG Intelligence** - Vector search & synthesis
        - **Model Management** - Deploy & monitor AI models
        - **Worker Orchestration** - Coordinate automation workers
        - **Knowledge Mesh** - Connect all Citadel nodes
        """)
    
    with col2:
        st.markdown("### 🌐 Connections")
        st.markdown("""
        - **GitHub** - DJ-Goana-Coding (single N)
        - **HuggingFace** - DJ-Goanna-Coding (double N)
        - **Mapping Hub** - Inventory & artifacts
        - **Districts** - D01-D12 data nodes
        """)
    
    with col3:
        st.markdown("### 📡 Status")
        st.success("✅ Core Systems Online")
        st.info(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.info(f"🔢 Python {sys.version.split()[0]}")

# ═══════════════════════════════════════════════════════════════════
# TAB 2: MODELS REGISTRY
# ═══════════════════════════════════════════════════════════════════

with tab2:
    st.header("🤖 AI Models Registry")
    
    # Check for models manifest
    models_manifest_path = Path("data/models/models_manifest.json")
    
    if models_manifest_path.exists():
        with open(models_manifest_path, 'r') as f:
            models_manifest = json.load(f)
        
        st.success(f"✅ Models Registry Loaded - {models_manifest.get('total_models', 0)} models")
        
        # Display categories
        categories = models_manifest.get("categories", {})
        
        if categories:
            for category, data in categories.items():
                with st.expander(f"📂 {category} ({data.get('count', 0)} models)"):
                    models = data.get("models", [])
                    if models:
                        for model in models:
                            st.markdown(f"- **{model.get('name', 'Unknown')}**")
                            st.caption(model.get('description', ''))
                    else:
                        st.info("No models in this category yet")
        else:
            st.info("Models registry is empty. Use the deployment tools to add models.")
    else:
        st.warning("⚠️ Models manifest not found")
        st.info("Run the model downloader to populate the registry")
    
    st.divider()
    
    # Model Downloader Section
    st.subheader("📥 Download Models")
    
    with st.expander("🔮 Frontier Models Downloader (2026)"):
        st.markdown("""
        Download cutting-edge AI models discovered via web reconnaissance:
        - **Gemma 4** (2B, 4B) - Multimodal, edge-ready
        - **Qwen 3.5** (7B, 14B) - Multilingual code specialist
        - **DeepSeek V4** - Reasoning & code expert
        - **Phi-4** - Microsoft's compact powerhouse
        - **Ministral 8B** - Mistral's efficient model
        """)
        
        if st.button("🚀 Launch Downloader"):
            st.info("Downloader script available in `scripts/download_frontier_models_2026.py`")
            st.code("python scripts/download_frontier_models_2026.py", language="bash")

# ═══════════════════════════════════════════════════════════════════
# TAB 3: WORKERS CONSTELLATION
# ═══════════════════════════════════════════════════════════════════

with tab3:
    st.header("⚙️ Workers Constellation")
    
    st.markdown("""
    Worker constellation enables automated task execution across the Citadel Mesh.
    """)
    
    # Check for workers manifest
    workers_manifest_path = Path("data/workers/workers_manifest.json")
    
    if workers_manifest_path.exists():
        with open(workers_manifest_path, 'r') as f:
            workers_manifest = json.load(f)
        
        st.success(f"✅ Workers Registry Loaded - {workers_manifest.get('total_workers', 0)} workers")
        
        # Display worker categories
        categories = workers_manifest.get("categories", {})
        
        for category, data in categories.items():
            with st.expander(f"🔧 {category} ({data.get('count', 0)} workers)"):
                workers = data.get("workers", [])
                if workers:
                    for worker in workers:
                        st.markdown(f"**{worker.get('name', 'Unknown')}**")
                        st.caption(worker.get('description', ''))
                else:
                    st.info("No workers in this category yet")
    else:
        st.warning("⚠️ Workers manifest not found")
    
    st.divider()
    
    # Apps Script Integration
    st.subheader("📱 Apps Script Workers")
    
    with st.expander("🛠️ Apps Script Toolbox"):
        st.markdown("""
        Bridge between CITADEL workers and Google Sheets for automated reporting.
        
        **Features:**
        - Identity Strike Reports (Section 44 Audit)
        - Full Archive Audits (MD5 hashing, file inventory)
        - Worker Status Dashboards
        
        **Available in:** `workers/apps_script_toolbox.py`
        """)

# ═══════════════════════════════════════════════════════════════════
# TAB 4: KNOWLEDGE BASE (RAG)
# ═══════════════════════════════════════════════════════════════════

with tab4:
    st.header("📚 Knowledge Base & RAG")
    
    st.info("🔮 RAG (Retrieval-Augmented Generation) system coming soon")
    
    st.markdown("""
    The Knowledge Base will provide:
    - **Vector Search** - Semantic search across all Citadel documents
    - **Intelligence Synthesis** - Connect related information
    - **Context Retrieval** - Pull relevant data for queries
    - **Memory Mesh** - Persistent knowledge graph
    """)
    
    # RAG status
    rag_dir = Path("rag_store")
    if rag_dir.exists():
        st.success("✅ RAG store detected")
        rag_files = list(rag_dir.glob("*"))
        st.metric("📄 RAG Files", len(rag_files))
    else:
        st.warning("⚠️ RAG store not initialized")

# ═══════════════════════════════════════════════════════════════════
# TAB 5: TOOLS & UTILITIES
# ═══════════════════════════════════════════════════════════════════

with tab5:
    st.header("🔧 Tools & Utilities")
    
    # System Information
    with st.expander("💻 System Information"):
        st.markdown(f"""
        - **Python Version:** {sys.version}
        - **Platform:** {sys.platform}
        - **Working Directory:** {os.getcwd()}
        """)
    
    # Environment Variables
    with st.expander("🔐 Environment Variables"):
        env_vars = ["HF_TOKEN", "GITHUB_TOKEN", "GOOGLE_API_KEY", "SPACE_ID"]
        for var in env_vars:
            value = os.getenv(var)
            if value:
                st.success(f"✅ {var} - Configured")
            else:
                st.warning(f"⚠️ {var} - Not set")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh Data"):
            st.rerun()
        
        if st.button("📊 Generate Report"):
            st.info("Report generation available via workers")
    
    with col2:
        if st.button("🧹 Clear Cache"):
            st.cache_data.clear()
            st.success("Cache cleared")
        
        if st.button("💾 Export Config"):
            config = {
                "identity": IDENTITY,
                "timestamp": datetime.now().isoformat(),
                "env_status": env_status
            }
            st.download_button(
                "⬇️ Download Config",
                data=json.dumps(config, indent=2),
                file_name="tia_config.json",
                mime="application/json"
            )

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.divider()
st.caption(f"🧠 {IDENTITY['full_name']} v{IDENTITY['version']} | GitHub: {IDENTITY['github']} | HF: {IDENTITY['huggingface']}")
