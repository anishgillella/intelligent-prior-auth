"""
Build ChromaDB vector index from PA policy documents

This script reads policy documents and indexes them for semantic search.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.data.vector_index import get_vector_manager, chunk_document
from app.core.config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_policy_documents():
    """Load policy documents from mock_data/policies/ directory"""
    policies_dir = Path(settings.mock_data_dir) / "policies"
    
    if not policies_dir.exists():
        logger.error(f"Policies directory not found: {policies_dir}")
        return []
    
    documents = []
    
    for policy_file in policies_dir.glob("*.txt"):
        logger.info(f"Loading policy: {policy_file.name}")
        
        with open(policy_file, 'r') as f:
            content = f.read()
        
        # Extract metadata from filename
        parts = policy_file.stem.split("_")
        plan = parts[0].replace("_", " ").title() if len(parts) > 0 else "Unknown"
        drug = parts[-2] if len(parts) >= 2 else "Unknown"
        
        # Chunk the document
        chunks = chunk_document(content, chunk_size=800, overlap=150)
        
        logger.info(f"  → Created {len(chunks)} chunks for {drug}")
        
        for i, chunk in enumerate(chunks):
            doc_id = f"{policy_file.stem}_chunk_{i}"
            documents.append({
                "id": doc_id,
                "text": chunk,
                "metadata": {
                    "source_file": policy_file.name,
                    "plan": plan,
                    "drug": drug,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
            })
    
    logger.info(f"\nLoaded {len(documents)} document chunks from {len(list(policies_dir.glob('*.txt')))} files")
    return documents


def main():
    """Main function to build vector index"""
    print("\n" + "=" * 60)
    print("🔍 BUILDING CHROMADB VECTOR INDEX")
    print("=" * 60 + "\n")
    
    # Get vector manager
    logger.info("Initializing ChromaDB...")
    vector_manager = get_vector_manager()
    
    # Check current collection stats
    stats = vector_manager.get_collection_stats()
    if stats["document_count"] > 0:
        logger.warning(f"⚠️  Collection already has {stats['document_count']} documents")
        logger.warning("   Clearing old collection...")
        vector_manager.delete_collection()
        vector_manager = get_vector_manager()  # Reinitialize
    
    # Load documents
    logger.info("\nLoading policy documents...")
    documents = load_policy_documents()
    
    if not documents:
        logger.error("❌ No documents found!")
        sys.exit(1)
    
    # Index documents
    logger.info(f"\nIndexing {len(documents)} document chunks...")
    vector_manager.add_documents_batch(documents)
    
    # Verify
    stats = vector_manager.get_collection_stats()
    
    print("\n" + "=" * 60)
    print("✅ VECTOR INDEX BUILD COMPLETE!")
    print("=" * 60)
    print(f"\nCollection: {stats['collection_name']}")
    print(f"Documents indexed: {stats['document_count']}")
    print(f"Persist directory: {stats['persist_directory']}")
    print("\n💡 Next Steps:")
    print("  1. Test vector search: python -m pytest tests/test_vector_search.py")
    print("  2. Start API: uvicorn app.main:app --reload")
    print("  3. Test endpoint: curl 'http://localhost:8000/policies/search?query=...'")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
