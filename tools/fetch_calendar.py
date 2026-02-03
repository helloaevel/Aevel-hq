import os
import sys
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

# Scopes now include both Gmail and Calendar to maintain a single token
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

class CalendarFetcher:
    def __init__(self, creds=None):
        self.service = None
        self.creds = creds
        self.authenticate()

        if self.creds:
            try:
                self.service = build('calendar', 'v3', credentials=self.creds)
            except Exception as e:
                print(f"[ERROR] Failed to build Calendar service: {e}")

    def authenticate(self):
        """Handles OAuth 2.0 Flow (Shared Logic)."""
        # If we already have valid creds (injected), skip file logic
        if self.creds and self.creds.valid:
            return

        token_path = os.path.join(os.path.dirname(__file__), "..", "token.json")
        client_secrets_path = os.path.join(os.path.dirname(__file__), "..", Config.GOOGLE_CLIENT_SECRET_PATH)

        # 1. Load existing token
        if not self.creds and os.path.exists(token_path):
            try:
                self.creds = Credentials.from_authorized_user_file(token_path, SCOPES)
            except Exception:
                print("[WARN] Token scopes mismatch or invalid. Re-authenticating...")
                self.creds = None

        # 2. Refresh or Login
        if self.creds and self.creds.expired and self.creds.refresh_token:
            print("[INFO] Refreshing OAuth Token...")
            try:
                self.creds.refresh(Request())
            except Exception as e:
                print(f"[WARN] Failed to refresh token: {e}. Re-authenticating.")
                self.creds = None
        
        if not self.creds or not self.creds.valid:
            # If still invalid and we are in production/headless (checked by env or missing file)
            # We cannot run local server.
            if not os.path.exists(client_secrets_path):
                print(f"[ERROR] Client Secrets not found. Cannot auth.")
                return

            # Check if we are running in interactive mode or if this is a headless server
            if os.getenv("RENDER") or os.getenv("HEADLESS"):
                 print("[ERROR] Cannot perform browser auth in headless environment. Please authenticate locally first.")
                 return

            print("[INFO] Starting OAuth Login Flow (Calendar + Gmail)...")
            # Force delete old token if it exists to avoid scope mixups
            if os.path.exists(token_path):
                os.remove(token_path)
                
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)
            self.creds = flow.run_local_server(port=0)
            
            # 3. Save Token
            with open(token_path, 'w') as token:
                token.write(self.creds.to_json())
            print(f"[INFO] New token saved to {token_path}")

    def fetch_upcoming_events(self, limit=10):
        """Fetches the next 10 events from the primary calendar."""
        if not self.service:
            print("[WARN] Calendar service not available.")
            return []

        try:
            # Fetch from Start of Today (Local Time) to see the whole day's context
            # Note: Ideally we handle timezones explicitly, but for local run, stripping time works for 'Today'
            start_of_day = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            time_min = start_of_day.isoformat() + 'Z' # Appending Z implies UTC, but for local MVP we accept the shift or fix later
            
            print(f"Fetching events from: {time_min}...")
            
            events_result = self.service.events().list(
                calendarId='primary', 
                timeMin=time_min,
                maxResults=limit, 
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            structured_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                
                structured_events.append({
                    "event_id": event['id'],
                    "summary": event.get('summary', 'Untitled Event'),
                    "start": start,
                    "end": end,
                    "link": event.get('htmlLink'),
                    "organizer": event.get('organizer', {}).get('email')
                })
                
            return structured_events

        except Exception as e:
            print(f"[ERROR] Failed to fetch events: {e}")
            return []

def run():
    fetcher = CalendarFetcher()
    return fetcher.fetch_upcoming_events()

if __name__ == "__main__":
    events = run()
    print("\n--- UPCOMING EVENTS ---")
    for e in events:
        print(f"[{e['start']}] {e['summary']}")
