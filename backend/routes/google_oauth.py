"""
Google OAuth Routes
Handle OAuth2 flow for Google Search Console and Analytics
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging
from urllib.parse import urlencode

from database import get_db
from auth import get_current_user, require_superadmin
from models import User

router = APIRouter(prefix="/oauth/google", tags=["Google OAuth"])
logger = logging.getLogger(__name__)

# Google OAuth Configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("FRONTEND_URL", "http://localhost:3000") + "/oauth/callback/google"

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"

# Scopes needed
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",  # Search Console
    "https://www.googleapis.com/auth/analytics.readonly",   # Analytics
    "openid",
    "email",
    "profile"
]


@router.get("/authorize")
async def google_authorize(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Initiate Google OAuth2 flow
    Redirect user to Google consent screen
    """
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured. Please add GOOGLE_CLIENT_ID to environment variables."
        )
    
    # Build authorization URL
    params = {
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(SCOPES),
        "access_type": "offline",  # Get refresh token
        "prompt": "consent",  # Force consent screen
        "state": current_user.id  # Pass user ID for verification
    }
    
    auth_url = f"{GOOGLE_AUTH_URL}?{urlencode(params)}"
    
    logger.info(f"Redirecting user {current_user.email} to Google OAuth")
    
    return {
        "authorization_url": auth_url,
        "message": "Redirect user to this URL to authorize Google access"
    }


@router.post("/callback")
async def google_callback(
    code: str,
    state: str,  # user_id
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Handle OAuth callback from Google
    Exchange authorization code for access token
    """
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=500,
            detail="Google OAuth not configured"
        )
    
    # TODO: Exchange code for tokens
    # TODO: Store tokens in database (encrypted)
    # TODO: Store in EnvironmentKey or new GoogleOAuthToken model
    
    return {
        "message": "Google OAuth callback received",
        "status": "OAuth flow implementation pending",
        "note": "Tokens would be stored here for Search Console and Analytics access"
    }


@router.get("/status")
async def google_oauth_status(
    current_user: User = Depends(require_superadmin),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if Google OAuth is configured and tokens are available
    """
    has_client_id = bool(GOOGLE_CLIENT_ID)
    has_client_secret = bool(GOOGLE_CLIENT_SECRET)
    
    # TODO: Check if tokens exist in database
    has_tokens = False
    
    return {
        "configured": has_client_id and has_client_secret,
        "client_id_set": has_client_id,
        "client_secret_set": has_client_secret,
        "tokens_available": has_tokens,
        "scopes_requested": SCOPES,
        "status": "ready_for_oauth" if (has_client_id and has_client_secret) else "missing_credentials"
    }
