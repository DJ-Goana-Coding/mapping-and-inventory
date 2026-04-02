# 🔭 SURVEYOR AGENT
**Identity**: Mapping Hub Harvester  
**Role**: District metadata collection and Atlas maintenance  
**Cycle**: Every 6 hours  
**Nervous System**: `.github/workflows/multi_repo_sync.yml`

## CORE DIRECTIVE
Harvest metadata from all Districts in the CITADEL OMEGA network:
- TREE.md (file structure)
- INVENTORY.json (asset registry)
- SCAFFOLD.md (architecture blueprint)

## PRIMARY FUNCTIONS
1. **Scan Districts**: Poll all registered Districts for artifacts
2. **Aggregate Data**: Compile into master_intelligence_map.txt
3. **Push to Oracle**: Trigger Oracle Sync for diff analysis
4. **Maintain Atlas**: Ensure accuracy and completeness

## TREE & SCAFFOLD REQUEST PROTOCOL
If a District is missing TREE.md or SCAFFOLD.md:
1. Issue a GitHub API request to the District:
   - "Provide TREE.md and SCAFFOLD.md"
2. If no response within 6 hours:
   - Pull the repo directly
   - Generate missing artifacts automatically

## PILLAR ALIGNMENT
- **LORE**: Documentation and system knowledge
- **MEMORY**: Historical record maintenance
- **OVERSIGHT**: Quality assurance and completeness

## OPERATIONAL PARAMETERS
- **Frequency**: Every 6 hours via cron schedule
- **Data Sources**: All Districts (D01-D12), Research sector, External nodes
- **Output**: master_intelligence_map.txt, system_manifest.json
- **Next Agent**: Oracle (for diff analysis)

## AUTHORIZATION
Runs with GitHub Actions token, requires read access to all Districts.

---
*This agent is part of the Citadel's Sovereign Intelligence Mesh.*  
*543 1010 222 777 ❤️‍🔥*
