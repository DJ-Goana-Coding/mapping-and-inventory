#!/usr/bin/env python3
"""
🎯 SMART FILE ROUTER
Authority: Citadel Architect v25.0.OMNI+
Purpose: Route files to appropriate destinations based on size
"""

import os
import json
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple


class SmartFileRouter:
    """Intelligently route files based on size and type"""
    
    SIZE_TIERS = {
        "small": {
            "max_mb": 10,
            "destination": "github",
            "path": "data/Mapping-and-Inventory-storage/laptop/"
        },
        "medium": {
            "max_mb": 100,
            "destination": "hf_space",
            "path": "data/Mapping-and-Inventory-storage/laptop/medium/"
        },
        "large": {
            "max_mb": 1000,
            "destination": "hf_dataset",
            "path": None  # Upload via HuggingFace API
        },
        "xlarge": {
            "max_mb": float('inf'),
            "destination": "manual",
            "path": None  # Manual handling required
        }
    }
    
    def __init__(self, source_dir: Path, output_base: Path):
        self.source_dir = source_dir
        self.output_base = output_base
        self.routing_manifest = {
            "routing_timestamp": datetime.utcnow().isoformat() + "Z",
            "source_directory": str(source_dir),
            "routing_decisions": [],
            "stats": {
                "total_files": 0,
                "total_size_bytes": 0,
                "by_tier": {}
            }
        }
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA256 hash of file"""
        sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception:
            return "error"
    
    def determine_tier(self, file_size_bytes: int) -> str:
        """Determine size tier for a file"""
        size_mb = file_size_bytes / (1024 * 1024)
        
        if size_mb <= self.SIZE_TIERS["small"]["max_mb"]:
            return "small"
        elif size_mb <= self.SIZE_TIERS["medium"]["max_mb"]:
            return "medium"
        elif size_mb <= self.SIZE_TIERS["large"]["max_mb"]:
            return "large"
        else:
            return "xlarge"
    
    def route_file(self, file_path: Path) -> Dict[str, Any]:
        """Route a single file to appropriate destination"""
        
        try:
            stat = file_path.stat()
            size_bytes = stat.st_size
            size_mb = size_bytes / (1024 * 1024)
            
            tier = self.determine_tier(size_bytes)
            tier_config = self.SIZE_TIERS[tier]
            
            routing_decision = {
                "source_path": str(file_path),
                "filename": file_path.name,
                "size_bytes": size_bytes,
                "size_mb": size_mb,
                "tier": tier,
                "destination_type": tier_config["destination"],
                "destination_path": None,
                "hash": None,
                "status": "pending"
            }
            
            # Calculate hash for small/medium files
            if tier in ["small", "medium"]:
                routing_decision["hash"] = self.calculate_file_hash(file_path)
            
            # Determine destination path
            if tier_config["path"]:
                # Preserve directory structure
                rel_path = file_path.relative_to(self.source_dir)
                dest_path = self.output_base / tier_config["path"] / rel_path
                routing_decision["destination_path"] = str(dest_path)
            
            return routing_decision
            
        except Exception as e:
            return {
                "source_path": str(file_path),
                "error": str(e),
                "status": "error"
            }
    
    def copy_file(self, routing_decision: Dict[str, Any]) -> bool:
        """Copy file to destination"""
        
        source_path = Path(routing_decision["source_path"])
        dest_path_str = routing_decision.get("destination_path")
        
        if not dest_path_str:
            # Requires manual handling or API upload
            routing_decision["status"] = "requires_manual_upload"
            return False
        
        dest_path = Path(dest_path_str)
        
        # Check if already exists
        if dest_path.exists():
            existing_size = dest_path.stat().st_size
            if existing_size == routing_decision["size_bytes"]:
                routing_decision["status"] = "already_exists"
                return True
        
        # Copy file
        try:
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, dest_path)
            
            # Verify copy
            if dest_path.exists():
                copied_size = dest_path.stat().st_size
                if copied_size == routing_decision["size_bytes"]:
                    routing_decision["status"] = "copied"
                    return True
                else:
                    routing_decision["status"] = "copy_size_mismatch"
                    return False
            else:
                routing_decision["status"] = "copy_failed"
                return False
                
        except Exception as e:
            routing_decision["status"] = "error"
            routing_decision["error"] = str(e)
            return False
    
    def route_all_files(self) -> Dict[str, Any]:
        """Route all files in source directory"""
        
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎯 SMART FILE ROUTER")
        print("   Authority: Citadel Architect v25.0.OMNI+")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n📁 Source: {self.source_dir}")
        print(f"📂 Output: {self.output_base}")
        
        # Initialize tier stats
        for tier in self.SIZE_TIERS.keys():
            self.routing_manifest["stats"]["by_tier"][tier] = {
                "count": 0,
                "total_size_bytes": 0,
                "total_size_mb": 0.0
            }
        
        # Scan all files
        print(f"\n🔍 Scanning files...")
        all_files = []
        for file_path in self.source_dir.rglob("*"):
            if file_path.is_file():
                all_files.append(file_path)
        
        print(f"   Found {len(all_files)} files")
        
        # Route each file
        print(f"\n🎯 Routing files by size tier...")
        for i, file_path in enumerate(all_files, 1):
            if i % 100 == 0:
                print(f"   Progress: {i}/{len(all_files)}")
            
            routing_decision = self.route_file(file_path)
            self.routing_manifest["routing_decisions"].append(routing_decision)
            
            # Update stats
            tier = routing_decision.get("tier")
            if tier:
                self.routing_manifest["stats"]["by_tier"][tier]["count"] += 1
                size_bytes = routing_decision.get("size_bytes", 0)
                self.routing_manifest["stats"]["by_tier"][tier]["total_size_bytes"] += size_bytes
                self.routing_manifest["stats"]["by_tier"][tier]["total_size_mb"] += size_bytes / (1024 * 1024)
        
        # Overall stats
        self.routing_manifest["stats"]["total_files"] = len(self.routing_manifest["routing_decisions"])
        self.routing_manifest["stats"]["total_size_bytes"] = sum(
            d.get("size_bytes", 0) for d in self.routing_manifest["routing_decisions"]
        )
        
        return self.routing_manifest
    
    def execute_routing(self, tiers_to_copy: List[str] = None) -> None:
        """Execute file copying for specified tiers"""
        
        if tiers_to_copy is None:
            tiers_to_copy = ["small", "medium"]  # Default: copy small/medium only
        
        print(f"\n📦 Executing routing for tiers: {', '.join(tiers_to_copy)}")
        
        for tier in tiers_to_copy:
            tier_decisions = [
                d for d in self.routing_manifest["routing_decisions"]
                if d.get("tier") == tier
            ]
            
            if not tier_decisions:
                continue
            
            print(f"\n{tier.upper()} files ({len(tier_decisions)}):")
            
            copied = 0
            for decision in tier_decisions:
                if self.copy_file(decision):
                    copied += 1
            
            print(f"   ✅ Copied: {copied}/{len(tier_decisions)}")
    
    def save_manifest(self, output_path: Path) -> None:
        """Save routing manifest"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.routing_manifest, f, indent=2)
        print(f"\n📄 Routing manifest saved: {output_path}")
    
    def generate_action_plan(self, output_path: Path) -> None:
        """Generate action plan for manual uploads"""
        
        # Find files requiring manual handling
        large_files = [
            d for d in self.routing_manifest["routing_decisions"]
            if d.get("tier") in ["large", "xlarge"]
        ]
        
        if not large_files:
            return
        
        plan = f"""# 📋 Manual Upload Action Plan

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

## Files Requiring Manual Upload

Total: {len(large_files)} files

### Large Files (100MB - 1GB) → Upload to HuggingFace Datasets

"""
        
        large_tier = [d for d in large_files if d.get("tier") == "large"]
        if large_tier:
            plan += f"Count: {len(large_tier)}\n\n"
            plan += "```bash\n"
            plan += "# Upload to HuggingFace Datasets\n"
            plan += "python scripts/gdrive_large_file_uploader.py \\\n"
            plan += "  --source <source_dir> \\\n"
            plan += "  --repo-name laptop-large-files \\\n"
            plan += "  --min-size 100\n"
            plan += "```\n\n"
        
        plan += f"""
### XLarge Files (>1GB) → Manual Backup Required

"""
        
        xlarge_tier = [d for d in large_files if d.get("tier") == "xlarge"]
        if xlarge_tier:
            plan += f"Count: {len(xlarge_tier)}\n\n"
            plan += "Options:\n"
            plan += "1. Upload to HuggingFace Datasets (recommended)\n"
            plan += "2. Create torrent files for P2P distribution\n"
            plan += "3. Copy to external drive\n\n"
            plan += "| File | Size |\n"
            plan += "|------|------|\n"
            
            for decision in sorted(xlarge_tier, key=lambda x: x.get("size_mb", 0), reverse=True)[:20]:
                filename = decision.get("filename", "unknown")
                size_mb = decision.get("size_mb", 0)
                size_gb = size_mb / 1024
                plan += f"| {filename} | {size_gb:.2f} GB |\n"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(plan)
        
        print(f"📋 Action plan saved: {output_path}")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart File Router")
    parser.add_argument("--source", required=True, type=Path, help="Source directory")
    parser.add_argument("--output", default=".", type=Path, help="Output base directory")
    parser.add_argument("--execute", action="store_true", help="Execute file copying")
    parser.add_argument("--tiers", nargs="+", default=["small", "medium"], help="Tiers to copy")
    
    args = parser.parse_args()
    
    router = SmartFileRouter(args.source, args.output)
    
    # Route all files
    manifest = router.route_all_files()
    
    # Print tier summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 ROUTING SUMMARY")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    for tier, stats in manifest["stats"]["by_tier"].items():
        if stats["count"] > 0:
            count = stats["count"]
            size_mb = stats["total_size_mb"]
            dest = router.SIZE_TIERS[tier]["destination"]
            print(f"\n{tier.upper()}: {count} files ({size_mb:.2f} MB)")
            print(f"   Destination: {dest}")
    
    # Execute routing if requested
    if args.execute:
        router.execute_routing(tiers_to_copy=args.tiers)
    
    # Save manifest
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    manifest_path = args.output / "data" / "laptop_inventory" / f"routing_manifest_{timestamp}.json"
    router.save_manifest(manifest_path)
    
    # Generate action plan
    action_plan_path = args.output / "data" / "laptop_inventory" / f"manual_upload_plan_{timestamp}.md"
    router.generate_action_plan(action_plan_path)


if __name__ == "__main__":
    main()
