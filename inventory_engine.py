from typing import Dict, List, Optional, Tuple, Any, Union
import os
import json
from datetime import datetime
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from huggingface_hub import HfApi
except ImportError:
    print("❌ Dependencies missing. Run: pip install google-api-python-client google-auth huggingface_hub")
    exit(1)

# Configuration
GD_SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')
HF_USER = "DJ-Goana-Coding"

def get_gdrive_inventory(service):
    """Maps the Citadel folder structure."""
    print("🛰️  Mapping Google Drive Districts...")
    inventory = []
    query = "mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, parents)").execute()
    folders = results.get('files', [])
    
    # Filter for Citadel-related folders
    for folder in folders:
        if any(keyword in folder['name'].upper() for keyword in ["CITADEL", "DISTRICT", "COMMAND"]):
            inventory.append({"name": folder['name'], "id": folder['id'], "type": "Folder"})
    return inventory

def get_hf_inventory():
    """Maps Hugging Face Spaces."""
    print("🧠 Mapping Hugging Face Spaces...")
    api = HfApi()
    try:
        spaces = api.list_spaces(author=HF_USER)
        return [{"name": s.id, "sdk": s.sdk, "lastModified": s.lastModified} for s in spaces]
    except Exception as e:
        return [f"Error: {str(e)}"]

def generate_report(google_drive_data, huggingface_data):
    """Generates the updated INVENTORY_REPORT.md"""
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    report = f"""# 🏛️ CITADEL MAPPING & INVENTORY REPORT
**Timestamp:** {timestamp}
**Commander:** DJ-Goana-Coding
**Status:** Handshake Protocol Ready

## 📂 GOOGLE DRIVE DISTRICTS (Architecture)
| District / Folder | Drive ID | Status |
| :--- | :--- | :--- |
"""
    for item in google_drive_data:
        report += f"| {item['name']} | `{item['id']}` | ✅ Mapped |\n"
        
    report += f"""
## 🚀 HUGGING FACE SPACES (Tia's Domains)
| Space Name | SDK | Last Updated |
| :--- | :--- | :--- |
"""
    for space in huggingface_data:
        if isinstance(space, dict):
            report += f"| {space['name']} | {space['sdk']} | {space['lastModified']} |\n"
        else:
            report += f"| {space} | - | - |\n"

    with open("INVENTORY_REPORT.md", "w") as report_file:
        report_file.write(report)
    print("✅ INVENTORY_REPORT.md updated.")

def main():
    # 1. GDrive Auth
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"⚠️  Missing {SERVICE_ACCOUNT_FILE}. Skipping Drive inventory.")
        google_drive_items = []
    else:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=GD_SCOPES)
        service = build('drive', 'v3', credentials=creds)
        google_drive_items = get_gdrive_inventory(service)

    # 2. HF Auth
    huggingface_items = get_hf_inventory()

    # 3. Generate Report
    generate_report(google_drive_items, huggingface_items)

if __name__ == "__main__":
    main()