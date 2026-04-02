"""
ARK_CORE // PARTITION_02 // FORENSIC_INGEST.PY
Mackay Court Telemetry - S10 Forensic Data Ingestion
Processes and catalogs forensic data from S10 device.
"""
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path


class ForensicIngestor:
    """S10 forensic data processor and cataloger."""
    
    def __init__(self, intel_path="./S10_CITADEL_OMEGA_INTEL"):
        """Initialize forensic ingestor."""
        self.intel_path = intel_path
        self.manifest_path = os.path.join(intel_path, "forensic_manifest.json")
        os.makedirs(intel_path, exist_ok=True)
    
    def scan_directory(self, scan_path=None):
        """
        Scan a directory and create forensic manifest.
        
        Args:
            scan_path: Path to scan (defaults to intel directory)
        
        Returns:
            dict: Forensic manifest with file metadata
        """
        if scan_path is None:
            scan_path = self.intel_path
        
        manifest = {
            "scan_timestamp": datetime.now().isoformat(),
            "scan_path": scan_path,
            "device_id": "S10_CITADEL",
            "files": []
        }
        
        print(f"🔍 FORENSIC SCAN: {scan_path}")
        
        for root, dirs, files in os.walk(scan_path):
            # Skip hidden directories and git
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.startswith('.'):
                    continue
                
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, scan_path)
                
                try:
                    stat = os.stat(file_path)
                    file_info = {
                        "path": rel_path,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        "extension": Path(file).suffix.lower(),
                        "hash": self._compute_hash(file_path) if stat.st_size < 10_000_000 else None
                    }
                    manifest["files"].append(file_info)
                    print(f"  ✓ {rel_path} ({self._format_size(stat.st_size)})")
                
                except Exception as e:
                    print(f"  ✗ {rel_path}: {e}")
        
        manifest["total_files"] = len(manifest["files"])
        manifest["total_size"] = sum(f["size"] for f in manifest["files"])
        
        return manifest
    
    def save_manifest(self, manifest):
        """Save forensic manifest to disk."""
        with open(self.manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"\n💾 Manifest saved: {self.manifest_path}")
    
    def load_manifest(self):
        """Load existing forensic manifest."""
        if os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'r') as f:
                return json.load(f)
        return None
    
    def analyze_manifest(self, manifest=None):
        """Analyze forensic manifest and generate statistics."""
        if manifest is None:
            manifest = self.load_manifest()
            if manifest is None:
                return {"error": "No manifest found"}
        
        analysis = {
            "total_files": manifest["total_files"],
            "total_size": manifest["total_size"],
            "total_size_formatted": self._format_size(manifest["total_size"]),
            "scan_timestamp": manifest["scan_timestamp"],
            "by_extension": {},
            "large_files": []
        }
        
        # Analyze by extension
        for file in manifest["files"]:
            ext = file["extension"] or "no_extension"
            if ext not in analysis["by_extension"]:
                analysis["by_extension"][ext] = {"count": 0, "size": 0}
            analysis["by_extension"][ext]["count"] += 1
            analysis["by_extension"][ext]["size"] += file["size"]
            
            # Track large files (>10MB)
            if file["size"] > 10_000_000:
                analysis["large_files"].append({
                    "path": file["path"],
                    "size": self._format_size(file["size"])
                })
        
        # Sort large files by size
        analysis["large_files"].sort(key=lambda x: x["size"], reverse=True)
        
        return analysis
    
    def _compute_hash(self, file_path):
        """Compute SHA256 hash of file (for files <10MB)."""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                sha256.update(f.read())
            return sha256.hexdigest()
        except Exception:
            return None
    
    def _format_size(self, size_bytes):
        """Format file size in human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"


def main():
    """Main forensic ingest CLI interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="S10 Forensic Data Ingestor")
    parser.add_argument("--scan", help="Scan directory and create manifest")
    parser.add_argument("--analyze", action="store_true", help="Analyze existing manifest")
    parser.add_argument("--intel-path", default="./S10_CITADEL_OMEGA_INTEL", 
                       help="Intel directory path")
    
    args = parser.parse_args()
    
    ingestor = ForensicIngestor(intel_path=args.intel_path)
    
    if args.scan:
        manifest = ingestor.scan_directory(args.scan)
        print(f"\n📊 SCAN COMPLETE")
        print(f"Total Files: {manifest['total_files']}")
        print(f"Total Size: {ingestor._format_size(manifest['total_size'])}")
        
        ingestor.save_manifest(manifest)
    
    elif args.analyze:
        analysis = ingestor.analyze_manifest()
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            exit(1)
        
        print(f"\n📈 FORENSIC ANALYSIS")
        print(f"Total Files: {analysis['total_files']}")
        print(f"Total Size: {analysis['total_size_formatted']}")
        print(f"Scan Time: {analysis['scan_timestamp']}")
        
        print(f"\n📁 By Extension:")
        for ext, data in sorted(analysis['by_extension'].items(), 
                               key=lambda x: x[1]['size'], reverse=True)[:10]:
            print(f"  {ext}: {data['count']} files ({ingestor._format_size(data['size'])})")
        
        if analysis['large_files']:
            print(f"\n📦 Large Files (>10MB):")
            for file in analysis['large_files'][:10]:
                print(f"  {file['path']}: {file['size']}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
