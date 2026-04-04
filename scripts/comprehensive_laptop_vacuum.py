#!/usr/bin/env python3
"""
🌊 COMPREHENSIVE LAPTOP VACUUM
Aggressive harvesting of ALL drives, ALL systems, EVERYTHING relevant

This is the nuclear option - crawls the entire laptop and copies everything
that can be used in the build. Uses MASTER_MERGE_2 as primary intelligence.

Usage:
    python scripts/comprehensive_laptop_vacuum.py
    python scripts/comprehensive_laptop_vacuum.py --drives C D E
    python scripts/comprehensive_laptop_vacuum.py --max-size 500  # MB per file
"""

import os
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Any
import sys
import platform


class ComprehensiveLaptopVacuum:
    """Aggressive vacuum of entire laptop - all drives, all systems"""
    
    def __init__(self, max_file_size_mb=500):
        self.repo_root = Path(__file__).parent.parent
        self.storage_root = self.repo_root / "data" / "Mapping-and-Inventory-storage" / "laptop_vacuum"
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        self.max_file_size = max_file_size_mb * 1024 * 1024
        
        # What we consider "relevant for the build"
        self.relevant_extensions = {
            # Code
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h', '.cs', '.go', '.rs', '.rb',
            '.php', '.swift', '.kt', '.scala', '.r', '.m', '.lua', '.pl', '.sh', '.bash', '.zsh', '.ps1',
            '.bat', '.cmd',
            
            # Web
            '.html', '.htm', '.css', '.scss', '.sass', '.less', '.vue', '.svelte',
            
            # Config/Data
            '.json', '.yaml', '.yml', '.toml', '.xml', '.ini', '.conf', '.config', '.env.example',
            
            # Documentation
            '.md', '.rst', '.txt', '.adoc', '.tex',
            
            # Data/ML
            '.csv', '.tsv', '.parquet', '.arrow', '.feather', '.jsonl', '.ndjson',
            '.pkl', '.pickle', '.h5', '.hdf5', '.npz', '.npy',
            
            # Models
            '.pt', '.pth', '.ckpt', '.safetensors', '.gguf', '.bin', '.model', '.weights',
            '.onnx', '.tflite', '.pb', '.keras',
            
            # Notebooks
            '.ipynb', '.Rmd',
            
            # SQL/Database
            '.sql', '.db', '.sqlite', '.sqlite3',
            
            # Archives (for later extraction)
            '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
            
            # Build/Project
            'Makefile', 'Dockerfile', '.dockerignore', 'docker-compose.yml',
            'requirements.txt', 'package.json', 'package-lock.json', 'yarn.lock',
            'Cargo.toml', 'go.mod', 'pom.xml', 'build.gradle', 'CMakeLists.txt',
            '.gitignore', '.gitattributes', 'README', 'LICENSE', 'CHANGELOG',
            
            # PowerShell/Scripts
            '.psm1', '.psd1',
        }
        
        # Directories to ALWAYS skip (system/junk)
        self.skip_dirs = {
            '$Recycle.Bin', 'System Volume Information', 'Windows', 'Program Files',
            'Program Files (x86)', 'ProgramData', 'AppData', 'node_modules', '__pycache__',
            '.git', '.svn', '.hg', 'venv', 'env', '.venv', '.env', 'vendor',
            'bower_components', 'dist', 'build', 'target', 'bin', 'obj',
            '.vs', '.vscode', '.idea', 'tmp', 'temp', 'cache', '.cache',
            'Thumbs.db', '.DS_Store', 'Library', 'Applications'
        }
        
        # Keywords that indicate relevance
        self.relevant_keywords = {
            'tia', 'architect', 'oracle', 'surveyor', 'citadel', 'omega', 'vamguard',
            'trading', 'bot', 'model', 'dataset', 'ml', 'ai', 'neural', 'transformer',
            'api', 'webhook', 'blockchain', 'crypto', 'web3', 'smart_contract',
            'analysis', 'research', 'project', 'source', 'script', 'tool', 'utility',
            'master', 'merge', 'system', 'map', 'intelligence', 'quantum', 'goanna'
        }
        
        self.stats = {
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'drives_scanned': [],
            'files_found': 0,
            'files_harvested': 0,
            'bytes_harvested': 0,
            'skipped_too_large': 0,
            'skipped_irrelevant': 0,
            'errors': 0
        }
        
        self.harvest_log = []
    
    def detect_all_drives(self):
        """Detect all available drives/partitions"""
        print("\n🔍 Detecting all drives and partitions...")
        
        drives = []
        system = platform.system()
        
        if system == 'Windows':
            # Windows: Check all drive letters
            for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
                drive = f"{letter}:\\"
                if os.path.exists(drive):
                    drives.append(drive)
                    print(f"   ✅ Found: {drive}")
        
        elif system in ['Linux', 'Darwin']:  # Darwin = macOS
            # Unix-like: Common mount points
            common_mounts = [
                '/',
                '/home',
                '/mnt',
                '/media',
                Path.home(),
            ]
            
            for mount in common_mounts:
                if os.path.exists(mount):
                    drives.append(str(mount))
                    print(f"   ✅ Found: {mount}")
            
            # Check /mnt and /media for additional mounts
            for base in ['/mnt', '/media']:
                if os.path.exists(base):
                    for item in os.listdir(base):
                        mount_path = os.path.join(base, item)
                        if os.path.ismount(mount_path):
                            drives.append(mount_path)
                            print(f"   ✅ Found mounted: {mount_path}")
        
        else:
            print(f"   ⚠️  Unknown OS: {system}")
            drives = [str(Path.home())]
        
        self.stats['drives_scanned'] = drives
        print(f"\n✅ Detected {len(drives)} drive(s)/partition(s)")
        
        return drives
    
    def is_relevant_file(self, file_path: Path) -> bool:
        """Determine if file is relevant for the build"""
        
        # Check extension
        if file_path.suffix.lower() in self.relevant_extensions:
            return True
        
        # Check if filename matches (no extension files like Makefile)
        if file_path.name in self.relevant_extensions:
            return True
        
        # Check for relevant keywords in path
        path_lower = str(file_path).lower()
        for keyword in self.relevant_keywords:
            if keyword in path_lower:
                return True
        
        return False
    
    def should_skip_directory(self, dir_path: Path) -> bool:
        """Check if directory should be skipped"""
        dir_name = dir_path.name.lower()
        
        # Check skip list
        for skip in self.skip_dirs:
            if skip.lower() in dir_name or dir_name == skip.lower():
                return True
        
        # Skip hidden directories (except .github, .huggingface)
        if dir_path.name.startswith('.') and dir_path.name not in ['.github', '.huggingface']:
            return True
        
        return False
    
    def harvest_file(self, file_path: Path, base_drive: str) -> bool:
        """Harvest a single file"""
        try:
            # Check size
            size = file_path.stat().st_size
            if size > self.max_file_size:
                self.stats['skipped_too_large'] += 1
                return False
            
            # Create relative path from drive
            try:
                rel_path = file_path.relative_to(base_drive)
            except ValueError:
                # If can't make relative, use the full path structure
                rel_path = Path(str(file_path).replace(':', '_').replace('\\', '/').lstrip('/'))
            
            # Create destination
            dest_path = self.storage_root / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(file_path, dest_path)
            
            # Generate metadata
            with open(file_path, 'rb') as f:
                content_hash = hashlib.sha256(f.read()).hexdigest()
            
            metadata = {
                'source_path': str(file_path),
                'source_drive': base_drive,
                'relative_path': str(rel_path),
                'size_bytes': size,
                'sha256': content_hash,
                'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                'harvested_at': datetime.utcnow().isoformat() + 'Z',
                'is_relevant': self.is_relevant_file(file_path)
            }
            
            # Save metadata
            meta_path = dest_path.with_suffix(dest_path.suffix + '.meta.json')
            with open(meta_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            self.stats['files_harvested'] += 1
            self.stats['bytes_harvested'] += size
            
            self.harvest_log.append({
                'file': str(file_path),
                'size': size,
                'status': 'success'
            })
            
            return True
        
        except Exception as e:
            self.stats['errors'] += 1
            self.harvest_log.append({
                'file': str(file_path),
                'status': 'error',
                'error': str(e)
            })
            return False
    
    def vacuum_drive(self, drive_path: str, max_files_per_drive=50000):
        """Vacuum a single drive"""
        print(f"\n{'='*70}")
        print(f"🌊 VACUUMING: {drive_path}")
        print(f"{'='*70}\n")
        
        drive = Path(drive_path)
        files_this_drive = 0
        
        for root, dirs, files in os.walk(drive):
            # Skip irrelevant directories
            root_path = Path(root)
            
            # Filter directories in-place
            dirs[:] = [d for d in dirs if not self.should_skip_directory(root_path / d)]
            
            # Process files
            for file in files:
                if files_this_drive >= max_files_per_drive:
                    print(f"⚠️  Reached max files per drive limit: {max_files_per_drive}")
                    return
                
                file_path = root_path / file
                
                # Skip if not accessible
                if not os.access(file_path, os.R_OK):
                    continue
                
                self.stats['files_found'] += 1
                
                # Check if relevant
                if self.is_relevant_file(file_path):
                    if self.harvest_file(file_path, drive_path):
                        files_this_drive += 1
                        
                        # Progress indicator
                        if files_this_drive % 100 == 0:
                            print(f"   📦 Harvested {files_this_drive} files from this drive...")
                else:
                    self.stats['skipped_irrelevant'] += 1
        
        print(f"\n✅ Drive vacuum complete: {files_this_drive} files harvested")
    
    def vacuum_all_drives(self, specific_drives=None, max_files_per_drive=50000):
        """Vacuum all drives or specific ones"""
        print("\n" + "="*70)
        print("🌊 COMPREHENSIVE LAPTOP VACUUM")
        print("   ALL drives, ALL systems, EVERYTHING relevant")
        print("="*70)
        
        # Detect drives
        if specific_drives:
            drives = specific_drives
            print(f"\n🎯 Targeting specific drives: {', '.join(drives)}")
        else:
            drives = self.detect_all_drives()
        
        # Vacuum each drive
        for drive in drives:
            try:
                self.vacuum_drive(drive, max_files_per_drive)
            except PermissionError:
                print(f"⚠️  Permission denied: {drive}")
            except Exception as e:
                print(f"❌ Error vacuuming {drive}: {e}")
                self.stats['errors'] += 1
    
    def generate_report(self):
        """Generate comprehensive harvest report"""
        print("\n" + "="*70)
        print("📊 VACUUM REPORT")
        print("="*70)
        
        self.stats['end_time'] = datetime.utcnow().isoformat() + 'Z'
        
        # Calculate stats
        gb_harvested = self.stats['bytes_harvested'] / (1024**3)
        
        print(f"\n⏱️  Duration: {self.stats['start_time']} → {self.stats['end_time']}")
        print(f"💾 Drives Scanned: {len(self.stats['drives_scanned'])}")
        for drive in self.stats['drives_scanned']:
            print(f"   • {drive}")
        
        print(f"\n📊 Statistics:")
        print(f"   Files Found: {self.stats['files_found']:,}")
        print(f"   Files Harvested: {self.stats['files_harvested']:,}")
        print(f"   Data Harvested: {gb_harvested:.2f} GB")
        print(f"   Skipped (too large): {self.stats['skipped_too_large']:,}")
        print(f"   Skipped (irrelevant): {self.stats['skipped_irrelevant']:,}")
        print(f"   Errors: {self.stats['errors']:,}")
        
        # Save report
        report = {
            'stats': self.stats,
            'harvest_log': self.harvest_log[-1000:]  # Last 1000 entries
        }
        
        report_path = self.storage_root / 'vacuum_report.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Report saved: {report_path}")
        
        # Save harvest index
        index = []
        for meta_file in self.storage_root.rglob('*.meta.json'):
            try:
                with open(meta_file) as f:
                    metadata = json.load(f)
                    index.append({
                        'source': metadata['source_path'],
                        'size': metadata['size_bytes'],
                        'hash': metadata['sha256'],
                        'harvested': metadata['harvested_at']
                    })
            except:
                pass
        
        index_path = self.storage_root / 'harvest_index.json'
        with open(index_path, 'w') as f:
            json.dump({
                'generated': datetime.utcnow().isoformat() + 'Z',
                'total_files': len(index),
                'files': index
            }, f, indent=2)
        
        print(f"✅ Index saved: {index_path}")
        
        return report


def main():
    parser = argparse.ArgumentParser(
        description="Comprehensive Laptop Vacuum - ALL drives, ALL systems"
    )
    parser.add_argument(
        '--drives',
        nargs='+',
        help='Specific drives to scan (e.g., C:\\ D:\\ or /home /mnt/data)'
    )
    parser.add_argument(
        '--max-size',
        type=int,
        default=500,
        help='Maximum file size in MB (default: 500)'
    )
    parser.add_argument(
        '--max-files-per-drive',
        type=int,
        default=50000,
        help='Maximum files to harvest per drive (default: 50000)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print("🌊 COMPREHENSIVE LAPTOP VACUUM v1.0")
    print("   Nuclear option: Crawl, vacuum, harvest EVERYTHING")
    print("="*70)
    print("\n⚠️  WARNING: This will scan ALL drives and copy ALL relevant files")
    print("   This may take significant time and disk space")
    print("\n💡 What's considered 'relevant':")
    print("   • Code files (.py, .js, .java, etc.)")
    print("   • ML models (.pt, .h5, .onnx, etc.)")
    print("   • Datasets (.csv, .parquet, .jsonl, etc.)")
    print("   • Config files (.json, .yaml, .toml, etc.)")
    print("   • Documentation (.md, .txt, .rst, etc.)")
    print("   • Build files (requirements.txt, package.json, etc.)")
    print("   • Files with relevant keywords (TIA, architect, citadel, etc.)")
    print(f"\n📏 Max file size: {args.max_size} MB")
    print(f"📊 Max files per drive: {args.max_files_per_drive:,}")
    
    response = input("\n🤔 Continue? (yes/no): ")
    if response.lower() != 'yes':
        print("❌ Aborted")
        sys.exit(0)
    
    vacuum = ComprehensiveLaptopVacuum(max_file_size_mb=args.max_size)
    vacuum.vacuum_all_drives(args.drives, args.max_files_per_drive)
    vacuum.generate_report()
    
    print("\n" + "="*70)
    print("✅ VACUUM COMPLETE")
    print("="*70)
    
    print(f"\n📁 Harvested files location:")
    print(f"   {vacuum.storage_root}")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"   1. Review harvest: {vacuum.storage_root}")
    print(f"   2. Check report: {vacuum.storage_root / 'vacuum_report.json'}")
    print(f"   3. Commit and push:")
    print(f"      git add data/Mapping-and-Inventory-storage/laptop_vacuum/")
    print(f"      git commit -m '🌊 Comprehensive laptop vacuum complete'")
    print(f"      git push")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    main()
