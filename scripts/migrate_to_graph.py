"""
Migrate mock data to Neo4j graph database

Loads patients, diagnoses, drugs, insurance plans, and relationships
into Neo4j for Graph RAG capabilities.
"""
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.graph_index import get_graph_manager
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_patients_from_json():
    """Load patient data from mock_data/patients.json"""
    patients_file = Path(settings.mock_data_dir) / "patients.json"
    
    if not patients_file.exists():
        logger.error(f"Patients file not found: {patients_file}")
        return []
    
    with open(patients_file) as f:
        return json.load(f)


def load_plans_from_json():
    """Load insurance plans from mock_data/plans.json"""
    plans_file = Path(settings.mock_data_dir) / "plans.json"
    
    if not plans_file.exists():
        logger.error(f"Plans file not found: {plans_file}")
        return []
    
    with open(plans_file) as f:
        return json.load(f)


def migrate_patients_to_graph():
    """Migrate all patients to Neo4j"""
    print("\n" + "=" * 60)
    print("🏥 MIGRATING PATIENTS TO NEO4J")
    print("=" * 60 + "\n")
    
    graph_manager = get_graph_manager()
    if not graph_manager.driver:
        logger.error("❌ Neo4j not connected!")
        return
    
    # Load data
    patients = load_patients_from_json()
    plans = load_plans_from_json()
    
    logger.info(f"Loading {len(patients)} patients...")
    
    # Create patient nodes
    patient_count = 0
    for patient in patients:
        if graph_manager.create_patient_node(patient):
            patient_count += 1
            
            # Create diagnosis nodes and relationships
            for diagnosis in patient.get("diagnoses", []):
                graph_manager.create_diagnosis_node(
                    diagnosis["name"], 
                    diagnosis["icd10"]
                )
                graph_manager.add_patient_diagnosis(
                    patient["patient_id"],
                    diagnosis["icd10"]
                )
            
            # Create treatment relationships
            for treatment in patient.get("treatment_history", []):
                drug_name = treatment["drug"]
                graph_manager.create_drug_node(drug_name)
                graph_manager.add_patient_treatment(
                    patient["patient_id"],
                    drug_name,
                    treatment["outcome"]
                )
        
        if patient_count % 20 == 0:
            logger.info(f"  ✓ Created {patient_count} patients...")
    
    logger.info(f"✅ Created {patient_count} patient nodes")
    
    # Create insurance plan nodes
    logger.info(f"\nLoading {len(plans)} insurance plans...")
    plan_count = 0
    unique_plans = set()
    unique_drugs = set()
    
    for plan in plans:
        plan_name = plan["plan"]
        drug_name = plan["drug"]
        
        if plan_name not in unique_plans:
            graph_manager.create_insurance_plan_node(plan_name)
            unique_plans.add(plan_name)
        
        if drug_name not in unique_drugs:
            graph_manager.create_drug_node(drug_name)
            unique_drugs.add(drug_name)
        
        # Link plan to drug with coverage info
        if plan["covered"]:
            graph_manager.add_plan_drug_coverage(
                plan_name,
                drug_name,
                plan["pa_required"],
                plan.get("criteria")
            )
            plan_count += 1
    
    logger.info(f"✅ Created {len(unique_plans)} insurance plan nodes")
    logger.info(f"✅ Created {len(unique_drugs)} drug nodes")
    logger.info(f"✅ Created {plan_count} plan→drug coverage relationships")
    
    # Link patients to insurance plans
    logger.info(f"\nLinking patients to insurance plans...")
    link_count = 0
    for patient in patients:
        if graph_manager.add_patient_insurance(
            patient["patient_id"],
            patient["insurance_plan"]
        ):
            link_count += 1
    
    logger.info(f"✅ Linked {link_count} patients to insurance plans")
    
    # Summary
    print("\n" + "=" * 60)
    print("✅ NEO4J MIGRATION COMPLETE!")
    print("=" * 60)
    print(f"\nGraph Statistics:")
    print(f"  • Patients: {patient_count}")
    print(f"  • Insurance Plans: {len(unique_plans)}")
    print(f"  • Drugs: {len(unique_drugs)}")
    print(f"  • Plan/Drug Combinations: {plan_count}")
    print(f"\n💡 Next Steps:")
    print(f"  1. Test graph queries: python -m pytest tests/test_graph_rag.py")
    print(f"  2. View Neo4j UI: http://localhost:7474 (when running)")
    print(f"  3. Start API: uvicorn app.main:app --reload")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    migrate_patients_to_graph()
