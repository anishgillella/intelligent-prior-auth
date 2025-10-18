"""
API routes for semantic policy search
"""
from fastapi import APIRouter, Query, Path
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.data.vector_index import get_vector_manager

router = APIRouter(prefix="/policies", tags=["Policy Search"])


# ==================== Response Models ====================

class SearchResultItem(BaseModel):
    """Single search result"""
    id: str
    text: str
    metadata: Dict[str, Any]
    similarity: float
    distance: float


class PolicySearchResponse(BaseModel):
    """Response model for policy search"""
    query: str
    results_count: int
    results: List[SearchResultItem]
    message: Optional[str] = None


class VectorIndexStats(BaseModel):
    """Vector index statistics"""
    collection_name: str
    document_count: int
    persist_directory: str


# ==================== Endpoints ====================

@router.get("/search", response_model=PolicySearchResponse)
async def search_policies(
    query: str = Query(..., description="Search query (natural language)"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
    min_similarity: float = Query(0.0, ge=0.0, le=1.0, description="Minimum similarity threshold")
):
    """
    Semantic search for PA policy documents
    
    - **query**: Natural language search query (e.g., "Ozempic BMI diabetes criteria")
    - **top_k**: Number of results to return (1-20)
    - **min_similarity**: Minimum similarity score threshold (0-1)
    
    Returns matching policy sections with similarity scores
    """
    vector_manager = get_vector_manager()
    
    results = vector_manager.search(
        query=query,
        top_k=top_k,
        distance_threshold=min_similarity
    )
    
    return PolicySearchResponse(
        query=query,
        results_count=len(results),
        results=[SearchResultItem(**r) for r in results],
        message=f"Found {len(results)} relevant policy sections"
    )


@router.get("/search/drug/{drug}", response_model=PolicySearchResponse)
async def search_policies_by_drug(
    drug: str = Path(..., description="Drug name (e.g., Ozempic, Trulicity)"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
):
    """
    Search for PA policies specific to a drug
    
    - **drug**: Drug name to search for
    - **top_k**: Number of results to return
    
    Returns policy sections related to the specified drug
    """
    vector_manager = get_vector_manager()
    
    query = f"{drug} prior authorization coverage criteria requirements"
    
    results = vector_manager.search(
        query=query,
        top_k=top_k,
        distance_threshold=0.0
    )
    
    # Filter results to drug-related ones
    filtered_results = [
        r for r in results 
        if drug.lower() in r["metadata"].get("drug", "").lower()
    ]
    
    # If no exact matches, return top results
    if not filtered_results:
        filtered_results = results[:top_k]
    
    return PolicySearchResponse(
        query=query,
        results_count=len(filtered_results),
        results=[SearchResultItem(**r) for r in filtered_results],
        message=f"Found {len(filtered_results)} policy sections for {drug}"
    )


@router.get("/search/plan/{plan}", response_model=PolicySearchResponse)
async def search_policies_by_plan(
    plan: str = Path(..., description="Insurance plan name"),
    top_k: int = Query(5, ge=1, le=20, description="Number of results"),
):
    """
    Search for PA policies from a specific insurance plan
    
    - **plan**: Insurance plan name (e.g., Aetna Gold, BlueCross Silver)
    - **top_k**: Number of results to return
    
    Returns all policy sections from the specified plan
    """
    vector_manager = get_vector_manager()
    
    query = f"{plan} insurance coverage prior authorization requirements"
    
    results = vector_manager.search(
        query=query,
        top_k=top_k * 2,  # Get more to filter
        distance_threshold=0.0
    )
    
    # Filter results to plan-related ones
    filtered_results = [
        r for r in results 
        if plan.lower() in r["metadata"].get("plan", "").lower()
    ]
    
    # If no exact matches, return top results
    if not filtered_results:
        filtered_results = results[:top_k]
    
    return PolicySearchResponse(
        query=query,
        results_count=len(filtered_results),
        results=[SearchResultItem(**r) for r in filtered_results],
        message=f"Found {len(filtered_results)} policy sections for {plan}"
    )


@router.get("/stats", response_model=VectorIndexStats)
async def get_index_stats():
    """
    Get statistics about the vector index
    
    Returns information about indexed documents and storage location
    """
    vector_manager = get_vector_manager()
    stats = vector_manager.get_collection_stats()
    
    return VectorIndexStats(**stats)
