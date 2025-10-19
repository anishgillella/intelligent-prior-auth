"""
Base LLM client interface for multiple provider support
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List


class BaseLLMClient(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def call(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call LLM API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens in response
            response_format: Optional JSON schema for structured output
            
        Returns:
            Response dict with choices, usage, and metadata
        """
        pass
    
    @abstractmethod
    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON response from LLM"""
        pass
