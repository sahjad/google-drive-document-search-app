import uuid
import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
CREDENTIALS_PATH = 'config/credentials.json'
TOKEN_PATH = 'config/token.json'
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

def authenticate():
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"credentials.json not found at {CREDENTIALS_PATH}. Please download it from Google Cloud Console.")
        sys.exit(1)
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("No valid token found. Launching browser for authentication...")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_PATH, 'w') as token_file:
                token_file.write(creds.to_json())
            print("Token saved.")
    return build('drive', 'v3', credentials=creds)

def register_watch():
    if not WEBHOOK_URL:
        print("Missing WEBHOOK_URL in .env")
        sys.exit(1)

    service = authenticate()

    try:
        start_token = service.changes().getStartPageToken().execute()
        token = start_token.get('startPageToken')
        if not token:
            print("[register_drive_webhook] Could not fetch startPageToken.")
            sys.exit(1)
        print("Start page token:", token)
    except Exception as e:
        print(f"[register_drive_webhook] Failed to fetch startPageToken: {e}")
        sys.exit(1)

    channel_id = str(uuid.uuid4())
    body = {
        "id": channel_id,
        "type": "web_hook",
        "address": WEBHOOK_URL
    }

    try:
        response = service.changes().watch(pageToken=start_token['startPageToken'], body=body).execute()
        print("Watch registered successfully.")

        expiration = response.get("expiration")
        if expiration:
            exp_dt = datetime.fromtimestamp(int(expiration) / 1000)
            print("Channel expires at:", exp_dt)
    except Exception as e:
        print(f"[register_drive_webhook] Failed to register webhook: {e}")
        sys.exit(1)

if __name__ == "__main__":
    register_watch()