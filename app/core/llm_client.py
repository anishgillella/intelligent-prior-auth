"""
LLM Client - Main entry point for LLM operations
Supports: Cerebras (default), OpenRouter (fallback)
"""
import logging
from typing import Optional
from app.core.config import settings
from app.core.llm_base import BaseLLMClient

logger = logging.getLogger(__name__)

_llm_client: Optional[BaseLLMClient] = None


def get_llm_client() -> BaseLLMClient:
    """
    Get or create the LLM client based on configuration
    
    Returns:
        Initialized LLM client (Cerebras or OpenRouter)
    """
    global _llm_client
    
    if _llm_client is not None:
        return _llm_client
    
    provider = settings.llm_provider.lower()
    logger.info(f"Initializing LLM provider: {provider}")
    
    if provider == "cerebras":
        from app.core.llm_cerebras import CerebrasLLMClient
        _llm_client = CerebrasLLMClient()
        
    elif provider == "openrouter":
        from app.core.llm_openrouter import OpenRouterLLMClient
        _llm_client = OpenRouterLLMClient()
        
    else:
        raise ValueError(
            f"Unknown LLM provider: {provider}. "
            f"Supported: 'cerebras' (default), 'openrouter'"
        )
    
    logger.info(f"LLM provider initialized: {provider}")
    return _llm_client
