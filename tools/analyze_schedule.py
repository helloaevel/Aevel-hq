import os
import sys
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.fetch_calendar import CalendarFetcher
from tools.fetch_notion import NotionFetcher

class ScheduleAnalyzer:
    def __init__(self, creds=None):
        self.cal_fetcher = CalendarFetcher(creds=creds)
        self.notion_fetcher = NotionFetcher()

    def _parse_iso(self, iso_str):
        # Handle 'Z' or offset if needed, basic implementation
        try:
            return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        except:
            return None

    def analyze_schedule(self):
        print("Analyzing Schedule...")
        events = self.cal_fetcher.fetch_upcoming_events(limit=10)
        
        # 1. Conflict Detection
        conflicts = []
        for i in range(len(events)):
            for j in range(i + 1, len(events)):
                ev1 = events[i]
                ev2 = events[j]
                
                # Parse ISO strings to datetime objects
                start1 = self._parse_iso(ev1['start'])
                end1 = self._parse_iso(ev1['end'])
                start2 = self._parse_iso(ev2['start'])
                end2 = self._parse_iso(ev2['end'])
                
                if not (start1 and end1 and start2 and end2):
                    continue

                # Overlap logic: StartA < EndB AND StartB < EndA
                if start1 < end2 and start2 < end1:
                    conflicts.append({
                        "event_a": ev1["summary"],
                        "event_b": ev2["summary"],
                        "reason": f"Overlap: {ev1['summary']} overlaps with {ev2['summary']}"
                    })

        # 2. Priority Tagging
        high_priority = []
        keywords = ["strategy", "client", "board", "urgent", "presentation"]
        formatted_events = []

        for e in events:
            # Re-structure for output
            item = {
                "event_id": e["event_id"],
                "summary": e["summary"],
                "start": e["start"],
                "end": e["end"],
                "link": e["link"],
                "tags": []
            }
            
            # Check keywords
            summary_lower = e["summary"].lower()
            if any(k in summary_lower for k in keywords):
                high_priority.append(e["event_id"])
                item["tags"].append("High Priority")
                
            formatted_events.append(item)

        # 3. Cross-Reference (Link to Notion)
        # We need a way to search Notion for pages with similar titles
        # Current NotionFetcher fetches "recent meetings", maybe we can search?
        # For MVP, we will just list the raw events formatted.
        
        return {
            "events": formatted_events,
            "analysis": {
                "conflicts": conflicts, # Placeholder until fetcher improves
                "high_priority_ids": high_priority,
                "total_events": len(events)
            }
        }

def run():
    analyzer = ScheduleAnalyzer()
    return analyzer.analyze_schedule()

if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
