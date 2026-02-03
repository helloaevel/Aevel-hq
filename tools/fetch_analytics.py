import os
import sys
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

class AnalyticsFetcher:
    def __init__(self):
        self.creds_path = Config.GOOGLE_CREDS_PATH
        self.service = None
        self.sheet_id = Config.GOOGLE_SHEET_ID
        
        if self.creds_path and os.path.exists(self.creds_path):
            try:
                scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
                creds = service_account.Credentials.from_service_account_file(
                    self.creds_path, scopes=scopes
                )
                self.service = build('sheets', 'v4', credentials=creds)
            except Exception as e:
                print(f"[ERROR] Failed to init Sheets service: {e}")
        else:
            print("[WARN] Google Credentials or Sheet ID not found.")

    def fetch_metrics(self, range_name="Sheet1!A1:B5"):
        """Fetches metrics from a specific range."""
        if not self.service or not self.sheet_id:
            print("[WARN] Sheets service or Sheet ID missing. Returning empty list.")
            return []

        try:
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.sheet_id, range=range_name).execute()
            rows = result.get('values', [])
            
            metrics = []
            for row in rows:
                if len(row) >= 2:
                    metrics.append({
                        "metric": row[0],
                        "value": row[1],
                        "source": "Google Sheets"
                    })
            return metrics

        except Exception as e:
            print(f"[ERROR] Failed to fetch metrics: {e}")
            return []

def run():
    fetcher = AnalyticsFetcher()
    return fetcher.fetch_metrics()

if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
