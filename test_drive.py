import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]

# Load token from GitHub Secret
creds = Credentials.from_authorized_user_info(
    json.loads(os.environ["GOOGLE_TOKEN"]),
    SCOPES
)

if creds.expired and creds.refresh_token:
    creds.refresh(Request())

drive = build("drive", "v3", credentials=creds)

# ---------------------------------------------------
# 1. Get or create folder "ytauto"
# ---------------------------------------------------
folder_name = "ytauto"

query = (
    f"name='{folder_name}' and "
    "mimeType='application/vnd.google-apps.folder' and "
    "trashed=false"
)

results = drive.files().list(
    q=query,
    spaces="drive",
    fields="files(id, name)"
).execute()

folders = results.get("files", [])

if folders:
    folder_id = folders[0]["id"]
    print(f"📁 Found folder '{folder_name}' ({folder_id})")
else:
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }
    folder = drive.files().create(
        body=folder_metadata,
        fields="id"
    ).execute()
    folder_id = folder["id"]
    print(f"📁 Created folder '{folder_name}' ({folder_id})")

# ---------------------------------------------------
# 2. Create test file
# ---------------------------------------------------
with open("github_test.txt", "w") as f:
    f.write("Hello from GitHub → ytauto 🚀")

media = MediaFileUpload("github_test.txt", mimetype="text/plain")

# ---------------------------------------------------
# 3. Upload file INTO the folder
# ---------------------------------------------------
file = drive.files().create(
    body={
        "name": "github_test.txt",
        "parents": [folder_id]
    },
    media_body=media,
    fields="id"
).execute()

print("✅ GitHub upload success:", file["id"])
