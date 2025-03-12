from fhir.resources.riskassessment import RiskAssessment, 
RiskAssessmentPredictionComponent
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.extension import Extension
from fhir.resources.quantity import Quantity
from fhir.resources.reference import Reference
from fhir.resources.coding import Coding
from fhir.resources.observation import Observation
from fhir.resources.patient import Patient

def map_to_risk_assessment(patient_data: dict, total_score: float, 
risk_category: str, suspected_subtypes: list) -> RiskAssessment:
    """
    Maps patient data to a FHIR RiskAssessment resource, incorporating 
clinical, molecular, and imaging data.
    """
    # Create a RiskAssessment resource
    risk_assessment = RiskAssessment()
    risk_assessment.status = "final"
    risk_assessment.subject = Reference(reference="Patient/12345")  # 
Reference to the patient in FHIR
    risk_assessment.code = CodeableConcept(
        coding=[Coding(system="http://snomed.info/sct", code="420324007", 
display="Sarcoma risk assessment")]
    )
    risk_assessment.prediction = [
        RiskAssessmentPredictionComponent(
            outcome=CodeableConcept(text=risk_category),
            probabilityDecimal=total_score / 100
        )
    ]

    # Adding suspected sarcoma subtypes based on molecular and clinical 
data
    risk_assessment.extension = [
        Extension(
            url="http://example.com/suspected-sarcoma-subtypes",
            valueCodeableConcept=CodeableConcept(text=", 
".join(suspected_subtypes))
        )
    ]
    
    # Adding tumor size, symptoms, and imaging data as extensions
    risk_assessment.extension.append(
        Extension(
            url="http://example.com/tumor-size",
            
valueQuantity=Quantity(value=patient_data["clinical_data"].get("tumor_size", 
0), unit="cm")
        )
    )
    risk_assessment.extension.append(
        Extension(
            url="http://example.com/clinical-symptoms",
            valueCodeableConcept=CodeableConcept(text="Pain, Swelling, 
Fever: " + ", ".join(patient_data["clinical_data"].keys()))
        )
    )
    risk_assessment.extension.append(
        Extension(
            url="http://example.com/imaging-findings",
            valueCodeableConcept=CodeableConcept(text="MRI Abnormalities, 
PET Scan Activity: " + ", ".join(patient_data["imaging_data"].keys()))
        )
    )

    # Setting the references to the relevant Observation resources
    risk_assessment.basis = [
        Reference(reference="Observation/clinical-data"),
        Reference(reference="Observation/molecular-data"),
        Reference(reference="Observation/tumor-size"),
        Reference(reference="Observation/clinical-symptoms"),
        Reference(reference="Observation/imaging-findings")
    ]
    
    return risk_assessment

def map_to_observation(resource_type: str, data: dict, code: str, display: 
str) -> Observation:
    """
    Maps clinical data to a FHIR Observation resource.
    """
    observation = Observation()
    observation.status = "final"
    observation.code = CodeableConcept(
        coding=[Coding(system="http://snomed.info/sct", code=code, 
display=display)]
    )
    
    if resource_type == "clinical":
        observation.valueQuantity = Quantity(value=data.get("tumor_size", 
0), unit="cm")
    elif resource_type == "molecular":
        observation.valueQuantity = Quantity(value=data.get("VEGF_level", 
0), unit="pg/mL")  # Example for VEGF level
    elif resource_type == "imaging":
        observation.valueCodeableConcept = CodeableConcept(text=", 
".join(data.keys()))  # Example imaging findings

    return observation

def map_to_patient(patient_data: dict) -> Patient:
    """
    Maps patient data to a FHIR Patient resource.
    """
    patient = Patient()
    patient.id = "12345"  # Example patient ID
    patient.name = [{"use": "official", "family": 
patient_data["name"]["family"], "given": patient_data["name"]["given"]}]
    
    # Add other patient demographics like gender, birth date, etc. if 
needed
    return patient

def main():
    # Example patient data
    patient_data = {
        "name": {"family": "Doe", "given": ["John"]},
        "molecular_data": {
            "VEGF_level": 120,  # High VEGF level
            "CDKN2A_mutation": True,  # CDKN2A mutation present
            "TP53_mutation": True,  # TP53 mutation detected
        },
        "clinical_data": {
            "pain": True,  # Persistent pain
            "swelling": True,  # Localized swelling
            "fever": False,  # No fever
            "tumor_size": 6  # Tumor size 6 cm
        },
        "imaging_data": {
            "mri_abnormalities": True,  # MRI shows irregularities
            "ct_scan_abnormalities": False,
            "pet_scan_high_activity": True,  # PET scan shows increased 
activity
            "x_ray_findings": False
        }
    }
    
    # Calculate risk score (using your calculation function from earlier)
    risk_score = calculate_risk_score_with_symptoms_and_imaging(
        patient_data["molecular_data"],
        patient_data["clinical_data"],
        patient_data["imaging_data"]
    )
    
    # Define risk category based on score
    risk_category = "High" if risk_score > 0.7 else "Medium" if risk_score 
> 0.4 else "Low"
    
    # Suspected subtypes based on clinical and molecular data
    suspected_subtypes = ["Soft Tissue Sarcoma", "Osteosarcoma"]  # 
Example, change based on logic
    
    # Map to FHIR resources
    patient_resource = map_to_patient(patient_data)
    risk_assessment_resource = map_to_risk_assessment(patient_data, 
risk_score, risk_category, suspected_subtypes)
    
    # Example of mapping clinical observation
    observation_resource = map_to_observation("clinical", 
patient_data["clinical_data"], "7530005", "Tumor Size")
    
    # Print the resulting resources as JSON
    print(patient_resource.json())
    print(risk_assessment_resource.json())
    print(observation_resource.json())

if __name__ == "__main__":
    main()

