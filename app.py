import gradio as gr
import os

def tia_architect(message, history):
    return f'T.I.A. ARCHITECT CORE ONLINE. Connected to ARK_CORE. Analyzing: {message}'

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown('# T.I.A. ARCHITECT CORE // D57')
    gr.ChatInterface(tia_architect)

if __name__ == '__main__':
    demo.launch()