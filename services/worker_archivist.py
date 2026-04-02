"""
THE ARCHIVIST WORKER
Jurisdiction: GENESIS_VAULT
Primary Task: Automatic filing, MD5 hashing, and folder structuring

This worker processes files from the Research cargo bays, computes MD5 hashes
for verification, organizes files into structured folders, and maintains
an index of all processed files.
"""

import os
import sys
import json
import hashlib
import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Repository root
REPO_ROOT = Path(__file__).parent.parent
WORKER_STATUS_PATH = REPO_ROOT / "worker_status.json"
ARCHIVE_INDEX_PATH = REPO_ROOT / "archive_index.json"


class ArchivistWorker:
    """The Archivist - Automatic filing and MD5 hashing for GENESIS_VAULT"""
    
    def __init__(self):
        self.worker_id = "archivist"
        self.files_processed = 0
        self.errors = []
        self.archive_index = self._load_archive_index()
    
    def _load_archive_index(self) -> Dict:
        """Load existing archive index or create new one"""
        if ARCHIVE_INDEX_PATH.exists():
            with open(ARCHIVE_INDEX_PATH, 'r') as f:
                return json.load(f)
        return {
            "created": datetime.datetime.utcnow().isoformat(),
            "last_updated": None,
            "total_files": 0,
            "files": {}
        }
    
    def _save_archive_index(self):
        """Save archive index to disk"""
        self.archive_index["last_updated"] = datetime.datetime.utcnow().isoformat()
        self.archive_index["total_files"] = len(self.archive_index["files"])
        
        with open(ARCHIVE_INDEX_PATH, 'w') as f:
            json.dump(self.archive_index, f, indent=2)
    
    def compute_md5(self, filepath: Path) -> str:
        """Compute MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        try:
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            self.errors.append(f"MD5 error for {filepath}: {e}")
            return None
    
    def organize_file(self, filepath: Path, source_dir: str) -> Optional[Dict]:
        """
        Organize a file and compute its metadata
        
        Args:
            filepath: Path to the file
            source_dir: Source directory (GDrive, Oppo, S10, Laptop)
        
        Returns:
            Dictionary with file metadata or None on error
        """
        try:
            # Get file stats
            stats = filepath.stat()
            
            # Compute MD5
            md5_hash = self.compute_md5(filepath)
            if md5_hash is None:
                return None
            
            # Build metadata
            metadata = {
                "filename": filepath.name,
                "path": str(filepath.relative_to(REPO_ROOT)),
                "source": source_dir,
                "size_bytes": stats.st_size,
                "md5": md5_hash,
                "modified": datetime.datetime.fromtimestamp(stats.st_mtime).isoformat(),
                "indexed": datetime.datetime.utcnow().isoformat(),
            }
            
            # Add to archive index
            self.archive_index["files"][str(filepath.relative_to(REPO_ROOT))] = metadata
            self.files_processed += 1
            
            return metadata
            
        except Exception as e:
            self.errors.append(f"Error organizing {filepath}: {e}")
            return None
    
    def scan_directory(self, directory: Path, source_name: str, max_files: int = None) -> int:
        """
        Scan a directory and organize all files
        
        Args:
            directory: Directory to scan
            source_name: Name of the source (GDrive, Oppo, S10, Laptop)
            max_files: Maximum number of files to process (None for unlimited)
        
        Returns:
            Number of files processed
        """
        if not directory.exists():
            print(f"⚠️  Directory does not exist: {directory}")
            return 0
        
        print(f"📂 Scanning {source_name}: {directory}")
        
        file_count = 0
        for filepath in directory.rglob('*'):
            if filepath.is_file():
                # Skip hidden files and README
                if filepath.name.startswith('.') or filepath.name == 'README.md':
                    continue
                
                metadata = self.organize_file(filepath, source_name)
                if metadata:
                    file_count += 1
                    if file_count % 100 == 0:
                        print(f"   Processed {file_count} files...")
                
                # Check max files limit
                if max_files and file_count >= max_files:
                    print(f"   Reached max files limit: {max_files}")
                    break
        
        return file_count
    
    def run(self, max_files_per_source: int = None):
        """
        Run the Archivist worker
        
        Args:
            max_files_per_source: Maximum files to process per source (None for unlimited)
        """
        print("🗄️  THE ARCHIVIST WORKER — Starting...")
        print("=" * 60)
        
        start_time = datetime.datetime.utcnow()
        
        # Scan all Research cargo bays
        research_dir = REPO_ROOT / "Research"
        sources = ["GDrive", "Oppo", "S10", "Laptop"]
        
        total_processed = 0
        for source in sources:
            source_dir = research_dir / source
            count = self.scan_directory(source_dir, source, max_files_per_source)
            total_processed += count
        
        # Scan S10_CITADEL_OMEGA_INTEL
        s10_intel_dir = REPO_ROOT / "S10_CITADEL_OMEGA_INTEL"
        count = self.scan_directory(s10_intel_dir, "S10_INTEL", max_files_per_source)
        total_processed += count
        
        # Save archive index
        self._save_archive_index()
        
        # Update worker status
        self._update_worker_status(start_time, total_processed)
        
        # Print summary
        print("=" * 60)
        print(f"✅ THE ARCHIVIST WORKER — Complete")
        print(f"   Files processed: {total_processed}")
        print(f"   Total files in index: {len(self.archive_index['files'])}")
        print(f"   Errors: {len(self.errors)}")
        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"   - {error}")
    
    def _update_worker_status(self, start_time: datetime.datetime, files_processed: int):
        """Update worker_status.json with run results"""
        try:
            if WORKER_STATUS_PATH.exists():
                with open(WORKER_STATUS_PATH, 'r') as f:
                    status = json.load(f)
            else:
                status = {"workers": {}}
            
            end_time = datetime.datetime.utcnow()
            success = len(self.errors) == 0
            
            # Update archivist worker status
            if "archivist" not in status["workers"]:
                status["workers"]["archivist"] = {}
            
            status["workers"]["archivist"].update({
                "status": "OPERATIONAL" if success else "ERROR",
                "last_run": end_time.isoformat(),
                "last_success": end_time.isoformat() if success else status["workers"]["archivist"].get("last_success"),
                "total_runs": status["workers"]["archivist"].get("total_runs", 0) + 1,
                "total_files_processed": status["workers"]["archivist"].get("total_files_processed", 0) + files_processed,
                "errors": self.errors[-10:] if self.errors else []  # Keep last 10 errors
            })
            
            status["last_updated"] = end_time.isoformat()
            
            with open(WORKER_STATUS_PATH, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to update worker_status.json: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="The Archivist Worker - Automatic filing and MD5 hashing")
    parser.add_argument("--max-files", type=int, default=None, help="Maximum files to process per source")
    parser.add_argument("--test", action="store_true", help="Test mode - process only 10 files per source")
    
    args = parser.parse_args()
    
    max_files = 10 if args.test else args.max_files
    
    worker = ArchivistWorker()
    worker.run(max_files_per_source=max_files)


if __name__ == "__main__":
    main()
