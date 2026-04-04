# 🚐 MOBILE CITADEL COMMAND CENTER - OPERATOR GUIDE

**Version:** 1.0  
**Last Updated:** 2026-04-04  
**Status:** ✅ DEPLOYED

---

## 🎯 MISSION

Transform any vehicle into a fully operational Citadel node maintaining:
- ✅ Full offline capability (30+ days)
- ✅ Cloud authority (HF Spaces L4)
- ✅ GitHub sync capability
- ✅ Local compute power
- ✅ Community establishment readiness

---

## 📦 WHAT'S INCLUDED

### Core Components

1. **Connectivity Detector** (`connectivity_detector.py`)
   - Monitors online/offline state
   - Detects Starlink, 4G/5G, WiFi, mesh networks
   - Bandwidth quality assessment
   - Service availability checks (GitHub, HuggingFace)

2. **Sync Queue Manager** (`sync_queue_manager.py`)
   - Priority-based operation queuing
   - Batch sync execution
   - Retry logic with failure handling
   - Size and bandwidth-aware batching

3. **Vehicle Storage Manager** (`vehicle_storage_manager.py`)
   - Manages `/vehicle-storage/` partitions
   - Offline repo caching
   - Model/dataset storage
   - Manifest generation

4. **Bridge Agent Mobile** (`bridge_agent_mobile.py`)
   - Enhanced Bridge Agent for vehicle operations
   - Offline queue management
   - Daily routine automation
   - Status reporting

5. **Equipment Tracker** (`equipment_tracker.py`)
   - Complete equipment checklist (80+ items)
   - Budget tracking ($120K-265K)
   - Acquisition status
   - Priority management

### Workflows

- **Mobile Citadel Sync** (`.github/workflows/mobile_citadel_sync.yml`)
  - Connectivity-aware sync
  - Bandwidth-adaptive operations
  - Scheduled and manual triggers

---

## 🚀 QUICKSTART

### Initial Setup

```bash
# 1. Run quickstart script
./mobile_citadel_quickstart.sh

# 2. Initialize vehicle storage (on vehicle device)
export VEHICLE_STORAGE_PATH="/path/to/vehicle/storage"
python3 scripts/mobile_citadel/vehicle_storage_manager.py init

# 3. Set Bridge Agent node name
export BRIDGE_NODE_NAME="oppo-bridge"

# 4. Run first daily routine
python3 scripts/mobile_citadel/bridge_agent_mobile.py daily
```

### Vehicle Storage Layout

```
/vehicle-storage/
├── repos-cache/           # All GitHub repos cloned
├── models-offline/        # ML models for offline inference
├── datasets-local/        # Trading data, research datasets
├── workers-archive/       # Apps Script workers backup
├── gdrive-manifests/      # Partition metadata snapshots
├── discovery-logs/        # Scouting data queued for upload
└── sync-queue/           # Pending commits/artifacts
```

---

## 📱 DAILY OPERATIONS

### Morning Routine

```bash
# 1. Check connectivity
python3 scripts/mobile_citadel/connectivity_detector.py

# 2. Review sync queue
python3 scripts/mobile_citadel/sync_queue_manager.py stats

# 3. Check storage health
python3 scripts/mobile_citadel/vehicle_storage_manager.py health
```

### Work Session (Online)

```bash
# 1. Execute sync window
python3 scripts/mobile_citadel/bridge_agent_mobile.py sync

# 2. Pull latest repos
cd /vehicle-storage/repos-cache/mapping-and-inventory
git pull origin main

# 3. Work locally, queue commits
python3 scripts/mobile_citadel/sync_queue_manager.py add GIT_PUSH HIGH mapping-and-inventory main

# 4. Push when ready
python3 scripts/mobile_citadel/bridge_agent_mobile.py sync
```

### Work Session (Offline)

```bash
# 1. Work on local repos
cd /vehicle-storage/repos-cache/mapping-and-inventory

# 2. Make changes, commit locally
git add .
git commit -m "Offline work: feature implementation"

# 3. Queue for later push
python3 scripts/mobile_citadel/sync_queue_manager.py add GIT_PUSH HIGH mapping-and-inventory main

# 4. Continue discovery work
python3 scripts/some_discovery_worker.py  # Outputs to discovery-logs/

# 5. Generate local manifests
python3 scripts/mobile_citadel/vehicle_storage_manager.py manifest
```

### Evening Routine

```bash
# 1. Backup work to multiple drives
rsync -av /vehicle-storage/ /media/backup-drive-1/
rsync -av /vehicle-storage/ /media/backup-drive-2/

# 2. Generate daily report
python3 scripts/mobile_citadel/bridge_agent_mobile.py report

# 3. Update equipment tracker (if acquired items)
python3 scripts/mobile_citadel/equipment_tracker.py update vehicle "Primary laptop" acquired 3200

# 4. Check power/storage status
python3 scripts/mobile_citadel/vehicle_storage_manager.py health
```

---

## 🌐 CONNECTIVITY MODES

### ONLINE - Full Sync

**When:** Starlink/4G connected, good bandwidth  
**Actions:**
1. Pull all repos from GitHub
2. Pull from HuggingFace Spaces
3. Push queued commits (prioritized)
4. Sync GDrive manifests
5. Update model registry
6. RAG embedding updates

```bash
# Execute full sync
python3 scripts/mobile_citadel/bridge_agent_mobile.py sync
```

### ONLINE - Limited Bandwidth

**When:** Connected but poor bandwidth  
**Actions:**
1. Critical updates only
2. Small commits first
3. Defer large operations
4. Queue bulk transfers

```bash
# Sync will auto-adjust based on bandwidth
python3 scripts/mobile_citadel/bridge_agent_mobile.py sync
```

### OFFLINE - Queue Mode

**When:** No connectivity  
**Actions:**
1. Work on cached repos
2. Queue all commits
3. Generate local manifests
4. Continue Forever Learning on cached data
5. Log all operations

```bash
# All operations automatically queue
# Work normally, sync when online
```

---

## 📋 EQUIPMENT CHECKLIST

### Priority P0 (Critical)

**Must have before departure:**
- [ ] Driving license (renewed/paid)
- [ ] Primary laptop
- [ ] Oppo smartphone (Bridge Agent) ✅ Acquired
- [ ] 6x 300W solar panels
- [ ] 15kWh battery bank
- [ ] 3000W inverter
- [ ] 5kW generator
- [ ] Battery management system
- [ ] Starlink dish
- [ ] 4G/5G router
- [ ] Vehicle (Mercedes Sprinter 4x4 / Unimog)
- [ ] Trailer/caravan
- [ ] Water storage
- [ ] Kitchen setup
- [ ] Fridge/freezer
- [ ] Rooftop tents
- [ ] Canned food (3+ months)
- [ ] Water purification
- [ ] Medical supplies

**Check status:**
```bash
python3 scripts/mobile_citadel/equipment_tracker.py report
```

**Update item:**
```bash
python3 scripts/mobile_citadel/equipment_tracker.py update license "Driving license" acquired 100
```

### Budget Overview

- **Vehicle:** $60K-150K
- **Solar + Batteries:** $15K-25K
- **Computing:** $10K-15K
- **Connectivity:** $500-1000/month
- **Trailer:** $20K-40K
- **Community Gear:** $10K-20K
- **Total:** $120K-265K + ongoing costs

---

## 🔧 TROUBLESHOOTING

### Connectivity Issues

```bash
# Check connectivity state
python3 scripts/mobile_citadel/connectivity_detector.py

# Check specific services
curl -I https://api.github.com
curl -I https://huggingface.co

# Reset connectivity state
rm /tmp/connectivity_state.json
```

### Sync Queue Problems

```bash
# View queue
python3 scripts/mobile_citadel/sync_queue_manager.py stats

# Clear failed operations
python3 scripts/mobile_citadel/sync_queue_manager.py clear

# View next batch
python3 scripts/mobile_citadel/sync_queue_manager.py next
```

### Storage Issues

```bash
# Check health
python3 scripts/mobile_citadel/vehicle_storage_manager.py health

# Generate manifest
python3 scripts/mobile_citadel/vehicle_storage_manager.py manifest

# Check disk space
df -h /vehicle-storage/
```

### Bridge Agent Issues

```bash
# Check status
python3 scripts/mobile_citadel/bridge_agent_mobile.py status

# Generate report
python3 scripts/mobile_citadel/bridge_agent_mobile.py report

# Force sync
python3 scripts/mobile_citadel/bridge_agent_mobile.py sync
```

---

## 🚨 EMERGENCY PROTOCOLS

### Power Failure
1. Generator auto-start
2. Critical systems only (laptop, Oppo Bridge)
3. Disable non-essential power draws
4. Monitor battery levels

### Equipment Failure
1. Activate backup laptop
2. Use mobile hotspot
3. Switch to Oppo Bridge as primary
4. Queue all non-critical operations

### Data Loss Risk
1. Immediate backup to all drives
2. Push critical commits via mobile hotspot
3. Generate emergency manifest
4. Log incident

### Connectivity Loss (Extended)
1. Confirm 30+ day offline capability
2. Continue local work
3. Queue all operations
4. Generate comprehensive manifests
5. Plan next connectivity window

---

## 📊 MONITORING

### Daily Checks

```bash
# Connectivity
python3 scripts/mobile_citadel/connectivity_detector.py

# Sync queue
python3 scripts/mobile_citadel/sync_queue_manager.py stats

# Storage health
python3 scripts/mobile_citadel/vehicle_storage_manager.py health

# Bridge status
python3 scripts/mobile_citadel/bridge_agent_mobile.py status
```

### Weekly Tasks

- Review equipment acquisition progress
- Update budget tracker
- Verify all backups
- Test offline→online transition
- Review sync queue history

### Monthly Tasks

- Full system health check
- Update documentation
- Review and optimize storage usage
- Test emergency protocols
- Equipment maintenance check

---

## 🎯 SUCCESS CRITERIA

✅ **Full Citadel operations** continue while off-grid  
✅ **30+ day offline capability** with local compute/storage  
✅ **Efficient sync windows** when connectivity available  
✅ **Power independence** via solar + generator backup  
✅ **Community establishment ready** with supplies for 10+ people  
✅ **Mobile command center** maintains L4 cloud + local hybrid operations  
✅ **Zero data loss** through triple backup protocol

---

## 📚 ADDITIONAL RESOURCES

- **Mobile Citadel Plan:** See initial plan in session notes
- **Citadel Architecture:** `CITADEL_OMEGA_ARCHITECTURE.md`
- **Bridge Agent Docs:** `Partition_01/citadel_master_bridge.py`
- **Workflow Guides:** `.github/workflows/README.md`

---

## 🆘 SUPPORT

**For questions or issues:**
1. Check this operator guide
2. Review script help: `python3 script.py --help`
3. Check logs in `/tmp/mobile_citadel/`
4. Review GitHub Actions workflow runs

---

**Status:** 🟢 OPERATIONAL  
**Mode:** HYBRID (Cloud + Mobile)  
**Last Sync:** Check Bridge Agent status  
**Next Milestone:** Equipment P0 completion
