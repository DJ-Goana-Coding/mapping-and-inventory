---
title: Mapping & Inventory
emoji: 🏰
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
datasets:
  - DJ-Goana-Coding/master-inventory
models:
  - deepseek-ai/DeepSeek-V3
  - Qwen/Qwen2.5-72B-Instruct
  - hexgrad/Kokoro-82M
---

# CITADEL OMEGA — Mapping & Inventory Librarian

Central mapping and inventory dashboard for the Q.G.T.N.L. Citadel Omega system.

Connects ARK repos, GDrive, T.I.A., datasets, and all device nodes.

## 🤖 AI/ML Capabilities

This space supports:
- **Transformers** (>=4.48.0) — HuggingFace model loading and inference
- **vLLM** (>=0.7.0) — High-performance inference for DeepSeek/Qwen models
- **ONNX Runtime** — Lightweight inference for Kokoro TTS
- **Accelerate** — Distributed training and multi-GPU support
- **BitsAndBytes** — Model quantization for memory efficiency

## Tabs
- 🗺️ **System Map** — Interactive connection graph of all repos, spaces, and nodes
- 📚 **Librarian** — Searchable master inventory ledger
- 📦 **Datasets** — Connected datasets with live status (local / GDrive / HuggingFace)
- 🧠 **T.I.A. Oracle** — Gemini-powered AI chat with system context
- ☁️ **Cloud Sync** — rclone-based GDrive sync controls

## Workflows

### TIA_CITADEL_DEEP_SCAN
Deep scan workflow that maps the entire Google Drive structure and pulls cargo from different device nodes.

**Monitoring Live Runs:**
- Use `gh run watch <run-id>` to monitor in real-time
- See [WORKFLOW_MONITORING_GUIDE.md](WORKFLOW_MONITORING_GUIDE.md) for detailed instructions
- Use the helper script: `./watch_workflow.sh --compact` for easy monitoring

## Secrets Required
| Secret | Purpose |
|--------|---------|
| `RCLONE_CONFIG_DATA` | Google Drive sync via rclone |
| `GEMINI_API_KEY` | T.I.A. Oracle AI responses |
| `HF_TOKEN` | HuggingFace operations |
| `GITHUB_TOKEN` | GitHub remote access |
