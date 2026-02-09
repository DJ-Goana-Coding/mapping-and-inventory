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
