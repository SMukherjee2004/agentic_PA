from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from starlette.requests import Request
from starlette.responses import JSONResponse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from sqlalchemy.orm import Session
from .config import settings
from .db import get_db, Base, engine
from .models import UserToken
import json
import os

router = APIRouter()

# Ensure DB tables exist
Base.metadata.create_all(bind=engine)

SCOPES = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid',
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/documents',
    'https://www.googleapis.com/auth/gmail.modify'
]


def get_flow():
    return Flow(
        client_type='web',
        client_config={
            'web': {
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'redirect_uris': [settings.GOOGLE_REDIRECT_URI],
                'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
                'token_uri': 'https://oauth2.googleapis.com/token'
            }
        },
        scopes=SCOPES,
        redirect_uri=settings.GOOGLE_REDIRECT_URI,
    )


@router.get('/google')
async def google_login_alias():
    return await google_login()


@router.get('/google/login')
async def google_login():
    flow = get_flow()
    auth_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return JSONResponse({"auth_url": auth_url, "state": state})


@router.get('/google/callback')
async def google_callback(request: Request, db: Session = Depends(get_db)):
    state = request.query_params.get('state')
    code = request.query_params.get('code')
    if not code:
        raise HTTPException(status_code=400, detail='Missing code')
    flow = get_flow()
    flow.fetch_token(code=code)
    credentials = flow.credentials

    # Get user email
    oauth2 = build('oauth2', 'v2', credentials=credentials)
    user_info = oauth2.userinfo().get().execute()
    email = user_info.get('email')

    # Store tokens
    token = db.query(UserToken).filter_by(email=email).first()
    if not token:
        token = UserToken(email=email, access_token=credentials.token,
                          refresh_token=credentials.refresh_token,
                          token_uri=credentials.token_uri,
                          client_id=credentials.client_id,
                          client_secret=credentials.client_secret,
                          scopes=' '.join(credentials.scopes) if credentials.scopes else None)
        db.add(token)
    else:
        token.access_token = credentials.token
        token.refresh_token = credentials.refresh_token or token.refresh_token
        token.token_uri = credentials.token_uri
        token.client_id = credentials.client_id
        token.client_secret = credentials.client_secret
        token.scopes = ' '.join(credentials.scopes) if credentials.scopes else token.scopes
    db.commit()

    # Redirect to frontend with email
    redirect = f"{settings.FRONTEND_URL}/?email={email}"
    return RedirectResponse(url=redirect)
