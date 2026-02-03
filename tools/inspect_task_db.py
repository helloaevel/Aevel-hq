import os
import sys
import json
from notion_client import Client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

def inspect_db():
    print(f"--- INSPECTING TASK DB ({Config.NOTION_TASK_DB_ID}) ---")
    
    if not Config.NOTION_API_KEY:
        print("[ERROR] No API Key found.")
        return

    client = Client(auth=Config.NOTION_API_KEY)
    
    try:
        db = client.databases.retrieve(database_id=Config.NOTION_TASK_DB_ID)
        props = db.get("properties", {})
        
        print(f"[SUCCESS] Database: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        print(f"Found {len(props)} properties:\n")
        
        needed = ["Status", "Priority", "Due Date", "Date"]
        found_map = {}

        for name, details in props.items():
            prop_type = details["type"]
            options = []
            if prop_type == "select":
                options = [opt["name"] for opt in details["select"]["options"]]
            elif prop_type == "status":
                options = [opt["name"] for opt in details["status"]["options"]]
            
            print(f"- {name} ({prop_type}) {options if options else ''}")
            
            # Check for needed fields (case-insensitive fuzzy match)
            for n in needed:
                if n.lower() in name.lower():
                    found_map[n] = {"name": name, "type": prop_type, "options": options}

        print("\n--- ANALYSIS ---")
        for n in needed:
            if n in found_map:
                print(f"✅ Found '{n}': {found_map[n]}")
            else:
                print(f"❌ Missing '{n}'")
                
        return found_map

    except Exception as e:
        print(f"[ERROR] Failed to retrieve database: {e}")
        return {}

if __name__ == "__main__":
    inspect_db()
