"""
Utility functions to load mock data from JSON files
"""
import json
from pathlib import Path
from typing import List, Dict, Any
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def load_json_file(filename: str) -> List[Dict[str, Any]]:
    """
    Load data from JSON file
    
    Args:
        filename: Name of JSON file (e.g., 'patients.json')
        
    Returns:
        List of dictionaries containing the data
    """
    file_path = Path(settings.mock_data_dir) / filename
    
    if not file_path.exists():
        logger.error(f"File not found: {file_path}")
        raise FileNotFoundError(f"Mock data file not found: {file_path}")
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} records from {filename}")
        return data
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON from {filename}: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading {filename}: {e}")
        raise


def load_patients() -> List[Dict[str, Any]]:
    """Load patient data from JSON"""
    return load_json_file("patients.json")


def load_plans() -> List[Dict[str, Any]]:
    """Load insurance plan data from JSON"""
    return load_json_file("plans.json")


def load_forms() -> List[Dict[str, Any]]:
    """Load PA form templates from JSON"""
    return load_json_file("forms.json")


def get_patient_by_id(patient_id: str) -> Dict[str, Any]:
    """
    Get a specific patient by ID from JSON data
    
    Args:
        patient_id: Patient ID (e.g., 'P001')
        
    Returns:
        Patient data dictionary
    """
    patients = load_patients()
    for patient in patients:
        if patient.get("patient_id") == patient_id:
            return patient
    
    raise ValueError(f"Patient not found: {patient_id}")


def get_plan_by_drug(plan_name: str, drug: str) -> Dict[str, Any]:
    """
    Get coverage information for a specific plan and drug
    
    Args:
        plan_name: Insurance plan name (e.g., 'Aetna Gold')
        drug: Drug name (e.g., 'Ozempic')
        
    Returns:
        Plan coverage dictionary
    """
    plans = load_plans()
    for plan in plans:
        if plan.get("plan") == plan_name and plan.get("drug") == drug:
            return plan
    
    raise ValueError(f"Plan not found: {plan_name} + {drug}")


def search_plans_by_drug(drug: str) -> List[Dict[str, Any]]:
    """
    Get all plans that cover a specific drug
    
    Args:
        drug: Drug name
        
    Returns:
        List of plan coverage dictionaries
    """
    plans = load_plans()
    return [p for p in plans if p.get("drug") == drug and p.get("covered")]


def search_plans_by_plan_name(plan_name: str) -> List[Dict[str, Any]]:
    """
    Get all drugs covered under a specific plan
    
    Args:
        plan_name: Insurance plan name
        
    Returns:
        List of plan coverage dictionaries
    """
    plans = load_plans()
    return [p for p in plans if p.get("plan") == plan_name]

