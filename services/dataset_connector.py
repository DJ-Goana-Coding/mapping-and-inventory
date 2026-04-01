"""
Q.G.T.N.L. (0) // DATASET CONNECTOR
Connects to HuggingFace datasets, local JSON inventories,
and the master_inventory.json Librarian ledger.
"""
import os
import json
from pathlib import Path


# Known HuggingFace datasets used across the system
KNOWN_HF_DATASETS = [
    {
        "name": "ARK_CORE / master_inventory",
        "type": "local",
        "path": "master_inventory.json",
        "description": "9,354-entity master inventory ledger — all files across the full stack",
    },
    {
        "name": "ARK_CORE / system_manifest",
        "type": "local",
        "path": "system_manifest.json",
        "description": "System identity, node list, and status manifest",
    },
    {
        "name": "HuggingFace: DJ-Goana-Coding",
        "type": "huggingface",
        "path": "https://huggingface.co/DJ-Goana-Coding",
        "description": "Public models and datasets hosted on HuggingFace",
    },
    {
        "name": "GDrive: GENESIS_VAULT",
        "type": "gdrive",
        "path": "gdrive:GENESIS_VAULT",
        "description": "Genesis Research Vault — 23GB of primary research data",
    },
    {
        "name": "GDrive: LAPTOP_CARGO",
        "type": "gdrive",
        "path": "gdrive:GENESIS_VAULT/LAPTOP_CARGO",
        "description": "Laptop 321GB data cargo — full laptop drive backup",
    },
    {
        "name": "Forever_Learning Neurons",
        "type": "local",
        "path": "Forever_Learning",
        "description": "Aetheric / spatial neuron JSON files from probe missions",
    },
    {
        "name": "Archive Vault",
        "type": "local",
        "path": "Archive_Vault",
        "description": "Master backup and archive JSON store",
    },
]


def load_local_inventory(path: str = "master_inventory.json") -> list:
    """Load the master_inventory.json ledger. Returns a list of entity dicts."""
    abs_path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
    if not os.path.exists(abs_path):
        return []
    with open(abs_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        # Flatten if nested
        items = []
        for k, v in data.items():
            if isinstance(v, list):
                items.extend(v)
            else:
                items.append({"key": k, **v} if isinstance(v, dict) else {"key": k, "value": v})
        return items
    return []


def search_inventory(inventory: list, query: str, limit: int = 100) -> list:
    """Case-insensitive search across all fields of inventory entries."""
    q = query.lower()
    return [item for item in inventory if q in str(item).lower()][:limit]


def load_neuron_data(base_path: str = None) -> list:
    """Load Forever_Learning neuron JSON files."""
    path = base_path or os.path.join(os.getcwd(), "Forever_Learning")
    neurons = []
    if not os.path.isdir(path):
        return neurons
    for fname in sorted(os.listdir(path)):
        if fname.endswith(".json"):
            try:
                with open(os.path.join(path, fname), "r") as f:
                    data = json.load(f)
                    data["_file"] = fname
                    neurons.append(data)
            except Exception:
                pass
    return neurons


def get_dataset_summary() -> list:
    """Return summary of all known datasets with availability status."""
    summary = []
    for ds in KNOWN_HF_DATASETS:
        entry = dict(ds)
        if ds["type"] == "local":
            p = ds["path"]
            abs_p = p if os.path.isabs(p) else os.path.join(os.getcwd(), p)
            if os.path.isfile(abs_p):
                try:
                    with open(abs_p) as f:
                        data = json.load(f)
                    count = len(data) if isinstance(data, list) else len(data)
                    entry["status"] = f"✅ ONLINE ({count} entries)"
                except Exception:
                    entry["status"] = "⚠️ FILE ERROR"
            elif os.path.isdir(abs_p):
                count = len([x for x in os.listdir(abs_p) if x.endswith(".json")])
                entry["status"] = f"✅ ONLINE ({count} JSON files)"
            else:
                entry["status"] = "❌ NOT FOUND"
        elif ds["type"] in ("gdrive", "huggingface"):
            entry["status"] = "🔗 REMOTE (requires sync)"
        else:
            entry["status"] = "❓ UNKNOWN"
        summary.append(entry)
    return summary


def get_inventory_stats(inventory: list) -> dict:
    """Return statistics about the inventory."""
    if not inventory:
        return {}
    exts = {}
    paths = []
    for item in inventory:
        name = item.get("name", "")
        path = item.get("path", "")
        if "." in name:
            ext = name.rsplit(".", 1)[-1].lower()
            exts[ext] = exts.get(ext, 0) + 1
        if path:
            paths.append(path)

    top_dirs = {}
    for p in paths:
        parts = p.split("/")
        if len(parts) > 1:
            top = parts[1] if parts[0] == "" else parts[0]
            top_dirs[top] = top_dirs.get(top, 0) + 1

    sorted_exts = sorted(exts.items(), key=lambda x: x[1], reverse=True)[:15]
    sorted_dirs = sorted(top_dirs.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "total": len(inventory),
        "top_extensions": dict(sorted_exts),
        "top_directories": dict(sorted_dirs),
    }
