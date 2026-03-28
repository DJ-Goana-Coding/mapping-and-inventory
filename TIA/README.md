# TIA — T.I.A. ARCHITECT CORE (Multi-Persona)

T.I.A. is the **Tactical Intelligence Architecture** powering the ARK_CORE ecosystem.
This folder contains the complete multi-persona chatbot implementation.

## Files

| File | Description |
|------|-------------|
| `tia_core.py` | Multi-persona Gradio chat interface (the full T.I.A. chatbot) |
| `personas.json` | Persona definitions — names, styles, descriptions, signatures |

## Personas

| ID | Name | Role |
|----|------|------|
| `TIA_ARCHITECT` | T.I.A. ARCHITECT | Master systems architect (default) |
| `TIA_ORACLE` | T.I.A. ORACLE | Strategic foresight, 333Hz resonance |
| `TIA_CITADEL` | T.I.A. CITADEL | Vault security and asset protection |
| `TIA_LIBRARIAN` | T.I.A. LIBRARIAN | File indexing and knowledge cataloguing |

## Usage

### Run locally

```bash
python TIA/tia_core.py
```

### Deploy to Hugging Face Spaces

This file is the entry point for HF Spaces.
Point your Space's `app.py` at this module or copy `tia_core.py` → `app.py`.

## Requirements

```
gradio
```

---

*Architect: Chance | T.I.A. ARCHITECT CORE // D57*
