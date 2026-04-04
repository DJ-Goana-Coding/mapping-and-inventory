#!/usr/bin/env python3
"""
🎵 LAPTOP MEDIA HARVESTER
Authority: Citadel Architect v25.0.OMNI+
Purpose: Extract and catalog all media files (music, art, video)
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import mimetypes


class MediaHarvester:
    """Extract and catalog media files from laptop"""
    
    MEDIA_CATEGORIES = {
        "music": {
            "extensions": [".mp3", ".wav", ".flac", ".m4a", ".aac", ".ogg", ".wma"],
            "locations": [
                "Music",
                "Downloads",
                "Documents/Music",
                "OneDrive/Music"
            ]
        },
        "art": {
            "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".psd", ".ai", ".xcf"],
            "locations": [
                "Pictures",
                "Documents/Art",
                "Documents/Images",
                "Desktop",
                "Downloads"
            ]
        },
        "video": {
            "extensions": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
            "locations": [
                "Videos",
                "Downloads",
                "Documents/Videos"
            ]
        }
    }
    
    def __init__(self, base_paths: List[Path]):
        self.base_paths = base_paths
        self.catalog = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "base_paths": [str(p) for p in base_paths],
            "music": [],
            "art": [],
            "video": [],
            "stats": {
                "total_files": 0,
                "total_size_bytes": 0,
                "by_category": {}
            }
        }
    
    def calculate_file_hash(self, file_path: Path, quick: bool = True) -> str:
        """Calculate file hash (quick mode uses first 1MB)"""
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                if quick:
                    # Quick hash: first 1MB only
                    data = f.read(1024 * 1024)
                    sha256.update(data)
                else:
                    # Full hash
                    for chunk in iter(lambda: f.read(8192), b''):
                        sha256.update(chunk)
            return sha256.hexdigest()[:16]  # First 16 chars
        except Exception:
            return "error"
    
    def extract_media_metadata(self, file_path: Path, category: str) -> Dict[str, Any]:
        """Extract metadata from media file"""
        metadata = {
            "path": str(file_path),
            "filename": file_path.name,
            "extension": file_path.suffix.lower(),
            "size_bytes": 0,
            "size_mb": 0.0,
            "modified": "",
            "hash": "",
            "category": category
        }
        
        try:
            stat = file_path.stat()
            metadata["size_bytes"] = stat.st_size
            metadata["size_mb"] = stat.st_size / (1024 * 1024)
            metadata["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            
            # Quick hash for deduplication
            metadata["hash"] = self.calculate_file_hash(file_path, quick=True)
            
            # Category-specific metadata
            if category == "music":
                metadata["artist"] = "Unknown"
                metadata["album"] = "Unknown"
                metadata["title"] = file_path.stem
                # Could use mutagen library here for ID3 tags
            
            elif category == "art":
                metadata["width"] = None
                metadata["height"] = None
                # Could use Pillow library here for dimensions
            
            elif category == "video":
                metadata["duration"] = None
                metadata["resolution"] = None
                # Could use ffprobe here for video info
                
        except Exception as e:
            metadata["error"] = str(e)
        
        return metadata
    
    def scan_directory(self, directory: Path, category: str, extensions: List[str]) -> List[Dict[str, Any]]:
        """Scan directory for media files"""
        files = []
        
        if not directory.exists():
            print(f"   ⚠️  Directory not found: {directory}")
            return files
        
        print(f"   🔍 Scanning: {directory}")
        
        try:
            for ext in extensions:
                pattern = f"**/*{ext}"
                for file_path in directory.glob(pattern):
                    if file_path.is_file():
                        metadata = self.extract_media_metadata(file_path, category)
                        files.append(metadata)
        except PermissionError:
            print(f"   ❌ Permission denied: {directory}")
        except Exception as e:
            print(f"   ❌ Error scanning {directory}: {e}")
        
        return files
    
    def harvest_category(self, category: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Harvest all files for a category"""
        print(f"\n📁 Harvesting {category.upper()}")
        
        all_files = []
        extensions = config["extensions"]
        locations = config["locations"]
        
        for base_path in self.base_paths:
            for location in locations:
                dir_path = base_path / location
                files = self.scan_directory(dir_path, category, extensions)
                all_files.extend(files)
        
        # Deduplicate by hash
        seen_hashes = set()
        unique_files = []
        for file_info in all_files:
            file_hash = file_info.get("hash")
            if file_hash and file_hash not in seen_hashes:
                seen_hashes.add(file_hash)
                unique_files.append(file_info)
        
        duplicates_removed = len(all_files) - len(unique_files)
        total_size = sum(f.get("size_bytes", 0) for f in unique_files)
        
        print(f"   ✅ Found {len(unique_files)} unique files ({duplicates_removed} duplicates removed)")
        print(f"   💾 Total size: {total_size / 1024 / 1024:.2f} MB")
        
        return unique_files
    
    def harvest_all(self) -> Dict[str, Any]:
        """Harvest all media categories"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎵 LAPTOP MEDIA HARVESTER")
        print("   Authority: Citadel Architect v25.0.OMNI+")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        for category, config in self.MEDIA_CATEGORIES.items():
            files = self.harvest_category(category, config)
            self.catalog[category] = files
            
            # Update stats
            self.catalog["stats"]["by_category"][category] = {
                "count": len(files),
                "total_size_bytes": sum(f.get("size_bytes", 0) for f in files),
                "total_size_mb": sum(f.get("size_mb", 0) for f in files)
            }
        
        # Overall stats
        self.catalog["stats"]["total_files"] = sum(
            len(self.catalog[cat]) for cat in ["music", "art", "video"]
        )
        self.catalog["stats"]["total_size_bytes"] = sum(
            self.catalog["stats"]["by_category"][cat]["total_size_bytes"]
            for cat in ["music", "art", "video"]
        )
        
        return self.catalog
    
    def save_catalog(self, output_path: Path) -> None:
        """Save media catalog"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.catalog, f, indent=2)
        print(f"\n📄 Catalog saved: {output_path}")
    
    def generate_report(self, output_path: Path) -> None:
        """Generate human-readable report"""
        report = f"""# 🎵 Media Harvest Report

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

## 📊 Summary

- **Total Files:** {self.catalog['stats']['total_files']:,}
- **Total Size:** {self.catalog['stats']['total_size_bytes'] / (1024**3):.2f} GB

## 📁 By Category

"""
        
        for category in ["music", "art", "video"]:
            stats = self.catalog["stats"]["by_category"].get(category, {})
            count = stats.get("count", 0)
            size_mb = stats.get("total_size_mb", 0)
            
            report += f"""### {category.title()}
- Files: {count:,}
- Size: {size_mb:.2f} MB ({size_mb / 1024:.2f} GB)

"""
            
            # Show top 10 largest files
            files = sorted(
                self.catalog[category],
                key=lambda x: x.get("size_mb", 0),
                reverse=True
            )[:10]
            
            if files:
                report += "**Top 10 Largest Files:**\n\n"
                for i, file_info in enumerate(files, 1):
                    filename = file_info.get("filename", "unknown")
                    size_mb = file_info.get("size_mb", 0)
                    report += f"{i}. {filename} ({size_mb:.2f} MB)\n"
                report += "\n"
        
        report += f"""---

**Next Steps:**
1. Review catalog at: `{output_path.parent / 'media_harvest_catalog.json'}`
2. Run smart file router to copy files by size
3. Upload large files to HuggingFace Datasets
4. Commit small files to GitHub
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"📊 Report saved: {output_path}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Laptop Media Harvester")
    parser.add_argument(
        "--paths",
        nargs="+",
        default=[Path.home()],
        type=Path,
        help="Base paths to scan (default: user home directory)"
    )
    parser.add_argument(
        "--output-dir",
        default="data/laptop_inventory",
        type=Path,
        help="Output directory for catalog"
    )
    
    args = parser.parse_args()
    
    harvester = MediaHarvester(args.paths)
    catalog = harvester.harvest_all()
    
    # Save catalog
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    catalog_path = args.output_dir / f"media_harvest_catalog_{timestamp}.json"
    harvester.save_catalog(catalog_path)
    
    # Generate report
    report_path = args.output_dir / f"media_harvest_report_{timestamp}.md"
    harvester.generate_report(report_path)
    
    # Summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 HARVEST SUMMARY")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n✅ Total files: {catalog['stats']['total_files']:,}")
    print(f"💾 Total size: {catalog['stats']['total_size_bytes'] / (1024**3):.2f} GB")
    print(f"\n📁 By category:")
    for category, stats in catalog['stats']['by_category'].items():
        print(f"   {category.title()}: {stats['count']:,} files ({stats['total_size_mb']:.2f} MB)")


if __name__ == "__main__":
    main()
