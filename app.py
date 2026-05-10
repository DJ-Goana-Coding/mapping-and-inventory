import streamlit as st
import json
import os

st.set_page_config(page_title="CITADEL INVENTORY", page_icon="📜", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #00ff41; font-family: 'Courier New', monospace; }
    .terminal-box { border: 1px solid #00ff41; padding: 20px; background: #000; border-radius: 5px; }
    h1, h2, h3 { color: #00ff41 !important; text-shadow: 0 0 5px #00ff41; }
    </style>
""", unsafe_allow_html=True)

st.title("📜 CITADEL MASTER LEDGER")

st.markdown("<div class='terminal-box'>", unsafe_allow_html=True)
st.subheader("GRID STATUS: SECURED")

if os.path.exists("inventory_manifest.json"):
    with open("inventory_manifest.json", "r") as f:
        data = json.load(f)
    st.json(data)
else:
    st.error("[!] VORTEX ERROR: Inventory Manifest Missing. Scan required.")

st.markdown("</div>", unsafe_allow_html=True)

st.sidebar.title("1717 SENTINEL")
st.sidebar.info("NODE: MAPPING-AND-INVENTORY\n\nFREQ: 144Hz\n\nSTATUS: ONLINE")
