import os
import sys
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailFetcher:
    def __init__(self, creds=None):
        self.service = None
        self.creds = creds
        
        self.authenticate()

        if self.creds:
            try:
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                print(f"[ERROR] Failed to build Gmail service: {e}")

    def authenticate(self):
        """Handles OAuth 2.0 Flow (Shared Logic)."""
        # If injected, skip file reads
        if self.creds and self.creds.valid:
            return

        token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
        client_secrets_path = os.path.join(os.path.dirname(__file__), "..", Config.GOOGLE_CLIENT_SECRET_PATH)

        # 1. Load existing token
        if os.path.exists(token_path):
            self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        # 2. Refresh or Login
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                print("[INFO] Refreshing Gmail OAuth Token...")
                try:
                    self.creds.refresh(Request())
                except Exception as e:
                    print(f"[WARN] Failed to refresh token: {e}. Re-authenticating.")
                    self.creds = None
            
            if not self.creds:
                if not os.path.exists(client_secrets_path):
                    print(f"[ERROR] Client Secrets file not found at: {client_secrets_path}")
                    print("Please download credentials from Google Cloud Console (OAuth 2.0 Client ID) and save as 'client_secret.json' in the project root.")
                    return

                print("[INFO] Starting Gmail OAuth Login Flow...")
                flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # 3. Save Token
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())
                print(f"[INFO] Token saved to {token_path}")

    def fetch_flagged_emails(self, limit=5):
        """Fetches starred emails."""
        if not self.service:
            print("[WARN] Gmail service not available. Returning empty list.")
            return []

        try:
            results = self.service.users().messages().list(userId='me', q='label:STARRED', maxResults=limit).execute()
            messages = results.get('messages', [])
            
            emails = []
            if not messages:
                print("[INFO] No starred emails found.")

            for msg in messages:
                txt = self.service.users().messages().get(userId='me', id=msg['id']).execute()
                payload = txt.get('payload', {})
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")
                sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
                
                emails.append({
                    "id": msg['id'],
                    "subject": subject,
                    "sender": sender,
                    "snippet": txt.get('snippet', '')
                })
            return emails

        except Exception as e:
            print(f"[ERROR] Failed to fetch emails: {e}")
            return []

def run():
    fetcher = GmailFetcher()
    return fetcher.fetch_flagged_emails()

if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
