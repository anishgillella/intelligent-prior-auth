"""
LLM Client - Main entry point for LLM operations (supports multiple backends)
"""
from app.core.llm_factory import get_llm_client

# Re-export for backward compatibility
__all__ = ["get_llm_client"]
