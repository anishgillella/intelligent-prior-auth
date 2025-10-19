"""
Prompt Tracking and Tuning Utilities
Monitors prompt performance and integrates with Langfuse for optimization
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.monitoring import LLMCallMonitor, PromptTuningTracker, get_langfuse_client

logger = logging.getLogger(__name__)


class PromptPerformanceTracker:
    """Tracks and analyzes prompt performance metrics"""
    
    def __init__(self):
        """Initialize prompt tracker"""
        self.prompts = {}
    
    def track_prompt_execution(
        self,
        prompt_name: str,
        prompt_type: str,  # 'clinical_qualification', 'prior_authorization', etc.
        input_data: Dict[str, Any],
        output: str,
        metrics: Dict[str, Any],
        variant: Optional[str] = None
    ):
        """
        Track a prompt execution for tuning and analysis
        
        Args:
            prompt_name: Name of the prompt (e.g., 'PA_NARRATIVE_GENERATION')
            prompt_type: Type/category of prompt
            input_data: Input variables used for the prompt
            output: LLM output
            metrics: Performance metrics (latency, tokens, cost, etc.)
            variant: Optional variant identifier for A/B testing
        """
        try:
            execution_log = {
                "timestamp": datetime.now().isoformat(),
                "prompt_name": prompt_name,
                "prompt_type": prompt_type,
                "variant": variant or "default",
                "input": input_data,
                "output": output,
                "metrics": metrics,
            }
            
            # Store locally
            if prompt_name not in self.prompts:
                self.prompts[prompt_name] = []
            self.prompts[prompt_name].append(execution_log)
            
            # Track with Langfuse
            PromptTuningTracker.track_prompt_variant(
                prompt_name=prompt_name,
                variant=variant or "default",
                input_data=input_data,
                output=output,
                metrics=metrics
            )
            
            logger.info(
                f"Prompt tracked: {prompt_name} (variant: {variant or 'default'}) | "
                f"Latency: {metrics.get('latency_ms', 0):.0f}ms"
            )
            
        except Exception as e:
            logger.error(f"Failed to track prompt execution: {e}")
    
    def get_prompt_stats(self, prompt_name: str) -> Dict[str, Any]:
        """Get statistics for a specific prompt"""
        if prompt_name not in self.prompts:
            return {}
        
        executions = self.prompts[prompt_name]
        if not executions:
            return {}
        
        latencies = [e["metrics"].get("latency_ms", 0) for e in executions]
        costs = [e["metrics"].get("cost", 0) for e in executions]
        tokens = [e["metrics"].get("tokens_used", {}).get("total", 0) for e in executions]
        
        return {
            "execution_count": len(executions),
            "avg_latency_ms": sum(latencies) / len(latencies) if latencies else 0,
            "min_latency_ms": min(latencies) if latencies else 0,
            "max_latency_ms": max(latencies) if latencies else 0,
            "total_cost": sum(costs),
            "avg_cost": sum(costs) / len(costs) if costs else 0,
            "total_tokens": sum(tokens),
            "avg_tokens": sum(tokens) / len(tokens) if tokens else 0,
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get statistics for all tracked prompts"""
        return {
            prompt_name: self.get_prompt_stats(prompt_name)
            for prompt_name in self.prompts.keys()
        }


class PromptVariantTester:
    """A/B testing framework for prompt variants"""
    
    @staticmethod
    def test_variant(
        prompt_name: str,
        variant_a: str,
        variant_b: str,
        test_input: Dict[str, Any],
        llm_client,
        variant_a_name: str = "variant_a",
        variant_b_name: str = "variant_b"
    ) -> Dict[str, Any]:
        """
        Test two prompt variants and compare results
        
        Args:
            prompt_name: Name of the prompt being tested
            variant_a: First prompt variant template
            variant_b: Second prompt variant template
            test_input: Test input data
            llm_client: LLM client to use for testing
            variant_a_name: Name for variant A (default: 'variant_a')
            variant_b_name: Name for variant B (default: 'variant_b')
        
        Returns:
            Comparison results with metrics
        """
        try:
            import time
            
            # Test Variant A
            start_a = time.time()
            messages_a = [
                {"role": "system", "content": variant_a},
                {"role": "user", "content": str(test_input)}
            ]
            result_a = llm_client.call(messages_a)
            latency_a = time.time() - start_a
            
            # Test Variant B
            start_b = time.time()
            messages_b = [
                {"role": "system", "content": variant_b},
                {"role": "user", "content": str(test_input)}
            ]
            result_b = llm_client.call(messages_b)
            latency_b = time.time() - start_b
            
            # Track both variants with Langfuse
            PromptTuningTracker.track_prompt_variant(
                prompt_name=prompt_name,
                variant=variant_a_name,
                input_data=test_input,
                output=result_a["content"],
                metrics={
                    "latency_ms": result_a.get("latency_ms", latency_a * 1000),
                    "tokens": result_a.get("tokens_used", {}),
                    "cost": result_a.get("cost", 0),
                }
            )
            
            PromptTuningTracker.track_prompt_variant(
                prompt_name=prompt_name,
                variant=variant_b_name,
                input_data=test_input,
                output=result_b["content"],
                metrics={
                    "latency_ms": result_b.get("latency_ms", latency_b * 1000),
                    "tokens": result_b.get("tokens_used", {}),
                    "cost": result_b.get("cost", 0),
                }
            )
            
            comparison = {
                "prompt_name": prompt_name,
                "test_input": test_input,
                variant_a_name: {
                    "output": result_a["content"],
                    "latency_ms": result_a.get("latency_ms"),
                    "tokens": result_a.get("tokens_used", {}),
                    "cost": result_a.get("cost", 0),
                },
                variant_b_name: {
                    "output": result_b["content"],
                    "latency_ms": result_b.get("latency_ms"),
                    "tokens": result_b.get("tokens_used", {}),
                    "cost": result_b.get("cost", 0),
                },
                "comparison": {
                    "faster_variant": variant_a_name if result_a.get("latency_ms", latency_a * 1000) < result_b.get("latency_ms", latency_b * 1000) else variant_b_name,
                    "cheaper_variant": variant_a_name if result_a.get("cost", 0) < result_b.get("cost", 0) else variant_b_name,
                    "latency_diff_ms": abs(result_a.get("latency_ms", latency_a * 1000) - result_b.get("latency_ms", latency_b * 1000)),
                    "cost_diff": abs(result_a.get("cost", 0) - result_b.get("cost", 0)),
                }
            }
            
            logger.info(
                f"Prompt variant test completed: {prompt_name} | "
                f"Faster: {comparison['comparison']['faster_variant']} | "
                f"Cheaper: {comparison['comparison']['cheaper_variant']}"
            )
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to test prompt variants: {e}")
            raise


# Global tracker instance
_prompt_tracker = None


def get_prompt_tracker() -> PromptPerformanceTracker:
    """Get or create global prompt tracker"""
    global _prompt_tracker
    if _prompt_tracker is None:
        _prompt_tracker = PromptPerformanceTracker()
    return _prompt_tracker
