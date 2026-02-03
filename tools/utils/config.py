import os
import sys
from dotenv import load_dotenv

# Load .env file
load_dotenv()

def get_env_var(name, required=True):
    val = os.getenv(name)
    if required and not val:
        print(f"[CRITICAL] Missing environment variable: {name}")
        print("Please check your .env file.")
        sys.exit(1)
    return val

class Config:
    NOTION_API_KEY = get_env_var("NOTION_API_KEY", required=False)
    NOTION_TASK_DB_ID = get_env_var("NOTION_TASK_DB_ID", required=False)
    NOTION_MEETING_DB_ID = get_env_var("NOTION_MEETING_DB_ID", required=False)
    
    SLACK_WEBHOOK_URL = get_env_var("SLACK_WEBHOOK_URL", required=False)
    
    GOOGLE_CREDS_PATH = get_env_var("GOOGLE_APPLICATION_CREDENTIALS", required=False)
    GOOGLE_CLIENT_SECRET_PATH = "client_secret.json" # Expected in root for OAuth flow
    GOOGLE_SHEET_ID = get_env_var("GOOGLE_SHEET_ID", required=False)
    GMAIL_SUBJECT = get_env_var("GMAIL_SUBJECT", required=False) # Email to impersonate if using domain-wide delegation

    @classmethod
    def validate(cls):
        missing = []
        if not cls.NOTION_API_KEY or "placeholder" in cls.NOTION_API_KEY:
            missing.append("NOTION_API_KEY")
        if not cls.SLACK_WEBHOOK_URL or "placeholder" in cls.SLACK_WEBHOOK_URL:
            missing.append("SLACK_WEBHOOK_URL")
        # Check if creds file exists if path is set
        if cls.GOOGLE_CREDS_PATH and not os.path.exists(cls.GOOGLE_CREDS_PATH):
             missing.append(f"GOOGLE_APPLICATION_CREDENTIALS file not found at: {cls.GOOGLE_CREDS_PATH}")
        
        return missing
