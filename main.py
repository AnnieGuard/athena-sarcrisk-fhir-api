from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import requests
import os
from typing import List, Optional
from urllib.parse import urlencode

# OAuth2 configuration
ATHENA_API_BASE_URL = "https://api.athenahealth.com"
ATHENA_CLIENT_ID = os.getenv("ATHENA_CLIENT_ID", "your-client-id-here")
ATHENA_CLIENT_SECRET = os.getenv("ATHENA_CLIENT_SECRET", 
"your-client-secret-here")
ATHENA_REDIRECT_URI = os.getenv("ATHENA_REDIRECT_URI", 
"https://athena-sarcrisk-fhir-api.ashystone-7ad37a18.eastus.azurecontainerapps.io/callback")
ATHENA_TOKEN_URL = f"{ATHENA_API_BASE_URL}/oauth2/token"

# FastAPI app initialization
app = FastAPI()

# Add this callback route
@app.get("/callback")
async def callback(code: str = None, state: str = None):
    """
    OAuth2 callback endpoint for athenahealth authentication
    
    This endpoint receives the authorization code from athenahealth after 
user authentication
    and exchanges it for an access token.
    """
    if not code:
        return {"error": "Authorization code missing"}
    
    try:
        # Exchange the authorization code for an access token
        token_request_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": ATHENA_REDIRECT_URI,
            "client_id": ATHENA_CLIENT_ID,
            "client_secret": ATHENA_CLIENT_SECRET
        }
        
        token_response = requests.post(
            ATHENA_TOKEN_URL,
            data=token_request_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if token_response.status_code != 200:
            return {
                "error": "Failed to obtain access token",
                "details": token_response.text,
                "status_code": token_response.status_code
            }
            
        # Successfully obtained the token
        token_data = token_response.json()
        
        # For debugging/development, return the token info
        # In production, you should store this securely and redirect to 
your app
        return {
            "message": "Authentication successful",
            "access_token": token_data.get("access_token"),
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "refresh_token": token_data.get("refresh_token", "Not 
provided")
        }
        
    except Exception as e:
        return {"error": f"Authentication failed: {str(e)}"}
