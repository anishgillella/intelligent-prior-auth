# Data Generation Guide

## Quick Start

Generate synthetic data with any number of patients:

```bash
# Generate 20 patients (default)
python scripts/generate_synthetic_data.py

# Generate 100 patients
python scripts/generate_synthetic_data.py 100

# Generate 500 patients
python scripts/generate_synthetic_data.py 500

# Generate 1000 patients
python scripts/generate_synthetic_data.py 1000
```

## What Gets Generated

### 1. **Patients Data** (`mock_data/patients.json`)
- Full patient profiles with:
  - Demographics (name, age, DOB, address, contact)
  - Insurance plan enrollment
  - Diagnoses (ICD-10 coded)
  - Lab results (HbA1c, BMI, weight, kidney function, liver enzymes)
  - Treatment history (medications tried, outcomes, durations)
  - Allergies

**Data Generation Logic:**
- Ages: 35-75 years
- BMI: 23-42 (realistic distribution)
- HbA1c: 5.8-11.0 (realistic diabetes progression)
- Diagnoses are logically generated based on BMI and lab values:
  - BMI > 30 → Obesity diagnosis
  - HbA1c > 6.5 → Type 2 Diabetes
  - Age > 50 + random → Hypertension
  - BMI > 35 + random → NASH (fatty liver)

### 2. **Insurance Plans** (`mock_data/plans.json`)
- Coverage information for:
  - 10 insurance payers
  - 10 diabetes/obesity medications
  - Results in 100 plan/drug combinations
- Each includes:
  - Coverage status (covered/not covered)
  - PA requirements
  - Approval criteria
  - Tier level
  - Copay amounts
  - Step therapy requirements
  - Quantity limits

### 3. **PA Form Templates** (`mock_data/forms.json`)
- 10 payer-specific PA form templates
- Contains:
  - Patient demographics sections
  - Prescriber information fields
  - Medication information fields
  - Clinical information sections
  - Submission method (phone/fax/portal/mail)

### 4. **Policy Documents** (`mock_data/policies/`)
- 6 detailed PA policy files in text format
- Covers: Ozempic and Trulicity for select plans
- Includes:
  - Coverage criteria
  - Clinical documentation requirements
  - Quantity limits
  - Authorization periods
  - Renewal criteria
  - Exclusions
  - Appeal process

**These are indexed by ChromaDB for semantic search**

## Data Volume by Patient Count

| # Patients | patients.json | File Size | Query Time |
|---|---|---|---|
| 20 | ~1,100 lines | ~80 KB | <5ms |
| 100 | ~5,500 lines | ~400 KB | <10ms |
| 500 | ~27,500 lines | ~2 MB | <20ms |
| 1,000 | ~55,000 lines | ~4 MB | <50ms |
| 5,000 | ~275,000 lines | ~20 MB | ~100ms |
| 10,000 | ~550,000 lines | ~40 MB | ~200ms |

## Important Notes

### Reproducibility
- Script uses `Faker.seed(42)` for reproducible data
- Same seed = same patient names, addresses, etc.
- Change seed in script if you want different patient data

### Insurance Plan Distribution
- 10 payers randomly assigned
- Each plan covers ~8 of 10 drugs (85% coverage rate)
- ~65% of covered drugs require PA

### Treatment History Logic
- Diabetic patients get at least 1 treatment (Metformin)
- ~60% get a second-line treatment (Glipizide/Jardiance/Invokana)
- Outcomes: "Inadequate response", "Intolerance - GI side effects", "Partial response"

## After Generation

### 1. Update Database
```bash
python scripts/import_data_to_db.py
```

### 2. Rebuild Vector Index
```bash
python scripts/build_vector_index.py
```

### 3. Test the System
```bash
# Start API
uvicorn app.main:app --reload

# Test orchestrator with P001
curl -X POST "http://localhost:8000/api/orchestrator/process" \
  -H "Content-Type: application/json" \
  -d '{"patient_id": "P001", "drug": "Ozempic"}'
```

## Scaling to 200K Patients

Current architecture works fine for:
- **100 patients**: Instant queries
- **1,000 patients**: Fast queries (< 100ms)
- **10,000 patients**: Acceptable (< 500ms)

At **200,000+ patients**, you'll want:
1. **Neo4j Graph DB** for relationship queries
2. **Redis caching** for frequent queries
3. **Query optimization** (indexes, partitioning)

See `ARCHITECTURE.md` for details.

## Troubleshooting

**Vector index errors?**
- Delete `chroma_db/` directory and rebuild: `python scripts/build_vector_index.py`

**Duplicate patients?**
- Script regenerates fresh each time (overwrites previous)
- To append: modify `generate_patients()` to load existing data first

**Memory issues with 10K+ patients?**
- Run in smaller batches
- Or increase available memory/use instance with more RAM

## Example: Generate 100 Patients

```bash
# Generate data
python scripts/generate_synthetic_data.py 100

# Load into database
python scripts/import_data_to_db.py

# Rebuild vector index
python scripts/build_vector_index.py

# Start API
uvicorn app.main:app --reload

# You now have 100 realistic patient cases ready for testing!
```
