import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/drive"]


def upload_video_to_drive(filename):
    creds = Credentials.from_authorized_user_info(
        json.loads(os.environ["GOOGLE_TOKEN"]),
        SCOPES
    )

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    drive = build("drive", "v3", credentials=creds)

    media = MediaFileUpload(
        filename,
        mimetype="video/mp4",
        resumable=True
    )

    file = drive.files().create(
        body={"name": os.path.basename(filename)},
        media_body=media,
        fields="id"
    ).execute()

    print("📤 Drive file ID:", file["id"])
