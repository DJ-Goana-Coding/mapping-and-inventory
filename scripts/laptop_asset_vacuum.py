#!/usr/bin/env python3
"""
💻 LAPTOP ASSET VACUUM v1.0
Comprehensive Asset Discovery & Cataloging

Scans and catalogs:
- VSCode extensions (.vsix files)
- Browser extensions (Chrome, Firefox)
- Audio VST plugins (music production)
- Video editing plugins (Premiere, After Effects, DaVinci)
- Blender addons (.py, .zip)
- APKs (Android packages)
- Desktop applications
- Development tools

Output: data/laptop_assets/
"""

import json
import os
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import subprocess
import sys

class LaptopAssetVacuum:
    """Comprehensive laptop asset discovery and cataloging"""
    
    def __init__(self, output_dir: str = "./data/laptop_assets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.assets = {
            "meta": {
                "scanner": "Laptop Asset Vacuum",
                "version": "1.0",
                "scan_time": datetime.utcnow().isoformat(),
                "platform": platform.system(),
                "hostname": platform.node()
            },
            "categories": {}
        }
        
        self.common_paths = self._get_common_paths()
    
    def _get_common_paths(self) -> Dict[str, List[str]]:
        """Get common paths based on OS"""
        system = platform.system()
        home = Path.home()
        
        if system == "Windows":
            return {
                "vscode_extensions": [
                    home / ".vscode" / "extensions",
                    home / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "resources" / "app" / "extensions"
                ],
                "browser_extensions": [
                    home / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default" / "Extensions",
                    home / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
                ],
                "vst_plugins": [
                    Path("C:/Program Files/VSTPlugins"),
                    Path("C:/Program Files/Common Files/VST3"),
                    Path("C:/Program Files/Steinberg/VSTPlugins")
                ],
                "video_plugins": [
                    home / "AppData" / "Roaming" / "Adobe" / "After Effects",
                    home / "AppData" / "Roaming" / "Adobe" / "Premiere Pro",
                    home / "AppData" / "Roaming" / "Blackmagic Design" / "DaVinci Resolve"
                ],
                "blender_addons": [
                    home / "AppData" / "Roaming" / "Blender Foundation" / "Blender",
                    Path("C:/Program Files/Blender Foundation/Blender")
                ],
                "apk_files": [
                    home / "Downloads",
                    home / "Documents",
                    home / "Desktop"
                ],
                "applications": [
                    Path("C:/Program Files"),
                    Path("C:/Program Files (x86)"),
                    home / "AppData" / "Local" / "Programs"
                ]
            }
        elif system == "Darwin":  # macOS
            return {
                "vscode_extensions": [
                    home / ".vscode" / "extensions"
                ],
                "browser_extensions": [
                    home / "Library" / "Application Support" / "Google" / "Chrome" / "Default" / "Extensions",
                    home / "Library" / "Application Support" / "Firefox" / "Profiles"
                ],
                "vst_plugins": [
                    Path("/Library/Audio/Plug-Ins/VST"),
                    Path("/Library/Audio/Plug-Ins/VST3"),
                    home / "Library" / "Audio" / "Plug-Ins" / "VST"
                ],
                "video_plugins": [
                    home / "Library" / "Application Support" / "Adobe" / "After Effects",
                    home / "Library" / "Application Support" / "Adobe" / "Premiere Pro",
                    home / "Library" / "Application Support" / "Blackmagic Design"
                ],
                "blender_addons": [
                    home / "Library" / "Application Support" / "Blender"
                ],
                "apk_files": [
                    home / "Downloads",
                    home / "Documents",
                    home / "Desktop"
                ],
                "applications": [
                    Path("/Applications"),
                    home / "Applications"
                ]
            }
        else:  # Linux
            return {
                "vscode_extensions": [
                    home / ".vscode" / "extensions"
                ],
                "browser_extensions": [
                    home / ".config" / "google-chrome" / "Default" / "Extensions",
                    home / ".mozilla" / "firefox"
                ],
                "vst_plugins": [
                    Path("/usr/lib/vst"),
                    Path("/usr/local/lib/vst"),
                    home / ".vst"
                ],
                "video_plugins": [
                    home / ".config" / "kdenlive",
                    home / ".local" / "share" / "kdenlive"
                ],
                "blender_addons": [
                    home / ".config" / "blender",
                    Path("/usr/share/blender")
                ],
                "apk_files": [
                    home / "Downloads",
                    home / "Documents",
                    home / "Desktop"
                ],
                "applications": [
                    Path("/usr/bin"),
                    Path("/usr/local/bin"),
                    Path("/opt")
                ]
            }
    
    def scan_vscode_extensions(self) -> Dict:
        """Scan for VSCode extensions"""
        extensions = []
        
        for path in self.common_paths.get("vscode_extensions", []):
            if not path.exists():
                continue
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        # Parse extension ID (publisher.name-version)
                        parts = item.name.split('-')
                        if len(parts) >= 2:
                            extensions.append({
                                "name": '-'.join(parts[:-1]),
                                "version": parts[-1] if parts[-1][0].isdigit() else "unknown",
                                "path": str(item),
                                "type": "VSCode Extension"
                            })
            except PermissionError:
                continue
        
        return {
            "name": "VSCode Extensions",
            "count": len(extensions),
            "extensions": extensions[:50]  # Limit output
        }
    
    def scan_browser_extensions(self) -> Dict:
        """Scan for browser extensions"""
        extensions = []
        
        for path in self.common_paths.get("browser_extensions", []):
            if not path.exists():
                continue
            
            try:
                for item in path.iterdir():
                    if item.is_dir():
                        # Try to read manifest.json
                        manifest_path = item / "manifest.json"
                        if manifest_path.exists():
                            try:
                                with open(manifest_path) as f:
                                    manifest = json.load(f)
                                    extensions.append({
                                        "name": manifest.get("name", item.name),
                                        "version": manifest.get("version", "unknown"),
                                        "description": manifest.get("description", "")[:100],
                                        "path": str(item),
                                        "type": "Browser Extension"
                                    })
                            except:
                                pass
            except PermissionError:
                continue
        
        return {
            "name": "Browser Extensions",
            "count": len(extensions),
            "extensions": extensions[:30]
        }
    
    def scan_vst_plugins(self) -> Dict:
        """Scan for VST audio plugins"""
        plugins = []
        
        for path in self.common_paths.get("vst_plugins", []):
            if not path.exists():
                continue
            
            try:
                for item in path.rglob("*"):
                    if item.suffix in ['.dll', '.vst', '.vst3', '.component']:
                        plugins.append({
                            "name": item.stem,
                            "type": f"VST Plugin ({item.suffix})",
                            "path": str(item),
                            "size_mb": round(item.stat().st_size / (1024 * 1024), 2)
                        })
            except PermissionError:
                continue
        
        return {
            "name": "VST Audio Plugins",
            "count": len(plugins),
            "plugins": plugins[:40]
        }
    
    def scan_video_plugins(self) -> Dict:
        """Scan for video editing plugins"""
        plugins = []
        
        for path in self.common_paths.get("video_plugins", []):
            if not path.exists():
                continue
            
            try:
                for item in path.rglob("*"):
                    if item.suffix in ['.aex', '.plugin', '.8bf', '.prproj']:
                        plugins.append({
                            "name": item.stem,
                            "type": f"Video Plugin ({item.suffix})",
                            "path": str(item),
                            "app": "After Effects" if item.suffix == '.aex' else "Premiere Pro"
                        })
            except PermissionError:
                continue
        
        return {
            "name": "Video Editing Plugins",
            "count": len(plugins),
            "plugins": plugins[:30]
        }
    
    def scan_blender_addons(self) -> Dict:
        """Scan for Blender addons"""
        addons = []
        
        for path in self.common_paths.get("blender_addons", []):
            if not path.exists():
                continue
            
            try:
                for item in path.rglob("*"):
                    if item.suffix in ['.py', '.zip'] and 'addons' in str(item):
                        addons.append({
                            "name": item.stem,
                            "type": f"Blender Addon ({item.suffix})",
                            "path": str(item)
                        })
            except PermissionError:
                continue
        
        return {
            "name": "Blender Addons",
            "count": len(addons),
            "addons": addons[:30]
        }
    
    def scan_apk_files(self) -> Dict:
        """Scan for APK files"""
        apks = []
        
        for path in self.common_paths.get("apk_files", []):
            if not path.exists():
                continue
            
            try:
                for item in path.rglob("*.apk"):
                    apks.append({
                        "name": item.stem,
                        "path": str(item),
                        "size_mb": round(item.stat().st_size / (1024 * 1024), 2),
                        "modified": datetime.fromtimestamp(item.stat().st_mtime).isoformat()
                    })
            except PermissionError:
                continue
        
        return {
            "name": "Android APK Files",
            "count": len(apks),
            "apks": apks[:50]
        }
    
    def scan_applications(self) -> Dict:
        """Scan for installed applications"""
        apps = []
        system = platform.system()
        
        try:
            if system == "Windows":
                # Use PowerShell to get installed programs
                result = subprocess.run(
                    ['powershell', '-Command', 
                     'Get-ItemProperty HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, Publisher | ConvertTo-Json'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    try:
                        programs = json.loads(result.stdout)
                        if isinstance(programs, list):
                            apps = [
                                {
                                    "name": p.get("DisplayName", "Unknown"),
                                    "version": p.get("DisplayVersion", ""),
                                    "publisher": p.get("Publisher", "")
                                }
                                for p in programs if p.get("DisplayName")
                            ][:100]
                    except:
                        pass
            
            elif system == "Darwin":
                # macOS: scan Applications folder
                app_paths = [Path("/Applications"), Path.home() / "Applications"]
                for app_path in app_paths:
                    if app_path.exists():
                        for item in app_path.iterdir():
                            if item.suffix == '.app':
                                apps.append({
                                    "name": item.stem,
                                    "path": str(item),
                                    "platform": "macOS"
                                })
            
            elif system == "Linux":
                # Linux: try to use dpkg or rpm
                try:
                    result = subprocess.run(['dpkg', '-l'], capture_output=True, text=True, timeout=10)
                    if result.returncode == 0:
                        lines = result.stdout.split('\n')[5:]  # Skip header
                        for line in lines[:100]:
                            parts = line.split()
                            if len(parts) >= 3:
                                apps.append({
                                    "name": parts[1],
                                    "version": parts[2],
                                    "platform": "Linux (dpkg)"
                                })
                except:
                    pass
        
        except Exception as e:
            print(f"Warning: Could not fully scan applications: {e}")
        
        return {
            "name": "Installed Applications",
            "count": len(apps),
            "applications": apps[:100]
        }
    
    def run_scan(self) -> Dict:
        """Execute full asset scan"""
        print("💻 Laptop Asset Vacuum - Scan Start")
        print("=" * 60)
        print(f"Platform: {self.assets['meta']['platform']}")
        print(f"Hostname: {self.assets['meta']['hostname']}")
        print()
        
        self.assets["categories"]["vscode_extensions"] = self.scan_vscode_extensions()
        print(f"✓ VSCode Extensions: {self.assets['categories']['vscode_extensions']['count']} found")
        
        self.assets["categories"]["browser_extensions"] = self.scan_browser_extensions()
        print(f"✓ Browser Extensions: {self.assets['categories']['browser_extensions']['count']} found")
        
        self.assets["categories"]["vst_plugins"] = self.scan_vst_plugins()
        print(f"✓ VST Plugins: {self.assets['categories']['vst_plugins']['count']} found")
        
        self.assets["categories"]["video_plugins"] = self.scan_video_plugins()
        print(f"✓ Video Plugins: {self.assets['categories']['video_plugins']['count']} found")
        
        self.assets["categories"]["blender_addons"] = self.scan_blender_addons()
        print(f"✓ Blender Addons: {self.assets['categories']['blender_addons']['count']} found")
        
        self.assets["categories"]["apk_files"] = self.scan_apk_files()
        print(f"✓ APK Files: {self.assets['categories']['apk_files']['count']} found")
        
        self.assets["categories"]["applications"] = self.scan_applications()
        print(f"✓ Applications: {self.assets['categories']['applications']['count']} found")
        
        # Calculate statistics
        total_assets = sum(
            cat.get("count", 0)
            for cat in self.assets["categories"].values()
        )
        
        self.assets["statistics"] = {
            "total_categories": len(self.assets["categories"]),
            "total_assets": total_assets,
            "scan_duration": "Complete"
        }
        
        return self.assets
    
    def save_results(self):
        """Save scan results"""
        # Save main manifest
        manifest_file = self.output_dir / "laptop_asset_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(self.assets, f, indent=2)
        
        print(f"\n✅ Asset manifest saved to: {manifest_file}")
        print(f"📊 Total assets cataloged: {self.assets['statistics']['total_assets']}")
        
        # Save installation guide
        self._generate_installation_guide()
    
    def _generate_installation_guide(self):
        """Generate installation/migration guide"""
        guide_file = self.output_dir / "INSTALLATION_GUIDE.md"
        
        content = f"""# 💻 Laptop Asset Installation Guide

**Generated**: {self.assets['meta']['scan_time']}  
**Platform**: {self.assets['meta']['platform']}  
**Total Assets**: {self.assets['statistics']['total_assets']}

## 📦 Asset Categories

"""
        
        for category_name, category_data in self.assets["categories"].items():
            count = category_data.get("count", 0)
            content += f"### {category_data.get('name', category_name)}\n"
            content += f"**Count**: {count} items\n\n"
        
        content += """
## 🔧 Migration Instructions

### VSCode Extensions
```bash
# Export extensions list
code --list-extensions > vscode-extensions.txt

# Install on new machine
cat vscode-extensions.txt | xargs -L 1 code --install-extension
```

### Browser Extensions
- Export bookmarks and settings from browser
- Manually reinstall extensions from Chrome/Firefox stores

### VST Plugins
- Copy plugin files to appropriate directories
- Rescan plugins in DAW

### APK Files
- Transfer APKs to Android device
- Install via file manager or ADB

## 📋 Backup Checklist

- [ ] VSCode settings and extensions
- [ ] Browser profiles and extensions
- [ ] Audio VST plugins
- [ ] Video editing plugins
- [ ] Blender addons
- [ ] APK files
- [ ] Application licenses

---

**Scanned by**: Laptop Asset Vacuum v1.0
"""
        
        with open(guide_file, 'w') as f:
            f.write(content)
        
        print(f"📝 Installation guide saved to: {guide_file}")

def main():
    scanner = LaptopAssetVacuum()
    scanner.run_scan()
    scanner.save_results()
    
    print("\n🎯 Mission Complete - Laptop Asset Vacuum")

if __name__ == "__main__":
    main()
