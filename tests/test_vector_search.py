"""
Unit tests for vector search functionality
"""
import pytest
from app.data.vector_index import VectorIndexManager, chunk_document


@pytest.fixture
def vector_manager():
    """Create a test vector manager with in-memory collection"""
    manager = VectorIndexManager()
    # Clear any existing documents
    try:
        manager.delete_collection()
    except:
        pass
    manager = VectorIndexManager()
    return manager


def test_chunk_document():
    """Test document chunking"""
    text = "This is a test document. " * 100
    chunks = chunk_document(text, chunk_size=200, overlap=50)
    
    assert len(chunks) > 0
    assert all(isinstance(c, str) for c in chunks)
    assert all(len(c) > 0 for c in chunks)


def test_add_single_document(vector_manager):
    """Test adding a single document"""
    vector_manager.add_document(
        doc_id="test_1",
        text="Ozempic is a GLP-1 agonist for Type 2 Diabetes with BMI > 30",
        metadata={"drug": "Ozempic", "plan": "Aetna Gold"}
    )
    
    stats = vector_manager.get_collection_stats()
    assert stats["document_count"] == 1


def test_add_batch_documents(vector_manager):
    """Test adding multiple documents"""
    documents = [
        {
            "id": "doc1",
            "text": "Ozempic requires BMI > 30 and HbA1c > 7.5",
            "metadata": {"drug": "Ozempic", "plan": "Aetna"}
        },
        {
            "id": "doc2",
            "text": "Trulicity requires failed metformin therapy",
            "metadata": {"drug": "Trulicity", "plan": "BlueCross"}
        },
        {
            "id": "doc3",
            "text": "Both drugs require Type 2 Diabetes diagnosis",
            "metadata": {"drug": "Both", "plan": "All"}
        }
    ]
    
    vector_manager.add_documents_batch(documents)
    
    stats = vector_manager.get_collection_stats()
    assert stats["document_count"] == 3


def test_semantic_search(vector_manager):
    """Test semantic search functionality"""
    # Add documents
    documents = [
        {
            "id": "ozempic_1",
            "text": "Ozempic (semaglutide) is a GLP-1 receptor agonist. Coverage requires BMI > 30, HbA1c > 7.5, and failed metformin therapy.",
            "metadata": {"drug": "Ozempic", "plan": "Aetna Gold"}
        },
        {
            "id": "trulicity_1",
            "text": "Trulicity (dulaglutide) is a GLP-1 agonist. Authorization needed for Type 2 Diabetes with two failed oral agents.",
            "metadata": {"drug": "Trulicity", "plan": "BlueCross"}
        },
        {
            "id": "metformin_1",
            "text": "Metformin is a first-line oral antidiabetic agent. Typically no prior auth required.",
            "metadata": {"drug": "Metformin", "plan": "All"}
        }
    ]
    
    vector_manager.add_documents_batch(documents)
    
    # Search for diabetes medications
    results = vector_manager.search("diabetes oral medication requirements", top_k=2)
    
    assert len(results) > 0
    assert all("id" in r and "similarity" in r and "text" in r for r in results)


def test_search_with_threshold(vector_manager):
    """Test search with similarity threshold"""
    documents = [
        {
            "id": "doc1",
            "text": "Patient with BMI > 30 and Type 2 Diabetes",
            "metadata": {"drug": "Ozempic"}
        },
        {
            "id": "doc2",
            "text": "Completely unrelated document about pizza recipes",
            "metadata": {"drug": "Other"}
        }
    ]
    
    vector_manager.add_documents_batch(documents)
    
    # Search with high threshold
    results = vector_manager.search(
        "BMI diabetes criteria",
        top_k=5,
        distance_threshold=0.5  # Only return highly similar
    )
    
    # Should filter out unrelated document
    assert all("diabetes" in r["text"].lower() or "bmi" in r["text"].lower() for r in results)


def test_get_collection_stats(vector_manager):
    """Test getting collection statistics"""
    documents = [
        {"id": f"doc{i}", "text": f"Test document {i}", "metadata": {"index": i}}
        for i in range(5)
    ]
    
    vector_manager.add_documents_batch(documents)
    
    stats = vector_manager.get_collection_stats()
    
    assert "collection_name" in stats
    assert "document_count" in stats
    assert stats["document_count"] == 5
    assert "persist_directory" in stats


def test_search_empty_collection(vector_manager):
    """Test searching in empty collection"""
    results = vector_manager.search("test query")
    
    assert isinstance(results, list)
    assert len(results) == 0


def test_metadata_preservation(vector_manager):
    """Test that metadata is preserved during indexing and search"""
    metadata = {
        "source_file": "test_policy.txt",
        "plan": "Aetna Gold",
        "drug": "Ozempic",
        "chunk_index": 5
    }
    
    vector_manager.add_document(
        doc_id="test_doc",
        text="Test document with metadata",
        metadata=metadata
    )
    
    results = vector_manager.search("metadata", top_k=1)
    
    assert len(results) > 0
    assert results[0]["metadata"]["plan"] == "Aetna Gold"
    assert results[0]["metadata"]["drug"] == "Ozempic"
