"""
API routes for clinical qualification and eligibility determination
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any

from app.data.database import get_db
from app.data.db_models import Patient
from app.modules.clinical_qualification import check_clinical_eligibility

router = APIRouter(prefix="/clinical-qualification", tags=["Clinical Qualification"])


# ==================== Request Models ====================

class EligibilityCheckRequest(BaseModel):
    """Request for clinical eligibility check"""
    patient_id: str
    drug: str
    policy_criteria: str
    use_rag: bool = True


# ==================== Response Models ====================

class EligibilityCheckResponse(BaseModel):
    """Response for eligibility check"""
    patient_id: str
    drug: str
    meets_criteria: bool
    confidence_score: float
    clinical_justification: str
    recommendation: str
    reasoning_details: Optional[Dict[str, Any]] = None
    llm_metadata: Optional[Dict[str, Any]] = None


# ==================== Endpoints ====================

@router.post("/check-eligibility", response_model=EligibilityCheckResponse)
async def check_eligibility(
    request: EligibilityCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if patient meets clinical eligibility criteria for requested drug
    
    Uses LLM reasoning augmented with retrieved insurance policy context (RAG).
    
    - **patient_id**: Patient identifier
    - **drug**: Requested medication
    - **policy_criteria**: Insurance policy eligibility requirements
    - **use_rag**: Whether to retrieve policy context from vector DB
    
    Returns eligibility determination with clinical reasoning and confidence score.
    """
    # Get patient from database
    patient = db.query(Patient).filter(Patient.patient_id == request.patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient not found: {request.patient_id}")
    
    # Convert patient DB record to dict
    patient_data = {
        "age": patient.age,
        "gender": patient.gender,
        "diagnoses": patient.diagnoses,
        "labs": patient.labs,
        "treatment_history": patient.treatment_history,
        "allergies": patient.allergies,
    }
    
    # Check eligibility using LLM
    try:
        result = check_clinical_eligibility(
            patient_id=request.patient_id,
            patient_data=patient_data,
            drug=request.drug,
            policy_criteria=request.policy_criteria,
            use_rag=request.use_rag,
        )
        
        return EligibilityCheckResponse(
            patient_id=request.patient_id,
            drug=request.drug,
            meets_criteria=result.meets_criteria,
            confidence_score=result.confidence_score,
            clinical_justification=result.clinical_justification,
            recommendation=result.recommendation,
            reasoning_details=result.reasoning_details,
            llm_metadata=result.llm_metadata,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Clinical qualification check failed: {str(e)}"
        )


@router.post("/check-eligibility/patient/{patient_id}")
async def check_patient_eligibility(
    patient_id: str,
    drug: str,
    policy_criteria: str,
    use_rag: bool = True,
    db: Session = Depends(get_db)
):
    """
    Check eligibility for a specific patient (simpler endpoint)
    
    - **patient_id**: Patient identifier (path parameter)
    - **drug**: Requested medication (query parameter)
    - **policy_criteria**: Policy requirements (query parameter)
    - **use_rag**: Use vector retrieval for context (query parameter)
    """
    request = EligibilityCheckRequest(
        patient_id=patient_id,
        drug=drug,
        policy_criteria=policy_criteria,
        use_rag=use_rag,
    )
    
    return await check_eligibility(request, db)
