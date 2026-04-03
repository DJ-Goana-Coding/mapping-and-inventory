#!/usr/bin/env python3
"""
LAPTOP FILESYSTEM SCANNER
Scans local laptop directories for models, libraries, scripts, and documents
Generates manifest for Bridge Agent protocol

Usage:
    python laptop_filesystem_scanner.py --scan /path/to/directory
    python laptop_filesystem_scanner.py --full-scan  # Scans common locations
"""

import os
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
import sys


class LaptopScanner:
    """Scanner for laptop filesystem - generates inventory manifest"""
    
    def __init__(self):
        self.scan_results = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown",
            "categories": {
                "models": [],
                "libraries": [],
                "scripts": [],
                "documents": [],
                "datasets": [],
                "other": []
            },
            "summary": {
                "total_files": 0,
                "total_size_bytes": 0
            }
        }
    
    def scan_directory(self, directory, max_depth=5):
        """Scan directory recursively up to max_depth"""
        print(f"🔍 Scanning: {directory}")
        
        try:
            for root, dirs, files in os.walk(directory):
                # Calculate depth
                depth = root[len(directory):].count(os.sep)
                if depth > max_depth:
                    del dirs[:]  # Don't recurse deeper
                    continue
                
                # Skip hidden directories and common excludes
                dirs[:] = [d for d in dirs if not d.startswith('.') 
                          and d not in ['node_modules', '__pycache__', 'venv', 'env']]
                
                for file in files:
                    if file.startswith('.'):
                        continue  # Skip hidden files
                    
                    file_path = os.path.join(root, file)
                    self.process_file(file_path)
        
        except PermissionError as e:
            print(f"⚠️  Permission denied: {directory}")
        except Exception as e:
            print(f"❌ Error scanning {directory}: {e}")
    
    def process_file(self, file_path):
        """Process individual file and categorize"""
        try:
            stat = os.stat(file_path)
            
            # Skip very large files (> 1GB)
            if stat.st_size > 1024 * 1024 * 1024:
                return
            
            file_info = {
                "path": file_path,
                "filename": os.path.basename(file_path),
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat() + "Z"
            }
            
            # Categorize file
            category = self.categorize_file(file_path)
            self.scan_results["categories"][category].append(file_info)
            
            # Update summary
            self.scan_results["summary"]["total_files"] += 1
            self.scan_results["summary"]["total_size_bytes"] += stat.st_size
        
        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
    
    def categorize_file(self, file_path):
        """Categorize file based on extension and path"""
        file_lower = file_path.lower()
        
        # Model files
        model_exts = ['.h5', '.pkl', '.pt', '.pth', '.safetensors', '.gguf', '.bin', '.model', '.weights']
        if any(file_lower.endswith(ext) for ext in model_exts):
            return "models"
        
        # Library/code files
        code_exts = ['.py', '.js', '.ts', '.go', '.java', '.cpp', '.c', '.rs']
        if any(file_lower.endswith(ext) for ext in code_exts):
            return "libraries"
        
        # Scripts
        script_exts = ['.sh', '.bash', '.zsh', '.ps1', '.bat']
        if any(file_lower.endswith(ext) for ext in script_exts):
            return "scripts"
        
        # Documents
        doc_exts = ['.md', '.txt', '.pdf', '.docx', '.doc', '.odt']
        if any(file_lower.endswith(ext) for ext in doc_exts):
            return "documents"
        
        # Datasets
        dataset_exts = ['.csv', '.json', '.jsonl', '.parquet', '.arrow', '.feather']
        if any(file_lower.endswith(ext) for ext in dataset_exts):
            return "datasets"
        
        return "other"
    
    def save_manifest(self, output_path):
        """Save scan results as JSON manifest"""
        with open(output_path, 'w') as f:
            json.dump(self.scan_results, f, indent=2)
        
        print(f"\n✅ Manifest saved: {output_path}")
        print(f"   Total Files: {self.scan_results['summary']['total_files']}")
        print(f"   Total Size: {self.scan_results['summary']['total_size_bytes'] / (1024**3):.2f} GB")
        print("\nCategory Breakdown:")
        for category, files in self.scan_results["categories"].items():
            if len(files) > 0:
                print(f"   {category}: {len(files)} files")


def main():
    parser = argparse.ArgumentParser(description="Laptop Filesystem Scanner")
    parser.add_argument("--scan", help="Directory to scan")
    parser.add_argument("--full-scan", action="store_true", 
                       help="Scan common locations (~/Documents, ~/Downloads, etc.)")
    parser.add_argument("--output", default="laptop_manifest.json",
                       help="Output manifest file (default: laptop_manifest.json)")
    parser.add_argument("--max-depth", type=int, default=5,
                       help="Maximum directory depth (default: 5)")
    
    args = parser.parse_args()
    
    if not args.scan and not args.full_scan:
        parser.print_help()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("💻 LAPTOP FILESYSTEM SCANNER")
    print("=" * 60 + "\n")
    
    scanner = LaptopScanner()
    
    if args.full_scan:
        # Scan common locations
        home = Path.home()
        common_dirs = [
            home / "Documents",
            home / "Downloads",
            home / "Desktop",
            home / "Projects",
            home / "Code",
            home / "models"
        ]
        
        for directory in common_dirs:
            if directory.exists():
                scanner.scan_directory(str(directory), args.max_depth)
    
    if args.scan:
        scanner.scan_directory(args.scan, args.max_depth)
    
    scanner.save_manifest(args.output)
    
    print("\n" + "=" * 60)
    print("🎯 NEXT STEPS:")
    print("=" * 60)
    print("1. Review the generated manifest")
    print("2. Copy manifest to Mapping-and-Inventory repo:")
    print(f"   cp {args.output} /path/to/mapping-and-inventory/data/laptop_inventory/")
    print("3. Commit and push to trigger laptop_push_workflow")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
