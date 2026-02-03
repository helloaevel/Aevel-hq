import os
from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, OAuthToken
from tools.utils.config import Config

router = APIRouter()

oauth = OAuth()

# Register Google OAuth
# Note: We expect GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in env
oauth.register(
    name='google',
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/calendar.readonly https://www.googleapis.com/auth/gmail.readonly'
    }
)

@router.get("/login")
async def login(request: Request):
    """Redirects user to Google Login."""
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth", name="auth_callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    """Handles Google Callback, creates user, stores token."""
    try:
        token = await oauth.google.authorize_access_token(request)
        user_info = token.get('userinfo')
        
        if not user_info:
             raise HTTPException(status_code=400, detail="Failed to retrieve user info")

        # Check if user exists
        user = db.query(User).filter(User.email == user_info['email']).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_info['email'],
                name=user_info.get('name'),
                avatar_url=user_info.get('picture')
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update info if changed
            user.name = user_info.get('name')
            user.avatar_url = user_info.get('picture')
            db.commit()

        # Update/Create Token
        # We store the access token to use for API calls later
        oauth_token = db.query(OAuthToken).filter(OAuthToken.user_id == user.id).first()
        if not oauth_token:
            oauth_token = OAuthToken(user_id=user.id)
            db.add(oauth_token)
        
        oauth_token.access_token = token.get('access_token')
        oauth_token.refresh_token = token.get('refresh_token')
        oauth_token.expires_at = token.get('expires_at')
        db.commit()

        # Set Session
        request.session['user_id'] = user.id
        
        return RedirectResponse(url="/")
        
    except Exception as e:
        print(f"Auth Error: {e}")
        return RedirectResponse(url="/?error=auth_failed")

@router.get("/logout")
async def logout(request: Request):
    request.session.pop('user_id', None)
    return RedirectResponse(url="/")

@router.get("/me")
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    user = db.query(User).filter(User.id == user_id).first()
    return user
