from typing import Dict, List, Optional, Tuple, Any, Union
import os
import json
import time
import hashlib
import logging
from datetime import datetime
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.http import MediaIoBaseUpload
except ImportError:
    print("❌ Dependencies missing. Install google-api-python-client and google-auth.")
    exit(1)
from io import BytesIO
from utils.drive_auth import get_drive_service, find_citadel_folder, download_file

logger = logging.getLogger(__name__)

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

# --- SOVEREIGN SYNC PROTOCOL ---

PANIC_CHECK_INTERVAL = 30  # Seconds (API-safe)
SYNC_CHECK_INTERVAL = 60   # Check for manifest updates every minute
LAST_PANIC_CHECK = 0
LAST_SYNC_CHECK = 0
LAST_MANIFEST_HASH = None

def check_panic_signal():
    """
    Check for authenticated panic.json signal from Google Drive.
    
    Returns:
        bool: True if valid panic signal detected, False otherwise
    """
    global LAST_PANIC_CHECK
    
    # Rate limit: only check every 30 seconds
    if time.time() - LAST_PANIC_CHECK < PANIC_CHECK_INTERVAL:
        return False
    
    LAST_PANIC_CHECK = time.time()
    
    try:
        service = get_drive_service()
        folder_id = find_citadel_folder(service)
        panic_data = download_file(service, folder_id, 'panic.json')
        
        if not panic_data:
            return False
        
        # Verify signature
        commander_token = os.getenv('AEGIS_COMMANDER_TOKEN')
        if not commander_token:
            logger.error("AEGIS_COMMANDER_TOKEN not configured - cannot verify panic signal")
            return False
        
        # Calculate expected signature
        expected_sig = hashlib.sha256(
            f"{commander_token}{panic_data['timestamp']}".encode()
        ).hexdigest()
        
        if panic_data.get('signature') != expected_sig:
            logger.warning("⚠️ INVALID PANIC SIGNATURE - Possible breach attempt")
            log_security_breach("Invalid panic signature")
            return False
        
        # Check timestamp (prevent replay attacks - 5 min expiry)
        if time.time() - panic_data['timestamp'] > 300:
            logger.warning("Expired panic signal (>5 minutes old)")
            return False
        
        logger.critical(f"🚨 AUTHENTICATED PANIC SIGNAL RECEIVED: {panic_data.get('reason', 'No reason provided')}")
        return True
        
    except Exception as e:
        logger.error(f"Error checking panic signal: {e}")
        return False

def sync_fleet_manifest():
    """
    Pull fleet_manifest.json from Drive and update local configuration.
    
    Returns:
        dict: Updated manifest data, or None if no changes
    """
    global LAST_SYNC_CHECK, LAST_MANIFEST_HASH
    
    # Rate limit: only check every 60 seconds
    if time.time() - LAST_SYNC_CHECK < SYNC_CHECK_INTERVAL:
        return None
    
    LAST_SYNC_CHECK = time.time()
    
    try:
        service = get_drive_service()
        folder_id = find_citadel_folder(service)
        manifest_data = download_file(service, folder_id, 'fleet_manifest.json')
        
        if not manifest_data:
            logger.warning("fleet_manifest.json not found in CITADEL-BOT folder")
            return None
        
        # Calculate manifest hash (MD5 is sufficient for change detection, not security)
        manifest_json = json.dumps(manifest_data, sort_keys=True)
        manifest_hash = hashlib.md5(manifest_json.encode()).hexdigest()
        
        # Check if manifest changed
        if manifest_hash == LAST_MANIFEST_HASH:
            return None  # No changes
        
        logger.info(f"📡 SOVEREIGN OVERRIDE DETECTED - Manifest version: {manifest_data.get('fleet_version')}")
        LAST_MANIFEST_HASH = manifest_hash
        
        # Save to local file
        with open('registry/fleet_manifest.json', 'w') as f:
            json.dump(manifest_data, f, indent=2)
        
        return manifest_data
        
    except Exception as e:
        logger.error(f"Error syncing fleet manifest: {e}")
        return None

def backup_active_positions(positions_data):
    """
    Upload current active positions to Drive recovery folder.
    
    Args:
        positions_data: Dictionary of active trading positions
    """
    try:
        service = get_drive_service()
        folder_id = find_citadel_folder(service)
        
        # Create recovery subfolder if needed
        recovery_folder_id = get_or_create_subfolder(service, folder_id, 'recovery')
        
        # Create backup file
        backup_data = {
            'timestamp': time.time(),
            'positions': positions_data,
            'version': '3.1.0'
        }
        
        upload_json_to_drive(service, recovery_folder_id, 'positions_backup.json', backup_data)
        logger.info(f"💾 Backed up {len(positions_data)} active positions to Drive")
        
    except Exception as e:
        logger.error(f"Error backing up positions: {e}")

def log_security_breach(breach_type):
    """
    Log security breach attempt to Drive.
    
    Args:
        breach_type: Description of breach attempt
    """
    try:
        service = get_drive_service()
        folder_id = find_citadel_folder(service)
        security_folder_id = get_or_create_subfolder(service, folder_id, 'security_logs')
        
        breach_data = {
            'timestamp': time.time(),
            'type': breach_type,
            'ip': 'N/A',  # Can be enhanced with actual IP detection
        }
        
        # Append to daily log file
        filename = f"breach_log_{time.strftime('%Y%m%d')}.json"
        upload_json_to_drive(service, security_folder_id, filename, breach_data, append=True)
        
    except Exception as e:
        logger.error(f"Error logging security breach: {e}")

# Helper functions
def get_or_create_subfolder(service, parent_id, folder_name):
    """Get or create a subfolder in Drive"""
    # First, check if folder exists
    results = service.files().list(
        q=f"name='{folder_name}' and '{parent_id}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    
    folders = results.get('files', [])
    
    if folders:
        return folders[0]['id']
    
    # Create new folder
    file_metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder',
        'parents': [parent_id]
    }
    
    folder = service.files().create(body=file_metadata, fields='id').execute()
    return folder.get('id')

def upload_json_to_drive(service, folder_id, filename, data, append=False):
    """Upload JSON data to Drive"""
    # If append mode, try to download existing file first
    if append:
        existing_data = download_file(service, folder_id, filename)
        if existing_data:
            # If existing data is a list, append to it
            if isinstance(existing_data, list):
                existing_data.append(data)
                data = existing_data
            # If existing data is a dict, create a list
            else:
                data = [existing_data, data]
    
    # Convert data to JSON
    json_str = json.dumps(data, indent=2)
    fh = BytesIO(json_str.encode('utf-8'))
    
    # Check if file exists
    results = service.files().list(
        q=f"name='{filename}' and '{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()
    
    files = results.get('files', [])
    
    file_metadata = {
        'name': filename,
        'parents': [folder_id]
    }
    
    media = MediaIoBaseUpload(fh, mimetype='application/json')
    
    if files:
        # Update existing file
        file_id = files[0]['id']
        service.files().update(
            fileId=file_id,
            media_body=media
        ).execute()
    else:
        # Create new file
        service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
import os, time, json, shutil, hashlib

def verify_signature(data):
    """[T.I.A.] Auth check for Drive commands"""
    token = os.getenv("AEGIS_COMMANDER_TOKEN")
    expected = hashlib.sha256(f"{token}{data['timestamp']}".encode()).hexdigest()
    return data.get('signature') == expected

def sovereign_sync(drive_path="/content/drive/MyDrive/CITADEL-BOT/"):
    """[T.I.A.] The Sovereign Handshake"""
    while True:
        if os.path.exists(f"{drive_path}panic.json"):
            with open(f"{drive_path}panic.json", 'r') as f:
                if verify_signature(json.load(f)): os.system("touch ../pioneer-trader/EXIT_NOW")
        
        if os.path.exists(f"{drive_path}fleet_manifest.json"):
            shutil.copy(f"{drive_path}fleet_manifest.json", "../pioneer-trader/registry/fleet_manifest.json")
        time.sleep(30)
