# 🚀 Complete Setup Guide - Running Everything

This guide will help you get the entire Intelligent Prior Authorization platform running with both backend and frontend.

## Prerequisites

- Docker & Docker Compose (easiest)
- OR Node.js 18+, Python 3.10+, PostgreSQL 16, Redis 7

## Option 1: Docker Compose (Recommended - Easiest)

### Step 1: Set Up Environment

```bash
# Navigate to project root
cd /Users/anishgillella/Desktop/Stuff/Projects/Develop\ Health/Replica

# Copy example env file and add your OpenRouter API key
cp .env.example .env

# Edit .env and add:
# OPENROUTER_API_KEY=your_key_here
```

### Step 2: Start All Services

```bash
# Build and start everything (backend + frontend + database + redis)
docker-compose up --build

# First time might take 5-10 minutes to build images
```

### Step 3: Access the Application

Once everything is running:

- **Frontend**: http://localhost:3000 🎨
- **Backend API**: http://localhost:8000 🔧
- **API Docs**: http://localhost:8000/docs 📚
- **ReDoc**: http://localhost:8000/redoc 📖

### Step 4: Initialize Data (First Time Only)

In a new terminal:

```bash
# Connect to the backend container
docker exec develop_health_backend bash

# Inside the container, run initialization scripts
python scripts/generate_synthetic_data.py
python scripts/import_data_to_db.py
python scripts/build_vector_index.py

exit
```

### That's it! 🎉

Visit http://localhost:3000 and start processing prescriptions!

---

## Option 2: Manual Setup (Local Development)

### Prerequisites

```bash
# Check versions
python --version  # >= 3.10
node --version    # >= 18
npm --version     # >= 9

# Make sure PostgreSQL and Redis are running
# PostgreSQL: localhost:5432
# Redis: localhost:6379
```

### Backend Setup

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file
cp .env.example .env
# Edit .env and add your OPENROUTER_API_KEY

# 4. Generate synthetic data
python scripts/generate_synthetic_data.py

# 5. Import data into database
python scripts/import_data_to_db.py

# 6. Build vector index
python scripts/build_vector_index.py

# 7. Start backend server
uvicorn app.main:app --reload
# Backend running at http://localhost:8000
```

### Frontend Setup (New Terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env file
cat > .env << 'ENVEOF'
VITE_API_URL=http://localhost:8000
ENVEOF

# Start development server
npm run dev
# Frontend running at http://localhost:3000
```

Visit http://localhost:3000 in your browser!

---

## Testing the System

### Quick Test: End-to-End Workflow

Go to **"End-to-End Workflow"** tab in frontend:

1. **Patient**: P001
2. **Drug**: Ozempic
3. **Provider**: Dr. Smith
4. **NPI**: 1234567890
5. Click **"Process Prescription"**

Expected result: Shows all phases executing with recommendations.

### Test Individual Phases

#### Phase 2: Coverage Check
- Tab: "Phase 2: Coverage Check"
- Patient ID: P001
- Drug: Ozempic
- Should show: Covered ✓

#### Phase 3: Policy Search
- Tab: "Phase 3: Policy Search"
- Drug: Ozempic
- Should find: 3+ relevant policies

#### Phase 4: Clinical Eligibility
- Tab: "Phase 4: Eligibility"
- Patient: P001
- Drug: Ozempic
- Use RAG: ✓
- Should show: Meets criteria with confidence score

#### Phase 5: PA Form Generation
- Tab: "Phase 5: PA Form"
- Patient: P001
- Drug: Ozempic
- Should generate: JSON form + Markdown form

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (React + Vite)                                     │
│  http://localhost:3000                                       │
│                                                               │
│  - Dashboard with 5 tabs                                     │
│  - Beautiful UI with Tailwind CSS                            │
│  - Real-time results visualization                           │
│  - Workflow timeline                                         │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTP/REST
┌─────────────────────────────────────────────────────────────┐
│  Backend (FastAPI)                                           │
│  http://localhost:8000                                       │
│                                                               │
│  ├─ Phase 2: Benefit Verification                           │
│  ├─ Phase 3: Policy Search (Vector DB)                      │
│  ├─ Phase 4: Clinical Qualification (LLM)                   │
│  ├─ Phase 5: PA Form Generation                             │
│  └─ Phase 6: Orchestrator (End-to-End)                      │
└─────────────────────────────────────────────────────────────┘
          ↓              ↓              ↓
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │PostgreSQL│   │ ChromaDB │   │ OpenAI  │
    │ Database │   │Vectors   │   │ LLM     │
    └──────────┘   └──────────┘   └──────────┘
```

---

## 📊 Project Structure

```
intelligent-prior-auth/
├── frontend/                    # React Dashboard
│   ├── src/
│   │   ├── api/                # API client & hooks
│   │   ├── components/         # React components
│   │   ├── App.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
│
├── app/                         # FastAPI Backend
│   ├── main.py                 # Entry point
│   ├── modules/                # Business logic
│   ├── routes/                 # API endpoints
│   ├── data/                   # Database & vectors
│   ├── core/                   # Config & logging
│   └── prompts/                # LLM prompts
│
├── scripts/
│   ├── generate_synthetic_data.py
│   ├── import_data_to_db.py
│   └── build_vector_index.py
│
├── mock_data/                  # Synthetic test data
├── chroma_db/                  # Vector database
├── docker-compose.yml          # Multi-container setup
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

---

## 🔑 Key Endpoints

### Health Check
```
GET /health
Response: { status: "healthy" }
```

### Benefit Verification (Phase 2)
```
POST /benefit-verification/check-coverage
Body: { patient_id: "P001", drug: "Ozempic" }
Response: { covered: true, pa_required: true, criteria: "..." }
```

### Policy Search (Phase 3)
```
POST /policy-search/search
Body: { drug: "Ozempic", top_k: 3 }
Response: { policies_found: 3, results: [...] }
```

### Clinical Qualification (Phase 4)
```
POST /clinical-qualification/check-eligibility
Body: { 
  patient_id: "P001", 
  drug: "Ozempic",
  policy_criteria: "...",
  use_rag: true 
}
Response: { 
  meets_criteria: true, 
  confidence_score: 0.85,
  clinical_justification: "..."
}
```

### PA Form (Phase 5)
```
POST /prior-authorization/generate-form
Body: { patient_id: "P001", drug: "Ozempic", ... }
Response: { form_id: "PA_...", clinical_narrative: "..." }
```

### End-to-End (Phase 6)
```
POST /orchestration/process-prescription
Body: { patient_id: "P001", drug: "Ozempic", ... }
Response: {
  workflow_id: "WF_...",
  phases: { phase2: {...}, phase3: {...}, ... },
  recommendation: "APPROVE"
}
```

---

## 🧪 Database

### PostgreSQL (localhost:5432)

```sql
-- Connect to database
psql -h localhost -U postgres -d develop_health_mvp

-- View patients
SELECT * FROM patient;

-- View forms
SELECT * FROM pa_form;

-- View logs
SELECT * FROM llm_log;
```

**Credentials:**
- User: `postgres`
- Password: `postgres`
- Database: `develop_health_mvp`

### ChromaDB (localhost)

Vector embeddings stored at: `./chroma_db/`

Contains policy documents as vectors for semantic search.

---

## 🐛 Troubleshooting

### Backend won't start

```bash
# Check if port 8000 is in use
lsof -i :8000
kill -9 <PID>

# Check logs
docker logs develop_health_backend

# Rebuild
docker-compose down
docker-compose up --build
```

### Frontend won't connect to backend

```bash
# Verify backend is running
curl http://localhost:8000/health

# Check browser console for CORS errors
# Make sure VITE_API_URL is correct in .env
```

### Database connection error

```bash
# Check PostgreSQL is running
psql -h localhost -U postgres

# Verify DATABASE_URL in .env:
# postgresql://postgres:postgres@localhost:5432/develop_health_mvp
```

### LLM API errors

```bash
# Verify OPENROUTER_API_KEY is set
echo $OPENROUTER_API_KEY

# Check if key is valid in .env file
cat .env | grep OPENROUTER
```

### Vector DB not initialized

```bash
# Rebuild vector index
python scripts/build_vector_index.py

# Verify ChromaDB exists
ls -la chroma_db/
```

---

## 📝 Sample Test Patients

These are included in synthetic data:

| ID  | Name            | Insurance       | Diagnoses        |
|-----|-----------------|-----------------|------------------|
| P001| John Doe        | Aetna Gold      | Type 2 Diabetes  |
| P002| Jane Smith      | BlueCross Silver| Hypertension     |
| P003| Bob Johnson     | United Health   | COPD             |
| P004| Alice Williams  | Cigna Connect   | Heart Disease    |
| P005| Charlie Brown   | Humana Premier  | Obesity          |

---

## 🚀 Common Tasks

### Restart Everything

```bash
docker-compose down
docker-compose up --build
```

### View Logs

```bash
# Backend logs
docker logs develop_health_backend -f

# Frontend logs
docker logs develop_health_frontend -f

# Database logs
docker logs develop_health_postgres
```

### Fresh Database

```bash
docker-compose down -v  # -v removes volumes
docker-compose up
# Re-run initialization scripts
```

### Stop Services

```bash
docker-compose stop
```

### Remove Everything

```bash
docker-compose down -v
```

---

## 📚 Documentation

- **Backend**: See `README.md`
- **Frontend**: See `frontend/README.md`
- **Setup**: See `FRONTEND_SETUP.md`
- **API Docs**: http://localhost:8000/docs
- **Architecture**: See project layout above

---

## 🎯 Next Steps

1. ✅ Get everything running (this guide)
2. ✅ Test End-to-End workflow
3. ✅ Test individual phases
4. ✅ Review API responses
5. 🔄 Customize for your use case
6. 🚀 Deploy to production

---

## 💡 Tips

- Use browser DevTools Network tab to see API calls
- Check backend logs for LLM processing details
- Use FastAPI docs at `/docs` to test endpoints directly
- Try different patient/drug combinations
- Monitor performance with browser Lighthouse

---

## 🆘 Still Having Issues?

1. Check Docker Desktop is running
2. Make sure all ports are free (3000, 8000, 5432, 6379)
3. Verify `.env` file has OPENROUTER_API_KEY
4. Check internet connection (needed for OpenRouter LLM)
5. Review logs: `docker-compose logs -f`

---

**Enjoy! 🎉**
