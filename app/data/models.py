"""
Pydantic models for request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ==================== Common Models ====================

class Address(BaseModel):
    """Address model"""
    street: str
    city: str
    state: str
    zip: str


class Diagnosis(BaseModel):
    """Diagnosis with ICD-10 code"""
    name: str
    icd10: str


class TreatmentHistory(BaseModel):
    """Treatment history entry"""
    drug: str
    duration_months: int
    dosage: Optional[str] = None
    outcome: str
    started_date: Optional[str] = None


class LabResults(BaseModel):
    """Laboratory results"""
    HbA1c: Optional[float] = None
    fasting_glucose: Optional[int] = None
    BMI: Optional[float] = None
    weight_lbs: Optional[float] = None
    creatinine: Optional[float] = None
    eGFR: Optional[int] = None
    ALT: Optional[int] = None
    AST: Optional[int] = None
    last_updated: Optional[str] = None


# ==================== Patient Models ====================

class Patient(BaseModel):
    """Patient data model"""
    patient_id: str
    name: str
    date_of_birth: str
    age: int
    gender: str
    address: Address
    phone: str
    email: str
    insurance_plan: str
    member_id: str
    diagnoses: List[Diagnosis]
    labs: LabResults
    treatment_history: List[TreatmentHistory]
    allergies: List[str]
    created_at: Optional[str] = None


class PatientSummary(BaseModel):
    """Simplified patient summary"""
    patient_id: str
    name: str
    age: int
    insurance_plan: str
    diagnoses: List[str]


# ==================== Insurance Plan Models ====================

class InsurancePlan(BaseModel):
    """Insurance plan coverage details"""
    plan: str
    drug: str
    covered: bool
    pa_required: bool
    criteria: Optional[str] = None
    tier: Optional[int] = None
    estimated_copay: Optional[float] = None
    step_therapy_required: bool = False
    quantity_limit: Optional[str] = None


# ==================== Request/Response Models ====================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    version: str


class SystemInfoResponse(BaseModel):
    """System information response"""
    environment: str
    openrouter_model: str
    database_connected: bool
    redis_connected: bool
    chromadb_initialized: bool


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

