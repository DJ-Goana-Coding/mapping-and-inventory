import os
import time
import subprocess

# --- CITADEL COMMS RELAY ---
LOCAL_FILE = "/sdcard/Documents/vanguard_audit.csv"
# This points to the folder on your Google Drive
REMOTE_PATH = "gdrive:The_12_Spaces/3_DATA/"

def sync_to_cloud():
    print(f"📡 Heartbeat: {time.strftime('%H:%M:%S')} | Syncing Vanguard Audit to Google Drive...")
    try:
        # Pushing the file to the Citadel Cloud
        subprocess.run(["rclone", "copy", LOCAL_FILE, REMOTE_PATH], check=True)
        print("✅ Sync Successful. Vault is up to date.")
    except Exception as e:
        print(f"⚠️ Sync Failed: {e}")

if __name__ == "__main__":
    while True:
        if os.path.exists(LOCAL_FILE):
            sync_to_cloud()
        else:
            print("🔍 Waiting for Vanguard Engine to generate the first audit log...")
        
        # We'll sync every 5 minutes to keep Google's rate limits happy
        time.sleep(300) 
