#!/usr/bin/env python3
"""
CITADEL OMEGA — T.I.A. IGNITION ENGINE

Purpose: Pull required models, tools, and libraries into persistent /data storage
for a 24GB L4 environment. Run from the Cloud Sync tab or CLI to pre-stage
weights and agentic frameworks.
"""
from __future__ import annotations

import os
import subprocess
from typing import Dict, Iterable

from huggingface_hub import snapshot_download


# ── Target Directories ──
MODELS_DIR = "/data/models"
TOOLS_DIR = "/data/tools"

# ── The Modal Selection (24GB L4 Optimized) ──
CORE_MODELS: Iterable[Dict[str, str]] = (
    {"repo": "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B", "role": "oracle"},
    {"repo": "Qwen/Qwen2.5-Coder-7B-Instruct", "role": "architect"},
    {"repo": "Qwen/Qwen2.5-VL-7B-Instruct", "role": "surveyor"},
)

# ── Agentic Tooling ──
AGENTIC_TOOLS = (
    "https://github.com/huggingface/smolagents",
    "https://github.com/run-llama/llama_index",
)


def ensure_directories() -> None:
    """Create target directories if they don't already exist."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(TOOLS_DIR, exist_ok=True)


def ignite_modals() -> None:
    """Download core models into /data/models/<role>."""
    print("🔥 IGNITE: Waking up T.I.A.'s brain centers...")
    for model in CORE_MODELS:
        target_dir = os.path.join(MODELS_DIR, model["role"])
        print(f"📥 VACUUM: Pulling {model['repo']} into {target_dir}...")
        try:
            snapshot_download(
                repo_id=model["repo"],
                local_dir=target_dir,
                local_dir_use_symlinks=False,
                ignore_patterns=["*.msgpack", "*.h5", "*.ot"],
            )
            print(f"✅ Download complete for {model['repo']}")
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to download {model['repo']}: {exc}")
    print("✅ MODALS: Oracle, Architect, and Surveyor nodes are online.")


def _clone_tool(repo_url: str, destination: str) -> None:
    """Clone a repository into destination if it is not already present."""
    if os.path.exists(destination):
        print(f"⚠️  Skipping {repo_url}; destination exists at {destination}")
        return

    print(f"🔧 Cloning {repo_url} into {destination}...")
    try:
        subprocess.run(
            ["git", "clone", repo_url, destination],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        print(f"✅ Cloned {repo_url}")
    except subprocess.CalledProcessError as exc:
        print(f"❌ Failed to clone {repo_url}: {exc.stdout}")


def ingest_tools() -> None:
    """Clone agentic tooling into /data/tools."""
    print("🛠️  ASSEMBLY: Installing Master Tools...")
    for tool_url in AGENTIC_TOOLS:
        tool_name = tool_url.rstrip("/").split("/")[-1]
        destination = os.path.join(TOOLS_DIR, tool_name)
        _clone_tool(tool_url, destination)
    print("✅ TOOLS: Agentic frameworks secured in /data/tools.")


def main() -> None:
    ensure_directories()
    ignite_modals()
    ingest_tools()


if __name__ == "__main__":
    main()
