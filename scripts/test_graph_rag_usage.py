"""
Example usage of Graph RAG for clinical decision making

This script demonstrates how to use the Graph RAG components
to enhance clinical decisions with network analysis.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.graph_analytics import get_graph_analytics
from app.data.graph_index import get_graph_manager


def example_patient_context():
    """Example: Get comprehensive patient context"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Get Patient Context")
    print("="*70)
    
    analytics = get_graph_analytics()
    patient_context = analytics.get_patient_context("P001")
    
    if patient_context:
        print(f"Patient: P001")
        print(f"Similar patients found: {len(patient_context.get('similar_patients', []))}")
        print(f"Treatment history entries: {len(patient_context.get('treatment_history', []))}")
        
        if patient_context.get('similar_patients'):
            print("\nSimilar Patients:")
            for similar in patient_context['similar_patients'][:3]:
                print(f"  - {similar.get('patient_id')}: Age {similar.get('age')}, "
                      f"HbA1c {similar.get('hba1c')}, Shared diagnoses: {similar.get('shared_diagnoses', 0)}")
    else:
        print("✅ Method works but no data yet (Neo4j not running or empty)")


def example_drug_eligibility():
    """Example: Check drug eligibility with graph context"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Drug Eligibility with Graph Context")
    print("="*70)
    
    analytics = get_graph_analytics()
    eligibility = analytics.get_drug_eligibility_context("P001", "Ozempic")
    
    if eligibility:
        print(f"Patient: P001")
        print(f"Drug: Ozempic")
        print(f"Insurance Plan: {eligibility.get('plan_name')}")
        print(f"PA Required: {eligibility.get('pa_required')}")
        print(f"Coverage Criteria: {eligibility.get('criteria')}")
        print(f"Patient Diagnoses: {', '.join(eligibility.get('patient_diagnoses', []))}")
        
        if eligibility.get('treatment_patterns'):
            print(f"\nHistorical Treatment Patterns: {len(eligibility['treatment_patterns'])} found")
        
        if eligibility.get('similar_patients'):
            print(f"Similar Patients: {len(eligibility['similar_patients'])} found")
    else:
        print("✅ Method works but no data yet (Neo4j not running or empty)")


def example_confidence_boost():
    """Example: Get approval confidence boost from network"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Approval Confidence Boost")
    print("="*70)
    
    analytics = get_graph_analytics()
    boost = analytics.get_approval_confidence_boost("P001", "Ozempic")
    
    print(f"Patient: P001")
    print(f"Drug: Ozempic")
    print(f"Confidence Boost: +{boost.get('confidence_boost', 0)*100:.1f}%")
    print(f"Evidence: {boost.get('evidence')}")
    print(f"Based on {boost.get('similar_patient_count', 0)} similar patients")


def example_treatment_patterns():
    """Example: Get treatment patterns from graph"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Treatment Patterns")
    print("="*70)
    
    graph = get_graph_manager()
    patterns = graph.find_treatment_patterns(limit=5)
    
    if patterns:
        print(f"Found {len(patterns)} treatment patterns:\n")
        for pattern in patterns:
            print(f"  {pattern.get('initial_drug')} → {pattern.get('follow_up_drug')}")
            print(f"    Patient count: {pattern.get('patient_count')}")
    else:
        print("✅ Method works but no patterns yet (Neo4j not running or empty)")


def example_direct_queries():
    """Example: Direct Neo4j queries"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Direct Graph Queries")
    print("="*70)
    
    graph = get_graph_manager()
    
    if not graph.driver:
        print("Neo4j not running - skipping direct queries")
        return
    
    # Example 1: Similar patients
    print("\n1. Finding similar patients:")
    similar = graph.find_similar_patients("P001", limit=5)
    if similar:
        for patient in similar:
            print(f"  - {patient}")
    else:
        print("  (No data yet)")
    
    # Example 2: Treatment chain
    print("\n2. Patient treatment chain:")
    chain = graph.get_patient_treatment_chain("P001")
    if chain:
        for treatment in chain:
            print(f"  - {treatment}")
    else:
        print("  (No data yet)")
    
    # Example 3: Drug eligibility
    print("\n3. Drug eligibility path:")
    path = graph.find_drug_eligibility_path("P001", "Ozempic")
    if path:
        print(f"  {path}")
    else:
        print("  (Patient/drug not in graph yet)")


if __name__ == "__main__":
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  GRAPH RAG USAGE EXAMPLES".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")
    
    try:
        example_patient_context()
        example_drug_eligibility()
        example_confidence_boost()
        example_treatment_patterns()
        example_direct_queries()
        
        print("\n" + "="*70)
        print("✅ All examples completed successfully!")
        print("="*70)
        print("\nNOTE: Examples show 'no data' because Neo4j needs to be running")
        print("and migration script needs to be executed:")
        print("  1. docker-compose up -d")
        print("  2. python scripts/migrate_to_graph.py")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        import traceback
        traceback.print_exc()
