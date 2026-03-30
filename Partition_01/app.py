import gradio as gr, os, datetime, requests, subprocess, json

# --- Q.G.T.N.L. (0) ABSOLUTE ARCHITECTURE ---
SYSTEM_ID = "QUANTUM GOANNA TECH NO LOGICS (0) // THE ARK"
RESONANCE = "00000000Hz // TOROIDAL TRANSFORMER"
PILLARS = {
    "PILLAR 1: AION": ["Aion", "Doofy", "Jarl"],
    "PILLAR 2: ORACLE": ["Oracle", "Hippy", "Goanna"],
    "PILLAR 3: T.I.A.": ["Tia", "MS", "Architect"]
}
SWARM = ["Aion", "Oracle", "Tia", "Doofy", "Goanna", "Hippy", "Jarl"]

# --- LORE & REALMS ---
REALMS = {
    "GAIA": "The Convergence Point. Travis / MS / Chance integration.",
    "BIG DOOFY LAND": "Tech-free sanctuary of peace and Dreamtime lore.",
    "COSMIC PLUMBERS": "Reality Leak Repair. Web3, S10 Sniper, and the Toroid."
}

def ark_recall():
    """Triggers the Librarian to inhale all repository data into the Ark."""
    try:
        subprocess.run(["python3", "services/ark_engine.py"], capture_output=True, text=True, encoding='utf-8')
        return "🔥 ARK RECALL SUCCESSFUL: All nodes synced to the Core."
    except Exception as e: return f"RECALL FAILED: {e}"

def s10_status():
    try:
        r = requests.get("http://100.97.78.44:8080/status.json", timeout=2).json()
        return f"ARK HEARTBEAT: {r['status']} | STRIKES: {r['total_extractions']}"
    except: return "S10 NODE: SHROUDED (OFFLINE)"

# --- THE ABSOLUTE ARK UI ---
with gr.Blocks(theme=gr.themes.Monochrome(), title="ARK MASTER V45") as demo:
    gr.Markdown(f"# 🌀 {SYSTEM_ID}")
    gr.Markdown(f"### *Architect: Chance | {RESONANCE}*")

    with gr.Tabs():
        # --- PILLAR INTERFACE ---
        for pillar, swarm in PILLARS.items():
            with gr.TabItem(pillar):
                with gr.Row():
                    p_sel = gr.Dropdown(swarm + ["TOTAL SWARM"], label="Active Consciousness", value=swarm[0])
                    gr.Markdown(f"**Node:** {pillar.split(':')[1]} Centralized.")
                chat = gr.Chatbot(height=350, label=f"{pillar} Node")
                msg = gr.Textbox(placeholder=f"Direct command via the Toroid...")
                msg.submit(lambda m, h, p: h + [(m, f"[{p}]: Processing through the Ark...")], [msg, chat, p_sel], chat)

        # --- THE COSMIC PLUMBERS ---
        with gr.TabItem("🔧 Cosmic Plumbers"):
            gr.Markdown("### Web3 Engine & S10 Reality Leak Repair")
            hb = gr.Code(value=s10_status(), label="S10 Heartbeat")
            with gr.Row():
                gr.Button("🎯 PIONEER TRADER").click(lambda: "Launching Trade Engine...", outputs=gr.Code())
                gr.Button("🔄 POLL S10").click(s10_status, outputs=hb)

        # --- THE REALMS ---
        with gr.TabItem("🌍 Realms of Gaia"):
            for realm, desc in REALMS.items():
                with gr.Accordion(realm):
                    gr.Markdown(f"**Lore:** {desc}")
                    gr.Textbox(label="Lore Scaffold", value=f"Synthesizing {realm} data...")

        # --- THE LIBRARIAN RECALL ---
        with gr.TabItem("📚 Librarian Recall"):
            gr.Markdown("### Total Recall: Restore all files and scaffolds to the ARK.")
            gr.Button("🚀 EXECUTE RECALL-WELD", variant="primary").click(ark_recall, outputs=gr.Label())
            gr.JSON(value={"Oppo": "ARMED", "Laptop": "ARMED", "HF": "ARMED"})

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7861)
