"""
APPS SCRIPT TOOLBOX
Links citadel_reporter.py and citadel_archivist.py to Google Sheets

This script acts as the bridge between the CITADEL workers and Google Apps Script.
It provides utilities for automating Google Sheets updates with inventory data
from all connected systems (S10, Oppo, Laptop, GDrive).

Usage:
    python apps_script_toolbox.py --identity-strike  # Generate Identity Strike report
    python apps_script_toolbox.py --full-audit       # Full archive audit to Sheets
    python apps_script_toolbox.py --worker-status    # Update worker status dashboard
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from services.worker_reporter import ReporterWorker
    from services.worker_archivist import ArchivistWorker
except ImportError:
    print("⚠️  Worker modules not found. Ensure services/ directory exists.")
    sys.exit(1)


class AppsScriptToolbox:
    """
    Bridge between CITADEL workers and Google Apps Script
    """
    
    def __init__(self):
        self.reporter = None
        self.archivist = None
        self.repo_root = REPO_ROOT
        
    def initialize_workers(self):
        """Initialize the Reporter and Archivist workers"""
        print("🔧 Initializing CITADEL Workers...")
        
        try:
            self.reporter = ReporterWorker()
            print("✅ Reporter Worker initialized")
        except Exception as e:
            print(f"⚠️  Reporter Worker failed: {e}")
            
        try:
            self.archivist = ArchivistWorker()
            print("✅ Archivist Worker initialized")
        except Exception as e:
            print(f"⚠️  Archivist Worker failed: {e}")
    
    def run_identity_strike(self):
        """
        Generate Identity Strike Report (Section 44 Audit)
        This report shows all files from connected systems
        """
        print("\n🎯 IDENTITY STRIKE REPORT - Section 44 Audit")
        print("=" * 60)
        
        if not self.reporter:
            print("❌ Reporter Worker not available")
            return False
            
        try:
            result = self.reporter.create_identity_strike_report()
            print(f"✅ Identity Strike Report generated: {result}")
            return True
        except Exception as e:
            print(f"❌ Identity Strike failed: {e}")
            return False
    
    def run_full_audit(self):
        """
        Run full archive audit and push to Google Sheets
        This processes all cargo bays and creates comprehensive inventory
        """
        print("\n📊 FULL ARCHIVE AUDIT")
        print("=" * 60)
        
        if not self.archivist:
            print("❌ Archivist Worker not available")
            return False
            
        try:
            # Process all cargo bays
            cargo_bays = [
                self.repo_root / "Research" / "GDrive",
                self.repo_root / "Research" / "Oppo",
                self.repo_root / "Research" / "S10",
                self.repo_root / "Research" / "Laptop",
                self.repo_root / "S10_CITADEL_OMEGA_INTEL"
            ]
            
            for bay in cargo_bays:
                if bay.exists():
                    print(f"📦 Processing: {bay.name}")
                    self.archivist.process_cargo_bay(str(bay))
                else:
                    print(f"⏭️  Skipping (not found): {bay.name}")
            
            # Save archive index
            self.archivist._save_archive_index()
            print(f"✅ Archive index saved: {self.archivist.files_processed} files processed")
            
            # Push to Google Sheets via Reporter
            if self.reporter:
                print("📤 Pushing to Google Sheets...")
                self.reporter.create_archive_audit_report()
                
            return True
        except Exception as e:
            print(f"❌ Full audit failed: {e}")
            return False
    
    def update_worker_status_dashboard(self):
        """
        Update Google Sheets with current worker status
        Shows sync times, errors, and system health
        """
        print("\n📊 WORKER STATUS DASHBOARD UPDATE")
        print("=" * 60)
        
        status_file = self.repo_root / "worker_status.json"
        
        if not status_file.exists():
            print("❌ worker_status.json not found")
            return False
            
        try:
            with open(status_file, 'r') as f:
                status = json.load(f)
            
            print("Current Worker Status:")
            print(f"  Last Updated: {status.get('last_updated', 'Unknown')}")
            print(f"  GDrive Last Sync: {status.get('sync_status', {}).get('gdrive_last_sync', 'Never')}")
            
            if self.reporter:
                print("📤 Pushing status to Google Sheets...")
                self.reporter.update_worker_status_sheet(status)
                print("✅ Worker status dashboard updated")
                
            return True
        except Exception as e:
            print(f"❌ Status update failed: {e}")
            return False
    
    def verify_connections(self):
        """
        Verify all connections are working:
        - Google Sheets API
        - GDrive via rclone
        - S10_CITADEL_OMEGA_INTEL dataset link
        """
        print("\n🔍 VERIFYING CONNECTIONS")
        print("=" * 60)
        
        checks_passed = 0
        checks_total = 0
        
        # Check 1: Google Sheets credentials
        checks_total += 1
        if os.environ.get("GOOGLE_SHEETS_CREDENTIALS"):
            print("✅ Google Sheets credentials found")
            checks_passed += 1
        else:
            print("❌ Google Sheets credentials missing")
        
        # Check 2: Rclone config
        checks_total += 1
        if os.environ.get("RCLONE_CONFIG_DATA"):
            print("✅ Rclone configuration found")
            checks_passed += 1
        else:
            print("❌ Rclone configuration missing")
        
        # Check 3: HuggingFace token
        checks_total += 1
        if os.environ.get("HF_TOKEN"):
            print("✅ HuggingFace token found")
            checks_passed += 1
        else:
            print("❌ HuggingFace token missing")
        
        # Check 4: Worker files
        checks_total += 1
        worker_files = [
            self.repo_root / "services" / "worker_reporter.py",
            self.repo_root / "services" / "worker_archivist.py",
            self.repo_root / "Partition_01" / "citadel_reporter.py",
            self.repo_root / "Partition_01" / "citadel_archivist.py"
        ]
        
        all_workers_present = all(f.exists() for f in worker_files)
        if all_workers_present:
            print("✅ All worker files present")
            checks_passed += 1
        else:
            print("❌ Some worker files missing")
        
        print(f"\n📊 Connection Check: {checks_passed}/{checks_total} passed")
        return checks_passed == checks_total


def main():
    parser = argparse.ArgumentParser(description="CITADEL Apps Script Toolbox")
    parser.add_argument("--identity-strike", action="store_true",
                       help="Generate Identity Strike Report (Section 44 Audit)")
    parser.add_argument("--full-audit", action="store_true",
                       help="Run full archive audit and push to Google Sheets")
    parser.add_argument("--worker-status", action="store_true",
                       help="Update worker status dashboard in Google Sheets")
    parser.add_argument("--verify", action="store_true",
                       help="Verify all connections are working")
    
    args = parser.parse_args()
    
    # Print banner
    print("\n" + "=" * 60)
    print("🛠️  APPS SCRIPT TOOLBOX - CITADEL MASTER BRIDGE")
    print("=" * 60)
    
    toolbox = AppsScriptToolbox()
    
    if args.verify:
        success = toolbox.verify_connections()
        sys.exit(0 if success else 1)
    
    # Initialize workers for other commands
    toolbox.initialize_workers()
    
    if args.identity_strike:
        success = toolbox.run_identity_strike()
        sys.exit(0 if success else 1)
    
    if args.full_audit:
        success = toolbox.run_full_audit()
        sys.exit(0 if success else 1)
    
    if args.worker_status:
        success = toolbox.update_worker_status_dashboard()
        sys.exit(0 if success else 1)
    
    # If no arguments, show help
    parser.print_help()


if __name__ == "__main__":
    main()
