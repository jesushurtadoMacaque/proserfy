from typing import Dict
from fastapi import HTTPException, logger, status
from config.social import GOOGLE_AUTH_ENDPOINT, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URL, GOOGLE_RESPONSE_TYPE, GOOGLE_SCOPE, GOOGLE_TOKEN_URL
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import requests

def get_google_auth_url() -> str:
    print("GOOGLE_REDIRECT_URL")
    print(GOOGLE_REDIRECT_URL)
    return (
        f"{GOOGLE_AUTH_ENDPOINT}?response_type={GOOGLE_RESPONSE_TYPE}&client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URL}&scope={GOOGLE_SCOPE}&prompt=select_account"
    )

def fetch_google_tokens(code: str) -> Dict:
    token_data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URL,
        "grant_type": "authorization_code"
    }
    try:
        token_response = requests.post(GOOGLE_TOKEN_URL, data=token_data)
        token_response.raise_for_status()
        return token_response.json()
    except requests.RequestException as e:
        logger.error(f"Error requesting tokens: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error requesting tokens from Google")

def verify_google_id_token(id_token_str: str) -> Dict:
    try:
        return id_token.verify_oauth2_token(id_token_str, google_requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Google token")
