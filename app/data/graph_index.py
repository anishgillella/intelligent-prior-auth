"""
Graph Database Manager using Neo4j for relationship-based RAG
Handles patient networks, approval patterns, and similarity analysis
"""
from neo4j import GraphDatabase, Session
from neo4j.exceptions import ServiceUnavailable
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class GraphDatabaseManager:
    """Manages Neo4j graph database for relationship-based queries"""
    
    def __init__(self):
        """Initialize Neo4j connection"""
        try:
            # Use cloud URI with SSL encryption
            self.driver = GraphDatabase.driver(
                settings.neo4j_uri,
                auth=(settings.neo4j_user, settings.neo4j_password),
                database=settings.neo4j_database
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("✅ Neo4j connection established")
        except ServiceUnavailable:
            logger.error("❌ Neo4j not available - Graph RAG disabled")
            self.driver = None
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
    
    # ==================== Node Creation ====================
    
    def create_patient_node(self, patient_data: Dict[str, Any]) -> bool:
        """Create or update patient node"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (p:Patient {patient_id: $patient_id})
                    SET p.name = $name,
                        p.age = $age,
                        p.gender = $gender,
                        p.hba1c = $hba1c,
                        p.bmi = $bmi,
                        p.insurance_plan = $insurance_plan,
                        p.updated_at = datetime()
                    RETURN p
                """, {
                    "patient_id": patient_data["patient_id"],
                    "name": patient_data["name"],
                    "age": patient_data["age"],
                    "gender": patient_data["gender"],
                    "hba1c": patient_data.get("labs", {}).get("HbA1c", 0),
                    "bmi": patient_data.get("labs", {}).get("BMI", 0),
                    "insurance_plan": patient_data["insurance_plan"]
                })
            logger.debug(f"Created patient node: {patient_data['patient_id']}")
            return True
        except Exception as e:
            logger.error(f"Error creating patient node: {e}")
            return False
    
    def create_diagnosis_node(self, diagnosis: str, icd10: str) -> bool:
        """Create or update diagnosis node"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (d:Diagnosis {icd10: $icd10})
                    SET d.name = $name
                    RETURN d
                """, {"icd10": icd10, "name": diagnosis})
            return True
        except Exception as e:
            logger.error(f"Error creating diagnosis node: {e}")
            return False
    
    def create_drug_node(self, drug_name: str) -> bool:
        """Create or update drug node"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (drug:Drug {name: $name})
                    RETURN drug
                """, {"name": drug_name})
            return True
        except Exception as e:
            logger.error(f"Error creating drug node: {e}")
            return False
    
    def create_insurance_plan_node(self, plan_name: str) -> bool:
        """Create or update insurance plan node"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MERGE (plan:InsurancePlan {name: $name})
                    RETURN plan
                """, {"name": plan_name})
            return True
        except Exception as e:
            logger.error(f"Error creating plan node: {e}")
            return False
    
    # ==================== Relationship Creation ====================
    
    def add_patient_diagnosis(self, patient_id: str, icd10: str) -> bool:
        """Link patient to diagnosis"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    MATCH (d:Diagnosis {icd10: $icd10})
                    MERGE (p)-[:HAS_DIAGNOSIS]->(d)
                """, {"patient_id": patient_id, "icd10": icd10})
            return True
        except Exception as e:
            logger.error(f"Error linking patient to diagnosis: {e}")
            return False
    
    def add_patient_insurance(self, patient_id: str, plan_name: str) -> bool:
        """Link patient to insurance plan"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    MATCH (plan:InsurancePlan {name: $plan_name})
                    MERGE (p)-[:ENROLLED_IN]->(plan)
                """, {"patient_id": patient_id, "plan_name": plan_name})
            return True
        except Exception as e:
            logger.error(f"Error linking patient to plan: {e}")
            return False
    
    def add_patient_treatment(self, patient_id: str, drug_name: str, outcome: str) -> bool:
        """Link patient to treatment drug"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                    MATCH (drug:Drug {name: $drug_name})
                    MERGE (p)-[r:TREATED_WITH]->(drug)
                    SET r.outcome = $outcome,
                        r.date = datetime()
                """, {
                    "patient_id": patient_id,
                    "drug_name": drug_name,
                    "outcome": outcome
                })
            return True
        except Exception as e:
            logger.error(f"Error linking patient to treatment: {e}")
            return False
    
    def add_plan_drug_coverage(self, plan_name: str, drug_name: str, 
                               pa_required: bool, criteria: str = None) -> bool:
        """Link insurance plan to drug coverage"""
        if not self.driver:
            return False
        
        try:
            with self.driver.session() as session:
                session.run("""
                    MATCH (plan:InsurancePlan {name: $plan_name})
                    MATCH (drug:Drug {name: $drug_name})
                    MERGE (plan)-[r:COVERS]->(drug)
                    SET r.pa_required = $pa_required,
                        r.criteria = $criteria
                """, {
                    "plan_name": plan_name,
                    "drug_name": drug_name,
                    "pa_required": pa_required,
                    "criteria": criteria
                })
            return True
        except Exception as e:
            logger.error(f"Error linking plan to drug: {e}")
            return False
    
    # ==================== Graph Queries ====================
    
    def find_similar_patients(self, patient_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find patients with similar diagnoses and clinical parameters"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                results = session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})-[:HAS_DIAGNOSIS]->(d:Diagnosis)
                    MATCH (similar:Patient)-[:HAS_DIAGNOSIS]->(d)
                    WHERE similar.patient_id <> p.patient_id
                      AND abs(similar.age - p.age) < 5
                      AND abs(similar.hba1c - p.hba1c) < 1.0
                      AND abs(similar.bmi - p.bmi) < 2.0
                    WITH similar, COUNT(d) as shared_diagnoses
                    ORDER BY shared_diagnoses DESC
                    LIMIT $limit
                    RETURN similar.patient_id as patient_id,
                           similar.name as name,
                           similar.age as age,
                           similar.hba1c as hba1c,
                           similar.bmi as bmi,
                           shared_diagnoses
                """, {"patient_id": patient_id, "limit": limit})
                
                return [dict(record) for record in results]
        except Exception as e:
            logger.error(f"Error finding similar patients: {e}")
            return []
    
    def get_patient_treatment_chain(self, patient_id: str) -> List[Dict[str, Any]]:
        """Get patient's treatment history chain"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                results = session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})-[r:TREATED_WITH]->(drug:Drug)
                    RETURN drug.name as drug_name,
                           r.outcome as outcome,
                           r.date as date
                    ORDER BY r.date DESC
                """, {"patient_id": patient_id})
                
                return [dict(record) for record in results]
        except Exception as e:
            logger.error(f"Error getting treatment chain: {e}")
            return []
    
    def find_drug_eligibility_path(self, patient_id: str, drug_name: str) -> Dict[str, Any]:
        """Find if patient can access drug through insurance and clinical path"""
        if not self.driver:
            return {}
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Patient {patient_id: $patient_id})
                           -[:ENROLLED_IN]->(plan:InsurancePlan)
                           -[covers:COVERS]->(drug:Drug {name: $drug_name})
                    MATCH (p)-[:HAS_DIAGNOSIS]->(diagnosis:Diagnosis)
                    RETURN plan.name as plan_name,
                           covers.pa_required as pa_required,
                           covers.criteria as criteria,
                           collect(diagnosis.name) as diagnoses
                    LIMIT 1
                """, {"patient_id": patient_id, "drug_name": drug_name})
                
                record = result.single()
                if record:
                    return dict(record)
                return {}
        except Exception as e:
            logger.error(f"Error finding drug eligibility: {e}")
            return {}
    
    def get_approval_statistics(self, drug_name: str) -> Dict[str, Any]:
        """Get approval statistics for a drug"""
        if not self.driver:
            return {}
        
        try:
            with self.driver.session() as session:
                result = session.run("""
                    MATCH (p:Patient)-[:TREATED_WITH]->(drug:Drug {name: $drug_name})
                    RETURN drug.name as drug_name,
                           COUNT(p) as patient_count,
                           COUNT(CASE WHEN p.approval_status = 'APPROVED' THEN 1 END) as approved_count
                    LIMIT 1
                """, {"drug_name": drug_name})
                
                record = result.single()
                if record:
                    return dict(record)
                return {}
        except Exception as e:
            logger.error(f"Error getting approval statistics: {e}")
            return {}
    
    def find_treatment_patterns(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find common treatment sequences (failed → approved)"""
        if not self.driver:
            return []
        
        try:
            with self.driver.session() as session:
                results = session.run("""
                    MATCH (p:Patient)-[r1:TREATED_WITH {outcome: 'Inadequate response'}]->(drug1:Drug)
                    MATCH (p)-[r2:TREATED_WITH {outcome: 'Partial response'}]->(drug2:Drug)
                    WHERE drug1 <> drug2
                    RETURN drug1.name as initial_drug,
                           drug2.name as follow_up_drug,
                           COUNT(p) as patient_count
                    ORDER BY patient_count DESC
                    LIMIT $limit
                """, {"limit": limit})
                
                return [dict(record) for record in results]
        except Exception as e:
            logger.error(f"Error finding treatment patterns: {e}")
            return []


# ==================== Global Instance ====================

_graph_manager: Optional[GraphDatabaseManager] = None


def get_graph_manager() -> GraphDatabaseManager:
    """Get or create global graph manager instance"""
    global _graph_manager
    if _graph_manager is None:
        _graph_manager = GraphDatabaseManager()
    return _graph_manager


def initialize_graph_db() -> GraphDatabaseManager:
    """Initialize graph database"""
    return get_graph_manager()
