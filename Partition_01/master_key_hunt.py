import os
import re
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# --- ⚙️ HUNTER CONFIG ---
LORE_DIR = "13th_Zone_Lore"
VAULT_FILE = "master_vault.json"
# Patterns: HuggingFace, GitHub, OpenAI, Ethereum/DEX Keys, Generic long strings
KEY_PATTERNS = [r'hf_[a-zA-Z0-0]{34}', r'ghp_[a-zA-Z0-0]{36}', r'sk-[a-zA-Z0-0]{48}', r'0x[a-fA-F0-0]{64}']

def hunt_drive():
    creds = Credentials.from_authorized_user_file('token.json')
    service = build('drive', 'v3', credentials=creds)
    
    # Searching for text files and docs
    query = "mimeType='application/vnd.google-apps.document' or mimeType='text/plain'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    print(f"\033[96m[+] Scanning {len(items)} Drive files for 'Really Long Keys'...\033[0m")
    
    for item in items:
        # Exporting Google Docs to plain text to scan them
        try:
            request = service.files().export_media(fileId=item['id'], mimeType='text/plain')
            content = request.execute().decode('utf-8')
            
            for pattern in KEY_PATTERNS:
                matches = re.findall(pattern, content)
                if matches:
                    print(f"\033[92m[FOUND] Key in file: {item['name']}\033[0m")
                    with open(VAULT_FILE, "a") as f:
                        for m in matches: f.write(f"{item['name']}: {m}\n")
        except: continue

if __name__ == "__main__":
    hunt_drive()
