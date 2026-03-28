import sys
import os

# Ensure the repo root is on the path so TIA package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from TIA.tia_core import build_ui  # noqa: E402

demo = build_ui()

if __name__ == '__main__':
    demo.launch()