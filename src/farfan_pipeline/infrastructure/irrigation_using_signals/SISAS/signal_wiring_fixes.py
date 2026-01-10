"""
Signal Irrigation Wiring Fixes

Production-ready code fixes for identified wiring gaps in signal irrigation ecosystem.
This module provides complete implementations for missing interfaces and connections.

Author: F.A.R.F.A.N Pipeline
Date: 2025-01-15
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
except ImportError:
    import logging

    logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
        QuestionnaireSignalRegistry,
    )
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_context_scoper import (
        create_document_context,
    )


# ============================================================================
# FIX 1: Context Scoping Integration in Signal Registry
# ============================================================================


def integrate_context_scoping_in_registry(
    signal_registry: QuestionnaireSignalRegistry,
    document_context: dict[str, Any],
    question_id: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Integrate context scoping into signal registry pattern retrieval.

    This fixes the missing connection between signal_context_scoper and
    signal_registry for context-aware pattern filtering.

    Implements SISAS-WIRING-001 from SPEC_SIGNAL_NORMALIZATION_COMPREHENSIVE.md.

    Args:
        signal_registry: Signal registry instance
        document_context: Document context dict with keys like:
            - section: str (e.g., "budget", "indicators")
            - chapter: int (e.g., 3)
            - page: int (e.g., 47)
            - policy_area: str (e.g., "PA01")
        question_id: Optional question ID to filter patterns for.
            If None, returns patterns for all questions.

    Returns:
        Tuple of (filtered_patterns, stats_dict) where:
            - filtered_patterns: List of pattern specs that match context
            - stats_dict: Statistics about filtering (total, filtered, passed)

    Example:
        >>> from orchestration.factory import load_questionnaire, create_signal_registry
        >>> q = load_questionnaire()
        >>> registry = create_signal_registry(q)
        >>> context = {"section": "budget", "chapter": 3}
        >>> filtered, stats = integrate_context_scoping_in_registry(registry, context)
        >>> print(f"Patterns: {len(filtered)}, Filtered out: {stats['context_filtered']}")
    """
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_context_scoper import (
        filter_patterns_by_context,
    )

    all_patterns: list[dict[str, Any]] = []

    try:
        if question_id is not None:
            # Get patterns for specific question
            try:
                signal_pack = signal_registry.get_micro_answering_signals(question_id)
                all_patterns.extend(signal_pack.pattern_specs)
            except Exception as e:
                logger.warning(
                    "context_scoping_question_failed",
                    question_id=question_id,
                    error=str(e),
                )
        else:
            # Get patterns for all questions in registry
            try:
                # Access questionnaire data to get all question IDs
                blocks = dict(signal_registry._questionnaire.data.get("blocks", {}))
                micro_questions = blocks.get("micro_questions", [])

                for q in micro_questions:
                    if isinstance(q, dict):
                        q_id = str(q.get("question_id", "")).strip()
                    else:
                        q_id = str(q).strip()

                    if not q_id:
                        continue

                    try:
                        signal_pack = signal_registry.get_micro_answering_signals(q_id)
                        all_patterns.extend(signal_pack.pattern_specs)
                    except Exception:
                        # Skip questions without valid signal packs
                        continue
            except Exception as e:
                logger.warning(
                    "context_scoping_questionnaire_access_failed",
                    error=str(e),
                )
    except Exception as e:
        logger.error(
            "context_scoping_pattern_collection_failed",
            error=str(e),
        )
        return [], {
            "total_patterns": 0,
            "context_filtered": 0,
            "scope_filtered": 0,
            "passed": 0,
            "error": str(e),
        }

    # Apply context-aware filtering
    filtered_patterns, stats = filter_patterns_by_context(all_patterns, document_context)

    logger.info(
        "context_scoping_integration_applied",
        context_keys=list(document_context.keys()),
        total_patterns=stats.get("total_patterns", 0),
        context_filtered=stats.get("context_filtered", 0),
        scope_filtered=stats.get("scope_filtered", 0),
        passed=stats.get("passed", 0),
        question_id=question_id,
    )

    return filtered_patterns, stats


# ============================================================================
# FIX 2: Consumption Tracking Integration in Evidence Extraction
# ============================================================================


def integrate_consumption_tracking_in_extraction(
    evidence_result: Any,
    consumption_tracker: Any,
    source_text: str,
) -> None:
    """Integrate consumption tracking into evidence extraction.

    This fixes the missing connection between signal_evidence_extractor and
    signal_consumption for tracking pattern matches.

    Args:
        evidence_result: Evidence extraction result
        consumption_tracker: Consumption tracker instance
        source_text: Source text used for matching
    """
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption_integration import (
        track_pattern_match_from_evidence,
    )

    # Track pattern matches from evidence
    if hasattr(evidence_result, "evidence"):
        evidence_dict = evidence_result.evidence
        for element_type, matches in evidence_dict.items():
            if not isinstance(matches, list):
                continue
            for match_item in matches:
                if isinstance(match_item, dict):
                    track_pattern_match_from_evidence(consumption_tracker, match_item, source_text)

    logger.info(
        "consumption_tracking_integrated",
        match_count=consumption_tracker.match_count,
    )


# ============================================================================
# FIX 3: Scope Verification in Pattern Application
# ============================================================================


def verify_pattern_scope_before_application(
    pattern: dict[str, Any],
    document_context: dict[str, Any],
    policy_area: str,
    question_id: str,
) -> tuple[bool, str | None]:
    """Verify pattern scope before applying to document.

    This enforces SCOPE COHERENCE principle by checking pattern boundaries.

    Args:
        pattern: Pattern dict with context_requirement and context_scope
        document_context: Document context dict
        policy_area: Policy area for the question
        question_id: Question ID

    Returns:
        Tuple of (is_valid, violation_message)

    Example:
        >>> pattern = {"pattern": "budget", "context_requirement": {"section": "budget"}}
        >>> context = {"section": "budget", "chapter": 3}
        >>> is_valid, msg = verify_pattern_scope_before_application(pattern, context, "PA01", "Q001")
        >>> assert is_valid
    """
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption_integration import (
        verify_pattern_scope,
    )

    return verify_pattern_scope(pattern, document_context, policy_area, question_id)


# ============================================================================
# FIX 4: Access Level Validation
# ============================================================================


def validate_access_level(
    accessor_module: str,
    accessor_class: str,
    accessor_method: str,
    requested_level: Any,  # AccessLevel
    accessed_block: str,
) -> bool:
    """Validate access level hierarchy compliance.

    This enforces the 3-level access hierarchy:
    - FACTORY: I/O total - Only AnalysisPipelineFactory
    - ORCHESTRATOR: Parcial recurrente - SISAS, ResourceProvider
    - CONSUMER: Granular scoped - Ejecutores, Evidence*

    Args:
        accessor_module: Module name of accessing code
        accessor_class: Class name
        accessor_method: Method name
        requested_level: Requested AccessLevel
        accessed_block: Block being accessed (e.g., "micro_questions", "patterns")

    Returns:
        True if access is valid, False otherwise

    Example:
        >>> from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption import AccessLevel
        >>> is_valid = validate_access_level(
        ...     "orchestration.factory",
        ...     "AnalysisPipelineFactory",
        ...     "_load_canonical_questionnaire",
        ...     AccessLevel.FACTORY,
        ...     "blocks"
        ... )
        >>> assert is_valid
    """
    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_consumption import (
        AccessLevel,
        get_access_audit,
    )

    # Factory-level accessors
    factory_modules = ["orchestration.factory"]
    factory_classes = ["AnalysisPipelineFactory"]

    # Orchestrator-level accessors
    orchestrator_modules = [
        "farfan_pipeline/infrastructure.irrigation_using_signals.SISAS",
        "orchestration.orchestrator",
    ]

    # Consumer-level accessors
    consumer_modules = [
        "farfan_pipeline.phases.Phase_2",
        "farfan_pipeline.phases.Phase_3",
    ]

    # Determine expected level from accessor
    expected_level = None
    if any(mod in accessor_module for mod in factory_modules) or any(
        cls in accessor_class for cls in factory_classes
    ):
        expected_level = AccessLevel.FACTORY
    elif any(mod in accessor_module for mod in orchestrator_modules):
        expected_level = AccessLevel.ORCHESTRATOR
    elif any(mod in accessor_module for mod in consumer_modules):
        expected_level = AccessLevel.CONSUMER

    # Validate
    if expected_level and requested_level != expected_level:
        access_audit = get_access_audit()
        access_audit.record_violation(
            violation_type="ACCESS_LEVEL_VIOLATION",
            accessor=f"{accessor_module}.{accessor_class}.{accessor_method}",
            expected_level=expected_level,
            actual_level=requested_level,
            details=f"Requested {requested_level.name} but expected {expected_level.name} for {accessor_module}",
        )
        logger.warning(
            "access_level_violation",
            accessor=f"{accessor_module}.{accessor_class}.{accessor_method}",
            expected=expected_level.name,
            actual=requested_level.name,
        )
        return False

    return True


# ============================================================================
# FIX 5: Complete Interface Implementation Verification
# ============================================================================


def verify_registry_interfaces_complete(registry: QuestionnaireSignalRegistry) -> dict[str, bool]:
    """Verify all required interfaces are implemented in registry.

    Args:
        registry: Signal registry instance

    Returns:
        Dict mapping method name to implementation status
    """
    required_methods = [
        "get_micro_answering_signals",
        "get_validation_signals",
        "get_scoring_signals",
        "get_assembly_signals",
        "get_chunking_signals",
    ]

    status = {}
    for method_name in required_methods:
        has_method = hasattr(registry, method_name)
        is_callable = callable(getattr(registry, method_name, None))
        status[method_name] = has_method and is_callable

    return status


# ============================================================================
# FIX 6: Synchronization Timing Validation
# ============================================================================


def validate_injection_timing(
    injection_time: float,
    phase_start_time: float,
    phase_state: str,
) -> tuple[bool, str | None]:
    """Validate signal injection timing relative to phase execution.

    This enforces SYNCHRONIZATION principle by checking injection timing.

    Args:
        injection_time: Time when signal was injected
        phase_start_time: Time when phase started
        phase_state: Current phase state

    Returns:
        Tuple of (is_valid, violation_message)

    Example:
        >>> import time
        >>> phase_start = time.time()
        >>> injection = phase_start + 0.1
        >>> is_valid, msg = validate_injection_timing(injection, phase_start, "EXECUTING")
        >>> assert is_valid
    """
    # Signal injection must happen after phase start
    if injection_time < phase_start_time:
        return False, f"Injection at {injection_time} before phase start at {phase_start_time}"

    # Signal injection only allowed in certain states
    valid_states = ["INITIALIZING", "EXECUTING", "READY"]
    if phase_state not in valid_states:
        return False, f"Injection attempted in invalid state: {phase_state}"

    return True, None
