import gradio as gr
import json
import os
import datetime

# ── Load persona definitions ─────────────────────────────────────────────────
_PERSONAS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'personas.json')
with open(_PERSONAS_PATH) as _f:
    PERSONAS = json.load(_f)

PERSONA_NAMES = list(PERSONAS.keys())


# ── Response logic ────────────────────────────────────────────────────────────
def tia_respond(message: str, history: list, persona_key: str) -> str:
    """Generate a T.I.A. response using the selected persona."""
    persona = PERSONAS.get(persona_key, PERSONAS['TIA_ARCHITECT'])
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return (
        f"[{persona['prefix']} | {timestamp}]\n"
        f"Persona: {persona['name']}  |  {persona['tagline']}\n"
        f"{'━' * 48}\n"
        f"Analyzing ({persona['style']}): {message}\n"
        f"\n— {persona['signature']}"
    )


def _on_persona_change(key: str) -> str:
    """Update the description box when a different persona is selected."""
    return PERSONAS.get(key, PERSONAS['TIA_ARCHITECT'])['description']


# ── Gradio UI ─────────────────────────────────────────────────────────────────
def build_ui() -> gr.Blocks:
    with gr.Blocks(theme=gr.themes.Soft(), title='T.I.A. ARCHITECT CORE') as demo:
        gr.Markdown('# ⚡ T.I.A. ARCHITECT CORE // D57')
        gr.Markdown(
            '**Tactical Intelligence Architecture** — Multi-Persona ARK_CORE Interface  \n'
            '*Architect: Chance | OPPO_FORGE Origin*'
        )

        with gr.Row():
            persona_dd = gr.Dropdown(
                choices=PERSONA_NAMES,
                value='TIA_ARCHITECT',
                label='🎭 Active Persona',
                interactive=True,
            )
            persona_desc = gr.Textbox(
                value=PERSONAS['TIA_ARCHITECT']['description'],
                label='Persona Description',
                interactive=False,
                lines=2,
            )

        persona_dd.change(_on_persona_change, inputs=persona_dd, outputs=persona_desc)

        gr.ChatInterface(
            fn=tia_respond,
            additional_inputs=[persona_dd],
            chatbot=gr.Chatbot(height=420, label='T.I.A.'),
            textbox=gr.Textbox(placeholder='Enter your message for T.I.A. ...', label=''),
            submit_btn='⚡ Send',
            retry_btn='🔄 Retry',
            undo_btn='↩ Undo',
            clear_btn='🗑 Clear',
        )

        gr.Markdown('---')
        gr.Markdown(
            '**Personas available:** ARCHITECT · ORACLE · CITADEL · LIBRARIAN  \n'
            '_T.I.A. ARCHITECT CORE // D57 — Connected to ARK_CORE_'
        )
    return demo


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    ui = build_ui()
    ui.launch()
