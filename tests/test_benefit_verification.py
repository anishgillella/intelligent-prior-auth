"""
Unit tests for benefit verification module
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.data.database import Base
from app.data.db_models import InsurancePlan, Patient
from app.modules.benefit_verification import check_coverage, check_coverage_by_plan


# Create in-memory SQLite database for testing
@pytest.fixture(scope="function")
def test_db():
    """Create a test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    # Add test data
    setup_test_data(db)
    
    yield db
    
    db.close()


def setup_test_data(db: Session):
    """Setup test data in database"""
    # Add test insurance plans
    plans = [
        InsurancePlan(
            plan="Aetna Gold",
            drug="Ozempic",
            covered=True,
            pa_required=True,
            criteria="BMI > 30 AND HbA1c > 7.5",
            tier=3,
            estimated_copay=25.0,
            step_therapy_required=False,
            quantity_limit="30 day supply"
        ),
        InsurancePlan(
            plan="Aetna Gold",
            drug="Metformin",
            covered=True,
            pa_required=False,
            tier=1,
            estimated_copay=10.0,
            step_therapy_required=False,
        ),
        InsurancePlan(
            plan="BlueCross Silver",
            drug="Trulicity",
            covered=False,
            pa_required=False,
        ),
    ]
    
    for plan in plans:
        db.add(plan)
    
    # Add test patient
    patient = Patient(
        patient_id="P001",
        name="John Doe",
        date_of_birth="1980-01-01",
        age=44,
        gender="Male",
        address={"street": "123 Main St", "city": "Boston", "state": "MA", "zip": "02101"},
        phone="555-1234",
        email="john@example.com",
        insurance_plan="Aetna Gold",
        member_id="MEM123456",
        diagnoses=[{"name": "Type 2 Diabetes", "icd10": "E11.9"}],
        labs={"HbA1c": 8.5, "BMI": 33.1},
        treatment_history=[{"drug": "Metformin", "duration_months": 6, "outcome": "Inadequate response"}],
        allergies=["None known"]
    )
    db.add(patient)
    
    db.commit()


# ==================== Tests ====================

def test_check_coverage_covered_with_pa(test_db):
    """Test coverage check for covered drug requiring PA"""
    result = check_coverage("P001", "Ozempic", test_db)
    
    assert result.covered == True
    assert result.pa_required == True
    assert result.criteria == "BMI > 30 AND HbA1c > 7.5"
    assert result.tier == 3
    assert result.estimated_copay == 25.0


def test_check_coverage_covered_no_pa(test_db):
    """Test coverage check for covered drug not requiring PA"""
    result = check_coverage("P001", "Metformin", test_db)
    
    assert result.covered == True
    assert result.pa_required == False
    assert result.tier == 1
    assert result.estimated_copay == 10.0


def test_check_coverage_not_covered(test_db):
    """Test coverage check for non-covered drug"""
    # Add patient with BlueCross
    patient = Patient(
        patient_id="P002",
        name="Jane Smith",
        date_of_birth="1985-01-01",
        age=39,
        gender="Female",
        address={"street": "456 Oak St", "city": "Boston", "state": "MA", "zip": "02102"},
        phone="555-5678",
        email="jane@example.com",
        insurance_plan="BlueCross Silver",
        member_id="MEM789012",
        diagnoses=[{"name": "Type 2 Diabetes", "icd10": "E11.9"}],
        labs={"HbA1c": 7.8, "BMI": 29.5},
        treatment_history=[],
        allergies=["None known"]
    )
    test_db.add(patient)
    test_db.commit()
    
    result = check_coverage("P002", "Trulicity", test_db)
    
    assert result.covered == False
    assert result.pa_required == False


def test_check_coverage_patient_not_found(test_db):
    """Test coverage check for non-existent patient"""
    result = check_coverage("P999", "Ozempic", test_db)
    
    assert result.covered == False
    assert result.pa_required == False
    assert "Patient not found" in result.reason


def test_check_coverage_drug_not_in_formulary(test_db):
    """Test coverage check for drug not in formulary"""
    result = check_coverage("P001", "NonexistentDrug", test_db)
    
    assert result.covered == False
    assert result.pa_required == False
    assert "not in formulary" in result.reason


def test_check_coverage_by_plan(test_db):
    """Test plan-based coverage check"""
    result = check_coverage_by_plan("Aetna Gold", "Ozempic", test_db)
    
    assert result.covered == True
    assert result.pa_required == True
    assert result.criteria == "BMI > 30 AND HbA1c > 7.5"


def test_check_coverage_by_plan_not_found(test_db):
    """Test plan-based coverage check for non-existent combination"""
    result = check_coverage_by_plan("Unknown Plan", "Ozempic", test_db)
    
    assert result.covered == False
    assert result.pa_required == False

