import os
import sys
import json
import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from tools.utils.config import Config
# Re-load config to ensure ENV vars are fresh
load_dotenv()

def run_validation():
    report = {
        "env_status": "valid",
        "missing_keys": [],
        "connection_status": {},
        "auto_fixes": [],
        "next_steps": []
    }
    
    print("--- AUTOMATED SYSTEM VALIDATION ---")
    
    # 1. Environment Variable Check
    required_vars = [
        "NOTION_API_KEY", "NOTION_TASK_DB_ID", "NOTION_MEETING_DB_ID",
        "GOOGLE_SHEET_ID" # Client secret is file based
    ]
    
    # Check what is loaded
    for var in required_vars:
        val = os.getenv(var)
        # Also check Config class
        config_val = getattr(Config, var, None)
        
        if not val and not config_val:
             report["missing_keys"].append(var)
        elif "placeholder" in str(val):
             report["missing_keys"].append(f"{var} (is placeholder)")

    # Check Files
    if not os.path.exists("client_secret.json"):
        report["missing_keys"].append("client_secret.json")
    else:
        # Check if placeholder
        try:
            with open("client_secret.json") as f:
                content = f.read()
                if "PLACEHOLDER" in content:
                    report["missing_keys"].append("client_secret.json (contains PLACEHOLDER)")
        except:
             pass

    if report["missing_keys"]:
        report["env_status"] = "invalid"

    # 2. Connection Checks
    
    # Notion
    report["connection_status"]["Notion"] = "Skipped"
    if "NOTION_API_KEY" not in report["missing_keys"]:
        try:
            from tools.fetch_notion import NotionFetcher
            nf = NotionFetcher()
            if nf.client:
                # Simple user list check for auth
                nf.client.users.list()
                report["connection_status"]["Notion"] = "Connected"
            else:
                report["connection_status"]["Notion"] = "Failed (Client Init)"
        except Exception as e:
             report["connection_status"]["Notion"] = f"Failed: {str(e)}"

    # Google Sheets
    report["connection_status"]["Sheets"] = "Skipped"
    if Config.GOOGLE_CREDS_PATH and os.path.exists(Config.GOOGLE_CREDS_PATH):
        try:
            from tools.fetch_analytics import AnalyticsFetcher
            af = AnalyticsFetcher()
            if af.service:
                report["connection_status"]["Sheets"] = "Connected (Service Account)"
            else:
                 report["connection_status"]["Sheets"] = "Failed (Service Init)"
        except Exception as e:
            report["connection_status"]["Sheets"] = f"Error: {str(e)}"
    else:
        report["connection_status"]["Sheets"] = "Missing credentials.json"

    # Gmail (OAuth)
    report["connection_status"]["Gmail"] = "Skipped"
    if os.path.exists("client_secret.json"):
        if os.path.exists("token.json"):
             report["connection_status"]["Gmail"] = "Token Found (Assuming Valid)"
        else:
             report["connection_status"]["Gmail"] = "Ready to Auth (token.json missing)"
             report["next_steps"].append("Run `python tools/fetch_gmail.py` to perform initial OAuth Login.")

    # Slack
    if Config.SLACK_WEBHOOK_URL and "placeholder" not in Config.SLACK_WEBHOOK_URL:
        report["connection_status"]["Slack"] = "Configured"
    else:
        report["connection_status"]["Slack"] = "Missing Webhook"


    # 3. Output
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    run_validation()
