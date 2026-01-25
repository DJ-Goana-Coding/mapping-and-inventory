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
    for f in folders:
        if any(keyword in f['name'].upper() for keyword in ["CITADEL", "DISTRICT", "COMMAND"]):
            inventory.append({"name": f['name'], "id": f['id'], "type": "Folder"})
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

def generate_report(gd_data, hf_data):
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
    for item in gd_data:
        report += f"| {item['name']} | {item['id']} | ✅ Mapped |\n"
        
    report += f"""
## 🚀 HUGGING FACE SPACES (Tia's Domains)
| Space Name | SDK | Last Updated |
| :--- | :--- | :--- |
"""
    for s in hf_data:
        if isinstance(s, dict):
            report += f"| {s['name']} | {s['sdk']} | {s['lastModified']} |\n"
        else:
            report += f"| {s} | - | - |\n"

    with open("INVENTORY_REPORT.md", "w") as f:
        f.write(report)
    print("✅ INVENTORY_REPORT.md updated.")

def main():
    # 1. GDrive Auth
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        print(f"⚠️  Missing {SERVICE_ACCOUNT_FILE}. Skipping Drive inventory.")
        gd_items = []
    else:
        creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=GD_SCOPES)
        service = build('drive', 'v3', credentials=creds)
        gd_items = get_gdrive_inventory(service)

    # 2. HF Auth
    hf_items = get_hf_inventory()

    # 3. Generate Report
    generate_report(gd_items, hf_items)

if __name__ == "__main__":
    main()