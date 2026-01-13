"""
Phase 4 Aggregation Module - Dimension Score Aggregation

This module implements ONLY Phase 4 dimension aggregation:
- PHASE 4: Dimension aggregation (300 micro-questions → 60 dimensions: 6 × 10 policy areas)

Phase 4 Contract:
- Input: 300 ScoredMicroQuestion from Phase 3
- Output: 60 DimensionScore (6 dimensions × 10 policy areas)
- Process: Aggregate 5 micro-questions per dimension using weighted averaging or Choquet integral

Requirements:
- Validation of weights, thresholds, and hermeticity
- Comprehensive logging and abortability
- Full provenance tracking via DAG
- Uncertainty quantification via bootstrap resampling
- Uses canonical notation for dimension and policy area validation

Architecture:
- DimensionAggregator: Aggregates 5 micro questions → 1 dimension score

NOTE: Phases 5, 6, and 7 have been separated into their own modules.
AreaPolicyAggregator, ClusterAggregator, and MacroAggregator are no longer in this file.
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 4
__stage__ = 10
__order__ = 0
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, TypeVar


# Calibration removed - stub placeholders
def get_parameter_loader() -> Any:
    """Stub: Calibration parameter loader removed."""
    return None


def calibrated_method(method_path: str) -> Any:
    """Stub decorator: Calibration removed."""

    def decorator(func: Any) -> Any:
        return func

    return decorator


# SOTA imports
from farfan_pipeline.phases.Phase_4.phase4_10_00_aggregation_provenance import (
    AggregationDAG,
    ProvenanceNode,
)
from farfan_pipeline.phases.Phase_4.phase4_10_00_uncertainty_quantification import (
    BootstrapAggregator,
    UncertaintyMetrics,
    aggregate_with_uncertainty,
)

# Lazy import for SystemicGapDetector to avoid circular dependency with Phase_7 __init__
def _get_systemic_gap_detector():
    """Lazy import SystemicGapDetector from Phase 7."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_systemic_gap_detector import (
        SystemicGapDetector,
    )
    return SystemicGapDetector


def _get_systemic_gap_class():
    """Lazy import SystemicGap dataclass from Phase 7."""
    from farfan_pipeline.phases.Phase_7.phase7_10_00_systemic_gap_detector import (
        SystemicGap,
    )
    return SystemicGap


# For TYPE_CHECKING, import the types
if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_7.phase7_10_00_systemic_gap_detector import (
        SystemicGap,
        SystemicGapDetector,
    )

# Lazy import to avoid circular dependency with choquet_adapter
# choquet_adapter imports AggregationSettings from this module (via TYPE_CHECKING)
# This module imports create_default_choquet_adapter from choquet_adapter
def _get_create_default_choquet_adapter():
    """Lazy import to break circular dependency."""
    from farfan_pipeline.phases.Phase_4.phase4_10_00_choquet_adapter import (
        create_default_choquet_adapter,
    )
    return create_default_choquet_adapter

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from farfan_pipeline.infrastructure.irrigation_using_signals.SISAS.signal_registry import (
        QuestionnaireSignalRegistry,
    )

T = TypeVar("T")


@dataclass(frozen=True)
class AggregationSettings:
    """Resolved aggregation settings derived from the questionnaire monolith.

    SISAS: Now supports construction from signal registry for deterministic irrigation.
    """

    dimension_group_by_keys: list[str]
    area_group_by_keys: list[str]
    cluster_group_by_keys: list[str]
    dimension_question_weights: dict[str, dict[str, float]]
    policy_area_dimension_weights: dict[str, dict[str, float]]
    cluster_policy_area_weights: dict[str, dict[str, float]]
    macro_cluster_weights: dict[str, float]
    dimension_expected_counts: dict[tuple[str, str], int]
    area_expected_dimension_counts: dict[str, int]
    # SISAS: Signal provenance for byte-reproducibility
    source_hash: str | None = None
    sisas_source: str = "legacy"  # "legacy" or "sisas_registry"

    @classmethod
    def from_signal_registry(
        cls,
        registry: QuestionnaireSignalRegistry,
        level: str = "MACRO_1",
    ) -> AggregationSettings:
        """SISAS: Build aggregation settings from signal registry.

        This method provides deterministic, signal-driven aggregation by:
        1. Using AssemblySignalPack for canonical weights
        2. Tracking source_hash for byte-reproducibility
        3. Ensuring single source of truth from registry

        Args:
            registry: SISAS signal registry with assembly signals
            level: Assembly level (MESO_1, MESO_2, MACRO_1)

        Returns:
            AggregationSettings with signal-derived weights

        Raises:
            SignalExtractionError: If assembly signals cannot be retrieved
        """
        logger.info(f"SISAS: Building AggregationSettings from registry (level={level})")

        try:
            # Get assembly signals from registry
            # Note: Using "meso" as the canonical level for aggregation assembly signals
            assembly_pack = registry.get_assembly_signals("meso")
            source_hash = getattr(assembly_pack, "source_hash", None)

            # Extract weights from assembly pack
            cluster_policy_areas = getattr(assembly_pack, "cluster_policy_areas", {})
            dimension_weights = getattr(assembly_pack, "dimension_weights", {})
            aggregation_methods = getattr(assembly_pack, "aggregation_methods", {})

            # Build cluster weights from cluster_policy_areas mapping
            cluster_policy_area_weights: dict[str, dict[str, float]] = {}
            for cluster_id, area_ids in cluster_policy_areas.items():
                if area_ids:
                    equal_weight = 1.0 / len(area_ids)
                    cluster_policy_area_weights[cluster_id] = dict.fromkeys(area_ids, equal_weight)

            # Build macro weights (equal across clusters)
            cluster_ids = list(cluster_policy_areas.keys())
            macro_cluster_weights: dict[str, float] = {}
            if cluster_ids:
                equal_weight = 1.0 / len(cluster_ids)
                macro_cluster_weights = dict.fromkeys(cluster_ids, equal_weight)

            settings = cls(
                dimension_group_by_keys=["policy_area", "dimension"],
                area_group_by_keys=["area_id"],
                cluster_group_by_keys=["cluster_id"],
                dimension_question_weights=dimension_weights,
                policy_area_dimension_weights={},  # Populated from registry if available
                cluster_policy_area_weights=cluster_policy_area_weights,
                macro_cluster_weights=macro_cluster_weights,
                dimension_expected_counts={},
                area_expected_dimension_counts={},
                source_hash=source_hash,
                sisas_source="sisas_registry",
            )

            logger.info(
                f"SISAS: AggregationSettings built from registry - "
                f"clusters={len(cluster_policy_area_weights)}, source_hash={source_hash[:16] if source_hash else 'N/A'}..."
            )

            return settings

        except Exception as e:
            logger.warning(
                "SISAS: Failed to build from registry (%s); falling back to legacy empty weights "
                "(callers will use equal-weight defaults).",
                e,
            )
            # Return empty settings as fallback
            return cls(
                dimension_group_by_keys=["policy_area", "dimension"],
                area_group_by_keys=["area_id"],
                cluster_group_by_keys=["cluster_id"],
                dimension_question_weights={},
                policy_area_dimension_weights={},
                cluster_policy_area_weights={},
                macro_cluster_weights={},
                dimension_expected_counts={},
                area_expected_dimension_counts={},
                source_hash=None,
                sisas_source="legacy_fallback",
            )

    @classmethod
    def from_monolith(cls, monolith: dict[str, Any] | None) -> AggregationSettings:
        """Build aggregation settings from canonical questionnaire data."""
        if not monolith:
            return cls(
                dimension_group_by_keys=["policy_area", "dimension"],
                area_group_by_keys=["area_id"],
                cluster_group_by_keys=["cluster_id"],
                dimension_question_weights={},
                policy_area_dimension_weights={},
                cluster_policy_area_weights={},
                macro_cluster_weights={},
                dimension_expected_counts={},
                area_expected_dimension_counts={},
                source_hash=None,  # SISAS: No hash for empty monolith
                sisas_source="legacy_monolith",  # SISAS: Track source
            )

        blocks = monolith.get("blocks", {})
        niveles = blocks.get("niveles_abstraccion", {})
        policy_areas = niveles.get("policy_areas", [])
        clusters = niveles.get("clusters", [])
        micro_questions = blocks.get("micro_questions", [])

        aggregation_block = (
            monolith.get("aggregation")
            or blocks.get("aggregation")
            or monolith.get("rubric", {}).get("aggregation")
            or {}
        )

        # Map question_id → base_slot for later normalization
        question_slot_lookup: dict[str, str] = {}
        dimension_slot_map: dict[str, set[str]] = defaultdict(set)
        dimension_expected_counts: dict[tuple[str, str], int] = defaultdict(int)

        for question in micro_questions:
            qid = question.get("question_id")
            dim_id = question.get("dimension_id") or question.get("dimension")
            area_id = question.get("policy_area_id") or question.get("policy_area")
            base_slot = question.get("base_slot")

            if dim_id and qid and not base_slot:
                base_slot = f"{dim_id}-{qid}"

            if qid and base_slot:
                question_slot_lookup[qid] = base_slot
                dimension_slot_map[dim_id].add(base_slot)

            if area_id and dim_id:
                dimension_expected_counts[(area_id, dim_id)] += 1

        area_expected_dimension_counts: dict[str, int] = {}
        for area in policy_areas:
            area_id = area.get("policy_area_id") or area.get("id")
            if not area_id:
                continue
            dims = area.get("dimension_ids") or []
            area_expected_dimension_counts[area_id] = len(dims)

        group_by_block = aggregation_block.get("group_by_keys") or {}
        dimension_group_by_keys = cls._coerce_str_list(
            group_by_block.get("dimension"),
            fallback=["policy_area", "dimension"],
        )
        area_group_by_keys = cls._coerce_str_list(
            group_by_block.get("area"),
            fallback=["area_id"],
        )
        cluster_group_by_keys = cls._coerce_str_list(
            group_by_block.get("cluster"),
            fallback=["cluster_id"],
        )

        dimension_question_weights = cls._build_dimension_weights(
            aggregation_block.get("dimension_question_weights") or {},
            question_slot_lookup,
            dimension_slot_map,
        )
        policy_area_dimension_weights = cls._build_area_dimension_weights(
            aggregation_block.get("policy_area_dimension_weights") or {},
            policy_areas,
        )
        cluster_policy_area_weights = cls._build_cluster_weights(
            aggregation_block.get("cluster_policy_area_weights") or {},
            clusters,
        )
        macro_cluster_weights = cls._build_macro_weights(
            aggregation_block.get("macro_cluster_weights") or {},
            clusters,
        )

        return cls(
            dimension_group_by_keys=dimension_group_by_keys,
            area_group_by_keys=area_group_by_keys,
            cluster_group_by_keys=cluster_group_by_keys,
            dimension_question_weights=dimension_question_weights,
            policy_area_dimension_weights=policy_area_dimension_weights,
            cluster_policy_area_weights=cluster_policy_area_weights,
            macro_cluster_weights=macro_cluster_weights,
            dimension_expected_counts=dict(dimension_expected_counts),
            area_expected_dimension_counts=area_expected_dimension_counts,
            source_hash=None,  # SISAS: No hash from raw monolith
            sisas_source="legacy_monolith",  # SISAS: Track source
        )

    @classmethod
    def from_empirical_corpus(
        cls,
        monolith: dict[str, Any] | None = None,
        corpus_path: str | None = None,
    ) -> AggregationSettings:
        """Build aggregation settings with empirical weights from corpus.

        This method enhances monolith-based settings with empirical weights
        from corpus_thresholds_weights.json, providing calibrated dimension
        weights based on 14 real PDT plans.

        Args:
            monolith: Base questionnaire monolith (required for structure)
            corpus_path: Optional path to empirical_weights.json

        Returns:
            AggregationSettings with empirical dimension weights

        Raises:
            ValueError: If monolith is None
        """
        if monolith is None:
            raise ValueError("Monolith required for empirical corpus integration")

        # Start with monolith-based settings
        base_settings = cls.from_monolith(monolith)

        try:
            # Import empirical thresholds loader
            from pathlib import Path

            from farfan_pipeline.phases.Phase_3.phase3_10_00_empirical_thresholds_loader import (
                load_empirical_thresholds,
            )

            # Load empirical corpus
            corpus = load_empirical_thresholds(corpus_path)

            # Extract Phase 5 policy area aggregation weights
            phase5_weights = corpus.get("aggregation_weights", {}).get(
                "phase5_policy_area_aggregation", {}
            )
            dimension_weights = phase5_weights.get("dimension_weights", {})

            if dimension_weights:
                # Apply empirical dimension weights to all policy areas
                # Format: {"DIM01_insumos": 0.15, "DIM02_actividades": 0.15, ...}
                policy_area_dimension_weights = {}

                niveles = monolith.get("blocks", {}).get("niveles_abstraccion", {})
                policy_areas = niveles.get("policy_areas", [])

                for area in policy_areas:
                    area_id = area.get("policy_area_id") or area.get("id")
                    if not area_id:
                        continue

                    # Map dimension IDs to empirical weights
                    area_weights = {}
                    for dim_id in area.get("dimension_ids", []):
                        # Extract dimension type (DIM01, DIM02, etc.) from dim_id
                        # Example: "PA01_DIM01" -> "DIM01"
                        dim_type = dim_id.split("_")[-1] if "_" in dim_id else dim_id

                        # Find matching empirical weight
                        for empirical_key, weight in dimension_weights.items():
                            if dim_type in empirical_key or empirical_key.startswith(dim_type):
                                area_weights[dim_id] = float(weight)
                                break

                    if area_weights:
                        # Normalize weights to sum to 1.0
                        total = sum(area_weights.values())
                        if total > 0:
                            area_weights = {k: v / total for k, v in area_weights.items()}
                        policy_area_dimension_weights[area_id] = area_weights

                if policy_area_dimension_weights:
                    base_settings.policy_area_dimension_weights = policy_area_dimension_weights
                    base_settings.sisas_source = "empirical_corpus"
                    logger.info(
                        f"Empirical corpus integrated: {len(policy_area_dimension_weights)} "
                        f"policy areas with dimension weights from corpus"
                    )
                else:
                    logger.warning("No empirical dimension weights applied (no matching dimensions)")

            else:
                logger.warning("No Phase 5 dimension weights found in empirical corpus")

        except ImportError as e:
            logger.warning(f"Failed to import empirical thresholds loader: {e}")
        except Exception as e:
            logger.warning(f"Failed to load empirical corpus, using monolith weights: {e}")

        return base_settings

    @classmethod
    def from_monolith_or_registry(
        cls,
        monolith: dict[str, Any] | None = None,
        registry: QuestionnaireSignalRegistry | None = None,
        level: str = "MACRO_1",
    ) -> AggregationSettings:
        """SISAS: Transition method - prefer registry, fallback to monolith.

        This method enables gradual migration from legacy monolith-based
        configuration to SISAS signal-driven configuration.

        Args:
            monolith: Legacy questionnaire monolith (fallback)
            registry: SISAS signal registry (preferred)
            level: Assembly level for registry (MESO_1, MESO_2, MACRO_1)

        Returns:
            AggregationSettings from registry if available, else from monolith

        Raises:
            ValueError: If neither registry nor monolith provided
        """
        if registry is not None:
            logger.info("SISAS: Building AggregationSettings from registry (preferred path)")
            return cls.from_signal_registry(registry, level)
        elif monolith is not None:
            logger.info("SISAS: Building AggregationSettings from monolith (fallback path)")
            return cls.from_monolith(monolith)
        else:
            raise ValueError("Must provide either registry or monolith")

    @staticmethod
    def _coerce_str_list(value: Any, *, fallback: list[str]) -> list[str]:
        if isinstance(value, list) and all(isinstance(item, str) for item in value):
            return value or fallback
        return fallback

    @staticmethod
    def _normalize_weights(weight_map: dict[str, float]) -> dict[str, float]:
        if not weight_map:
            return {}
        positive_map = {
            key: float(value)
            for key, value in weight_map.items()
            if isinstance(value, (float, int)) and float(value) >= 0.0
        }
        if not positive_map:
            return {}
        total = sum(positive_map.values())
        if total <= 0:
            return {}
        return {k: value / total for k, value in positive_map.items()}

    @classmethod
    def _build_dimension_weights(
        cls,
        raw_weights: dict[str, dict[str, Any]],
        question_slot_lookup: dict[str, str],
        dimension_slot_map: dict[str, set[str]],
    ) -> dict[str, dict[str, float]]:
        dimension_weights: dict[str, dict[str, float]] = {}
        if raw_weights:
            for dim_id, weights in raw_weights.items():
                resolved: dict[str, float] = {}
                for qid, weight in weights.items():
                    slot = question_slot_lookup.get(qid, qid)
                    try:
                        resolved[slot] = float(weight)
                    except (TypeError, ValueError):
                        continue
                if resolved:
                    normalized = cls._normalize_weights(resolved)
                    if normalized:
                        dimension_weights[dim_id] = normalized

        if not dimension_weights:
            for dim_id, slots in dimension_slot_map.items():
                if not slots:
                    continue
                equal = 1.0 / len(slots)
                dimension_weights[dim_id] = dict.fromkeys(slots, equal)

        return dimension_weights

    @classmethod
    def _build_area_dimension_weights(
        cls,
        raw_weights: dict[str, dict[str, Any]],
        policy_areas: list[dict[str, Any]],
    ) -> dict[str, dict[str, float]]:
        area_weights: dict[str, dict[str, float]] = {}
        if raw_weights:
            for area_id, weights in raw_weights.items():
                resolved: dict[str, float] = {}
                for dim_id, value in weights.items():
                    try:
                        resolved[dim_id] = float(value)
                    except (TypeError, ValueError):
                        continue
                if resolved:
                    normalized = cls._normalize_weights(resolved)
                    if normalized:
                        area_weights[area_id] = normalized

        if not area_weights:
            for area in policy_areas:
                area_id = area.get("policy_area_id") or area.get("id")
                dims = area.get("dimension_ids") or []
                if not area_id or not dims:
                    continue
                equal = 1.0 / len(dims)
                area_weights[area_id] = dict.fromkeys(dims, equal)

        return area_weights

    @classmethod
    def _build_cluster_weights(
        cls,
        raw_weights: dict[str, dict[str, Any]],
        clusters: list[dict[str, Any]],
    ) -> dict[str, dict[str, float]]:
        cluster_weights: dict[str, dict[str, float]] = {}
        if raw_weights:
            for cluster_id, weights in raw_weights.items():
                resolved: dict[str, float] = {}
                for area_id, value in weights.items():
                    try:
                        resolved[area_id] = float(value)
                    except (TypeError, ValueError):
                        continue
                if resolved:
                    normalized = cls._normalize_weights(resolved)
                    if normalized:
                        cluster_weights[cluster_id] = normalized

        if not cluster_weights:
            for cluster in clusters:
                cluster_id = cluster.get("cluster_id")
                area_ids = cluster.get("policy_area_ids") or []
                if not cluster_id or not area_ids:
                    continue
                equal = 1.0 / len(area_ids)
                cluster_weights[cluster_id] = dict.fromkeys(area_ids, equal)

        return cluster_weights

    @classmethod
    def _build_macro_weights(
        cls,
        raw_weights: dict[str, Any],
        clusters: list[dict[str, Any]],
    ) -> dict[str, float]:
        if raw_weights:
            resolved = {}
            for cluster_id, weight in raw_weights.items():
                try:
                    resolved[cluster_id] = float(weight)
                except (TypeError, ValueError):
                    continue
            normalized = cls._normalize_weights(resolved)
            if normalized:
                return normalized

        cluster_ids = [
            cluster.get("cluster_id") for cluster in clusters if cluster.get("cluster_id")
        ]
        if not cluster_ids:
            return {}
        equal = 1.0 / len(cluster_ids)
        return dict.fromkeys(cluster_ids, equal)


def group_by(items: Iterable[T], key_func: Callable[[T], tuple]) -> dict[tuple, list[T]]:
    """
    Groups a sequence of items into a dictionary based on a key function.

    This utility function iterates over a collection, applies a key function to each
    item, and collects items into lists, keyed by the result of the key function.

    The key function must return a tuple. This is because dictionary keys must be
    hashable, and tuples are hashable whereas lists are not. Using a tuple allows
    for grouping by multiple attributes.

    If the input iterable `items` is empty, this function will return an empty
    dictionary.

    Example:
        >>> from dataclasses import dataclass
        >>> @dataclass
        ... class Record:
        ...     category: str
        ...     value: int
        ...
        >>> data = [Record("A", 1), Record("B", 2), Record("A", 3)]
        >>> group_by(data, key_func=lambda r: (r.category,))
        {('A',): [Record(category='A', value=1), Record(category='A', value=3)],
         ('B',): [Record(category='B', value=2)]}

    Args:
        items: An iterable of items to be grouped.
        key_func: A callable that accepts an item and returns a tuple to be
                  used as the grouping key.

    Returns:
        A dictionary where keys are the result of the key function and values are
        lists of items belonging to that group.
    """
    grouped = defaultdict(list)
    for item in items:
        grouped[key_func(item)].append(item)
    return dict(grouped)


def validate_scored_results(results: list[dict[str, Any]]) -> list[ScoredResult]:
    """
    Validates a list of dictionaries and converts them to ScoredResult objects.

    Args:
        results: A list of dictionaries representing scored results.

    Returns:
        A list of ScoredResult objects.

    Raises:
        ValidationError: If any of the dictionaries are invalid.
    """
    validated_results: list[ScoredResult] = []
    required_keys: dict[str, type[Any] | tuple[type[Any], ...]] = {
        "question_global": (int, float, str),
        "base_slot": str,
        "policy_area": str,
        "dimension": str,
        "score": (float, int),
        "quality_level": str,
        "evidence": dict,
        "raw_results": dict,
    }
    for i, res_dict in enumerate(results):
        missing_keys = set(required_keys) - set(res_dict)
        if missing_keys:
            raise ValidationError(f"Invalid ScoredResult at index {i}: missing keys {missing_keys}")

        normalized = dict(res_dict)
        qid = normalized["question_global"]
        if isinstance(qid, bool):
            raise ValidationError(
                f"Invalid type for key 'question_global' at index {i}. "
                f"Expected int|float|str, got bool."
            )
        if isinstance(qid, float):
            if not qid.is_integer():
                raise ValidationError(
                    f"Invalid value for key 'question_global' at index {i}. "
                    f"Expected integer-like float, got {qid}."
                )
            normalized["question_global"] = int(qid)
        elif isinstance(qid, str):
            qid_str = qid.strip()
            if qid_str.isdigit():
                normalized["question_global"] = int(qid_str)
            else:
                normalized["question_global"] = qid_str

        score_value = normalized["score"]
        if isinstance(score_value, bool):
            raise ValidationError(
                f"Invalid type for key 'score' at index {i}. Expected float|int, got bool."
            )
        normalized["score"] = float(score_value)

        for key, expected_type in required_keys.items():
            if key in {"question_global", "score"}:
                continue
            if not isinstance(normalized[key], expected_type):
                raise ValidationError(
                    f"Invalid type for key '{key}' at index {i}. "
                    f"Expected {expected_type}, got {type(normalized[key])}."
                )
        try:
            validated_results.append(ScoredResult(**normalized))
        except TypeError as e:
            raise ValidationError(f"Invalid ScoredResult at index {i}: {e}") from e
    return validated_results


def _normalize_question_node_id(question_id: int | str) -> str:
    if isinstance(question_id, int):
        return f"Q{question_id:03d}"

    question_id_str = question_id.strip()
    suffix = question_id_str.lstrip("Qq")
    if suffix.isdigit():
        return f"Q{int(suffix):03d}"
    return question_id_str


# Import canonical notation for validation
try:
    from farfan_pipeline.core.canonical_notation import get_all_dimensions, get_all_policy_areas

    HAS_CANONICAL_NOTATION = True
except ImportError:
    HAS_CANONICAL_NOTATION = False

logger = logging.getLogger(__name__)


@dataclass
class ScoredResult:
    """Represents a single, scored micro-question, forming the input for aggregation."""

    question_global: int | str
    base_slot: str
    policy_area: str
    dimension: str
    score: float
    quality_level: str
    evidence: dict[str, Any]
    raw_results: dict[str, Any]


@dataclass
class DimensionScore:
    """
    Aggregated score for a single dimension within a policy area.

    SOTA Extensions:
    - Uncertainty quantification (mean, std, CI)
    - Provenance tracking (DAG node ID)
    - Aggregation method recording
    """

    dimension_id: str
    area_id: str
    score: float
    quality_level: str
    contributing_questions: list[int | str]
    validation_passed: bool = True
    validation_details: dict[str, Any] = field(default_factory=dict)

    # SOTA: Uncertainty quantification
    score_std: float = 0.0
    confidence_interval_95: tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    epistemic_uncertainty: float = 0.0
    aleatoric_uncertainty: float = 0.0

    # SOTA: Provenance tracking
    provenance_node_id: str = ""
    aggregation_method: str = "weighted_average"


# NOTE: AreaScore, ClusterScore, and MacroScore have been removed from Phase 4.
# These classes belong to Phases 5, 6, and 7 respectively.
# Phase 4 is ONLY responsible for DimensionScore aggregation.


class AggregationError(Exception):
    """Base exception for aggregation errors."""

    pass


class ValidationError(AggregationError):
    """Raised when validation fails."""

    pass


class WeightValidationError(ValidationError):
    """Raised when weight validation fails."""

    pass


class ThresholdValidationError(ValidationError):
    """Raised when threshold validation fails."""

    pass


class HermeticityValidationError(ValidationError):
    """Raised when hermeticity validation fails."""

    pass


class CoverageError(AggregationError):
    """Raised when coverage requirements are not met."""

    pass


def calculate_weighted_average(scores: list[float], weights: list[float] | None = None) -> float:
    if not scores:
        return 0.0

    if weights is None:
        weights = [1.0 / len(scores)] * len(scores)

    if len(weights) != len(scores):
        msg = f"Weight length mismatch: {len(weights)} weights for {len(scores)} scores"
        logger.error(msg)
        raise WeightValidationError(msg)

    expected_sum = 1.0
    weight_sum = sum(weights)
    tolerance = 1e-6
    if abs(weight_sum - expected_sum) > tolerance:
        msg = f"Weight sum validation failed: sum={weight_sum:.6f}, expected={expected_sum}"
        logger.error(msg)
        raise WeightValidationError(msg)

    return sum(score * weight for score, weight in zip(scores, weights, strict=False))


class DimensionAggregator:
    """
    Aggregates micro question scores into dimension scores.

    Responsibilities:
    - Aggregate 5 micro questions (Q1-Q5) per dimension
    - Validate weights sum to 1.0
    - Apply rubric thresholds
    - Ensure coverage (abort if insufficient)
    - Provide detailed logging
    """

    def __init__(
        self,
        monolith: dict[str, Any] | None = None,
        abort_on_insufficient: bool = True,
        aggregation_settings: AggregationSettings | None = None,
        enable_sota_features: bool = True,
        signal_registry: QuestionnaireSignalRegistry | None = None,  # SISAS injection
    ) -> None:
        """
        Initialize dimension aggregator.

        Args:
            monolith: Questionnaire monolith configuration (optional, required for run())
            abort_on_insufficient: Whether to abort on insufficient coverage
            aggregation_settings: Resolved aggregation settings
            enable_sota_features: Enable SOTA features (Choquet, UQ, provenance)
            signal_registry: SISAS signal registry for signal-driven aggregation

        Raises:
            ValueError: If monolith is None and required for operations
        """
        self.monolith = monolith
        self.abort_on_insufficient = abort_on_insufficient
        self._signal_registry = signal_registry  # SISAS: Cache for signal-driven config

        # SISAS: Use transition method for automatic detection
        # Handle case where both are None gracefully
        if aggregation_settings is not None:
            self.aggregation_settings = aggregation_settings
        elif signal_registry is not None or monolith is not None:
            self.aggregation_settings = AggregationSettings.from_monolith_or_registry(
                monolith=monolith, registry=signal_registry, level="MACRO_1"
            )
        else:
            # Both None - use empty settings (legacy fallback)
            self.aggregation_settings = AggregationSettings.from_monolith(None)
        self.dimension_group_by_keys = self.aggregation_settings.dimension_group_by_keys or [
            "policy_area",
            "dimension",
        ]
        self.enable_sota_features = enable_sota_features

        # Extract configuration if monolith provided
        if monolith is not None:
            self.scoring_config = monolith["blocks"]["scoring"]
            self.niveles = monolith["blocks"]["niveles_abstraccion"]
        else:
            self.scoring_config = None
            self.niveles = None

        # SOTA: Initialize provenance DAG
        if self.enable_sota_features:
            self.provenance_dag = AggregationDAG()
            self.bootstrap_aggregator = BootstrapAggregator(iterations=1000, seed=42)
            logger.info("DimensionAggregator initialized with SOTA features enabled")
        else:
            self.provenance_dag = None
            self.bootstrap_aggregator = None
            logger.info("DimensionAggregator initialized (legacy mode)")

        # Validate canonical notation if available
        if HAS_CANONICAL_NOTATION:
            try:
                canonical_dims = get_all_dimensions()
                canonical_areas = get_all_policy_areas()
                logger.info(
                    f"Canonical notation loaded: {len(canonical_dims)} dimensions, "
                    f"{len(canonical_areas)} policy areas"
                )
            except Exception as e:
                logger.warning(f"Could not load canonical notation: {e}")

    @calibrated_method(
        "farfan_core.processing.aggregation.DimensionAggregator.validate_dimension_id"
    )
    def validate_dimension_id(self, dimension_id: str) -> bool:
        """
        Validate dimension ID against canonical notation.

        Args:
            dimension_id: Dimension ID to validate (e.g., "DIM01")

        Returns:
            True if dimension ID is valid

        Raises:
            ValidationError: If dimension ID is invalid and abort_on_insufficient is True
        """
        if not HAS_CANONICAL_NOTATION:
            logger.debug("Canonical notation not available, skipping validation")
            return True

        try:
            canonical_dims = get_all_dimensions()
            # Check if dimension_id is a valid code
            valid_codes = {info.code for info in canonical_dims.values()}
            if dimension_id in valid_codes:
                return True

            msg = f"Invalid dimension ID: {dimension_id}. Valid codes: {sorted(valid_codes)}"
            logger.error(msg)
            if self.abort_on_insufficient:
                raise ValidationError(msg)
            return False
        except Exception as e:
            logger.warning(f"Could not validate dimension ID: {e}")
            return True  # Don't fail if validation can't be performed

    @calibrated_method(
        "farfan_core.processing.aggregation.DimensionAggregator.validate_policy_area_id"
    )
    def validate_policy_area_id(self, area_id: str) -> bool:
        """
        Validate policy area ID against canonical notation.

        Args:
            area_id: Policy area ID to validate (e.g., "PA01")

        Returns:
            True if policy area ID is valid

        Raises:
            ValidationError: If policy area ID is invalid and abort_on_insufficient is True
        """
        if not HAS_CANONICAL_NOTATION:
            logger.debug("Canonical notation not available, skipping validation")
            return True

        try:
            canonical_areas = get_all_policy_areas()
            if area_id in canonical_areas:
                return True

            msg = (
                f"Invalid policy area ID: {area_id}. Valid codes: {sorted(canonical_areas.keys())}"
            )
            logger.error(msg)
            if self.abort_on_insufficient:
                raise ValidationError(msg)
            return False
        except Exception as e:
            logger.warning(f"Could not validate policy area ID: {e}")
            return True  # Don't fail if validation can't be performed

    @calibrated_method("farfan_core.processing.aggregation.DimensionAggregator.validate_weights")
    def validate_weights(self, weights: list[float]) -> tuple[bool, str]:
        """
        Ensures that a list of weights sums to 1.0 within a small tolerance.

        Args:
            weights: A list of floating-point weights.

        Returns:
            A tuple containing a boolean indicating validity and a descriptive message.

        Raises:
            WeightValidationError: If `abort_on_insufficient` is True and validation fails.
        """
        if not weights:
            msg = "No weights provided"
            logger.error(msg)
            if self.abort_on_insufficient:
                raise WeightValidationError(msg)
            return False, msg

        weight_sum = sum(weights)
        tolerance = 1e-6

        if abs(weight_sum - 1.0) > tolerance:
            expected_weight = 1.0
            msg = f"Weight sum validation failed: sum={weight_sum:.6f}, expected={expected_weight}"
            logger.error(msg)
            if self.abort_on_insufficient:
                raise WeightValidationError(msg)
            return False, msg

        logger.debug(f"Weight validation passed: sum={weight_sum:.6f}")
        return True, "Weights valid"

    def validate_coverage(
        self, results: list[ScoredResult], expected_count: int = 5
    ) -> tuple[bool, str]:
        """
        Checks if the number of results meets a minimum expectation.

        Args:
            results: A list of ScoredResult objects.
            expected_count: The minimum number of results required.

        Returns:
            A tuple containing a boolean indicating validity and a descriptive message.

        Raises:
            CoverageError: If `abort_on_insufficient` is True and coverage is insufficient.
        """
        actual_count = len(results)

        if actual_count < expected_count:
            msg = (
                f"Coverage validation failed: "
                f"expected {expected_count} questions, got {actual_count}"
            )
            logger.error(msg)
            if self.abort_on_insufficient:
                raise CoverageError(msg)
            return False, msg

        logger.debug(f"Coverage validation passed: {actual_count}/{expected_count} questions")
        return True, "Coverage sufficient"

    def calculate_weighted_average(
        self, scores: list[float], weights: list[float] | None = None
    ) -> float:
        """
        Calculates a weighted average, defaulting to an equal weighting if none provided.

        Args:
            scores: A list of scores to be averaged.
            weights: An optional list of weights. If None, equal weights are assumed.

        Returns:
            The calculated weighted average.

        Raises:
            WeightValidationError: If the weights are invalid (e.g., mismatched length).
        """
        weighted_sum = calculate_weighted_average(scores, weights)
        logger.debug(
            "Weighted average calculated: scores=%s, weights=%s, result=%.4f",
            scores,
            weights,
            weighted_sum,
        )
        return weighted_sum

    def aggregate_with_sota(
        self,
        scores: list[float],
        weights: list[float] | None = None,
        method: str = "choquet",
        compute_uncertainty: bool = True,
    ) -> tuple[float, UncertaintyMetrics | None]:
        """
        SOTA aggregation with Choquet integral and uncertainty quantification.

        This method provides:
        1. Non-linear aggregation via Choquet integral (captures synergies)
        2. Bayesian uncertainty quantification via bootstrap
        3. Full reproducibility with fixed random seed

        Args:
            scores: Input scores to aggregate
            weights: Optional weights (default: uniform)
            method: Aggregation method ("choquet" or "weighted_average")
            compute_uncertainty: Whether to compute uncertainty metrics

        Returns:
            Tuple of (aggregated_score, uncertainty_metrics)
            If compute_uncertainty=False, uncertainty_metrics is None

        Raises:
            ValueError: If scores is empty or method invalid
        """
        if not scores:
            raise ValueError("Cannot aggregate empty score list")

        if method == "choquet":
            # Use Choquet integral for non-linear aggregation
            # Lazy import to avoid circular dependency
            create_default_choquet_adapter = _get_create_default_choquet_adapter()
            choquet_adapter = create_default_choquet_adapter(len(scores))
            score = choquet_adapter.aggregate(scores, weights)
            logger.info(f"Choquet aggregation: {len(scores)} inputs → {score:.4f}")
        elif method == "weighted_average":
            # Fall back to standard weighted average
            score = self.calculate_weighted_average(scores, weights)
        else:
            raise ValueError(f"Unknown aggregation method: {method}")

        # Compute uncertainty if requested
        uncertainty = None
        if compute_uncertainty and self.bootstrap_aggregator:
            _, uncertainty = aggregate_with_uncertainty(
                scores, weights, n_bootstrap=1000, random_seed=42
            )
            logger.debug(
                f"Uncertainty: mean={uncertainty.mean:.4f}, "
                f"std={uncertainty.std:.4f}, "
                f"CI95={uncertainty.confidence_interval_95}"
            )

        return score, uncertainty

    def apply_rubric_thresholds(
        self, score: float, thresholds: dict[str, float] | None = None
    ) -> str:
        """
        Apply rubric thresholds to determine quality level.

        Args:
            score: Aggregated score (0-3 range)
            thresholds: Optional threshold definitions (dict with keys: EXCELENTE, BUENO, ACEPTABLE)
                       Each value should be a normalized threshold (0-1 range)

        Returns:
            Quality level (EXCELENTE, BUENO, ACEPTABLE, INSUFICIENTE)
        """
        # Clamp score to valid range [0, 3]
        clamped_score = max(0.0, min(3.0, score))

        # Normalize to 0-1 range
        normalized_score = clamped_score / 3.0

        # Use provided thresholds or defaults
        if thresholds:
            excellent_threshold = thresholds.get("EXCELENTE", 0.85)
            good_threshold = thresholds.get("BUENO", 0.70)
            acceptable_threshold = thresholds.get("ACEPTABLE", 0.55)
        else:
            excellent_threshold = 0.85  # Refactored
            good_threshold = 0.7  # Refactored
            acceptable_threshold = 0.55  # Refactored

        # Apply thresholds
        if normalized_score >= excellent_threshold:
            quality = "EXCELENTE"
        elif normalized_score >= good_threshold:
            quality = "BUENO"
        elif normalized_score >= acceptable_threshold:
            quality = "ACEPTABLE"
        else:
            quality = "INSUFICIENTE"

        logger.debug(
            f"Rubric applied: score={score:.4f}, "
            f"normalized={normalized_score:.4f}, quality={quality}"
        )

        return quality

    def aggregate_dimension(
        self,
        scored_results: list[ScoredResult],
        group_by_values: dict[str, Any],
        weights: list[float] | None = None,
    ) -> DimensionScore:
        """
        Aggregate a single dimension from micro question results.

        Args:
            scored_results: List of scored results for this dimension/area.
            group_by_values: Dictionary of grouping keys and their values.
            weights: Optional weights for questions (defaults to equal weights).

        Returns:
            DimensionScore with aggregated score and quality level.

        Raises:
            ValidationError: If validation fails.
            CoverageError: If coverage is insufficient.
        """
        dimension_id = group_by_values.get("dimension", "UNKNOWN")
        area_id = group_by_values.get("policy_area", "UNKNOWN")
        logger.info(f"Aggregating dimension {dimension_id} for area {area_id}")

        validation_details = {}

        # In this context, scored_results are already grouped, so we can use them directly.
        dim_results = scored_results

        expected_count = self._expected_question_count(area_id, dimension_id)

        # Validate coverage
        try:
            coverage_valid, coverage_msg = self.validate_coverage(
                dim_results,
                expected_count=expected_count or 5,
            )
            validation_details["coverage"] = {
                "valid": coverage_valid,
                "message": coverage_msg,
                "count": len(dim_results),
            }
        except CoverageError as e:
            logger.error(f"Coverage validation failed for {dimension_id}/{area_id}: {e}")
            # Return minimal score if aborted
            return DimensionScore(
                dimension_id=dimension_id,
                area_id=area_id,
                score=0.0,
                quality_level="INSUFICIENTE",
                contributing_questions=[],
                validation_passed=False,
                validation_details={"error": str(e), "type": "coverage"},
            )

        if not dim_results:
            logger.warning(f"No results for dimension {dimension_id}/{area_id}")
            return DimensionScore(
                dimension_id=dimension_id,
                area_id=area_id,
                score=0.0,
                quality_level="INSUFICIENTE",
                contributing_questions=[],
                validation_passed=False,
                validation_details={"error": "No results", "type": "empty"},
            )

        raw_scores = [r.score for r in dim_results]
        scores = [min(3.0, max(0.0, score)) for score in raw_scores]
        n_clamped = sum(
            1 for raw, clamped in zip(raw_scores, scores, strict=False) if raw != clamped
        )
        if n_clamped:
            validation_details["clamping"] = {
                "applied": True,
                "n_clamped": n_clamped,
                "original_min": min(raw_scores),
                "original_max": max(raw_scores),
                "clamped_min": min(scores),
                "clamped_max": max(scores),
            }

        question_ids = [r.question_global for r in dim_results]

        # Calculate weighted average with SOTA features
        resolved_weights = weights or self._resolve_dimension_weights(dimension_id, dim_results)

        # SOTA: Use Choquet + uncertainty if enabled
        if self.enable_sota_features and len(scores) >= 3:
            try:
                avg_score, uncertainty = self.aggregate_with_sota(
                    scores,
                    resolved_weights,
                    method="choquet",
                    compute_uncertainty=True,
                )
                validation_details["aggregation"] = {
                    "method": "choquet",
                    "uncertainty": uncertainty.to_dict() if uncertainty else None,
                }
            except Exception as e:
                logger.warning(f"SOTA aggregation failed, falling back to standard: {e}")
                avg_score = self.calculate_weighted_average(scores, resolved_weights)
                uncertainty = None
                validation_details["aggregation"] = {"method": "weighted_average", "fallback": True}
        else:
            # Standard aggregation
            avg_score = self.calculate_weighted_average(scores, resolved_weights)
            uncertainty = None
            validation_details["aggregation"] = {"method": "weighted_average"}

        validation_details["weights"] = {
            "valid": True,
            "weights": resolved_weights if resolved_weights else "equal",
            "score": avg_score,
        }

        # Apply rubric thresholds
        quality_level = self.apply_rubric_thresholds(avg_score)
        validation_details["rubric"] = {"score": avg_score, "quality_level": quality_level}
        validation_details["score_max"] = 3.0

        # SOTA: Add provenance tracking
        provenance_node_id = f"DIM_{dimension_id}_{area_id}"
        if self.enable_sota_features and self.provenance_dag:
            # Add dimension node
            dim_node = ProvenanceNode(
                node_id=provenance_node_id,
                level="dimension",
                score=avg_score,
                quality_level=quality_level,
                metadata={
                    "dimension_id": dimension_id,
                    "area_id": area_id,
                    "n_questions": len(question_ids),
                },
            )
            self.provenance_dag.add_node(dim_node)

            # Add aggregation edges from questions to dimension
            question_node_ids = [_normalize_question_node_id(qid) for qid in question_ids]
            for qid_str, score_value in zip(question_node_ids, scores, strict=False):
                # Add question node if not exists
                if qid_str not in self.provenance_dag.nodes:
                    q_node = ProvenanceNode(
                        node_id=qid_str,
                        level="micro",
                        score=score_value,
                        quality_level="UNKNOWN",
                    )
                    self.provenance_dag.add_node(q_node)

            # Record aggregation operation
            self.provenance_dag.add_aggregation_edge(
                source_ids=question_node_ids,
                target_id=provenance_node_id,
                operation="choquet" if self.enable_sota_features else "weighted_average",
                weights=resolved_weights or [1.0 / len(question_ids)] * len(question_ids),
                metadata={"dimension": dimension_id, "area": area_id},
            )

            logger.debug(
                f"Provenance recorded: {len(question_node_ids)} questions → {provenance_node_id}"
            )

        logger.info(
            f"✓ Dimension {dimension_id}/{area_id}: "
            f"score={avg_score:.4f}, quality={quality_level}"
            + (f", std={uncertainty.std:.4f}" if uncertainty else "")
        )

        return DimensionScore(
            dimension_id=dimension_id,
            area_id=area_id,
            score=avg_score,
            quality_level=quality_level,
            contributing_questions=question_ids,
            validation_passed=True,
            validation_details=validation_details,
            # SOTA fields
            score_std=uncertainty.std if uncertainty else 0.0,
            confidence_interval_95=(
                uncertainty.confidence_interval_95 if uncertainty else (0.0, 0.0)
            ),
            epistemic_uncertainty=uncertainty.epistemic_uncertainty if uncertainty else 0.0,
            aleatoric_uncertainty=uncertainty.aleatoric_uncertainty if uncertainty else 0.0,
            provenance_node_id=provenance_node_id if self.enable_sota_features else "",
            aggregation_method=(
                "choquet"
                if (self.enable_sota_features and len(scores) >= 3)
                else "weighted_average"
            ),
        )

    def run(
        self, scored_results: list[ScoredResult], group_by_keys: list[str]
    ) -> list[DimensionScore]:
        """
        Run the dimension aggregation process.

        Args:
            scored_results: List of all scored results.
            group_by_keys: List of keys to group by.

        Returns:
            A list of DimensionScore objects.
        """

        def key_func(r):
            return tuple(getattr(r, key) for key in group_by_keys)

        grouped_results = group_by(scored_results, key_func)

        dimension_scores = []
        for group_key, results in grouped_results.items():
            group_by_values = dict(zip(group_by_keys, group_key, strict=False))
            score = self.aggregate_dimension(results, group_by_values)
            dimension_scores.append(score)

        return dimension_scores

    @calibrated_method(
        "farfan_core.processing.aggregation.DimensionAggregator._expected_question_count"
    )
    def _expected_question_count(self, area_id: str, dimension_id: str) -> int | None:
        if not self.aggregation_settings.dimension_expected_counts:
            return None
        return self.aggregation_settings.dimension_expected_counts.get((area_id, dimension_id))

    def _resolve_dimension_weights(
        self,
        dimension_id: str,
        dim_results: list[ScoredResult],
    ) -> list[float] | None:
        mapping = self.aggregation_settings.dimension_question_weights.get(dimension_id)
        if not mapping:
            return None

        weights: list[float] = []
        for result in dim_results:
            slot = result.base_slot
            weight = mapping.get(slot)
            if weight is None:
                logger.debug(
                    "Missing weight for slot %s in dimension %s – falling back to equal weights",
                    slot,
                    dimension_id,
                )
                return None
            weights.append(weight)

        total = sum(weights)
        if total <= 0:
            return None
        return [w / total for w in weights]


# NOTE: run_aggregation_pipeline has been removed from Phase 4.
# This function orchestrated Phases 4-7 which is no longer appropriate.
# Phase 4 should only handle dimension aggregation.
# For multi-phase aggregation, use the appropriate phase modules directly.

