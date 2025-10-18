"""
Orchestrator API Routes - Phase 6
Unified endpoint for end-to-end prescription processing
"""
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.modules.orchestrator import PrescriptionOrchestrator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/orchestration", tags=["Orchestration"])

# Initialize orchestrator
orchestrator = PrescriptionOrchestrator()


# ==================== Request/Response Models ====================

class ProcessPrescriptionRequest(BaseModel):
    """Request to process a complete prescription workflow"""
    patient_id: str
    drug: str
    provider_name: str = "Dr. Unknown"
    npi: str = "0000000000"


class ProcessPrescriptionResponse(BaseModel):
    """Response with complete workflow result"""
    workflow_id: str
    status: str
    result: str = None
    recommendation: str
    timestamp: str = None
    patient: dict = None
    summary: str = None
    phases: dict = None


# ==================== Endpoints ====================

@router.post("/process-prescription", response_model=ProcessPrescriptionResponse)
async def process_prescription(request: ProcessPrescriptionRequest):
    """
    End-to-end prescription processing workflow
    
    Orchestrates all phases (2-5):
    - Phase 2: Coverage verification
    - Phase 3: Policy search with vector search
    - Phase 4: Clinical eligibility (LLM-based)
    - Phase 5: PA form generation
    
    This is the main entry point for prescription processing.
    
    Args:
        patient_id: Patient identifier (e.g., "P001")
        drug: Requested drug name (e.g., "Ozempic")
        provider_name: Prescribing provider name
        npi: Provider NPI number
    
    Returns:
        Complete workflow result with outputs from all phases
    
    Example Response:
        {
          "workflow_id": "WF_20251018150000_P001_OZEMPIC",
          "status": "completed",
          "result": "success",
          "recommendation": "DENY",
          "patient": {...},
          "summary": "Recommendation: DENY\nCoverage: Covered...",
          "phases": {
            "phase2_coverage": {...},
            "phase3_policy_search": {...},
            "phase4_eligibility": {...},
            "phase5_pa_form": {...}
          }
        }
    """
    try:
        logger.info(f"[API] Received prescription processing request: {request.patient_id}, {request.drug}")
        
        # Call orchestrator
        result = orchestrator.process_prescription(
            patient_id=request.patient_id,
            drug=request.drug,
            provider_name=request.provider_name,
            npi=request.npi
        )
        
        # Check for errors
        if result.get("status") == "error":
            logger.error(f"[API] Workflow error: {result.get('error')}")
            raise HTTPException(status_code=400, detail=result.get("error"))
        
        logger.info(f"[API] ✓ Workflow completed: {result.get('workflow_id')}")
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Prescription processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Workflow failed: {str(e)}")


@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """
    Get the status of a workflow (placeholder for future implementation)
    
    In the future, this would retrieve workflow status from a database
    """
    return {
        "workflow_id": workflow_id,
        "status": "not_implemented",
        "message": "Workflow status tracking will be implemented in Phase 7"
    }


@router.post("/process-prescription/quick-test")
async def quick_test():
    """
    Quick test endpoint - processes a sample prescription
    """
    return await process_prescription(
        ProcessPrescriptionRequest(
            patient_id="P001",
            drug="Ozempic",
            provider_name="Dr. Test",
            npi="0000000000"
        )
    )
