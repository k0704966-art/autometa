import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_to_drive(file_path, folder_name="ytauto"):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_authorized_user_info(json.loads(os.environ["GOOGLE_TOKEN"]), SCOPES)
    drive = build("drive", "v3", credentials=creds)

    # Find folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive.files().list(q=query, fields="files(id)").execute()
    folders = results.get("files", [])
    folder_id = folders[0]["id"] if folders else None

    if not folder_id:
        print("📁 Folder not found, creating it...")
        folder_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        folder = drive.files().create(body=folder_metadata, fields="id").execute()
        folder_id = folder["id"]

    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
    file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    
    file = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Drive Upload Success! ID: {file.get('id')}")
