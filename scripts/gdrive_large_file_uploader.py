#!/usr/bin/env python3
"""
🚀 GDRIVE LARGE FILE UPLOADER
Authority: Citadel Architect v25.0.OMNI+
Purpose: Upload large files (>100MB) to HuggingFace Datasets
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import json
import hashlib

try:
    from huggingface_hub import HfApi, create_repo, upload_file
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️  huggingface_hub not installed. Install with: pip install huggingface_hub")


class GDriveLargeFileUploader:
    """Upload large GDrive files to HuggingFace Datasets"""
    
    def __init__(self, hf_token: str = None):
        self.hf_token = hf_token or os.getenv("HF_TOKEN")
        if not self.hf_token:
            raise ValueError("HF_TOKEN environment variable not set")
        
        if not HF_AVAILABLE:
            raise ImportError("huggingface_hub not installed")
        
        self.api = HfApi(token=self.hf_token)
        self.upload_log = []
    
    def create_dataset_repo(self, repo_name: str, private: bool = True) -> str:
        """Create HuggingFace dataset repository"""
        try:
            repo_id = f"DJ-Goanna-Coding/{repo_name}"
            
            # Try to create repo (will skip if exists)
            create_repo(
                repo_id=repo_id,
                token=self.hf_token,
                repo_type="dataset",
                private=private,
                exist_ok=True
            )
            
            print(f"✅ Dataset repo ready: https://huggingface.co/datasets/{repo_id}")
            return repo_id
            
        except Exception as e:
            print(f"❌ Error creating repo: {e}")
            return None
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    
    def upload_file_to_dataset(
        self,
        file_path: Path,
        repo_id: str,
        path_in_repo: str = None
    ) -> Dict[str, Any]:
        """Upload single file to HuggingFace Dataset"""
        
        if not file_path.exists():
            return {"error": "File not found", "file": str(file_path)}
        
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        if path_in_repo is None:
            path_in_repo = file_path.name
        
        print(f"\n📤 Uploading: {file_path.name} ({file_size_mb:.2f} MB)")
        print(f"   To: {repo_id}/{path_in_repo}")
        
        result = {
            "file": str(file_path),
            "size_mb": file_size_mb,
            "repo_id": repo_id,
            "path_in_repo": path_in_repo,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "success": False
        }
        
        try:
            # Calculate hash before upload
            print(f"   🔐 Calculating hash...")
            file_hash = self.calculate_file_hash(file_path)
            result["sha256"] = file_hash
            
            # Upload file
            print(f"   ⬆️  Uploading...")
            upload_result = upload_file(
                path_or_fileobj=str(file_path),
                path_in_repo=path_in_repo,
                repo_id=repo_id,
                repo_type="dataset",
                token=self.hf_token
            )
            
            result["success"] = True
            result["url"] = f"https://huggingface.co/datasets/{repo_id}/blob/main/{path_in_repo}"
            print(f"   ✅ Upload complete!")
            print(f"   🔗 URL: {result['url']}")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Upload failed: {e}")
        
        self.upload_log.append(result)
        return result
    
    def upload_directory(
        self,
        dir_path: Path,
        repo_id: str,
        file_pattern: str = "*",
        min_size_mb: float = 100.0
    ) -> List[Dict[str, Any]]:
        """Upload all large files from directory"""
        
        print(f"\n📁 Scanning: {dir_path}")
        print(f"   Pattern: {file_pattern}")
        print(f"   Min size: {min_size_mb} MB")
        
        large_files = []
        for file_path in dir_path.rglob(file_pattern):
            if file_path.is_file():
                size_mb = file_path.stat().st_size / (1024 * 1024)
                if size_mb >= min_size_mb:
                    large_files.append((file_path, size_mb))
        
        large_files.sort(key=lambda x: x[1], reverse=True)  # Largest first
        
        print(f"\n📊 Found {len(large_files)} large files:")
        total_size = sum(size for _, size in large_files)
        print(f"   Total size: {total_size:.2f} MB ({total_size / 1024:.2f} GB)")
        
        results = []
        for i, (file_path, size_mb) in enumerate(large_files, 1):
            print(f"\n[{i}/{len(large_files)}]")
            
            # Generate path in repo (preserve directory structure)
            rel_path = file_path.relative_to(dir_path)
            path_in_repo = str(rel_path).replace('\\', '/')
            
            result = self.upload_file_to_dataset(file_path, repo_id, path_in_repo)
            results.append(result)
        
        return results
    
    def save_upload_manifest(self, output_path: Path) -> None:
        """Save upload manifest"""
        manifest = {
            "upload_session": datetime.utcnow().isoformat() + "Z",
            "total_files": len(self.upload_log),
            "successful_uploads": sum(1 for r in self.upload_log if r.get("success")),
            "failed_uploads": sum(1 for r in self.upload_log if not r.get("success")),
            "total_size_mb": sum(r.get("size_mb", 0) for r in self.upload_log),
            "uploads": self.upload_log
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n📄 Upload manifest saved: {output_path}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="GDrive Large File Uploader to HuggingFace")
    parser.add_argument("--source", required=True, help="Source directory or file")
    parser.add_argument("--repo-name", required=True, help="HuggingFace dataset repo name")
    parser.add_argument("--min-size", type=float, default=100.0, help="Minimum file size in MB")
    parser.add_argument("--pattern", default="*", help="File pattern (e.g., '*.mp4')")
    parser.add_argument("--private", action="store_true", help="Create private dataset")
    
    args = parser.parse_args()
    
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("🚀 GDRIVE LARGE FILE UPLOADER")
    print("   Authority: Citadel Architect v25.0.OMNI+")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    try:
        uploader = GDriveLargeFileUploader()
        
        # Create dataset repo
        repo_id = uploader.create_dataset_repo(args.repo_name, private=args.private)
        if not repo_id:
            sys.exit(1)
        
        source_path = Path(args.source)
        
        # Upload
        if source_path.is_file():
            # Single file
            result = uploader.upload_file_to_dataset(source_path, repo_id)
        elif source_path.is_dir():
            # Directory
            results = uploader.upload_directory(
                source_path,
                repo_id,
                file_pattern=args.pattern,
                min_size_mb=args.min_size
            )
        else:
            print(f"❌ Source not found: {source_path}")
            sys.exit(1)
        
        # Save manifest
        manifest_path = Path("data/gdrive_archive/upload_manifests") / f"{args.repo_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
        uploader.save_upload_manifest(manifest_path)
        
        # Summary
        successful = sum(1 for r in uploader.upload_log if r.get("success"))
        total = len(uploader.upload_log)
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 UPLOAD SUMMARY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n✅ Successful: {successful}/{total}")
        print(f"❌ Failed: {total - successful}")
        print(f"\n🔗 Dataset: https://huggingface.co/datasets/{repo_id}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
