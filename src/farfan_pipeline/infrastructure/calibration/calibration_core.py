"""
Calibration Layer Core Types
============================
Module: calibration_core.py
Purpose: Foundational types for calibration within epistemic regime
Lifecycle: DESIGN-TIME FROZEN, RUNTIME IMMUTABLE

INVARIANTS ENFORCED:
- INV-CAL-FREEZE-001: All calibration parameters immutable post-construction
- INV-CAL-REGIME-001: Calibration operates within existing epistemic regime
- INV-CAL-AUDIT-001: All parameters subject to N3-AUD verification
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
class CalibrationPhase(Enum):
    """Phase in which calibration applies."""

    INGESTION = auto()
    PHASE_2_COMPUTATION = auto()


@dataclass(frozen=True, slots=True)
class CalibrationBounds:
    """Immutable bounds for a calibration parameter."""

    min_value: float
    max_value: float
    default_value: float
    unit: str

    def __post_init__(self) -> None:
        if not (self.min_value <= self.default_value <= self.max_value):
            raise ValueError(
                f"Default {self.default_value} not in [{self.min_value}, {self.max_value}]"
            )


@dataclass(frozen=True, slots=True)
class CalibrationParameter:
    """Single calibration parameter with full provenance."""

    name: str
    value: float
    bounds: CalibrationBounds
    rationale: str
    source_evidence: str
    calibration_date: datetime
    validity_days: int

    def __post_init__(self) -> None:
        if not (self.bounds.min_value <= self.value <= self.bounds.max_value):
            raise ValueError(
                f"Value {self.value} violates bounds [{self.bounds.min_value}, {self.bounds.max_value}]"
            )
        if not self.rationale:
            raise ValueError("Rationale cannot be empty")
        if not self.source_evidence.startswith("src/") and not self.source_evidence.startswith(
            "artifacts/"
        ):
            raise ValueError(
                f"Source evidence must reference repo path, got: {self.source_evidence}"
            )

    def is_valid_at(self, check_date: datetime) -> bool:
        """Check if parameter is still within validity window."""
        age_days = (check_date - self.calibration_date).days
        return age_days <= self.validity_days

    def content_hash(self) -> str:
        """SHA-256 hash for integrity verification."""
        content = f"{self.name}|{self.value}|{self.bounds}|{self.rationale}|{self.source_evidence}"
        return hashlib.sha256(content.encode()).hexdigest()


@dataclass(frozen=True, slots=True)
class CalibrationLayer:
    """
    Complete calibration configuration for a contract.

    REGIME COMPLIANCE:
    - This layer operates WITHIN the epistemic regime, not parallel to it
    - All parameters are frozen at design-time
    - N3-AUD methods can audit but not modify calibration
    """

    unit_of_analysis_id: str
    phase: CalibrationPhase
    contract_type_code: str

    prior_strength: CalibrationParameter
    veto_threshold: CalibrationParameter
    chunk_size: CalibrationParameter
    extraction_coverage_target: CalibrationParameter

    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: str = field(default="1.0.0", init=False)

    def manifest_hash(self) -> str:
        """Compute hash of entire calibration manifest."""
        components = [
            self.unit_of_analysis_id,
            self.phase.name,
            self.contract_type_code,
            self.prior_strength.content_hash(),
            self.veto_threshold.content_hash(),
            self.chunk_size.content_hash(),
            self.extraction_coverage_target.content_hash(),
        ]
        return hashlib.sha256("|".join(components).encode()).hexdigest()
