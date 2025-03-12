# test_main.py
import pytest
from main import (
    calculate_molecular_score,
    calculate_risk_score_with_symptoms_and_imaging,
    update_fhir_risk_assessment_with_symptoms_and_imaging
)
from fhir.resources.riskassessment import RiskAssessment
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.extension import Extension
from fhir.resources.quantity import Quantity

# Test calculate_molecular_score function
def test_calculate_molecular_score():
    # Test case 1: High VEGF, CDKN2A mutation, and TP53 mutation
    molecular_data = {
        "VEGF_level": 120,
        "CDKN2A_mutation": True,
        "TP53_mutation": True
    }
    score = calculate_molecular_score(molecular_data)
    assert score == 1.2, f"Expected 1.2 but got {score}"

    # Test case 2: No genetic markers
    molecular_data = {
        "VEGF_level": 50,
        "CDKN2A_mutation": False,
        "TP53_mutation": False
    }
    score = calculate_molecular_score(molecular_data)
    assert score == 0.0, f"Expected 0.0 but got {score}"

# Test calculate_risk_score_with_symptoms_and_imaging function
def test_calculate_risk_score_with_symptoms_and_imaging():
    molecular_data = {
        "VEGF_level": 120,
        "CDKN2A_mutation": True,
        "TP53_mutation": True
    }
    clinical_data = {
        "pain": True,
        "swelling": True,
        "fever": False,
        "tumor_size": 6
    }
    imaging_data = {
        "mri_abnormalities": True,
        "ct_scan_abnormalities": False,
        "pet_scan_high_activity": True,
        "x_ray_findings": False
    }
    
    score = calculate_risk_score_with_symptoms_and_imaging(
        molecular_data, clinical_data, imaging_data
    )
    assert score > 0.8, f"Expected score > 0.8 but got {score}"

# Test update_fhir_risk_assessment_with_symptoms_and_imaging function
def test_update_fhir_risk_assessment_with_symptoms_and_imaging():
    request_data = {
        "molecular_data": {
            "VEGF_level": 120,
            "CDKN2A_mutation": True,
            "TP53_mutation": True,
        },
        "clinical_data": {
            "pain": True,
            "swelling": True,
            "fever": False,
            "tumor_size": 6
        },
        "imaging_data": {
            "mri_abnormalities": True,
            "ct_scan_abnormalities": False,
            "pet_scan_high_activity": True,
            "x_ray_findings": False
        }
    }
    
    # Simulating the risk score
    risk_score = 0.9
    risk_category = "High"
    suspected_subtypes = ["Soft Tissue Sarcoma", "Osteosarcoma"]

    risk_assessment = 
update_fhir_risk_assessment_with_symptoms_and_imaging(
        request_data, risk_score, risk_category, suspected_subtypes
    )

    # Check if the FHIR RiskAssessment object is created correctly
    assert isinstance(risk_assessment, RiskAssessment), "RiskAssessment 
object was not created."
    assert risk_assessment.status == "final", f"Expected 'final' status, 
but got {risk_assessment.status}"
    assert len(risk_assessment.prediction) == 1, "Risk assessment should 
have one prediction."
    
    # Check for specific fields in the RiskAssessment object
    prediction = risk_assessment.prediction[0]
    assert prediction.outcome.text == "High", f"Expected 'High' outcome 
but got {prediction.outcome.text}"

    # Check for extensions (suspected subtypes)
    extensions = [ext for ext in risk_assessment.extension if ext.url == 
"http://example.com/suspected-sarcoma-subtypes"]
    assert extensions, "Suspected sarcoma subtypes not found in the 
extensions."
    assert extensions[0].valueCodeableConcept.text == "Soft Tissue 
Sarcoma, Osteosarcoma", (
        f"Expected 'Soft Tissue Sarcoma, Osteosarcoma', but got 
{extensions[0].valueCodeableConcept.text}"
    )

    # Check for tumor size extension
    tumor_size_ext = [ext for ext in risk_assessment.extension if ext.url 
== "http://example.com/tumor-size"]
    assert tumor_size_ext, "Tumor size extension not found."
    assert tumor_size_ext[0].valueQuantity.value == 6, f"Expected tumor 
size of 6 cm, but got {tumor_size_ext[0].valueQuantity.value}"

# Run the tests
if __name__ == "__main__":
    pytest.main()

