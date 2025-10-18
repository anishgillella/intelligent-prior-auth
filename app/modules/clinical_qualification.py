"""
Clinical Qualification Module

Determines if patients meet medical necessity criteria using LLM reasoning
augmented with retrieved insurance policy context (RAG pattern).
"""
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import logging
import json

from app.core.llm_client import get_llm_client
from app.data.vector_index import get_vector_manager
from app.prompts.clinical_qualification import (
    get_rag_enhanced_prompt,
    SYSTEM_PROMPT
)

logger = logging.getLogger(__name__)


class EligibilityResult:
    """Clinical eligibility determination result"""
    
    def __init__(
        self,
        meets_criteria: bool,
        confidence_score: float,
        clinical_justification: str,
        recommendation: str,
        reasoning_details: Optional[Dict[str, Any]] = None,
        llm_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.meets_criteria = meets_criteria
        self.confidence_score = confidence_score
        self.clinical_justification = clinical_justification
        self.recommendation = recommendation
        self.reasoning_details = reasoning_details or {}
        self.llm_metadata = llm_metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "meets_criteria": self.meets_criteria,
            "confidence_score": round(self.confidence_score, 4),
            "clinical_justification": self.clinical_justification,
            "recommendation": self.recommendation,
            "reasoning_details": self.reasoning_details,
            "llm_metadata": self.llm_metadata,
        }


def check_clinical_eligibility(
    patient_id: str,
    patient_data: Dict[str, Any],
    drug: str,
    policy_criteria: str,
    use_rag: bool = True,
) -> EligibilityResult:
    """
    Check if patient meets clinical eligibility criteria using LLM reasoning
    
    Args:
        patient_id: Patient identifier
        patient_data: Patient clinical data
        drug: Requested drug
        policy_criteria: Insurance policy eligibility criteria
        use_rag: Whether to use RAG (retrieve policy context)
        
    Returns:
        EligibilityResult with determination
    """
    logger.info(f"Checking eligibility for patient {patient_id}, drug {drug}")
    
    # Get LLM client
    llm_client = get_llm_client()
    
    # Build treatment history string
    treatment_history = _format_treatment_history(patient_data.get("treatment_history", []))
    
    # Build diagnoses string
    diagnoses = _format_diagnoses(patient_data.get("diagnoses", []))
    
    # Retrieve policy context if RAG enabled
    policy_context = ""
    if use_rag:
        logger.info(f"Retrieving policy context for {drug}...")
        vector_manager = get_vector_manager()
        
        search_query = f"{drug} {diagnoses} treatment criteria requirements"
        search_results = vector_manager.search(search_query, top_k=3)
        
        if search_results:
            policy_context = _format_policy_context(search_results)
            logger.info(f"Retrieved {len(search_results)} policy context chunks")
    
    # Build prompt
    prompt = get_rag_enhanced_prompt(
        policy_context=policy_context,
        policy_criteria=policy_criteria,
        patient_id=patient_id,
        age=patient_data.get("age", 0),
        gender=patient_data.get("gender", "Unknown"),
        diagnoses=diagnoses,
        hba1c=patient_data.get("labs", {}).get("HbA1c", 0),
        bmi=patient_data.get("labs", {}).get("BMI", 0),
        weight=patient_data.get("labs", {}).get("weight_lbs", 0),
        creatinine=patient_data.get("labs", {}).get("creatinine", 0),
        egfr=patient_data.get("labs", {}).get("eGFR", 0),
        treatment_history=treatment_history,
        drug=drug,
        specific_requirements=policy_criteria,
    )
    
    # Call LLM
    logger.info("Calling LLM for clinical reasoning...")
    try:
        llm_response = llm_client.call(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,  # Low temp for consistent reasoning
            max_tokens=1000,
        )
        
        # Parse response
        response_content = llm_response["content"]
        parsed_response = llm_client.parse_json_response(response_content)
        
        logger.info(f"LLM response: {parsed_response}")
        
        # Extract fields
        meets_criteria = parsed_response.get("meets_criteria", False)
        confidence_score = parsed_response.get("confidence_score", 0.0)
        clinical_justification = parsed_response.get("clinical_justification", "")
        recommendation = parsed_response.get("recommendation", "NEEDS_REVIEW")
        
        # Build result
        result = EligibilityResult(
            meets_criteria=meets_criteria,
            confidence_score=confidence_score,
            clinical_justification=clinical_justification,
            recommendation=recommendation,
            reasoning_details=parsed_response,
            llm_metadata={
                "model": llm_response["model"],
                "latency_ms": llm_response["latency_ms"],
                "tokens_used": llm_response["tokens_used"],
                "cost": llm_response["cost"],
            }
        )
        
        logger.info(f"Eligibility check complete: {recommendation} (confidence: {confidence_score})")
        return result
        
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


def _format_treatment_history(treatment_history: List[Dict[str, Any]]) -> str:
    """Format treatment history for prompt"""
    if not treatment_history:
        return "No prior treatment history available"
    
    lines = []
    for i, treatment in enumerate(treatment_history, 1):
        drug = treatment.get("drug", "Unknown")
        months = treatment.get("duration_months", "Unknown")
        outcome = treatment.get("outcome", "Unknown")
        lines.append(f"{i}. {drug}: {months} months, outcome: {outcome}")
    
    return "\n".join(lines)


def _format_diagnoses(diagnoses: List[Dict[str, str]]) -> str:
    """Format diagnoses for prompt"""
    if not diagnoses:
        return "No diagnoses recorded"
    
    return ", ".join([f"{d.get('name')} ({d.get('icd10', 'N/A')})" for d in diagnoses])


def _format_policy_context(search_results: List[Dict[str, Any]]) -> str:
    """Format retrieved policy context"""
    if not search_results:
        return ""
    
    lines = ["Retrieved Policy Context:"]
    for i, result in enumerate(search_results, 1):
        text = result.get("text", "")[:300]  # Truncate
        plan = result.get("metadata", {}).get("plan", "Unknown")
        drug = result.get("metadata", {}).get("drug", "Unknown")
        similarity = result.get("similarity", 0)
        
        lines.append(f"\n[Context {i} - {plan}/{drug} ({similarity:.2%} match)]")
        lines.append(text + "...")
    
    return "\n".join(lines)
