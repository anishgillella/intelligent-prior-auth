"""
Security utilities for PHI handling and data redaction
"""
import re
from typing import Any, Dict


def redact_phi(text: str) -> str:
    """
    Redact Protected Health Information (PHI) from text
    
    Args:
        text: Input text potentially containing PHI
        
    Returns:
        Text with PHI redacted
    """
    if not text:
        return text
    
    # Redact SSN (XXX-XX-XXXX)
    text = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', 'XXX-XX-XXXX', text)
    
    # Redact dates of birth (MM/DD/YYYY)
    text = re.sub(r'\b\d{2}/\d{2}/\d{4}\b', 'XX/XX/XXXX', text)
    
    # Redact phone numbers
    text = re.sub(r'\b\d{3}-\d{3}-\d{4}\b', 'XXX-XXX-XXXX', text)
    text = re.sub(r'\(\d{3}\)\s*\d{3}-\d{4}', '(XXX) XXX-XXXX', text)
    
    # Redact email addresses (keep domain for debugging)
    text = re.sub(r'\b[A-Za-z0-9._%+-]+@', 'REDACTED@', text)
    
    # Redact ZIP codes (last 4 digits)
    text = re.sub(r'\b(\d{5})-\d{4}\b', r'\1-XXXX', text)
    
    return text


def redact_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Redact PHI from patient data dictionary
    
    Args:
        data: Patient data dictionary
        
    Returns:
        Dictionary with sensitive fields redacted
    """
    if not isinstance(data, dict):
        return data
    
    redacted = data.copy()
    
    # Fields to completely redact
    sensitive_fields = ['ssn', 'date_of_birth', 'phone', 'email', 'address']
    
    for field in sensitive_fields:
        if field in redacted:
            if field == 'date_of_birth':
                redacted[field] = 'XXXX-XX-XX'
            elif field == 'phone':
                redacted[field] = 'XXX-XXX-XXXX'
            elif field == 'email':
                redacted[field] = 'redacted@example.com'
            elif field == 'address':
                redacted[field] = {'street': 'REDACTED', 'city': 'REDACTED', 'state': 'XX', 'zip': 'XXXXX'}
            else:
                redacted[field] = 'REDACTED'
    
    return redacted


def validate_api_key(api_key: str, expected_key: str) -> bool:
    """
    Validate API key for endpoint authentication
    
    Args:
        api_key: Provided API key
        expected_key: Expected API key from settings
        
    Returns:
        True if valid, False otherwise
    """
    return api_key == expected_key

