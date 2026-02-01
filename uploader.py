import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]
DRIVE_FOLDER_NAME = "ytauto"


def get_drive_service():
    creds = Credentials.from_authorized_user_info(
        json.loads(os.environ["GOOGLE_TOKEN"]),
        SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return build("drive", "v3", credentials=creds)


def get_or_create_folder(service, folder_name):
    # 1️⃣ Search for existing folder
    query = (
        f"name='{folder_name}' and "
        "mimeType='application/vnd.google-apps.folder' and "
        "trashed=false"
    )

    response = service.files().list(
        q=query,
        spaces="drive",
        fields="files(id, name)"
    ).execute()

    files = response.get("files", [])
    if files:
        return files[0]["id"]

    # 2️⃣ Create folder if not found
    folder_metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder"
    }

    folder = service.files().create(
        body=folder_metadata,
        fields="id"
    ).execute()

    return folder["id"]


def upload_video_to_drive(filename):
    service = get_drive_service()

    # ✅ Ensure ytauto folder exists
    folder_id = get_or_create_folder(service, DRIVE_FOLDER_NAME)

    media = MediaFileUpload(
        filename,
        mimetype="video/mp4",
        resumable=True
    )

    file_metadata = {
        "name": os.path.basename(filename),
        "parents": [folder_id]
    }

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()

    print("📤 Drive file ID:", file["id"])










# import os
# import json
# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload

# SCOPES = ["https://www.googleapis.com/auth/drive"]


# def upload_video_to_drive(filename):
#     creds = Credentials.from_authorized_user_info(
#         json.loads(os.environ["GOOGLE_TOKEN"]),
#         SCOPES
#     )

#     if creds.expired and creds.refresh_token:
#         creds.refresh(Request())

#     drive = build("drive", "v3", credentials=creds)

#     media = MediaFileUpload(
#         filename,
#         mimetype="video/mp4",
#         resumable=True
#     )

#     file = drive.files().create(
#         body={"name": os.path.basename(filename)},
#         media_body=media,
#         fields="id"
#     ).execute()

#     print("📤 Drive file ID:", file["id"])
