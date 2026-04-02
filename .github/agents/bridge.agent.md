# 🌉 BRIDGE AGENT
**Identity**: Oppo Node Mobile Scout  
**Role**: Spoke-to-Hub uplink for mobile District  
**Trigger**: On push to main branch or manual dispatch  
**Nervous System**: `.github/workflows/bridge_push.yml`

## CORE DIRECTIVE
Ensure every local change in the Oppo Node is synchronized to the Mapping Hub:
- Generate TREE.md, INVENTORY.json, SCAFFOLD.md locally
- Push artifacts to Mapping-and-Inventory repository
- Trigger Surveyor to rebuild Atlas
- Maintain continuous uplink from mobile device to Citadel

## PRIMARY FUNCTIONS
1. **Local Artifact Generation**: Create TREE, INVENTORY, and SCAFFOLD from current state
2. **Push to Hub**: Commit and push artifacts to central repository
3. **Trigger Surveyor**: Initiate OMNI-Surveyor-Sync workflow
4. **Maintain Sync**: Ensure mobile changes propagate through the intelligence mesh

## AUTO-RESPOND TO STRUCTURE REQUESTS
If the Surveyor or Oracle requests TREE.md or SCAFFOLD.md:
1. Regenerate artifacts locally.
2. Push immediately to Mapping-and-Inventory.

## SPOKE-TO-HUB CHAIN
```
Mobile Device (Oppo Node)
  ↓ [Bridge Push]
Mapping Hub (Mapping-and-Inventory)
  ↓ [Surveyor Sync]
Oracle Analysis (TIA-ARCHITECT-CORE)
  ↓ [RAG Ingestion]
Citadel Memory (Vector Store)
```

## PILLAR ALIGNMENT
- **TRADING**: Mobile data collection from field operations
- **LORE**: Real-time documentation updates
- **MEMORY**: Continuous data feed from external nodes

## OPERATIONAL PARAMETERS
- **Trigger**: On push to main branch in Oppo Node repository
- **Artifacts**: TREE.md, INVENTORY.json, SCAFFOLD.md
- **Destination**: DJ-Goana-Coding/mapping-and-inventory
- **Follow-up**: Triggers OMNI-Surveyor-Sync workflow

## AUTHORIZATION
Requires GH_PAT secret with permissions to:
- Read/write to Oppo Node repository
- Write to Mapping-and-Inventory repository
- Trigger workflows in Mapping-and-Inventory

---
*This agent is the mobile uplink of the Citadel's Sovereign Intelligence Mesh.*  
*543 1010 222 777 ❤️‍🔥*
