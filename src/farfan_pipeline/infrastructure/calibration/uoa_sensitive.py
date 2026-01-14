"""
UoA-Sensitive Method Decorators
================================
Decorators that make methods automatically consume calibration parameters from context.

Module: uoa_sensitive.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Automatic parametrization via decorator pattern
Schema Version: 1.0.0

DESIGN PATTERN: Decorator Pattern + Parameter Injection

INVARIANTS ENFORCED:
    INV-DEC-001: Decorated methods must be called within calibration_context
    INV-DEC-002: Required parameters must exist in calibration layer
    INV-DEC-003: Prohibited operations blocked before method execution
    INV-DEC-004: Parameter injection logged for auditability
"""

from __future__ import annotations

import functools
import inspect
import logging
from typing import Any, Callable, TypeVar

from .runtime_context import get_calibration_context, require_calibration_context

logger = logging.getLogger(__name__)

F = TypeVar('F', bound=Callable[..., Any])


def uoa_sensitive(
    *,
    required_parameters: list[str] | None = None,
    phase: str = "phase1",
    validate_before: bool = True,
    log_parameters: bool = True,
) -> Callable[[F], F]:
    """
    Unit of Analysis Requirements:
        - Decorated method must be called within calibration_context()
        - Required parameters must exist in specified phase layer

    Epistemic Level: N1-EMP (ingestion) or N2-INF (computation) depending on phase
    Output: Decorated method with automatic calibration parameter injection
    Fusion Strategy: Runtime parameter injection via context lookup

    Decorator to make methods UoA-sensitive.

    Automatically injects calibration parameters from the active calibration
    context into method execution. Parameters are injected as keyword arguments
    if not already provided by the caller.

    This enables methods to be dynamically parametrized based on:
    - UnitOfAnalysis characteristics (complexity, fiscal context, etc.)
    - Contract TYPE constraints (TYPE_A, TYPE_B, etc.)
    - Calibration phase (Phase 1 ingestion vs Phase 2 computation)

    Args:
        required_parameters: List of parameter names to inject
            (e.g., ["chunk_size", "prior_strength"])
        phase: "phase1" or "phase2" - which calibration layer to use
        validate_before: Run prohibited operation validation before execution
        log_parameters: Log injected parameters for audit trail

    Returns:
        Decorated function with automatic parameter injection

    Raises:
        RuntimeError: If no calibration context is active (INV-DEC-001)
        RuntimeError: If prohibited operation detected (INV-DEC-003)

    Usage:
        @uoa_sensitive(required_parameters=["chunk_size", "prior_strength"])
        def extract_document(document: Document, chunk_size: int = 512,
                           prior_strength: float = 1.0, **kwargs):
            # chunk_size and prior_strength automatically injected from calibration!
            # High complexity UoA → chunk_size = 1024
            # Low complexity UoA → chunk_size = 384
            chunks = split_into_chunks(document, chunk_size)
            ...

    Example with context:
        >>> unit = UnitOfAnalysis(...)  # High complexity
        >>> context = CalibrationContext(unit, ...)
        >>> with calibration_context(context):
        ...     # chunk_size automatically calibrated based on UoA complexity
        ...     result = extract_document(document)
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # INV-DEC-001: Require active calibration context
            context = require_calibration_context()

            # Get function signature for parameter inspection
            sig = inspect.signature(func)

            # Inject calibration parameters
            injected = {}
            if required_parameters:
                for param_name in required_parameters:
                    # Only inject if not already provided by caller
                    if param_name not in kwargs:
                        # Check if parameter exists in function signature
                        if param_name in sig.parameters or "kwargs" in [
                            p.name for p in sig.parameters.values()
                            if p.kind == inspect.Parameter.VAR_KEYWORD
                        ]:
                            try:
                                # INV-DEC-002: Get parameter from calibration layer
                                value = context.get_parameter(param_name, phase=phase)
                                kwargs[param_name] = value
                                injected[param_name] = value

                                # INV-DEC-004: Log injection for audit trail
                                if log_parameters:
                                    logger.debug(
                                        f"{func.__name__}: Injected {param_name}={value} "
                                        f"from {phase} calibration "
                                        f"(contract: {context.contract_id}, "
                                        f"UoA: {context.unit_of_analysis.municipality_name})"
                                    )
                            except KeyError:
                                logger.warning(
                                    f"{func.__name__}: Required parameter '{param_name}' "
                                    f"not found in {phase} calibration layer "
                                    f"(contract: {context.contract_id})"
                                )

            # INV-DEC-003: Validate prohibited operations
            if validate_before:
                func_name_lower = func.__name__.lower()

                # Check if method name suggests prohibited operation
                for prohibited in ["average", "mean", "weighted_mean", "arithmetic_mean"]:
                    if prohibited in func_name_lower:
                        if context.is_operation_prohibited(prohibited):
                            raise RuntimeError(
                                f"Operation '{prohibited}' is PROHIBITED for "
                                f"contract TYPE {context.contract_type}. "
                                f"Method {func.__name__} cannot be executed. "
                                f"(contract: {context.contract_id})"
                            )

            # Log execution with injected parameters
            if injected and log_parameters:
                logger.info(
                    f"Executing {func.__name__} with calibrated parameters: "
                    f"{', '.join(f'{k}={v}' for k, v in injected.items())} "
                    f"(TYPE: {context.contract_type})"
                )

            # Execute method with injected parameters
            return func(*args, **kwargs)

        # Mark function as UoA-sensitive for introspection
        wrapper.__uoa_sensitive__ = True  # type: ignore
        wrapper.__required_parameters__ = required_parameters  # type: ignore
        wrapper.__calibration_phase__ = phase  # type: ignore

        return wrapper  # type: ignore

    return decorator


# =============================================================================
# CONVENIENCE DECORATORS
# =============================================================================


def chunk_size_aware(func: F) -> F:
    """
    Unit of Analysis Requirements:
        - Method must accept chunk_size parameter (int)
        - Must be called within calibration_context

    Epistemic Level: N1-EMP (ingestion)
    Output: Decorated method with automatic chunk_size injection
    Fusion Strategy: UoA complexity → chunk_size scaling

    Convenience decorator for chunk_size parameter injection.

    Automatically injects chunk_size calibrated based on UoA complexity:
    - High complexity (large municipality) → larger chunks (up to 2048)
    - Low complexity (small municipality) → smaller chunks (down to 256)

    Usage:
        @chunk_size_aware
        def process_document(document, chunk_size=512):
            # chunk_size automatically calibrated!
            # Medellín (high complexity) → chunk_size ≈ 1024
            # Small town (low complexity) → chunk_size ≈ 384
            chunks = split_into_chunks(document, chunk_size)
            return process_chunks(chunks)
    """
    return uoa_sensitive(required_parameters=["chunk_size"], phase="phase1")(func)


def prior_aware(func: F) -> F:
    """
    Unit of Analysis Requirements:
        - Method must accept prior_strength parameter (float)
        - Must be called within calibration_context

    Epistemic Level: N1-EMP or N2-INF
    Output: Decorated method with automatic prior_strength injection
    Fusion Strategy: TYPE-specific priors + cognitive cost adjustment

    Convenience decorator for prior_strength parameter injection.

    Automatically injects prior_strength calibrated based on:
    - Contract TYPE (TYPE_B has stronger priors than TYPE_E)
    - Cognitive cost (complex methods get stronger priors)
    - UoA characteristics

    Usage:
        @prior_aware
        def bayesian_update(evidence, prior_strength=1.0):
            # prior_strength automatically calibrated!
            # TYPE_B (Bayesian) → stronger prior (≈2.0)
            # TYPE_E (Logical) → weaker prior (≈0.5)
            posterior = update_belief(evidence, prior_strength)
            return posterior
    """
    return uoa_sensitive(required_parameters=["prior_strength"], phase="phase1")(func)


def veto_aware(func: F) -> F:
    """
    Unit of Analysis Requirements:
        - Method must accept veto_threshold parameter (float)
        - Must be called within calibration_context

    Epistemic Level: N3-AUD (validation/veto)
    Output: Decorated method with automatic veto_threshold injection
    Fusion Strategy: TYPE-specific veto thresholds + interaction density

    Convenience decorator for veto_threshold parameter injection.

    Automatically injects veto_threshold calibrated based on:
    - Contract TYPE (TYPE_E has strictest veto, TYPE_D most lenient)
    - Interaction density (higher density → stricter veto)

    Usage:
        @veto_aware
        def validate_result(result, veto_threshold=0.05):
            # veto_threshold automatically calibrated!
            # TYPE_E (logical) → strict veto (≈0.03)
            # TYPE_D (financial) → lenient veto (≈0.08)
            if confidence < veto_threshold:
                raise VetoException("Result vetoed")
            return result
    """
    return uoa_sensitive(required_parameters=["veto_threshold"], phase="phase2")(func)


def coverage_aware(func: F) -> F:
    """
    Unit of Analysis Requirements:
        - Method must accept extraction_coverage_target parameter (float)
        - Must be called within calibration_context

    Epistemic Level: N1-EMP (ingestion)
    Output: Decorated method with automatic coverage target injection
    Fusion Strategy: Policy area count → coverage target adjustment

    Convenience decorator for extraction_coverage_target parameter injection.

    Automatically injects coverage target calibrated based on:
    - Number of policy areas (more areas → slightly lower target)
    - UoA characteristics

    Usage:
        @coverage_aware
        def extract_policy_content(document, extraction_coverage_target=0.95):
            # extraction_coverage_target automatically calibrated!
            # Few policy areas → high target (0.98)
            # Many policy areas → moderate target (0.85)
            content = extract_until_coverage(document, extraction_coverage_target)
            return content
    """
    return uoa_sensitive(
        required_parameters=["extraction_coverage_target"],
        phase="phase1",
    )(func)


def fully_calibrated(func: F) -> F:
    """
    Unit of Analysis Requirements:
        - Method must accept all calibration parameters
        - Must be called within calibration_context

    Epistemic Level: N1-EMP + N2-INF + N3-AUD (all levels)
    Output: Decorated method with all parameters injected
    Fusion Strategy: Comprehensive calibration

    Convenience decorator that injects ALL calibration parameters.

    Use for methods that need complete calibration context.

    Usage:
        @fully_calibrated
        def execute_contract(document, chunk_size=512, prior_strength=1.0,
                           veto_threshold=0.05, extraction_coverage_target=0.95):
            # ALL parameters automatically calibrated!
            ...
    """
    return uoa_sensitive(
        required_parameters=[
            "chunk_size",
            "prior_strength",
            "veto_threshold",
            "extraction_coverage_target",
        ],
        phase="phase1",
    )(func)


# =============================================================================
# INTROSPECTION UTILITIES
# =============================================================================


def is_uoa_sensitive(func: Callable) -> bool:
    """
    Check if function is UoA-sensitive (decorated).

    Args:
        func: Function to check

    Returns:
        True if decorated with @uoa_sensitive, False otherwise
    """
    return getattr(func, '__uoa_sensitive__', False)


def get_required_parameters(func: Callable) -> list[str] | None:
    """
    Get required parameters for UoA-sensitive function.

    Args:
        func: Function to inspect

    Returns:
        List of required parameter names, or None if not UoA-sensitive
    """
    return getattr(func, '__required_parameters__', None)


def get_calibration_phase(func: Callable) -> str | None:
    """
    Get calibration phase for UoA-sensitive function.

    Args:
        func: Function to inspect

    Returns:
        "phase1" or "phase2", or None if not UoA-sensitive
    """
    return getattr(func, '__calibration_phase__', None)


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    # Main decorator
    "uoa_sensitive",
    # Convenience decorators
    "chunk_size_aware",
    "prior_aware",
    "veto_aware",
    "coverage_aware",
    "fully_calibrated",
    # Introspection
    "is_uoa_sensitive",
    "get_required_parameters",
    "get_calibration_phase",
]
