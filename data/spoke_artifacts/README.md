# Spoke Artifacts Directory

This directory stores artifacts synchronized from spoke repositories.

## Structure

```
spoke_artifacts/
├── repo-name-1/
│   ├── TREE.md
│   ├── INVENTORY.json
│   ├── SCAFFOLD.md
│   ├── README.md
│   ├── system_manifest.json
│   └── sync_metadata.json
├── repo-name-2/
│   └── ...
└── repo-name-N/
    └── ...
```

## Sync Metadata Format

Each spoke directory contains a `sync_metadata.json` file:

```json
{
  "spoke_name": "repository-name",
  "spoke_url": "https://github.com/DJ-Goana-Coding/repository-name",
  "sync_timestamp": "2026-04-04T20:00:00Z",
  "commit_sha": "abc123...",
  "artifacts_fetched": 5,
  "sync_method": "repository_dispatch"
}
```

## Artifacts Collected

Standard artifacts synchronized from each spoke:

1. **TREE.md** - Repository structure tree
2. **INVENTORY.json** - Complete inventory manifest
3. **SCAFFOLD.md** - Architecture scaffold
4. **README.md** - Repository documentation
5. **system_manifest.json** - System configuration

## Automatic Updates

Artifacts are automatically updated when:
- Spoke repository pushes to main branch
- Every 6 hours (scheduled sync)
- Manual workflow dispatch from spoke

## Registry

All spoke sync activity is tracked in:
- `../spoke_sync_registry.json`

---

**Authority:** Citadel Architect v25.0.OMNI+
