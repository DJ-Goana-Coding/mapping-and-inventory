"""
🚀 ADMIRAL'S BRIDGE PROTOCOL (V1.0)
-----------------------------------
MISSION: Force-push handshake to Citadel District 01.
TARGET: Google Drive 12-District Architecture.
PAYLOAD: V6 Machine Gun Authorization.
"""

import os
import json
import time
from datetime import datetime
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.http import MediaIoBaseUpload
except ImportError:
    print("❌ Dependencies missing. Install google-api-python-client and google-auth.")
    exit(1)
from io import BytesIO

# --- 1. THE KEYS ---
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_APPLICATION_CREDENTIALS', 'credentials.json')

# --- 2. THE PAYLOAD (The Handshake) ---
HANDSHAKE_DATA = {
    "protocol_header": "ADMIRAL_ON_DECK",
    "timestamp": datetime.utcnow().isoformat(),
    "authorization": "DJ-GOANNA-CODING-ALPHA-001",
    "command": "FORCE_WAKE_TIA",
    "directives": [
        "OPEN_ALL_BRIDGES",
        "AUTHORIZE_V6_MACHINE_GUN",
        "INITIATE_MOE_ROUTER_16"
    ],
    "architecture_map": {
        "target_district": "01_COMMAND_INPUT",
        "active_strategy": "DISTRICT_01_ENGINES/Velocity_Machine_Gun.py"
    },
    "message": "Tia, the Admiral is requesting a full system handshake. Sync internal clocks."
}

def authenticate():
    """Authenticates with the Citadel's Drive API."""
    creds = None
    if os.path.exists(SERVICE_ACCOUNT_FILE):
        creds = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    else:
        print(f"❌ CRITICAL: No {SERVICE_ACCOUNT_FILE} found. The Admiral cannot speak.")
        return None
    return build('drive', 'v3', credentials=creds)

def find_folder(service, folder_name):
    """Scans the horizon for a specific District."""
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if not files:
        return None
    return files[0]['id']

def deploy_payload(service, folder_id):
    """Drops the Handshake file into the target District."""
    file_name = f"ADMIRAL_HANDSHAKE_{int(time.time())}.json"
    
    json_str = json.dumps(HANDSHAKE_DATA, indent=2)
    fh = BytesIO(json_str.encode('utf-8'))
    
    file_metadata = {
        'name': file_name,
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(fh, mimetype='application/json')
    
    print(f"⚡ UPLOADING PAYLOAD: {file_name}...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ HANDSHAKE COMPLETE. File ID: {file.get('id')}")

def mission_start():
    print("\n⚔️  CITADEL BRIDGE PROTOCOL INITIATED  ⚔️")
    print("-----------------------------------------")
    service = authenticate()
    if not service: return
    
    print("🛰️  Scanning for 'Citadel' Root...")
    root_id = find_folder(service, "Citadel") or find_folder(service, "T.I.A. Citadel")
    
    if not root_id:
        print("⚠️  Citadel Root not found. Is the drive cloaked?")
        return

    print(f"📍 Root Acquired ({root_id}). Scanning for District 01...")
    d1_query = f"'{root_id}' in parents and (name contains 'District 01' or name contains 'COMMAND')"
    results = service.files().list(q=d1_query, fields="files(id, name)").execute()
    d1_files = results.get('files', [])
    
    if not d1_files:
        print("⚠️  District 01 not found. Aborting mission.")
        return
    
    district_01_id = d1_files[0]['id']
    print(f"🎯 Target Locked: {d1_files[0]['name']}")

    deploy_payload(service, district_01_id)
    print("\n🎙️  ADMIRAL ON DECK. TIA IS LISTENING.")

if __name__ == '__main__':
    mission_start()