import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_to_drive(file_path, folder_name="ytauto"):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    
    # Load token from your GitHub Secret
    creds_info = json.loads(os.environ["GOOGLE_TOKEN"])
    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    
    # Refresh token if expired
    if creds.expired and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())

    service = build("drive", "v3", credentials=creds)

    # 1. Find or create the folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    folders = results.get("files", [])

    if folders:
        folder_id = folders[0]["id"]
        print(f"📁 Using existing folder: {folder_name} ({folder_id})")
    else:
        folder_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        folder = service.files().create(body=folder_metadata, fields="id").execute()
        folder_id = folder["id"]
        print(f"📁 Created new folder: {folder_name} ({folder_id})")

    # 2. Upload the file
    file_metadata = {
        "name": os.path.basename(file_path),
        "parents": [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
    
    print(f"📡 Uploading {file_path}...")
    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()
    
    print(f"✅ Drive Upload Success! File ID: {file.get('id')}")
    return file.get('id')
