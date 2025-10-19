"""
Monitoring & Observability Module
Integrates LogFire for validation tracking and Langfuse for LLM call monitoring
"""
import logging
import time
import json
from typing import Dict, Any, Optional, List, Callable
from functools import wraps
from datetime import datetime
from app.core.config import settings

logger = logging.getLogger(__name__)

# Initialize LogFire if API key is available
logfire = None
langfuse_client = None
langfuse_handler = None

try:
    import logfire as logfire_module
    if settings.logfire_api_key:
        logfire_module.configure(token=settings.logfire_api_key)
        logfire = logfire_module
        logger.info("✓ LogFire initialized successfully")
    else:
        logger.warning("⚠ LogFire API key not configured")
except ImportError:
    logger.warning("⚠ LogFire not installed")
except Exception as e:
    logger.warning(f"⚠ LogFire initialization failed: {e}")

try:
    from langfuse import Langfuse
    from langfuse.decorators import langfuse_context
    
    if settings.langfuse_secret_key and settings.langfuse_public_key:
        langfuse_client = Langfuse(
            secret_key=settings.langfuse_secret_key,
            public_key=settings.langfuse_public_key,
            host=settings.langfuse_host,
        )
        logger.info("✓ Langfuse initialized successfully")
    else:
        logger.warning("⚠ Langfuse API keys not configured")
except ImportError:
    logger.warning("⚠ Langfuse not installed")
except Exception as e:
    logger.warning(f"⚠ Langfuse initialization failed: {e}")


class ValidationEventLogger:
    """Logs validation events to LogFire"""
    
    @staticmethod
    def log_validation_event(
        event_type: str,
        model_name: str,
        field_name: str,
        status: str,  # "success" or "error"
        details: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Log validation event to LogFire"""
        if not logfire:
            return
        
        event_data = {
            "event_type": event_type,
            "model": model_name,
            "field": field_name,
            "status": status,
            "timestamp": datetime.now().isoformat(),
        }
        
        if details:
            event_data["details"] = details
        
        if error_message:
            event_data["error"] = error_message
        
        try:
            logfire.info(
                f"validation_{status}",
                **event_data
            )
        except Exception as e:
            logger.error(f"Failed to log validation event: {e}")


class LLMCallMonitor:
    """Monitors and tracks LLM calls with Langfuse integration"""
    
    @staticmethod
    def monitor_llm_call(func: Callable) -> Callable:
        """Decorator to monitor LLM calls and track with Langfuse"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            call_id = None
            span = None
            
            try:
                # Extract relevant information
                messages = kwargs.get("messages", [])
                temperature = kwargs.get("temperature")
                max_tokens = kwargs.get("max_tokens")
                
                # Initialize Langfuse span if client is available
                if langfuse_client:
                    span = langfuse_client.start_span(
                        name=f"llm_call_{func.__name__}",
                        input={
                            "messages": messages,
                            "temperature": temperature,
                            "max_tokens": max_tokens,
                        }
                    )
                    call_id = span.span_id if hasattr(span, 'span_id') else None
                
                # Log input to LogFire
                if logfire:
                    logfire.info(
                        "llm_call_start",
                        function=func.__name__,
                        message_count=len(messages),
                        temperature=temperature,
                        max_tokens=max_tokens,
                        call_id=call_id,
                    )
                
                # Execute the LLM call
                result = func(*args, **kwargs)
                
                elapsed_time = time.time() - start_time
                
                # Log success to both systems
                if logfire:
                    logfire.info(
                        "llm_call_success",
                        function=func.__name__,
                        latency_ms=round(elapsed_time * 1000, 2),
                        tokens_used=result.get("tokens_used", {}),
                        cost=result.get("cost", 0),
                        call_id=call_id,
                    )
                
                # End Langfuse span with output
                if span:
                    span.update(
                        output={
                            "content": result.get("content", ""),
                            "model": result.get("model"),
                            "tokens_used": result.get("tokens_used", {}),
                            "cost": result.get("cost", 0),
                        },
                    )
                    langfuse_client.flush()
                
                return result
                
            except Exception as e:
                elapsed_time = time.time() - start_time
                
                # Log error to both systems
                if logfire:
                    logfire.error(
                        "llm_call_error",
                        function=func.__name__,
                        error=str(e),
                        latency_ms=round(elapsed_time * 1000, 2),
                        call_id=call_id,
                    )
                
                # End Langfuse span with error
                if span:
                    span.update(
                        output=None,
                    )
                    langfuse_client.flush()
                
                raise
        
        return wrapper
    
    @staticmethod
    def log_prompt_used(
        prompt_name: str,
        prompt_template: str,
        variables: Dict[str, Any],
        response: str,
        model: str,
        latency_ms: float,
        tokens_used: Dict[str, int],
        cost: float
    ):
        """Log prompt usage and performance to Langfuse for optimization"""
        if not langfuse_client:
            return
        
        try:
            span = langfuse_client.start_span(
                name=f"prompt_{prompt_name}",
                input={
                    "template_name": prompt_name,
                    "variables": variables,
                    "model": model,
                }
            )
            
            span.update(
                output={
                    "response": response,
                    "model": model,
                    "latency_ms": latency_ms,
                    "tokens_used": tokens_used,
                    "cost": cost,
                },
            )
            
            # Log to LogFire
            if logfire:
                logfire.info(
                    "prompt_used",
                    prompt_name=prompt_name,
                    model=model,
                    latency_ms=latency_ms,
                    tokens_used=tokens_used,
                    cost=cost,
                )
            
            langfuse_client.flush()
            
        except Exception as e:
            logger.error(f"Failed to log prompt usage: {e}")


class PromptTuningTracker:
    """Tracks prompt performance for A/B testing and optimization"""
    
    @staticmethod
    def track_prompt_variant(
        prompt_name: str,
        variant: str,
        input_data: Dict[str, Any],
        output: str,
        metrics: Dict[str, Any]
    ):
        """Track a prompt variant for tuning analysis"""
        if not langfuse_client:
            return
        
        try:
            span = langfuse_client.start_span(
                name=f"prompt_variant_{prompt_name}_{variant}",
                input={
                    "variant": variant,
                    "data": input_data,
                }
            )
            
            span.update(
                output={
                    "output": output,
                    "metrics": metrics,
                },
            )
            
            if logfire:
                logfire.info(
                    "prompt_variant_tracked",
                    prompt_name=prompt_name,
                    variant=variant,
                    metrics=metrics,
                )
            
            langfuse_client.flush()
            
        except Exception as e:
            logger.error(f"Failed to track prompt variant: {e}")


def initialize_monitoring():
    """Initialize monitoring systems on app startup"""
    logger.info("=" * 60)
    logger.info("MONITORING INITIALIZATION")
    logger.info("=" * 60)
    
    monitoring_status = {
        "logfire": bool(logfire and settings.logfire_api_key),
        "langfuse": bool(langfuse_client and settings.langfuse_secret_key),
        "enabled": settings.enable_monitoring,
    }
    
    logger.info(f"LogFire: {'✓ Enabled' if monitoring_status['logfire'] else '✗ Disabled'}")
    logger.info(f"Langfuse: {'✓ Enabled' if monitoring_status['langfuse'] else '✗ Disabled'}")
    logger.info(f"Monitoring: {'✓ Enabled' if monitoring_status['enabled'] else '✗ Disabled'}")
    logger.info("=" * 60)
    
    return monitoring_status


def get_langfuse_client():
    """Get Langfuse client instance"""
    return langfuse_client
