"""
OpenRouter LLM client implementation
"""
import logging
import time
import json
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.llm_base import BaseLLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenRouterLLMClient(BaseLLMClient):
    """OpenRouter LLM client with retry and monitoring"""
    
    # Pricing per 1K tokens (as of 2024)
    PRICING = {
        "openai/gpt-4o": {"input": 0.005, "output": 0.015},
        "openai/gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "anthropic/claude-3.5-sonnet": {"input": 0.003, "output": 0.015},
        "meta-llama/llama-3.1-70b-instruct": {"input": 0.00054, "output": 0.00081},
    }
    
    def __init__(self):
        """Initialize LLM client"""
        try:
            import openai
            self.openai_lib = openai
        except ImportError:
            raise ImportError(
                "OpenAI SDK not installed. Install with: pip install openai"
            )
        
        self.api_key = settings.openrouter_api_key
        self.model = settings.openrouter_model
        self.base_url = settings.openrouter_base_url
        self.timeout = settings.llm_timeout
        
        if not self.api_key:
            logger.warning("OpenRouter API key not configured")
        
        logger.info(f"OpenRouter LLM Client initialized with model: {self.model}")
    
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
        Call OpenRouter API with retry logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Max tokens in response
            response_format: Optional JSON schema for structured output
            
        Returns:
            Response dict with choices, usage, and metadata
        """
        
        if not self.api_key:
            raise ValueError(
                "OpenRouter API key not configured. Set OPENROUTER_API_KEY environment variable."
            )
        
        # Use defaults if not provided
        if temperature is None:
            temperature = settings.llm_temperature
        if max_tokens is None:
            max_tokens = settings.llm_max_tokens
        
        start_time = time.time()
        
        try:
            # Create HTTP client with explicit proxy=None to prevent system proxy detection
            import httpx
            http_client = httpx.Client(proxy=None)
            
            # Create OpenAI client (compatible with OpenRouter)
            client = self.openai_lib.OpenAI(
                api_key=self.api_key,
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
            
            # Add response format if provided
            if response_format:
                kwargs["response_format"] = response_format
            
            # Make API call
            response = client.chat.completions.create(**kwargs)
            
            latency = time.time() - start_time
            
            # Extract response data
            result = {
                "content": response.choices[0].message.content,
                "model": self.model,
                "latency_ms": round(latency * 1000, 2),
                "tokens_used": {
                    "input": response.usage.prompt_tokens,
                    "output": response.usage.completion_tokens,
                    "total": response.usage.total_tokens,
                },
                "cost": self._calculate_cost(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                ),
            }
            
            logger.info(
                f"OpenRouter LLM call successful: {self.model} | "
                f"Tokens: {result['tokens_used']['total']} | "
                f"Latency: {result['latency_ms']}ms | "
                f"Cost: ${result['cost']:.6f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            raise
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost for tokens"""
        pricing = self.PRICING.get(self.model)
        
        if not pricing:
            logger.warning(f"Pricing not found for {self.model}")
            return 0.0
        
        cost = (
            (input_tokens / 1000) * pricing["input"] +
            (output_tokens / 1000) * pricing["output"]
        )
        
        return cost
    
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
