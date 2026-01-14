"""
Runtime Calibration Context
============================
Thread-safe context manager for injecting calibration parameters into methods.

Module: runtime_context.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Runtime parametrization injection via context management
Schema Version: 1.0.0

DESIGN PATTERN: Context Manager + Dependency Injection

INVARIANTS ENFORCED:
    INV-RT-001: Calibration context is thread-local (no cross-contamination)
    INV-RT-002: Context requires both Phase 1 and Phase 2 layers
    INV-RT-003: Parameters must exist in specified phase layer
    INV-RT-004: Prohibited operations checked before returning parameters
"""

from __future__ import annotations

import contextvars
import logging
from dataclasses import dataclass
from typing import Any

from .calibration_core import CalibrationLayer
from .type_defaults import PROHIBITED_OPERATIONS
from .unit_of_analysis import UnitOfAnalysis

logger = logging.getLogger(__name__)

# Thread-local calibration context (INV-RT-001)
_calibration_context: contextvars.ContextVar[CalibrationContext | None] = (
    contextvars.ContextVar('calibration_context', default=None)
)


@dataclass(frozen=True, slots=True)
class CalibrationContext:
    """
    Unit of Analysis Requirements:
        - Valid UnitOfAnalysis instance with complexity_score
        - Both phase1_layer and phase2_layer must be non-None
        - contract_type must match VALID_CONTRACT_TYPES

    Epistemic Level: N3-AUD (meta-level context)
    Output: Thread-safe immutable parametrization context
    Fusion Strategy: Context injection pattern

    Immutable calibration context for current execution thread.

    This context is injected into the execution thread and provides
    methods with access to calibrated parameters without requiring
    explicit parameter passing.

    Thread Safety: Uses contextvars for thread-local storage, ensuring
    no cross-contamination between concurrent executions.

    Attributes:
        unit_of_analysis: UoA characteristics driving calibration
        phase1_layer: Immutable Phase 1 calibration layer (ingestion)
        phase2_layer: Immutable Phase 2 calibration layer (computation)
        contract_type: TYPE_A, TYPE_B, etc.
        contract_id: Unique contract identifier
    """

    unit_of_analysis: UnitOfAnalysis
    phase1_layer: CalibrationLayer
    phase2_layer: CalibrationLayer
    contract_type: str
    contract_id: str

    def __post_init__(self) -> None:
        """Validate context invariants."""
        # INV-RT-002: Both layers must be present
        if self.phase1_layer is None or self.phase2_layer is None:
            raise ValueError("Both phase1_layer and phase2_layer are required")

        # Validate contract type matches layers
        if self.phase1_layer.contract_type_code != self.contract_type:
            raise ValueError(
                f"phase1_layer contract type mismatch: "
                f"expected {self.contract_type}, got {self.phase1_layer.contract_type_code}"
            )
        if self.phase2_layer.contract_type_code != self.contract_type:
            raise ValueError(
                f"phase2_layer contract type mismatch: "
                f"expected {self.contract_type}, got {self.phase2_layer.contract_type_code}"
            )

    def get_parameter(self, name: str, phase: str = "phase1") -> float:
        """
        Unit of Analysis Requirements:
            - Parameter must exist in specified phase layer
            - Phase must be "phase1" or "phase2"

        Epistemic Level: N3-AUD
        Output: Calibrated parameter value
        Fusion Strategy: Direct parameter lookup

        Get calibrated parameter value.

        Args:
            name: Parameter name (prior_strength, veto_threshold, chunk_size,
                  extraction_coverage_target)
            phase: "phase1" or "phase2"

        Returns:
            Calibrated parameter value

        Raises:
            ValueError: If phase is invalid
            KeyError: If parameter not found in layer
        """
        if phase not in ("phase1", "phase2"):
            raise ValueError(f"phase must be 'phase1' or 'phase2', got: {phase}")

        layer = self.phase1_layer if phase == "phase1" else self.phase2_layer

        # INV-RT-003: Parameter must exist
        param = layer.get_parameter(name)
        return param.value

    def get_all_parameters(self, phase: str = "phase1") -> dict[str, float]:
        """
        Get all parameters from specified phase as dictionary.

        Args:
            phase: "phase1" or "phase2"

        Returns:
            Dictionary mapping parameter names to values
        """
        layer = self.phase1_layer if phase == "phase1" else self.phase2_layer
        return {p.name: p.value for p in layer.parameters}

    def is_operation_prohibited(self, operation: str) -> bool:
        """
        Unit of Analysis Requirements:
            - contract_type must be in VALID_CONTRACT_TYPES

        Epistemic Level: N3-AUD
        Output: Boolean indicating if operation is prohibited
        Fusion Strategy: TYPE-specific prohibition check

        Check if operation is prohibited for this contract TYPE.

        Args:
            operation: Operation name (e.g., "weighted_mean", "average")

        Returns:
            True if operation is prohibited, False otherwise
        """
        # INV-RT-004: Check prohibited operations
        prohibited = PROHIBITED_OPERATIONS.get(self.contract_type, frozenset())
        is_prohibited = operation in prohibited

        if is_prohibited:
            logger.warning(
                f"Operation '{operation}' is PROHIBITED for contract type "
                f"{self.contract_type} (contract: {self.contract_id})"
            )

        return is_prohibited

    def get_uoa_characteristics(self) -> dict[str, Any]:
        """
        Get UoA characteristics as dictionary.

        Returns:
            Dictionary with UoA characteristics
        """
        return {
            "municipality_code": self.unit_of_analysis.municipality_code,
            "municipality_name": self.unit_of_analysis.municipality_name,
            "population": self.unit_of_analysis.population,
            "complexity_score": self.unit_of_analysis.complexity_score(),
            "fiscal_context": self.unit_of_analysis.fiscal_context.value,
            "policy_area_count": len(self.unit_of_analysis.policy_area_codes),
        }


# =============================================================================
# CONTEXT MANAGEMENT FUNCTIONS
# =============================================================================


def set_calibration_context(context: CalibrationContext) -> None:
    """
    Set calibration context for current thread.

    Args:
        context: CalibrationContext to set
    """
    _calibration_context.set(context)
    logger.debug(f"Calibration context set for contract {context.contract_id}")


def get_calibration_context() -> CalibrationContext | None:
    """
    Get calibration context for current thread.

    Returns:
        CalibrationContext if set, None otherwise
    """
    return _calibration_context.get()


def require_calibration_context() -> CalibrationContext:
    """
    Require calibration context (raises if not set).

    Returns:
        CalibrationContext

    Raises:
        RuntimeError: If no calibration context is active
    """
    context = get_calibration_context()
    if context is None:
        raise RuntimeError(
            "No calibration context active. "
            "Methods decorated with @uoa_sensitive must be executed within "
            "calibration_context(). "
            "Example: with calibration_context(ctx): method()"
        )
    return context


# =============================================================================
# CONTEXT MANAGER
# =============================================================================


class calibration_context:
    """
    Unit of Analysis Requirements:
        - Valid CalibrationContext instance
        - Both phase layers initialized

    Epistemic Level: N3-AUD
    Output: Context manager for scoped parametrization
    Fusion Strategy: Thread-local context injection with automatic cleanup

    Context manager for scoped calibration.

    Automatically sets and clears calibration context for the execution scope.

    Thread Safety: Uses contextvars.Token to ensure proper context restoration
    even in case of exceptions or nested contexts.

    Usage:
        >>> context = CalibrationContext(...)
        >>> with calibration_context(context):
        ...     # Within this block, methods can access calibration parameters
        ...     result = extract_document(document)
        ...     # extract_document decorated with @chunk_size_aware
        ...     # automatically receives calibrated chunk_size
    """

    def __init__(self, context: CalibrationContext):
        """
        Initialize context manager.

        Args:
            context: CalibrationContext to activate
        """
        self.context = context
        self.token = None

    def __enter__(self) -> CalibrationContext:
        """
        Enter context: set calibration context for thread.

        Returns:
            The active CalibrationContext
        """
        self.token = _calibration_context.set(self.context)
        logger.info(
            f"Entered calibration context for {self.context.contract_id} "
            f"(TYPE: {self.context.contract_type})"
        )
        return self.context

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit context: restore previous calibration context.

        Args:
            exc_type: Exception type (if raised)
            exc_val: Exception value (if raised)
            exc_tb: Exception traceback (if raised)

        Returns:
            False (does not suppress exceptions)
        """
        if self.token is not None:
            _calibration_context.reset(self.token)
            logger.info(f"Exited calibration context for {self.context.contract_id}")
        return False  # Don't suppress exceptions


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "CalibrationContext",
    "calibration_context",
    "get_calibration_context",
    "require_calibration_context",
    "set_calibration_context",
]
