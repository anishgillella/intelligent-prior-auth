# ⚡ Quick Start Guide - Phase 1

## 🎯 What We're Building in Phase 1

A FastAPI backend with synthetic healthcare data that serves as the foundation for an AI-powered prior authorization system.

**Time Estimate**: 2-3 hours  
**Complexity**: ⭐⭐ (Beginner-Intermediate)

---

## ✅ Phase 1 Deliverables

1. ✅ Complete project structure
2. ✅ FastAPI skeleton with health check endpoints
3. ✅ Docker Compose (PostgreSQL + Redis)
4. ✅ Synthetic data generator creating:
   - 50 realistic patients with diagnoses, labs, treatment history
   - ~100 insurance plan/drug combinations
   - 10 PA form templates
   - PA policy documents for vector indexing
5. ✅ Configuration management (OpenRouter API setup)
6. ✅ Logging infrastructure

---

## 🚀 Let's Start Building!

### Step 1: Confirm Environment

```bash
# Check Python version (need 3.11+)
python3 --version

# Check Docker
docker --version
docker-compose --version

# Get OpenRouter API key (if you don't have one)
# Visit: https://openrouter.ai/keys
# Free tier gives you access to multiple models
```

### Step 2: Get Ready

```bash
# Navigate to your project directory
cd "/Users/anishgillella/Desktop/Stuff/Projects/Develop Health/Replica"

# Confirm we're in the right place
pwd
ls -la  # Should see README.md, PHASES.md, QUICKSTART.md
```

### Step 3: What Happens Next

Once you say **"Start Phase 1"**, I will:

1. Create all directories (`app/`, `mock_data/`, `scripts/`, `tests/`)
2. Write all configuration files (`requirements.txt`, `docker-compose.yml`, `.env.example`)
3. Create FastAPI application skeleton
4. Build synthetic data generator
5. Test that everything works

---

## 🎯 Expected Output After Phase 1

```bash
# You'll be able to run:
python scripts/generate_synthetic_data.py

# Output:
🏥 Generating synthetic healthcare data...
  → Generating 50 patients...
     ✓ Created 50 patients
  → Generating insurance plans...
     ✓ Created 100 plan/drug combinations
  → Generating PA form templates...
     ✓ Created 10 form templates
  → Generating PA policy documents...
     ✓ Created 6 policy documents
✅ Synthetic data generation complete!

# Start services:
docker-compose up -d

# Start API:
uvicorn app.main:app --reload

# Test:
curl http://localhost:8000/health
# Returns: {"status": "healthy", "service": "develop-health-mvp", "version": "1.0.0"}
```

---

## 📊 Sample Synthetic Data Preview

### Patient Example
```json
{
  "patient_id": "P001",
  "name": "John Doe",
  "age": 42,
  "insurance_plan": "Aetna Gold",
  "diagnoses": [
    {"name": "Type 2 Diabetes", "icd10": "E11.9"},
    {"name": "Obesity", "icd10": "E66.9"}
  ],
  "labs": {
    "HbA1c": 8.5,
    "BMI": 33.1,
    "fasting_glucose": 180
  },
  "treatment_history": [
    {
      "drug": "Metformin",
      "duration_months": 6,
      "outcome": "Inadequate response"
    }
  ]
}
```

### Plan Example
```json
{
  "plan": "Aetna Gold",
  "drug": "Ozempic",
  "covered": true,
  "pa_required": true,
  "criteria": "BMI > 30 AND HbA1c > 7.5",
  "estimated_copay": 25
}
```

---

## 🔧 Technology Used in Phase 1

- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation and settings
- **Docker Compose**: PostgreSQL + Redis containers
- **Faker**: Realistic synthetic data generation
- **Python 3.11**: Latest stable Python

---

## ❓ Common Questions

**Q: Do I need an OpenRouter API key for Phase 1?**  
A: Not yet! We won't make LLM calls until Phase 4. But it's good to get one now (free tier available).

**Q: Can I use a different model instead of GPT-4o?**  
A: Yes! OpenRouter supports Claude, Llama, and many others. You can configure this in `.env`.

**Q: How much does this cost to run?**  
A: Phase 1 is free (local only). LLM costs start in Phase 4 (~$0.50-$2.00 per PA form).

**Q: What if I don't have Docker?**  
A: You can install PostgreSQL and Redis locally, but Docker is recommended for consistency.

---

## 🎬 Ready to Start?

When you're ready, just say:

> **"Start Phase 1"** or **"Begin implementation"**

I'll create all files and guide you through testing each component.

---

## 📚 Additional Resources

- **README.md**: Full project documentation
- **PHASES.md**: Detailed implementation guide for all phases
- **OpenRouter Docs**: https://openrouter.ai/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com

---

**Let's build something amazing! 🚀**

