import os
import json
import asyncio
import requests
from datetime import datetime, timedelta
try:
    from googleapiclient.discovery import build
    from google.oauth2 import service_account
    from googleapiclient.http import MediaIoBaseUpload
except ImportError:
    print("❌ Dependencies missing. Install google-api-python-client and google-auth.")
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

class PioneerBridge:
    def __init__(self):
        self.pioneer_url = os.getenv("PIONEER_TRADER_URL")
        self.huggingface_url = os.getenv("HUGGINGFACE_SPACE_URL")  # If applicable
        self.auth_token = os.getenv("PIONEER_AUTH_TOKEN")
        
        self.node_status = {
            "pioneer_trader": {"status": "UNKNOWN", "last_check": None},
            "huggingface_space": {"status": "UNKNOWN", "last_check": None}
        }
        
        self.pulse_interval = 30  # 30 seconds
        self.zombie_threshold = timedelta(minutes=2)  # Mark as zombie after 2 mins
    
    async def health_pulse(self):
        """
        Continuous health monitoring loop.
        Checks all deployment nodes every 30 seconds.
        """
        while True:
            try:
                await self._check_node_health("pioneer_trader", self.pioneer_url)
                
                if self.huggingface_url:
                    await self._check_node_health("huggingface_space", self.huggingface_url)
                
                # Update inventory report if any zombie detected
                if self._has_zombies():
                    await self._trigger_zombie_alert()
                
                await asyncio.sleep(self.pulse_interval)
            except Exception as e:
                print(f"⚠️ [T.I.A.] Health pulse error: {e}")
                await asyncio.sleep(self.pulse_interval)
    
    async def _check_node_health(self, node_name, url):
        """Check if a deployment node is alive"""
        if not url:
            return
        
        try:
            response = requests.get(
                f"{url}/health",
                timeout=5,
                headers={"User-Agent": "T.I.A./Berserker-Monitor"}
            )
            
            if response.status_code == 200:
                self.node_status[node_name] = {
                    "status": "ALIVE",
                    "last_check": datetime.now(),
                    "response_time": response.elapsed.total_seconds()
                }
                print(f"✅ [T.I.A.] {node_name} - ALIVE ({response.elapsed.total_seconds():.2f}s)")
            else:
                self._mark_as_zombie(node_name, f"HTTP {response.status_code}")
        except requests.exceptions.Timeout:
            self._mark_as_zombie(node_name, "TIMEOUT")
        except Exception as e:
            self._mark_as_zombie(node_name, f"ERROR: {str(e)}")
    
    def _mark_as_zombie(self, node_name, reason):
        """Mark a node as zombie and log"""
        self.node_status[node_name] = {
            "status": "ZOMBIE",
            "last_check": datetime.now(),
            "reason": reason
        }
        print(f"🧟 [T.I.A.] {node_name} - ZOMBIE ({reason})")
    
    def _has_zombies(self):
        """Check if any nodes are zombies"""
        return any(node["status"] == "ZOMBIE" for node in self.node_status.values())
    
    async def _trigger_zombie_alert(self):
        """Update INVENTORY_REPORT.md with zombie alert"""
        # This will be called by inventory_engine to regenerate report
        print(f"🚨 [T.I.A.] ZOMBIE DETECTED - Triggering re-deployment alert")
        # Could also send notification via webhook, email, etc.

if __name__ == '__main__':
    mission_start()
