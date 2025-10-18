"""
Prompt templates for clinical qualification and eligibility determination
"""

SYSTEM_PROMPT = """You are an expert medical utilization review specialist with 15+ years of experience evaluating prior authorization requests for insurance companies.

Your role is to:
1. Carefully analyze patient clinical data
2. Compare against insurance policy criteria
3. Make evidence-based eligibility determinations
4. Provide clear, concise reasoning citing specific data points

Always:
- Use clinical terminology accurately
- Reference specific lab values, diagnosis codes, and treatment history
- Distinguish between medical necessity and coverage policy
- Flag missing data that could affect the determination
- Provide JSON-formatted responses for system integration"""

CLINICAL_QUALIFICATION_PROMPT = """
Analyze the following patient case for clinical eligibility:

=== INSURANCE POLICY CRITERIA ===
{policy_criteria}

=== PATIENT CLINICAL DATA ===
Patient ID: {patient_id}
Age: {age}
Diagnoses: {diagnoses}
Lab Values:
  - HbA1c: {hba1c}%
  - BMI: {bmi} kg/m²
  - Weight: {weight} lbs

Treatment History:
{treatment_history}

Current Request: Authorization for {drug}

=== TASK ===
Determine if this patient meets the clinical criteria for {drug} authorization.

Respond ONLY with valid JSON (no markdown formatting):
{{
  "meets_criteria": true/false,
  "clinical_justification": "Detailed explanation citing specific data points",
  "confidence_score": 0.0-1.0,
  "missing_data": ["list of missing data that would strengthen assessment"],
  "icd10_codes": {{"diagnosis": "code", ...}},
  "recommendation": "APPROVE/DENY/NEEDS_REVIEW"
}}
"""

RAG_ENHANCED_PROMPT = """
Analyze the following patient case using policy context retrieved from our document system:

=== RETRIEVED POLICY CONTEXT ===
{policy_context}

=== INSURANCE POLICY CRITERIA ===
{policy_criteria}

=== PATIENT CLINICAL DATA ===
Patient ID: {patient_id}
Age: {age}
Gender: {gender}
Diagnoses: {diagnoses}
Lab Values:
  - HbA1c: {hba1c}%
  - BMI: {bmi} kg/m²
  - Weight: {weight} lbs
  - Creatinine: {creatinine}
  - eGFR: {egfr}

Treatment History:
{treatment_history}

Current Request: Authorization for {drug}

=== SPECIFIC POLICY REQUIREMENTS TO EVALUATE ===
{specific_requirements}

=== TASK ===
Using the retrieved policy context and clinical data:
1. Verify patient meets EACH requirement
2. Identify any clinical contraindications
3. Note strength of evidence for each criterion
4. Provide specific recommendations

Respond ONLY with valid JSON:
{{
  "meets_criteria": true/false,
  "criteria_analysis": {{
    "requirement_1": {{"met": true/false, "evidence": "specific data"}},
    "requirement_2": {{"met": true/false, "evidence": "specific data"}},
    ...
  }},
  "clinical_justification": "Comprehensive reasoning tying together all criteria",
  "contraindications": ["list any red flags"],
  "confidence_score": 0.0-1.0,
  "missing_data": ["what's needed for stronger evidence"],
  "recommendation": "APPROVE/DENY/NEEDS_REVIEW",
  "estimated_pa_approval_probability": 0.0-1.0
}}
"""

NARRATIVE_GENERATION_PROMPT = """
Generate a professional clinical narrative for a prior authorization form based on patient data and eligibility determination.

=== PATIENT DATA ===
Patient: {patient_name}
Age: {age}
Diagnoses: {diagnoses}
Current Medications: {current_medications}
Treatment History: {treatment_history}

Lab Results:
- HbA1c: {hba1c}%
- BMI: {bmi}
- Other Relevant: {lab_values}

=== AUTHORIZATION REQUEST ===
Requested Medication: {drug}
Indication: {indication}

=== ELIGIBILITY DETERMINATION ===
Meets Criteria: Yes
Confidence: {confidence}%

=== TASK ===
Write a 150-200 word clinical narrative for the PA form that:
1. Establishes medical necessity
2. Cites specific clinical data (labs, diagnoses, treatment history)
3. Explains why alternative treatments have failed or are contraindicated
4. Justifies this specific medication choice
5. Uses professional, standardized medical language

Format: Plain text, no bullets, suitable for insurance review.

Narrative:
"""

def get_clinical_qualification_prompt(
    policy_criteria: str,
    patient_id: str,
    age: int,
    diagnoses: str,
    hba1c: float,
    bmi: float,
    weight: float,
    treatment_history: str,
    drug: str,
    **kwargs
) -> str:
    """Build clinical qualification prompt"""
    return CLINICAL_QUALIFICATION_PROMPT.format(
        policy_criteria=policy_criteria,
        patient_id=patient_id,
        age=age,
        diagnoses=diagnoses,
        hba1c=hba1c,
        bmi=bmi,
        weight=weight,
        treatment_history=treatment_history,
        drug=drug,
        **kwargs
    )


def get_rag_enhanced_prompt(
    policy_context: str,
    policy_criteria: str,
    patient_id: str,
    age: int,
    gender: str,
    diagnoses: str,
    hba1c: float,
    bmi: float,
    weight: float,
    creatinine: float,
    egfr: int,
    treatment_history: str,
    drug: str,
    specific_requirements: str,
    **kwargs
) -> str:
    """Build RAG-enhanced prompt with policy context"""
    return RAG_ENHANCED_PROMPT.format(
        policy_context=policy_context,
        policy_criteria=policy_criteria,
        patient_id=patient_id,
        age=age,
        gender=gender,
        diagnoses=diagnoses,
        hba1c=hba1c,
        bmi=bmi,
        weight=weight,
        creatinine=creatinine,
        egfr=egfr,
        treatment_history=treatment_history,
        drug=drug,
        specific_requirements=specific_requirements,
        **kwargs
    )


def get_narrative_prompt(
    patient_name: str,
    age: int,
    diagnoses: str,
    current_medications: str,
    treatment_history: str,
    hba1c: float,
    bmi: float,
    lab_values: str,
    drug: str,
    indication: str,
    confidence: int,
    **kwargs
) -> str:
    """Build narrative generation prompt"""
    return NARRATIVE_GENERATION_PROMPT.format(
        patient_name=patient_name,
        age=age,
        diagnoses=diagnoses,
        current_medications=current_medications,
        treatment_history=treatment_history,
        hba1c=hba1c,
        bmi=bmi,
        lab_values=lab_values,
        drug=drug,
        indication=indication,
        confidence=confidence,
        **kwargs
    )
