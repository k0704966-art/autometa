import os
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from uploader import upload_to_drive

def run_connection_test():
    folder_id = os.getenv("FOLDER_ID")
    test_filename = "drive_test_success.txt"
    
    # Load credentials to check permissions first
    info = json.loads(os.environ["GDRIVE_CREDENTIALS"])
    creds = service_account.Credentials.from_service_account_info(
        info, scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)

    print("🛠️ Starting Drive Connection Test...")

    # 1. PRE-CHECK: Can the robot see the folder?
    try:
        print(f"🔍 Checking access to Folder ID: {folder_id}...")
        folder_metadata = service.files().get(
            fileId=folder_id, 
            fields='name, capabilities',
            supportsAllDrives=True
        ).execute()
        print(f"✅ Robot found folder: '{folder_metadata.get('name')}'")
        
        can_add_children = folder_metadata.get('capabilities', {}).get('canAddChildren')
        print(f"ℹ️ Permission to write: {'YES' if can_add_children else 'NO'}")
        
    except Exception as e:
        print(f"❌ PRE-CHECK FAILED: Cannot find folder. Error: {e}")
        print("💡 FIX: Ensure you shared the folder with the service account email.")
        return

    # 2. Create tiny dummy file
    with open(test_filename, "w") as f:
        f.write("Google Drive connection is working perfectly!")

    # 3. Attempt Upload using updated uploader logic
    try:
        print(f"📡 Attempting upload...")
        upload_to_drive(test_filename, folder_id)
        print("\n✨ TEST SUCCESS: Check your Google Drive now!")
    except Exception as e:
        print(f"\n❌ UPLOAD FAILED: {str(e)}")
    finally:
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == "__main__":
    run_connection_test()
