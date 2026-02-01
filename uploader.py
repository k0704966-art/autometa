import os
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def upload_to_drive(file_path, folder_id):
    # 1. Parse credentials from GitHub Secret
    info = json.loads(os.environ["GDRIVE_CREDENTIALS"])
    
    # 2. Define Scopes explicitly for Python 3.11+ compatibility
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = service_account.Credentials.from_service_account_info(info, scopes=SCOPES)
    
    # 3. Build the Service
    service = build('drive', 'v3', credentials=creds)

    # 4. Prepare Metadata
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    
    # 5. Use Resumable Upload (Better for larger 60s video files)
    media = MediaFileUpload(
        file_path, 
        mimetype='video/mp4', 
        resumable=True
    )
    
    print(f"📡 Starting resumable upload of {file_path}...")
    
    try:
        request = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   ⬆️ Uploaded {int(status.progress() * 100)}%")
        
        print(f"✅ Upload Complete! File ID: {response.get('id')}")
        return response.get('id')
        
    except Exception as e:
        print(f"❌ Google Drive Upload Error: {e}")
        raise e
