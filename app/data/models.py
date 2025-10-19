"""
Pydantic models for request/response validation
Enhanced with LogFire validation tracking
"""
from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.core.monitoring import ValidationEventLogger


# ==================== Common Models ====================

class Address(BaseModel):
    """Address model"""
    street: str
    city: str
    state: str
    zip: str

    @field_validator('zip')
    @classmethod
    def validate_zip(cls, v):
        """Validate ZIP code format"""
        if not v or len(v) < 5:
            error_msg = "Invalid ZIP code format"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Address",
                field_name="zip",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Address",
            field_name="zip",
            status="success",
            details={"zip": v}
        )
        return v

    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        """Validate state code"""
        valid_states = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
                       'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
                       'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
                       'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
                       'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        if v.upper() not in valid_states:
            error_msg = f"Invalid state: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Address",
                field_name="state",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Address",
            field_name="state",
            status="success",
            details={"state": v}
        )
        return v.upper()


class Diagnosis(BaseModel):
    """Diagnosis with ICD-10 code"""
    name: str
    icd10: str

    @field_validator('icd10')
    @classmethod
    def validate_icd10(cls, v):
        """Validate ICD-10 code format"""
        # Basic ICD-10 format: Letter followed by 2 digits, optionally dot and additional characters
        import re
        pattern = r'^[A-Z]\d{2}(\.\d{1,2})?$'
        if not re.match(pattern, v):
            error_msg = f"Invalid ICD-10 code format: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Diagnosis",
                field_name="icd10",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Diagnosis",
            field_name="icd10",
            status="success",
            details={"icd10": v}
        )
        return v


class TreatmentHistory(BaseModel):
    """Treatment history entry"""
    drug: str
    duration_months: int
    dosage: Optional[str] = None
    outcome: str
    started_date: Optional[str] = None

    @field_validator('duration_months')
    @classmethod
    def validate_duration(cls, v):
        """Validate treatment duration"""
        if v <= 0 or v > 1200:  # Max 100 years
            error_msg = f"Invalid duration: {v} months"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="TreatmentHistory",
                field_name="duration_months",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="TreatmentHistory",
            field_name="duration_months",
            status="success",
            details={"duration_months": v}
        )
        return v


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

    @field_validator('HbA1c')
    @classmethod
    def validate_hba1c(cls, v):
        """Validate HbA1c value (normal: 4-6%, diabetic: >6.5%)"""
        if v is not None and (v < 3 or v > 15):
            error_msg = f"Invalid HbA1c: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="LabResults",
                field_name="HbA1c",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        if v is not None:
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="LabResults",
                field_name="HbA1c",
                status="success",
                details={"HbA1c": v}
            )
        return v

    @field_validator('BMI')
    @classmethod
    def validate_bmi(cls, v):
        """Validate BMI (typical range: 10-60)"""
        if v is not None and (v < 10 or v > 60):
            error_msg = f"Invalid BMI: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="LabResults",
                field_name="BMI",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        if v is not None:
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="LabResults",
                field_name="BMI",
                status="success",
                details={"BMI": v}
            )
        return v


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

    @field_validator('age')
    @classmethod
    def validate_age(cls, v):
        """Validate patient age (0-150 years)"""
        if v < 0 or v > 150:
            error_msg = f"Invalid age: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Patient",
                field_name="age",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Patient",
            field_name="age",
            status="success",
            details={"age": v}
        )
        return v

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        """Validate gender field"""
        valid_genders = ['M', 'F', 'Other', 'Prefer not to say']
        if v not in valid_genders:
            error_msg = f"Invalid gender: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Patient",
                field_name="gender",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Patient",
            field_name="gender",
            status="success",
            details={"gender": v}
        )
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            error_msg = f"Invalid email: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Patient",
                field_name="email",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Patient",
            field_name="email",
            status="success"
        )
        return v

    @model_validator(mode='after')
    def validate_diagnoses_not_empty(self):
        """Validate that patient has at least one diagnosis"""
        if not self.diagnoses or len(self.diagnoses) == 0:
            error_msg = "Patient must have at least one diagnosis"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="Patient",
                field_name="diagnoses",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        ValidationEventLogger.log_validation_event(
            event_type="validation",
            model_name="Patient",
            field_name="diagnoses",
            status="success",
            details={"diagnosis_count": len(self.diagnoses)}
        )
        return self


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

    @field_validator('tier')
    @classmethod
    def validate_tier(cls, v):
        """Validate insurance tier (1-4)"""
        if v is not None and (v < 1 or v > 4):
            error_msg = f"Invalid tier: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="InsurancePlan",
                field_name="tier",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        if v is not None:
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="InsurancePlan",
                field_name="tier",
                status="success",
                details={"tier": v}
            )
        return v

    @field_validator('estimated_copay')
    @classmethod
    def validate_copay(cls, v):
        """Validate copay amount"""
        if v is not None and v < 0:
            error_msg = f"Invalid copay: {v}"
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="InsurancePlan",
                field_name="estimated_copay",
                status="error",
                error_message=error_msg
            )
            raise ValueError(error_msg)
        if v is not None:
            ValidationEventLogger.log_validation_event(
                event_type="validation",
                model_name="InsurancePlan",
                field_name="estimated_copay",
                status="success",
                details={"copay": v}
            )
        return v


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

