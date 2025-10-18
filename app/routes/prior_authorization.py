"""
Prior Authorization API Routes
Endpoints for generating PA forms with clinical narratives
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sqlalchemy.orm import Session
from app.data.database import get_db_context
from app.data.db_models import Patient
from app.modules.prior_authorization import PriorAuthorizationGenerator
from app.modules.clinical_qualification import check_clinical_eligibility

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prior-authorization", tags=["prior-authorization"])

# Initialize generators
pa_generator = PriorAuthorizationGenerator()



# Request/Response Models
class PAFormGenerationRequest(BaseModel):
    """Request to generate a PA form"""
    patient_id: str
    drug: str
    policy_criteria: str = "Standard medical necessity"
    use_rag: bool = True
    provider_name: str = "Dr. Unknown"
    npi: str = "0000000000"


class PAFormGenerationResponse(BaseModel):
    """Response containing generated PA form"""
    form_id: str
    patient_name: str
    drug_name: str
    clinical_narrative: str
    submission_date: str
    confidence_score: float
    recommendation: str
    llm_metadata: dict


class PAFormMarkdownResponse(BaseModel):
    """Response containing markdown PA form"""
    form_id: str
    markdown: str
    llm_metadata: dict


@router.post("/generate-form", response_model=PAFormGenerationResponse)
async def generate_pa_form(request: PAFormGenerationRequest):
    """
    Generate a complete PA form with LLM-generated clinical narrative
    
    This endpoint:
    1. Checks clinical eligibility using Phase 4 logic
    2. Generates clinical narrative with LLM
    3. Packages into standardized PA form
    
    Args:
        patient_id: Patient identifier
        drug: Requested drug name
        policy_criteria: Insurance policy criteria string
        use_rag: Whether to use vector search for policy context
        provider_name: Prescribing provider name
        npi: Provider NPI number
    
    Returns:
        Complete PA form with clinical narrative
    """
    try:
        logger.info(f"[PA] Generating form for {request.patient_id}, drug: {request.drug}")
        
        # Step 1: Check clinical eligibility (Phase 4)
        logger.info("[PA] Step 1: Checking clinical eligibility...")

        # Fetch patient data
        with get_db_context() as session:
            patient_obj = session.query(Patient).filter(Patient.patient_id == request.patient_id).first()
            
            if not patient_obj:
                raise ValueError(f"Patient {request.patient_id} not found")
            
            # Extract all data while session is active
            patient_dict = {
                "patient_id": patient_obj.patient_id,
                "name": patient_obj.name,
                "age": patient_obj.age,
                "gender": patient_obj.gender,
                "diagnoses": patient_obj.diagnoses or [],
                "labs": patient_obj.labs or {},
                "treatment_history": patient_obj.treatment_history or []
            }

        eligibility_check = check_clinical_eligibility(
            patient_id=request.patient_id,
            patient_data=patient_dict,
            drug=request.drug,
            policy_criteria=request.policy_criteria,
            use_rag=request.use_rag
        )
        logger.info("[PA] Step 2: Generating PA form with clinical narrative...")
        form_data = pa_generator.generate_form(
            patient_id=request.patient_id,
            drug=request.drug,
            eligibility_result=eligibility_check,
            provider_name=request.provider_name,
            npi=request.npi
        )
        
        # Return response
        logger.info(f"[PA] ✓ Form generated: {form_data['form_id']}")
        return PAFormGenerationResponse(
            form_id=form_data["form_id"],
            patient_name=form_data["patient_name"],
            drug_name=form_data["drug_name"],
            clinical_narrative=form_data["clinical_narrative"],
            submission_date=form_data["submission_date"],
            confidence_score=form_data["eligibility_result"]["confidence_score"],
            recommendation=form_data["eligibility_result"]["recommendation"],
            llm_metadata=form_data["llm_metadata"]
        )
    
    except ValueError as e:
        logger.error(f"[PA] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[PA] Form generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PA form generation failed: {str(e)}")


@router.post("/generate-form-markdown", response_model=PAFormMarkdownResponse)
async def generate_pa_form_markdown(request: PAFormGenerationRequest):
    """
    Generate a PA form in markdown format (human-readable)
    
    Args:
        Same as generate_pa_form
    
    Returns:
        Markdown-formatted PA form suitable for display/printing
    """
    try:
        logger.info(f"[PA-Markdown] Generating markdown form for {request.patient_id}")
        
        # Fetch patient data
        with get_db_context() as session:
            patient_obj = session.query(Patient).filter(Patient.patient_id == request.patient_id).first()
            
            if not patient_obj:
                raise ValueError(f"Patient {request.patient_id} not found")
            
            # Extract all data while session is active
            patient_dict = {
                "patient_id": patient_obj.patient_id,
                "name": patient_obj.name,
                "age": patient_obj.age,
                "gender": patient_obj.gender,
                "diagnoses": patient_obj.diagnoses or [],
                "labs": patient_obj.labs or {},
                "treatment_history": patient_obj.treatment_history or []
            }
        
        eligibility_check = check_clinical_eligibility(
            patient_id=request.patient_id,
            patient_data=patient_dict,
            drug=request.drug,
            policy_criteria=request.policy_criteria,
            use_rag=request.use_rag
        )
        
        # Generate form
        form_data = pa_generator.generate_form(
            patient_id=request.patient_id,
            drug=request.drug,
            eligibility_result=eligibility_check,
            provider_name=request.provider_name,
            npi=request.npi
        )
        
        # Generate markdown
        markdown = pa_generator.generate_markdown_form(form_data)
        
        logger.info(f"[PA-Markdown] ✓ Markdown form generated")
        return PAFormMarkdownResponse(
            form_id=form_data["form_id"],
            markdown=markdown,
            llm_metadata=form_data["llm_metadata"]
        )
    
    except ValueError as e:
        logger.error(f"[PA-Markdown] Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"[PA-Markdown] Form generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"PA markdown generation failed: {str(e)}")
