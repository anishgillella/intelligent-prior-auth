"""
Monitoring Integration for Clinical Modules
Tracks clinical operations with Langfuse and LogFire
"""
import logging
from typing import Dict, Any, Optional
from app.core.prompt_tracker import get_prompt_tracker
from app.core.monitoring import get_langfuse_client

logger = logging.getLogger(__name__)


def track_clinical_eligibility_prompt(
    patient_id: str,
    drug: str,
    llm_response: str,
    metrics: Dict[str, Any],
    eligibility_assessment: Dict[str, Any]
):
    """Track clinical eligibility assessment prompt execution"""
    try:
        tracker = get_prompt_tracker()
        tracker.track_prompt_execution(
            prompt_name="clinical_eligibility_assessment",
            prompt_type="clinical_qualification",
            input_data={
                "patient_id": patient_id,
                "drug": drug,
            },
            output=llm_response,
            metrics=metrics,
            variant=None
        )
        
        # Also log assessment result to Langfuse
        langfuse_client = get_langfuse_client()
        if langfuse_client:
            trace = langfuse_client.trace(
                name="clinical_eligibility_result",
                input={
                    "patient_id": patient_id,
                    "drug": drug,
                }
            )
            trace.update(
                output={
                    "meets_criteria": eligibility_assessment.get("meets_criteria"),
                    "confidence_score": eligibility_assessment.get("confidence_score"),
                    "recommendation": eligibility_assessment.get("recommendation"),
                },
                level="DEFAULT",
            )
            langfuse_client.flush()
        
        logger.info(
            f"Clinical eligibility tracked | Patient: {patient_id} | Drug: {drug} | "
            f"Meets Criteria: {eligibility_assessment.get('meets_criteria')}"
        )
    except Exception as e:
        logger.error(f"Failed to track clinical eligibility: {e}")


def track_prior_authorization_prompt(
    patient_id: str,
    drug: str,
    pa_form_id: str,
    llm_response: str,
    metrics: Dict[str, Any]
):
    """Track prior authorization form generation prompt execution"""
    try:
        tracker = get_prompt_tracker()
        tracker.track_prompt_execution(
            prompt_name="prior_authorization_narrative",
            prompt_type="prior_authorization",
            input_data={
                "patient_id": patient_id,
                "drug": drug,
                "form_id": pa_form_id,
            },
            output=llm_response,
            metrics=metrics,
            variant=None
        )
        
        # Log to Langfuse
        langfuse_client = get_langfuse_client()
        if langfuse_client:
            trace = langfuse_client.trace(
                name="prior_authorization_generation",
                input={
                    "patient_id": patient_id,
                    "drug": drug,
                    "form_id": pa_form_id,
                }
            )
            trace.update(
                output={
                    "narrative_generated": bool(llm_response),
                    "content_length": len(llm_response),
                },
                level="DEFAULT",
            )
            langfuse_client.flush()
        
        logger.info(
            f"PA narrative tracked | Form: {pa_form_id} | Drug: {drug} | "
            f"Content Length: {len(llm_response)} chars"
        )
    except Exception as e:
        logger.error(f"Failed to track prior authorization prompt: {e}")


def track_benefit_verification_check(
    patient_id: str,
    drug: str,
    coverage_result: Dict[str, Any]
):
    """Track benefit verification check results"""
    try:
        langfuse_client = get_langfuse_client()
        if langfuse_client:
            trace = langfuse_client.trace(
                name="benefit_verification",
                input={
                    "patient_id": patient_id,
                    "drug": drug,
                }
            )
            trace.update(
                output={
                    "covered": coverage_result.get("covered"),
                    "pa_required": coverage_result.get("pa_required"),
                    "tier": coverage_result.get("tier"),
                    "copay": coverage_result.get("estimated_copay"),
                },
                level="DEFAULT",
            )
            langfuse_client.flush()
        
        logger.info(
            f"Benefit verification tracked | Patient: {patient_id} | Drug: {drug} | "
            f"Covered: {coverage_result.get('covered')}"
        )
    except Exception as e:
        logger.error(f"Failed to track benefit verification: {e}")


def track_policy_search(
    drug: str,
    policies_found: int,
    search_metrics: Dict[str, Any]
):
    """Track policy search results"""
    try:
        langfuse_client = get_langfuse_client()
        if langfuse_client:
            trace = langfuse_client.trace(
                name="policy_search",
                input={
                    "drug": drug,
                }
            )
            trace.update(
                output={
                    "policies_found": policies_found,
                    "search_time_ms": search_metrics.get("latency_ms"),
                },
                level="DEFAULT",
            )
            langfuse_client.flush()
        
        logger.info(
            f"Policy search tracked | Drug: {drug} | Policies Found: {policies_found}"
        )
    except Exception as e:
        logger.error(f"Failed to track policy search: {e}")


def track_orchestrator_workflow(
    workflow_id: str,
    patient_id: str,
    drug: str,
    final_recommendation: str,
    phase_results: Dict[str, Any]
):
    """Track complete orchestrator workflow execution"""
    try:
        langfuse_client = get_langfuse_client()
        if langfuse_client:
            trace = langfuse_client.trace(
                name="orchestrator_workflow",
                input={
                    "workflow_id": workflow_id,
                    "patient_id": patient_id,
                    "drug": drug,
                }
            )
            trace.update(
                output={
                    "recommendation": final_recommendation,
                    "phases_completed": len([p for p in phase_results.values() if p]),
                    "total_phases": len(phase_results),
                },
                level="DEFAULT",
            )
            langfuse_client.flush()
        
        logger.info(
            f"Workflow tracked | ID: {workflow_id} | Recommendation: {final_recommendation}"
        )
    except Exception as e:
        logger.error(f"Failed to track orchestrator workflow: {e}")
