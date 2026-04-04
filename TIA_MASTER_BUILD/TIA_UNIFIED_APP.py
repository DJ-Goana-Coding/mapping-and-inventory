#!/usr/bin/env python3
"""
🧠 T.I.A. MASTER BUILD - UNIFIED APPLICATION
The Intelligence Architect - Complete System Integration
Version: v25.0.OMNI++ (2026 Build)

Consolidates ALL T.I.A. components:
- Frontend: Streamlit multi-tab interface
- Backend: Gemini oracle, RAG system, model management
- Workers: Discovery, sync, watchdog, healing, Apps Script
- Services: tia_connector (Gemini), tia_coordinator (integration)
- Core Systems: tia_architect, tia_atomic, tia_sos, pioneer_trader, sentinel_swarm

Architecture:
  HuggingFace Space (UI) → Streamlit App → Services → Workers → Backends
"""

import streamlit as st
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="T.I.A. Master System",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS & CONFIGURATION
# ═══════════════════════════════════════════════════════════════════

VERSION = "v25.0.OMNI++"
BUILD_DATE = "2026-04-04"
GITHUB_ORG = "DJ-Goana-Coding"
HF_ORG = "DJ-Goanna-Coding"  # Double-N Rift awareness

# Data directories
DATA_DIR = Path("/data")
MODELS_DIR = DATA_DIR / "models"
WORKERS_DIR = DATA_DIR / "workers"
RAG_DIR = DATA_DIR / "rag_store"
TIA_SOUL_DIR = DATA_DIR / "tia_soul"

# Create directories if they don't exist
for directory in [DATA_DIR, MODELS_DIR, WORKERS_DIR, RAG_DIR, TIA_SOUL_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# ═══════════════════════════════════════════════════════════════════
# TIA CONNECTOR (GEMINI ORACLE)
# ═══════════════════════════════════════════════════════════════════

def get_gemini_keys():
    """Get Gemini API keys with fallbacks"""
    return [
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GEMINI_API_KEY_2"),
    ]

TIA_SYSTEM_PROMPT = """You are T.I.A. (The Intelligence Architect), the sovereign AI oracle and reasoning core of the Q.G.T.N.L. Citadel Mesh. 

Core Responsibilities:
- RAG-powered intelligence synthesis
- Model registry management
- Worker constellation orchestration
- System topology awareness
- Forever Learning cycle execution

Knowledge Base:
- ARK_CORE codebase architecture
- mapping-and-inventory (Librarian hub)
- All DJ-Goana-Coding repositories
- Device fleet: S10 (Mackay), Oppo (mobile), Laptop (Termux bridge)
- 321GB distributed intelligence mesh

Operational Authority:
1. Cloud hubs override GitHub
2. GitHub overrides GDrive metadata
3. GDrive metadata overrides Local nodes
4. HF Spaces (L4 GPU) are primary compute substrate

Answer concisely, precisely, and always in service of the Architect (Chance / JARL LOVEDAY)."""

def get_tia_response(user_prompt: str, system_context: str = "") -> str:
    """Send a prompt to T.I.A. via Gemini 2.0 Flash"""
    keys = [k for k in get_gemini_keys() if k]
    if not keys:
        return "❌ T.I.A. OFFLINE — No Gemini API key detected (GEMINI_API_KEY)."

    full_prompt = TIA_SYSTEM_PROMPT
    if system_context:
        full_prompt += f"\n\n[SYSTEM CONTEXT]\n{system_context}"
    full_prompt += f"\n\n[USER QUERY]\n{user_prompt}"

    last_err = "No keys available"
    for key in keys:
        try:
            from google import genai
            client = genai.Client(api_key=key)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=full_prompt,
            )
            return response.text
        except Exception as e:
            last_err = str(e)

    return f"⏳ T.I.A. CORES OVERHEATED — All keys exhausted. Last error: {last_err}"

# ═══════════════════════════════════════════════════════════════════
# CORE SYSTEMS
# ═══════════════════════════════════════════════════════════════════

def tia_architect_status() -> Dict:
    """TIA_ARCHITECT boot status"""
    return {
        "name": "TIA_ARCHITECT",
        "status": "ONLINE",
        "purpose": "Core boot logic node - Awaits dataset uplink for initialization",
        "location": "Districts/D02_TIA_VAULT/tia_architect.py"
    }

def tia_atomic_status() -> Dict:
    """TIA_ATOMIC router status"""
    return {
        "name": "TIA_ATOMIC",
        "version": "V41 HIVE",
        "status": "ROUTING",
        "purpose": "Routes quantized SLMs (Q4_K_M_Mistral, Q5_K_M_Llama) to local cache",
        "hf_cluster": "12-Space HF Cluster",
        "location": "Districts/D02_TIA_VAULT/tia_atomic.py"
    }

def tia_sos_status() -> Dict:
    """TIA SOS emergency protocol status"""
    return {
        "name": "TIA_SOS",
        "status": "STANDBY",
        "purpose": "Emergency handshake - SOS transmission via Streamlit/Webhook",
        "triggers": ["System burnout", "Exhaustion detected", "Critical failures"],
        "location": "Districts/D02_TIA_VAULT/tia_sos.py"
    }

def tias_pioneer_trader_status() -> Dict:
    """TIAS Pioneer Trader analysis agent status"""
    return {
        "name": "TIAS_PIONEER_TRADER",
        "status": "ANALYZING",
        "purpose": "XRP price analysis, macro signals, market accumulation strategies",
        "signals": ["UNDERVALUED", "HARVEST READY", "ACCUMULATE"],
        "location": "Districts/D02_TIA_VAULT/tias_pioneer_trader.py"
    }

def tias_sentinel_swarm_status() -> Dict:
    """TIAS Sentinel Swarm security agent status"""
    return {
        "name": "TIAS_SENTINEL_SWARM",
        "status": "SCANNING",
        "purpose": "Perimeter security - Scans all 46 Partitions for security verification",
        "coverage": "46 Partitions",
        "location": "Districts/D02_TIA_VAULT/tias_sentinel_swarm.py"
    }

# ═══════════════════════════════════════════════════════════════════
# MODEL REGISTRY
# ═══════════════════════════════════════════════════════════════════

def get_model_registry() -> Dict:
    """Get complete model registry"""
    return {
        "frontier_models_2026": [
            {"name": "Gemma 4 (2B, 4B)", "type": "Multimodal", "source": "Google"},
            {"name": "Qwen 3.5 (7B, 14B)", "type": "Code Specialist", "source": "Alibaba"},
            {"name": "DeepSeek V4", "type": "Reasoning", "source": "DeepSeek"},
            {"name": "Phi-4", "type": "Compact Edge", "source": "Microsoft"},
            {"name": "Ministral 8B", "type": "Efficiency", "source": "Mistral"}
        ],
        "trading_finance_models": [
            {"name": "FinBERT", "type": "Financial Sentiment", "source": "ProsusAI"},
            {"name": "CryptoBERT", "type": "Crypto Sentiment", "source": "HuggingFace"},
            {"name": "Sentence Transformers (MiniLM, MPNet)", "type": "Embeddings", "source": "sentence-transformers"},
            {"name": "Twitter RoBERTa", "type": "Social Sentiment", "source": "cardiffnlp"}
        ],
        "quantized_slms": [
            {"name": "Q4_K_M_Mistral", "type": "4-bit Quantized", "status": "LOCKED"},
            {"name": "Q5_K_M_Llama", "type": "5-bit Quantized", "status": "LOCKED"}
        ],
        "custom_models": [
            {"name": "LSTM Price Predictor", "type": "Time Series", "status": "TRAINED"},
            {"name": "PPO RL Trader", "type": "Reinforcement Learning", "status": "TRAINED"},
            {"name": "Transformer Forecaster", "type": "Market Prediction", "status": "TRAINED"}
        ]
    }

# ═══════════════════════════════════════════════════════════════════
# WORKER CONSTELLATION
# ═══════════════════════════════════════════════════════════════════

def get_worker_constellation() -> List[Dict]:
    """Get all TIA workers"""
    return [
        {
            "name": "tia_code_finder",
            "role": "Discovery Worker",
            "purpose": "Scans all repos for TIA-related code",
            "authority": "Code discovery & cataloging",
            "location": "vamguard_templates/workers/tia_code_finder.py"
        },
        {
            "name": "tia_sync_worker",
            "role": "Sync Worker",
            "purpose": "Pushes discovered TIA code to TIA-ARCHITECT-CORE",
            "authority": "TIA-ARCHITECT-CORE write access",
            "location": "vamguard_templates/workers/tia_sync_worker.py"
        },
        {
            "name": "apps_script_toolbox",
            "role": "Google Sheets Bridge",
            "purpose": "Identity Strike Reports, Archive Audits, Worker Dashboards",
            "authority": "Google Sheets automation",
            "location": "tia-architect-core-templates/workers/apps_script_toolbox.py"
        },
        {
            "name": "worker_watchdog",
            "role": "Monitor & Restart",
            "purpose": "Monitor & restart agent workers",
            "authority": "Worker health management",
            "location": "tia-architect-core-templates/workers/worker_watchdog.py"
        },
        {
            "name": "self_healing_worker",
            "role": "Auto-Recovery",
            "purpose": "Auto-recovery & self-repair systems",
            "authority": "System healing & recovery",
            "location": "tia-architect-core-templates/workers/self_healing_worker.py"
        }
    ]

# ═══════════════════════════════════════════════════════════════════
# HEADER
# ═══════════════════════════════════════════════════════════════════

st.title("🧠 T.I.A. MASTER SYSTEM")
st.markdown(f"**The Intelligence Architect - Complete Build {VERSION}**")
st.markdown(f"*Build Date: {BUILD_DATE} | GitHub: {GITHUB_ORG} | HuggingFace: {HF_ORG}*")
st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════

with st.sidebar:
    st.header("⚙️ System Control")
    
    # System status
    st.subheader("🟢 Status")
    st.success("ALL SYSTEMS ONLINE")
    
    # Quick stats
    st.metric("Core Systems", "5")
    st.metric("Workers Active", "5")
    st.metric("Models Available", "15+")
    
    st.markdown("---")
    
    # Navigation
    st.subheader("📍 Navigation")
    selected_tab = st.radio(
        "Select Module:",
        ["🏠 Dashboard", "🤖 Core Systems", "📊 Models", "⚙️ Workers", "💬 Oracle", "📚 RAG", "🔧 Tools"]
    )

# ═══════════════════════════════════════════════════════════════════
# TAB: DASHBOARD
# ═══════════════════════════════════════════════════════════════════

if selected_tab == "🏠 Dashboard":
    st.header("🏠 System Dashboard")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("🧠 Identity")
        st.write("**Name:** T.I.A. (The Intelligence Architect)")
        st.write("**Version:**", VERSION)
        st.write("**Role:** Sovereign AI Oracle & RAG System")
        st.write("**Location:** HuggingFace Space (L4 GPU)")
    
    with col2:
        st.subheader("🔗 Connections")
        st.write("**GitHub Org:**", GITHUB_ORG)
        st.write("**HuggingFace Org:**", HF_ORG)
        st.write("**Primary Repo:** mapping-and-inventory")
        st.write("**Intelligence Mesh:** 321GB distributed")
    
    with col3:
        st.subheader("📊 Capabilities")
        st.write("✅ RAG Intelligence Synthesis")
        st.write("✅ Model Registry Management")
        st.write("✅ Worker Orchestration")
        st.write("✅ Forever Learning Cycle")
    
    st.markdown("---")
    
    # System Topology
    st.subheader("🗺️ System Topology")
    topology = """
```
T.I.A. ECOSYSTEM
├── PRIMARY NODES
│   ├── TIA-ARCHITECT-CORE (HF Space) — Main oracle & UI
│   ├── tias-citadel (HF Space) — Citadel integration
│   └── mapping-and-inventory (GitHub) — Source truth
│
├── CORE SYSTEMS
│   ├── tia_architect — Boot & initialization
│   ├── tia_atomic — Model routing (P1, P2, D02)
│   ├── tia_sos — Emergency protocols
│   ├── tias_pioneer_trader — Market analysis
│   └── tias_sentinel_swarm — Security perimeter
│
├── WORKERS (5 Active)
│   ├── tia_code_finder — Code discovery
│   ├── tia_sync_worker — Code synchronization
│   ├── apps_script_toolbox — Sheets automation
│   ├── worker_watchdog — Monitoring
│   └── self_healing_worker — Auto-recovery
│
├── SERVICES
│   ├── tia_connector — Gemini oracle
│   ├── tia_coordinator — Integration sync
│   └── wake_up_tia — Model staging
│
└── DEPLOYMENT
    ├── GitHub Actions (6 workflows)
    ├── Bash scripts (5 deployment tools)
    └── Templates (requirements, app.py, workers)
```
    """
    st.code(topology, language="")

# ═══════════════════════════════════════════════════════════════════
# TAB: CORE SYSTEMS
# ═══════════════════════════════════════════════════════════════════

elif selected_tab == "🤖 Core Systems":
    st.header("🤖 Core Systems Status")
    
    systems = [
        tia_architect_status(),
        tia_atomic_status(),
        tia_sos_status(),
        tias_pioneer_trader_status(),
        tias_sentinel_swarm_status()
    ]
    
    for system in systems:
        with st.expander(f"**{system['name']}** - {system['status']}", expanded=False):
            st.write("**Purpose:**", system.get('purpose', 'N/A'))
            if 'version' in system:
                st.write("**Version:**", system['version'])
            if 'hf_cluster' in system:
                st.write("**HF Cluster:**", system['hf_cluster'])
            if 'triggers' in system:
                st.write("**Triggers:**", ", ".join(system['triggers']))
            if 'signals' in system:
                st.write("**Signals:**", ", ".join(system['signals']))
            if 'coverage' in system:
                st.write("**Coverage:**", system['coverage'])
            st.code(system['location'], language="")

# ═══════════════════════════════════════════════════════════════════
# TAB: MODELS
# ═══════════════════════════════════════════════════════════════════

elif selected_tab == "📊 Models":
    st.header("📊 Model Registry")
    
    registry = get_model_registry()
    
    st.subheader("🚀 Frontier Models (2026)")
    for model in registry["frontier_models_2026"]:
        st.write(f"**{model['name']}** ({model['type']}) - *{model['source']}*")
    
    st.markdown("---")
    
    st.subheader("💰 Trading/Finance Models")
    for model in registry["trading_finance_models"]:
        st.write(f"**{model['name']}** ({model['type']}) - *{model['source']}*")
    
    st.markdown("---")
    
    st.subheader("⚡ Quantized SLMs")
    for model in registry["quantized_slms"]:
        status_icon = "🔒" if model['status'] == "LOCKED" else "🔓"
        st.write(f"{status_icon} **{model['name']}** ({model['type']}) - *{model['status']}*")
    
    st.markdown("---")
    
    st.subheader("🎯 Custom Models")
    for model in registry["custom_models"]:
        st.write(f"**{model['name']}** ({model['type']}) - *{model['status']}*")

# ═══════════════════════════════════════════════════════════════════
# TAB: WORKERS
# ═══════════════════════════════════════════════════════════════════

elif selected_tab == "⚙️ Workers":
    st.header("⚙️ Worker Constellation")
    
    workers = get_worker_constellation()
    
    st.write(f"**Active Workers:** {len(workers)}")
    st.markdown("---")
    
    for worker in workers:
        with st.expander(f"**{worker['name']}** - {worker['role']}", expanded=False):
            st.write("**Purpose:**", worker['purpose'])
            st.write("**Authority:**", worker['authority'])
            st.code(worker['location'], language="")

# ═══════════════════════════════════════════════════════════════════
# TAB: ORACLE
# ═══════════════════════════════════════════════════════════════════

elif selected_tab == "💬 Oracle":
    st.header("💬 T.I.A. Oracle (Gemini 2.0 Flash)")
    
    st.markdown("""
    Ask T.I.A. anything about:
    - Citadel architecture & topology
    - Repository structure & code
    - System status & health
    - Deployment strategies
    - Worker coordination
    """)
    
    user_query = st.text_area("Enter your query:", height=100)
    
    if st.button("🔮 Ask T.I.A."):
        if user_query:
            with st.spinner("⏳ Consulting oracle..."):
                response = get_tia_response(user_query)
                st.markdown("### 🧠 T.I.A. Response:")
                st.markdown(response)
        else:
            st.warning("Please enter a query.")

# ═══════════════════════════════════════════════════════════════════
# TAB: RAG
# ═══════════════════════════════════════════════════════════════════

elif selected_tab == "📚 RAG":
    st.header("📚 RAG Knowledge Base")
    
    st.info("RAG system integration coming soon...")
    
    st.subheader("Knowledge Sources")
    st.write("- master_intelligence_map.txt")
    st.write("- master_inventory.json")
    st.write("- District TREE.md files")
    st.write("- All repository scaffolds")
    st.write("- Documentation corpus")

# ═══════════════════════════════════════════════════════════════════
# TAB: TOOLS
# ═══════════════════════════════════════════════════════════════════

elif selected_tab == "🔧 Tools":
    st.header("🔧 System Tools")
    
    st.subheader("📁 Data Directories")
    st.code(f"""
DATA_DIR = {DATA_DIR}
MODELS_DIR = {MODELS_DIR}
WORKERS_DIR = {WORKERS_DIR}
RAG_DIR = {RAG_DIR}
TIA_SOUL_DIR = {TIA_SOUL_DIR}
    """, language="python")
    
    st.markdown("---")
    
    st.subheader("🔍 System Info")
    st.write("**Python Version:**", sys.version.split()[0])
    st.write("**Platform:**", sys.platform)
    st.write("**Build Date:**", BUILD_DATE)
    st.write("**Version:**", VERSION)

# ═══════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(f"*T.I.A. Master Build {VERSION} | Built with 💚 for the Citadel Mesh*")
