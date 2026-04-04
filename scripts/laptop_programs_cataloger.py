#!/usr/bin/env python3
"""
🎯 LAPTOP PROGRAMS CATALOGER
Authority: Citadel Architect v25.0.OMNI+
Purpose: Catalog all installed programs and portable apps
"""

import os
import json
import winreg
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any


class ProgramsCataloger:
    """Catalog installed programs on Windows"""
    
    REGISTRY_PATHS = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    COMMON_PROGRAM_DIRS = [
        Path("C:/Program Files"),
        Path("C:/Program Files (x86)"),
        Path.home() / "AppData/Local/Programs"
    ]
    
    PORTABLE_APP_LOCATIONS = [
        "Desktop",
        "Downloads",
        "Documents/Apps",
        "Documents/Portable"
    ]
    
    def __init__(self):
        self.catalog = {
            "scan_timestamp": datetime.utcnow().isoformat() + "Z",
            "installed_programs": [],
            "portable_apps": [],
            "stats": {
                "total_installed": 0,
                "total_portable": 0,
                "total_size_bytes": 0
            }
        }
    
    def get_registry_programs(self) -> List[Dict[str, Any]]:
        """Get programs from Windows Registry"""
        programs = []
        
        print("🔍 Scanning Windows Registry for installed programs...")
        
        for reg_path in self.REGISTRY_PATHS:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                
                i = 0
                while True:
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        
                        program_info = {}
                        
                        # Try to get program details
                        try:
                            program_info["name"] = winreg.QueryValueEx(subkey, "DisplayName")[0]
                        except:
                            pass
                        
                        try:
                            program_info["version"] = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                        except:
                            program_info["version"] = "Unknown"
                        
                        try:
                            program_info["publisher"] = winreg.QueryValueEx(subkey, "Publisher")[0]
                        except:
                            program_info["publisher"] = "Unknown"
                        
                        try:
                            program_info["install_location"] = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                        except:
                            program_info["install_location"] = "Unknown"
                        
                        try:
                            program_info["install_date"] = winreg.QueryValueEx(subkey, "InstallDate")[0]
                        except:
                            program_info["install_date"] = "Unknown"
                        
                        try:
                            size = winreg.QueryValueEx(subkey, "EstimatedSize")[0]
                            program_info["size_kb"] = size
                            program_info["size_mb"] = size / 1024
                        except:
                            program_info["size_kb"] = 0
                            program_info["size_mb"] = 0.0
                        
                        if "name" in program_info:
                            programs.append(program_info)
                        
                        winreg.CloseKey(subkey)
                        i += 1
                        
                    except OSError:
                        break
                
                winreg.CloseKey(key)
                
            except Exception as e:
                print(f"   ⚠️  Error accessing {reg_path}: {e}")
        
        # Sort by name
        programs.sort(key=lambda x: x.get("name", "").lower())
        
        print(f"   ✅ Found {len(programs)} installed programs")
        return programs
    
    def scan_portable_apps(self) -> List[Dict[str, Any]]:
        """Scan for portable applications (exe files in user directories)"""
        portable_apps = []
        
        print("\n🔍 Scanning for portable applications...")
        
        for location in self.PORTABLE_APP_LOCATIONS:
            dir_path = Path.home() / location
            
            if not dir_path.exists():
                continue
            
            print(f"   📁 Scanning: {dir_path}")
            
            try:
                # Look for .exe files
                for exe_file in dir_path.rglob("*.exe"):
                    try:
                        stat = exe_file.stat()
                        
                        app_info = {
                            "name": exe_file.stem,
                            "path": str(exe_file),
                            "size_bytes": stat.st_size,
                            "size_mb": stat.st_size / (1024 * 1024),
                            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "type": "portable_exe"
                        }
                        
                        portable_apps.append(app_info)
                    except Exception as e:
                        pass
            
            except PermissionError:
                print(f"      ⚠️  Permission denied")
            except Exception as e:
                print(f"      ⚠️  Error: {e}")
        
        # Deduplicate by name
        seen_names = set()
        unique_apps = []
        for app in portable_apps:
            name = app.get("name", "").lower()
            if name and name not in seen_names:
                seen_names.add(name)
                unique_apps.append(app)
        
        print(f"   ✅ Found {len(unique_apps)} portable apps")
        return unique_apps
    
    def catalog_all(self) -> Dict[str, Any]:
        """Run complete program cataloging"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🎯 LAPTOP PROGRAMS CATALOGER")
        print("   Authority: Citadel Architect v25.0.OMNI+")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        # Windows-only features
        if os.name == 'nt':
            self.catalog["installed_programs"] = self.get_registry_programs()
        else:
            print("⚠️  Registry scanning only available on Windows")
        
        # Portable apps (cross-platform)
        self.catalog["portable_apps"] = self.scan_portable_apps()
        
        # Calculate stats
        self.catalog["stats"]["total_installed"] = len(self.catalog["installed_programs"])
        self.catalog["stats"]["total_portable"] = len(self.catalog["portable_apps"])
        
        total_size = sum(p.get("size_kb", 0) for p in self.catalog["installed_programs"]) * 1024
        total_size += sum(p.get("size_bytes", 0) for p in self.catalog["portable_apps"])
        self.catalog["stats"]["total_size_bytes"] = total_size
        
        return self.catalog
    
    def save_catalog(self, output_path: Path) -> None:
        """Save programs catalog"""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(self.catalog, f, indent=2)
        print(f"\n📄 Catalog saved: {output_path}")
    
    def generate_report(self, output_path: Path) -> None:
        """Generate human-readable report"""
        report = f"""# 🎯 Programs Catalog Report

**Generated:** {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}

## 📊 Summary

- **Installed Programs:** {self.catalog['stats']['total_installed']}
- **Portable Apps:** {self.catalog['stats']['total_portable']}
- **Total Size:** {self.catalog['stats']['total_size_bytes'] / (1024**3):.2f} GB

## 💾 Installed Programs

"""
        
        # Sort by size
        programs = sorted(
            self.catalog["installed_programs"],
            key=lambda x: x.get("size_mb", 0),
            reverse=True
        )
        
        if programs:
            report += "| Name | Version | Publisher | Size |\n"
            report += "|------|---------|-----------|------|\n"
            
            for program in programs[:50]:  # Top 50
                name = program.get("name", "Unknown")
                version = program.get("version", "Unknown")
                publisher = program.get("publisher", "Unknown")
                size_mb = program.get("size_mb", 0)
                
                report += f"| {name} | {version} | {publisher} | {size_mb:.2f} MB |\n"
            
            if len(programs) > 50:
                report += f"\n*... and {len(programs) - 50} more*\n"
        
        report += f"""

## 📦 Portable Apps

"""
        
        if self.catalog["portable_apps"]:
            report += "| Name | Path | Size |\n"
            report += "|------|------|------|\n"
            
            for app in self.catalog["portable_apps"][:30]:  # Top 30
                name = app.get("name", "Unknown")
                path = Path(app.get("path", "")).name
                size_mb = app.get("size_mb", 0)
                
                report += f"| {name} | {path} | {size_mb:.2f} MB |\n"
        
        report += f"""

---

**Next Steps:**
1. Review catalog at: `{output_path.parent / 'programs_catalog.json'}`
2. Backup portable apps and installers
3. Document licenses and activation keys
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"📊 Report saved: {output_path}")


def main():
    """Main execution"""
    cataloger = ProgramsCataloger()
    catalog = cataloger.catalog_all()
    
    # Save catalog
    output_dir = Path("data/laptop_inventory")
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    
    catalog_path = output_dir / f"programs_catalog_{timestamp}.json"
    cataloger.save_catalog(catalog_path)
    
    # Generate report
    report_path = output_dir / f"programs_catalog_report_{timestamp}.md"
    cataloger.generate_report(report_path)
    
    # Summary
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📊 CATALOG SUMMARY")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"\n💾 Installed programs: {catalog['stats']['total_installed']}")
    print(f"📦 Portable apps: {catalog['stats']['total_portable']}")
    print(f"💽 Total size: {catalog['stats']['total_size_bytes'] / (1024**3):.2f} GB")


if __name__ == "__main__":
    main()
