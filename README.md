# Mapping and Inventory — T.I.A. ARCHITECT CORE

A project for mapping, indexing, and monitoring files across the ARK_CORE system.

## Project Structure

```
mapping-and-inventory/
├── app.py                        # Gradio chat interface (T.I.A. ARCHITECT CORE)
├── requirements.txt              # Python dependencies
├── services/
│   ├── manifest_generator.py     # Indexes project files into master_inventory.json
│   └── ark_engine.py             # Orchestrates manifest generation and git sync
├── ARK_CORE/
│   └── scripts/
│       └── god_view.py           # Live dashboard monitoring (GOD-VIEW)
└── Partition_01/
    └── master_inventory.json     # Auto-generated file inventory
```

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Launch the chat interface

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

### Run the live GOD-VIEW dashboard

```bash
python ARK_CORE/scripts/god_view.py
```

## Components

- **app.py** — Gradio-powered chat UI for T.I.A. ARCHITECT CORE (D57).
- **manifest_generator.py** — Walks the project root and indexes all `.py`, `.sh`, `.json`, `.csv`, and `.log` files into `Partition_01/master_inventory.json`.
- **ark_engine.py** — Runs the manifest generator, commits the result, and force-pushes to configured remotes.
- **god_view.py** — Polls a remote status endpoint every 30 seconds and renders a live dashboard.
