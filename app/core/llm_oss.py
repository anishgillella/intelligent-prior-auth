"""
Open Source Model LLM client implementation (Ollama or vLLM)
"""
import logging
import time
import json
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.llm_base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class OSSLLMClient(BaseLLMClient):
    """Open Source Model client via Ollama or vLLM"""
    
    def __init__(self):
        """Initialize OSS LLM client"""
        try:
            import openai
            self.openai_lib = openai
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )
        
        self.provider = settings.oss_provider  # "ollama" or "vllm"
        self.model = settings.oss_model
        self.base_url = settings.oss_base_url
        self.timeout = settings.llm_timeout
        
        logger.info(
            f"OSS LLM Client initialized with provider: {self.provider}, "
            f"model: {self.model}, base_url: {self.base_url}"
        )
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Call OSS LLM API via Ollama or vLLM
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens in response
            response_format: Optional JSON schema for structured output
            
        Returns:
            Response dict with choices, usage, and metadata
        """
        
        # Use defaults if not provided
        if temperature is None:
            temperature = settings.llm_temperature
        if max_tokens is None:
            max_tokens = settings.llm_max_tokens
        
        start_time = time.time()
        
        try:
            # Create OpenAI-compatible client
            import httpx
            http_client = httpx.Client(proxy=None)
            
            client = self.openai_lib.OpenAI(
                api_key="not-needed" if self.provider == "ollama" else "dummy-key",
                base_url=self.base_url,
                http_client=http_client
            )
            
            # Build kwargs
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": float(temperature),
                "max_tokens": int(max_tokens),
            }
            
            # Add response format if provided and supported
            if response_format and self.provider == "vllm":
                kwargs["response_format"] = response_format
            
            # Make API call
            response = client.chat.completions.create(**kwargs)
            
            latency = time.time() - start_time
            
            # Extract response data
            result = {
                "content": response.choices[0].message.content,
                "model": self.model,
                "provider": self.provider,
                "latency_ms": round(latency * 1000, 2),
                "tokens_used": {
                    "input": getattr(response.usage, "prompt_tokens", 0),
                    "output": getattr(response.usage, "completion_tokens", 0),
                    "total": getattr(response.usage, "total_tokens", 0),
                },
                "cost": 0.0,  # OSS models running locally have no API cost
            }
            
            logger.info(
                f"OSS LLM call successful: {self.provider}/{self.model} | "
                f"Tokens: {result['tokens_used']['total']} | "
                f"Latency: {result['latency_ms']}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"OSS LLM API error ({self.provider}): {e}")
            raise
    
    def parse_json_response(self, content: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM
        
        Args:
            content: LLM response content
            
        Returns:
            Parsed JSON dict
            
        Raises:
            ValueError: If content is not valid JSON
        """
        try:
            # Try to extract JSON if wrapped in markdown
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            
            return json.loads(content.strip())
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON in LLM response: {content}") from e
