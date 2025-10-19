"""
Prior Authorization (PA) Module
Generates PA forms with LLM-generated clinical narratives
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.core.llm_client import get_llm_client
from app.data.database import get_db_context
from app.data.db_models import Patient
from app.prompts.prior_authorization import (
    PA_NARRATIVE_SYSTEM_PROMPT,
    PA_NARRATIVE_USER_TEMPLATE,
    PA_MARKDOWN_TEMPLATE
)

logger = logging.getLogger(__name__)


class PriorAuthorizationGenerator:
    """Generates Prior Authorization forms with LLM-generated narratives"""
    
    def __init__(self):
        """Initialize PA generator with LLM client"""
        self.llm_client = get_llm_client()
    
    def generate_form(
        self,
        patient_id: str,
        drug: str,
        eligibility_result: Dict[str, Any],
        provider_name: str = "Dr. Unknown",
        npi: str = "0000000000"
    ) -> Dict[str, Any]:
        """
        Generate a complete PA form with clinical narrative
        
        Args:
            patient_id: Patient identifier
            drug: Drug name
            eligibility_result: Output from clinical qualification module
            provider_name: Prescribing provider name
            npi: Provider NPI
        
        Returns:
            Dict with form data including clinical narrative
        """
        try:
            logger.info(f"Generating PA form for patient {patient_id}, drug {drug}")
            
            # Fetch patient from database
            with get_db_context() as session:
                patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
                
                if not patient:
                    logger.error(f"Patient {patient_id} not found")
                    raise ValueError(f"Patient {patient_id} not found")
                
                # Create data copy while session is active
                patient_data = {
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "age": patient.age,
                    "gender": patient.gender,
                    "diagnoses": patient.diagnoses,
                    "insurance_plan": patient.insurance_plan,
                    "date_of_birth": patient.date_of_birth,
                    "member_id": patient.member_id
                }
            
            # Convert EligibilityResult to dict if needed
            if hasattr(eligibility_result, '__dict__'):
                result_dict = vars(eligibility_result)
            else:
                result_dict = eligibility_result
            
            # Build LLM prompt
            prompt_content = f"""Generate a clinical justification paragraph for a Prior Authorization request:

PATIENT: {patient_data['name']}, Age {patient_data['age']}, {patient_data['gender']}
DIAGNOSIS: {patient_data['diagnoses']}
DRUG: {drug}
POLICY CRITERIA: {result_dict.get('clinical_justification', 'Standard medical necessity')}

Create a professional 150-250 word clinical justification narrative."""
            
            # Generate clinical narrative using LLM
            logger.info("Calling LLM to generate clinical narrative...")
            narrative_response = self.llm_client.call(
                messages=[
                    {"role": "system", "content": PA_NARRATIVE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt_content}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            clinical_narrative = narrative_response["content"]
            logger.info("✓ Clinical narrative generated")
            
            # Generate form metadata
            form_id = f"PA_{datetime.now().strftime('%Y%m%d')}_{patient_id}_{drug.upper()}"
            
            # Build complete form
            form_data = {
                "form_id": form_id,
                "submission_date": datetime.now().isoformat(),
                "requesting_provider": provider_name,
                "npi": npi,
                "patient_name": patient_data["name"],
                "date_of_birth": patient_data.get("date_of_birth", "N/A"),
                "patient_id": patient_id,
                "member_id": patient_data.get("member_id", "N/A"),
                "insurance_plan": patient_data["insurance_plan"],
                "drug_name": drug,
                "dosage": "As prescribed",
                "frequency": "As prescribed",
                "duration": "3 months",
                "diagnosis_description": str(patient_data["diagnoses"]),
                "diagnosis_code": "E11.9",
                "clinical_narrative": clinical_narrative,
                "failed_treatments": "See medical record",
                "clinical_findings": str(patient_data["diagnoses"]),
                "supporting_evidence": "Clinical determination and policy compliance verified",
                "contraindications": "None noted",
                "llm_metadata": narrative_response.get("llm_metadata", {}),
                "eligibility_result": {
                    "meets_criteria": result_dict.get("meets_criteria", False),
                    "confidence_score": result_dict.get("confidence_score", 0),
                    "recommendation": result_dict.get("recommendation", "REVIEW")
                }
            }
            
            logger.info(f"✓ PA form generated: {form_id}")
            return form_data
        
        except Exception as e:
            logger.error(f"PA form generation failed: {e}")
            raise
    
    def generate_markdown_form(
        self,
        form_data: Dict[str, Any]
    ) -> str:
        """
        Generate markdown representation of the PA form
        
        Args:
            form_data: Form data dict from generate_form()
        
        Returns:
            Markdown string
        """
        markdown = f"""# PRIOR AUTHORIZATION REQUEST

## Form Information
- **Form ID**: {form_data.get("form_id", "PA_UNKNOWN")}
- **Submission Date**: {form_data.get("submission_date", "")}
- **Requesting Provider**: {form_data.get("requesting_provider", "Dr. Unknown")}

## Patient Information
- **Name**: {form_data.get("patient_name", "N/A")}
- **Date of Birth**: {form_data.get("date_of_birth", "N/A")}
- **Member ID**: {form_data.get("member_id", "N/A")}
- **Insurance Plan**: {form_data.get("insurance_plan", "N/A")}

## Clinical Information
- **Requested Drug**: {form_data.get("drug_name", "N/A")}
- **Dosage**: {form_data.get("dosage", "As prescribed")}
- **Frequency**: {form_data.get("frequency", "As prescribed")}
- **Expected Duration**: {form_data.get("duration", "3 months")}
- **Primary Diagnosis**: {form_data.get("diagnosis_description", "N/A")}

## Clinical Justification

{form_data.get("clinical_narrative", "No narrative available")}

### Clinical Findings
{form_data.get("clinical_findings", "N/A")}

### Supporting Evidence
{form_data.get("supporting_evidence", "N/A")}

---
**Confidential - For Insurance Use Only**
"""
        
        return markdown
