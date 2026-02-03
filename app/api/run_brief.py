from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from app.core.database import get_db
from app.models.user import User, OAuthToken
from tools.navigation import generate_daily_brief
import traceback
import json

router = APIRouter()

def get_google_creds(user_id: int, db: Session):
    token = db.query(OAuthToken).filter(OAuthToken.user_id == user_id).first()
    if not token:
        return None
        
    # Reconstruct Credentials object
    # We need: token, refresh_token, token_uri, client_id, client_secret
    # Ideally we'd have these all in DB or Config. For now we assume we can build minimal
    
    creds_data = {
        "token": token.access_token,
        "refresh_token": token.refresh_token,
        "expiry":  None, # handled via refresh logic if needed, or raw string
        # IMPORTANT: Google lib expects more fields to auto-refresh
    }
    
    # We construct explicitly
    try:
        from tools.utils.config import Config
        import os
        
        # We need client config to allow refreshing
        # This is a bit hacky to read from env here but works
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        token_uri = "https://oauth2.googleapis.com/token"
        
        creds = Credentials(
            token=token.access_token,
            refresh_token=token.refresh_token,
            token_uri=token_uri,
            client_id=client_id,
            client_secret=client_secret,
            scopes=['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/calendar.readonly']
        )
        return creds
    except Exception as e:
        print(f"[AUTH ERROR] Failed to reconstruct creds: {e}")
        return None

@router.post("/run-brief")
async def run_brief(request: Request, db: Session = Depends(get_db)):
    """
    Triggers the Daily Executive Brief generation.
    Returns the generated JSON data.
    """
    try:
        user_id = request.session.get('user_id')
        creds = None
        if user_id:
            print(f"[API] Fetching credentials for User ID {user_id}...")
            creds = get_google_creds(user_id, db)
            if not creds:
                print("[WARN] User found but no Google Token in DB.")
        else:
            print("[WARN] No active session. Attempting legacy local mode (will fail on Render).")

        # Call the existing logic directly
        # navigation.py's generate_daily_brief returns the 'daily_brief' dict
        print("[API] Triggering Daily Brief generation...")
        brief, slack_payload = generate_daily_brief(creds=creds)
        return brief
    except Exception as e:
        print(f"[API ERROR] {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
