import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, folder_id):
    # Load credentials from GitHub Secret
    info = json.loads(os.environ["GDRIVE_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(info)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='video/mp4')
    
    print(f"Uploading {file_path} to Google Drive...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f"✅ Upload Complete! File ID: {file.get('id')}")
