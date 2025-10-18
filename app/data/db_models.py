"""
SQLAlchemy database models
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON, Text
from datetime import datetime
from app.data.database import Base


class InsurancePlan(Base):
    """Insurance plan coverage information"""
    __tablename__ = "insurance_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan = Column(String(100), nullable=False, index=True)
    drug = Column(String(100), nullable=False, index=True)
    covered = Column(Boolean, nullable=False)
    pa_required = Column(Boolean, nullable=False)
    criteria = Column(Text, nullable=True)
    tier = Column(Integer, nullable=True)
    estimated_copay = Column(Float, nullable=True)
    step_therapy_required = Column(Boolean, default=False)
    quantity_limit = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<InsurancePlan(plan={self.plan}, drug={self.drug}, covered={self.covered})>"


class Patient(Base):
    """Patient information"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    date_of_birth = Column(String(20), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    address = Column(JSON, nullable=False)  # Store as JSON
    phone = Column(String(50), nullable=False)
    email = Column(String(200), nullable=False)
    insurance_plan = Column(String(100), nullable=False, index=True)
    member_id = Column(String(100), nullable=False)
    diagnoses = Column(JSON, nullable=False)  # Store as JSON array
    labs = Column(JSON, nullable=False)  # Store as JSON object
    treatment_history = Column(JSON, nullable=False)  # Store as JSON array
    allergies = Column(JSON, nullable=False)  # Store as JSON array
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Patient(patient_id={self.patient_id}, name={self.name}, plan={self.insurance_plan})>"


class PAForm(Base):
    """PA form templates"""
    __tablename__ = "pa_forms"
    
    id = Column(Integer, primary_key=True, index=True)
    plan = Column(String(100), nullable=False, index=True)
    payer_name = Column(String(100), nullable=False)
    form_version = Column(String(50), nullable=False)
    template = Column(JSON, nullable=False)  # Store template as JSON
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PAForm(plan={self.plan}, version={self.form_version})>"


class LLMLog(Base):
    """Log of LLM API calls for monitoring and debugging"""
    __tablename__ = "llm_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    model = Column(String(100), nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    tokens_used = Column(Integer, nullable=True)
    latency_ms = Column(Float, nullable=True)
    cost = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f"<LLMLog(model={self.model}, tokens={self.tokens_used}, latency={self.latency_ms}ms)>"

