#!/usr/bin/env python3
"""
🔬 HARDWARE FORENSICS TOOL
Detects hidden drives, unmounted SSDs, and extracts data from them

Priority: Find the hidden SSD FIRST and pull ALL data from it

Usage:
    python scripts/hardware_forensics.py
    python scripts/hardware_forensics.py --mount-hidden
    python scripts/hardware_forensics.py --extract-all
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import platform
import argparse


class HardwareForensics:
    """Forensic tool for detecting and accessing hidden storage devices"""
    
    def __init__(self):
        self.repo_root = Path(__file__).parent.parent
        self.output_dir = self.repo_root / "data" / "hardware_forensics"
        self.ssd_storage = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "hidden_ssd"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.ssd_storage.mkdir(parents=True, exist_ok=True)
        
        self.system = platform.system()
        
        self.forensics_report = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "hostname": platform.node(),
            "os": self.system,
            "all_drives": [],
            "mounted_drives": [],
            "unmounted_drives": [],
            "hidden_ssd": None,
            "ram_analysis": {}
        }
    
    def detect_all_storage_devices(self):
        """Detect ALL storage devices including hidden/unmounted ones"""
        print("\n" + "="*70)
        print("🔍 DETECTING ALL STORAGE DEVICES")
        print("   Including hidden, unmounted, and offline drives")
        print("="*70 + "\n")
        
        all_devices = []
        
        if self.system == "Windows":
            all_devices = self._detect_windows_devices()
        elif self.system == "Linux":
            all_devices = self._detect_linux_devices()
        elif self.system == "Darwin":  # macOS
            all_devices = self._detect_macos_devices()
        
        self.forensics_report["all_drives"] = all_devices
        
        print(f"\n✅ Detected {len(all_devices)} storage device(s)")
        return all_devices
    
    def _detect_windows_devices(self):
        """Detect all storage devices on Windows (including hidden)"""
        print("🪟 Windows: Scanning for all storage devices...")
        
        devices = []
        
        # Method 1: WMIC - All physical disks
        try:
            print("\n📊 Method 1: WMIC Physical Disks")
            result = subprocess.run(
                ['wmic', 'diskdrive', 'get', 'DeviceID,Model,Size,Status,MediaType'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                for line in lines:
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            device = {
                                "device_id": parts[0],
                                "model": ' '.join(parts[1:-3]) if len(parts) > 3 else parts[1],
                                "size_bytes": int(parts[-3]) if len(parts) > 3 and parts[-3].isdigit() else 0,
                                "status": parts[-2] if len(parts) > 2 else "Unknown",
                                "media_type": parts[-1] if len(parts) > 1 else "Unknown",
                                "source": "wmic_diskdrive"
                            }
                            devices.append(device)
                            print(f"   ✅ {device['device_id']}: {device['model']} ({device.get('size_bytes', 0) / (1024**3):.1f} GB)")
        except Exception as e:
            print(f"   ⚠️  WMIC failed: {e}")
        
        # Method 2: List volumes (including unmounted)
        try:
            print("\n📊 Method 2: List Volumes (including hidden)")
            result = subprocess.run(
                ['wmic', 'volume', 'get', 'DriveLetter,Label,Capacity,FreeSpace,FileSystem'],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                for line in lines:
                    if line.strip():
                        parts = line.strip().split()
                        if len(parts) >= 1:
                            volume = {
                                "drive_letter": parts[0] if len(parts) > 0 and ':' in parts[0] else "No Letter (HIDDEN)",
                                "label": parts[1] if len(parts) > 1 else "",
                                "capacity": int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0,
                                "free_space": int(parts[3]) if len(parts) > 3 and parts[3].isdigit() else 0,
                                "filesystem": parts[4] if len(parts) > 4 else "Unknown",
                                "source": "wmic_volume",
                                "is_hidden": "No Letter" in str(parts[0]) or not any(':' in str(p) for p in parts)
                            }
                            devices.append(volume)
                            
                            if volume["is_hidden"]:
                                print(f"   🚨 HIDDEN VOLUME FOUND: {volume['label']} ({volume.get('capacity', 0) / (1024**3):.1f} GB)")
                            else:
                                print(f"   ✅ {volume['drive_letter']}: {volume['label']} ({volume.get('capacity', 0) / (1024**3):.1f} GB)")
        except Exception as e:
            print(f"   ⚠️  Volume list failed: {e}")
        
        # Method 3: PowerShell - Get all disks including offline
        try:
            print("\n📊 Method 3: PowerShell Get-Disk (includes offline)")
            ps_command = "Get-Disk | Select-Object Number,FriendlyName,Size,PartitionStyle,OperationalStatus | ConvertTo-Json"
            result = subprocess.run(
                ['powershell', '-Command', ps_command],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0 and result.stdout.strip():
                try:
                    disks = json.loads(result.stdout)
                    if not isinstance(disks, list):
                        disks = [disks]
                    
                    for disk in disks:
                        device = {
                            "disk_number": disk.get("Number"),
                            "friendly_name": disk.get("FriendlyName"),
                            "size_bytes": disk.get("Size", 0),
                            "partition_style": disk.get("PartitionStyle"),
                            "status": disk.get("OperationalStatus"),
                            "source": "powershell_get_disk",
                            "is_offline": disk.get("OperationalStatus") != "Online"
                        }
                        devices.append(device)
                        
                        if device["is_offline"]:
                            print(f"   🚨 OFFLINE DISK FOUND: Disk {device['disk_number']}: {device['friendly_name']} ({device.get('size_bytes', 0) / (1024**3):.1f} GB) - STATUS: {device['status']}")
                        else:
                            print(f"   ✅ Disk {device['disk_number']}: {device['friendly_name']} ({device.get('size_bytes', 0) / (1024**3):.1f} GB)")
                except json.JSONDecodeError:
                    print(f"   ⚠️  PowerShell output not valid JSON")
        except Exception as e:
            print(f"   ⚠️  PowerShell Get-Disk failed: {e}")
        
        return devices
    
    def _detect_linux_devices(self):
        """Detect all storage devices on Linux"""
        print("🐧 Linux: Scanning for all storage devices...")
        
        devices = []
        
        # Method 1: lsblk
        try:
            print("\n📊 Method 1: lsblk")
            result = subprocess.run(['lsblk', '-J', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE'],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lsblk_data = json.loads(result.stdout)
                for device in lsblk_data.get("blockdevices", []):
                    dev_info = {
                        "name": device.get("name"),
                        "size": device.get("size"),
                        "type": device.get("type"),
                        "mountpoint": device.get("mountpoint"),
                        "fstype": device.get("fstype"),
                        "source": "lsblk",
                        "is_unmounted": not device.get("mountpoint")
                    }
                    devices.append(dev_info)
                    
                    if dev_info["is_unmounted"] and dev_info["type"] == "disk":
                        print(f"   🚨 UNMOUNTED DISK: /dev/{dev_info['name']} ({dev_info['size']})")
                    else:
                        print(f"   ✅ /dev/{dev_info['name']}: {dev_info['size']} ({dev_info['mountpoint'] or 'not mounted'})")
        except Exception as e:
            print(f"   ⚠️  lsblk failed: {e}")
        
        # Method 2: /proc/partitions
        try:
            print("\n📊 Method 2: /proc/partitions")
            with open('/proc/partitions', 'r') as f:
                lines = f.readlines()[2:]  # Skip header
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 4:
                        print(f"   ✅ {parts[3]}: {int(parts[2]) / 1024:.1f} MB")
        except Exception as e:
            print(f"   ⚠️  /proc/partitions failed: {e}")
        
        return devices
    
    def _detect_macos_devices(self):
        """Detect all storage devices on macOS"""
        print("🍎 macOS: Scanning for all storage devices...")
        
        devices = []
        
        try:
            result = subprocess.run(['diskutil', 'list', '-plist'],
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse plist output
                print(f"   ✅ Found disk information")
                # Note: Would need plistlib to parse properly
        except Exception as e:
            print(f"   ⚠️  diskutil failed: {e}")
        
        return devices
    
    def find_hidden_ssd(self):
        """Identify the hidden SSD from detected devices"""
        print("\n" + "="*70)
        print("🎯 IDENTIFYING HIDDEN SSD")
        print("="*70 + "\n")
        
        hidden_candidates = []
        
        for device in self.forensics_report["all_drives"]:
            # Look for unmounted/hidden/offline drives
            if device.get("is_hidden") or device.get("is_unmounted") or device.get("is_offline"):
                # Check if it's an SSD (look for SSD keywords or solid state)
                device_str = json.dumps(device).lower()
                is_ssd = any(keyword in device_str for keyword in ['ssd', 'solid', 'nvme', 'samsung', 'crucial', 'kingston'])
                
                if is_ssd or device.get("media_type") == "Fixed hard disk media":
                    hidden_candidates.append(device)
                    print(f"🚨 HIDDEN SSD CANDIDATE: {device}")
        
        if hidden_candidates:
            # Take the first candidate as the hidden SSD
            self.forensics_report["hidden_ssd"] = hidden_candidates[0]
            print(f"\n✅ HIDDEN SSD IDENTIFIED!")
            print(f"   Device: {hidden_candidates[0]}")
            return hidden_candidates[0]
        else:
            print(f"\n⚠️  No hidden SSD found in scan")
            print(f"   All {len(self.forensics_report['all_drives'])} devices appear to be mounted/online")
            return None
    
    def mount_hidden_ssd(self, ssd_device):
        """Attempt to mount the hidden SSD"""
        print("\n" + "="*70)
        print("💾 MOUNTING HIDDEN SSD")
        print("="*70 + "\n")
        
        if self.system == "Windows":
            return self._mount_windows_ssd(ssd_device)
        elif self.system == "Linux":
            return self._mount_linux_ssd(ssd_device)
        elif self.system == "Darwin":
            return self._mount_macos_ssd(ssd_device)
    
    def _mount_windows_ssd(self, ssd_device):
        """Mount SSD on Windows"""
        print("🪟 Windows: Attempting to bring disk online and assign letter...")
        
        # If it's an offline disk, bring it online
        if ssd_device.get("is_offline") and ssd_device.get("disk_number") is not None:
            disk_num = ssd_device["disk_number"]
            
            print(f"\n📌 Step 1: Bringing Disk {disk_num} online...")
            ps_online = f"Set-Disk -Number {disk_num} -IsOffline $false"
            
            try:
                result = subprocess.run(['powershell', '-Command', ps_online],
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"   ✅ Disk {disk_num} is now ONLINE")
                else:
                    print(f"   ⚠️  Failed to bring disk online: {result.stderr}")
                    return None
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return None
            
            # Assign drive letter to first partition
            print(f"\n📌 Step 2: Assigning drive letter...")
            ps_assign = f"Get-Partition -DiskNumber {disk_num} | Where-Object {{-not $_.DriveLetter}} | Select-Object -First 1 | Add-PartitionAccessPath -AssignDriveLetter"
            
            try:
                result = subprocess.run(['powershell', '-Command', ps_assign],
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print(f"   ✅ Drive letter assigned")
                    
                    # Get the assigned letter
                    ps_get_letter = f"(Get-Partition -DiskNumber {disk_num} | Where-Object {{$_.DriveLetter}}).DriveLetter"
                    result = subprocess.run(['powershell', '-Command', ps_get_letter],
                                          capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0 and result.stdout.strip():
                        drive_letter = result.stdout.strip() + ":\\"
                        print(f"   ✅ Mounted at: {drive_letter}")
                        return drive_letter
                else:
                    print(f"   ⚠️  Failed to assign drive letter: {result.stderr}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # If it's a hidden volume, try to get its path
        if ssd_device.get("is_hidden"):
            print(f"\n⚠️  This is a hidden volume without a drive letter")
            print(f"   Manual intervention may be required")
            print(f"   Suggestion: Open Disk Management and assign a drive letter")
        
        return None
    
    def _mount_linux_ssd(self, ssd_device):
        """Mount SSD on Linux"""
        print("🐧 Linux: Attempting to mount...")
        
        device_name = ssd_device.get("name")
        if not device_name:
            print("   ❌ No device name found")
            return None
        
        mount_point = f"/mnt/hidden_ssd_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Create mount point
            subprocess.run(['sudo', 'mkdir', '-p', mount_point], check=True)
            
            # Mount
            subprocess.run(['sudo', 'mount', f'/dev/{device_name}', mount_point], check=True)
            
            print(f"   ✅ Mounted at: {mount_point}")
            return mount_point
        except Exception as e:
            print(f"   ❌ Mount failed: {e}")
            return None
    
    def _mount_macos_ssd(self, ssd_device):
        """Mount SSD on macOS"""
        print("🍎 macOS: Attempting to mount...")
        # Implementation would go here
        return None
    
    def extract_all_ssd_data(self, ssd_path):
        """Extract ALL data from the mounted SSD"""
        print("\n" + "="*70)
        print(f"📦 EXTRACTING ALL DATA FROM SSD: {ssd_path}")
        print("="*70 + "\n")
        
        if not ssd_path or not os.path.exists(ssd_path):
            print(f"❌ SSD path not accessible: {ssd_path}")
            return False
        
        print(f"🎯 Source: {ssd_path}")
        print(f"🎯 Destination: {self.ssd_storage}")
        print(f"\n⚠️  This may take a long time depending on data size...")
        print(f"   Copying ALL files recursively...\n")
        
        try:
            # Use shutil to copy entire directory tree
            for item in os.listdir(ssd_path):
                source = os.path.join(ssd_path, item)
                dest = self.ssd_storage / item
                
                print(f"📁 Copying: {item}")
                
                if os.path.isdir(source):
                    shutil.copytree(source, dest, dirs_exist_ok=True, 
                                  ignore=shutil.ignore_patterns('$RECYCLE.BIN', 'System Volume Information'))
                else:
                    shutil.copy2(source, dest)
            
            print(f"\n✅ ALL SSD DATA EXTRACTED SUCCESSFULLY")
            print(f"   Location: {self.ssd_storage}")
            
            # Generate index
            self._generate_ssd_index()
            
            return True
        
        except Exception as e:
            print(f"❌ Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _generate_ssd_index(self):
        """Generate index of extracted SSD data"""
        print(f"\n📊 Generating SSD data index...")
        
        index = {
            "extracted_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_files": 0,
            "total_size_bytes": 0,
            "file_types": {},
            "directory_structure": []
        }
        
        for root, dirs, files in os.walk(self.ssd_storage):
            rel_root = os.path.relpath(root, self.ssd_storage)
            
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    size = os.path.getsize(file_path)
                    ext = os.path.splitext(file)[1].lower()
                    
                    index["total_files"] += 1
                    index["total_size_bytes"] += size
                    index["file_types"][ext] = index["file_types"].get(ext, 0) + 1
                except:
                    pass
        
        index["total_size_gb"] = round(index["total_size_bytes"] / (1024**3), 2)
        
        index_file = self.output_dir / "hidden_ssd_index.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
        
        print(f"✅ Index saved: {index_file}")
        print(f"   Total Files: {index['total_files']:,}")
        print(f"   Total Size: {index['total_size_gb']} GB")
    
    def analyze_ram(self):
        """Analyze RAM for residual data (limited capabilities without admin)"""
        print("\n" + "="*70)
        print("🧠 RAM ANALYSIS")
        print("   Note: Deep RAM forensics requires admin/root privileges")
        print("="*70 + "\n")
        
        ram_info = {
            "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
            "warning": "Full RAM dump requires elevated privileges",
            "basic_info": {}
        }
        
        # Get basic RAM info
        if self.system == "Windows":
            try:
                result = subprocess.run(['wmic', 'memorychip', 'get', 'Capacity,Manufacturer,PartNumber,SerialNumber'],
                                      capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    print("💾 RAM Chips Detected:")
                    lines = result.stdout.strip().split('\n')[1:]
                    chips = []
                    
                    for i, line in enumerate(lines, 1):
                        if line.strip():
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                chip = {
                                    "slot": i,
                                    "capacity_bytes": int(parts[0]) if parts[0].isdigit() else 0,
                                    "capacity_gb": round(int(parts[0]) / (1024**3), 2) if parts[0].isdigit() else 0,
                                    "manufacturer": parts[1] if len(parts) > 1 else "Unknown",
                                    "part_number": parts[2] if len(parts) > 2 else "Unknown",
                                    "serial": parts[3] if len(parts) > 3 else "Unknown"
                                }
                                chips.append(chip)
                                print(f"   RAM {i}: {chip['capacity_gb']} GB - {chip['manufacturer']} {chip['part_number']}")
                    
                    ram_info["chips"] = chips
            except Exception as e:
                print(f"   ⚠️  RAM detection failed: {e}")
        
        self.forensics_report["ram_analysis"] = ram_info
        
        print(f"\n💡 Note about RAM data recovery:")
        print(f"   • RAM is volatile - data is lost when power is removed")
        print(f"   • Cold boot attacks can recover data within ~30 seconds of power loss")
        print(f"   • Data remanence can persist briefly but requires specialized tools")
        print(f"   • We've cataloged the RAM chips for inventory purposes")
        
        return ram_info
    
    def save_report(self):
        """Save forensics report"""
        report_file = self.output_dir / f"hardware_forensics_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(self.forensics_report, f, indent=2)
        
        print(f"\n✅ Forensics report saved: {report_file}")
        return report_file


def main():
    parser = argparse.ArgumentParser(description="Hardware Forensics - Find and extract hidden SSD data")
    parser.add_argument("--mount-hidden", action="store_true", help="Attempt to mount hidden SSD")
    parser.add_argument("--extract-all", action="store_true", help="Extract ALL data from SSD")
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🔬 HARDWARE FORENSICS TOOL")
    print("   Priority: Find hidden SSD and extract ALL data")
    print("="*70)
    
    forensics = HardwareForensics()
    
    # Step 1: Detect all storage devices
    forensics.detect_all_storage_devices()
    
    # Step 2: Identify hidden SSD
    hidden_ssd = forensics.find_hidden_ssd()
    
    # Step 3: Mount if requested
    ssd_path = None
    if args.mount_hidden and hidden_ssd:
        ssd_path = forensics.mount_hidden_ssd(hidden_ssd)
    
    # Step 4: Extract data if requested
    if args.extract_all and ssd_path:
        forensics.extract_all_ssd_data(ssd_path)
    elif args.extract_all and not ssd_path:
        print("\n⚠️  Cannot extract data - SSD not mounted")
        print("   Run with --mount-hidden first, or manually mount the SSD")
    
    # Step 5: Analyze RAM
    forensics.analyze_ram()
    
    # Step 6: Save report
    forensics.save_report()
    
    print("\n" + "="*70)
    print("✅ HARDWARE FORENSICS COMPLETE")
    print("="*70)
    
    print(f"\n📊 Summary:")
    print(f"   Total Devices Detected: {len(forensics.forensics_report['all_drives'])}")
    print(f"   Hidden SSD Found: {'Yes' if hidden_ssd else 'No'}")
    print(f"   SSD Mounted: {'Yes' if ssd_path else 'No'}")
    print(f"   Data Extracted: {'Yes' if args.extract_all and ssd_path else 'No'}")
    
    if hidden_ssd and not args.mount_hidden:
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Run with --mount-hidden to mount the SSD")
        print(f"   2. Run with --extract-all to copy all data")
        print(f"   Or run both: python scripts/hardware_forensics.py --mount-hidden --extract-all")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
