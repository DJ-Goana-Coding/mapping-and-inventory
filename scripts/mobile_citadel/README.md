# 🚐 Mobile Citadel Scripts

**Vehicle-based Citadel Operations Infrastructure**

This directory contains scripts for operating a Mobile Citadel Command Center from a vehicle platform. Enables full Citadel operations while traveling off-grid with intermittent connectivity.

---

## 📦 Components

### 1. Connectivity Detector (`connectivity_detector.py`)
Monitors network state and detects connectivity tiers.

**Features:**
- Multi-tier detection (Starlink, 4G/5G, WiFi, mesh)
- Service availability checks (GitHub, HuggingFace)
- Bandwidth quality assessment
- State transition detection

**Usage:**
```bash
python3 connectivity_detector.py
```

**Outputs:**
- Console report with recommendations
- `/tmp/connectivity_state.json` - Current state
- `/tmp/connectivity_check.json` - JSON for scripts
- Exit code: 0 (online), 1 (offline)

---

### 2. Sync Queue Manager (`sync_queue_manager.py`)
Manages offline/online sync operations with priority queuing.

**Features:**
- Priority-based queuing (CRITICAL > HIGH > NORMAL > LOW > BULK)
- Operation types: git_pull, git_push, hf_pull, hf_push, gdrive_sync, model_download
- Bandwidth-aware batching
- Retry logic with failure handling
- Size estimation and limits

**Usage:**
```bash
# Show queue stats
python3 sync_queue_manager.py stats

# Add operation
python3 sync_queue_manager.py add GIT_PUSH HIGH mapping-and-inventory main

# View next batch
python3 sync_queue_manager.py next

# Clear completed
python3 sync_queue_manager.py clear
```

**Storage:**
- `/tmp/mobile_citadel/sync_queue/queue.json` - Active queue
- `/tmp/mobile_citadel/sync_queue/history.json` - Completed operations (last 1000)

---

### 3. Vehicle Storage Manager (`vehicle_storage_manager.py`)
Manages vehicle-based storage partitions for offline operations.

**Features:**
- Partition initialization and management
- Storage usage statistics
- Health monitoring
- Manifest generation
- Repo caching
- Discovery data queuing

**Partition Layout:**
```
/vehicle-storage/
├── repos-cache/           # Cloned repos for offline work
├── models-offline/        # ML models
├── datasets-local/        # Trading/research data
├── workers-archive/       # Apps Script workers
├── gdrive-manifests/      # GDrive metadata
├── discovery-logs/        # Queued discoveries
└── sync-queue/           # Pending artifacts
```

**Usage:**
```bash
# Initialize storage
export VEHICLE_STORAGE_PATH="/path/to/storage"
python3 vehicle_storage_manager.py init

# Generate report
python3 vehicle_storage_manager.py report

# Check health
python3 vehicle_storage_manager.py health

# Generate manifest
python3 vehicle_storage_manager.py manifest
```

---

### 4. Equipment Tracker (`equipment_tracker.py`)
Tracks equipment acquisition and budget for mobile operations.

**Features:**
- Complete equipment checklist (80+ items)
- Budget tracking with estimates and actuals
- Status tracking (not_started, researching, quoted, ordered, acquired, installed)
- Priority levels (P0, P1, P2)
- Category breakdown (computing, power, connectivity, vehicle, community, license)
- Monthly/yearly cost tracking

**Usage:**
```bash
# Show checklist report
python3 equipment_tracker.py report

# Show budget summary
python3 equipment_tracker.py budget

# Update item status
python3 equipment_tracker.py update vehicle "Primary laptop" acquired 3200
python3 equipment_tracker.py update license "Driving license" acquired 100
```

**Categories:**
- **Computing:** Laptops, phones, tablets, storage (17 items, ~$10-15K)
- **Power:** Solar panels, batteries, inverters (8 items, ~$15-25K)
- **Connectivity:** Starlink, 4G/5G, mesh (7 items, ~$2K + $270/month)
- **Vehicle:** Vehicle, trailer, motorbikes (11 items, ~$140-190K)
- **Community:** Supplies for establishing off-grid community (11 items, ~$13K)
- **License:** Licenses, insurance, registration (7 items, ~$6K + $5.3K/year)

---

### 5. Bridge Agent Mobile (`bridge_agent_mobile.py`)
Enhanced Bridge Agent orchestrator for mobile/vehicle operations.

**Features:**
- Integrates all mobile citadel components
- System status monitoring
- Sync window execution
- Daily routine automation
- Comprehensive reporting
- Offline queue management

**Usage:**
```bash
# System status (JSON)
python3 bridge_agent_mobile.py status

# Execute sync window
python3 bridge_agent_mobile.py sync

# Daily routine
python3 bridge_agent_mobile.py daily

# Generate report
python3 bridge_agent_mobile.py report
```

**Environment Variables:**
- `BRIDGE_NODE_NAME` - Node identifier (default: "oppo-bridge")
- `VEHICLE_STORAGE_PATH` - Storage base path (default: "/tmp/vehicle-storage")

---

## 🚀 Quickstart

```bash
# Run from repo root
./mobile_citadel_quickstart.sh
```

This will:
1. Check Python availability
2. Make scripts executable
3. Initialize vehicle storage
4. Check connectivity
5. Show equipment checklist
6. Show sync queue status
7. Run daily routine

---

## 📊 Operating Modes

### ONLINE_READY
- Connectivity available
- Sync queue empty
- Normal operations

### ONLINE_SYNCING
- Connectivity available
- Processing sync queue
- Active sync operations

### OFFLINE_QUEUE
- No connectivity
- Queue mode active
- All operations queued

---

## 🔄 Sync Priority Levels

1. **CRITICAL** - Security updates, emergency commits
2. **HIGH** - Code changes, bug fixes
3. **NORMAL** - Features, documentation
4. **LOW** - Discovery data, logs
5. **BULK** - Large datasets, models

---

## 🌐 Connectivity Tiers

1. **Starlink** - Primary off-grid satellite link
2. **Cellular** - 4G/5G with multi-SIM redundancy
3. **WiFi** - When near infrastructure
4. **Mesh** - Local mesh network

---

## 📅 Daily Routine

### Morning
1. Check connectivity
2. Review sync queue
3. Check storage health
4. Deploy portable solar panels if needed

### Work Session (Online)
1. Execute sync window
2. Pull latest from GitHub
3. Work locally
4. Queue commits
5. Push when ready

### Work Session (Offline)
1. Work on cached repos
2. Commit locally
3. Queue for later push
4. Continue discovery work
5. Generate manifests

### Evening
1. Backup to multiple drives
2. Generate daily report
3. Update equipment tracker
4. Monitor power/storage

---

## 🎯 Success Criteria

✅ 30+ day offline capability  
✅ Efficient sync windows  
✅ Zero data loss (triple backup)  
✅ Full Citadel operations  
✅ Power independence  
✅ Community establishment ready

---

## 📚 Documentation

- **Operator Guide:** `../MOBILE_CITADEL_OPERATOR_GUIDE.md`
- **Plan:** See initial Mobile Citadel Plan
- **Workflows:** `../.github/workflows/mobile_citadel_sync.yml`

---

**Status:** 🟢 OPERATIONAL  
**Version:** 1.0  
**Last Updated:** 2026-04-04
