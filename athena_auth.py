import requests
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from typing import Dict

# Athena API credentials (you should set these as environment variables 
for security)
CLIENT_ID = os.getenv("ATHENA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ATHENA_CLIENT_SECRET")
AUTH_URL = "https://athenahealth.com/oauth2/token"
REDIRECT_URI = "https://your-app-url.com/callback"  # Replace with your 
actual callback URL

# Use FastAPI security for authentication
security = HTTPBearer()

class AthenaAuth:
    def __init__(self):
        self.client_id = CLIENT_ID
        self.client_secret = CLIENT_SECRET
        self.auth_url = AUTH_URL
        self.redirect_uri = REDIRECT_URI

    def get_auth_url(self) -> str:
        """Generate the OAuth2 authorization URL"""
        auth_url = (
            f"{self.auth_url}?client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}&response_type=code"
        )
        return auth_url

    def get_access_token(self, code: str) -> Dict[str, str]:
        """Exchange authorization code for access token"""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.auth_url, data=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
detail="Failed to get access token")

        return response.json()

    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using the refresh token"""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.auth_url, data=payload)

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, 
detail="Failed to refresh access token")

        return response.json()

def get_oauth_token(credentials: HTTPAuthorizationCredentials = 
Depends(security)) -> Dict[str, str]:
    """Retrieve OAuth token from the header and return the token"""
    if credentials:
        return {"Authorization": f"Bearer {credentials.credentials}"}
    raise HTTPException(status_code=401, detail="Authentication 
credentials are missing")

# Example function to retrieve the access token after the user completes 
OAuth flow
async def oauth_callback(code: str):
    """Handle the OAuth callback and exchange code for access token"""
    athena_auth = AthenaAuth()
    access_token_data = athena_auth.get_access_token(code)
    return access_token_data


