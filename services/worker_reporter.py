"""
THE REPORTER WORKER
Jurisdiction: Google Sheets/Docs
Primary Task: Real-time logging of Section 44 audits and trading bot ROI

This worker creates automated reports by reading the master_intelligence_map.txt
and archive_index.json, then generating structured Google Sheets for analysis.

Requires: GOOGLE_SHEETS_CREDENTIALS environment variable
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Optional
import traceback

# Repository root
REPO_ROOT = Path(__file__).parent.parent
WORKER_STATUS_PATH = REPO_ROOT / "worker_status.json"
MASTER_INTELLIGENCE_MAP = REPO_ROOT / "master_intelligence_map.txt"
ARCHIVE_INDEX_PATH = REPO_ROOT / "archive_index.json"


class ReporterWorker:
    """The Reporter - Real-time logging to Google Sheets/Docs"""
    
    def __init__(self):
        self.worker_id = "reporter"
        self.reports_generated = 0
        self.errors = []
        self.gspread_client = None
        
        # Initialize Google Sheets client
        self._init_gspread()
    
    def _init_gspread(self):
        """Initialize Google Sheets API client"""
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            
            # Get credentials from environment
            creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
            
            if not creds_json:
                self.errors.append("GOOGLE_SHEETS_CREDENTIALS not set in environment")
                print("⚠️  GOOGLE_SHEETS_CREDENTIALS not found - Reporter Worker will run in dry-run mode")
                return
            
            # Parse credentials JSON
            creds_dict = json.loads(creds_json)
            
            # Define scopes
            scopes = [
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
            
            # Create credentials object
            credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
            
            # Initialize gspread client
            self.gspread_client = gspread.authorize(credentials)
            
            print("✅ Google Sheets API client initialized")
            
        except ImportError:
            self.errors.append("gspread not installed - run: pip install gspread google-auth")
            print("⚠️  gspread not installed - Reporter Worker will run in dry-run mode")
        except Exception as e:
            self.errors.append(f"Failed to initialize Google Sheets API: {e}")
            print(f"⚠️  Google Sheets API initialization failed: {e}")
            traceback.print_exc()
    
    def load_intelligence_map(self) -> List[str]:
        """Load the master intelligence map"""
        if not MASTER_INTELLIGENCE_MAP.exists():
            self.errors.append("master_intelligence_map.txt not found")
            return []
        
        with open(MASTER_INTELLIGENCE_MAP, 'r') as f:
            lines = f.readlines()
        
        return [line.strip() for line in lines if line.strip()]
    
    def load_archive_index(self) -> Dict:
        """Load the archive index"""
        if not ARCHIVE_INDEX_PATH.exists():
            return {"files": {}, "total_files": 0}
        
        with open(ARCHIVE_INDEX_PATH, 'r') as f:
            return json.load(f)
    
    def create_identity_strike_report(self, dry_run: bool = False) -> Optional[str]:
        """
        Create the 'Identity Strike' template report
        
        This report provides a comprehensive view of all indexed files
        with their MD5 hashes and source locations.
        
        Args:
            dry_run: If True, don't actually create the sheet (for testing)
        
        Returns:
            URL of the created spreadsheet or None on error
        """
        print("📊 Creating Identity Strike Report...")
        
        try:
            # Load data
            archive_index = self.load_archive_index()
            intelligence_map = self.load_intelligence_map()
            
            # Prepare report data
            report_data = {
                "title": f"Identity Strike Report - {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                "summary": {
                    "total_files_indexed": len(archive_index.get("files", {})),
                    "total_gdrive_entries": len(intelligence_map),
                    "report_generated": datetime.datetime.utcnow().isoformat()
                },
                "files": []
            }
            
            # Process archived files
            for filepath, metadata in archive_index.get("files", {}).items():
                report_data["files"].append({
                    "File Path": filepath,
                    "Source": metadata.get("source", "Unknown"),
                    "Size (MB)": round(metadata.get("size_bytes", 0) / 1024 / 1024, 2),
                    "MD5 Hash": metadata.get("md5", "N/A"),
                    "Modified": metadata.get("modified", "N/A"),
                    "Indexed": metadata.get("indexed", "N/A")
                })
            
            # If dry run, just print summary
            if dry_run or not self.gspread_client:
                print("\n📋 DRY RUN - Report Summary:")
                print(f"   Title: {report_data['title']}")
                print(f"   Total Files: {report_data['summary']['total_files_indexed']}")
                print(f"   GDrive Entries: {report_data['summary']['total_gdrive_entries']}")
                print(f"   Sample files: {len(report_data['files'][:5])}")
                if report_data['files']:
                    print("\n   First 5 files:")
                    for file_info in report_data['files'][:5]:
                        print(f"      - {file_info['File Path']} ({file_info['Size (MB)']} MB)")
                return "DRY_RUN_SUCCESS"
            
            # Create Google Sheet
            spreadsheet = self.gspread_client.create(report_data['title'])
            
            # Share with owner (optional - adjust email as needed)
            # spreadsheet.share('your-email@example.com', perm_type='user', role='owner')
            
            # Get the first worksheet
            worksheet = spreadsheet.sheet1
            worksheet.update_title("File Index")
            
            # Write summary
            summary_data = [
                ["Identity Strike Report - ARK_CORE Archive Index"],
                [""],
                ["Report Generated", report_data['summary']['report_generated']],
                ["Total Files Indexed", report_data['summary']['total_files_indexed']],
                ["Total GDrive Entries", report_data['summary']['total_gdrive_entries']],
                [""],
                ["File Index"],
                ["File Path", "Source", "Size (MB)", "MD5 Hash", "Modified", "Indexed"]
            ]
            
            # Add file data
            for file_info in report_data['files']:
                summary_data.append([
                    file_info['File Path'],
                    file_info['Source'],
                    file_info['Size (MB)'],
                    file_info['MD5 Hash'],
                    file_info['Modified'],
                    file_info['Indexed']
                ])
            
            # Update worksheet
            worksheet.update('A1', summary_data)
            
            # Format header row
            worksheet.format('A1:F1', {
                'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.8},
                'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
            })
            
            self.reports_generated += 1
            
            print(f"✅ Identity Strike Report created: {spreadsheet.url}")
            return spreadsheet.url
            
        except Exception as e:
            error_msg = f"Failed to create Identity Strike Report: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return None
    
    def create_section_44_audit_report(self, dry_run: bool = False) -> Optional[str]:
        """
        Create Section 44 Audit Report (Liquor/Food Act Compliance)
        
        This report analyzes the GDrive structure and provides audit information,
        with special focus on Section 44 compliance including:
        - Orange Stars (C-rating) violations
        - 72-hour notice window tracking
        - Liquor licensing compliance
        - Food safety certifications
        
        Args:
            dry_run: If True, don't actually create the sheet
        
        Returns:
            URL of the created spreadsheet or None on error
        """
        print("📊 Creating Section 44 Audit Report (Liquor/Food Act)...")
        
        try:
            intelligence_map = self.load_intelligence_map()
            
            # Analyze GDrive structure
            folders = [line for line in intelligence_map if line.endswith('/')]
            files = [line for line in intelligence_map if not line.endswith('/')]
            
            # Section 44 specific analysis - flag potential compliance issues
            orange_star_keywords = ['c-rating', 'orange star', 'critical', 'violation', 'non-compliance']
            liquor_keywords = ['liquor', 'license', 'alcohol', 'festival', 'event']
            notice_keywords = ['72-hour', '72 hour', 'notice', 'deadline', 'compliance']
            
            # Categorize files for Section 44 audit
            orange_star_flags = []
            liquor_related = []
            notice_tracking = []
            
            for file_entry in files:
                file_lower = file_entry.lower()
                
                # Check for Orange Star (C-rating) indicators
                if any(keyword in file_lower for keyword in orange_star_keywords):
                    orange_star_flags.append({
                        "path": file_entry,
                        "category": "ORANGE_STAR",
                        "severity": "CRITICAL",
                        "requires_action": "72-hour remediation window"
                    })
                
                # Check for liquor licensing files
                if any(keyword in file_lower for keyword in liquor_keywords):
                    liquor_related.append({
                        "path": file_entry,
                        "category": "LIQUOR_LICENSE",
                        "requires_review": True
                    })
                
                # Check for notice/deadline tracking
                if any(keyword in file_lower for keyword in notice_keywords):
                    notice_tracking.append({
                        "path": file_entry,
                        "category": "NOTICE_TRACKING",
                        "window": "72 hours"
                    })
            
            report_data = {
                "title": f"Section 44 Audit (Liquor/Food) - {datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
                "summary": {
                    "total_entries": len(intelligence_map),
                    "total_folders": len(folders),
                    "total_files": len(files),
                    "orange_star_flags": len(orange_star_flags),
                    "liquor_related_files": len(liquor_related),
                    "notice_tracking_items": len(notice_tracking),
                    "report_generated": datetime.datetime.utcnow().isoformat()
                }
            }
            
            if dry_run or not self.gspread_client:
                print("\n📋 DRY RUN - Section 44 Audit Summary:")
                print(f"   Title: {report_data['title']}")
                print(f"   Total Entries: {report_data['summary']['total_entries']}")
                print(f"   🔴 Orange Star Flags: {report_data['summary']['orange_star_flags']}")
                print(f"   🍺 Liquor-Related Files: {report_data['summary']['liquor_related_files']}")
                print(f"   ⏰ 72-Hour Notice Items: {report_data['summary']['notice_tracking_items']}")
                
                if orange_star_flags:
                    print("\n   🔴 CRITICAL - Orange Star (C-Rating) Flags:")
                    for flag in orange_star_flags[:5]:
                        print(f"      - {flag['path']} [SEVERITY: {flag['severity']}]")
                
                return "DRY_RUN_SUCCESS"
            
            # Create Google Sheet
            spreadsheet = self.gspread_client.create(report_data['title'])
            worksheet = spreadsheet.sheet1
            worksheet.update_title("Section 44 Compliance")
            
            # Write summary data
            data = [
                ["Section 44 Audit Report - Liquor & Food Act Compliance"],
                [""],
                ["Report Generated", report_data['summary']['report_generated']],
                ["Total Entries", report_data['summary']['total_entries']],
                ["Total Folders", report_data['summary']['total_folders']],
                ["Total Files", report_data['summary']['total_files']],
                [""],
                ["🔴 COMPLIANCE ALERTS"],
                ["Orange Star (C-Rating) Flags", report_data['summary']['orange_star_flags']],
                ["Liquor-Related Files Requiring Review", report_data['summary']['liquor_related_files']],
                ["72-Hour Notice Window Items", report_data['summary']['notice_tracking_items']],
                [""],
                ["🔴 ORANGE STAR (C-RATING) FLAGS - CRITICAL"],
                ["Path", "Category", "Severity", "Required Action"],
            ]
            
            # Add Orange Star flags
            for flag in orange_star_flags[:100]:
                data.append([
                    flag['path'],
                    flag['category'],
                    flag['severity'],
                    flag['requires_action']
                ])
            
            # Add separator for liquor licensing section
            data.append([""])
            data.append(["🍺 LIQUOR LICENSING FILES"])
            data.append(["Path", "Category", "Requires Review"])
            
            for item in liquor_related[:100]:
                data.append([
                    item['path'],
                    item['category'],
                    "Yes" if item['requires_review'] else "No"
                ])
            
            # Add separator for notice tracking
            data.append([""])
            data.append(["⏰ 72-HOUR NOTICE WINDOW TRACKING"])
            data.append(["Path", "Category", "Notice Window"])
            
            for item in notice_tracking[:100]:
                data.append([
                    item['path'],
                    item['category'],
                    item['window']
                ])
            
            # Update worksheet
            worksheet.update('A1', data)
            
            # Format critical sections in red
            if orange_star_flags:
                worksheet.format('A13:D13', {
                    'backgroundColor': {'red': 0.9, 'green': 0.2, 'blue': 0.2},
                    'textFormat': {'bold': True, 'foregroundColor': {'red': 1, 'green': 1, 'blue': 1}}
                })
            
            self.reports_generated += 1
            print(f"✅ Section 44 Audit Report created: {spreadsheet.url}")
            print(f"   🔴 {len(orange_star_flags)} Orange Star (C-Rating) flags identified")
            print(f"   🍺 {len(liquor_related)} liquor-related files flagged for review")
            print(f"   ⏰ {len(notice_tracking)} items with 72-hour notice windows")
            
            return spreadsheet.url
            
        except Exception as e:
            error_msg = f"Failed to create Section 44 Audit Report: {e}"
            self.errors.append(error_msg)
            print(f"❌ {error_msg}")
            return None
    
    def run(self, dry_run: bool = False):
        """
        Run the Reporter worker
        
        Args:
            dry_run: If True, don't actually create sheets (for testing)
        """
        print("📰 THE REPORTER WORKER — Starting...")
        print("=" * 60)
        
        start_time = datetime.datetime.utcnow()
        
        # Create reports
        reports = []
        
        # Identity Strike Report
        url = self.create_identity_strike_report(dry_run=dry_run)
        if url:
            reports.append(("Identity Strike Report", url))
        
        # Section 44 Audit Report
        url = self.create_section_44_audit_report(dry_run=dry_run)
        if url:
            reports.append(("Section 44 Audit Report", url))
        
        # Update worker status
        self._update_worker_status(start_time, reports)
        
        # Print summary
        print("=" * 60)
        print(f"✅ THE REPORTER WORKER — Complete")
        print(f"   Reports generated: {len(reports)}")
        print(f"   Errors: {len(self.errors)}")
        
        if reports:
            print("\n📊 Generated Reports:")
            for name, url in reports:
                print(f"   - {name}: {url}")
        
        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:10]:
                print(f"   - {error}")
    
    def _update_worker_status(self, start_time: datetime.datetime, reports: List):
        """Update worker_status.json with run results"""
        try:
            if WORKER_STATUS_PATH.exists():
                with open(WORKER_STATUS_PATH, 'r') as f:
                    status = json.load(f)
            else:
                status = {"workers": {}}
            
            end_time = datetime.datetime.utcnow()
            success = len(self.errors) == 0
            
            if "reporter" not in status["workers"]:
                status["workers"]["reporter"] = {}
            
            status["workers"]["reporter"].update({
                "status": "OPERATIONAL" if success else "ERROR",
                "last_run": end_time.isoformat(),
                "last_success": end_time.isoformat() if success else status["workers"]["reporter"].get("last_success"),
                "total_runs": status["workers"]["reporter"].get("total_runs", 0) + 1,
                "total_reports_generated": status["workers"]["reporter"].get("total_reports_generated", 0) + len(reports),
                "errors": self.errors[-10:] if self.errors else []
            })
            
            status["last_updated"] = end_time.isoformat()
            
            with open(WORKER_STATUS_PATH, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            print(f"⚠️  Failed to update worker_status.json: {e}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="The Reporter Worker - Google Sheets/Docs automation")
    parser.add_argument("--dry-run", action="store_true", help="Dry run mode - don't create actual sheets")
    
    args = parser.parse_args()
    
    worker = ReporterWorker()
    worker.run(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
