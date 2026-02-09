"""
Google Drive Authentication Module
Decodes GOOGLE_CREDENTIALS_B64 from environment and creates temporary credentials.json
"""
import os
import base64
import json
import tempfile
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive']
DRIVE_FOLDER_NAME = 'CITADEL-BOT'

def get_drive_service():
    """
    Initialize Google Drive service with base64-encoded credentials.
    
    Returns:
        Google Drive API service object
    
    Raises:
        ValueError: If GOOGLE_CREDENTIALS_B64 not found in environment
    """
    creds_b64 = os.getenv('GOOGLE_CREDENTIALS_B64')
    
    if not creds_b64:
        raise ValueError("GOOGLE_CREDENTIALS_B64 not found in environment variables")
    
    # Decode base64 credentials
    creds_json = base64.b64decode(creds_b64).decode('utf-8')
    creds_dict = json.loads(creds_json)
    
    # Create credentials object
    credentials = service_account.Credentials.from_service_account_info(
        creds_dict, scopes=SCOPES
    )
    
    # Build Drive service
    service = build('drive', 'v3', credentials=credentials)
    
    return service

def find_citadel_folder(service):
    """
    Locate the CITADEL-BOT folder in Google Drive.
    
    Returns:
        str: Folder ID of CITADEL-BOT
    """
    results = service.files().list(
        q=f"name='{DRIVE_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
        fields="files(id, name)"
    ).execute()
    
    folders = results.get('files', [])
    
    if not folders:
        raise FileNotFoundError(f"{DRIVE_FOLDER_NAME} folder not found in Google Drive")
    
    return folders[0]['id']

def download_file(service, folder_id, filename):
    """
    Download a file from CITADEL-BOT folder.
    
    Args:
        service: Google Drive service object
        folder_id: ID of CITADEL-BOT folder
        filename: Name of file to download
    
    Returns:
        dict: Parsed JSON content of file
    """
    results = service.files().list(
        q=f"name='{filename}' and '{folder_id}' in parents",
        fields="files(id, name)"
    ).execute()
    
    files = results.get('files', [])
    
    if not files:
        return None
    
    file_id = files[0]['id']
    
    # Download file content
    request = service.files().get_media(fileId=file_id)
    content = request.execute()
    
    return json.loads(content.decode('utf-8'))
