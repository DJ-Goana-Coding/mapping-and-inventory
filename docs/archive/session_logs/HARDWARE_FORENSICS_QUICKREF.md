# 🔬 HARDWARE FORENSICS QUICK REFERENCE

**Find and extract hidden SSD data + analyze RAM chips**

---

## 🎯 PRIORITY: Hidden SSD Extraction

### Quick Start (Auto Mode)
```bash
# On your laptop - this will automatically find, mount, and extract the SSD
python3 scripts/hardware_forensics.py --mount-hidden --extract-all
```

### What It Does

1. **Detects ALL storage devices** (including hidden/unmounted)
2. **Finds the hidden SSD** that's not showing up
3. **Mounts it** (brings offline disk online, assigns drive letter)
4. **Extracts ALL data** from it to `data/Mapping-and-Inventory-storage/hidden_ssd/`
5. **Analyzes RAM chips** (both sticks, including the old one)

---

## 📊 Detection Methods

### Windows
- **WMIC Physical Disks** - All physical drives
- **WMIC Volumes** - Including hidden volumes without drive letters
- **PowerShell Get-Disk** - Includes OFFLINE disks

### Linux
- **lsblk** - Block devices including unmounted
- **/proc/partitions** - All partitions

### macOS
- **diskutil** - All disks including unmounted

---

## 🚨 Hidden SSD Indicators

The script looks for:
- Drives without drive letters (Windows)
- Offline disks (Windows)
- Unmounted partitions (Linux/macOS)
- SSD keywords: 'ssd', 'solid', 'nvme', 'samsung', 'crucial', 'kingston'

---

## 💾 SSD Mounting Process

### Windows
1. Detects offline disk number
2. Runs: `Set-Disk -Number X -IsOffline $false`
3. Assigns drive letter: `Add-PartitionAccessPath -AssignDriveLetter`
4. Returns drive path (e.g., `E:\`)

### Linux
1. Creates mount point: `/mnt/hidden_ssd_TIMESTAMP`
2. Runs: `sudo mount /dev/sdX /mnt/hidden_ssd_TIMESTAMP`
3. Returns mount point

---

## 📦 Data Extraction

Once mounted, the script:
1. Copies **ALL files** from SSD to `data/Mapping-and-Inventory-storage/hidden_ssd/`
2. Preserves directory structure
3. Skips system folders (`$RECYCLE.BIN`, `System Volume Information`)
4. Generates index with:
   - Total files count
   - Total size in GB
   - File type breakdown
   - Directory structure

Output: `data/hardware_forensics/hidden_ssd_index.json`

---

## 🧠 RAM Analysis

### What It Detects
- Number of RAM chips (both sticks)
- Manufacturer
- Part number
- Serial number
- Capacity (per chip and total)

### About RAM Data Recovery
- **RAM is volatile** - data is lost when power is removed
- **Cold boot attacks** can recover data within ~30 seconds of power loss
- **Data remanence** can persist briefly but requires specialized tools
- **We catalog the chips** for inventory and identification

### Old RAM Stick
The script will detect if there are 2 RAM sticks and catalog both:
- Current system RAM
- Old RAM from another computer (if still installed)

**Note:** Extracting residual data from old RAM requires:
- Specialized hardware (JTAG, chip-off forensics)
- Or immediate cold boot attack (within 30 seconds of removal)
- Since the old RAM has been depowered, residual data is likely gone
- We can only catalog its specifications

---

## 📁 Output Files

### Forensics Report
`data/hardware_forensics/hardware_forensics_TIMESTAMP.json`

Contains:
- All detected drives (mounted and unmounted)
- Hidden SSD identification
- RAM chip specifications
- Mounting status
- Extraction status

### SSD Data Index
`data/hardware_forensics/hidden_ssd_index.json`

Contains:
- Total files extracted
- Total size in GB
- File type breakdown
- Timestamp

### Extracted SSD Data
`data/Mapping-and-Inventory-storage/hidden_ssd/`

Contains:
- **ALL files** from the hidden SSD
- Original directory structure preserved
- All file types included

---

## 🎯 Manual Mode (Step-by-Step)

### Step 1: Detect Only
```bash
python3 scripts/hardware_forensics.py
```
This scans and reports all devices without making changes.

### Step 2: Mount the SSD
```bash
python3 scripts/hardware_forensics.py --mount-hidden
```
This brings the hidden SSD online and assigns a drive letter.

### Step 3: Extract Data
```bash
python3 scripts/hardware_forensics.py --mount-hidden --extract-all
```
This mounts AND extracts all data.

---

## 🔧 Troubleshooting

### "No hidden SSD found"
**Possible causes:**
- SSD is already mounted (check Disk Management on Windows)
- SSD is not physically connected
- SSD requires drivers (some NVMe drives)

**Solutions:**
1. Open Disk Management (Windows) or `lsblk` (Linux)
2. Look for drives without drive letters
3. Manually assign drive letter
4. Re-run the script

### "Permission denied" when mounting
**Windows:**
- Run PowerShell as Administrator
- Or run the entire script as Administrator

**Linux:**
- Use `sudo` for mount operations
- Script will prompt for sudo password

### "Cannot access SSD path"
**Check:**
1. Was the SSD successfully mounted?
2. Do you have permissions to read from it?
3. Is the drive letter/mount point correct?

---

## 🚀 Integration with Ultra Vacuum

The ultra vacuum script now includes hardware forensics as **Phase 0A** (highest priority):

```bash
./ultra_laptop_vacuum.sh --auto
```

This will:
1. **Phase 0A:** Find and extract hidden SSD FIRST
2. **Phase 0B:** Profile system hardware/software
3. **Phase 0C:** Process MASTER_MERGE_2
4. **Phase 1:** Comprehensive vacuum of all drives
5. **Phase 2-5:** Additional scanning and sync

---

## 📊 Example Output

```
🔬 HARDWARE FORENSICS TOOL
   Priority: Find hidden SSD and extract ALL data
======================================================================

🔍 DETECTING ALL STORAGE DEVICES
   Including hidden, unmounted, and offline drives
======================================================================

🪟 Windows: Scanning for all storage devices...

📊 Method 1: WMIC Physical Disks
   ✅ \\.\PHYSICALDRIVE0: Samsung SSD 970 EVO 500GB
   ✅ \\.\PHYSICALDRIVE1: WDC WD10EZEX-08WN4A0 (1000 GB)

📊 Method 2: List Volumes (including hidden)
   ✅ C:: Windows (476 GB)
   ✅ D:: Data (931 GB)
   🚨 HIDDEN VOLUME FOUND: Recovery (20 GB)

📊 Method 3: PowerShell Get-Disk (includes offline)
   ✅ Disk 0: Samsung SSD 970 EVO 500GB
   🚨 OFFLINE DISK FOUND: Disk 1: Crucial MX500 1TB - STATUS: Offline

✅ Detected 4 storage device(s)

🎯 IDENTIFYING HIDDEN SSD
======================================================================

🚨 HIDDEN SSD CANDIDATE: Disk 1: Crucial MX500 1TB (OFFLINE)

✅ HIDDEN SSD IDENTIFIED!
   Device: Disk 1: Crucial MX500 1TB

💾 MOUNTING HIDDEN SSD
======================================================================

🪟 Windows: Attempting to bring disk online and assign letter...

📌 Step 1: Bringing Disk 1 online...
   ✅ Disk 1 is now ONLINE

📌 Step 2: Assigning drive letter...
   ✅ Drive letter assigned
   ✅ Mounted at: E:\

📦 EXTRACTING ALL DATA FROM SSD: E:\
======================================================================

🎯 Source: E:\
🎯 Destination: data/Mapping-and-Inventory-storage/hidden_ssd/

📁 Copying: Documents
📁 Copying: Projects
📁 Copying: Pictures
📁 Copying: Code

✅ ALL SSD DATA EXTRACTED SUCCESSFULLY
   Location: data/Mapping-and-Inventory-storage/hidden_ssd/

📊 Generating SSD data index...
✅ Index saved: data/hardware_forensics/hidden_ssd_index.json
   Total Files: 15,432
   Total Size: 87.3 GB

🧠 RAM ANALYSIS
   Note: Deep RAM forensics requires admin/root privileges
======================================================================

💾 RAM Chips Detected:
   RAM 1: 16 GB - Samsung M471A2K43CB1-CTD
   RAM 2: 8 GB - Crucial CT8G4SFS824A

💡 Note about RAM data recovery:
   • RAM is volatile - data is lost when power is removed
   • We've cataloged the RAM chips for inventory purposes

✅ HARDWARE FORENSICS COMPLETE
======================================================================

📊 Summary:
   Total Devices Detected: 4
   Hidden SSD Found: Yes
   SSD Mounted: Yes
   Data Extracted: Yes
```

---

**Status:** ✅ READY TO USE  
**Priority:** Runs FIRST in ultra vacuum workflow  
**Authority:** Extracts everything before anything else
