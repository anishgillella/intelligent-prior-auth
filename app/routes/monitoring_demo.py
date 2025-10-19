"""
Monitoring Demo Routes
Demonstrates LogFire validation and Langfuse LLM monitoring
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Dict, Any, Optional
import logging

from app.data.models import Patient, Address, Diagnosis, LabResults, TreatmentHistory
from app.core.monitoring import ValidationEventLogger, LLMCallMonitor, get_langfuse_client
from app.core.prompt_tracker import get_prompt_tracker
from app.core.llm_client import get_llm_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.post("/validate-patient", response_model=Dict[str, Any])
async def validate_patient(patient_data: Dict[str, Any] = Body(...)):
    """
    Endpoint to test Pydantic validation with LogFire tracking
    
    LogFire will track all validation events (success/failure) with field details.
    """
    try:
        # This will trigger all Pydantic validators and log to LogFire
        patient = Patient(**patient_data)
        
        return {
            "status": "success",
            "message": "Patient validated successfully",
            "patient_id": patient.patient_id,
            "name": patient.name,
            "age": patient.age,
            "diagnoses_count": len(patient.diagnoses),
        }
    except ValueError as e:
        logger.error(f"Patient validation error: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-llm-monitoring", response_model=Dict[str, Any])
async def test_llm_monitoring(
    prompt: str = Body(..., embed=True),
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
):
    """
    Endpoint to test Langfuse LLM monitoring
    
    Sends a prompt to the LLM and Langfuse tracks:
    - Input messages and parameters
    - Output content and tokens
    - Latency and cost
    - Success/error status
    """
    try:
        llm_client = get_llm_client()
        
        messages = [
            {
                "role": "system",
                "content": "You are a medical assistant helping with healthcare documentation."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        # This call is automatically monitored by Langfuse
        result = llm_client.call(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        # Track with prompt tracker for A/B testing capability
        tracker = get_prompt_tracker()
        tracker.track_prompt_execution(
            prompt_name="demo_prompt",
            prompt_type="demo",
            input_data={"user_prompt": prompt},
            output=result["content"],
            metrics={
                "latency_ms": result["latency_ms"],
                "tokens_used": result["tokens_used"],
                "cost": result["cost"],
            }
        )
        
        return {
            "status": "success",
            "model": result["model"],
            "content": result["content"],
            "tokens_used": result["tokens_used"],
            "latency_ms": result["latency_ms"],
            "cost": result["cost"],
        }
    except Exception as e:
        logger.error(f"LLM monitoring test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prompt-stats", response_model=Dict[str, Any])
async def get_prompt_stats():
    """
    Get statistics for all tracked prompts
    
    Returns performance metrics for A/B testing analysis
    """
    try:
        tracker = get_prompt_tracker()
        stats = tracker.get_all_stats()
        
        return {
            "status": "success",
            "tracked_prompts": list(stats.keys()),
            "statistics": stats,
        }
    except Exception as e:
        logger.error(f"Failed to get prompt stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/monitoring-status", response_model=Dict[str, Any])
async def get_monitoring_status():
    """
    Get current monitoring system status
    
    Shows if LogFire and Langfuse are enabled
    """
    try:
        import logfire
        from app.core.config import settings
        
        langfuse_client = get_langfuse_client()
        
        return {
            "status": "active",
            "monitoring_systems": {
                "logfire": {
                    "enabled": bool(settings.logfire_api_key),
                    "configured": bool(logfire),
                },
                "langfuse": {
                    "enabled": bool(settings.langfuse_api_key),
                    "connected": langfuse_client is not None,
                    "host": settings.langfuse_host if langfuse_client else None,
                },
            },
            "monitoring_enabled": settings.enable_monitoring,
        }
    except Exception as e:
        logger.error(f"Failed to get monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
