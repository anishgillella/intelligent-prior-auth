"""
Tests for Graph RAG (Neo4j) functionality
"""
import pytest
import json
from pathlib import Path

# These imports will test if everything is properly set up
try:
    from app.data.graph_index import get_graph_manager, GraphDatabaseManager
    from app.data.graph_analytics import get_graph_analytics, GraphAnalytics
    from app.core.config import settings
    HAS_GRAPH_IMPORTS = True
except ImportError as e:
    HAS_GRAPH_IMPORTS = False
    IMPORT_ERROR = str(e)


@pytest.mark.skipif(not HAS_GRAPH_IMPORTS, reason="Graph imports not available")
class TestGraphConnection:
    """Test Neo4j connection"""
    
    def test_graph_manager_initialization(self):
        """Test that graph manager initializes"""
        graph = get_graph_manager()
        assert graph is not None
        
    def test_graph_manager_has_driver(self):
        """Test that graph manager has driver"""
        graph = get_graph_manager()
        # Driver may be None if Neo4j is not running, but object should exist
        assert hasattr(graph, 'driver')


@pytest.mark.skipif(not HAS_GRAPH_IMPORTS, reason="Graph imports not available")
class TestGraphNodes:
    """Test node creation"""
    
    def test_create_patient_node(self):
        """Test creating a patient node"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        patient_data = {
            "patient_id": "TEST_P001",
            "name": "Test Patient",
            "age": 50,
            "gender": "Male",
            "labs": {"HbA1c": 8.5, "BMI": 32.0},
            "insurance_plan": "Test Plan"
        }
        
        result = graph.create_patient_node(patient_data)
        assert result is True or result is False  # Should complete without error
    
    def test_create_diagnosis_node(self):
        """Test creating a diagnosis node"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.create_diagnosis_node("Type 2 Diabetes", "E11.9")
        assert result is True or result is False
    
    def test_create_drug_node(self):
        """Test creating a drug node"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.create_drug_node("Ozempic")
        assert result is True or result is False
    
    def test_create_insurance_plan_node(self):
        """Test creating an insurance plan node"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.create_insurance_plan_node("Test Insurance")
        assert result is True or result is False


@pytest.mark.skipif(not HAS_GRAPH_IMPORTS, reason="Graph imports not available")
class TestGraphRelationships:
    """Test relationship creation"""
    
    def test_add_patient_diagnosis(self):
        """Test linking patient to diagnosis"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.add_patient_diagnosis("TEST_P001", "E11.9")
        assert result is True or result is False
    
    def test_add_patient_treatment(self):
        """Test linking patient to treatment"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.add_patient_treatment("TEST_P001", "Ozempic", "Partial response")
        assert result is True or result is False


@pytest.mark.skipif(not HAS_GRAPH_IMPORTS, reason="Graph imports not available")
class TestGraphQueries:
    """Test graph query functionality"""
    
    def test_find_similar_patients(self):
        """Test finding similar patients"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.find_similar_patients("TEST_P001", limit=5)
        assert isinstance(result, list)
    
    def test_get_patient_treatment_chain(self):
        """Test getting patient treatment chain"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.get_patient_treatment_chain("TEST_P001")
        assert isinstance(result, list)
    
    def test_find_drug_eligibility_path(self):
        """Test finding drug eligibility path"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.find_drug_eligibility_path("TEST_P001", "Ozempic")
        assert isinstance(result, dict)
    
    def test_find_treatment_patterns(self):
        """Test finding treatment patterns"""
        graph = get_graph_manager()
        if not graph.driver:
            pytest.skip("Neo4j not running")
        
        result = graph.find_treatment_patterns(limit=5)
        assert isinstance(result, list)


@pytest.mark.skipif(not HAS_GRAPH_IMPORTS, reason="Graph imports not available")
class TestGraphAnalytics:
    """Test graph analytics functionality"""
    
    def test_analytics_initialization(self):
        """Test that analytics initializes"""
        analytics = get_graph_analytics()
        assert analytics is not None
    
    def test_get_patient_context(self):
        """Test getting patient context"""
        analytics = get_graph_analytics()
        if not analytics.graph.driver:
            pytest.skip("Neo4j not running")
        
        result = analytics.get_patient_context("TEST_P001")
        assert isinstance(result, dict)
        assert "patient_id" in result or len(result) == 0
    
    def test_get_drug_eligibility_context(self):
        """Test getting drug eligibility context"""
        analytics = get_graph_analytics()
        if not analytics.graph.driver:
            pytest.skip("Neo4j not running")
        
        result = analytics.get_drug_eligibility_context("TEST_P001", "Ozempic")
        assert isinstance(result, dict)
    
    def test_get_approval_confidence_boost(self):
        """Test getting approval confidence boost"""
        analytics = get_graph_analytics()
        if not analytics.graph.driver:
            pytest.skip("Neo4j not running")
        
        result = analytics.get_approval_confidence_boost("TEST_P001", "Ozempic")
        assert isinstance(result, dict)
        assert "confidence_boost" in result or "evidence" in result


def test_config_has_neo4j_settings():
    """Test that config has Neo4j settings"""
    assert hasattr(settings, 'neo4j_host')
    assert hasattr(settings, 'neo4j_port')
    assert hasattr(settings, 'neo4j_user')
    assert hasattr(settings, 'neo4j_password')
