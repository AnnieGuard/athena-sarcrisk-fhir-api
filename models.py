from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Define FHIR-compliant models (as a starting point for the data you will 
interact with)

# Basic Patient Model
class Patient(BaseModel):
    id: str
    resourceType: str = "Patient"
    identifier: List[dict] = Field(..., description="A list of identifiers 
for the patient")
    name: List[dict] = Field(..., description="Patient's full name")
    gender: Optional[str] = None
    birthDate: Optional[datetime] = None
    address: Optional[List[dict]] = None
    phone: Optional[List[dict]] = None

# Basic Observation Model for Sarcoma Risk (Could include biomarkers, lab 
results, etc.)
class Observation(BaseModel):
    id: str
    resourceType: str = "Observation"
    status: str  # "final", "amended", etc.
    code: dict = Field(..., description="Code for the observation 
(biomarker or test result)")
    valueQuantity: dict = Field(..., description="The observed value")
    subject: dict = Field(..., description="Reference to the patient this 
observation is related to")
    effectiveDateTime: Optional[datetime] = None

# Sarcoma Risk Model - This will hold the results of SarcRisk biomarker 
analysis
class SarcomaRisk(BaseModel):
    id: str
    resourceType: str = "RiskAssessment"
    status: str  # "final" or other values indicating the risk assessment 
status
    subject: Patient  # The Patient associated with the risk
    date: datetime  # When the risk assessment was done
    prediction: List[dict]  # Contains risk predictions based on 
biomarkers and other data
    method: Optional[str] = None  # Example: "Biomarker analysis", "Family 
history", etc.
    rationale: Optional[str] = None  # Reasoning for the risk prediction

# Model for handling biomarkers
class Biomarker(BaseModel):
    id: str
    name: str  # Name of the biomarker (e.g., VEGF, MDM2)
    result: str  # Test result (e.g., positive, negative, elevated, etc.)
    unit: str  # Units for the result (e.g., pg/ml, ng/ml)
    referenceRange: str  # Possible range for the biomarker value (e.g., 
"10-50 pg/ml")
    observation: Observation  # A link to the actual observation or lab 
result for the biomarker

# Model for capturing genetic information linked to sarcoma risk
class GeneticData(BaseModel):
    id: str
    geneName: str  # Gene name (e.g., TP53, CDKN2A)
    mutationType: str  # e.g., missense, frameshift, etc.
    geneAlteration: str  # e.g., deletion, duplication, etc.
    associatedRisk: Optional[str] = None  # Possible risk increase linked 
to the mutation (e.g., "High")

# Model for linking the sarcoma risk prediction to a particular test or 
method
class RiskAssessmentMethod(BaseModel):
    id: str
    methodName: str  # e.g., "Biomarker Analysis", "Genetic Testing"
    description: Optional[str] = None  # A more detailed description of 
the method
    evidence: List[str] = []  # References to clinical evidence or studies 
supporting the method

# Model to track users who access the SarcRisk API (patient data 
requestors, clinicians, etc.)
class User(BaseModel):
    id: str
    username: str
    role: str  # e.g., "clinician", "researcher", "patient"
    email: Optional[str] = None
    lastLogin: Optional[datetime] = None
    apiKey: str  # API key for authentication purposes

# Sample Data Model to handle API responses and make the data consistent
class ApiResponse(BaseModel):
    status: str  # "success" or "error"
    data: dict  # The actual data returned in the response
    message: Optional[str] = None  # Any message or error description

