import os
import sys
import json
from notion_client import Client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

class MeetingContentFetcher:
    def __init__(self):
        self.api_key = Config.NOTION_API_KEY
        self.db_id = Config.NOTION_MEETING_DB_ID
        if not self.api_key:
            print("[ERROR] Notion API Key not set.")
            self.client = None
        else:
            self.client = Client(auth=self.api_key)

    def get_recent_meeting_id(self):
        """Finds the most recent meeting to test with."""
        if not self.client or not self.db_id:
            print("[ERROR] Client or DB ID missing.")
            return None
        
        try:
            response = self.client.databases.query(
                database_id=self.db_id,
                page_size=1
            )
            results = response.get("results", [])
            if results:
                page = results[0]
                props = page.get("properties", {})
                title_list = props.get("Name", {}).get("title", [])
                title = title_list[0].get("plain_text") if title_list else "Untitled"
                print(f"[INFO] Found recent meeting: '{title}' ({page['id']})")
                return page['id'], title
            else:
                print("[WARN] No meetings found in database.")
                return None, None
        except Exception as e:
            print(f"[ERROR] Failed to query database: {e}")
            return None, None

    def fetch_blocks(self, block_id):
        """Recursively fetches children blocks."""
        if not self.client:
            return []
        
        all_blocks = []
        try:
            response = self.client.blocks.children.list(block_id=block_id)
            results = response.get("results", [])
            all_blocks.extend(results)
            
            # Handle pagination if needed (basic implementation)
            while response.get("has_more"):
                response = self.client.blocks.children.list(
                    block_id=block_id, 
                    start_cursor=response["next_cursor"]
                )
                all_blocks.extend(response.get("results", []))
                
            return all_blocks
        except Exception as e:
            print(f"[ERROR] Failed to fetch blocks for {block_id}: {e}")
            return []

def run():
    fetcher = MeetingContentFetcher()
    page_id, title = fetcher.get_recent_meeting_id()
    
    if page_id:
        print(f"Fetching content for: {title}...")
        blocks = fetcher.fetch_blocks(page_id)
        
        # Simplified output for demonstration
        valid_content = []
        for b in blocks:
            b_type = b["type"]
            content = ""
            if "rich_text" in b[b_type]:
                text_list = b[b_type]["rich_text"]
                content = "".join([t["plain_text"] for t in text_list])
            
            valid_content.append(f"[{b_type}] {content}")
        
        return valid_content
    return []

if __name__ == "__main__":
    content = run()
    print("\n--- PAGE CONTENT PREVIEW ---")
    for line in content:
        print(line)
