"""
Q.G.T.N.L. (0) // REPO MAPPER
Maps all connected repositories, HuggingFace spaces, frameworks,
and their connections/scaffolds for the Mapping & Inventory Librarian.
"""
import os
import subprocess
import json
from datetime import datetime


# Known repos, spaces and their metadata
KNOWN_REPOS = [
    {
        "name": "mapping-and-inventory",
        "type": "GitHub Repo",
        "role": "Librarian / Central Hub",
        "framework": "Streamlit",
        "url": "https://github.com/DJ-Goana-Coding/mapping-and-inventory",
        "connected_to": ["ARK_CORE", "tia-architect-core", "S10_Uplink", "GDrive"],
    },
    {
        "name": "ARK_CORE",
        "type": "GitHub Repo",
        "role": "Sovereign Intelligence Engine",
        "framework": "Python / Streamlit",
        "url": "https://github.com/DJ-Goana-Coding/ARK_CORE",
        "connected_to": ["mapping-and-inventory", "tia-architect-core", "GDrive"],
    },
    {
        "name": "tia-architect-core",
        "type": "HuggingFace Space",
        "role": "T.I.A. Oracle / AI Interface",
        "framework": "Streamlit / Gemini",
        "url": "https://huggingface.co/spaces/DJ-Goana-Coding/ARK_CORE",
        "connected_to": ["ARK_CORE", "mapping-and-inventory"],
    },
    {
        "name": "S10_Uplink",
        "type": "Device Node",
        "role": "Mobile Termux Node",
        "framework": "Termux / Python",
        "url": "local",
        "connected_to": ["ARK_CORE", "GDrive"],
    },
    {
        "name": "Oppo_Termux",
        "type": "Device Node",
        "role": "Secondary Mobile Node",
        "framework": "Termux / Python",
        "url": "local",
        "connected_to": ["ARK_CORE", "GDrive"],
    },
    {
        "name": "Laptop_Matrix",
        "type": "Device Node",
        "role": "Primary Compute Node",
        "framework": "Ubuntu / Python",
        "url": "local",
        "connected_to": ["ARK_CORE", "GDrive", "mapping-and-inventory"],
    },
    {
        "name": "GDrive",
        "type": "Cloud Storage",
        "role": "Genesis Vault / LAPTOP_CARGO",
        "framework": "rclone",
        "url": "gdrive:GENESIS_VAULT",
        "connected_to": ["ARK_CORE", "mapping-and-inventory", "S10_Uplink", "Oppo_Termux", "Laptop_Matrix"],
    },
]

# Known frameworks / tech stack across the system
FRAMEWORKS = [
    {"name": "Streamlit", "role": "UI / HUD Layer", "used_in": ["mapping-and-inventory", "ARK_CORE", "tia-architect-core"]},
    {"name": "Gemini / google-genai", "role": "AI / T.I.A. Brain", "used_in": ["mapping-and-inventory", "ARK_CORE"]},
    {"name": "rclone", "role": "Cloud Sync Engine", "used_in": ["mapping-and-inventory", "ARK_CORE"]},
    {"name": "HuggingFace Hub", "role": "Model / Dataset Store", "used_in": ["ARK_CORE", "tia-architect-core"]},
    {"name": "pandas", "role": "Data Processing", "used_in": ["mapping-and-inventory", "ARK_CORE"]},
    {"name": "plotly", "role": "Visual Mapping", "used_in": ["mapping-and-inventory"]},
    {"name": "git", "role": "Version Control / Remote Sync", "used_in": ["mapping-and-inventory", "ARK_CORE"]},
    {"name": "Python 3.12", "role": "Core Runtime", "used_in": ["mapping-and-inventory", "ARK_CORE", "S10_Uplink"]},
]


def get_git_remotes(repo_path=None):
    """Return git remotes for a given repo path."""
    path = repo_path or os.getcwd()
    try:
        out = subprocess.check_output(
            ["git", "remote", "-v"], cwd=path, stderr=subprocess.DEVNULL
        ).decode().strip()
        remotes = {}
        for line in out.splitlines():
            parts = line.split()
            if len(parts) >= 2 and "(fetch)" in line:
                remotes[parts[0]] = parts[1]
        return remotes
    except Exception:
        return {}


def get_local_structure(base_path=None):
    """Walk the local repo and return a scaffold/structure map."""
    base = base_path or os.getcwd()
    structure = {}
    for root, dirs, files in os.walk(base):
        # Skip hidden dirs and __pycache__
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "__pycache__"]
        rel = os.path.relpath(root, base)
        structure[rel] = {"dirs": dirs, "files": files, "file_count": len(files)}
    return structure


def build_connection_graph():
    """Build a node/edge list for the visual connection map."""
    nodes = []
    edges = []
    seen = set()

    for repo in KNOWN_REPOS:
        name = repo["name"]
        if name not in seen:
            nodes.append({
                "id": name,
                "label": name,
                "type": repo["type"],
                "role": repo["role"],
                "framework": repo["framework"],
            })
            seen.add(name)
        for conn in repo.get("connected_to", []):
            if conn not in seen:
                # Add placeholder if not explicitly listed
                nodes.append({"id": conn, "label": conn, "type": "Node", "role": "", "framework": ""})
                seen.add(conn)
            # Avoid duplicate edges (undirected)
            edge = tuple(sorted([name, conn]))
            if edge not in edges:
                edges.append(edge)

    return nodes, edges


def get_system_snapshot():
    """Return a full snapshot: repos, frameworks, remotes, structure."""
    remotes = get_git_remotes()
    structure = get_local_structure()
    nodes, edges = build_connection_graph()
    return {
        "timestamp": datetime.now().isoformat(),
        "repos": KNOWN_REPOS,
        "frameworks": FRAMEWORKS,
        "git_remotes": remotes,
        "local_structure": {k: v["file_count"] for k, v in structure.items()},
        "graph_nodes": nodes,
        "graph_edges": [list(e) for e in edges],
        "env_tokens": {
            "GITHUB_TOKEN": "DETECTED" if os.getenv("GITHUB_TOKEN") else "MISSING",
            "HF_TOKEN": "DETECTED" if os.getenv("HF_TOKEN") else "MISSING",
            "GEMINI_API_KEY": "DETECTED" if os.getenv("GEMINI_API_KEY") else "MISSING",
            "RCLONE_CONFIG_DATA": "DETECTED" if os.getenv("RCLONE_CONFIG_DATA") else "MISSING",
        },
    }


if __name__ == "__main__":
    snap = get_system_snapshot()
    print(json.dumps(snap, indent=2))
