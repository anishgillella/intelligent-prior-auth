"""
Import mock data from JSON files into PostgreSQL database
"""
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.database import init_db, get_db_context, check_db_connection
from app.data.db_models import InsurancePlan, Patient, PAForm
from app.data.mock_loader import load_patients, load_plans, load_forms
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def import_plans():
    """Import insurance plans into database"""
    logger.info("Importing insurance plans...")
    
    plans_data = load_plans()
    
    with get_db_context() as db:
        # Clear existing plans
        db.query(InsurancePlan).delete()
        
        # Insert new plans
        for plan_data in plans_data:
            plan = InsurancePlan(
                plan=plan_data["plan"],
                drug=plan_data["drug"],
                covered=plan_data["covered"],
                pa_required=plan_data["pa_required"],
                criteria=plan_data.get("criteria"),
                tier=plan_data.get("tier"),
                estimated_copay=plan_data.get("estimated_copay"),
                step_therapy_required=plan_data.get("step_therapy_required", False),
                quantity_limit=plan_data.get("quantity_limit"),
            )
            db.add(plan)
        
        db.commit()
        
        count = db.query(InsurancePlan).count()
        logger.info(f"✓ Imported {count} insurance plan records")


def import_patients():
    """Import patients into database"""
    logger.info("Importing patients...")
    
    patients_data = load_patients()
    
    with get_db_context() as db:
        # Clear existing patients
        db.query(Patient).delete()
        
        # Insert new patients
        for patient_data in patients_data:
            patient = Patient(
                patient_id=patient_data["patient_id"],
                name=patient_data["name"],
                date_of_birth=patient_data["date_of_birth"],
                age=patient_data["age"],
                gender=patient_data["gender"],
                address=patient_data["address"],
                phone=patient_data["phone"],
                email=patient_data["email"],
                insurance_plan=patient_data["insurance_plan"],
                member_id=patient_data["member_id"],
                diagnoses=patient_data["diagnoses"],
                labs=patient_data["labs"],
                treatment_history=patient_data["treatment_history"],
                allergies=patient_data["allergies"],
            )
            db.add(patient)
        
        db.commit()
        
        count = db.query(Patient).count()
        logger.info(f"✓ Imported {count} patient records")


def import_forms():
    """Import PA form templates into database"""
    logger.info("Importing PA form templates...")
    
    forms_data = load_forms()
    
    with get_db_context() as db:
        # Clear existing forms
        db.query(PAForm).delete()
        
        # Insert new forms
        for form_data in forms_data:
            form = PAForm(
                plan=form_data["plan"],
                payer_name=form_data["payer_name"],
                form_version=form_data["form_version"],
                template=form_data["template"],
            )
            db.add(form)
        
        db.commit()
        
        count = db.query(PAForm).count()
        logger.info(f"✓ Imported {count} PA form templates")


def main():
    """Main import function"""
    print("\n" + "=" * 60)
    print("📊 IMPORTING MOCK DATA TO DATABASE")
    print("=" * 60 + "\n")
    
    # Check database connection
    logger.info("Checking database connection...")
    if not check_db_connection():
        logger.error("❌ Database connection failed! Make sure PostgreSQL is running:")
        logger.error("   Run: docker-compose up -d")
        sys.exit(1)
    logger.info("✓ Database connection successful\n")
    
    # Initialize database tables
    logger.info("Initializing database tables...")
    init_db()
    logger.info("✓ Database tables initialized\n")
    
    # Import data
    try:
        import_plans()
        import_patients()
        import_forms()
        
        print("\n" + "=" * 60)
        print("✅ DATA IMPORT COMPLETE!")
        print("=" * 60)
        print("\n💡 Next Steps:")
        print("  1. Test the API: curl http://localhost:8000/check-coverage")
        print("  2. Or visit the docs: http://localhost:8000/docs")
        print("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Import failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

