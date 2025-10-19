"""
Graph RAG Analytics Module

High-level graph queries for clinical decision-making and pattern analysis
"""
from typing import Dict, List, Any, Optional
import logging

from app.data.graph_index import get_graph_manager

logger = logging.getLogger(__name__)


class GraphAnalytics:
    """Provides high-level graph queries for clinical insights"""
    
    def __init__(self):
        self.graph = get_graph_manager()
    
    def get_patient_context(self, patient_id: str) -> Dict[str, Any]:
        """Get comprehensive patient context from graph"""
        if not self.graph.driver:
            return {}
        
        context = {
            "patient_id": patient_id,
            "similar_patients": self.graph.find_similar_patients(patient_id, limit=10),
            "treatment_history": self.graph.get_patient_treatment_chain(patient_id),
        }
        
        return context
    
    def get_drug_eligibility_context(self, patient_id: str, drug_name: str) -> Dict[str, Any]:
        """Get drug eligibility context from graph"""
        if not self.graph.driver:
            return {}
        
        eligibility = self.graph.find_drug_eligibility_path(patient_id, drug_name)
        
        if eligibility:
            # Get treatment patterns for this drug
            patterns = self.graph.find_treatment_patterns(limit=5)
            
            return {
                "patient_id": patient_id,
                "drug_name": drug_name,
                "plan_name": eligibility.get("plan_name"),
                "pa_required": eligibility.get("pa_required"),
                "criteria": eligibility.get("criteria"),
                "patient_diagnoses": eligibility.get("diagnoses", []),
                "treatment_patterns": patterns,
                "similar_patients": self.graph.find_similar_patients(patient_id, limit=5),
            }
        
        return {}
    
    def get_approval_confidence_boost(self, patient_id: str, drug_name: str) -> Dict[str, Any]:
        """Calculate approval confidence based on graph patterns"""
        if not self.graph.driver:
            return {
                "confidence_boost": 0,
                "evidence": "Graph DB not available",
                "similar_patient_approvals": 0
            }
        
        # Get similar patients
        similar = self.graph.find_similar_patients(patient_id, limit=20)
        
        if not similar:
            return {
                "confidence_boost": 0,
                "evidence": "No similar patients found",
                "similar_patient_count": 0
            }
        
        # Count how many would qualify for this drug
        # This is a simplified metric - in production you'd track actual approval outcomes
        confidence_boost = min(0.15, len(similar) * 0.01)  # Max 15% boost
        
        return {
            "confidence_boost": confidence_boost,
            "similar_patient_count": len(similar),
            "evidence": f"Based on {len(similar)} similar patients in network"
        }
    
    def get_treatment_recommendation_from_patterns(self, 
                                                   patient_diagnoses: List[str],
                                                   failed_drugs: List[str]) -> Dict[str, Any]:
        """Get treatment recommendations from historical patterns"""
        if not self.graph.driver:
            return {
                "recommendations": [],
                "source": "Pattern analysis not available"
            }
        
        patterns = self.graph.find_treatment_patterns(limit=10)
        
        if not patterns:
            return {
                "recommendations": [],
                "source": "No treatment patterns found",
                "message": "Insufficient historical data"
            }
        
        # Filter patterns that are relevant (initial drug in failed_drugs)
        relevant_patterns = [
            p for p in patterns 
            if p.get("initial_drug") in failed_drugs
        ]
        
        return {
            "recommendations": relevant_patterns[:3],  # Top 3 patterns
            "source": "Graph pattern analysis",
            "total_patterns_analyzed": len(patterns),
            "relevant_patterns": len(relevant_patterns)
        }


# Global analytics instance
_analytics: Optional[GraphAnalytics] = None


def get_graph_analytics() -> GraphAnalytics:
    """Get or create graph analytics instance"""
    global _analytics
    if _analytics is None:
        _analytics = GraphAnalytics()
    return _analytics
