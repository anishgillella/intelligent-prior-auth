# 🏥 Develop Health MVP Replica

> **AI-Powered Prior Authorization Automation Platform**  
> Built to demonstrate end-to-end understanding of healthcare AI workflows for Develop Health's AI Engineer role.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o-412991.svg)](https://openai.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](https://www.docker.com)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Phased Implementation Plan](#-phased-implementation-plan)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Core Modules](#-core-modules)
- [Data Flow](#-data-flow)
- [Setup & Installation](#-setup--installation)
- [API Documentation](#-api-documentation)
- [LLM Pipeline Design](#-llm-pipeline-design)
- [Evaluation & Quality Assurance](#-evaluation--quality-assurance)
- [Security & Compliance](#-security--compliance)
- [Future Enhancements](#-future-enhancements)
- [Interview Talking Points](#-interview-talking-points)

---

## 🎯 Overview

This MVP replicates the core AI automation workflow at Develop Health:

1. **Benefit Verification**: Determine if a drug is covered under patient's insurance plan
2. **Clinical Qualification**: Validate patient meets medical necessity criteria using LLM reasoning
3. **Prior Authorization**: Auto-generate PA forms with clinical justification narratives

**Key Differentiators:**
- ✅ Multi-step LLM orchestration with failure handling
- ✅ Hybrid approach: rule-based + AI reasoning (safety-first)
- ✅ Vector retrieval for insurance policy documents
- ✅ Confidence scoring and human-in-the-loop fallback
- ✅ Async processing for real-world scalability

---

## 🎯 Phased Implementation Plan

This project is built incrementally in **6 distinct phases** to ensure step-by-step learning and validation.

---

### **Phase 1: Foundation & Synthetic Data** ⏱️ ~2-3 hours | ✅ COMPLETE
**Goal**: Set up project skeleton, generate realistic synthetic healthcare data

**Deliverables**:
- ✅ Project structure (FastAPI app, config, data, modules)
- ✅ `pyproject.toml` with dependency management
- ✅ `.env.example` for OpenRouter credentials
- ✅ Synthetic data generation:
  - 20 realistic patients with demographics, diagnoses, labs, treatment history
  - 10 insurance plans with formularies and PA criteria
  - PA policy documents for vector indexing
- ✅ Docker Compose setup (PostgreSQL + Redis + Chroma)
- ✅ FastAPI skeleton with health checks

**Modules & Files**:
- `app/main.py` - FastAPI application entry point
- `app/core/config.py` - Settings management (Pydantic)
- `scripts/generate_synthetic_data.py` - Mock data generator
- `docker-compose.yml` - Service orchestration
- `pyproject.toml` - Dependency management with `uv`

**Endpoints**:
- `GET /` - API info
- `GET /health` - Health check
- `GET /info` - System information

**Validation**: 
```bash
python scripts/generate_synthetic_data.py
docker-compose up -d
curl http://localhost:8000/health
```

---

### **Phase 2: Benefit Verification (SQL-based)** ⏱️ ~2-3 hours | ✅ COMPLETE
**Goal**: Implement deterministic coverage lookup (rule-based, no LLM)

**What it does**:
- Looks up drug coverage by patient's insurance plan
- Determines if Prior Authorization is required
- Extracts coverage criteria from database
- Returns estimated patient cost

**Technology**:
- PostgreSQL database with insurance plan data
- SQLAlchemy ORM for queries
- Deterministic rule matching

**Modules & Files**:
- `app/modules/benefit_verification.py` - Core coverage logic
- `app/routes/benefit_verification.py` - API routes
- `app/data/db_models.py` - SQLAlchemy ORM models
- `app/data/database.py` - Database session management
- `tests/test_benefit_verification.py` - Unit tests

**Endpoints**:
```
POST /benefit-verification/check-coverage
```

**Request**:
```json
{
  "patient_id": "P001",
  "drug": "Ozempic"
}
```

**Response**:
```json
{
  "covered": true,
  "pa_required": true,
  "criteria": "BMI > 30 AND HbA1c > 7.5",
  "estimated_copay": 25.00,
  "status": "success"
}
```

**Validation**:
```bash
curl -X POST http://localhost:8000/benefit-verification/check-coverage \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P001", "drug": "Ozempic"}'
```

---

### **Phase 3: Policy Search (Vector Search / RAG Foundation)** ⏱️ ~3-4 hours | ✅ COMPLETE
**Goal**: Index PA policies in vector database for semantic retrieval

**What it does**:
- Chunks insurance policy documents into semantic units
- Indexes chunks in ChromaDB vector database (local persistence)
- Retrieves relevant policies using vector similarity search
- Supports RAG (Retrieval-Augmented Generation) for Phase 4

**Technology**:
- ChromaDB - local persistent vector database
- Embeddings - semantic text representation
- Vector similarity search (cosine distance)
- 36 policy documents indexed

**Modules & Files**:
- `app/data/vector_index.py` - ChromaDB management
- `app/routes/policy_search.py` - API routes
- `scripts/build_vector_index.py` - Indexing script
- `tests/test_vector_search.py` - Unit tests

**Endpoints**:
```
POST /policy-search/search
POST /policy-search/search/drug/{drug}
POST /policy-search/search/plan/{plan}
```

**Request**:
```json
{
  "query": "Ozempic BMI criteria",
  "top_k": 3
}
```

**Response**:
```json
{
  "query": "Ozempic BMI criteria",
  "results": [
    {
      "id": "aetna_gold_ozempic_chunk_0",
      "text": "Coverage criteria: BMI > 30 AND HbA1c > 7.5...",
      "similarity": 0.92,
      "metadata": {
        "plan": "Aetna Gold",
        "drug": "Ozempic",
        "source": "aetna_gold_ozempic_policy.txt"
      }
    }
  ],
  "status": "success"
}
```

**Validation**:
```bash
python scripts/build_vector_index.py
curl -X POST http://localhost:8000/policy-search/search \
  -d '{"query": "Ozempic criteria", "top_k": 3}'
```

---

### **Phase 4: Clinical Qualification (LLM + RAG)** ⏱️ ~4-5 hours | ✅ COMPLETE
**Goal**: Use LLM to verify patient meets clinical criteria, with policy context from Phase 3

**What it does**:
- Retrieves relevant policies using Phase 3 vector search
- Formats patient data + policy criteria + labs into LLM prompt
- LLM analyzes: Does patient meet ALL criteria?
- Returns: binary decision + confidence score + clinical reasoning
- **RAG Pattern**: Retrieved policies → LLM context → improved reasoning

**Technology**:
- OpenRouter API (GPT-4o-mini for cost/speed)
- LLM reasoning with structured prompts
- Confidence scoring (0-1)
- Retry logic with exponential backoff
- Token counting and cost tracking

**Modules & Files**:
- `app/core/llm_client.py` - OpenRouter API client wrapper
- `app/prompts/clinical_qualification.py` - System & user prompts
- `app/modules/clinical_qualification.py` - Clinical eligibility logic
- `app/routes/clinical_qualification.py` - API routes
- `tests/test_clinical_qualification.py` - Unit tests

**Endpoints**:
```
POST /clinical-qualification/check-eligibility
```

**Request**:
```json
{
  "patient_id": "P001",
  "drug": "Ozempic",
  "policy_criteria": "BMI > 30 AND HbA1c > 7.5",
  "use_rag": true
}
```

**Response**:
```json
{
  "patient_id": "P001",
  "drug": "Ozempic",
  "meets_criteria": false,
  "confidence_score": 0.85,
  "recommendation": "DENY",
  "clinical_justification": "Patient's BMI is 25.1 kg/m² (below required >30), though HbA1c is 9.7% (above required >7.5)...",
  "reasoning_details": {
    "criteria_analysis": {
      "requirement_1": {
        "met": false,
        "evidence": "BMI is 25.1 kg/m², below threshold >30"
      },
      "requirement_2": {
        "met": true,
        "evidence": "HbA1c is 9.7%, above threshold >7.5"
      }
    }
  },
  "llm_metadata": {
    "model": "openai/gpt-4o-mini",
    "latency_ms": 4251.88,
    "tokens_used": {"input": 788, "output": 267, "total": 1055},
    "cost": 0.0
  }
}
```

**LLM Pipeline**:
1. ✅ Retrieve policy context (Phase 3 vector search)
2. ✅ Format patient clinical history
3. ✅ Build RAG-enhanced prompt with policy context
4. ✅ Call LLM with structured prompt
5. ✅ Parse LLM response into structured output
6. ✅ Calculate confidence score
7. ✅ Track costs and latency

**Validation**:
```bash
curl -X POST http://localhost:8000/clinical-qualification/check-eligibility \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "drug": "Ozempic",
    "policy_criteria": "BMI > 30 AND HbA1c > 7.5",
    "use_rag": true
  }'
```

---

### **Phase 5: PA Form Generation (LLM Narratives)** ⏱️ ~3-4 hours | ✅ COMPLETE
**Goal**: Generate clinical justification narratives and package into PA forms

**What it does**:
- Takes Phase 4 eligibility result as input
- Uses LLM to generate professional clinical narrative (~300-400 words)
- Packages narrative into standardized PA form
- Generates both JSON and Markdown formats
- Forms ready for insurance submission

**Technology**:
- LLM (GPT-4o-mini) for narrative generation
- Professional medical language templates
- Structured form generation
- JSON + Markdown outputs

**Modules & Files**:
- `app/prompts/prior_authorization.py` - PA prompt templates
- `app/modules/prior_authorization.py` - PA form generation logic
- `app/routes/prior_authorization.py` - API routes

**Endpoints**:
```
POST /prior-authorization/generate-form
POST /prior-authorization/generate-form-markdown
```

**Request**:
```json
{
  "patient_id": "P001",
  "drug": "Ozempic",
  "policy_criteria": "BMI > 30 AND HbA1c > 7.5",
  "use_rag": true,
  "provider_name": "Dr. Sarah Johnson",
  "npi": "1234567890"
}
```

**Response (JSON)**:
```json
{
  "form_id": "PA_20251018_P001_OZEMPIC",
  "patient_name": "Michael Miller",
  "drug_name": "Ozempic",
  "clinical_narrative": "[LLM-generated 400-word professional narrative]",
  "submission_date": "2025-10-18T15:10:08.549803",
  "confidence_score": 0.85,
  "recommendation": "DENY",
  "llm_metadata": {
    "model": "openai/gpt-4o-mini",
    "latency_ms": 3400,
    "tokens_used": {"input": 450, "output": 267, "total": 717},
    "cost": 0.0
  }
}
```

**Response (Markdown)**:
```markdown
# PRIOR AUTHORIZATION REQUEST

## Form Information
- **Form ID**: PA_20251018_P001_OZEMPIC
- **Submission Date**: 2025-10-18T15:10:08

## Patient Information
- **Name**: Michael Miller
- **Member ID**: MEM9275666116
- **Insurance Plan**: Anthem Blue Cross

## Clinical Information
- **Requested Drug**: Ozempic
- **Dosage**: As prescribed
- **Primary Diagnosis**: Type 2 Diabetes (E11.9)

## Clinical Justification

[LLM-generated clinical narrative here...]
```

**Validation**:
```bash
curl -X POST http://localhost:8000/prior-authorization/generate-form \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "drug": "Ozempic",
    "policy_criteria": "BMI > 30 AND HbA1c > 7.5",
    "use_rag": true,
    "provider_name": "Dr. Sarah Johnson"
  }'
```

---

### **Phase 6: Unified Orchestrator (End-to-End Pipeline)** ⏱️ ~2-3 hours | ✅ COMPLETE
**Goal**: Chain all phases (2-5) into a single API endpoint for complete workflow

**What it does**:
- **Single endpoint** that orchestrates ALL phases
- Phase 2: Check coverage
- Phase 3: Search relevant policies
- Phase 4: Check clinical eligibility
- Phase 5: Generate PA form
- Returns complete workflow with all outputs
- Includes summary and recommendation

**Technology**:
- Orchestrator pattern (chain of operations)
- Error handling and fallback logic
- Workflow ID tracking
- Human-readable summary generation

**Modules & Files**:
- `app/modules/orchestrator.py` - Core orchestration logic
- `app/routes/orchestrator.py` - API routes
- Integration in `app/main.py`

**Endpoints**:
```
POST /orchestration/process-prescription
```

**Request**:
```json
{
  "patient_id": "P001",
  "drug": "Ozempic",
  "provider_name": "Dr. Sarah Johnson",
  "npi": "1234567890"
}
```

**Response**:
```json
{
  "workflow_id": "WF_20251018151444_P001_OZEMPIC",
  "status": "completed",
  "result": "success",
  "recommendation": "APPROVE",
  "timestamp": "2025-10-18T15:15:24.859180",
  "patient": {
    "id": "P001",
    "name": "Michael Miller",
    "age": 75,
    "insurance_plan": "Anthem Blue Cross"
  },
  "summary": "Recommendation: APPROVE\nCoverage: Covered (No PA Required)\nEligibility: Meets criteria (Confidence: 95%)\nClinical Justification: The patient is a 75-year-old male...",
  "phases": {
    "phase2_coverage": {
      "covered": true,
      "pa_required": false,
      "criteria": null,
      "status": "success"
    },
    "phase3_policy_search": {
      "drug": "Ozempic",
      "policies_found": 3,
      "results": [...],
      "status": "success"
    },
    "phase4_eligibility": {
      "meets_criteria": true,
      "confidence_score": 0.95,
      "clinical_justification": "The patient is...",
      "recommendation": "APPROVE",
      "status": "success"
    },
    "phase5_pa_form": {
      "form_id": "PA_20251018_P001_OZEMPIC",
      "status": "ready_for_submission",
      "has_clinical_narrative": true,
      "full_form": {...}
    }
  }
}
```

**Workflow Architecture**:
```
Patient Request
      ↓
Phase 2: Coverage Check (SQL)
      ↓
[If not covered → DENY]
      ↓
Phase 3: Policy Search (Vector DB)
      ↓
Phase 4: LLM Clinical Eligibility (RAG)
      ↓
Phase 5: PA Form Generation (LLM)
      ↓
Complete Workflow Response
```

**Validation**:
```bash
curl -X POST http://localhost:8000/orchestration/process-prescription \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "drug": "Ozempic",
    "provider_name": "Dr. Sarah Johnson",
    "npi": "1234567890"
  }'
```

---

## 📊 Complete Phase Summary Table

| Phase | Technology | Input | Output | Endpoints | Status |
|-------|-----------|-------|--------|-----------|--------|
| **1** | FastAPI, PostgreSQL, Docker | Synthetic data config | Data files, DB schema | `/health`, `/info` | ✅ |
| **2** | SQLAlchemy, SQL | patient_id, drug | coverage, pa_required, criteria | `/benefit-verification/check-coverage` | ✅ |
| **3** | ChromaDB, Embeddings | query string | retrieved policies, similarity | `/policy-search/search`, `/policy-search/search/drug/{drug}` | ✅ |
| **4** | LLM (GPT-4o-mini), RAG | patient, drug, criteria | eligibility decision, confidence | `/clinical-qualification/check-eligibility` | ✅ |
| **5** | LLM (GPT-4o-mini) | eligibility_result | PA form, narrative | `/prior-authorization/generate-form`, `/prior-authorization/generate-form-markdown` | ✅ |
| **6** | Orchestration | patient_id, drug | complete workflow | `/orchestration/process-prescription` | ✅ COMPLETE |

---

## 🏗️ System Architecture

```
                 ┌────────────────────────────────┐
                 │        API Gateway             │
                 │      (FastAPI Backend)         │
                 │   POST /process-prescription   │
                 └────────────────────────────────┘
                                │
             ┌──────────────────┼──────────────────┐
             │                  │                  │
             ▼                  ▼                  ▼
┌──────────────────┐  ┌──────────────────┐  ┌─────────────────────┐
│ BenefitVerifier  │  │ ClinicalChecker  │  │ PriorAuthGenerator  │
│                  │  │                  │  │                     │
│ • Plan lookup    │  │ • Policy search  │  │ • Form selection    │
│ • Coverage rules │  │ • LLM reasoning  │  │ • LLM generation    │
│ • PA flag        │  │ • Confidence     │  │ • Quality eval      │
└──────────────────┘  └──────────────────┘  └─────────────────────┘
             │                  │                  │
             └──────────┬───────┴──────────┬───────┘
                        ▼                  ▼
                 ┌─────────────┐     ┌───────────────┐
                 │ Vector Store│     │ PostgreSQL DB │
                 │ (ChromaDB)  │     │ Patients/Plans│
                 │ PA Policies │     │ Audit Logs    │
                 └─────────────┘     └───────────────┘
```

### Design Principles

1. **Fail-Safe First**: Deterministic rules before LLM calls
2. **Observable**: Every LLM call logged with prompt/response/latency
3. **Testable**: Each module independently unit-testable
4. **Scalable**: Async orchestration via Celery for production readiness

---

## ⚙️ Tech Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| **Backend** | FastAPI | Async-first, auto OpenAPI docs, Pydantic validation |
| **LLM Orchestration** | LangChain | Prompt templates, chain management, retrieval |
| **LLM Provider** | OpenRouter (GPT-4o, Claude, Llama) | Flexible multi-model routing, cost optimization |
| **Vector DB** | ChromaDB | Semantic search for PA policy criteria |
| **Queue** | Celery + Redis | Async PA submission, status checks |
| **Database** | PostgreSQL | Structured patient/plan data, audit logs |
| **PDF Generation** | ReportLab | Professional PA form PDFs |
| **Deployment** | Docker Compose | Reproducible multi-service environment |
| **Monitoring** | Prometheus + Grafana | LLM latency, cost, error tracking (optional) |

---

## 📁 Project Structure

```
develop-health-mvp/
│
├── app/
│   ├── main.py                      # FastAPI app entrypoint
│   │
│   ├── core/
│   │   ├── config.py                # Environment config (OpenAI keys, DB URLs)
│   │   ├── logger.py                # Structured logging (JSON format)
│   │   └── security.py              # PHI redaction utilities
│   │
│   ├── modules/
│   │   ├── benefit_verification.py  # Step 1: Coverage + PA requirement check
│   │   ├── clinical_qualification.py # Step 2: LLM-based eligibility validation
│   │   ├── prior_authorization.py   # Step 3: Form generation + submission
│   │   └── orchestrator.py          # Unified workflow coordinator
│   │
│   ├── data/
│   │   ├── mock_loader.py           # Load mock JSON data
│   │   ├── vector_index.py          # ChromaDB index for PA policies
│   │   └── models.py                # Pydantic models for type safety
│   │
│   ├── utils/
│   │   ├── pdf_generator.py         # PA form PDF creation
│   │   ├── evaluator.py             # LLM output quality scoring
│   │   └── retry.py                 # Exponential backoff for API calls
│   │
│   ├── routes/
│   │   └── api.py                   # REST API endpoints
│   │
│   └── tests/
│       ├── test_benefit_verification.py
│       ├── test_clinical_qualification.py
│       └── test_prior_authorization.py
│
├── mock_data/
│   ├── plans.json                   # Insurance plan formularies
│   ├── patients.json                # Mock patient demographics + clinical data
│   ├── forms.json                   # PA form templates by plan/drug
│   └── policies/                    # Mock PA policy PDFs (for vector indexing)
│       ├── aetna_ozempic_criteria.txt
│       └── bcbs_trulicity_criteria.txt
│
├── docker-compose.yml               # Multi-container orchestration
├── Dockerfile                       # Python app container
├── requirements.txt                 # Python dependencies
├── .env.example                     # Template for secrets
├── pytest.ini                       # Test configuration
└── README.md                        # This file
```

---

## 🧩 Core Modules

### 1️⃣ Benefit Verification (`benefit_verification.py`)

**Purpose**: Determine coverage and PA requirements using deterministic rules.

**Algorithm**:
```python
def check_coverage(patient, drug):
    plan = patient.insurance_plan
    rule = lookup_plan_rule(plan, drug)  # DB or vector search
    
    return {
        "covered": bool,
        "pa_required": bool,
        "criteria": str,  # Medical necessity requirements if PA needed
        "estimated_cost": float
    }
```

**Why No LLM Here?**  
Coverage is rule-based (formulary lookup) - no need for probabilistic reasoning. Saves cost and ensures deterministic results.

---

### 2️⃣ Clinical Qualification (`clinical_qualification.py`)

**Purpose**: Validate patient meets medical necessity criteria using LLM + retrieval.

**Algorithm**:
```python
def check_eligibility(patient, criteria):
    # Step 1: Retrieve detailed policy from vector DB
    policy_context = vector_search(criteria, top_k=3)
    
    # Step 2: LLM reasoning with structured output
    prompt = f"""
    Policy: {policy_context}
    Patient: {patient}
    
    Does patient meet criteria? Respond JSON:
    {{"meets_criteria": bool, "reasoning": str, "confidence": 0-1}}
    """
    
    response = call_llm(prompt, temperature=0.1)
    
    # Step 3: Confidence threshold (if < 0.8, route to human review)
    if response.confidence < 0.8:
        route_to_human_queue(patient, criteria)
        
    return response
```

**Why LLM Here?**  
Medical necessity criteria are complex, nuanced, and require reasoning over clinical data (e.g., "BMI > 30 AND failed metformin for 3+ months").

---

### 3️⃣ Prior Authorization (`prior_authorization.py`)

**Purpose**: Generate clinical justification narrative and fill PA form.

**Algorithm**:
```python
def generate_pa_form(patient, drug, plan):
    # Step 1: Select form template
    template = get_form_template(plan, drug)
    
    # Step 2: Generate clinical narrative
    prompt = f"""
    Write a clinical justification for {drug} for:
    
    Patient: {patient.demographics}
    Diagnosis: {patient.diagnoses}
    Labs: {patient.labs}
    Treatment History: {patient.treatment_history}
    
    Requirements: Professional tone, 150-200 words, cite diagnosis codes.
    """
    
    narrative = call_llm(prompt, temperature=0.3)
    
    # Step 3: Quality evaluation (check for hallucinations)
    quality_score = evaluate_narrative(narrative, patient)
    if quality_score < 0.9:
        regenerate_with_stricter_prompt()
    
    # Step 4: Fill form and generate PDF
    form_data = {
        "patient_name": patient.name,
        "drug": drug,
        "justification": narrative,
        "icd10_codes": extract_codes(patient.diagnoses)
    }
    
    pdf_path = generate_pdf(template, form_data)
    
    return {"status": "submitted", "pdf": pdf_path}
```

**Why Evaluation?**  
Healthcare LLM outputs must be factually accurate. The evaluator checks:
- No hallucinated diagnoses/labs
- Correct ICD-10 code mapping
- No contradictory statements

---

### 4️⃣ Orchestrator (`orchestrator.py`)

**Purpose**: Coordinate multi-step workflow with failure handling.

**Workflow**:
```python
def process_prescription(patient, drug):
    # Step 1: Benefit Verification
    coverage = check_coverage(patient, drug)
    if not coverage.covered:
        return {"status": "not_covered", "reason": "Drug not in formulary"}
    
    if not coverage.pa_required:
        return {"status": "approved", "reason": "No PA required"}
    
    # Step 2: Clinical Qualification
    eligibility = check_eligibility(patient, coverage.criteria)
    if not eligibility.meets_criteria:
        return {"status": "denied", "reason": eligibility.reasoning}
    
    # Step 3: PA Generation
    pa_result = generate_pa_form(patient, drug, patient.insurance_plan)
    
    # Step 4: Async submission (Celery task)
    task_id = submit_pa_async.delay(pa_result.pdf)
    
    return {
        "status": "pa_submitted",
        "task_id": task_id,
        "estimated_completion": "2-5 business days"
    }
```

---

## 🔄 Data Flow

```
User Request
    ↓
┌─────────────────────────────────────────┐
│ POST /process-prescription              │
│ Body: {patient, drug}                   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Orchestrator.process_prescription()     │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 1: BenefitVerifier                 │
│ → Query: plans.json or PostgreSQL       │
│ → Output: {covered, pa_required, ...}   │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 2: ClinicalChecker                 │
│ → Vector Search: ChromaDB (policies)    │
│ → LLM Call: GPT-4o reasoning            │
│ → Output: {meets_criteria, confidence}  │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Step 3: PriorAuthGenerator              │
│ → LLM Call: Generate narrative          │
│ → Evaluation: Quality check             │
│ → PDF Generation: ReportLab             │
│ → Output: {pdf_path, status}            │
└─────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────┐
│ Celery Task: submit_pa_async()          │
│ → Mock submission to payer portal       │
│ → Log to PostgreSQL audit trail         │
└─────────────────────────────────────────┘
    ↓
API Response
```

---

## 🚀 Setup & Installation

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- OpenRouter API Key ([get one here](https://openrouter.ai/keys))
  - Free tier available with access to multiple models (GPT-4o, Claude, Llama, etc.)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/develop-health-mvp.git
cd develop-health-mvp

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env and add:
#   OPENROUTER_API_KEY=your_key_here
#   OPENROUTER_MODEL=openai/gpt-4o  # or anthropic/claude-3.5-sonnet, meta-llama/llama-3.1-70b-instruct

# 5. Initialize mock data
python scripts/init_mock_data.py  # Loads JSON + builds ChromaDB index

# 6. Run database migrations (PostgreSQL)
alembic upgrade head

# 7. Start services
docker-compose up -d  # Starts PostgreSQL, Redis, Celery worker

# 8. Run FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points

- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Health Check**: http://localhost:8000/health
- **Prometheus Metrics**: http://localhost:9090 (if monitoring enabled)

---

## 📡 API Documentation

### `POST /process-prescription`

**Request**:
```json
{
  "patient": {
    "patient_id": "P123",
    "name": "John Doe",
    "age": 42,
    "BMI": 33.1,
    "diagnoses": ["E11.9"],  // ICD-10 for Type 2 Diabetes
    "labs": {
      "HbA1c": 8.5,
      "fasting_glucose": 180
    },
    "treatment_history": [
      {"drug": "Metformin", "duration_months": 6, "outcome": "Inadequate response"}
    ],
    "insurance_plan": "Aetna Gold"
  },
  "drug": "Ozempic"
}
```

**Response (Success - PA Required)**:
```json
{
  "status": "pa_submitted",
  "task_id": "celery-task-uuid-1234",
  "details": {
    "coverage": {
      "covered": true,
      "pa_required": true,
      "estimated_patient_cost": 25.00
    },
    "eligibility": {
      "meets_criteria": true,
      "confidence": 0.94,
      "reasoning": "Patient meets criteria: BMI > 30 (33.1), HbA1c > 7.5 (8.5), failed first-line therapy (Metformin 6 months)"
    },
    "pa_form": {
      "pdf_path": "/tmp/pa_forms/P123_ozempic_20250118.pdf",
      "submitted_at": "2025-01-18T14:32:10Z"
    }
  },
  "estimated_completion": "2-5 business days"
}
```

**Response (Not Covered)**:
```json
{
  "status": "not_covered",
  "reason": "Ozempic not in formulary for Aetna Gold plan",
  "alternatives": ["Trulicity", "Victoza"]
}
```

### `GET /pa-status/{task_id}`

Check PA submission status (async tracking).

**Response**:
```json
{
  "task_id": "celery-task-uuid-1234",
  "status": "approved",
  "updated_at": "2025-01-20T09:15:00Z",
  "approval_details": {
    "authorization_number": "AUTH-987654",
    "valid_until": "2026-01-20"
  }
}
```

---

## 🧠 LLM Pipeline Design

### Prompt Engineering Strategy

1. **System Prompts**: Role definition for medical context
2. **Few-Shot Examples**: Include 2-3 reference PA narratives
3. **Structured Output**: JSON schema enforcement via function calling
4. **Temperature Control**: 
   - 0.1 for clinical eligibility (deterministic)
   - 0.3 for narrative generation (slight creativity for fluency)

### Example Prompt (Clinical Qualification)

```python
SYSTEM_PROMPT = """
You are a medical utilization review specialist evaluating prior authorization requests.
Analyze patient clinical data against insurance policy criteria with precision.
Always cite specific data points (lab values, diagnosis codes, treatment history).
"""

USER_PROMPT = """
Insurance Policy Criteria:
{policy_text}

Patient Clinical Data:
- Age: {age}
- Diagnoses: {diagnoses}
- Labs: {labs}
- Treatment History: {treatment_history}

Task: Determine if patient meets medical necessity criteria.

Output JSON:
{
  "meets_criteria": boolean,
  "reasoning": "detailed explanation citing specific data",
  "confidence": 0.0-1.0,
  "missing_data": ["list any gaps in patient data"]
}
"""
```

### LLM Call Wrapper (with Retry & Logging)

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def call_llm(prompt, temperature=0.1, max_tokens=500):
    start_time = time.time()
    
    # OpenRouter API (OpenAI-compatible endpoint)
    response = openai.ChatCompletion.create(
        model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o"),
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1"
    )
    
    latency = time.time() - start_time
    
    # Log to PostgreSQL audit table
    log_llm_call(
        prompt=prompt,
        response=response.choices[0].message.content,
        model=os.getenv("OPENROUTER_MODEL"),
        latency=latency,
        tokens_used=response.usage.total_tokens,
        cost=calculate_cost(response.usage)
    )
    
    return response.choices[0].message.content
```

---

## 🎯 Evaluation & Quality Assurance

### LLM Output Evaluation Pipeline

**Goal**: Catch hallucinations and ensure clinical accuracy.

```python
def evaluate_narrative(narrative: str, patient: dict) -> float:
    """
    Returns quality score 0.0-1.0
    """
    checks = [
        check_diagnosis_hallucination(narrative, patient.diagnoses),
        check_lab_value_accuracy(narrative, patient.labs),
        check_treatment_history_consistency(narrative, patient.treatment_history),
        check_medical_terminology(narrative),  # No jargon errors
        check_icd10_code_validity(narrative)
    ]
    
    return sum(checks) / len(checks)

def check_diagnosis_hallucination(narrative, diagnoses):
    """Ensure narrative doesn't mention diagnoses not in patient record"""
    mentioned_diagnoses = extract_diagnoses_from_text(narrative)
    return 1.0 if mentioned_diagnoses.issubset(diagnoses) else 0.0
```

### Unit Testing for LLM Pipelines

```python
# tests/test_clinical_qualification.py
def test_eligibility_check_with_qualified_patient():
    patient = load_mock_patient("qualified_ozempic.json")
    criteria = "BMI > 30 AND HbA1c > 7.5"
    
    result = check_eligibility(patient, criteria)
    
    assert result["meets_criteria"] == True
    assert result["confidence"] > 0.8
    assert "BMI" in result["reasoning"]
    assert "HbA1c" in result["reasoning"]

def test_eligibility_check_confidence_threshold():
    """If confidence < 0.8, should route to human review"""
    patient = load_mock_patient("edge_case.json")
    criteria = "Complex multi-factor criteria..."
    
    with patch('app.modules.clinical_qualification.route_to_human_queue') as mock_queue:
        result = check_eligibility(patient, criteria)
        
        if result["confidence"] < 0.8:
            mock_queue.assert_called_once()
```

---

## 🔒 Security & Compliance

### PHI (Protected Health Information) Handling

1. **Data Retention**: 
   - OpenRouter offers zero-retention mode for HIPAA compliance
   - ChromaDB data stored locally (never leaves your infrastructure)
   - Local logs redact PII (patient names, addresses)

2. **Access Control**:
   - API key authentication for all endpoints
   - Role-based access (not implemented in MVP, but production-ready pattern)

3. **Audit Trail**:
   - Every LLM call logged to PostgreSQL with timestamp, user, input/output
   - Immutable log entries for compliance

### Example PHI Redaction

```python
def redact_phi(text: str) -> str:
    """Redact patient names, DOB, SSN from logs"""
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX', text)  # SSN
    text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', 'XX/XX/XXXX', text)  # DOB
    # Add more patterns...
    return text
```

### HIPAA Considerations for Production

- Encrypt data at rest (PostgreSQL encryption)
- TLS 1.3 for API traffic
- BAA (Business Associate Agreement) with OpenRouter/LLM providers
- ChromaDB local deployment (no external data transfer)
- Annual security audits

---

## 🚀 Future Enhancements

### Phase 2: Advanced Features

1. **Multi-Modal AI**:
   - OCR for parsing existing PA forms (using GPT-4 Vision)
   - Voice AI for calling insurance companies (like Develop Health's actual product)

2. **Reinforcement Learning**:
   - Train on approval/denial outcomes to optimize narrative generation
   - A/B test different prompt templates

3. **Real-Time Collaboration**:
   - WebSocket endpoint for live PA status updates
   - Slack/Teams integration for human review notifications

4. **Advanced Retrieval**:
   - RAG (Retrieval-Augmented Generation) with multiple vector stores:
     - Insurance policy database
     - FDA drug labels
     - Clinical practice guidelines

5. **Cost Optimization**:
   - Cache common LLM responses (e.g., same drug + criteria combo)
   - Use GPT-4o-mini for simple tasks, GPT-4o for complex reasoning

6. **Analytics Dashboard**:
   - Approval rate by drug/plan
   - Average PA turnaround time
   - LLM cost per PA ($0.50-$2.00 estimated)

---

## 💬 Interview Talking Points

### Technical Deep Dives

**Q: How do you handle LLM hallucinations in a healthcare context?**

A: Multi-layered approach:
1. **Prompt Engineering**: Strict instructions to cite only provided data
2. **Structured Outputs**: JSON schema enforcement prevents free-form errors
3. **Post-Generation Validation**: Evaluator checks narrative against source data
4. **Confidence Thresholds**: Route low-confidence outputs to human review
5. **Audit Trail**: Every LLM call logged for retrospective analysis

**Q: How would you scale this to handle 10,000 PAs/day?**

A: 
1. **Async Processing**: Celery workers across multiple machines
2. **Rate Limiting**: Respect OpenAI rate limits (use queue backpressure)
3. **Caching**: Redis cache for common plan/drug lookups
4. **Database Optimization**: Index on (plan, drug) for fast coverage checks
5. **Horizontal Scaling**: Stateless API allows easy Kubernetes deployment

**Q: How do you measure success for an AI-generated PA form?**

A: Key metrics:
1. **Approval Rate**: % of AI-generated PAs approved (target: match human baseline)
2. **Turnaround Time**: Days from submission to decision (faster = better)
3. **Edit Distance**: How much do human reviewers modify AI narratives?
4. **Cost per PA**: OpenAI API cost + compute (target: < $2.00)
5. **Denial Reasons**: Track why PAs get denied (improve prompts iteratively)

---

## 📚 References

- [Develop Health Website](https://develophealth.com)
- [OpenRouter Documentation](https://openrouter.ai/docs) - Multi-model LLM API
- [ChromaDB Documentation](https://docs.trychroma.com/) - Local vector database
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/index.html)
- [ICD-10 Code Reference](https://www.icd10data.com/)
- [Synthetic Healthcare Data Generation](https://synthea.mitre.org/)

---

## 📝 License

MIT License - Educational/Portfolio Project

---

## 👤 Author

**Anish Gillella**  
Preparing for AI Engineer role at Develop Health

Built with ❤️ to demonstrate end-to-end AI engineering skills in healthcare automation.

---

## 🤝 Acknowledgments

- Develop Health team for building innovative healthcare AI solutions
- OpenAI for GPT-4o API access
- Healthcare professionals who inspired this workflow design

