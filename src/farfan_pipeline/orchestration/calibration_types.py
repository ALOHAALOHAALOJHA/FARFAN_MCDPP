"""
Calibration Types for Orchestrator API
======================================

Module: calibration_types.py
Owner: farfan_pipeline.orchestration
Purpose: Type definitions for Orchestrator.calibrate_method() API
Schema Version: 1.0.0

This module provides the bridge types between the main Orchestrator and
the infrastructure calibration stack (infrastructure/calibration/).

DESIGN DECISION (TS-OPT-B-001):
    Option B selected - Direct integration without adapter layer.
    These types enable the Orchestrator to directly consume the existing
    calibration infrastructure without intermediate compatibility layers.

INVARIANTS ENFORCED:
    INV-CS-001: CalibrationSubject.method_id is non-empty
    INV-CS-002: CalibrationSubject.role is one of VALID_ROLES
    INV-CS-003: CalibrationSubject.context is immutable (MappingProxyType)
    INV-CEC-001: CalibrationEvidenceContext scores in [0.0, 1.0]
    INV-CR-001: CalibrationResult.final_score in [0.0, 1.0]
    INV-CR-002: All CalibrationResult.layer_scores values in [0.0, 1.0]
    INV-CR-003: CalibrationResult.active_layers is non-empty

ROLE-LAYER ACTIVATION:
    Each execution role activates a specific subset of the 8 calibration layers.
    This follows the FARFAN epistemic architecture with role-based layer binding.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any

# =============================================================================
# LAYER IDENTIFIERS
# =============================================================================


class LayerId(Enum):
    """
    Calibration layer identifiers per FARFAN architecture.

    The 8 layers correspond to distinct epistemic dimensions:
    - @b (BASE): Foundational calibration parameters
    - @chain (CHAIN): Method chain coherence
    - @u (UNIT): Unit of analysis calibration
    - @q (QUESTION): Question-specific calibration
    - @d (DIMENSION): Dimension-level aggregation calibration
    - @p (POLICY): Policy area calibration
    - @C (CONGRUENCE): Cross-dimension congruence checks
    - @m (META): Meta-level calibration (audit, signatures)
    """

    BASE = "@b"
    CHAIN = "@chain"
    UNIT = "@u"
    QUESTION = "@q"
    DIMENSION = "@d"
    POLICY = "@p"
    CONGRUENCE = "@C"
    META = "@m"


# =============================================================================
# ROLE-LAYER ACTIVATION MATRIX
# =============================================================================


ROLE_LAYER_REQUIREMENTS: Mapping[str, frozenset[LayerId]] = MappingProxyType(
    {
        "INGEST_PDM": frozenset({LayerId.BASE, LayerId.CHAIN, LayerId.UNIT, LayerId.META}),
        "STRUCTURE": frozenset({LayerId.BASE, LayerId.CHAIN, LayerId.UNIT, LayerId.META}),
        "EXTRACT": frozenset({LayerId.BASE, LayerId.CHAIN, LayerId.UNIT, LayerId.META}),
        "SCORE_Q": frozenset(
            {
                LayerId.BASE,
                LayerId.CHAIN,
                LayerId.QUESTION,
                LayerId.DIMENSION,
                LayerId.POLICY,
                LayerId.CONGRUENCE,
                LayerId.UNIT,
                LayerId.META,
            }
        ),
        "AGGREGATE": frozenset(
            {
                LayerId.BASE,
                LayerId.CHAIN,
                LayerId.DIMENSION,
                LayerId.POLICY,
                LayerId.CONGRUENCE,
                LayerId.META,
            }
        ),
        "REPORT": frozenset({LayerId.BASE, LayerId.CHAIN, LayerId.CONGRUENCE, LayerId.META}),
        "META_TOOL": frozenset({LayerId.BASE, LayerId.CHAIN, LayerId.META}),
        "TRANSFORM": frozenset({LayerId.BASE, LayerId.CHAIN, LayerId.META}),
    }
)

# Valid roles extracted from matrix for validation
VALID_ROLES: frozenset[str] = frozenset(ROLE_LAYER_REQUIREMENTS.keys())


# =============================================================================
# CALIBRATION SUBJECT
# =============================================================================


@dataclass(frozen=True, slots=True)
class CalibrationSubject:
    """
    Immutable descriptor of the entity being calibrated.

    Invariants:
        INV-CS-001: method_id is non-empty
        INV-CS-002: role is one of VALID_ROLES
        INV-CS-003: context is immutable (MappingProxyType)

    Attributes:
        method_id: Fully qualified method identifier
            (e.g., "farfan_pipeline.core.executors.D1Q1_Executor")
        role: Execution role determining layer activation
            ("INGEST_PDM", "STRUCTURE", "EXTRACT", "SCORE_Q",
             "AGGREGATE", "REPORT", "META_TOOL", "TRANSFORM")
        context: Immutable mapping of contextual data
            (question_id, dimension_id, policy_area_id, etc.)
    """

    method_id: str
    role: str
    context: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        # INV-CS-001: method_id non-empty
        if not self.method_id.strip():
            raise ValueError("method_id cannot be empty")

        # INV-CS-002: valid role
        if self.role not in VALID_ROLES:
            raise ValueError(f"role must be one of {VALID_ROLES}, got: {self.role}")

        # INV-CS-003: ensure context is immutable
        if not isinstance(self.context, MappingProxyType):
            object.__setattr__(self, "context", MappingProxyType(dict(self.context)))

    def get_active_layers(self) -> frozenset[LayerId]:
        """Return the set of layers activated by this subject's role."""
        return ROLE_LAYER_REQUIREMENTS.get(self.role, frozenset())


# =============================================================================
# CALIBRATION EVIDENCE CONTEXT
# =============================================================================


@dataclass(frozen=True, slots=True)
class CalibrationEvidenceContext:
    """
    Document and question context for calibration layer evaluation.

    This replaces the non-existent 'EvidenceStore' with a properly scoped type
    that captures the evidence needed for calibration decisions.

    Invariants:
        INV-CEC-001: document_quality in [0.0, 1.0]
        INV-CEC-002: completeness in [0.0, 1.0]
        INV-CEC-003: structure_quality in [0.0, 1.0]

    Attributes:
        chunk_count: Number of document chunks (60 expected for standard CPP)
        completeness: Document extraction completeness score
        structure_quality: Document structural quality score
        document_quality: Overall document quality metric
        question_id: Current question identifier (e.g., "Q001")
        dimension_id: Dimension identifier (e.g., "D1")
        policy_area_id: Policy area identifier (e.g., "PA01")
    """

    chunk_count: int
    completeness: float
    structure_quality: float
    document_quality: float
    question_id: str | None = None
    dimension_id: str | None = None
    policy_area_id: str | None = None

    def __post_init__(self) -> None:
        # Validate score bounds
        for attr_name in ("completeness", "structure_quality", "document_quality"):
            value = getattr(self, attr_name)
            if not (0.0 <= value <= 1.0):
                raise ValueError(f"{attr_name} must be in [0.0, 1.0], got: {value}")

        # Validate chunk_count
        if self.chunk_count < 0:
            raise ValueError(f"chunk_count must be non-negative, got: {self.chunk_count}")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for passing to calibration infrastructure."""
        return {
            "chunk_count": self.chunk_count,
            "completeness": self.completeness,
            "structure_quality": self.structure_quality,
            "document_quality": self.document_quality,
            "question_id": self.question_id,
            "dimension_id": self.dimension_id,
            "policy_area_id": self.policy_area_id,
        }


# =============================================================================
# CALIBRATION RESULT
# =============================================================================


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    """
    Immutable result of calibration computation.

    Invariants:
        INV-CR-001: final_score in [0.0, 1.0]
        INV-CR-002: All layer_scores values in [0.0, 1.0]
        INV-CR-003: active_layers is non-empty

    Attributes:
        method_id: Method that was calibrated
        role: Role used for layer activation
        final_score: Aggregated calibration score (Choquet integral)
        layer_scores: Per-layer scores keyed by LayerId
        active_layers: Tuple of LayerIds that were evaluated
        metadata: Additional calibration metadata
    """

    method_id: str
    role: str
    final_score: float
    layer_scores: Mapping[LayerId, float]
    active_layers: tuple[LayerId, ...]
    metadata: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))

    def __post_init__(self) -> None:
        # INV-CR-001: final_score bounds
        if not (0.0 <= self.final_score <= 1.0):
            raise ValueError(f"final_score must be in [0.0, 1.0], got: {self.final_score}")

        # INV-CR-002: layer_scores bounds
        for layer_id, score in self.layer_scores.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"layer_scores[{layer_id}] must be in [0.0, 1.0], got: {score}")

        # INV-CR-003: non-empty active_layers
        if not self.active_layers:
            raise ValueError("active_layers cannot be empty")

        # Ensure metadata is immutable
        if not isinstance(self.metadata, MappingProxyType):
            object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for logging/storage."""
        return {
            "method_id": self.method_id,
            "role": self.role,
            "final_score": self.final_score,
            "layer_scores": {k.value: v for k, v in self.layer_scores.items()},
            "active_layers": [layer.value for layer in self.active_layers],
            "metadata": dict(self.metadata),
        }

    def get_layer_score(self, layer_id: LayerId) -> float | None:
        """Get score for a specific layer, or None if not evaluated."""
        return self.layer_scores.get(layer_id)

    def is_layer_active(self, layer_id: LayerId) -> bool:
        """Check if a layer was active in this calibration."""
        return layer_id in self.active_layers


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    # Enumeration
    "LayerId",
    # Role-Layer mapping
    "ROLE_LAYER_REQUIREMENTS",
    "VALID_ROLES",
    # Subject and context types
    "CalibrationSubject",
    "CalibrationEvidenceContext",
    # Result type
    "CalibrationResult",
]
