import os
import io
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# --- 🎯 TARGET GENETIC MARKERS ---
# These are the keywords the script will hunt for in file names and full text
TARGET_KEYWORDS = [
    '1986', 'NACC', 'Magna Carta', 'CGAL', 'Genesis', 'Citadel', 
    'ISO 20022', 'AP+', 'Sovereign', 'Swarm', 'T.I.A.', 'Oracle', 
    'Big Doofy', 'Goanna', 'Trading Ledger', 'Vault', 'Private Key'
]

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
LORE_DIR = "13th_Zone_Lore"

def get_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('drive', 'v3', credentials=creds)

def search_and_download():
    service = get_service()
    if not os.path.exists(LORE_DIR): os.makedirs(LORE_DIR)

    print("\033[96m[+] INITIATING DEEP CRAWL FOR SOVEREIGN ASSETS...\033[0m")
    
    # Building a complex query to find Lore, Code, and Personas
    query_parts = [f"fullText contains '{kw}'" for kw in TARGET_KEYWORDS]
    query = " or ".join(query_parts)
    
    results = service.files().list(
        q=f"({query}) and trashed = false",
        fields="files(id, name, mimeType)",
        pageSize=100
    ).execute()
    
    items = results.get('files', [])

    if not items:
        print("\033[91m[-] No new important assets found. The perimeter is clean.\033[0m")
        return

    for item in items:
        file_id = item['id']
        name = item['name'].replace("/", "_")
        mime = item['mimeType']
        
        print(f"\033[38;5;214m[FOUND] {name} ({mime})\033[0m")
        
        try:
            # Handle Google Docs (Convert to Markdown/Text)
            if mime == 'application/vnd.google-apps.document':
                request = service.files().export_media(fileId=file_id, mimeType='text/plain')
                extension = ".md"
            # Handle Binaries (PDF, Zip, JSON)
            else:
                request = service.files().get_media(fileId=file_id)
                extension = "" if "." in name else ".bin"

            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                _, done = downloader.next_chunk()

            save_path = os.path.join(LORE_DIR, f"Drive_{name}{extension}")
            with open(save_path, "wb") as f:
                f.write(fh.getvalue())
            print(f"    └─ \033[92mDownloaded to {LORE_DIR}\033[0m")
            
        except Exception as e:
            print(f"    └─ \033[91mError: {e}\033[0m")

if __name__ == "__main__":
    search_and_download()
