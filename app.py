import streamlit as st
import os
import json
import pandas as pd
from google import genai

st.set_page_config(page_title="CITADEL OMEGA HUD", layout="wide", page_icon="🏰")

def get_tia_response(prompt):
    # 🧬 DUAL-CORE NEURAL ROTATION
    keys = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_2")]
    keys = [k for k in keys if k]
    if not keys: return "❌ Neural Signal Offline (Check HF Secrets)."
    
    for key in keys:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            return response.text
        except Exception:
            continue
    return "⏳ BOTH CORES OVERHEATED. Wait 60s."

st.title("🏰 CITADEL OMEGA // SOVEREIGN COMMAND")
st.sidebar.info(f"💎 MAP: 9,354 ENTITIES SECURED")

tabs = st.tabs(["🎮 Command", "📊 Librarian", "🛰️ Heavy Lift"])

with tabs[0]:
    u_input = st.chat_input("Direct Directive...")
    if u_input: st.write(get_tia_response(u_input))

with tabs[1]:
    st.header("📊 Librarian Discovery")
    if os.path.exists("master_inventory.json"):
        with open("master_inventory.json", "r") as f:
            inventory = json.load(f)
            st.write(f"Entities: {len(inventory)}")
            search = st.text_input("🔍 Search...")
            if search:
                results = [i for i in inventory if search.lower() in str(i).lower()]
                st.dataframe(pd.DataFrame(results))

with tabs[2]:
    st.header("🛰️ Heavy Lift (23GB)")
    st.write("Source: `gdrive:GENESIS_VAULT` | Destination: `/data/Research/Genesis`")
    if st.button("🔥 START INGESTION"):
        st.info("🚀 SYNCING G-DRIVE -> SOUL VAULT...")
        os.system("rclone sync gdrive:GENESIS_VAULT /data/Research/Genesis --progress")
