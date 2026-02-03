import os
import sys
import json
from datetime import datetime, timedelta
from notion_client import Client

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config

class TaskRanker:
    def __init__(self):
        self.api_key = Config.NOTION_API_KEY
        self.db_id = Config.NOTION_TASK_DB_ID
        if self.api_key:
            self.client = Client(auth=self.api_key)
        else:
            self.client = None

    def _infer_priority(self, title):
        """Option B: Infer priority from keywords."""
        t_lower = title.lower()
        if any(w in t_lower for w in ["urgent", "critical", "blocking", "asap", "high"]):
            return "High"
        if any(w in t_lower for w in ["low", "someday", "idea", "maybe"]):
            return "Low"
        return "Medium"

    def _calculate_score(self, task):
        # Base Score
        score = 50
        
        # 1. Priority Modifier
        priority = task.get("priority", "Medium")
        if priority == "High": score += 30
        elif priority == "Medium": score += 10
        elif priority == "Low": score -= 10
        
        # 2. Status Modifier
        # Encouraging "In progress" to get finished
        status = task.get("status", "Not started")
        if status == "In progress": score += 15
        
        # 3. Urgency Modifier (Due Date)
        due_date_str = task.get("due_date")
        if due_date_str:
            try:
                due = datetime.fromisoformat(due_date_str)
                now = datetime.now()
                delta = (due - now).days
                
                if delta < 0: score += 40 # Overdue
                elif delta == 0: score += 20 # Due Today
                elif delta == 1: score += 10 # Due Tomorrow
                elif delta < 7: score += 5   # Due this week
            except:
                pass
                
        return score

    def fetch_ranked_tasks(self, limit=5):
        if not self.client:
            return []

        print("Fetching and Ranking Tasks...")
        
        # Fetch generic "Not Done" tasks
        # We filter logic in python for simplicity of "Done" check if status naming varies
        try:
            results = self.client.databases.query(
                database_id=self.db_id,
                filter={
                    "property": "Status",
                    "status": {
                        "does_not_equal": "Done"
                    }
                }
            ).get("results", [])
            
            ranked_tasks = []
            for page in results:
                props = page["properties"]
                
                # Extract Title (property: 'Milestone')
                title_list = props.get("Milestone", {}).get("title", [])
                title = title_list[0]["plain_text"] if title_list else "Untitled"
                
                # Extract Status
                status = "Unknown"
                if "Status" in props:
                    status = props["Status"]["status"]["name"]
                
                # Extract Due Date (property: 'Due date')
                due_date = None
                if "Due date" in props and props["Due date"]["date"]:
                    due_date = props["Due date"]["date"]["start"]
                
                # Extract Priority (property: 'Priority')
                priority = "Medium"
                if "Priority" in props and props["Priority"]["select"]:
                    priority = props["Priority"]["select"]["name"]
                
                task_obj = {
                    "task_id": page["id"],
                    "title": title,
                    "status": status,
                    "priority": priority,
                    "due_date": due_date,
                    "url": page["url"]
                }
                
                # Calc Score
                task_obj["score"] = self._calculate_score(task_obj)
                ranked_tasks.append(task_obj)
                
            # Sort by Score Descending
            ranked_tasks.sort(key=lambda x: x["score"], reverse=True)
            
            return ranked_tasks[:limit]

        except Exception as e:
            print(f"[ERROR] Ranking failed: {e}")
            return []

def run():
    ranker = TaskRanker()
    return ranker.fetch_ranked_tasks()

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
