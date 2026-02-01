import os
import json
from uploader import upload_to_drive

# This script only tests the Google Drive connection
def run_connection_test():
    folder_id = os.getenv("FOLDER_ID")
    test_filename = "drive_test_success.txt"
    
    print("🛠️ Starting Drive Connection Test...")
    
    # 1. Create a tiny dummy file
    with open(test_filename, "w") as f:
        f.write("Google Drive connection is working perfectly!")
    
    # 2. Try to upload it
    try:
        print(f"📡 Attempting to upload to Folder ID: {folder_id}")
        upload_to_drive(test_filename, folder_id)
        print("\n✅ TEST SUCCESS: The file should be visible in your Drive folder now.")
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        print("\nChecklist for failure:")
        print("1. Did you share the Drive folder with the Service Account email?")
        print("2. Is the GDRIVE_CREDENTIALS secret exactly correct (with { } braces)?")
    finally:
        # Cleanup local file
        if os.path.exists(test_filename):
            os.remove(test_filename)

if __name__ == "__main__":
    run_connection_test()
