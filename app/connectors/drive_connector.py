# This module provides functionality to connect to Google Drive, list supported files, and download files.
# It handles authentication, file listing, and downloading files with size limits.

import os
import io
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_PATH = 'config/credentials.json'
TOKEN_PATH = 'config/token.json'

SUPPORTED_MIME_TYPES = {
    'text/plain': '.txt',
    'text/csv': '.csv',
    'application/pdf': '.pdf',
    'image/png': '.png'
}
MAX_FILE_SIZE_MB = 2

class GoogleDriveConnector:
    def __init__(self):
        self.service = self.authenticate()

    def authenticate(self):
        try:
            creds = None
            if os.path.exists(TOKEN_PATH):
                creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_PATH):
                        raise FileNotFoundError(f"Credentials file not found at {CREDENTIALS_PATH}")
                    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                    creds = flow.run_local_server(port=0)
                with open(TOKEN_PATH, 'w') as token:
                    token.write(creds.to_json())
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            print(f"Auth Failed to authenticate with Google Drive: {e}")
            raise

    def get_full_folder_path(self, parent_id):
        path_parts = []
        while parent_id:
            try:
                folder = self.service.files().get(fileId=parent_id, fields="name, parents").execute()
                path_parts.insert(0, folder["name"])
                parent_id = folder.get("parents", [None])[0]
            except Exception:
                break
        return "/".join(path_parts)

    def list_supported_files(self, folder_id=None):
        query = " or ".join([f"mimeType='{mime}'" for mime in SUPPORTED_MIME_TYPES])
        if folder_id:
            query = f"'{folder_id}' in parents and ({query})"
        query = f"({query}) and trashed = false"

        files = []
        page_token = None

        while True:
            try:
                results = self.service.files().list(
                    q=query,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, parents)",
                    pageToken=page_token
                ).execute()

                for file in results.get('files', []):
                    try:
                        size_mb = int(file.get('size', 0)) / (1024 * 1024)
                        if size_mb > MAX_FILE_SIZE_MB:
                            continue
                        parent_id = file.get("parents", [None])[0]
                        file["folder_name"] = self.get_full_folder_path(parent_id) if parent_id else ""
                        files.append(file)
                    except Exception as e:
                        print(f"Skipped file due to error: {e}")
                        continue

                page_token = results.get('nextPageToken')
                if not page_token:
                    break

            except Exception as e:
                print(f"Error fetching files: {e}")
                break

        return files

    def download_file(self, file_id):
        try:
            request = self.service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
            return fh
        except Exception as e:
            print(f"Failed to download file {file_id}: {e}")
            return None