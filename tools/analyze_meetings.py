import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.fetch_meeting_content import MeetingContentFetcher

class MeetingAnalyzer:
    def __init__(self):
        self.fetcher = MeetingContentFetcher()

    def extract_text(self, block):
        """Helper to extract plain text from a block."""
        b_type = block.get("type")
        if not b_type or b_type not in block:
            return ""
        
        rich_text = block[b_type].get("rich_text", [])
        return "".join([t.get("plain_text", "") for t in rich_text])

    def analyze_meeting(self, meeting_id, title="Untitled", date="Unknown"):
        print(f"Analyzing meeting: {title}...")
        blocks = self.fetcher.fetch_blocks(meeting_id)
        
        analysis = {
            "meeting_id": meeting_id,
            "title": title,
            "date": date,  # In a full flow, this comes from the Page properties
            "analysis": {
                "summary": "Auto-generated analysis.", # Placeholder for LLM
                "decisions": [],
                "action_items": [],
                "keywords": []
            }
        }

        # Parsing State
        in_decision_section = False
        
        for block in blocks:
            b_type = block.get("type")
            text = self.extract_text(block)
            
            # 1. Action Items (To-Do blocks)
            # These are captured regardless of where they are in the doc
            if b_type == "to_do":
                is_checked = block["to_do"].get("checked", False)
                status = "Done" if is_checked else "Open"
                analysis["analysis"]["action_items"].append({
                    "task": text,
                    "owner": "Unassigned", # Owner needs extraction from mentions or properties
                    "status": status
                })
                continue

            # 2. Section Detection (Headers)
            if "heading" in b_type:
                lower_text = text.lower()
                if "decision" in lower_text:
                    in_decision_section = True
                else:
                    in_decision_section = False
                continue

            # 3. Decision Extraction
            # If we are under a "Decisions" header, capture bullets
            if in_decision_section and b_type == "bulleted_list_item":
                if text.strip():
                    analysis["analysis"]["decisions"].append(text)

        return analysis

def run():
    analyzer = MeetingAnalyzer()
    # For testing, grab the most recent meeting
    page_id, title = analyzer.fetcher.get_recent_meeting_id()
    
    if page_id:
        result = analyzer.analyze_meeting(page_id, title=title)
        return result
    else:
        return {"error": "No meetings found"}

if __name__ == "__main__":
    result = run()
    print("\n--- ANALYSIS RESULT ---")
    print(json.dumps(result, indent=2))
