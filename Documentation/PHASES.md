# 🚀 Phase-by-Phase Implementation Guide

This document provides detailed implementation steps for each phase of the Develop Health MVP replica.

---

## 📦 Phase 1: Foundation & Synthetic Data

### Step 1.1: Project Structure Setup

Create the following directory structure:

```bash
develop-health-mvp/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── logger.py
│   │   └── security.py
│   ├── modules/
│   │   └── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── models.py
│   ├── utils/
│   │   └── __init__.py
│   └── routes/
│       └── __init__.py
├── mock_data/
│   └── policies/
├── scripts/
│   └── __init__.py
├── tests/
│   └── __init__.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── pytest.ini
```

### Step 1.2: Create `requirements.txt`

```txt
# Web Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.6.0
pydantic-settings==2.1.0

# LLM & Embeddings
openai==1.10.0  # OpenRouter uses OpenAI-compatible API
langchain==0.1.4
langchain-community==0.0.16
sentence-transformers==2.3.1

# Vector Database
chromadb==0.4.22

# Database
psycopg2-binary==2.9.9
sqlalchemy==2.0.25
alembic==1.13.1

# Async Tasks
celery==5.3.6
redis==5.0.1

# PDF Generation
reportlab==4.0.9
pypdf2==3.0.1

# Data Generation & Processing
faker==22.6.0
python-dateutil==2.8.2

# Utilities
tenacity==8.2.3  # Retry logic
python-dotenv==1.0.1
httpx==0.26.0

# Testing
pytest==8.0.0
pytest-asyncio==0.23.4
pytest-cov==4.1.0

# Monitoring (optional)
prometheus-client==0.19.0
```

### Step 1.3: Create `.env.example`

```bash
# OpenRouter Configuration
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=openai/gpt-4o
# Alternative models:
# OPENROUTER_MODEL=anthropic/claude-3.5-sonnet
# OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct

# Database
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/develop_health_mvp
REDIS_URL=redis://localhost:6379/0

# ChromaDB
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Application
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Security
API_KEY=dev_api_key_change_in_production

# Paths
PA_FORMS_OUTPUT_DIR=/tmp/pa_forms
MOCK_DATA_DIR=./mock_data
```

### Step 1.4: Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:16-alpine
    container_name: develop_health_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: develop_health_mvp
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: develop_health_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  celery_worker:
    build: .
    container_name: develop_health_celery
    command: celery -A app.core.celery_app worker --loglevel=info
    depends_on:
      - redis
      - postgres
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/develop_health_mvp
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./app:/app/app
      - ./mock_data:/app/mock_data

volumes:
  postgres_data:
  redis_data:
```

### Step 1.5: Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create output directory for PA forms
RUN mkdir -p /tmp/pa_forms

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Step 1.6: Create `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
dist/
*.egg-info/

# Environment
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# Database
*.db
*.sqlite3
chroma_db/

# Outputs
/tmp/pa_forms/
*.pdf

# Testing
.coverage
htmlcov/
.pytest_cache/

# Docker
.dockerignore

# macOS
.DS_Store
```

### Step 1.7: Create Basic FastAPI App (`app/main.py`)

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.logger import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Develop Health MVP API...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"OpenRouter Model: {settings.openrouter_model}")
    yield
    logger.info("Shutting down Develop Health MVP API...")


# Create FastAPI app
app = FastAPI(
    title="Develop Health MVP - AI Prior Authorization",
    description="AI-powered healthcare automation for benefit verification, clinical qualification, and prior authorization",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Develop Health MVP - AI Prior Authorization API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "develop-health-mvp",
        "version": "1.0.0",
    }


@app.get("/info")
async def system_info():
    """System information endpoint"""
    return {
        "environment": settings.environment,
        "openrouter_model": settings.openrouter_model,
        "database_connected": True,  # TODO: Add actual DB connection check
        "redis_connected": True,  # TODO: Add actual Redis connection check
        "chromadb_initialized": False,  # TODO: Add actual ChromaDB check
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
    )
```

### Step 1.8: Create Configuration (`app/core/config.py`)

```python
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Environment
    environment: str = "development"
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_key: str = "dev_api_key"
    
    # OpenRouter Settings
    openrouter_api_key: str
    openrouter_model: str = "openai/gpt-4o"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str
    
    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"
    
    # Paths
    pa_forms_output_dir: str = "/tmp/pa_forms"
    mock_data_dir: str = "./mock_data"
    
    # Logging
    log_level: str = "INFO"
    
    # LLM Settings
    llm_temperature: float = 0.1
    llm_max_tokens: int = 1000
    llm_timeout: int = 30
    
    # Confidence Thresholds
    eligibility_confidence_threshold: float = 0.8
    quality_score_threshold: float = 0.9
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

### Step 1.9: Create Logger (`app/core/logger.py`)

```python
import logging
import sys
from pathlib import Path
from app.core.config import settings


def setup_logging():
    """Setup application logging"""
    
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_dir / "app.log"),
        ],
    )
    
    # Set specific loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("chromadb").setLevel(logging.WARNING)
```

### Step 1.10: Create Synthetic Data Generator (`scripts/generate_synthetic_data.py`)

```python
"""
Generate synthetic healthcare data for testing
"""
import json
from pathlib import Path
from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Output directory
DATA_DIR = Path("mock_data")
DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "policies").mkdir(exist_ok=True)

# Common drugs for diabetes/GLP-1 agonists
DRUGS = [
    "Ozempic", "Trulicity", "Victoza", "Mounjaro", "Wegovy",
    "Jardiance", "Invokana", "Metformin", "Glipizide", "Lantus"
]

# Insurance plans
INSURANCE_PLANS = [
    "Aetna Gold", "Aetna Silver", "BlueCross Silver", "BlueCross Gold",
    "UnitedHealthcare Choice", "Cigna Open Access", "Humana Gold Plus",
    "Kaiser Permanente", "Anthem Blue Cross", "Medicare Part D"
]

# ICD-10 codes for common conditions
ICD10_CODES = {
    "Type 2 Diabetes": "E11.9",
    "Type 1 Diabetes": "E10.9",
    "Obesity": "E66.9",
    "Hypertension": "I10",
    "Hyperlipidemia": "E78.5",
    "NASH": "K76.0",
    "Chronic Kidney Disease": "N18.9",
}


def generate_patients(n=50):
    """Generate synthetic patient data"""
    patients = []
    
    for i in range(1, n + 1):
        age = random.randint(25, 75)
        bmi = random.uniform(22, 45)
        hba1c = random.uniform(5.5, 12.0)
        
        # Generate diagnoses based on BMI/age
        diagnoses = []
        if bmi > 30:
            diagnoses.append("Obesity")
        if hba1c > 6.5 or random.random() > 0.5:
            diagnoses.append("Type 2 Diabetes")
        if age > 50 and random.random() > 0.5:
            diagnoses.append("Hypertension")
        if random.random() > 0.7:
            diagnoses.append("Hyperlipidemia")
        
        # Generate treatment history
        treatment_history = []
        if "Type 2 Diabetes" in diagnoses:
            treatment_history.append({
                "drug": "Metformin",
                "duration_months": random.randint(3, 24),
                "dosage": "1000mg twice daily",
                "outcome": random.choice(["Inadequate response", "Partial response", "Good response"]),
                "started_date": (datetime.now() - timedelta(days=random.randint(90, 730))).strftime("%Y-%m-%d")
            })
            
            if random.random() > 0.5:
                treatment_history.append({
                    "drug": "Glipizide",
                    "duration_months": random.randint(2, 12),
                    "dosage": "10mg daily",
                    "outcome": random.choice(["Inadequate response", "Intolerance"]),
                    "started_date": (datetime.now() - timedelta(days=random.randint(60, 365))).strftime("%Y-%m-%d")
                })
        
        patient = {
            "patient_id": f"P{i:03d}",
            "name": fake.name(),
            "date_of_birth": fake.date_of_birth(minimum_age=age, maximum_age=age).strftime("%Y-%m-%d"),
            "age": age,
            "gender": random.choice(["Male", "Female"]),
            "address": {
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zip": fake.zipcode()
            },
            "phone": fake.phone_number(),
            "email": fake.email(),
            "insurance_plan": random.choice(INSURANCE_PLANS),
            "member_id": f"MEM{fake.random_number(digits=10)}",
            "diagnoses": [{"name": d, "icd10": ICD10_CODES[d]} for d in diagnoses],
            "labs": {
                "HbA1c": round(hba1c, 1),
                "fasting_glucose": random.randint(90, 250),
                "BMI": round(bmi, 1),
                "weight_lbs": round(bmi * 703 / (68 ** 2) * (68 ** 2), 1),  # Approx
                "creatinine": round(random.uniform(0.7, 1.5), 2),
                "eGFR": random.randint(60, 120),
                "ALT": random.randint(10, 60),
                "AST": random.randint(10, 55),
                "last_updated": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            },
            "treatment_history": treatment_history,
            "allergies": random.sample(["Penicillin", "Sulfa", "None known"], k=1),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        patients.append(patient)
    
    return patients


def generate_plans():
    """Generate insurance plan formularies"""
    plans = []
    
    for plan in INSURANCE_PLANS:
        for drug in DRUGS:
            # Randomly assign coverage
            covered = random.random() > 0.1  # 90% coverage rate
            pa_required = random.random() > 0.3 if covered else False  # 70% need PA if covered
            
            # Generate criteria for PA
            criteria = None
            if pa_required:
                criteria_options = [
                    "BMI > 30 AND HbA1c > 7.5",
                    "BMI > 27 AND HbA1c > 8.0 AND failed metformin for 3+ months",
                    "HbA1c > 9.0 OR failed two oral agents",
                    "Type 2 Diabetes AND BMI > 30 AND cardiovascular risk factors present",
                ]
                criteria = random.choice(criteria_options)
            
            plan_entry = {
                "plan": plan,
                "drug": drug,
                "covered": covered,
                "pa_required": pa_required,
                "criteria": criteria,
                "tier": random.randint(2, 4) if covered else None,
                "estimated_copay": random.choice([10, 25, 50, 100]) if covered else None,
                "step_therapy_required": random.random() > 0.7,
                "quantity_limit": random.choice([None, "30 day supply", "90 day supply"]),
            }
            
            plans.append(plan_entry)
    
    return plans


def generate_forms():
    """Generate PA form templates"""
    forms = []
    
    for plan in INSURANCE_PLANS:
        form = {
            "plan": plan,
            "payer_name": plan.split()[0],  # e.g., "Aetna" from "Aetna Gold"
            "form_version": "2024.1",
            "template": {
                "patient_demographics": {
                    "patient_name": "",
                    "date_of_birth": "",
                    "member_id": "",
                    "gender": ""
                },
                "prescriber_info": {
                    "prescriber_name": "Dr. Sarah Johnson",
                    "npi": "1234567890",
                    "phone": "(555) 123-4567",
                    "fax": "(555) 123-4568",
                    "practice_name": "Endocrine Associates",
                    "address": "123 Medical Plaza, Suite 200"
                },
                "medication_info": {
                    "drug_name": "",
                    "strength": "",
                    "quantity": "",
                    "days_supply": "30",
                    "refills": "11"
                },
                "clinical_information": {
                    "diagnosis": "",
                    "icd10_codes": [],
                    "relevant_labs": {},
                    "treatment_history": "",
                    "clinical_justification": ""
                },
                "submission_method": random.choice(["portal", "fax", "mail"])
            }
        }
        forms.append(form)
    
    return forms


def generate_pa_policies():
    """Generate PA policy documents for vector indexing"""
    policies = []
    
    policy_templates = {
        "Ozempic": """
PRIOR AUTHORIZATION POLICY: SEMAGLUTIDE (OZEMPIC)

Plan: {plan}
Effective Date: January 1, 2024

INDICATION:
Treatment of Type 2 Diabetes Mellitus as an adjunct to diet and exercise.

COVERAGE CRITERIA:
Patient must meet ALL of the following:

1. Diagnosis of Type 2 Diabetes Mellitus (ICD-10: E11.x)
2. Body Mass Index (BMI) ≥ 30 kg/m² OR BMI ≥ 27 kg/m² with weight-related comorbidity
3. HbA1c ≥ 7.5% within the past 90 days
4. Trial and inadequate response to metformin for at least 3 months (unless contraindicated)
5. Prescribed by or in consultation with an endocrinologist or PCP with diabetes management experience

QUANTITY LIMITS:
- One pen per 28 days
- Starting dose: 0.25mg weekly for 4 weeks, then 0.5mg weekly

DURATION OF AUTHORIZATION:
Initial: 6 months
Renewal: 12 months with documentation of:
  - HbA1c reduction of ≥ 0.5% OR
  - Weight loss of ≥ 5% from baseline

EXCLUSIONS:
- Type 1 Diabetes
- Personal or family history of medullary thyroid carcinoma
- Multiple Endocrine Neoplasia syndrome type 2 (MEN 2)
""",
        "Trulicity": """
PRIOR AUTHORIZATION POLICY: DULAGLUTIDE (TRULICITY)

Plan: {plan}
Effective Date: January 1, 2024

INDICATION:
Treatment of Type 2 Diabetes Mellitus

COVERAGE CRITERIA:
Patient must meet ALL of the following:

1. Diagnosis of Type 2 Diabetes Mellitus confirmed
2. HbA1c ≥ 8.0% within past 60 days
3. Failed or intolerant to at least TWO oral antidiabetic agents including metformin
4. BMI > 27 kg/m²
5. No history of pancreatitis

CLINICAL DOCUMENTATION REQUIRED:
- Current HbA1c value and date
- List of previous diabetes medications tried with dates and outcomes
- Current weight and BMI
- Recent lipid panel and renal function tests

AUTHORIZATION PERIOD:
12 months with annual renewal
""",
    }
    
    for drug, template in policy_templates.items():
        for plan in INSURANCE_PLANS[:3]:  # Generate for first 3 plans
            policy_text = template.format(plan=plan)
            filename = f"{plan.lower().replace(' ', '_')}_{drug.lower()}_policy.txt"
            
            # Write to file
            with open(DATA_DIR / "policies" / filename, "w") as f:
                f.write(policy_text)
            
            policies.append({
                "drug": drug,
                "plan": plan,
                "filename": filename
            })
    
    return policies


def main():
    """Generate all synthetic data"""
    print("🏥 Generating synthetic healthcare data...")
    
    # Generate patients
    print("  → Generating 50 patients...")
    patients = generate_patients(50)
    with open(DATA_DIR / "patients.json", "w") as f:
        json.dump(patients, f, indent=2)
    print(f"     ✓ Created {len(patients)} patients")
    
    # Generate plans
    print("  → Generating insurance plans...")
    plans = generate_plans()
    with open(DATA_DIR / "plans.json", "w") as f:
        json.dump(plans, f, indent=2)
    print(f"     ✓ Created {len(plans)} plan/drug combinations")
    
    # Generate forms
    print("  → Generating PA form templates...")
    forms = generate_forms()
    with open(DATA_DIR / "forms.json", "w") as f:
        json.dump(forms, f, indent=2)
    print(f"     ✓ Created {len(forms)} form templates")
    
    # Generate policies
    print("  → Generating PA policy documents...")
    policies = generate_pa_policies()
    print(f"     ✓ Created {len(policies)} policy documents")
    
    print("\n✅ Synthetic data generation complete!")
    print(f"   Files created in: {DATA_DIR}/")
    print(f"   - patients.json ({len(patients)} patients)")
    print(f"   - plans.json ({len(plans)} entries)")
    print(f"   - forms.json ({len(forms)} templates)")
    print(f"   - policies/ ({len(policies)} documents)")


if __name__ == "__main__":
    main()
```

### Step 1.11: Validation Commands

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Generate synthetic data
python scripts/generate_synthetic_data.py

# Create .env from example
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# Start Docker services
docker-compose up -d

# Run FastAPI app
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/info
```

### Phase 1 Success Criteria ✅

- [ ] All directories created
- [ ] Dependencies installed without errors
- [ ] Synthetic data generated (patients.json, plans.json, forms.json, policy files)
- [ ] Docker services running (PostgreSQL, Redis)
- [ ] FastAPI app accessible at http://localhost:8000
- [ ] `/health` endpoint returns `{"status": "healthy"}`
- [ ] `/info` endpoint shows system information

---

## 📦 Phase 2: Benefit Verification Module

*Details to be added after Phase 1 completion*

---

## 📦 Phase 3: ChromaDB + Vector Retrieval

*Details to be added after Phase 2 completion*

---

## 📦 Phase 4: Clinical Qualification (LLM Integration)

*Details to be added after Phase 3 completion*

---

## 📦 Phase 5: Prior Authorization Generation

*Details to be added after Phase 4 completion*

---

## 📦 Phase 6: Orchestrator + End-to-End Flow

*Details to be added after Phase 5 completion*

---

## 📦 Phase 7: Testing, Evaluation & Documentation

*Details to be added after Phase 6 completion*

---

## 📝 Notes

- Each phase builds on the previous one
- Validate each phase before moving to the next
- Keep commits small and focused
- Test incrementally
- Document any issues or learnings

