import streamlit as st
import os
import json
import pandas as pd
from google import genai

st.set_page_config(page_title="CITADEL OMEGA HUD", layout="wide", page_icon="🏰")

def get_tia_response(prompt):
    keys = [os.getenv("GEMINI_API_KEY"), os.getenv("GEMINI_API_KEY_2")]
    keys = [k for k in keys if k]
    if not keys: return "❌ Neural Signal Offline."
    for key in keys:
        try:
            client = genai.Client(api_key=key)
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            return response.text
        except Exception: continue
    return "⏳ BOTH CORES OVERHEATED."

st.title("🏰 CITADEL OMEGA // SOVEREIGN COMMAND")
st.sidebar.info(f"💎 MAP: 9,354 ENTITIES SECURED")

tabs = st.tabs(["🎮 Command", "📊 Librarian", "🚢 Heavy Lift"])

with tabs[1]:
    st.header("📊 Librarian Discovery")
    if os.path.exists("master_inventory.json"):
        with open("master_inventory.json", "r") as f:
            inventory = json.load(f)
            st.write(f"Total Entities: **{len(inventory)}**")
            search = st.text_input("🔍 Search...")
            if search:
                results = [i for i in inventory if search.lower() in str(i).lower()]
                st.dataframe(pd.DataFrame(results))

with tabs[2]:
    st.header("🚢 Heavy Lift: Ingestion Engine")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚀 PULL OPPO CARGO"):
            st.info("Syncing 23GB Genesis Haul...")
            os.system("rclone sync gdrive:GENESIS_VAULT /data/Research/Genesis --progress")
    with c2:
        if st.button("🏗️ PULL LAPTOP CARGO"):
            st.info("Syncing 321GB Laptop Haul...")
            # THIS IS THE LINE THAT WAS MISSING:
            os.system("rclone sync gdrive:GENESIS_VAULT/LAPTOP_CARGO /data/Research/Laptop --progress")
