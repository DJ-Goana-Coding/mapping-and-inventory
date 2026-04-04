#!/usr/bin/env python3
"""
📦 GDRIVE PRIORITY COPIER
Authority: Citadel Architect v25.0.OMNI+
Purpose: Intelligent file copier with P0-P3 priority tiers
"""

import subprocess
import json
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import concurrent.futures
import time

class GDrivePriorityCopier:
    """Copy GDrive files by priority tiers"""
    
    # Priority definitions
    PRIORITIES = {
        "P0": {
            "name": "CRITICAL",
            "patterns": [
                r"(?i).*tia.*\.(py|md|txt|json)",
                r"(?i).*citadel.*\.(py|md|txt|json)",
                r"(?i).*early.*work.*",
                r"(?i).*agent.*\.(py|js|gs)",
                r"(?i).*build.*\.(py|md)",
                r"(?i).*architecture.*\.md"
            ],
            "max_size_mb": 100,
            "destination": "data/gdrive_archive/{account}/P0_CRITICAL/"
        },
        "P1": {
            "name": "HIGH",
            "patterns": [
                r".*\.(md|txt|json|yaml|yml)$",
                r".*\.(py|js|ts|gs|html|css)$",
                r".*\.(sh|bash|ps1)$"
            ],
            "max_size_mb": 100,
            "destination": "data/gdrive_archive/{account}/P1_HIGH/"
        },
        "P2": {
            "name": "MEDIUM",
            "patterns": [
                r".*\.(mp3|wav|flac|m4a)$",
                r".*\.(jpg|jpeg|png|gif|svg|psd|ai)$",
                r".*\.(gguf|pt|pth|bin|safetensors)$",
                r".*\.(csv|parquet|feather|db)$"
            ],
            "max_size_mb": 1000,
            "destination": "data/gdrive_archive/{account}/P2_MEDIUM/"
        },
        "P3": {
            "name": "LOW",
            "patterns": [
                r".*\.(zip|rar|7z|tar|gz)$",
                r".*\.(mp4|avi|mkv|mov)$",
                r".*\.(exe|msi|dmg)$"
            ],
            "max_size_mb": 5000,
            "destination": "data/gdrive_archive/{account}/P3_LOW/"
        }
    }
    
    def __init__(self, remote_name: str, account_name: str, base_path: Path):
        self.remote_name = remote_name
        self.account_name = account_name
        self.base_path = base_path
        self.manifest = {
            "copy_start": datetime.utcnow().isoformat() + "Z",
            "remote": remote_name,
            "account": account_name,
            "priorities": {},
            "stats": {
                "total_files": 0,
                "total_bytes": 0,
                "files_copied": 0,
                "bytes_copied": 0,
                "files_skipped": 0,
                "errors": []
            }
        }
    
    def scan_remote(self, path: str = "") -> List[Dict[str, Any]]:
        """Scan remote and get file list with metadata"""
        print(f"🔍 Scanning {self.remote_name}:{path}")
        
        try:
            # Use rclone lsjson for detailed file info
            result = subprocess.run(
                ["rclone", "lsjson", f"{self.remote_name}:{path}", "--recursive"],
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                files = json.loads(result.stdout)
                print(f"   Found {len(files)} files")
                return files
            else:
                print(f"   ❌ Error: {result.stderr}")
                return []
                
        except subprocess.TimeoutExpired:
            print(f"   ❌ Timeout scanning {path}")
            return []
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []
    
    def classify_file(self, file_path: str, file_size_bytes: int) -> Optional[str]:
        """Classify file into priority tier"""
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        for priority_level, config in self.PRIORITIES.items():
            # Check size limit
            if file_size_mb > config["max_size_mb"]:
                continue
            
            # Check patterns
            for pattern in config["patterns"]:
                if re.match(pattern, file_path):
                    return priority_level
        
        return None  # No priority match
    
    def copy_file(self, file_info: Dict[str, Any], priority: str) -> bool:
        """Copy a single file"""
        file_path = file_info["Path"]
        file_size = file_info.get("Size", 0)
        
        # Determine destination
        dest_template = self.PRIORITIES[priority]["destination"]
        dest_dir = Path(dest_template.format(account=self.account_name))
        dest_file = dest_dir / file_path
        
        # Create destination directory
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Check if already exists
        if dest_file.exists():
            existing_size = dest_file.stat().st_size
            if existing_size == file_size:
                print(f"   ⏭️  Skip (exists): {file_path}")
                self.manifest["stats"]["files_skipped"] += 1
                return True
        
        # Copy file
        try:
            print(f"   📥 Copying [{priority}]: {file_path} ({file_size / 1024 / 1024:.2f} MB)")
            
            result = subprocess.run(
                [
                    "rclone", "copy",
                    f"{self.remote_name}:{file_path}",
                    str(dest_file.parent),
                    "--progress"
                ],
                capture_output=True,
                text=True,
                timeout=600
            )
            
            if result.returncode == 0:
                # Verify copy
                if dest_file.exists():
                    self.manifest["stats"]["files_copied"] += 1
                    self.manifest["stats"]["bytes_copied"] += file_size
                    print(f"      ✅ Copied successfully")
                    return True
            else:
                error_msg = f"Copy failed: {result.stderr}"
                print(f"      ❌ {error_msg}")
                self.manifest["stats"]["errors"].append({
                    "file": file_path,
                    "error": error_msg
                })
                return False
                
        except subprocess.TimeoutExpired:
            error_msg = "Timeout during copy"
            print(f"      ❌ {error_msg}")
            self.manifest["stats"]["errors"].append({
                "file": file_path,
                "error": error_msg
            })
            return False
        except Exception as e:
            error_msg = str(e)
            print(f"      ❌ Error: {error_msg}")
            self.manifest["stats"]["errors"].append({
                "file": file_path,
                "error": error_msg
            })
            return False
        
        return False
    
    def copy_priority_tier(self, priority: str, files: List[Dict[str, Any]]) -> None:
        """Copy all files in a priority tier"""
        priority_name = self.PRIORITIES[priority]["name"]
        print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"📦 Copying {priority} ({priority_name}) - {len(files)} files")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        self.manifest["priorities"][priority] = {
            "name": priority_name,
            "total_files": len(files),
            "files_copied": 0,
            "bytes_copied": 0,
            "start_time": datetime.utcnow().isoformat() + "Z"
        }
        
        for file_info in files:
            if self.copy_file(file_info, priority):
                self.manifest["priorities"][priority]["files_copied"] += 1
                self.manifest["priorities"][priority]["bytes_copied"] += file_info.get("Size", 0)
        
        self.manifest["priorities"][priority]["end_time"] = datetime.utcnow().isoformat() + "Z"
        
        copied = self.manifest["priorities"][priority]["files_copied"]
        total = self.manifest["priorities"][priority]["total_files"]
        bytes_copied = self.manifest["priorities"][priority]["bytes_copied"]
        
        print(f"\n✅ {priority} complete: {copied}/{total} files ({bytes_copied / 1024 / 1024:.2f} MB)")
    
    def run_prioritized_copy(self) -> Dict[str, Any]:
        """Run complete prioritized copy"""
        print(f"\n🚀 Starting prioritized copy for {self.account_name}")
        print(f"   Remote: {self.remote_name}")
        print(f"   Base: {self.base_path}")
        
        # Scan all files
        all_files = self.scan_remote()
        self.manifest["stats"]["total_files"] = len(all_files)
        self.manifest["stats"]["total_bytes"] = sum(f.get("Size", 0) for f in all_files)
        
        # Classify files by priority
        prioritized_files = {p: [] for p in self.PRIORITIES.keys()}
        unprioritized_files = []
        
        for file_info in all_files:
            if file_info.get("IsDir", False):
                continue  # Skip directories
            
            file_path = file_info["Path"]
            file_size = file_info.get("Size", 0)
            
            priority = self.classify_file(file_path, file_size)
            if priority:
                prioritized_files[priority].append(file_info)
            else:
                unprioritized_files.append(file_info)
        
        # Print classification summary
        print(f"\n📊 File Classification:")
        for priority, files in prioritized_files.items():
            priority_name = self.PRIORITIES[priority]["name"]
            total_size = sum(f.get("Size", 0) for f in files)
            print(f"   {priority} ({priority_name}): {len(files)} files ({total_size / 1024 / 1024:.2f} MB)")
        print(f"   Unprioritized: {len(unprioritized_files)} files")
        
        # Copy in priority order
        for priority in ["P0", "P1", "P2", "P3"]:
            if prioritized_files[priority]:
                self.copy_priority_tier(priority, prioritized_files[priority])
        
        self.manifest["copy_end"] = datetime.utcnow().isoformat() + "Z"
        
        return self.manifest
    
    def save_manifest(self, output_path: Path) -> None:
        """Save copy manifest"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        print(f"\n📄 Manifest saved: {output_path}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GDrive Priority Copier")
    parser.add_argument("--remote", required=True, help="Rclone remote name")
    parser.add_argument("--account", required=True, help="Account identifier")
    parser.add_argument("--base-path", default=".", help="Base output path")
    
    args = parser.parse_args()
    
    base_path = Path(args.base_path)
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📦 GDRIVE PRIORITY COPIER")
    print("   Authority: Citadel Architect v25.0.OMNI+")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    copier = GDrivePriorityCopier(args.remote, args.account, base_path)
    manifest = copier.run_prioritized_copy()
    
    # Save manifest
    manifest_path = base_path / "data" / "gdrive_archive" / args.account / "copy_manifest.json"
    copier.save_manifest(manifest_path)
    
    # Print summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 COPY SUMMARY")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n✅ Files copied: {manifest['stats']['files_copied']}/{manifest['stats']['total_files']}")
    print(f"💾 Data copied: {manifest['stats']['bytes_copied'] / 1024 / 1024:.2f} MB")
    print(f"⏭️  Files skipped: {manifest['stats']['files_skipped']}")
    print(f"❌ Errors: {len(manifest['stats']['errors'])}")
    
    if manifest['stats']['errors']:
        print("\n⚠️  Errors occurred:")
        for error in manifest['stats']['errors'][:5]:
            print(f"   - {error['file']}: {error['error']}")
        if len(manifest['stats']['errors']) > 5:
            print(f"   ... and {len(manifest['stats']['errors']) - 5} more")


if __name__ == "__main__":
    main()
