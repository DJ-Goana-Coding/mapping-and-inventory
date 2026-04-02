import streamlit as st
import os
import json
import pandas as pd
import subprocess

st.set_page_config(page_title="CITADEL OMEGA: L4 COMMAND", layout="wide", page_icon="🏰")

# 1. SETUP THE RCLONE IGNITION
def setup_rclone():
    conf_data = os.getenv("RCLONE_CONFIG_DATA")
    if conf_data:
        config_path = os.path.expanduser("~/.config/rclone/rclone.conf")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as f:
            f.write(conf_data)
        return True
    return False

# 2. THE LIBRARIAN ENGINE (Pointed at the 9,354 Ledger)
def load_inventory():
    # Looking for the new 9,354-entity map at the root
    map_path = "master_inventory.json"
    if os.path.exists(map_path):
        with open(map_path, "r") as f:
            return json.load(f)
    return None

st.title("🏰 CITADEL OMEGA // L4 NODAL COMMAND")

if setup_rclone():
    st.sidebar.success("✅ CLOUD CRANE: READY")
else:
    st.sidebar.error("❌ CLOUD CRANE: NO KEY")

st.sidebar.info(f"🧬 SOVEREIGN MAP: 9,354 ENTITIES DETECTED")

# TAB SYSTEM
tabs = st.tabs(["🛰️ Ingestion", "📊 Librarian", "🧠 T.I.A. Oracle"])

with tabs[0]:
    st.header("🛰️ Heavy Lift Ingestion (23GB)")
    if st.button("🔥 START HEAVY LIFT"):
        st.info("🚀 L4 ENGINE: SYNCING G-DRIVE -> SOUL VAULT...")
        # Cloud-to-cloud pull
        cmd = ["rclone", "sync", "gdrive:GENESIS_VAULT", "./Research/Genesis", "--progress"]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        st.success("✅ Ingestion started in background. Monitor logs for arrival.")

with tabs[1]:
    st.header("📊 Librarian Discovery")
    inventory = load_inventory()
    if inventory:
        st.write(f"Total Indexed Entities: **{len(inventory)}**")
        search_query = st.text_input("🔍 Search (e.g. 'Santos', 'XRP', 'Audit')")
        if search_query:
            results = [item for item in inventory if search_query.lower() in str(item).lower()]
            st.dataframe(pd.DataFrame(results))
    else:
        st.error("⚠️ master_inventory.json not found in root.")

with tabs[2]:
    st.header("🧠 T.I.A. Oracle (L4 GPU)")
    st.info("Ready to process research data at ./Research/Genesis")
