"""
API routes for benefit verification
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from app.data.database import get_db
from app.modules.benefit_verification import (
    check_coverage,
    check_coverage_by_plan,
    get_covered_alternatives,
    get_patient_insurance_info,
)

router = APIRouter(prefix="/benefit-verification", tags=["Benefit Verification"])


# ==================== Request Models ====================

class CoverageCheckRequest(BaseModel):
    """Request model for coverage check"""
    patient_id: str = Field(..., description="Patient ID (e.g., P001)")
    drug: str = Field(..., description="Drug name (e.g., Ozempic)")


class PlanCoverageRequest(BaseModel):
    """Request model for plan-based coverage check"""
    plan: str = Field(..., description="Insurance plan name (e.g., Aetna Gold)")
    drug: str = Field(..., description="Drug name (e.g., Ozempic)")


# ==================== Response Models ====================

class CoverageResponse(BaseModel):
    """Response model for coverage check"""
    covered: bool
    pa_required: bool
    criteria: Optional[str] = None
    tier: Optional[int] = None
    estimated_copay: Optional[float] = None
    step_therapy_required: bool = False
    quantity_limit: Optional[str] = None
    reason: Optional[str] = None


class PatientInsuranceResponse(BaseModel):
    """Response model for patient insurance info"""
    patient_id: str
    name: str
    insurance_plan: str
    member_id: str


# ==================== Endpoints ====================

@router.post("/check-coverage", response_model=CoverageResponse)
async def check_patient_coverage(
    request: CoverageCheckRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a drug is covered under a patient's insurance plan
    
    - **patient_id**: Patient identifier
    - **drug**: Drug name to check coverage for
    
    Returns coverage details including PA requirements and estimated costs
    """
    result = check_coverage(
        patient_id=request.patient_id,
        drug=request.drug,
        db=db
    )
    
    return result.to_dict()


@router.post("/check-plan-coverage", response_model=CoverageResponse)
async def check_plan_drug_coverage(
    request: PlanCoverageRequest,
    db: Session = Depends(get_db)
):
    """
    Check if a drug is covered under a specific insurance plan
    
    - **plan**: Insurance plan name
    - **drug**: Drug name to check coverage for
    
    Useful for checking coverage without patient context
    """
    result = check_coverage_by_plan(
        plan_name=request.plan,
        drug=request.drug,
        db=db
    )
    
    return result.to_dict()


@router.get("/patient/{patient_id}/insurance", response_model=PatientInsuranceResponse)
async def get_patient_insurance(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    Get patient's insurance information
    
    - **patient_id**: Patient identifier
    
    Returns basic insurance details for the patient
    """
    info = get_patient_insurance_info(patient_id, db)
    
    if not info:
        raise HTTPException(status_code=404, detail=f"Patient not found: {patient_id}")
    
    return info


@router.get("/plan/{plan_name}/alternatives")
async def get_alternative_drugs(
    plan_name: str,
    drug_class: str = "GLP-1",
    db: Session = Depends(get_db)
):
    """
    Get alternative drugs covered under a plan
    
    - **plan_name**: Insurance plan name
    - **drug_class**: Drug class/category (optional)
    
    Returns list of alternative medications covered by the plan
    """
    alternatives = get_covered_alternatives(
        plan_name=plan_name,
        drug_class=drug_class,
        db=db
    )
    
    return {
        "plan": plan_name,
        "alternatives": alternatives,
        "count": len(alternatives)
    }


@router.get("/plans")
async def list_insurance_plans(db: Session = Depends(get_db)):
    """
    List all available insurance plans
    
    Returns distinct list of insurance plan names in the system
    """
    from app.data.db_models import InsurancePlan
    from sqlalchemy import distinct
    
    plans = db.query(distinct(InsurancePlan.plan)).all()
    plan_names = [p[0] for p in plans]
    
    return {
        "plans": sorted(plan_names),
        "count": len(plan_names)
    }


@router.get("/drugs")
async def list_drugs(db: Session = Depends(get_db)):
    """
    List all drugs in the formulary
    
    Returns distinct list of drug names in the system
    """
    from app.data.db_models import InsurancePlan
    from sqlalchemy import distinct
    
    drugs = db.query(distinct(InsurancePlan.drug)).all()
    drug_names = [d[0] for d in drugs]
    
    return {
        "drugs": sorted(drug_names),
        "count": len(drug_names)
    }

