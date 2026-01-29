"""
Phase 1 Questionnaire Mapper - Question-Level Granularity
=========================================================

This module provides utilities to map questionnaire questions to PA×DIM×Q structure
and invoke method sets defined in the questionnaire.

This addresses the audit findings:
- 2.2: 60 chunks (PA×DIM) vs 300 questions (PA×DIM×Q) granularity mismatch
- 2.3: Method sets defined in questionnaire are not invoked
- 2.4: Expected elements are not verified

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 - Question-Aware Architecture
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 1
__stage__ = 15
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"

import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    import structlog

    logger = structlog.get_logger(__name__)
    STRUCTLOG_AVAILABLE = True
except ImportError:
    import logging

    logger = logging.getLogger(__name__)
    STRUCTLOG_AVAILABLE = False


# Question mapping constants
QUESTIONS_PER_DIMENSION = 5  # Q1-Q5 per PA×DIM combination
NUM_POLICY_AREAS = 10  # PA01-PA10
NUM_DIMENSIONS = 6  # DIM01-DIM06
TOTAL_QUESTIONS = NUM_POLICY_AREAS * NUM_DIMENSIONS * QUESTIONS_PER_DIMENSION  # 300


@dataclass
class QuestionSpec:
    """
    Specification for a single question from the questionnaire.

    Contains all metadata needed for processing:
    - Patterns for text matching
    - Method sets for analysis
    - Expected elements for verification
    """

    question_id: str  # e.g., "Q001"
    policy_area: str  # e.g., "PA01"
    dimension: str  # e.g., "DIM01"
    slot: int  # 1-5, position within PA×DIM

    # Question text and metadata
    text: str = ""
    question_type: str = ""
    scoring_modality: str = ""

    # Patterns for matching
    patterns: list[dict[str, Any]] = field(default_factory=list)

    # Method sets to invoke
    method_sets: list[dict[str, Any]] = field(default_factory=list)

    # Expected elements for verification
    expected_elements: list[dict[str, Any]] = field(default_factory=list)

    # Failure contract
    failure_contract: dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestionnaireMap:
    """
    Complete mapping of questionnaire questions to PA×DIM×Q structure.

    Provides:
    - Lookup by question_id
    - Lookup by PA×DIM→List[QuestionSpec]
    - Method invocation utilities
    - Expected elements verification
    """

    questions_by_id: dict[str, QuestionSpec] = field(default_factory=dict)
    questions_by_pa_dim: dict[tuple[str, str], list[QuestionSpec]] = field(default_factory=dict)

    # Method registry for invoking methods
    method_registry: Any | None = None

    def get_question(self, question_id: str) -> QuestionSpec | None:
        """Get question specification by ID."""
        return self.questions_by_id.get(question_id)

    def get_questions_for_pa_dim(self, policy_area: str, dimension: str) -> list[QuestionSpec]:
        """Get all questions for a specific PA×DIM combination."""
        key = (policy_area, dimension)
        return self.questions_by_pa_dim.get(key, [])

    def get_all_question_ids(self) -> list[str]:
        """Get all question IDs sorted."""
        return sorted(self.questions_by_id.keys())

    def is_loaded(self) -> bool:
        """Check if questionnaire has been loaded."""
        return len(self.questions_by_id) > 0


def load_questionnaire_map(questionnaire_path: Path) -> QuestionnaireMap:
    """
    Load questionnaire and build PA×DIM×Q mapping.

    Args:
        questionnaire_path: Path to questionnaire_monolith.json

    Returns:
        QuestionnaireMap with all questions loaded

    Raises:
        FileNotFoundError: If questionnaire not found
        json.JSONDecodeError: If questionnaire is invalid
    """
    if not questionnaire_path.exists():
        raise FileNotFoundError(f"Questionnaire not found: {questionnaire_path}")

    with open(questionnaire_path) as f:
        data = json.load(f)

    qmap = QuestionnaireMap()

    # Extract micro questions (300 questions)
    micro_questions = data.get("blocks", {}).get("micro_questions", [])

    if not micro_questions:
        logger.warning("No micro_questions found in questionnaire")
        return qmap

    # Extract canonical notation for PA and DIM mappings
    canonical = data.get("canonical_notation", {})
    policy_areas = canonical.get("policy_areas", {})
    dimensions = canonical.get("dimensions", {})

    # Process each question
    for q_data in micro_questions:
        question_id = q_data.get("question_id", "")
        if not question_id:
            continue

        # Parse question_id to extract PA and DIM
        # Format: Q### where ### = (PA-1)*30 + (DIM-1)*5 + slot
        # Q001-Q005: PA01×DIM01×Q1-Q5
        # Q006-Q010: PA01×DIM02×Q1-Q5
        # ...
        try:
            q_num = int(question_id[1:])  # Remove 'Q' prefix
            pa_idx = (q_num - 1) // (NUM_DIMENSIONS * QUESTIONS_PER_DIMENSION)
            dim_idx = (
                (q_num - 1) % (NUM_DIMENSIONS * QUESTIONS_PER_DIMENSION)
            ) // QUESTIONS_PER_DIMENSION
            slot = ((q_num - 1) % QUESTIONS_PER_DIMENSION) + 1

            policy_area = f"PA{pa_idx + 1:02d}"
            dimension = f"DIM{dim_idx + 1:02d}"
        except (ValueError, IndexError):
            logger.warning(f"Invalid question_id format: {question_id}")
            continue

        # Create QuestionSpec
        spec = QuestionSpec(
            question_id=question_id,
            policy_area=policy_area,
            dimension=dimension,
            slot=slot,
            text=q_data.get("text", ""),
            question_type=q_data.get("type", ""),
            scoring_modality=q_data.get("scoring_modality", ""),
            patterns=q_data.get("patterns", []),
            method_sets=q_data.get("method_sets", []),
            expected_elements=q_data.get("expected_elements", []),
            failure_contract=q_data.get("failure_contract", {}),
        )

        # Add to mappings
        qmap.questions_by_id[question_id] = spec

        key = (policy_area, dimension)
        if key not in qmap.questions_by_pa_dim:
            qmap.questions_by_pa_dim[key] = []
        qmap.questions_by_pa_dim[key].append(spec)

    logger.info(
        f"Loaded questionnaire map: {len(qmap.questions_by_id)} questions, "
        f"{len(qmap.questions_by_pa_dim)} PA×DIM combinations"
    )

    # Verify we have exactly 300 questions
    if len(qmap.questions_by_id) != TOTAL_QUESTIONS:
        logger.warning(f"Expected {TOTAL_QUESTIONS} questions, got {len(qmap.questions_by_id)}")

    return qmap


def invoke_method_set(
    chunk_text: str,
    question_spec: QuestionSpec,
    method_registry: Any,
    method_filter: Callable[[dict[str, Any]], bool] | None = None,
) -> dict[str, Any]:
    """
    Invoke all method sets defined for a question.

    This addresses audit finding 2.3: Method sets defined in questionnaire
    are not invoked by Phase 1.

    Args:
        chunk_text: Text content to analyze
        question_spec: Question specification with method_sets
        method_registry: MethodRegistry for retrieving methods
        method_filter: Optional filter to select which methods to invoke

    Returns:
        Dict with method_name -> result mapping
    """
    import importlib
    results = {}

    if not question_spec.method_sets:
        logger.debug(f"No method sets defined for {question_spec.question_id}")
        return results

    logger.info(
        f"Invoking {len(question_spec.method_sets)} method sets for {question_spec.question_id}"
    )

    for method_spec in question_spec.method_sets:
        class_name = method_spec.get("class")
        function_name = method_spec.get("function")
        priority = method_spec.get("priority", 0)
        method_type = method_spec.get("method_type", "analysis")

        # Apply filter if provided
        if method_filter and not method_filter(method_spec):
            continue

        try:
            # Get method from registry
            if method_registry is None:
                logger.warning(
                    f"Method registry not available, skipping {class_name}.{function_name}"
                )
                continue

            method = method_registry.get_method(class_name, function_name)

            # Fallback for Stub Registry (returns None or non-callable)
            if method is None or not callable(method):
                if hasattr(method_registry, "class_paths") and class_name in method_registry.class_paths:
                    try:
                        module_path = method_registry.class_paths[class_name]
                        module = importlib.import_module(module_path)
                        cls = getattr(module, class_name)
                        instance = cls()
                        if hasattr(instance, function_name):
                            method = getattr(instance, function_name)
                            logger.debug(f"Resolved {class_name}.{function_name} via dynamic import fallback")
                    except Exception as fallback_err:
                        logger.warning(f"Fallback import failed for {class_name}: {fallback_err}")

            if not callable(method):
                raise ValueError(f"Method {class_name}.{function_name} not found or not callable")

            # Invoke method
            logger.debug(
                f"Invoking {class_name}.{function_name} (priority={priority}, type={method_type})"
            )

            result = method(chunk_text)

            # Store result
            key = f"{class_name}.{function_name}"
            results[key] = {
                "result": result,
                "priority": priority,
                "method_type": method_type,
                "success": True,
            }

        except Exception as e:
            logger.error(f"Method invocation failed for {class_name}.{function_name}: {e}")
            key = f"{class_name}.{function_name}"
            results[key] = {
                "result": None,
                "priority": priority,
                "method_type": method_type,
                "success": False,
                "error": str(e),
            }

    logger.info(
        f"Method invocation complete: {sum(1 for r in results.values() if r['success'])}/{len(results)} succeeded"
    )

    return results


def verify_expected_elements(chunk_text: str, question_spec: QuestionSpec) -> dict[str, bool]:
    """
    Verify expected elements for a question.

    This addresses audit finding 2.4: Expected elements defined in
    questionnaire are not verified by Phase 1.

    Args:
        chunk_text: Text content to verify
        question_spec: Question specification with expected_elements

    Returns:
        Dict mapping element_type -> verification_result (True/False)
    """
    verification = {}

    if not question_spec.expected_elements:
        logger.debug(f"No expected elements defined for {question_spec.question_id}")
        return verification

    logger.info(
        f"Verifying {len(question_spec.expected_elements)} expected elements for {question_spec.question_id}"
    )

    for element_spec in question_spec.expected_elements:
        element_type = element_spec.get("type", "unknown")
        required = element_spec.get("required", False)

        # Check if element is present in chunk text
        # This is a simplified check - more sophisticated verification
        # would use pattern matching and semantic analysis
        text_lower = chunk_text.lower()

        # Pattern-based verification
        pattern = element_spec.get("pattern", "")
        if pattern:
            import re

            match = re.search(pattern, chunk_text, re.IGNORECASE)
            verification[element_type] = match is not None
        else:
            # Keyword-based verification (fallback)
            keywords = element_spec.get("keywords", [])
            if keywords:
                verification[element_type] = any(kw.lower() in text_lower for kw in keywords)
            else:
                # If no pattern or keywords, check based on type
                verification[element_type] = _verify_element_by_type(element_type, chunk_text)

        # Log verification result
        status = "✓" if verification.get(element_type, False) else "✗"
        required_flag = " [REQUIRED]" if required else ""
        logger.debug(f"  {status} {element_type}{required_flag}")

    # Check if all required elements are present
    required_elements = [e for e in question_spec.expected_elements if e.get("required", False)]
    all_required_present = all(
        verification.get(e.get("type", ""), False) for e in required_elements
    )

    logger.info(
        f"Expected elements verification: "
        f"{sum(1 for v in verification.values() if v)}/{len(verification)} present, "
        f"{len(required_elements)} required, all required present: {all_required_present}"
    )

    return verification


def _verify_element_by_type(element_type: str, text: str) -> bool:
    """
    Verify element presence based on type heuristics.

    This is a fallback when no pattern or keywords are specified.
    """
    text_lower = text.lower()

    # Type-specific heuristics
    if "diagnostico" in element_type or "diagnosis" in element_type:
        return any(
            term in text_lower for term in ["diagnóstico", "diagnóstico", "análisis de situación"]
        )
    elif "dato" in element_type or "data" in element_type:
        return any(term in text_lower for term in ["dato", "estadística", "%", "tasa"])
    elif "meta" in element_type or "objetivo" in element_type:
        return any(term in text_lower for term in ["meta", "objetivo", "indicador"])
    elif "presupuesto" in element_type or "financiero" in element_type:
        return any(term in text_lower for term in ["presupuesto", "financiero", "inversión", "$"])
    else:
        # Generic check: element type appears in text
        return element_type.lower() in text_lower


def create_chunk_id_for_question(policy_area: str, dimension: str, slot: int) -> str:
    """
    Create a chunk ID for a specific question.

    Format: CHUNK-{PA}{DIM}-Q{slot}
    Example: CHUNK-PA01DIM01-Q1
    """
    return f"CHUNK-{policy_area}{dimension}-Q{slot}"


def parse_question_id(question_id: str) -> tuple[str, str, int]:
    """
    Parse question_id into (policy_area, dimension, slot).

    Args:
        question_id: e.g., "Q001" or "Q056"

    Returns:
        (policy_area, dimension, slot) e.g., ("PA01", "DIM02", 1)
    """
    try:
        q_num = int(question_id[1:])  # Remove 'Q' prefix
        pa_idx = (q_num - 1) // (NUM_DIMENSIONS * QUESTIONS_PER_DIMENSION)
        dim_idx = (
            (q_num - 1) % (NUM_DIMENSIONS * QUESTIONS_PER_DIMENSION)
        ) // QUESTIONS_PER_DIMENSION
        slot = ((q_num - 1) % QUESTIONS_PER_DIMENSION) + 1

        return (f"PA{pa_idx + 1:02d}", f"DIM{dim_idx + 1:02d}", slot)
    except (ValueError, IndexError):
        logger.warning(f"Invalid question_id format: {question_id}")
        return ("", "", 0)


__all__ = [
    "NUM_DIMENSIONS",
    "NUM_POLICY_AREAS",
    "QUESTIONS_PER_DIMENSION",
    "TOTAL_QUESTIONS",
    "QuestionSpec",
    "QuestionnaireMap",
    "create_chunk_id_for_question",
    "invoke_method_set",
    "load_questionnaire_map",
    "parse_question_id",
    "verify_expected_elements",
]
