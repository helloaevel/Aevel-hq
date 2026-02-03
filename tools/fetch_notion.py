import os
import sys
from notion_client import Client
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

class NotionFetcher:
    def __init__(self):
        self.api_key = Config.NOTION_API_KEY
        if not self.api_key or "placeholder" in self.api_key:
            print("[ERROR] Notion API Key not set.")
            self.client = None
        else:
            self.client = Client(auth=self.api_key)

    def fetch_high_priority_tasks(self, limit=5):
        """Fetches high priority tasks that are not done."""
        if not self.client or not Config.NOTION_TASK_DB_ID:
            print("[WARN] Notion Client or Task DB ID missing. Returning empty list.")
            return []

        try:
            response = self.client.databases.query(
                database_id=Config.NOTION_TASK_DB_ID,
                filter={
                    "and": [
                        {
                            "property": "Status",
                            "status": {
                                "does_not_equal": "Done"
                            }
                        },
                        {
                            "property": "Priority",
                            "select": {
                                "equals": "High"
                            }
                        }
                    ]
                },
                page_size=limit
            )
            
            tasks = []
            for page in response.get("results", []):
                props = page.get("properties", {})
                title_list = props.get("Name", {}).get("title", [])
                title = title_list[0].get("plain_text") if title_list else "Untitled"
                
                tasks.append({
                    "id": page["id"],
                    "title": title,
                    "status": props.get("Status", {}).get("status", {}).get("name", "Unknown"),
                    "url": page["url"]
                })
            return tasks

        except Exception as e:
            print(f"[ERROR] Failed to fetch tasks: {e}")
            return []

    def fetch_recent_meetings(self):
        """Fetches meetings modified in the last 24 hours."""
        if not self.client or not Config.NOTION_MEETING_DB_ID:
            print("[WARN] Notion Client or Meeting DB ID missing. Returning empty list.")
            return []

        yesterday = (datetime.now() - timedelta(days=1)).isoformat()

        try:
            response = self.client.databases.query(
                database_id=Config.NOTION_MEETING_DB_ID,
                filter={
                    "timestamp": "last_edited_time",
                    "last_edited_time": {
                        "on_or_after": yesterday
                    }
                },
                page_size=5
            )

            meetings = []
            for page in response.get("results", []):
                props = page.get("properties", {})
                title_list = props.get("Name", {}).get("title", [])
                title = title_list[0].get("plain_text") if title_list else "Untitled"
                
                meetings.append({
                    "id": page["id"],
                    "title": title,
                    "date": props.get("Date", {}).get("date", {}).get("start", "No Date"),
                    "url": page["url"]
                })
            return meetings

        except Exception as e:
            print(f"[ERROR] Failed to fetch meetings: {e}")
            return []

def run():
    fetcher = NotionFetcher()
    tasks = fetcher.fetch_high_priority_tasks()
    meetings = fetcher.fetch_recent_meetings()
    return {"tasks": tasks, "meetings": meetings}

if __name__ == "__main__":
    import json
    print(json.dumps(run(), indent=2))
