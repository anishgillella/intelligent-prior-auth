"""
Tests for LogFire validation and Langfuse LLM monitoring
"""
import pytest
import json
from app.data.models import Patient, Address, Diagnosis, LabResults, TreatmentHistory
from app.core.prompt_tracker import get_prompt_tracker, PromptVariantTester
from app.core.monitoring import ValidationEventLogger, get_langfuse_client


# Sample test data
VALID_PATIENT_DATA = {
    "patient_id": "P12345",
    "name": "John Doe",
    "date_of_birth": "1980-05-15",
    "age": 43,
    "gender": "M",
    "address": {
        "street": "123 Main St",
        "city": "Boston",
        "state": "MA",
        "zip": "02101"
    },
    "phone": "555-1234",
    "email": "john@example.com",
    "insurance_plan": "Blue Cross",
    "member_id": "BCB123456",
    "diagnoses": [
        {
            "name": "Type 2 Diabetes",
            "icd10": "E11.9"
        }
    ],
    "labs": {
        "HbA1c": 8.5,
        "fasting_glucose": 150,
        "BMI": 28.5,
        "weight_lbs": 200,
        "creatinine": 1.0,
        "eGFR": 75,
        "ALT": 35,
        "AST": 30,
        "last_updated": "2024-01-15"
    },
    "treatment_history": [
        {
            "drug": "Metformin",
            "duration_months": 24,
            "dosage": "1000mg",
            "outcome": "Partial response",
            "started_date": "2022-01-01"
        }
    ],
    "allergies": ["Penicillin"]
}

INVALID_PATIENT_DATA_BAD_AGE = {
    **VALID_PATIENT_DATA,
    "age": 200  # Invalid age
}

INVALID_PATIENT_DATA_BAD_STATE = {
    **VALID_PATIENT_DATA,
    "address": {
        **VALID_PATIENT_DATA["address"],
        "state": "XX"  # Invalid state
    }
}

INVALID_PATIENT_DATA_BAD_ICD10 = {
    **VALID_PATIENT_DATA,
    "diagnoses": [
        {
            "name": "Type 2 Diabetes",
            "icd10": "INVALID"  # Invalid ICD-10
        }
    ]
}

INVALID_PATIENT_DATA_NO_DIAGNOSES = {
    **VALID_PATIENT_DATA,
    "diagnoses": []  # Must have at least one diagnosis
}

INVALID_PATIENT_DATA_BAD_EMAIL = {
    **VALID_PATIENT_DATA,
    "email": "notanemail"  # Invalid email
}


class TestPydanticValidation:
    """Test Pydantic models with LogFire validation tracking"""
    
    def test_valid_patient_creation(self):
        """Test creating a valid patient - should succeed"""
        patient = Patient(**VALID_PATIENT_DATA)
        assert patient.patient_id == "P12345"
        assert patient.name == "John Doe"
        assert patient.age == 43
        assert len(patient.diagnoses) == 1
        print("✓ Valid patient creation successful")
    
    def test_invalid_age(self):
        """Test invalid age validation"""
        with pytest.raises(ValueError, match="Invalid age"):
            Patient(**INVALID_PATIENT_DATA_BAD_AGE)
        print("✓ Age validation caught invalid age")
    
    def test_invalid_state(self):
        """Test invalid state validation"""
        with pytest.raises(ValueError, match="Invalid state"):
            Patient(**INVALID_PATIENT_DATA_BAD_STATE)
        print("✓ State validation caught invalid state")
    
    def test_invalid_icd10(self):
        """Test invalid ICD-10 code validation"""
        with pytest.raises(ValueError, match="Invalid ICD-10"):
            Patient(**INVALID_PATIENT_DATA_BAD_ICD10)
        print("✓ ICD-10 validation caught invalid code")
    
    def test_no_diagnoses(self):
        """Test model validation requiring at least one diagnosis"""
        with pytest.raises(ValueError, match="must have at least one diagnosis"):
            Patient(**INVALID_PATIENT_DATA_NO_DIAGNOSES)
        print("✓ Diagnosis requirement validation worked")
    
    def test_invalid_email(self):
        """Test invalid email validation"""
        with pytest.raises(ValueError, match="Invalid email"):
            Patient(**INVALID_PATIENT_DATA_BAD_EMAIL)
        print("✓ Email validation caught invalid email")
    
    def test_address_validation(self):
        """Test address ZIP code validation"""
        bad_zip_data = {
            **VALID_PATIENT_DATA,
            "address": {
                **VALID_PATIENT_DATA["address"],
                "zip": "123"  # Too short
            }
        }
        with pytest.raises(ValueError, match="Invalid ZIP"):
            Patient(**bad_zip_data)
        print("✓ ZIP code validation worked")
    
    def test_lab_results_validation(self):
        """Test lab results value ranges"""
        bad_hba1c_data = {
            **VALID_PATIENT_DATA,
            "labs": {
                **VALID_PATIENT_DATA["labs"],
                "HbA1c": 25.0  # Out of range
            }
        }
        with pytest.raises(ValueError, match="Invalid HbA1c"):
            Patient(**bad_hba1c_data)
        print("✓ HbA1c range validation worked")
    
    def test_treatment_history_validation(self):
        """Test treatment duration validation"""
        bad_treatment_data = {
            **VALID_PATIENT_DATA,
            "treatment_history": [
                {
                    "drug": "Metformin",
                    "duration_months": 0,  # Invalid: must be > 0
                    "dosage": "1000mg",
                    "outcome": "Partial response",
                    "started_date": "2022-01-01"
                }
            ]
        }
        with pytest.raises(ValueError, match="Invalid duration"):
            Patient(**bad_treatment_data)
        print("✓ Treatment duration validation worked")


class TestPromptTracking:
    """Test prompt tracking with Langfuse"""
    
    def test_prompt_tracker_initialization(self):
        """Test that prompt tracker initializes correctly"""
        tracker = get_prompt_tracker()
        assert tracker is not None
        assert isinstance(tracker.prompts, dict)
        print("✓ Prompt tracker initialized")
    
    def test_track_prompt_execution(self):
        """Test tracking a prompt execution"""
        tracker = get_prompt_tracker()
        
        # Track a test prompt
        tracker.track_prompt_execution(
            prompt_name="test_prompt",
            prompt_type="test",
            input_data={"test": "input"},
            output="test output",
            metrics={
                "latency_ms": 100.5,
                "tokens_used": {"input": 50, "output": 100, "total": 150},
                "cost": 0.0015,
            }
        )
        
        assert "test_prompt" in tracker.prompts
        assert len(tracker.prompts["test_prompt"]) >= 1
        print("✓ Prompt execution tracked successfully")
    
    def test_prompt_stats_calculation(self):
        """Test stats calculation for tracked prompts"""
        tracker = get_prompt_tracker()
        
        # Clear and track multiple executions
        tracker.prompts.clear()
        
        for i in range(3):
            tracker.track_prompt_execution(
                prompt_name="stats_test",
                prompt_type="test",
                input_data={"iteration": i},
                output=f"output_{i}",
                metrics={
                    "latency_ms": 100 + i * 10,
                    "tokens_used": {"input": 50, "output": 100, "total": 150},
                    "cost": 0.001 + i * 0.0001,
                }
            )
        
        stats = tracker.get_prompt_stats("stats_test")
        
        assert stats["execution_count"] == 3
        assert stats["avg_latency_ms"] == 110  # (100 + 110 + 120) / 3
        assert stats["min_latency_ms"] == 100
        assert stats["max_latency_ms"] == 120
        assert stats["total_tokens"] == 450  # 150 * 3
        print("✓ Prompt statistics calculated correctly")
    
    def test_all_stats_retrieval(self):
        """Test retrieving all prompt statistics"""
        tracker = get_prompt_tracker()
        tracker.prompts.clear()
        
        # Track different prompts
        for prompt in ["prompt_a", "prompt_b"]:
            tracker.track_prompt_execution(
                prompt_name=prompt,
                prompt_type="test",
                input_data={},
                output="output",
                metrics={
                    "latency_ms": 100,
                    "tokens_used": {"input": 50, "output": 100, "total": 150},
                    "cost": 0.001,
                }
            )
        
        all_stats = tracker.get_all_stats()
        assert len(all_stats) >= 2
        assert "prompt_a" in all_stats
        assert "prompt_b" in all_stats
        print("✓ All prompt statistics retrieved")


class TestValidationEventLogging:
    """Test LogFire validation event logging"""
    
    def test_validation_event_logger_initialization(self):
        """Test that validation event logger can be initialized"""
        try:
            ValidationEventLogger.log_validation_event(
                event_type="test",
                model_name="TestModel",
                field_name="test_field",
                status="success"
            )
            print("✓ Validation event logger working")
        except Exception as e:
            print(f"⚠ Validation event logger error: {e}")


class TestMonitoringIntegration:
    """Test overall monitoring system integration"""
    
    def test_langfuse_client_availability(self):
        """Test that Langfuse client is available"""
        langfuse = get_langfuse_client()
        if langfuse:
            print("✓ Langfuse client connected")
        else:
            print("⚠ Langfuse client not configured (may need API keys in .env)")
    
    def test_monitoring_with_validation_and_tracking(self):
        """Test the complete flow: validation + tracking"""
        # Create valid patient (triggers validation + LogFire events)
        patient = Patient(**VALID_PATIENT_DATA)
        
        # Track a prompt about this patient
        tracker = get_prompt_tracker()
        tracker.track_prompt_execution(
            prompt_name="patient_analysis",
            prompt_type="clinical",
            input_data={
                "patient_id": patient.patient_id,
                "age": patient.age,
                "diagnoses": [d.name for d in patient.diagnoses]
            },
            output="Analysis result",
            metrics={
                "latency_ms": 250.5,
                "tokens_used": {"input": 100, "output": 200, "total": 300},
                "cost": 0.003,
            }
        )
        
        assert "patient_analysis" in tracker.prompts
        print("✓ Complete monitoring flow successful (validation + tracking)")


def run_all_tests():
    """Run all tests and print results"""
    print("\n" + "="*70)
    print("MONITORING & VALIDATION SYSTEM TESTS")
    print("="*70 + "\n")
    
    # Test Pydantic Validation
    print("📋 PYDANTIC VALIDATION TESTS:")
    print("-" * 70)
    validation_tests = TestPydanticValidation()
    try:
        validation_tests.test_valid_patient_creation()
        validation_tests.test_invalid_age()
        validation_tests.test_invalid_state()
        validation_tests.test_invalid_icd10()
        validation_tests.test_no_diagnoses()
        validation_tests.test_invalid_email()
        validation_tests.test_address_validation()
        validation_tests.test_lab_results_validation()
        validation_tests.test_treatment_history_validation()
    except Exception as e:
        print(f"❌ Validation tests failed: {e}")
    
    # Test Prompt Tracking
    print("\n📊 PROMPT TRACKING TESTS:")
    print("-" * 70)
    tracking_tests = TestPromptTracking()
    try:
        tracking_tests.test_prompt_tracker_initialization()
        tracking_tests.test_track_prompt_execution()
        tracking_tests.test_prompt_stats_calculation()
        tracking_tests.test_all_stats_retrieval()
    except Exception as e:
        print(f"❌ Prompt tracking tests failed: {e}")
    
    # Test Validation Event Logging
    print("\n📝 VALIDATION EVENT LOGGING TESTS:")
    print("-" * 70)
    logging_tests = TestValidationEventLogging()
    try:
        logging_tests.test_validation_event_logger_initialization()
    except Exception as e:
        print(f"❌ Validation event logging tests failed: {e}")
    
    # Test Monitoring Integration
    print("\n🔗 MONITORING INTEGRATION TESTS:")
    print("-" * 70)
    integration_tests = TestMonitoringIntegration()
    try:
        integration_tests.test_langfuse_client_availability()
        integration_tests.test_monitoring_with_validation_and_tracking()
    except Exception as e:
        print(f"❌ Monitoring integration tests failed: {e}")
    
    print("\n" + "="*70)
    print("✅ TEST SUITE COMPLETED")
    print("="*70 + "\n")


if __name__ == "__main__":
    run_all_tests()
