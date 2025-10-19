"""
LLM Provider Factory - handles selection and initialization of different LLM backends
"""
import logging
from typing import Optional

from app.core.config import settings
from app.core.llm_base import BaseLLMClient

logger = logging.getLogger(__name__)


class LLMProviderFactory:
    """Factory for creating LLM client instances based on provider selection"""
    
    _instance: Optional[BaseLLMClient] = None
    _provider: str = ""
    
    @classmethod
    def get_client(cls) -> BaseLLMClient:
        """
        Get or create the appropriate LLM client based on configuration
        
        Returns:
            Initialized LLM client instance
            
        Raises:
            ValueError: If provider is not recognized or not configured
        """
        # Return cached instance if provider hasn't changed
        if cls._instance is not None and cls._provider == settings.llm_provider:
            return cls._instance
        
        provider = settings.llm_provider.lower()
        cls._provider = provider
        
        logger.info(f"Initializing LLM provider: {provider}")
        
        if provider == "cerebras":
            from app.core.llm_cerebras import CerebrasLLMClient
            cls._instance = CerebrasLLMClient()
            
        elif provider == "oss":
            from app.core.llm_oss import OSSLLMClient
            cls._instance = OSSLLMClient()
            
        elif provider == "openrouter":
            from app.core.llm_openrouter import OpenRouterLLMClient
            cls._instance = OpenRouterLLMClient()
            
        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Supported providers: 'cerebras', 'oss', 'openrouter'"
            )
        
        logger.info(f"LLM provider initialized successfully: {provider}")
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the cached client instance (useful for testing or provider switching)"""
        cls._instance = None
        cls._provider = ""
        logger.info("LLM provider factory reset")


def get_llm_client() -> BaseLLMClient:
    """
    Convenience function to get the global LLM client
    
    Returns:
        Initialized LLM client instance
    """
    return LLMProviderFactory.get_client()
