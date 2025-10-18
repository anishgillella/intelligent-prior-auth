"""
Generate synthetic healthcare data for testing and development

Creates realistic patient data, insurance plans, PA forms, and policy documents.
Designed to generate smaller dataset (20 patients) for MVP testing.
"""
import json
from pathlib import Path
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()
Faker.seed(42)  # For reproducibility
random.seed(42)

# Output directory
DATA_DIR = Path("mock_data")
DATA_DIR.mkdir(exist_ok=True)
POLICIES_DIR = DATA_DIR / "policies"
POLICIES_DIR.mkdir(exist_ok=True)

# ==================== Reference Data ====================

# Common drugs for diabetes and weight management
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
    "Coronary Artery Disease": "I25.10",
}

# First and last names for realistic data
FIRST_NAMES = ["John", "Sarah", "Michael", "Emily", "David", "Jessica", "Robert", "Jennifer", "William", "Lisa",
               "James", "Mary", "Richard", "Patricia", "Thomas", "Linda", "Charles", "Barbara", "Daniel", "Elizabeth"]

LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
              "Hernandez", "Lopez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee"]


# ==================== Data Generation Functions ====================

def generate_patients(n=20):
    """Generate synthetic patient data"""
    patients = []
    
    print(f"  → Generating {n} patients...")
    
    for i in range(1, n + 1):
        age = random.randint(35, 75)
        bmi = random.uniform(23, 42)
        hba1c = random.uniform(5.8, 11.0)
        
        # Generate realistic diagnoses based on BMI/age
        diagnoses = []
        if bmi > 30:
            diagnoses.append("Obesity")
        if hba1c > 6.5 or random.random() > 0.4:
            diagnoses.append("Type 2 Diabetes")
        if age > 50 and random.random() > 0.4:
            diagnoses.append("Hypertension")
        if random.random() > 0.6:
            diagnoses.append("Hyperlipidemia")
        if bmi > 35 and random.random() > 0.8:
            diagnoses.append("NASH")
        
        # Generate treatment history for diabetes patients
        treatment_history = []
        if "Type 2 Diabetes" in diagnoses:
            # First-line: Metformin
            treatment_history.append({
                "drug": "Metformin",
                "duration_months": random.randint(4, 24),
                "dosage": random.choice(["500mg twice daily", "1000mg twice daily"]),
                "outcome": random.choice([
                    "Inadequate response", 
                    "Partial response", 
                    "Intolerance - GI side effects"
                ]),
                "started_date": (datetime.now() - timedelta(days=random.randint(120, 730))).strftime("%Y-%m-%d")
            })
            
            # Second-line therapy (for some patients)
            if random.random() > 0.4:
                treatment_history.append({
                    "drug": random.choice(["Glipizide", "Jardiance", "Invokana"]),
                    "duration_months": random.randint(3, 12),
                    "dosage": "10mg daily",
                    "outcome": random.choice(["Inadequate response", "Intolerance", "Partial response"]),
                    "started_date": (datetime.now() - timedelta(days=random.randint(90, 365))).strftime("%Y-%m-%d")
                })
        
        # Generate realistic name
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"
        
        # Calculate weight from BMI (assuming average height of 5'8" / 68 inches)
        height_inches = random.randint(62, 74)
        weight_lbs = round((bmi * (height_inches ** 2)) / 703, 1)
        
        patient = {
            "patient_id": f"P{i:03d}",
            "name": full_name,
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
            "email": f"{first_name.lower()}.{last_name.lower()}@{fake.free_email_domain()}",
            "insurance_plan": random.choice(INSURANCE_PLANS),
            "member_id": f"MEM{fake.random_number(digits=10)}",
            "diagnoses": [{"name": d, "icd10": ICD10_CODES[d]} for d in diagnoses],
            "labs": {
                "HbA1c": round(hba1c, 1),
                "fasting_glucose": random.randint(95, 280),
                "BMI": round(bmi, 1),
                "weight_lbs": weight_lbs,
                "creatinine": round(random.uniform(0.7, 1.8), 2),
                "eGFR": random.randint(55, 120),
                "ALT": random.randint(12, 75),
                "AST": random.randint(10, 60),
                "last_updated": (datetime.now() - timedelta(days=random.randint(1, 90))).strftime("%Y-%m-%d")
            },
            "treatment_history": treatment_history,
            "allergies": random.sample(["Penicillin", "Sulfa drugs", "None known"], k=1),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        patients.append(patient)
    
    print(f"     ✓ Created {len(patients)} patients")
    return patients


def generate_plans():
    """Generate insurance plan formularies"""
    plans = []
    
    print("  → Generating insurance plan formularies...")
    
    for plan in INSURANCE_PLANS:
        for drug in DRUGS:
            # Coverage logic
            covered = random.random() > 0.15  # 85% coverage rate
            pa_required = random.random() > 0.35 if covered else False  # 65% need PA if covered
            
            # Generate PA criteria
            criteria = None
            if pa_required:
                criteria_options = [
                    "BMI > 30 AND HbA1c > 7.5",
                    "BMI > 27 AND HbA1c > 8.0 AND failed metformin for 3+ months",
                    "HbA1c > 9.0 OR failed two oral agents",
                    "Type 2 Diabetes AND BMI > 30 AND cardiovascular risk factors present",
                    "BMI > 30 AND failed lifestyle modifications for 6+ months",
                ]
                criteria = random.choice(criteria_options)
            
            plan_entry = {
                "plan": plan,
                "drug": drug,
                "covered": covered,
                "pa_required": pa_required,
                "criteria": criteria,
                "tier": random.randint(2, 4) if covered else None,
                "estimated_copay": random.choice([10.0, 25.0, 50.0, 100.0]) if covered else None,
                "step_therapy_required": random.random() > 0.75,
                "quantity_limit": random.choice([None, "30 day supply", "90 day supply"]),
            }
            
            plans.append(plan_entry)
    
    print(f"     ✓ Created {len(plans)} plan/drug combinations")
    return plans


def generate_forms():
    """Generate PA form templates"""
    forms = []
    
    print("  → Generating PA form templates...")
    
    for plan in INSURANCE_PLANS:
        payer_name = plan.split()[0]  # e.g., "Aetna" from "Aetna Gold"
        
        form = {
            "plan": plan,
            "payer_name": payer_name,
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
                "submission_method": random.choice(["portal", "fax", "phone", "mail"])
            }
        }
        forms.append(form)
    
    print(f"     ✓ Created {len(forms)} form templates")
    return forms


def generate_pa_policies():
    """Generate PA policy documents for vector indexing"""
    policies = []
    
    print("  → Generating PA policy documents...")
    
    policy_templates = {
        "Ozempic": """
PRIOR AUTHORIZATION POLICY: SEMAGLUTIDE (OZEMPIC)

Payer: {plan}
Effective Date: January 1, 2024
Policy Number: PA-2024-{policy_num}

===================================================
INDICATION
===================================================
Treatment of Type 2 Diabetes Mellitus as an adjunct to diet and exercise to improve glycemic control.

===================================================
COVERAGE CRITERIA
===================================================
Prior authorization will be granted if the patient meets ALL of the following criteria:

1. DIAGNOSIS
   - Confirmed diagnosis of Type 2 Diabetes Mellitus (ICD-10: E11.x)
   - Documentation of diagnosis in medical record

2. CLINICAL PARAMETERS
   - Body Mass Index (BMI) ≥ 30 kg/m² 
     OR BMI ≥ 27 kg/m² with at least one weight-related comorbidity
   - HbA1c ≥ 7.5% documented within the past 90 days
   - Baseline weight documented

3. PREVIOUS THERAPY
   - Trial of metformin for at least 3 months (unless contraindicated or not tolerated)
   - Documentation of inadequate response, defined as:
     * Failure to achieve HbA1c goal, OR
     * Intolerance to first-line therapy

4. PRESCRIBER REQUIREMENTS
   - Prescribed by or in consultation with an endocrinologist or primary care physician 
     with experience in diabetes management
   - Prescriber must monitor patient regularly

5. CONTRAINDICATIONS CHECK
   - No personal or family history of medullary thyroid carcinoma (MTC)
   - No Multiple Endocrine Neoplasia syndrome type 2 (MEN 2)
   - No history of pancreatitis

===================================================
QUANTITY LIMITS
===================================================
- Initial dose: 0.25 mg weekly for 4 weeks
- Maintenance dose: 0.5 mg to 2 mg weekly
- Maximum: One pen per 28 days

===================================================
DURATION OF AUTHORIZATION
===================================================
Initial Authorization: 6 months

Renewal Criteria: Must demonstrate one of the following:
  - HbA1c reduction of ≥ 0.5% from baseline, OR
  - Weight loss of ≥ 5% from baseline, OR
  - Significant improvement in cardiovascular risk factors

Renewal Authorization: 12 months

===================================================
EXCLUSIONS
===================================================
- Type 1 Diabetes Mellitus
- Diabetic ketoacidosis
- Use for weight loss alone (without diabetes diagnosis)
- Pregnancy or planning pregnancy

===================================================
DOCUMENTATION REQUIREMENTS
===================================================
The following documentation must be submitted:
1. Recent HbA1c value (within 90 days) and date of test
2. Current BMI calculation
3. List of previous diabetes medications tried with:
   - Medication names and dates
   - Duration of therapy
   - Reason for discontinuation
4. Relevant lab values (renal function, lipid panel)
5. Statement of medical necessity

===================================================
APPEAL PROCESS
===================================================
If denied, provider may appeal with additional clinical documentation 
demonstrating medical necessity within 30 days of denial notice.

Contact: Prior Authorization Department
Phone: 1-800-555-PRIOR
Fax: 1-800-555-FAXPA
""",
        
        "Trulicity": """
PRIOR AUTHORIZATION POLICY: DULAGLUTIDE (TRULICITY)

Payer: {plan}
Effective Date: January 1, 2024
Policy Number: PA-2024-{policy_num}

===================================================
INDICATION
===================================================
Treatment of Type 2 Diabetes Mellitus to improve glycemic control.

===================================================
COVERAGE CRITERIA
===================================================
Prior authorization will be approved if ALL criteria are met:

1. DIAGNOSIS REQUIREMENTS
   - Type 2 Diabetes Mellitus diagnosis confirmed (ICD-10: E11.x)
   - Documented in medical record by healthcare provider

2. LABORATORY VALUES
   - HbA1c ≥ 8.0% within past 60 days
   - Baseline creatinine and eGFR documented
   - No evidence of end-stage renal disease (eGFR > 15 mL/min)

3. BODY MASS INDEX
   - BMI > 27 kg/m² required
   - Current weight documented

4. PRIOR MEDICATION TRIALS
   - Patient must have failed or been intolerant to at least TWO oral 
     antidiabetic agents, including:
     * Metformin (unless contraindicated), AND
     * One additional agent (sulfonylurea, DPP-4 inhibitor, or SGLT2 inhibitor)
   - Each medication trial must be at least 3 months duration
   - Documentation of inadequate glycemic control or intolerance required

5. MEDICAL HISTORY
   - No personal history of pancreatitis
   - No history of medullary thyroid carcinoma
   - No pregnancy or plans to become pregnant

===================================================
CLINICAL DOCUMENTATION REQUIRED
===================================================
Submit the following with PA request:
1. Current HbA1c value and date of test
2. Complete list of previous diabetes medications:
   - Medication names
   - Start and stop dates
   - Doses used
   - Reason for discontinuation or inadequacy
3. Current BMI and weight
4. Recent comprehensive metabolic panel (within 6 months)
5. Thyroid screening if family history of thyroid cancer

===================================================
QUANTITY LIMITS
===================================================
- 0.75 mg weekly: 4 pens per 28 days
- 1.5 mg weekly: 4 pens per 28 days
- 3.0 mg weekly: 4 pens per 28 days
- 4.5 mg weekly: 4 pens per 28 days

===================================================
AUTHORIZATION PERIOD
===================================================
Initial: 12 months with documented monitoring plan

Renewal: Requires documentation showing:
  - Continued appropriate use
  - HbA1c improvement or maintenance of glycemic control
  - Weight trend monitoring
  - No serious adverse events

===================================================
STEP THERAPY
===================================================
This medication requires step therapy. Patients must try and fail:
1. Metformin (first-line)
2. One additional oral agent (second-line)
   Before approval for GLP-1 agonist therapy

===================================================
DENIAL CRITERIA
===================================================
PA will be denied if:
- Type 1 Diabetes
- HbA1c < 8.0%
- BMI < 27 kg/m²
- Inadequate trial of oral medications
- History of MEN 2 or medullary thyroid cancer
- Pregnancy

===================================================
CONTACT INFORMATION
===================================================
Questions: 1-800-FORMULARY
PA Submissions: Online portal or fax to 1-800-PA-SUBMIT
""",
    }
    
    # Generate policies for top 3 plans and 2 key drugs
    plans_to_use = INSURANCE_PLANS[:3]
    drugs_to_use = ["Ozempic", "Trulicity"]
    
    for plan in plans_to_use:
        for drug in drugs_to_use:
            template = policy_templates[drug]
            policy_num = fake.random_number(digits=6)
            policy_text = template.format(plan=plan, policy_num=policy_num)
            
            filename = f"{plan.lower().replace(' ', '_')}_{drug.lower()}_policy.txt"
            
            # Write to file
            with open(POLICIES_DIR / filename, "w") as f:
                f.write(policy_text)
            
            policies.append({
                "drug": drug,
                "plan": plan,
                "filename": filename,
                "policy_number": f"PA-2024-{policy_num}"
            })
    
    print(f"     ✓ Created {len(policies)} policy documents in {POLICIES_DIR}/")
    return policies


# ==================== Main Execution ====================

def main():
    """Generate all synthetic data"""
    print("\n" + "=" * 60)
    print("🏥 DEVELOP HEALTH MVP - SYNTHETIC DATA GENERATOR")
    print("=" * 60)
    print(f"Output Directory: {DATA_DIR.absolute()}\n")
    
    # Generate patients
    patients = generate_patients(20)  # Smaller dataset for MVP
    with open(DATA_DIR / "patients.json", "w") as f:
        json.dump(patients, f, indent=2)
    
    # Generate insurance plans
    plans = generate_plans()
    with open(DATA_DIR / "plans.json", "w") as f:
        json.dump(plans, f, indent=2)
    
    # Generate PA forms
    forms = generate_forms()
    with open(DATA_DIR / "forms.json", "w") as f:
        json.dump(forms, f, indent=2)
    
    # Generate PA policies
    policies = generate_pa_policies()
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ SYNTHETIC DATA GENERATION COMPLETE!")
    print("=" * 60)
    print(f"📁 Output Location: {DATA_DIR.absolute()}/")
    print(f"\nFiles Created:")
    print(f"  • patients.json     → {len(patients)} patients with full clinical profiles")
    print(f"  • plans.json        → {len(plans)} insurance plan/drug combinations")
    print(f"  • forms.json        → {len(forms)} PA form templates")
    print(f"  • policies/         → {len(policies)} detailed PA policy documents")
    print("\n💡 Next Steps:")
    print("  1. Copy env.example to .env and configure your OpenRouter API key")
    print("  2. Run: docker-compose up -d")
    print("  3. Run: uvicorn app.main:app --reload")
    print("  4. Test: curl http://localhost:8000/health")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()

