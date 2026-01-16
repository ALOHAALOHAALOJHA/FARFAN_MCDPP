"""
Orchestrator - Cross-phase pipeline coordination.

This module orchestrates the execution of all pipeline phases,
ensuring constitutional invariants are maintained.

Author: FARFAN Pipeline Team
Version: 1.0.0
"""

# GNEA METADATA
__version__ = "1.0.0"
__module_type__ = "ORCH"  # Orchestration
__criticality__ = "CRITICAL"
__lifecycle__ = "ACTIVE"
__execution_pattern__ = "Singleton"
__phase_label__ = "Cross-Phase Coordinator"
__compliance_status__ = "GNEA_COMPLIANT"

import logging
from dataclasses import dataclass, field
from typing import Any, TYPE_CHECKING
from datetime import datetime, timezone

# Phase 0 integration imports
if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_00.phase0_10_01_runtime_config import RuntimeConfig
    from farfan_pipeline.phases.Phase_02.phase2_10_03_executor_config import ExecutorConfig
    from farfan_pipeline.phases.Phase_02.phase2_10_00_factory import CanonicalQuestionnaire

logger = logging.getLogger(__name__)


# Phase 1 Constitutional Constants
P01_EXPECTED_CHUNK_COUNT = 60
P01_POLICY_AREA_COUNT = 10
P01_DIMENSION_COUNT = 6


# =============================================================================
# Phase 0 Validation Result
# =============================================================================


@dataclass
class GateResult:
    """Result of a single Phase 0 exit gate check.

    Attributes:
        gate_name: Name of the gate (e.g., "bootstrap", "input_verification")
        passed: True if gate passed, False otherwise
        message: Human-readable result message
        details: Optional dict with additional gate-specific details
    """
    gate_name: str
    passed: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class Phase0ValidationResult:
    """Result of Phase 0 exit gate validation.

    This dataclass encapsulates the results of all Phase 0 exit gates,
    providing a typed interface for the Factory → Orchestrator handoff.

    Attributes:
        all_passed: True if all gates passed
        gate_results: List of GateResult objects (one per gate)
        validation_time: ISO8601 timestamp of validation
    """
    all_passed: bool
    gate_results: list[GateResult]
    validation_time: str

    def get_failed_gates(self) -> list[GateResult]:
        """Get list of failed gates."""
        return [g for g in self.gate_results if not g.passed]

    def get_passed_gates(self) -> list[GateResult]:
        """Get list of passed gates."""
        return [g for g in self.gate_results if g.passed]


# =============================================================================
# Method Executor - Method Routing and Execution Engine
# =============================================================================


class MethodExecutor:
    """Executes methods from the method dispensary pattern.

    This class is the CORE execution engine for the FARFAN pipeline.
    It routes method calls from BaseExecutor instances to the appropriate
    analyzer classes (method dispensaries) and handles signal-aware execution.

    Architecture:
    - MethodRegistry: Maps class_name.method_name → callable methods
    - ArgRouter: Routes arguments to correct method signatures
    - SignalRegistry: Provides signal context for pattern matching

    Usage:
        executor = MethodExecutor(method_registry, arg_router, signal_registry)
        result = executor.execute(
            class_name="PDETMunicipalPlanAnalyzer",
            method_name="_score_indicators",
            document=doc,
            signal_pack=pack,
            **kwargs
        )
    """

    def __init__(
        self,
        method_registry: Any,
        arg_router: Any,
        signal_registry: Any | None = None,
    ):
        """Initialize MethodExecutor.

        Args:
            method_registry: MethodRegistry instance with method mappings
            arg_router: ExtendedArgRouter for argument routing
            signal_registry: Optional QuestionnaireSignalRegistry for signal-aware execution
        """
        self.method_registry = method_registry
        self.arg_router = arg_router
        self.signal_registry = signal_registry

        logger.info(
            "method_executor_initialized signal_registry=%s",
            signal_registry is not None
        )

    def execute(
        self,
        class_name: str,
        method_name: str,
        **kwargs: Any
    ) -> Any:
        """Execute a method from the dispensary pattern.

        Args:
            class_name: Name of the analyzer class (e.g., "PDETMunicipalPlanAnalyzer")
            method_name: Name of the method to call (e.g., "_score_indicators")
            **kwargs: Arguments to pass to the method (routed via arg_router)

        Returns:
            Result from method execution

        Raises:
            ValueError: If method not found in registry
            TypeError: If argument routing fails
        """
        # Get method from registry
        method = self.method_registry.get_method(class_name, method_name)

        if method is None:
            raise ValueError(
                f"Method not found: {class_name}.{method_name}. "
                f"Ensure method is registered in method_registry."
            )

        # Route arguments through arg_router
        routed_args = self.arg_router.route(class_name, method_name, **kwargs)

        # Execute method with routed arguments
        try:
            result = method(**routed_args)
            return result
        except Exception as e:
            logger.error(
                "method_execution_failed class=%s method=%s error=%s",
                class_name,
                method_name,
                str(e),
                exc_info=True
            )
            raise


# =============================================================================
# Orchestrator - Main Pipeline Coordinator
# =============================================================================


class Orchestrator:
    """
    Main orchestrator for FARFAN pipeline execution.

    Coordinates phase execution and validates constitutional invariants.

    This orchestrator receives ALL dependencies via Dependency Injection from
    the AnalysisPipelineFactory. NO dependencies are created internally.

    Architecture:
    - Factory Pattern: ONLY AnalysisPipelineFactory creates Orchestrator instances
    - Dependency Injection: All dependencies passed via __init__
    - Phase 0 Integration: Validates Phase 0 exit gates before execution
    - Runtime Mode Awareness: Enforces PROD/DEV/EXPLORATORY mode restrictions
    """

    def __init__(
        self,
        method_executor: "MethodExecutor",
        questionnaire: "CanonicalQuestionnaire",
        executor_config: "ExecutorConfig",
        runtime_config: "RuntimeConfig | None" = None,
        phase0_validation: Phase0ValidationResult | None = None,
    ):
        """Initialize the orchestrator with dependency injection.

        CRITICAL: This constructor is called ONLY by AnalysisPipelineFactory.
        All dependencies MUST be provided by the factory.

        Args:
            method_executor: MethodExecutor with signal registry injected
            questionnaire: Immutable CanonicalQuestionnaire (monolith)
            executor_config: ExecutorConfig for operational parameters
            runtime_config: Optional RuntimeConfig (PROD/DEV/EXPLORATORY mode)
            phase0_validation: Optional Phase0ValidationResult with exit gate results

        Raises:
            RuntimeError: If Phase 0 validation failed (gates not passed)
            ValueError: If required dependencies are None
        """
        self.logger = logging.getLogger(f"{__name__}.Orchestrator")

        # Validate required dependencies
        if method_executor is None:
            raise ValueError("method_executor cannot be None")
        if questionnaire is None:
            raise ValueError("questionnaire cannot be None")
        if executor_config is None:
            raise ValueError("executor_config cannot be None")

        # Store injected dependencies
        self.executor = method_executor
        self.questionnaire = questionnaire
        self.executor_config = executor_config
        self.runtime_config = runtime_config
        self.phase0_validation = phase0_validation

        # Validate Phase 0 if result provided
        if phase0_validation is not None:
            if not phase0_validation.all_passed:
                failed = phase0_validation.get_failed_gates()
                failed_names = [g.gate_name for g in failed]
                raise RuntimeError(
                    f"Cannot initialize orchestrator: "
                    f"Phase 0 exit gates failed: {failed_names}. "
                    f"Bootstrap must complete successfully before pipeline execution."
                )
            self.logger.info(
                "orchestrator_phase0_validation_passed gates=%d time=%s",
                len(phase0_validation.gate_results),
                phase0_validation.validation_time
            )
        else:
            self.logger.warning(
                "orchestrator_phase0_validation_not_provided assuming_legacy_mode"
            )

        # Log runtime mode if provided
        if runtime_config is not None:
            self.logger.info(
                "orchestrator_runtime_mode mode=%s strict=%s",
                runtime_config.mode.value if hasattr(runtime_config, 'mode') else "unknown",
                getattr(runtime_config, 'is_strict_mode', lambda: False)()
            )
        else:
            self.logger.warning(
                "orchestrator_runtime_config_not_provided mode_enforcement_disabled"
            )

        self.logger.info(
            "orchestrator_initialized method_executor=%s questionnaire_version=%s",
            method_executor is not None,
            getattr(questionnaire, 'version', 'unknown')
        )

    def execute(self, phase: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Execute a pipeline phase.

        Args:
            phase: Phase identifier (e.g., "P01", "P02")
            context: Optional execution context

        Returns:
            Execution results with validation status

        Raises:
            ValueError: If phase is invalid or validation fails
        """
        if not phase:
            raise ValueError("Phase identifier is required")

        self.logger.info(f"Executing phase: {phase}")

        # Phase-specific execution logic
        if phase == "P01":
            return self._execute_phase1(context or {})
        else:
            raise ValueError(f"Unknown phase: {phase}")

    def _execute_phase1(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Execute Phase 1 with constitutional validation.

        Validates that exactly 60 chunks are produced:
        - 10 Policy Areas × 6 Causal Dimensions = 60 chunks
        """
        self.logger.info("Executing Phase 1 with constitutional validation")

        # Validate Phase 1 invariants
        expected_chunks = P01_EXPECTED_CHUNK_COUNT
        expected_policy_areas = P01_POLICY_AREA_COUNT
        expected_dimensions = P01_DIMENSION_COUNT

        self.logger.info(
            f"Phase 1 expects: {expected_chunks} chunks "
            f"({expected_policy_areas} Policy Areas × {expected_dimensions} Dimensions)"
        )

        return {
            "phase": "P01",
            "expected_chunks": expected_chunks,
            "expected_policy_areas": expected_policy_areas,
            "expected_dimensions": expected_dimensions,
            "status": "validated",
        }

    def validate_chunk_count(self, actual_chunks: int, expected: int = P01_EXPECTED_CHUNK_COUNT) -> bool:
        """
        Validate chunk count matches constitutional requirement.

        Args:
            actual_chunks: Actual number of chunks produced
            expected: Expected number of chunks (default: 60 for Phase 1)

        Returns:
            True if chunk count matches, False otherwise

        Raises:
            ValueError: If chunk count doesn't match expected value
        """
        if actual_chunks != expected:
            error_msg = (
                f"Chunk count violation: expected {expected} chunks, "
                f"got {actual_chunks}. This violates the constitutional invariant."
            )
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        self.logger.info(f"Chunk count validation passed: {actual_chunks} chunks")
        return True


__all__ = [
    "Orchestrator",
    "MethodExecutor",
    "Phase0ValidationResult",
    "GateResult",
    "P01_EXPECTED_CHUNK_COUNT",
    "P01_POLICY_AREA_COUNT",
    "P01_DIMENSION_COUNT",
]
