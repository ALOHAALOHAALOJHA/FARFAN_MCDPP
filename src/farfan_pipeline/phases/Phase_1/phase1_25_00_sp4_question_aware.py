"""
Phase 1 SP4 - Question-Aware Segmentation (v2.0)
=================================================

NEW implementation of SP4 that creates 300 chunks (PA×DIM×Q) instead of 60 chunks (PA×DIM).

This addresses the audit finding 2.2: Phase 1 must map to questionnaire questions,
not just PA×DIM combinations.

Architecture:
- OLD: 60 chunks (10 PA × 6 DIM) = chunk per PA×DIM combination
- NEW: 300 chunks (10 PA × 6 DIM × 5 Q) = chunk per questionnaire question

Each chunk now includes:
- question_id: Maps to questionnaire (Q001-Q300)
- question_slot: 1-5 position within PA×DIM
- question_patterns: Patterns from questionnaire for this question
- question_method_sets: Methods to invoke for this question
- expected_elements: Elements to verify for this question

Author: F.A.R.F.A.N Pipeline Team
Version: 2.0.0 - Question-Aware Architecture
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 1
__stage__ = 25
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "MEDIUM"
__execution_pattern__ = "On-Demand"

import logging
import re
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

# Import Phase 1 models
from farfan_pipeline.phases.Phase_1.phase1_10_00_models import (
    Chunk,
)

# Import questionnaire mapper
from farfan_pipeline.phases.Phase_1.phase1_15_00_questionnaire_mapper import (
    QuestionSpec,
)

# Import Phase 1 constants
from farfan_pipeline.phases.Phase_1.phase1_10_00_phase_1_constants import (
    POLICY_AREA_COUNT,
)

# Try to import canonical types
try:
    from farfan_pipeline.core.types import DimensionCausal, PolicyArea

    CANONICAL_TYPES_AVAILABLE = True
except ImportError:
    CANONICAL_TYPES_AVAILABLE = False
    PolicyArea = None
    DimensionCausal = None


# Policy Area identifiers
POLICY_AREAS = [f"PA{i:02d}" for i in range(1, POLICY_AREA_COUNT + 1)]
DIMENSIONS = [f"DIM{i:02d}" for i in range(1, DIMENSION_COUNT + 1)]


def execute_sp4_question_aware(
    preprocessed: PreprocessedDoc,
    structure: StructureData,
    kg: KnowledgeGraph,
    questionnaire_path: Path,
    method_registry: Any | None = None,
    signal_enricher: Any | None = None,
) -> list[Chunk]:
    """
    SP4 v2.0: Question-Aware Segmentation.

    Creates EXACTLY 300 chunks (10 PA × 6 DIM × 5 Q) mapped to questionnaire questions.

    Args:
        preprocessed: Preprocessed document from SP1
        structure: Document structure from SP2
        kg: Knowledge graph from SP3
        questionnaire_path: Path to questionnaire_monolith.json
        method_registry: Optional MethodRegistry for method invocation
        signal_enricher: Optional SignalEnricher for pattern matching

    Returns:
        List[Chunk]: EXACTLY 300 chunks, one per questionnaire question

    Raises:
        AssertionError: If not exactly 300 chunks are created
        FileNotFoundError: If questionnaire not found
    """
    logger.info("SP4 v2.0: Starting question-aware segmentation - 300 chunks (PA×DIM×Q)")

    # Load questionnaire map
    qmap = load_questionnaire_map(questionnaire_path)

    if not qmap.is_loaded():
        raise ValueError(f"Failed to load questionnaire from {questionnaire_path}")

    qmap.method_registry = method_registry

    # Verify questionnaire has 300 questions
    assert len(qmap.questions_by_id) == TOTAL_QUESTIONS, (
        f"Questionnaire has {len(qmap.questions_by_id)} questions, " f"expected {TOTAL_QUESTIONS}"
    )

    chunks: list[Chunk] = []
    chunk_index = 0

    # Distribute paragraphs across chunks for text assignment
    total_paragraphs = len(preprocessed.paragraphs)
    paragraphs_per_chunk = max(1, total_paragraphs // TOTAL_CHUNK_COMBINATIONS)

    # Policy Area semantic keywords for intelligent assignment
    PA_KEYWORDS = {
        "PA01": [
            "mujer",
            "género",
            "igualdad",
            "feminicidio",
            "brecha salarial",
            "economía del cuidado",
        ],
        "PA02": ["violencia", "conflicto", "paz", "victim", "reconciliación", "posconflicto"],
        "PA03": ["ambient", "ecológic", "sostenib", "cambio climático", "conserv", "natural"],
        "PA04": ["derecho", "social", "económico", "cultural", "acceso", "garantía"],
        "PA05": ["víctim", "reparación", "verdad", "justicia", "memoria", "paz"],
        "PA06": ["niñez", "juventud", "adolescente", "protección", "menor", "infancia"],
        "PA07": ["tierra", "territorio", "rural", "campesin", "agrario", "propiedad"],
        "PA08": ["defensor", "líder", "activista", "protección", "amenaza", "derechos humanos"],
        "PA09": [
            "prisión",
            "penal",
            "carcel",
            "reclusión",
            "privación de libertad",
            "penitenciario",
        ],
        "PA10": ["migración", "migrant", "frontera", "desplazamiento", "refugio", "extranjero"],
    }

    # Dimension semantic keywords
    DIM_KEYWORDS = {
        "DIM01": ["diagnóstico", "insumo", "recurso", "dato", "línea base", "situación inicial"],
        "DIM02": ["actividad", "acción", "intervención", "proyecto", "programa", "iniciativa"],
        "DIM03": ["producto", "entregable", "output", "resultado inmediato", "logro", "producción"],
        "DIM04": ["resultado", "outcome", "efecto", "impacto corto", "cambio", "transformación"],
        "DIM05": ["impacto", "efecto largo", "cambio estructural", "sostenibilidad", "permanencia"],
        "DIM06": [
            "teoría del cambio",
            "causal",
            "relación",
            "hipótesis",
            "causa-efecto",
            "cadena causal",
        ],
    }

    # Generate EXACTLY 300 chunks - iterate through all PA×DIM×Q combinations
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            # Get questions for this PA×DIM combination
            questions = qmap.get_questions_for_pa_dim(pa, dim)

            # Should have exactly 5 questions per PA×DIM
            assert (
                len(questions) == QUESTIONS_PER_SLOT
            ), f"Expected {QUESTIONS_PER_SLOT} questions for {pa}×{dim}, got {len(questions)}"

            for question_spec in questions:
                question_id = question_spec.question_id
                slot = question_spec.slot

                # Create chunk_id in new format: CHUNK-PA01DIM01-Q1
                chunk_id = create_chunk_id_for_question(pa, dim, slot)

                # Find relevant paragraphs for this chunk
                relevant_paragraphs = _find_relevant_paragraphs(
                    preprocessed,
                    pa,
                    dim,
                    question_spec,
                    PA_KEYWORDS,
                    DIM_KEYWORDS,
                    signal_enricher,
                    paragraphs_per_chunk,
                    chunk_index,
                    total_paragraphs,
                )

                # Extract text and metadata
                chunk_text, text_spans, paragraph_ids, assignment_method, semantic_confidence = (
                    _extract_chunk_text_and_metadata(
                        relevant_paragraphs,
                        paragraphs_per_chunk,
                        chunk_index,
                        total_paragraphs,
                        preprocessed.paragraphs,
                    )
                )

                # Convert to enum types for type-safe aggregation
                policy_area_enum, dimension_enum = _convert_to_enums(pa, dim)

                # Create chunk with question-aware fields
                chunk = Chunk(
                    chunk_id=chunk_id,
                    policy_area_id=pa,
                    dimension_id=dim,
                    question_id=question_id,
                    question_slot=slot,
                    chunk_index=chunk_index,
                    text=chunk_text[:2000],
                    policy_area=policy_area_enum,
                    dimension=dimension_enum,
                    text_spans=text_spans,
                    paragraph_ids=paragraph_ids,
                    signal_tags=[pa, dim, question_id],
                    signal_scores={pa: 0.5, dim: 0.5, question_id: 0.5},
                    assignment_method=assignment_method,
                    semantic_confidence=semantic_confidence,
                    # NEW: Questionnaire-specific fields
                    question_patterns=question_spec.patterns,
                    question_method_sets=question_spec.method_sets,
                    expected_elements=question_spec.expected_elements,
                    segmentation_metadata={
                        "question_text": question_spec.text,
                        "scoring_modality": question_spec.scoring_modality,
                    },
                )

                # Invoke method sets if method registry is available
                if method_registry is not None and question_spec.method_sets:
                    logger.debug(f"Invoking method sets for {question_id}")
                    method_results = invoke_method_set(chunk_text, question_spec, method_registry)
                    chunk.method_invocation_results = method_results

                # Verify expected elements
                if REQUIRED_ELEMENT_VERIFICATION and question_spec.expected_elements:
                    logger.debug(f"Verifying expected elements for {question_id}")
                    verification = verify_expected_elements(chunk_text, question_spec)
                    chunk.elements_verification = verification

                    # Check if required elements are present
                    required_elements = [
                        e for e in question_spec.expected_elements if e.get("required", False)
                    ]
                    required_present = sum(
                        1 for e in required_elements if verification.get(e.get("type", ""), False)
                    )

                    if required_present < MIN_REQUIRED_ELEMENTS_PRESENT:
                        logger.warning(
                            f"{question_id}: Only {required_present}/{len(required_elements)} "
                            f"required elements present"
                        )

                chunks.append(chunk)
                chunk_index += 1

    # CONSTITUTIONAL INVARIANT: EXACTLY 300 chunks
    assert len(chunks) == TOTAL_CHUNK_COMBINATIONS, (
        f"SP4 v2.0 FATAL: Generated {len(chunks)} chunks, "
        f"MUST be EXACTLY {TOTAL_CHUNK_COMBINATIONS}"
    )

    # Verify complete PA×DIM×Q coverage
    chunk_ids = {c.chunk_id for c in chunks}
    expected_ids = set()
    for pa in POLICY_AREAS:
        for dim in DIMENSIONS:
            for q in range(1, QUESTIONS_PER_SLOT + 1):
                expected_ids.add(create_chunk_id_for_question(pa, dim, q))

    missing_ids = expected_ids - chunk_ids
    extra_ids = chunk_ids - expected_ids

    assert not missing_ids, f"SP4 v2.0 FATAL: Missing chunks: {missing_ids}"
    assert not extra_ids, f"SP4 v2.0 FATAL: Extra chunks: {extra_ids}"

    # Verify all question_ids are present
    question_ids = {c.question_id for c in chunks if c.question_id}
    assert (
        len(question_ids) == TOTAL_QUESTIONS
    ), f"Expected {TOTAL_QUESTIONS} unique question_ids, got {len(question_ids)}"

    logger.info(f"SP4 v2.0: Generated EXACTLY {len(chunks)} chunks with complete PA×DIM×Q coverage")

    # Log statistics
    _log_chunk_statistics(chunks, qmap)

    return chunks


def _find_relevant_paragraphs(
    preprocessed: PreprocessedDoc,
    pa: str,
    dim: str,
    question_spec: QuestionSpec,
    PA_KEYWORDS: dict[str, list[str]],
    DIM_KEYWORDS: dict[str, list[str]],
    signal_enricher: Any | None,
    paragraphs_per_chunk: int,
    chunk_index: int,
    total_paragraphs: int,
) -> list[tuple[int, str, float]]:
    """Find paragraphs relevant to a specific PA×DIM×Q combination."""

    relevant_paragraphs = []
    pa_keywords = PA_KEYWORDS.get(pa, [])
    dim_keywords = DIM_KEYWORDS.get(dim, [])

    # Also use question-specific patterns for relevance scoring
    question_patterns = []
    for pat in question_spec.patterns:
        pattern = pat.get("pattern", "")
        if pattern:
            question_patterns.append(pattern)

    for para_idx, para in enumerate(preprocessed.paragraphs):
        para_lower = para.lower()
        pa_score = sum(1 for kw in pa_keywords if kw.lower() in para_lower)
        dim_score = sum(1 for kw in dim_keywords if kw.lower() in para_lower)

        # Question-specific pattern matching
        question_score = 0
        for pattern in question_patterns[:5]:  # Limit to first 5 patterns
            try:
                if re.search(pattern, para, re.IGNORECASE):
                    question_score += 2  # Weight question patterns higher
                    break
            except re.error:
                continue

        # Signal enrichment boost
        signal_boost = 0
        if signal_enricher is not None:
            # Check for causal patterns matching the question
            causal_patterns = signal_enricher.get_causal_patterns()
            for pattern, _, _ in causal_patterns:
                try:
                    if re.search(pattern, para_lower, re.IGNORECASE):
                        signal_boost += 0.5
                        break
                except re.error:
                    continue

        total_score = pa_score + dim_score + question_score + signal_boost
        if total_score > 0:
            relevant_paragraphs.append((para_idx, para, total_score))

    # Sort by relevance score
    relevant_paragraphs.sort(key=lambda x: x[2], reverse=True)

    return relevant_paragraphs


def _extract_chunk_text_and_metadata(
    relevant_paragraphs: list[tuple[int, str, float]],
    paragraphs_per_chunk: int,
    chunk_index: int,
    total_paragraphs: int,
    all_paragraphs: list[str],
) -> tuple[str, list[tuple[int, int]], list[int], str, float]:
    """Extract text, spans, and metadata for a chunk."""

    if relevant_paragraphs:
        # Use top relevant paragraphs
        text_spans = [(p[0], p[0] + len(p[1])) for p in relevant_paragraphs[:3]]
        paragraph_ids = [p[0] for p in relevant_paragraphs[:3]]
        chunk_text = " ".join(p[1][:500] for p in relevant_paragraphs[:3])

        assignment_method = ASSIGNMENT_METHOD_SEMANTIC
        top_score = relevant_paragraphs[0][2]
        semantic_confidence = min(1.0, top_score / SEMANTIC_SCORE_MAX_EXPECTED)
    else:
        # Fallback: distribute sequentially
        start_idx = chunk_index * paragraphs_per_chunk
        end_idx = min(start_idx + paragraphs_per_chunk, total_paragraphs)
        text_spans = [(start_idx, end_idx)]
        paragraph_ids = list(range(start_idx, end_idx))
        chunk_text = " ".join(all_paragraphs[start_idx:end_idx])[:1500]

        assignment_method = ASSIGNMENT_METHOD_FALLBACK
        semantic_confidence = 0.0

    return chunk_text, text_spans, paragraph_ids, assignment_method, semantic_confidence


def _convert_to_enums(pa: str, dim: str) -> tuple[Any, Any]:
    """Convert PA and DIM strings to canonical enum types."""

    policy_area_enum = None
    dimension_enum = None

    if CANONICAL_TYPES_AVAILABLE and PolicyArea is not None and DimensionCausal is not None:
        try:
            policy_area_enum = getattr(PolicyArea, pa, None)

            dim_mapping = {
                "DIM01": DimensionCausal.DIM01_INSUMOS,
                "DIM02": DimensionCausal.DIM02_ACTIVIDADES,
                "DIM03": DimensionCausal.DIM03_PRODUCTOS,
                "DIM04": DimensionCausal.DIM04_RESULTADOS,
                "DIM05": DimensionCausal.DIM05_IMPACTOS,
                "DIM06": DimensionCausal.DIM06_CAUSALIDAD,
            }
            dimension_enum = dim_mapping.get(dim)
        except (AttributeError, KeyError) as e:
            logger.warning(f"Enum conversion failed for {pa}-{dim}: {e}")

    return policy_area_enum, dimension_enum


def _log_chunk_statistics(chunks: list[Chunk], qmap: QuestionnaireMap) -> None:
    """Log statistics about generated chunks."""

    # Count chunks with method invocation results
    chunks_with_methods = sum(
        1 for c in chunks if c.method_invocation_results and len(c.method_invocation_results) > 0
    )

    # Count chunks with element verification
    chunks_with_verification = sum(
        1 for c in chunks if c.elements_verification and len(c.elements_verification) > 0
    )

    # Count successful verifications
    total_required_present = 0
    total_required_checked = 0
    for chunk in chunks:
        for element_spec in chunk.expected_elements:
            if element_spec.get("required", False):
                total_required_checked += 1
                element_type = element_spec.get("type", "")
                if chunk.elements_verification.get(element_type, False):
                    total_required_present += 1

    logger.info(
        f"SP4 v2.0 Statistics: "
        f"{len(chunks)} total chunks, "
        f"{chunks_with_methods} with method invocations, "
        f"{chunks_with_verification} with element verification, "
        f"{total_required_present}/{total_required_checked} required elements present"
    )


__all__ = [
    "TOTAL_CHUNK_COMBINATIONS",
    "TOTAL_QUESTIONS",
    "execute_sp4_question_aware",
]
