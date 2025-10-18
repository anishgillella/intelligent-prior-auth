"""
Benefit Verification Module

Determines if a drug is covered under a patient's insurance plan
and whether prior authorization is required.
"""
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
import logging

from app.data.db_models import InsurancePlan, Patient

logger = logging.getLogger(__name__)


class CoverageResult:
    """Coverage check result"""
    def __init__(
        self,
        covered: bool,
        pa_required: bool,
        criteria: Optional[str] = None,
        tier: Optional[int] = None,
        estimated_copay: Optional[float] = None,
        step_therapy_required: bool = False,
        quantity_limit: Optional[str] = None,
        reason: Optional[str] = None,
    ):
        self.covered = covered
        self.pa_required = pa_required
        self.criteria = criteria
        self.tier = tier
        self.estimated_copay = estimated_copay
        self.step_therapy_required = step_therapy_required
        self.quantity_limit = quantity_limit
        self.reason = reason
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "covered": self.covered,
            "pa_required": self.pa_required,
            "criteria": self.criteria,
            "tier": self.tier,
            "estimated_copay": self.estimated_copay,
            "step_therapy_required": self.step_therapy_required,
            "quantity_limit": self.quantity_limit,
            "reason": self.reason,
        }


def check_coverage(
    patient_id: str,
    drug: str,
    db: Session
) -> CoverageResult:
    """
    Check if a drug is covered under patient's insurance plan
    
    Args:
        patient_id: Patient ID
        drug: Drug name
        db: Database session
        
    Returns:
        CoverageResult with coverage details
    """
    logger.info(f"Checking coverage for patient {patient_id}, drug {drug}")
    
    # Get patient
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not patient:
        logger.warning(f"Patient not found: {patient_id}")
        return CoverageResult(
            covered=False,
            pa_required=False,
            reason=f"Patient not found: {patient_id}"
        )
    
    # Get plan coverage for drug
    plan_coverage = db.query(InsurancePlan).filter(
        InsurancePlan.plan == patient.insurance_plan,
        InsurancePlan.drug == drug
    ).first()
    
    if not plan_coverage:
        logger.warning(f"Drug not in formulary: {drug} for plan {patient.insurance_plan}")
        return CoverageResult(
            covered=False,
            pa_required=False,
            reason=f"Drug not in formulary for {patient.insurance_plan}"
        )
    
    # Drug is in formulary
    if not plan_coverage.covered:
        return CoverageResult(
            covered=False,
            pa_required=False,
            reason=f"Drug not covered under {patient.insurance_plan}"
        )
    
    # Drug is covered
    logger.info(f"Drug covered: {drug}, PA required: {plan_coverage.pa_required}")
    
    return CoverageResult(
        covered=True,
        pa_required=plan_coverage.pa_required,
        criteria=plan_coverage.criteria,
        tier=plan_coverage.tier,
        estimated_copay=plan_coverage.estimated_copay,
        step_therapy_required=plan_coverage.step_therapy_required,
        quantity_limit=plan_coverage.quantity_limit,
        reason="Coverage found" if plan_coverage.pa_required else "Covered, no PA required"
    )


def check_coverage_by_plan(
    plan_name: str,
    drug: str,
    db: Session
) -> CoverageResult:
    """
    Check coverage for a specific plan and drug (without patient)
    
    Args:
        plan_name: Insurance plan name
        drug: Drug name
        db: Database session
        
    Returns:
        CoverageResult with coverage details
    """
    logger.info(f"Checking coverage for plan {plan_name}, drug {drug}")
    
    plan_coverage = db.query(InsurancePlan).filter(
        InsurancePlan.plan == plan_name,
        InsurancePlan.drug == drug
    ).first()
    
    if not plan_coverage:
        return CoverageResult(
            covered=False,
            pa_required=False,
            reason=f"Drug not in formulary for {plan_name}"
        )
    
    if not plan_coverage.covered:
        return CoverageResult(
            covered=False,
            pa_required=False,
            reason=f"Drug not covered under {plan_name}"
        )
    
    return CoverageResult(
        covered=True,
        pa_required=plan_coverage.pa_required,
        criteria=plan_coverage.criteria,
        tier=plan_coverage.tier,
        estimated_copay=plan_coverage.estimated_copay,
        step_therapy_required=plan_coverage.step_therapy_required,
        quantity_limit=plan_coverage.quantity_limit,
        reason="Coverage found" if plan_coverage.pa_required else "Covered, no PA required"
    )


def get_covered_alternatives(
    plan_name: str,
    drug_class: str,
    db: Session
) -> List[Dict]:
    """
    Get alternative drugs covered under a plan
    
    Args:
        plan_name: Insurance plan name
        drug_class: Drug class/category (for future implementation)
        db: Database session
        
    Returns:
        List of alternative drugs
    """
    # For MVP, return all covered drugs under the plan
    alternatives = db.query(InsurancePlan).filter(
        InsurancePlan.plan == plan_name,
        InsurancePlan.covered == True
    ).limit(10).all()
    
    return [
        {
            "drug": alt.drug,
            "tier": alt.tier,
            "estimated_copay": alt.estimated_copay,
            "pa_required": alt.pa_required,
        }
        for alt in alternatives
    ]


def get_patient_insurance_info(patient_id: str, db: Session) -> Optional[Dict]:
    """
    Get patient's insurance information
    
    Args:
        patient_id: Patient ID
        db: Database session
        
    Returns:
        Dictionary with insurance info or None
    """
    patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    
    if not patient:
        return None
    
    return {
        "patient_id": patient.patient_id,
        "name": patient.name,
        "insurance_plan": patient.insurance_plan,
        "member_id": patient.member_id,
    }

