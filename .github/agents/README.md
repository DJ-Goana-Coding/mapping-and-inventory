# Citadel Omega Agent Identities

This directory contains the **Sovereign Ingestion Protocol** agent identity files that define the behavior and responsibilities of L4 cores in the Citadel ecosystem.

## Agent Registry

### 🧭 Surveyor Agent (`surveyor.agent.md`)
- **Location:** This repository (Mapping-and-Inventory)
- **Role:** Global intelligence atlas maintainer
- **Schedule:** Every 6 hours or manual trigger
- **Outputs:** `master_intelligence_map.txt`, `district_status_report.json`

### 🧠 Oracle Agent (`oracle.agent.md`)
- **Location:** TIA-ARCHITECT-CORE repository
- **Role:** Intelligence reasoning and coherence layer
- **Schedule:** Every hour
- **Outputs:** `tia_diff_report.json`

### 🔧 Bridge Agent (`bridge.agent.md`)
- **Location:** Oppo Node (mobile)
- **Role:** Mobile-to-Citadel bridge
- **Outputs:** `TREE.md`, `INVENTORY.json`, `SCAFFOLD.md`

## Registry Files

- **`districts.json`** - Master registry of all Districts and external nodes
- **`district_status_report.json`** - Health and status of all registered entities

## The 777.1122 Alignment

These agent identities enable the system to transition from:

**Push-only → Push + Pull → Self-observing mesh**

Each agent now knows:
- **who they are**
- **what they watch**
- **what they harvest**
- **what they maintain**
- **what they report**

This is the foundation of a **self-maintaining** architecture.

---

*Deployed: 2026-04-02*  
*Protocol Version: 1.0.0*  
*Status: Active*
