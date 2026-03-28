"""
app.py — T.I.A. ARCHITECT CORE // Gradio Entry Point
Architect: Chance | OPPO_FORGE Origin

Minimal Gradio launcher that delegates UI construction to TIA/tia_core.py.
Compatible with Hugging Face Spaces (SDK: Gradio) as-is.
"""

import sys
import os

# Ensure the repo root is on the path so the TIA package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from TIA.tia_core import build_ui  # noqa: E402
except ImportError as exc:
    raise SystemExit(
        f'[ERROR] Could not import TIA.tia_core: {exc}\n'
        'Make sure the TIA/ directory and its dependencies are present.'
    ) from exc

demo = build_ui()

if __name__ == '__main__':
    demo.launch()