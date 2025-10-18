"""
Orchestrator Module - Phase 6
Unified workflow that chains all phases (2-5) into a single end-to-end process
"""
import logging
from datetime import datetime
from typing import Dict, Any
from uuid import uuid4

from app.modules.benefit_verification import check_coverage
from app.modules.clinical_qualification import check_clinical_eligibility
from app.modules.prior_authorization import PriorAuthorizationGenerator
from app.data.database import get_db_context
from app.data.db_models import Patient
from app.data.vector_index import VectorIndexManager

logger = logging.getLogger(__name__)


class PrescriptionOrchestrator:
    """Orchestrates the complete prescription processing workflow (Phases 2-5)"""
    
    def __init__(self):
        """Initialize orchestrator with required modules"""
        self.pa_generator = PriorAuthorizationGenerator()
        self.vector_index = VectorIndexManager()
        logger.info("Orchestrator initialized")
    
    def process_prescription(
        self,
        patient_id: str,
        drug: str,
        provider_name: str = "Dr. Unknown",
        npi: str = "0000000000"
    ) -> Dict[str, Any]:
        """
        End-to-end prescription processing workflow
        
        Phases:
        - Phase 2: Coverage verification
        - Phase 3: Policy search (vector search for relevant policies)
        - Phase 4: Clinical eligibility (LLM-based)
        - Phase 5: PA form generation
        
        Args:
            patient_id: Patient identifier
            drug: Requested drug name
            provider_name: Prescribing provider name
            npi: Provider NPI
        
        Returns:
            Complete workflow result with all phase outputs
        """
        workflow_id = f"WF_{datetime.now().strftime('%Y%m%d%H%M%S')}_{patient_id}_{drug.upper()}"
        
        logger.info(f"[ORCHESTRATOR] Starting workflow: {workflow_id}")
        
        try:
            # Fetch patient data
            with get_db_context() as session:
                patient = session.query(Patient).filter(Patient.patient_id == patient_id).first()
                if not patient:
                    return self._error_response(workflow_id, f"Patient {patient_id} not found")
                
                patient_dict = {
                    "patient_id": patient.patient_id,
                    "name": patient.name,
                    "age": patient.age,
                    "gender": patient.gender,
                    "diagnoses": patient.diagnoses,
                    "labs": patient.labs,
                    "treatment_history": patient.treatment_history,
                    "insurance_plan": patient.insurance_plan,
                }
            
            # ============ PHASE 2: Coverage Verification ============
            logger.info(f"[ORCHESTRATOR] Phase 2: Checking coverage for {drug}...")
            coverage_result = self._phase2_coverage_check(patient_dict, drug)
            
            if not coverage_result["covered"]:
                logger.info(f"[ORCHESTRATOR] Drug not covered, workflow complete")
                return {
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "result": "not_covered",
                    "phases": {
                        "phase2_coverage": coverage_result,
                        "phase3_policy_search": None,
                        "phase4_eligibility": None,
                        "phase5_pa_form": None
                    },
                    "recommendation": "DENY",
                    "reason": f"{drug} is not covered under {patient_dict['insurance_plan']}"
                }
            
            # ============ PHASE 3: Policy Search ============
            logger.info(f"[ORCHESTRATOR] Phase 3: Searching for relevant policies...")
            policy_result = self._phase3_policy_search(drug)
            
            # Build policy criteria from search results
            policy_criteria = self._extract_policy_criteria(policy_result)
            
            # ============ PHASE 4: Clinical Eligibility ============
            logger.info(f"[ORCHESTRATOR] Phase 4: Checking clinical eligibility...")
            eligibility_result = self._phase4_eligibility_check(
                patient_dict=patient_dict,
                drug=drug,
                policy_criteria=policy_criteria
            )
            
            # ============ PHASE 5: PA Form Generation ============
            logger.info(f"[ORCHESTRATOR] Phase 5: Generating PA form...")
            pa_form_result = self._phase5_pa_generation(
                patient_id=patient_id,
                drug=drug,
                eligibility_result=eligibility_result,
                provider_name=provider_name,
                npi=npi
            )
            
            # ============ Determine Overall Recommendation ============
            recommendation = self._determine_recommendation(
                coverage_result,
                eligibility_result
            )
            
            # ============ Compile Complete Workflow Result ============
            workflow_result = {
                "workflow_id": workflow_id,
                "status": "completed",
                "result": "success",
                "timestamp": datetime.now().isoformat(),
                "patient": {
                    "id": patient_id,
                    "name": patient_dict["name"],
                    "age": patient_dict["age"],
                    "insurance_plan": patient_dict["insurance_plan"]
                },
                "phases": {
                    "phase2_coverage": coverage_result,
                    "phase3_policy_search": policy_result,
                    "phase4_eligibility": eligibility_result,
                    "phase5_pa_form": pa_form_result
                },
                "recommendation": recommendation,
                "summary": self._build_summary(
                    coverage_result,
                    eligibility_result,
                    recommendation
                )
            }
            
            logger.info(f"[ORCHESTRATOR] ✓ Workflow complete: {recommendation}")
            return workflow_result
        
        except Exception as e:
            logger.error(f"[ORCHESTRATOR] Workflow failed: {e}")
            return self._error_response(workflow_id, str(e))
    
    def _phase2_coverage_check(self, patient_dict: Dict[str, Any], drug: str) -> Dict[str, Any]:
        """Phase 2: Check coverage"""
        try:
            with get_db_context() as session:
                result = check_coverage(patient_dict["patient_id"], drug, session)
            
            # Convert result to dict if needed
            if hasattr(result, '__dict__'):
                result_dict = vars(result)
            else:
                result_dict = result
            
            return {
                "covered": result_dict.get("covered", False),
                "pa_required": result_dict.get("pa_required", False),
                "criteria": result_dict.get("criteria", ""),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Phase 2 failed: {e}")
            return {"covered": False, "status": "error", "error": str(e)}
    
    def _phase3_policy_search(self, drug: str) -> Dict[str, Any]:
        """Phase 3: Search for relevant policies"""
        try:
            results = self.vector_index.search(drug, top_k=3)
            return {
                "drug": drug,
                "policies_found": len(results),
                "results": results,
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Phase 3 failed: {e}")
            return {"policies_found": 0, "status": "error", "error": str(e)}
    
    def _phase4_eligibility_check(
        self,
        patient_dict: Dict[str, Any],
        drug: str,
        policy_criteria: str
    ) -> Dict[str, Any]:
        """Phase 4: Check clinical eligibility"""
        try:
            result = check_clinical_eligibility(
                patient_id=patient_dict["patient_id"],
                patient_data=patient_dict,
                drug=drug,
                policy_criteria=policy_criteria,
                use_rag=True
            )
            
            # Convert EligibilityResult to dict if needed
            if hasattr(result, '__dict__'):
                result_dict = vars(result)
            else:
                result_dict = result
            
            return {
                "meets_criteria": result_dict.get("meets_criteria", False),
                "confidence_score": result_dict.get("confidence_score", 0),
                "clinical_justification": result_dict.get("clinical_justification", ""),
                "recommendation": result_dict.get("recommendation", "REVIEW"),
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Phase 4 failed: {e}")
            return {"meets_criteria": False, "status": "error", "error": str(e)}
    
    def _phase5_pa_generation(
        self,
        patient_id: str,
        drug: str,
        eligibility_result: Dict[str, Any],
        provider_name: str,
        npi: str
    ) -> Dict[str, Any]:
        """Phase 5: Generate PA form"""
        try:
            form_data = self.pa_generator.generate_form(
                patient_id=patient_id,
                drug=drug,
                eligibility_result=eligibility_result,
                provider_name=provider_name,
                npi=npi
            )
            
            return {
                "form_id": form_data.get("form_id"),
                "status": "ready_for_submission",
                "has_clinical_narrative": bool(form_data.get("clinical_narrative")),
                "narrative_preview": (form_data.get("clinical_narrative", "")[:100] + "...") if form_data.get("clinical_narrative") else "",
                "full_form": form_data,
                "api_status": "success"
            }
        except Exception as e:
            logger.error(f"Phase 5 failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def _extract_policy_criteria(self, policy_result: Dict[str, Any]) -> str:
        """Extract policy criteria from search results"""
        if policy_result.get("status") != "success" or not policy_result.get("results"):
            return "Standard medical necessity criteria"
        
        # Combine all policy criteria into a single string
        criteria_list = []
        for result in policy_result.get("results", [])[:3]:
            if isinstance(result, dict) and "metadata" in result:
                metadata = result["metadata"]
                if "criteria" in metadata:
                    criteria_list.append(metadata["criteria"])
        
        return "; ".join(criteria_list) if criteria_list else "Standard medical necessity criteria"
    
    def _determine_recommendation(
        self,
        coverage_result: Dict[str, Any],
        eligibility_result: Dict[str, Any]
    ) -> str:
        """Determine overall recommendation"""
        if coverage_result.get("status") != "success" or not coverage_result.get("covered"):
            return "DENY"
        
        if eligibility_result.get("status") != "success":
            return "REVIEW"
        
        if eligibility_result.get("meets_criteria"):
            return "APPROVE"
        else:
            return "DENY"
    
    def _build_summary(
        self,
        coverage_result: Dict[str, Any],
        eligibility_result: Dict[str, Any],
        recommendation: str
    ) -> str:
        """Build human-readable summary"""
        lines = []
        
        lines.append(f"Recommendation: {recommendation}")
        
        if coverage_result.get("status") == "success":
            coverage_status = "Covered" if coverage_result.get("covered") else "Not Covered"
            pa_req = "PA Required" if coverage_result.get("pa_required") else "No PA Required"
            lines.append(f"Coverage: {coverage_status} ({pa_req})")
        
        if eligibility_result.get("status") == "success":
            criteria_status = "Meets" if eligibility_result.get("meets_criteria") else "Does Not Meet"
            confidence = eligibility_result.get("confidence_score", 0)
            lines.append(f"Eligibility: {criteria_status} criteria (Confidence: {confidence*100:.0f}%)")
            lines.append(f"Clinical Justification: {eligibility_result.get('clinical_justification', 'N/A')[:150]}...")
        
        return "\n".join(lines)
    
    def _error_response(self, workflow_id: str, error_msg: str) -> Dict[str, Any]:
        """Create error response"""
        return {
            "workflow_id": workflow_id,
            "status": "error",
            "error": error_msg,
            "timestamp": datetime.now().isoformat(),
            "phases": {
                "phase2_coverage": None,
                "phase3_policy_search": None,
                "phase4_eligibility": None,
                "phase5_pa_form": None
            }
        }
