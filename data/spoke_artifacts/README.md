# 📦 Spoke Artifacts Directory

This directory contains artifacts synced from spoke repositories to the mapping-and-inventory hub.

## Purpose

The spoke artifacts system enables centralized metadata aggregation from all repositories in the DJ-Goana-Coding organization.

## Structure

```
data/spoke_artifacts/
├── README.md (this file)
├── CITADEL_OMEGA/          # Trading intelligence hub
│   ├── TREE.md
│   ├── INVENTORY.json
│   ├── SCAFFOLD.md
│   ├── system_manifest.json
│   ├── README.md
│   └── sync_metadata.json
├── TIA-ARCHITECT-CORE/     # Oracle and reasoning hub
├── ark-core/               # Physical node bridge
└── [other repositories]/   # Additional spokes
```

## How Artifacts Get Here

1. **Spoke repositories** have `.github/workflows/spoke-to-hub-sync.yml`
2. **Workflow triggers** on push to main + every 6 hours
3. **Workflow collects** artifacts (TREE.md, INVENTORY.json, etc.)
4. **Workflow sends** `repository_dispatch` event to mapping-and-inventory
5. **Hub receives** event via `.github/workflows/spoke_sync_receiver.yml`
6. **Hub downloads** artifacts via GitHub API
7. **Hub commits** artifacts to this directory
8. **Hub updates** `data/spoke_sync_registry.json`

## Registry

Central registry of all synced spokes: `data/spoke_sync_registry.json`

View registry:
```bash
cat data/spoke_sync_registry.json | jq .
```

View specific spoke:
```bash
cat data/spoke_sync_registry.json | jq '.spokes["CITADEL_OMEGA"]'
```

## CITADEL_OMEGA

**Status:** Connected  
**Agent Config:** `.github/agents/citadel-omega.agent.md`  
**Connection Guide:** `CITADEL_OMEGA_CONNECTION_GUIDE.md`  
**Verification:** `./verify_citadel_omega_connection.sh`

CITADEL_OMEGA is the unified trading intelligence hub containing:
- omega_trader (trading operations)
- omega_bots (AI trading agents)
- omega_scout (API connectors & security)
- omega_archive (strategy library)
- ML models and datasets
- Trading libraries and tools

## Adding New Spokes

To connect a new repository to the hub:

```bash
# Option 1: Automated deployment
export GITHUB_TOKEN=ghp_your_token
python scripts/deploy_workflows_to_spokes.py --repos REPO_NAME

# Option 2: Manual setup
# Copy workflow templates from .github/workflow-templates/
# to the spoke repository's .github/workflows/
```

## Monitoring

View sync history:
```bash
git log --oneline -- data/spoke_artifacts/
```

Check workflow runs:
```bash
gh run list --workflow spoke_sync_receiver.yml
```

## Documentation

- `REPOSITORY_CONNECTION_GUIDE.md` - Complete hub sync system
- `CITADEL_OMEGA_CONNECTION_GUIDE.md` - CITADEL_OMEGA specific guide
- `.github/workflow-templates/README.md` - Workflow templates

---

**Authority:** Citadel Architect v25.0.OMNI+  
**Status:** Operational
