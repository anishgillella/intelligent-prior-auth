"""
Vector indexing using ChromaDB for semantic search of PA policies
"""
import chromadb
from pathlib import Path
import logging
import os
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorIndexManager:
    """Manages ChromaDB vector index for policy documents"""
    
    def __init__(self):
        """Initialize ChromaDB client with persistent storage"""
        # Use new ChromaDB API (0.4+) with PersistentClient
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory
        )
        
        # Get or create collection
        self.collection_name = "pa_policies"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """
        Add a document to the vector index
        
        Args:
            doc_id: Unique document identifier
            text: Document content to embed
            metadata: Optional metadata dict
        """
        if metadata is None:
            metadata = {}
        
        self.collection.add(
            ids=[doc_id],
            documents=[text],
            metadatas=[metadata]
        )
        
        logger.debug(f"Added document to index: {doc_id}")
    
    def add_documents_batch(
        self,
        documents: List[Dict[str, Any]]
    ) -> None:
        """
        Add multiple documents to the index
        
        Args:
            documents: List of dicts with keys: id, text, metadata (optional)
        """
        ids = []
        texts = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc["id"])
            texts.append(doc["text"])
            metadatas.append(doc.get("metadata", {}))
        
        self.collection.add(
            ids=ids,
            documents=texts,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to index")
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        distance_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Semantic search for similar documents
        
        Args:
            query: Search query (natural language)
            top_k: Number of results to return
            distance_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of matching documents with scores
        """
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k
        )
        
        # Parse results
        matches = []
        if results["ids"] and len(results["ids"]) > 0:
            for i, doc_id in enumerate(results["ids"][0]):
                distance = results["distances"][0][i] if results["distances"] else 0
                # ChromaDB returns distances, convert to similarity (1 - distance for cosine)
                similarity = 1 - distance
                
                if similarity >= distance_threshold:
                    matches.append({
                        "id": doc_id,
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": round(similarity, 4),
                        "distance": round(distance, 4)
                    })
        
        logger.debug(f"Search query: '{query}' returned {len(matches)} results")
        return matches
    
    def delete_collection(self) -> None:
        """Delete the current collection"""
        self.client.delete_collection(name=self.collection_name)
        logger.info(f"Deleted collection: {self.collection_name}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        count = self.collection.count()
        return {
            "collection_name": self.collection_name,
            "document_count": count,
            "persist_directory": settings.chroma_persist_directory
        }


# Global instance
_vector_manager: VectorIndexManager = None


def get_vector_manager() -> VectorIndexManager:
    """Get or create global vector manager instance"""
    global _vector_manager
    if _vector_manager is None:
        _vector_manager = VectorIndexManager()
    return _vector_manager


def initialize_vector_index() -> VectorIndexManager:
    """Initialize vector index"""
    return get_vector_manager()


def chunk_document(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Split document into chunks with overlap
    
    Args:
        text: Document text
        chunk_size: Size of each chunk (approximate)
        overlap: Overlap between chunks
        
    Returns:
        List of text chunks
    """
    chunks = []
    start = 0
    
    while start < len(text):
        # End at chunk_size, but try to break at sentence/line boundary
        end = start + chunk_size
        
        if end < len(text):
            # Look for nearest newline or period within reasonable range
            search_end = min(end + 50, len(text))
            last_break = max(
                text.rfind('\n', start, end),
                text.rfind('. ', start, end)
            )
            if last_break > start + chunk_size // 2:
                end = last_break + 1
        
        chunks.append(text[start:end].strip())
        
        # Move to next chunk with overlap
        start = end - overlap
    
    return [c for c in chunks if c]  # Filter empty chunks
