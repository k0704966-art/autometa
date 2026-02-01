import os
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_video_to_drive(file_path, folder_name="ytauto"):
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    
    # Load token from your working GitHub Secret
    creds = Credentials.from_authorized_user_info(
        json.loads(os.environ["GOOGLE_TOKEN"]), 
        SCOPES
    )
    drive = build("drive", "v3", credentials=creds)

    # Find or Create Folder
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive.files().list(q=query, spaces="drive", fields="files(id)").execute()
    folders = results.get("files", [])

    if folders:
        folder_id = folders[0]["id"]
    else:
        folder_metadata = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
        folder = drive.files().create(body=folder_metadata, fields="id").execute()
        folder_id = folder["id"]

    # Upload Media (Resumable for larger video files)
    media = MediaFileUpload(file_path, mimetype="video/mp4", resumable=True)
    file_metadata = {"name": os.path.basename(file_path), "parents": [folder_id]}
    
    print(f"📡 Uploading {file_path} to Drive...")
    file = drive.files().create(body=file_metadata, media_body=media, fields="id").execute()
    print(f"✅ Upload success! File ID: {file.get('id')}")
    return file.get('id')
