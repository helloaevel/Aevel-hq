import os
import sys
from notion_client import Client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

def list_accessible_objects():
    print("--- NOTION DEBUGGER ---")
    
    if not Config.NOTION_API_KEY:
        print("[ERROR] No API Key found.")
        return

    client = Client(auth=Config.NOTION_API_KEY)
    
    try:
        # Search for *everything* this bot can see
        print("Searching for all accessible pages and databases...")
        results = client.search(page_size=100).get("results", [])
        
        if not results:
            print("[INFO] The bot cannot see ANY pages or databases.")
            print("       This means no connections have been made yet, or the integration was added to a page that has no children.")
        else:
            print(f"[SUCCESS] Found {len(results)} accessible objects:\n")
            for item in results:
                obj_type = item["object"]
                id = item["id"]
                
                title = "Untitled"
                if obj_type == "database":
                    title_list = item.get("title", [])
                    if title_list:
                         title = title_list[0].get("plain_text", "Untitled")
                elif obj_type == "page":
                    # Title property name varies, usually "Name" or "title"
                    props = item.get("properties", {})
                    # Try to find a title property
                    for key, val in props.items():
                        if val["id"] == "title":
                            title_list = val.get("title", [])
                            if title_list:
                                title = title_list[0].get("plain_text")
                            break
                            
                print(f"[{obj_type.upper()}] {title}")
                print(f"  ID: {id}")
                print(f"  URL: {item['url']}")
                print("-" * 40)

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")

if __name__ == "__main__":
    list_accessible_objects()
