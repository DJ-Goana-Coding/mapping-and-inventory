---
title: VAMGUARD TITAN
emoji: 🛡️
colorFrom: red
colorTo: orange
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: true
license: mit
duplicated_from: DJ-Goanna-Coding/Mapping-and-Inventory
suggested_hardware: l4-large
suggested_storage: persistent
---

# 🛡️ VAMGUARD TITAN

**Security & Worker Coordination Hub for the Citadel Mesh**

## Hardware Configuration

This Space runs on **NVIDIA L4 GPU** (24GB VRAM) for:
- ML model inference
- RAG embedding generation
- Security threat detection
- Worker coordination
- Real-time monitoring

### GPU Acceleration

The L4 GPU enables:
- **Fast embedding generation** for TIA code indexing
- **ML-powered security scanning** for threat detection
- **High-throughput data processing** for laptop/GDrive harvesting
- **Real-time inference** for worker health prediction

### Alternative Hardware

- **L4 (24GB)** - Recommended for full operations
- **T4 (16GB)** - Adequate for basic operations
- **A10G (24GB)** - Alternative high-performance option

## Features

### 🛡️ Sentinel Guard
Active security monitoring across all Citadel nodes

### 🤖 Worker Coordination
Orchestrate Apps Script, Python, and Node.js workers

### 🌉 Bridge Network
Secure connections to GitHub, HuggingFace, and GDrive

### 💻 Data Harvesting
Flow data from laptop and GDrive to central storage

### 🎯 TIA Code Discovery
Find and sync all TIA-related code to TIA-ARCHITECT-CORE

## Architecture

```
VAMGUARD-TITAN (L4 GPU)
├── Sentinel Guard (Security)
├── Worker Coordinator (Orchestration)
├── Mesh Connector (Bridges)
├── Laptop Harvester (Data ingestion)
├── GDrive Harvester (Metadata extraction)
├── TIA Code Finder (Discovery)
└── TIA Sync Worker (Push to TIA-ARCHITECT-CORE)
```

## Integration

### Citadel Mesh
- **D12 ZENITH_VIEW** - Reports security status
- **D02 TIA_VAULT** - Coordinates with Oracle
- **Mapping Hub** - Registers workers and artifacts
- **TIA-ARCHITECT-CORE** - Receives discovered TIA code

### Data Flow

```
Laptop ─────┐
            ├──> Mapping-and-Inventory-storage ──> TIA-ARCHITECT-CORE
GDrive ─────┘                (L4 Processing)
```

## Deployment

This Space automatically:
1. Pulls from GitHub every 6 hours
2. Runs security scans
3. Checks worker health
4. Tests bridge connections
5. Harvests data from laptop/GDrive
6. Discovers TIA code
7. Syncs to TIA-ARCHITECT-CORE

## Environment Variables

Required secrets (set in Space settings):
- `GITHUB_TOKEN` - GitHub API access
- `HF_TOKEN` - HuggingFace authentication
- `RCLONE_CONFIG_DATA` - GDrive access configuration
- `GOOGLE_SHEETS_CREDENTIALS` - Worker reporting
- `LAPTOP_SOURCE_PATH` - Laptop data source

## Sovereign Guardrails

- ✅ All credentials via environment variables
- ✅ Relative paths only
- ✅ Encrypted data transfer
- ✅ Comprehensive audit logging
- ✅ Double-N Rift aware (GitHub: DJ-Goana-Coding, HF: DJ-Goanna-Coding)

## Forever Learning Cycle

VAMGUARD TITAN follows the Forever Learning protocol:
1. Pull → 2. Validate → 3. Embed → 4. Store → 5. Update RAG → 6. Rebuild Mesh → 7. Version Bump

---

**Status:** ACTIVE | **Authority:** Security Override | **Tier:** L3
