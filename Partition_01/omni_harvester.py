import os
import csv
import time
import io
import json

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# --- ⚙️ HARVESTER CONFIGURATION ---
LORE_DIR = "13th_Zone_Lore"
CSV_FILE = "copilot-activity-history.csv"
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
# The genetic markers the script hunts for to separate Lore from Junk
KEYWORDS = ['1986', 'nacc', 'magna carta', 'ap+', 'iso 20022', 'framework', 'worldbuilding', 'sovereign', 'swarm', 'lore', 'citadel', 't.i.a.', 'goanna']

def type_effect(text):
    print(text)
    time.sleep(0.02)

def ensure_directory():
    if not os.path.exists(LORE_DIR):
        os.makedirs(LORE_DIR)

# --- 🚀 STAGE 1: LOCAL CSV EXTRACTION ---
def harvest_csv():
    type_effect("\033[96m\033[1m[+] INITIATING STAGE 1: CSV LORE EXTRACTION...\033[0m")
    if not os.path.exists(CSV_FILE):
        print(f"\033[91m[-] {CSV_FILE} not found in root. Skipping Stage 1.\033[0m")
        return

    extracted_count = 0
    with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        # Some CSVs use different delimiters, sniffing helps but we assume standard comma
        reader = csv.reader(f)
        try:
            headers = next(reader)
        except:
            return

        for i, row in enumerate(reader):
            if len(row) >= 4:
                author = row[2]
                message = row[3]
                
                # Check if message is substantial and contains Sovereign genetic markers
                if len(message) > 300 and any(kw in message.lower() for kw in KEYWORDS):
                    filename = os.path.join(LORE_DIR, f"Copilot_Lore_Fragment_{i}.md")
                    with open(filename, "w", encoding='utf-8') as out_f:
                        out_f.write(f"# Extracted Lore Fragment (Row {i})\n\n")
                        out_f.write(message)
                    extracted_count += 1
                    
    print(f"\033[92m[✓] Extracted {extracted_count} massive lore fragments from the CSV.\033[0m")

# --- ☁️ STAGE 2: GOOGLE DRIVE VACUUM ---
def harvest_drive():
    type_effect("\n\033[96m\033[1m[+] INITIATING STAGE 2: GOOGLE DRIVE CLOUD VACUUM...\033[0m")
    
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

    try:
        service = build('drive', 'v3', credentials=creds)
        # Search for Google Docs, JSON, or Markdown files containing our Lore keywords
        query = "(mimeType='application/vnd.google-apps.document' or mimeType='text/markdown' or mimeType='application/json') and (" + " or ".join([f"fullText contains '{kw}'" for kw in KEYWORDS[:5]]) + ")"
        
        results = service.files().list(q=query, pageSize=50, fields="nextPageToken, files(id, name, mimeType)").execute()
        items = results.get('files', [])

        if not items:
            print('\033[90m[-] No matching Drive assets found.\033[0m')
            return

        for item in items:
            file_id = item['id']
            file_name = item['name'].replace("/", "_").replace(" ", "_")
            mime_type = item['mimeType']
            
            print(f"\033[38;5;214m    └─ Vacuuming Cloud Asset: {file_name}...\033[0m")
            
            try:
                # If it's a Google Doc, we force-export it to plain text for the Omni-Brain
                if mime_type == 'application/vnd.google-apps.document':
                    request = service.files().export_media(fileId=file_id, mimeType='text/plain')
                    file_ext = ".md"
                else:
                    # Native JSON or MD files
                    request = service.files().get_media(fileId=file_id)
                    file_ext = ".json" if "json" in mime_type else ".md"
                
                # Download stream
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                # Save to 13th Zone Lore directory
                save_path = os.path.join(LORE_DIR, f"Drive_{file_name}{file_ext}")
                with open(save_path, "wb") as f:
                    f.write(fh.getvalue())
                    
            except Exception as e:
                print(f"\033[91m      [!] Error extracting {file_name}: {e}\033[0m")

        print(f"\033[92m[✓] Successfully harvested {len(items)} files from Google Drive.\033[0m")

    except HttpError as error:
        print(f'\033[91m[!] Google Drive Auth Error: {error}\033[0m')
        print(f"\033[90m(If you don't have credentials.json set up, skip Stage 2 for now).\033[0m")

def run_omni_harvest():
    os.system('clear' if os.name == 'posix' else 'cls')
    type_effect("\033[96m\033[1m╔═══════════════════════════════════════════════════════════╗\033[0m")
    type_effect("\033[96m\033[1m║ 🌪️ THE OMNI-HARVESTER: TOTAL DATA ASSIMILATION            ║\033[0m")
    type_effect("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")
    
    ensure_directory()
    harvest_csv()
    harvest_drive()
    
    print("\033[96m\033[1m╠═══════════════════════════════════════════════════════════╣\033[0m")
    print("\033[96m\033[1m║ 🧠 HARVEST COMPLETE. 13TH_ZONE_LORE IS PRIMED.           ║\033[0m")
    print("\033[96m\033[1m╚═══════════════════════════════════════════════════════════╝\033[0m")
    print("\033[38;5;214m>> Next Step: Run omni_brain_mesh.py to vectorize the harvest.\033[0m\n")

if __name__ == "__main__":
    run_omni_harvest()
