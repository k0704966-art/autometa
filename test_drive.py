import os
import json
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

def test_drive_with_transfer():
    # 1. Setup
    folder_id = os.getenv("FOLDER_ID")
    your_email = "k0704966@gmail.com" # <--- CHANGE THIS
    test_file = "connection_test.txt"
    
    print(f"🛠️ Initializing Test for Folder: {folder_id}")
    
    # Load Credentials
    info = json.loads(os.environ["GDRIVE_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    # 2. Create local test file
    with open(test_file, "w") as f:
        f.write(f"Test successful at {time.ctime()}. Robot has handed this file to you.")

    try:
        # 3. Upload the file
        print("📡 Step 1: Uploading tiny file...")
        file_metadata = {'name': test_file, 'parents': [folder_id]}
        media = MediaFileUpload(test_file, mimetype='text/plain')
        
        # We use supportsAllDrives=True to ensure it respects the shared folder
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id',
            supportsAllDrives=True 
        ).execute()
        
        file_id = uploaded_file.get('id')
        print(f"✅ File Uploaded! ID: {file_id}")

        # 4. Transfer Ownership (The key to fixing the Quota error)
        print(f"🔑 Step 2: Transferring ownership to {your_email}...")
        permission = {
            'role': 'owner',
            'type': 'user',
            'emailAddress': your_email
        }
        
        # This moves the file into YOUR storage quota
        service.permissions().create(
            fileId=file_id,
            body=permission,
            transferOwnership=True,
            supportsAllDrives=True
        ).execute()
        
        print("\n✨ ALL TESTS PASSED!")
        print(f"Check your Drive folder '{folder_id}'. You should see '{test_file}' owned by YOU.")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        if "storageQuotaExceeded" in str(e):
            print("\n💡 DIAGNOSIS: The 'Transfer' failed because the Robot tried to 'own' it for too long.")
            print("Action: Make sure the Service Account is an EDITOR on the folder.")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)

if __name__ == "__main__":
    test_drive_with_transfer()
