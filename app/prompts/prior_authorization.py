"""
Prior Authorization (PA) Form Prompt Templates
Generates clinical justification narratives for PA submissions
"""

# System prompt for PA narrative generation
PA_NARRATIVE_SYSTEM_PROMPT = """You are a clinical documentation specialist who writes professional medical justifications for insurance prior authorization requests. Your narratives must be:

- Clinically accurate and evidence-based
- Concise but comprehensive (150-250 words)
- Written in professional medical language
- Focused on why the requested drug is medically necessary for this specific patient
- Include relevant clinical history, failed treatments, and clinical reasoning

Output format: A single cohesive paragraph suitable for submission to insurance companies."""

# User prompt template for PA narrative generation
PA_NARRATIVE_USER_TEMPLATE = """Generate a clinical justification paragraph for a Prior Authorization request with the following information:

PATIENT INFORMATION:
- Name: {patient_name}
- Age: {patient_age}
- Gender: {patient_gender}
- Primary Diagnosis: {diagnosis}

REQUESTED MEDICATION:
- Drug: {drug_name}
- Indication: {indication}

CLINICAL HISTORY:
- Current Medications: {current_medications}
- Previous Drug Trials: {previous_trials}
- Relevant Labs/Vitals: {clinical_findings}

POLICY REQUIREMENTS:
{policy_requirements}

CLINICAL REASONING:
{clinical_reasoning}

Generate a professional clinical justification narrative that explains why this patient needs this drug. Focus on clinical necessity and policy compliance."""

# System prompt for form metadata extraction
PA_FORM_METADATA_SYSTEM_PROMPT = """You are extracting structured data for a Prior Authorization form. Extract the following information and return as JSON:
- drug_name: The requested medication name
- indication: The medical indication/reason for the drug
- estimated_duration: Expected length of treatment (e.g., "3 months", "indefinite")
- priority_level: "Standard", "Urgent", or "Emergency"
- return JSON format only."""

# PA Form Template Structure
PA_FORM_TEMPLATE = {
    "form_header": {
        "title": "PRIOR AUTHORIZATION REQUEST FORM",
        "form_id": "{form_id}",
        "submission_date": "{submission_date}",
        "requesting_provider": "{provider_name}",
        "npi": "{npi}"
    },
    "patient_section": {
        "patient_name": "{patient_name}",
        "date_of_birth": "{date_of_birth}",
        "member_id": "{member_id}",
        "insurance_plan": "{insurance_plan}"
    },
    "clinical_section": {
        "requested_drug": "{drug_name}",
        "dosage": "{dosage}",
        "frequency": "{frequency}",
        "quantity": "{quantity}",
        "duration": "{duration}",
        "diagnosis_code": "{diagnosis_code}",
        "diagnosis_description": "{diagnosis_description}"
    },
    "justification_section": {
        "clinical_narrative": "{clinical_narrative}",
        "failed_prior_treatments": "{failed_treatments}",
        "clinical_findings": "{clinical_findings}",
        "contraindications": "{contraindications}",
        "supporting_evidence": "{supporting_evidence}"
    },
    "signature_section": {
        "provider_signature": "_" * 30,
        "date": "{date}",
        "contact_info": "{contact_info}"
    }
}

# Template for markdown form output
PA_MARKDOWN_TEMPLATE = """# PRIOR AUTHORIZATION REQUEST

## Form Information
- **Form ID**: {form_id}
- **Submission Date**: {submission_date}
- **Requesting Provider**: {provider_name}

## Patient Information
- **Name**: {patient_name}
- **Date of Birth**: {date_of_birth}
- **Member ID**: {member_id}
- **Insurance Plan**: {insurance_plan}

## Clinical Information
- **Requested Drug**: {drug_name}
- **Dosage**: {dosage}
- **Frequency**: {frequency}
- **Expected Duration**: {duration}
- **Primary Diagnosis**: {diagnosis_description} ({diagnosis_code})

## Clinical Justification

{clinical_narrative}

### Failed Prior Treatments
{failed_treatments}

### Clinical Findings
{clinical_findings}

### Supporting Evidence
{supporting_evidence}

---
**Confidential - For Insurance Use Only**
"""
