# Mapping and Inventory — T.I.A. ARCHITECT CORE

A project for mapping, indexing, and monitoring files across the ARK_CORE system.

## Project Structure

```
mapping-and-inventory/
├── app.py                        # Gradio chat interface (T.I.A. ARCHITECT CORE)
├── requirements.txt              # Python dependencies
├── TIA/                          # ⚡ T.I.A. multi-persona chatbot (highlighted)
│   ├── tia_core.py               # Full multi-persona Gradio interface
│   ├── personas.json             # Persona definitions (ARCHITECT, ORACLE, CITADEL, LIBRARIAN)
│   └── README.md                 # T.I.A. usage guide
├── CRYPTO_SNIPER/                # 📡 Crypto extraction & vault monitoring
│   ├── god_view.py               # Live GOD-VIEW dashboard (polls ARK node)
│   ├── sniper_config.json        # Node connection configuration template
│   └── README.md                 # Dashboard usage guide
├── services/
│   ├── manifest_generator.py     # Indexes project files into master_inventory.json
│   └── ark_engine.py             # Orchestrates manifest generation and git sync
├── ARK_CORE/
│   └── scripts/
│       └── god_view.py           # Original live dashboard (GOD-VIEW)
└── Partition_01/
    └── master_inventory.json     # Auto-generated file inventory (paths + sizes + timestamps)
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### ⚡ Launch the T.I.A. multi-persona chatbot

```bash
python TIA/tia_core.py
```

Switch between four personas (ARCHITECT, ORACLE, CITADEL, LIBRARIAN) directly in the UI.

### 📡 Launch the crypto GOD-VIEW dashboard

```bash
python CRYPTO_SNIPER/god_view.py
```

Edit `CRYPTO_SNIPER/sniper_config.json` to set your S10 node IP before running.

### Launch the basic chat interface

```bash
python app.py
```

### Generate the file inventory

```bash
python services/manifest_generator.py
```

### Run the sync engine (generates manifest + commits + pushes)

```bash
python services/ark_engine.py
```

## Components

- **TIA/tia_core.py** — Full multi-persona T.I.A. chatbot. Loads personas from `personas.json` and provides a Gradio UI with persona switching. This is the primary file to deploy to Hugging Face Spaces.
- **TIA/personas.json** — Defines all T.I.A. personas: `TIA_ARCHITECT`, `TIA_ORACLE`, `TIA_CITADEL`, `TIA_LIBRARIAN`.
- **CRYPTO_SNIPER/god_view.py** — Polls a remote ARK node and renders a live extraction/vault dashboard every 30 seconds. Reads connection config from `sniper_config.json`.
- **CRYPTO_SNIPER/sniper_config.json** — Node endpoint configuration template (copy and edit before running).
- **app.py** — Minimal Gradio chat UI (single-persona entry point, compatible with HF Spaces as-is).
- **manifest_generator.py** — Walks the project root and indexes all `.py`, `.sh`, `.json`, `.csv`, and `.log` files into `Partition_01/master_inventory.json` with per-file path, size, and modification timestamp.
- **ark_engine.py** — Runs the manifest generator, commits the result, and force-pushes to configured remotes.

## Secrets Required for Full CI/CD

| Secret | Purpose |
|--------|---------|
| `HF_TOKEN` | Push to Hugging Face Space (`DJ-Goanna-Coding/TIA-ARCHITECT-CORE`) |
| `TOKEN_ARK_CORE` | Push to the `ARK_CORE` GitHub repository |
| `TOKEN_MAPPING_INVENTORY` | Push to this repo via PAT (optional — falls back to `github.token`) |

Configure these in **Settings → Secrets and variables → Actions** for this repository.

