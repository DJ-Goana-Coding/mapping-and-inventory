#!/usr/bin/env python3
"""
🔍 GDRIVE ACCESS VERIFIER
Authority: Citadel Architect v25.0.OMNI+
Purpose: Test Rclone authentication and list GDrive contents
"""

import subprocess
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class GDriveAccessVerifier:
    """Verify Rclone access to GDrive accounts"""
    
    def __init__(self):
        self.remotes = {
            "gdrive_chanceroofing": "chanceroofing@gmail.com",
            "gdrive_mynewemail": "mynewemail110411@gmail.com"
        }
        self.results = {}
    
    def check_rclone_installed(self) -> bool:
        """Check if Rclone is installed"""
        try:
            result = subprocess.run(
                ["rclone", "version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                print(f"✅ Rclone installed: {version}")
                return True
        except FileNotFoundError:
            print("❌ Rclone not installed!")
            print("   Install: curl https://rclone.org/install.sh | sudo bash")
            return False
        except Exception as e:
            print(f"❌ Error checking Rclone: {e}")
            return False
        return False
    
    def list_configured_remotes(self) -> List[str]:
        """List all configured Rclone remotes"""
        try:
            result = subprocess.run(
                ["rclone", "listremotes"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                remotes = [r.strip().rstrip(':') for r in result.stdout.strip().split('\n') if r.strip()]
                return remotes
        except Exception as e:
            print(f"❌ Error listing remotes: {e}")
            return []
        return []
    
    def get_remote_info(self, remote_name: str) -> Dict[str, Any]:
        """Get information about a remote"""
        print(f"\n🔍 Testing: {remote_name}")
        
        result = {
            "remote_name": remote_name,
            "email": self.remotes.get(remote_name, "unknown"),
            "configured": False,
            "accessible": False,
            "root_items": [],
            "total_items": 0,
            "storage_used": "unknown",
            "error": None
        }
        
        # Check if configured
        configured_remotes = self.list_configured_remotes()
        if remote_name not in configured_remotes:
            result["error"] = "Remote not configured"
            print(f"   ❌ Not configured")
            return result
        
        result["configured"] = True
        print(f"   ✅ Configured")
        
        # Test access by listing root
        try:
            list_result = subprocess.run(
                ["rclone", "lsf", f"{remote_name}:", "--max-depth", "1"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if list_result.returncode == 0:
                items = [item.strip() for item in list_result.stdout.strip().split('\n') if item.strip()]
                result["accessible"] = True
                result["root_items"] = items[:10]  # First 10 items
                result["total_items"] = len(items)
                print(f"   ✅ Accessible")
                print(f"   📁 Root items: {len(items)}")
                
                # Show first 5 items
                for item in items[:5]:
                    print(f"      - {item}")
                if len(items) > 5:
                    print(f"      ... and {len(items) - 5} more")
                
            else:
                result["error"] = f"Access failed: {list_result.stderr}"
                print(f"   ❌ Not accessible: {list_result.stderr}")
        
        except subprocess.TimeoutExpired:
            result["error"] = "Timeout accessing remote"
            print(f"   ❌ Timeout")
        except Exception as e:
            result["error"] = str(e)
            print(f"   ❌ Error: {e}")
        
        # Try to get storage info
        if result["accessible"]:
            try:
                about_result = subprocess.run(
                    ["rclone", "about", f"{remote_name}:"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if about_result.returncode == 0:
                    # Parse storage info
                    for line in about_result.stdout.split('\n'):
                        if 'Used:' in line:
                            result["storage_used"] = line.split('Used:')[1].strip()
                            print(f"   💾 Storage used: {result['storage_used']}")
            except Exception as e:
                print(f"   ⚠️  Could not get storage info: {e}")
        
        return result
    
    def verify_all_accounts(self) -> Dict[str, Any]:
        """Verify access to all configured accounts"""
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 GDRIVE ACCESS VERIFICATION")
        print("   Authority: Citadel Architect v25.0.OMNI+")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        
        if not self.check_rclone_installed():
            return {"error": "Rclone not installed"}
        
        print(f"\n📋 Checking {len(self.remotes)} GDrive accounts...")
        
        for remote_name, email in self.remotes.items():
            self.results[remote_name] = self.get_remote_info(remote_name)
        
        return self.results
    
    def generate_report(self, output_path: Path) -> None:
        """Generate verification report"""
        report = {
            "verification_timestamp": datetime.utcnow().isoformat() + "Z",
            "remotes_tested": len(self.remotes),
            "remotes_configured": sum(1 for r in self.results.values() if r.get("configured")),
            "remotes_accessible": sum(1 for r in self.results.values() if r.get("accessible")),
            "results": self.results,
            "next_steps": []
        }
        
        # Add next steps based on results
        if report["remotes_accessible"] == 0:
            report["next_steps"].append("Run: ./scripts/setup_gdrive_rclone.sh")
        elif report["remotes_accessible"] < len(self.remotes):
            report["next_steps"].append("Reconfigure failed remotes")
        else:
            report["next_steps"].extend([
                "✅ All remotes accessible",
                "Run: gh workflow run gdrive_emergency_extraction.yml",
                "Monitor: data/gdrive_archive/"
            ])
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("📊 VERIFICATION SUMMARY")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"\n✅ Accessible: {report['remotes_accessible']}/{report['remotes_tested']}")
        
        for remote_name, result in self.results.items():
            status = "✅" if result.get("accessible") else "❌"
            email = result.get("email", "unknown")
            print(f"\n{status} {remote_name}")
            print(f"   Email: {email}")
            print(f"   Configured: {'Yes' if result.get('configured') else 'No'}")
            print(f"   Accessible: {'Yes' if result.get('accessible') else 'No'}")
            if result.get("accessible"):
                print(f"   Items: {result.get('total_items', 0)}")
                if result.get("storage_used"):
                    print(f"   Storage: {result['storage_used']}")
        
        print("\n📋 Next Steps:")
        for step in report["next_steps"]:
            print(f"   - {step}")
        
        print(f"\n📄 Report saved: {output_path}")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    def generate_shared_access_guide(self, output_path: Path) -> None:
        """Generate guide for accessing chanceroofing via mynewemail"""
        guide = """# 🔐 Accessing chanceroofing@gmail.com GDrive via Shared Access

## 🎯 Situation
- **Primary Account:** chanceroofing@gmail.com (locked out June 2025)
- **Access Method:** mynewemail110411@gmail.com (has shared access)
- **GDrive Status:** Still accessible despite account lockout
- **Google One:** Still being charged monthly

---

## 📋 Method 1: Via "Shared with me"

### Using Rclone
```bash
# List files shared with mynewemail account
rclone lsf gdrive_mynewemail:shared_with_me --max-depth 1

# Copy shared files
rclone copy gdrive_mynewemail:shared_with_me ./local_backup/shared_files -P
```

### Using Web Interface
1. Login to mynewemail110411@gmail.com
2. Go to Google Drive
3. Click "Shared with me" in left sidebar
4. Find files from chanceroofing@gmail.com
5. Right-click → "Make a copy" or "Add to My Drive"

---

## 📋 Method 2: Via "Starred" Items

If you previously starred important files:

```bash
# List starred items
rclone lsf gdrive_mynewemail:starred --max-depth 1

# Copy starred files
rclone copy gdrive_mynewemail:starred ./local_backup/starred_files -P
```

---

## 📋 Method 3: Direct Folder Access

If specific folders were shared:

```bash
# Search for folders shared by chanceroofing
rclone lsf gdrive_mynewemail: --max-depth 1 | grep -i "chanceroofing\\|early\\|work\\|tia\\|citadel"

# Copy specific folder
rclone copy "gdrive_mynewemail:Folder Name" ./local_backup/folder_name -P
```

---

## 📋 Method 4: Google Takeout (RECOMMENDED)

For complete backup of chanceroofing account:

### Steps:
1. Try to access: https://takeout.google.com
2. If you can still login to chanceroofing@gmail.com:
   - Select "Google Drive" 
   - Choose "All Drive data included"
   - Click "Next step"
   - Choose "Export once"
   - File type: .zip
   - Max size: 50GB per file
   - Delivery: Email link to mynewemail110411@gmail.com
   - Click "Create export"
   
3. Wait for email (can take hours to days for large archives)
4. Download all .zip files
5. Extract to safe location

### Advantages:
- ✅ Complete account backup
- ✅ Includes all files, even non-shared
- ✅ Preserves folder structure
- ✅ Works even if account is locked

---

## 🚨 CRITICAL: Do This NOW

**Priority Actions (Within 24 hours):**

1. **Immediate Backup via Takeout**
   ```bash
   # Visit takeout.google.com with chanceroofing account
   # Request full GDrive export
   ```

2. **Copy All Shared Files**
   ```bash
   rclone copy gdrive_mynewemail:shared_with_me ./backup/shared -P
   ```

3. **Search for "Early Work"**
   ```bash
   # Search all accessible files
   rclone lsf gdrive_mynewemail: --recursive | grep -i "early\\|2020\\|2021\\|2022"
   ```

4. **Document Everything**
   ```bash
   # Generate complete file list
   rclone lsf gdrive_mynewemail:shared_with_me --recursive > shared_files_manifest.txt
   ```

---

## 📞 If Access is Lost

If you can no longer access chanceroofing@gmail.com at all:

1. **Google Account Recovery**
   - Go to: https://accounts.google.com/signin/recovery
   - Use recovery email: mynewemail110411@gmail.com
   - Use recovery phone if configured
   
2. **Contact Google Support**
   - Mention active Google One subscription
   - Request account access restoration
   - Reference payment history

3. **Legal Options**
   - Consumer protection laws
   - Payment dispute with credit card company
   - Small claims court (last resort)

---

## ✅ Success Checklist

- [ ] Accessed shared files via mynewemail account
- [ ] Requested Google Takeout export
- [ ] Downloaded all shared files locally
- [ ] Copied to GitHub/HuggingFace infrastructure
- [ ] Verified file integrity (checksums)
- [ ] Generated backup manifests
- [ ] Documented all file locations
- [ ] Multiple backup copies created

---

**Generated:** """ + datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC") + """
**Authority:** Citadel Architect v25.0.OMNI+
"""
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(guide)
        
        print(f"\n📘 Shared access guide: {output_path}")


def main():
    """Main execution"""
    verifier = GDriveAccessVerifier()
    
    # Run verification
    results = verifier.verify_all_accounts()
    
    if "error" in results:
        print(f"\n❌ Verification failed: {results['error']}")
        return False
    
    # Generate reports
    output_dir = Path(__file__).parent.parent / "data" / "gdrive_access_reports"
    
    report_path = output_dir / f"gdrive_access_verification_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    verifier.generate_report(report_path)
    
    # Generate shared access guide
    guide_path = Path(__file__).parent.parent / "GDRIVE_SHARED_ACCESS_GUIDE.md"
    verifier.generate_shared_access_guide(guide_path)
    
    # Check if all accessible
    accessible_count = sum(1 for r in results.values() if r.get("accessible"))
    total_count = len(results)
    
    if accessible_count == total_count:
        print("\n✅ All GDrive accounts accessible!")
        print("   Ready for emergency extraction")
        return True
    else:
        print(f"\n⚠️  Only {accessible_count}/{total_count} accounts accessible")
        print("   Run ./scripts/setup_gdrive_rclone.sh to configure missing remotes")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
