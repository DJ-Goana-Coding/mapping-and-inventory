import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

def type_effect(text):
    print(text)

def main():
    type_effect("\033[96m\033[1m>>> INITIATING 13TH ZONE GOOGLE DRIVE SWEEP...\033[0m")
    type_effect("\033[38;5;214m[+] Scanning for Hugging Face and GitHub connections...\033[0m\n")

    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('drive', 'v3', credentials=creds)

        # The Query: Look for any file containing these keywords
        query = "fullText contains 'Hugging Face' or fullText contains 'huggingface' or fullText contains 'GitHub' or fullText contains 'github'"
        
        results = service.files().list(
            q=query,
            pageSize=50,
            fields="nextPageToken, files(id, name, webViewLink, createdTime)"
        ).execute()
        
        items = results.get('files', [])

        if not items:
            print('\033[91m[-] No bridging documents found.\033[0m')
        else:
            print("\033[92m[✓] TARGETS ACQUIRED:\033[0m\n")
            for item in items:
                print(f"📄 \033[1m{item['name']}\033[0m")
                print(f"   └─ Created: {item['createdTime']}")
                print(f"   └─ Link: {item['webViewLink']}\n")

    except HttpError as error:
        print(f'\033[91m[!] An error occurred: {error}\033[0m')

if __name__ == '__main__':
    main()
