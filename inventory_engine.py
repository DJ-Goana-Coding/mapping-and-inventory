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

def generate_report(gd_data, hf_data, pioneer_data=None):
    """
    Generates the updated INVENTORY_REPORT.md with Pioneer Trader integration.
    
    Args:
        gd_data: Google Drive inventory
        hf_data: Hugging Face Spaces inventory
        pioneer_data: Live Pioneer Trader telemetry (optional)
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    report = f"""# 🏛️ CITADEL MAPPING & INVENTORY REPORT
**Timestamp:** {timestamp}
**Commander:** DJ-Goana-Coding
**Status:** Unified Handshake Protocol Active

## 📂 GOOGLE DRIVE DISTRICTS (Architecture)
| District / Folder | Drive ID | Status |
| :--- | :--- | :--- |
"""
    for item in gd_data:
        report += f"| {item['name']} | `{item['id']}` | ✅ Mapped |\n"
        
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
    
    # Add Pioneer Trader integration section
    report += f"""
## 🛡️ LIVE FLEET STATUS (Pioneer Trader)
"""
    
    if pioneer_data and pioneer_data.get("success"):
        data = pioneer_data["data"]
        report += f"""
**Last Sync:** {pioneer_data.get("timestamp", "Unknown")}
**Wallet Balance:** {data.get("wallet", "N/A")}
**Total Equity:** {data.get("equity", "N/A")}
**Engine Status:** {data.get("status", "Unknown")}

### 7-Slot Vortex Configuration
| Slot | Type | Status | Asset | Entry | Current | PnL | Peak | Stop |
|------|------|--------|-------|-------|---------|-----|------|------|
"""
        # Parse slots data and populate table
        slots = data.get("slots", {})
        for slot_id in range(1, 8):
            slot_data = slots.get(str(slot_id), {})
            
            if slot_data:
                slot_type = slot_data.get("type", "UNKNOWN")
                status = slot_data.get("status", "INACTIVE")
                asset = slot_data.get("asset", "-")
                entry = slot_data.get("entry_price", "-")
                current = slot_data.get("current_price", "-")
                pnl = slot_data.get("pnl", "-")
                
                # Handle SCALP vs GRID type differences
                if slot_type == "SCALP":
                    peak = slot_data.get("take_profit", "-")
                    stop = "-"
                elif slot_type == "GRID":
                    peak = slot_data.get("peak_price", "-")
                    stop = slot_data.get("stop_loss", "-")
                else:
                    peak = "-"
                    stop = "-"
                
                report += f"| {slot_id} | {slot_type} | {status} | {asset} | {entry} | {current} | {pnl} | {peak} | {stop} |\n"
            else:
                report += f"| {slot_id} | - | EMPTY | - | - | - | - | - | - |\n"
        
    else:
        report += f"""
**Status:** ⚠️ Pioneer Trader Offline or Unreachable
**Last Known State:** Check shadow archive at `SHADOW_ARCHIVE_PATH/pioneer_status.json`
**Action Required:** Verify PIONEER_TRADER_URL and PIONEER_AUTH_TOKEN environment variables
"""
        if pioneer_data:
            report += f"**Error:** {pioneer_data.get('error', 'Unknown error')}\n"

    with open("INVENTORY_REPORT.md", "w") as f:
        f.write(report)
    print("✅ [T.I.A.] INVENTORY_REPORT.md updated with unified telemetry")

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

    # 3. Pioneer Trader Integration (NEW)
    pioneer_data = None
    try:
        from bridge_protocol import PioneerBridge
        bridge = PioneerBridge()
        print("🌉 [T.I.A.] Initiating handshake with Pioneer Trader...")
        pioneer_data = bridge.fetch_pioneer_status()
        
        if pioneer_data.get("success"):
            print(f"✅ [T.I.A.] Handshake successful - {pioneer_data['data'].get('status', 'UNKNOWN')}")
            bridge.sync_to_shadow_archive(pioneer_data)
        else:
            print(f"⚠️ [T.I.A.] Handshake failed: {pioneer_data.get('error')}")
    except Exception as e:
        print(f"❌ [T.I.A.] Pioneer integration error: {e}")

    # 4. Generate Unified Report
    generate_report(gd_items, hf_items, pioneer_data)

if __name__ == "__main__":
    main()