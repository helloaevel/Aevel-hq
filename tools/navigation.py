import json
import os
import sys
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.fetch_notion import NotionFetcher
from tools.fetch_gmail import GmailFetcher
from tools.fetch_analytics import AnalyticsFetcher

from tools.stylize import BriefStylizer
from tools.rank_tasks import TaskRanker
from tools.analyze_meetings import MeetingAnalyzer
from tools.analyze_schedule import ScheduleAnalyzer

def generate_daily_brief(creds=None):
    print(f"--- AEVEL HQ: Generating Daily Executive Brief [{datetime.now().isoformat()}] ---")
    
    # 1. Initialize Fetchers
    # notion = NotionFetcher() # Deprecated for Tasks, but used for legacy meetings? 
    # Actually NotionFetcher serves legacy meetings. TaskRanker serves tasks.
    # To keep it clean, we instantiate what we need.
    notion_legacy = NotionFetcher() 
    gmail = GmailFetcher(creds=creds)
    analytics = AnalyticsFetcher()
    
    ranker = TaskRanker()
    analyzer = MeetingAnalyzer()
    scheduler = ScheduleAnalyzer(creds=creds)
    
    # 2. Fetch Data (Layer 3)
    print("Fetching & Ranking Tasks...")
    tasks = ranker.fetch_ranked_tasks(limit=5)
    
    # Legacy: Notion Meetings (Notes)
    meetings = notion_legacy.fetch_recent_meetings()
    
    meeting_insights = []
    if meetings:
        print(f"Analyzing {len(meetings)} recent meetings...")
        for m in meetings:
            insight = analyzer.analyze_meeting(m["id"], title=m["title"], date=m["date"])
            meeting_insights.append(insight)

    # New: Calendar Schedule
    print("Analyzing Schedule...")
    schedule_analysis = scheduler.analyze_schedule()
    
    print("Fetching Emails...")
    emails = gmail.fetch_flagged_emails()
    
    print("Fetching Analytics...")
    metrics = analytics.fetch_metrics()
    
    # 3. Aggregation & Synthesis (Layer 2)
    daily_brief = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "task_count": len(tasks),
            "meeting_count": schedule_analysis["analysis"]["total_events"], # Use Calendar count
            "urgent_email_count": len(emails)
        },
        "priorities": tasks,
        "meeting_summaries": meetings, # Keeping legacy for reference, but UI will prefer Schedule
        "meeting_insights": meeting_insights,
        "schedule": schedule_analysis, # New payload
        "flagged_emails": emails,
        "metrics": metrics
    }
    
    # 4. Stylize (Phase S)
    print("Stylizing Outputs...")
    slack_payload = BriefStylizer.to_slack_blocks(daily_brief)
    email_html = BriefStylizer.to_email_html(daily_brief)

    # 5. Output
    tmp_dir = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    os.makedirs(tmp_dir, exist_ok=True)
    
    # Save Raw
    with open(os.path.join(tmp_dir, "daily_brief.json"), "w") as f:
        json.dump(daily_brief, f, indent=2)

    # Save Slack
    with open(os.path.join(tmp_dir, "slack_payload.json"), "w") as f:
        json.dump(slack_payload, f, indent=2)

    # Save Email
    with open(os.path.join(tmp_dir, "email_body.html"), "w", encoding='utf-8') as f:
        f.write(email_html)
        
    print(f"[SUCCESS] Brief generated in .tmp/:")
    print(f" - raw: daily_brief.json")
    print(f" - slack: slack_payload.json")
    print(f" - email: email_body.html")
    
    return daily_brief, slack_payload

def send_to_slack(payload):
    url = Config.SLACK_WEBHOOK_URL
    if not url or "placeholder" in url:
        print("[ERROR] Slack Webhook URL not configured. Cannot send.")
        return

    try:
        import requests
        print(f"Sending to Slack ({url})...")
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("[SUCCESS] Posted to Slack.")
        else:
            print(f"[ERROR] Slack API returned {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] Failed to send to Slack: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate and optionally send Aevel HQ Daily Brief.")
    parser.add_argument("--send", action="store_true", help="Send the brief to configured channels (Slack).")
    args = parser.parse_args()

    brief, slack_data = generate_daily_brief()

    if args.send:
        print("--- SENDING MODE ---")
        send_to_slack(slack_data)
    else:
        print("--- DRY RUN (Use --send to post) ---")
