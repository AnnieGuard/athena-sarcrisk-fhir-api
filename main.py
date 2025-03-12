from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
import requests
import os
from typing import List, Optional

# OAuth2 configuration
ATHENA_API_BASE_URL = "https://api.athenahealth.com"
ATHENA_CLIENT_ID = os.getenv("ATHENA_CLIENT_ID")  # Replace with your 
client ID
ATHENA_CLIENT_SECRET = os.getenv("ATHENA_CLIENT_SECRET")  # Replace with 
your client secret
ATHENA_REDIRECT_URI = os.getenv("ATHENA_REDIRECT_URI")  # Replace with 
your redirect URI
ATHENA_TOKEN_URL = f"{ATHENA_API_BASE_URL}/oauth/token"

# FastAPI app initialization
app = FastAPI()

# OAuth2 dependency
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models
class RiskScoreResponse:
    patient_id: str
    sarcoma_risk_score: float
    recommended_action: str


class AthenaUser:
    id: str
    name: str
    email: str


@app.get("/auth/callback")
async def auth_callback(code: str):
    """
    OAuth2 callback handler that receives the authorization code, 
exchanges it for an access token,
    and returns the access token.
    """
    try:
        # Exchange authorization code for access token
        response = requests.post(
            ATHENA_TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": ATHENA_REDIRECT_URI,
                "client_id": ATHENA_CLIENT_ID,
                "client_secret": ATHENA_CLIENT_SECRET,
            },
        )
        response_data = response.json()
        if response.status_code == 200:
            access_token = response_data["access_token"]
            return {"access_token": access_token}
        else:
            raise HTTPException(status_code=400, detail="Failed to 
exchange code for access token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during token 
exchange: {str(e)}")


@app.get("/api/sarc-risks/{patient_id}", response_model=RiskScoreResponse)
async def get_sarc_risk(patient_id: str, token: str = 
Depends(oauth2_scheme)):
    """
    Endpoint to calculate sarcoma risk score for a patient by interacting 
with AthenaHealth API
    to retrieve patient data and return a recommended action based on the 
risk score.
    """
    # Step 1: Use the token to authenticate with AthenaHealth API and 
fetch patient data
    user = authenticate_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Fetch patient data from AthenaHealth
    patient_data = await get_patient_data(patient_id, token)
    if not patient_data:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Step 2: Calculate the sarcoma risk score based on biomarkers
    sarcoma_risk_score = calculate_sarcoma_risk(patient_data)

    # Step 3: Determine the recommended action based on the risk score
    recommended_action = "Monitor closely"
    if sarcoma_risk_score > 0.8:
        recommended_action = "Immediate biopsy recommended"
    elif sarcoma_risk_score > 0.5:
        recommended_action = "Further imaging required"

    # Return the risk score response
    return RiskScoreResponse(
        patient_id=patient_id,
        sarcoma_risk_score=sarcoma_risk_score,
        recommended_action=recommended_action
    )


def authenticate_user(token: str) -> Optional[AthenaUser]:
    """
    Function to authenticate the user using the provided OAuth2 token.
    If successful, returns user info; otherwise, raises an exception.
    """
    try:
        # Authenticate user using the OAuth2 token
        response = requests.get(
            f"{ATHENA_API_BASE_URL}/api/1/athenahealth/v1/userinfo",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            return AthenaUser(**response.json())  # Assuming Athena 
returns user info in JSON format
        else:
            raise HTTPException(status_code=401, detail="Unauthorized")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication 
failed: {str(e)}")


async def get_patient_data(patient_id: str, token: str) -> Optional[dict]:
    """
    Function to fetch patient data from AthenaHealth's API.
    """
    try:
        response = requests.get(
            
f"{ATHENA_API_BASE_URL}/api/1/athenahealth/v1/patients/{patient_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=404, detail="Patient data not 
found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch 
patient data: {str(e)}")


def calculate_sarcoma_risk(patient_data: dict) -> float:
    """
    Placeholder function to calculate sarcoma risk score based on patient 
data.
    Here you can add your logic to calculate the risk score from 
biomarkers.
    """
    # Example: Assuming patient_data contains biomarkers like tumor size, 
weight, age, etc.
    # For the sake of simplicity, we will return a random risk score.
    # Replace this with actual calculation logic.
    return 0.7  # Random placeholder risk score


# Run the app (usually this is done in your CLI: `uvicorn main:app 
--reload`)

