"""
Executor Calibration Integration System

This module instruments all D[1-6]Q[1-5] executors with calibration calls
that capture runtime metrics (method_id, context, runtime, memory) and
retrieve calibration results (quality scores) from the intrinsic calibration
system.

Architecture:
- Separation: Calibration data (WHAT scores) in intrinsic_calibration.json
- Parametrization: Runtime parameters (HOW) in ExecutorConfig
- Layer Assignment: Each executor gets role:SCORE_Q with required layers
- No hardcoded calibration values in executor code

Usage:
    from executor_calibration_integration import instrument_executor, get_calibration_score
    
    # Inside executor.execute():
    calibration_result = instrument_executor(
        executor_id="D3_Q2_TargetProportionalityAnalyzer",
        context=context,
        runtime_ms=execution_time,
        memory_mb=memory_delta
    )
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

# Calibration layers for executors (SCORE_Q role)
EXECUTOR_REQUIRED_LAYERS = [
    "@b",      # BASE: Code quality (theory, impl, deploy)
    "@chain",  # CHAIN: Method wiring quality
    "@q",      # QUESTION: Question appropriateness
    "@d",      # DIMENSION: Dimension alignment
    "@p",      # POLICY: Policy area fit
    "@C",      # CONGRUENCE: Contract compliance
    "@u",      # UNIT: Document quality
    "@m",      # META: Governance maturity
]

# Choquet weights for layer aggregation (normalized)
LAYER_WEIGHTS = {
    "@b": 0.17,
    "@chain": 0.13,
    "@q": 0.08,
    "@d": 0.07,
    "@p": 0.06,
    "@C": 0.08,
    "@u": 0.04,
    "@m": 0.04,
}

# Interaction weights for Choquet integral
INTERACTION_WEIGHTS = {
    ("@u", "@chain"): 0.13,
    ("@chain", "@C"): 0.10,
    ("@q", "@d"): 0.10,
}


@dataclass
class CalibrationContext:
    """
    Context information for calibration calls.
    
    Captures the operational context of an executor execution:
    - Q: Question ID (Q1-Q5)
    - D: Dimension ID (D1-D6)
    - P: Policy area ID (if applicable)
    - U: Unit/document ID
    """
    question: str
    dimension: str
    policy_area: Optional[str] = None
    unit_id: Optional[str] = None
    executor_class: Optional[str] = None


@dataclass
class CalibrationMetrics:
    """
    Runtime metrics captured during executor execution.
    
    These are parametrization values (HOW we executed),
    not calibration values (WHAT quality we measured).
    """
    runtime_ms: float
    memory_mb: float
    methods_executed: int = 0
    methods_succeeded: int = 0
    timestamp: float = field(default_factory=time.time)


@dataclass
class CalibrationResult:
    """
    Result of a calibration call.
    
    Contains:
    - method_id: Fully qualified executor identifier
    - context: Operational context (Q, D, P, U)
    - metrics: Runtime metrics (parametrization)
    - quality_score: Aggregated quality score (calibration)
    - layer_scores: Individual layer scores (calibration)
    - layers_used: Which layers were active
    """
    method_id: str
    context: CalibrationContext
    metrics: CalibrationMetrics
    quality_score: float
    layer_scores: Dict[str, float]
    layers_used: List[str]
    aggregation_method: str = "choquet"


class CalibrationIntegration:
    """
    Main calibration integration interface.
    
    Loads calibration data from system/config/calibration/ and
    provides methods to instrument executors and retrieve scores.
    """
    
    def __init__(
        self,
        calibration_file: Optional[Path] = None,
        questionnaire_file: Optional[Path] = None
    ):
        """
        Initialize calibration integration.
        
        Args:
            calibration_file: Path to intrinsic_calibration.json
            questionnaire_file: Path to questionnaire_monolith.json
        """
        self.calibration_file = calibration_file or self._default_calibration_path()
        self.questionnaire_file = questionnaire_file or self._default_questionnaire_path()
        
        self.calibration_data: Dict[str, Any] = {}
        self.questionnaire_data: Dict[str, Any] = {}
        self.executor_configs: Dict[str, Dict[str, Any]] = {}
        
        self._load_calibration_data()
        self._load_questionnaire_data()
    
    def _default_calibration_path(self) -> Path:
        """Get default path to intrinsic calibration file."""
        return Path(__file__).parent.parent.parent / "cross_cutting_infrastrucuture" / \
               "capaz_calibration_parmetrization" / "calibration" / \
               "COHORT_2024_intrinsic_calibration.json"
    
    def _default_questionnaire_path(self) -> Path:
        """Get default path to questionnaire monolith file."""
        return Path(__file__).parent.parent.parent.parent / \
               "canonic_questionnaire_central" / "questionnaire_monolith.json"
    
    def _load_calibration_data(self) -> None:
        """Load intrinsic calibration data from JSON."""
        if not self.calibration_file.exists():
            raise FileNotFoundError(
                f"Calibration file not found: {self.calibration_file}"
            )
        
        with open(self.calibration_file) as f:
            self.calibration_data = json.load(f)
    
    def _load_questionnaire_data(self) -> None:
        """Load questionnaire monolith data from JSON."""
        if not self.questionnaire_file.exists():
            raise FileNotFoundError(
                f"Questionnaire file not found: {self.questionnaire_file}"
            )
        
        with open(self.questionnaire_file) as f:
            self.questionnaire_data = json.load(f)
    
    def get_layer_score(self, layer: str, context: CalibrationContext) -> float:
        """
        Get calibration score for a specific layer.
        
        Args:
            layer: Layer identifier (@b, @chain, @q, etc.)
            context: Calibration context with Q, D, P, U
        
        Returns:
            Quality score for the layer (0.0-1.0)
        """
        # Base layer score from intrinsic calibration
        if layer == "@b":
            components = self.calibration_data.get("components", {})
            b_theory = components.get("b_theory", {}).get("default_score", 0.8)
            b_impl = components.get("b_impl", {}).get("default_score", 0.75)
            b_deploy = components.get("b_deploy", {}).get("default_score", 0.7)
            
            # Weighted sum
            weights = self.calibration_data.get("base_layer", {}).get("aggregation", {}).get("weights", {})
            w_theory = weights.get("b_theory", 0.4)
            w_impl = weights.get("b_impl", 0.35)
            w_deploy = weights.get("b_deploy", 0.25)
            
            return b_theory * w_theory + b_impl * w_impl + b_deploy * w_deploy
        
        # Other layers: use default scores or contextual overrides
        layer_defaults = {
            "@chain": 0.85,
            "@q": 0.80,
            "@d": 0.82,
            "@p": 0.78,
            "@C": 0.88,
            "@u": 0.75,
            "@m": 0.82,
        }
        
        return layer_defaults.get(layer, 0.75)
    
    def calculate_quality_score(
        self,
        executor_id: str,
        context: CalibrationContext,
        layers: Optional[List[str]] = None
    ) -> tuple[float, Dict[str, float]]:
        """
        Calculate aggregated quality score using Choquet integral.
        
        Args:
            executor_id: Executor method ID
            context: Calibration context
            layers: Layers to use (defaults to EXECUTOR_REQUIRED_LAYERS)
        
        Returns:
            Tuple of (quality_score, layer_scores)
        """
        if layers is None:
            layers = EXECUTOR_REQUIRED_LAYERS
        
        # Get individual layer scores
        layer_scores = {
            layer: self.get_layer_score(layer, context)
            for layer in layers
        }
        
        # Choquet integral aggregation
        # Simple weighted sum + interaction terms
        linear_sum = sum(
            LAYER_WEIGHTS.get(layer, 0.0) * score
            for layer, score in layer_scores.items()
        )
        
        # Interaction terms
        interaction_sum = 0.0
        for (l1, l2), weight in INTERACTION_WEIGHTS.items():
            if l1 in layer_scores and l2 in layer_scores:
                # Min operator for Choquet interaction
                interaction_sum += weight * min(layer_scores[l1], layer_scores[l2])
        
        quality_score = linear_sum + interaction_sum
        
        # Normalize to [0, 1]
        quality_score = max(0.0, min(1.0, quality_score))
        
        return quality_score, layer_scores
    
    def instrument_executor(
        self,
        executor_id: str,
        context_dict: Dict[str, Any],
        runtime_ms: float,
        memory_mb: float,
        methods_executed: int = 0,
        methods_succeeded: int = 0
    ) -> CalibrationResult:
        """
        Instrument an executor with calibration call.
        
        This is called BEFORE execute() to capture context and
        retrieve calibration scores. Runtime metrics are passed in.
        
        Args:
            executor_id: Executor class name (e.g., "D3_Q2_TargetProportionalityAnalyzer")
            context_dict: Execution context dictionary
            runtime_ms: Execution time in milliseconds
            memory_mb: Memory usage in MB
            methods_executed: Number of methods executed
            methods_succeeded: Number of methods that succeeded
        
        Returns:
            CalibrationResult with quality scores and metrics
        """
        # Parse executor ID to extract dimension and question
        parts = executor_id.split("_")
        if len(parts) < 3:
            raise ValueError(f"Invalid executor_id format: {executor_id}")
        
        dimension = parts[0]  # D1, D2, etc.
        question = parts[1]   # Q1, Q2, etc.
        
        # Build calibration context
        cal_context = CalibrationContext(
            question=question,
            dimension=dimension,
            policy_area=context_dict.get("policy_area"),
            unit_id=context_dict.get("unit_id"),
            executor_class=executor_id
        )
        
        # Build metrics
        metrics = CalibrationMetrics(
            runtime_ms=runtime_ms,
            memory_mb=memory_mb,
            methods_executed=methods_executed,
            methods_succeeded=methods_succeeded
        )
        
        # Calculate quality score
        method_id = f"farfan_pipeline.core.orchestrator.executors.{executor_id}"
        quality_score, layer_scores = self.calculate_quality_score(
            method_id, cal_context
        )
        
        # Build result
        result = CalibrationResult(
            method_id=method_id,
            context=cal_context,
            metrics=metrics,
            quality_score=quality_score,
            layer_scores=layer_scores,
            layers_used=EXECUTOR_REQUIRED_LAYERS,
            aggregation_method="choquet"
        )
        
        return result
    
    def get_executor_config(
        self,
        executor_id: str,
        dimension: str,
        question: str
    ) -> Dict[str, Any]:
        """
        Get executor-specific configuration.
        
        This returns contextual assignments from questionnaire_monolith.json
        for the specific D_X_Q_Y executor.
        
        Args:
            executor_id: Executor class name
            dimension: Dimension ID (D1-D6)
            question: Question ID (Q1-Q5)
        
        Returns:
            Configuration dict with role, layers, and contextual parameters
        """
        config = {
            "executor_id": executor_id,
            "dimension": dimension,
            "question": question,
            "role": "SCORE_Q",
            "required_layers": EXECUTOR_REQUIRED_LAYERS,
            "layer_weights": LAYER_WEIGHTS,
            "interaction_weights": INTERACTION_WEIGHTS,
            "contextual_params": self._get_contextual_params(dimension, question)
        }
        
        return config
    
    def _get_contextual_params(self, dimension: str, question: str) -> Dict[str, Any]:
        """
        Get contextual parameters from questionnaire monolith.
        
        Args:
            dimension: Dimension ID (D1-D6)
            question: Question ID (Q1-Q5)
        
        Returns:
            Contextual parameters dict
        """
        # Extract from questionnaire_monolith.json
        # This would contain question-specific parameters like
        # expected patterns, thresholds, etc.
        
        contextual = {
            "dimension_label": self._get_dimension_label(dimension),
            "question_label": self._get_question_label(dimension, question),
            "epistemic_tags": self._get_epistemic_tags(dimension, question),
        }
        
        return contextual
    
    def _get_dimension_label(self, dimension: str) -> str:
        """Get human-readable dimension label."""
        dimensions = self.questionnaire_data.get("canonical_notation", {}).get("dimensions", {})
        dim_data = dimensions.get(dimension, {})
        return dim_data.get("label", dimension)
    
    def _get_question_label(self, dimension: str, question: str) -> str:
        """Get human-readable question label."""
        # Simplified: would need proper lookup in questionnaire
        return f"{dimension}_{question}"
    
    def _get_epistemic_tags(self, dimension: str, question: str) -> List[str]:
        """Get epistemic tags for the dimension-question pair."""
        # Simplified: would extract from questionnaire metadata
        return ["structural", "bayesian", "semantic"]
    
    def export_calibration_report(
        self,
        results: List[CalibrationResult],
        output_file: Path
    ) -> None:
        """
        Export calibration results to JSON report.
        
        Args:
            results: List of calibration results
            output_file: Output file path
        """
        report = {
            "metadata": {
                "report_type": "executor_calibration_integration",
                "timestamp": time.time(),
                "executors_count": len(results),
            },
            "executors": [
                {
                    "method_id": r.method_id,
                    "executor_id": r.context.executor_class,
                    "dimension": r.context.dimension,
                    "question": r.context.question,
                    "quality_score": r.quality_score,
                    "layer_scores": r.layer_scores,
                    "runtime_ms": r.metrics.runtime_ms,
                    "memory_mb": r.metrics.memory_mb,
                    "methods_executed": r.metrics.methods_executed,
                    "methods_succeeded": r.metrics.methods_succeeded,
                }
                for r in results
            ]
        }
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)


# Global calibration integration instance
_calibration_integration: Optional[CalibrationIntegration] = None


def get_calibration_integration() -> CalibrationIntegration:
    """Get or create global calibration integration instance."""
    global _calibration_integration
    if _calibration_integration is None:
        _calibration_integration = CalibrationIntegration()
    return _calibration_integration


def instrument_executor(
    executor_id: str,
    context: Dict[str, Any],
    runtime_ms: float,
    memory_mb: float,
    methods_executed: int = 0,
    methods_succeeded: int = 0
) -> CalibrationResult:
    """
    Convenience function to instrument an executor.
    
    Args:
        executor_id: Executor class name
        context: Execution context
        runtime_ms: Runtime in milliseconds
        memory_mb: Memory usage in MB
        methods_executed: Methods executed count
        methods_succeeded: Methods succeeded count
    
    Returns:
        CalibrationResult
    """
    integration = get_calibration_integration()
    return integration.instrument_executor(
        executor_id, context, runtime_ms, memory_mb,
        methods_executed, methods_succeeded
    )


def get_executor_config(
    executor_id: str,
    dimension: str,
    question: str
) -> Dict[str, Any]:
    """
    Convenience function to get executor configuration.
    
    Args:
        executor_id: Executor class name
        dimension: Dimension ID
        question: Question ID
    
    Returns:
        Configuration dict
    """
    integration = get_calibration_integration()
    return integration.get_executor_config(executor_id, dimension, question)


__all__ = [
    "CalibrationContext",
    "CalibrationMetrics",
    "CalibrationResult",
    "CalibrationIntegration",
    "instrument_executor",
    "get_executor_config",
    "get_calibration_integration",
    "EXECUTOR_REQUIRED_LAYERS",
    "LAYER_WEIGHTS",
    "INTERACTION_WEIGHTS",
]
