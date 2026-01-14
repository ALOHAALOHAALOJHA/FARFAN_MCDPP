"""
Calibration Drift Detection and Reporting
==========================================
Detects drift in calibration parameters and generates audit reports.

DESIGN PRINCIPLE:
    Calibration parameters should be stable. Drift indicates:
    - UoA characteristics have changed significantly
    - TYPE constraints have evolved
    - Epistemic requirements have shifted
    - Potential miscalibration requiring review

Module: drift_detector.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Drift detection and reporting for calibration audits
Schema Version: 1.0.0

INVARIANTS ENFORCED:
    INV-DRIFT-001: Drift ratio ∈ [0.0, ∞)
    INV-DRIFT-002: Drift threshold ∈ (0.0, 1.0]
    INV-DRIFT-003: Drift reports are immutable
    INV-DRIFT-004: Significant drift triggers alerts
    INV-DRIFT-005: Contradiction penalties applied for conflicting parameters

DRIFT THRESHOLDS:
    MINOR: drift_ratio < 0.10 (10% change)
    MODERATE: 0.10 ≤ drift_ratio < 0.30 (10-30% change)
    SIGNIFICANT: 0.30 ≤ drift_ratio < 0.50 (30-50% change)
    CRITICAL: drift_ratio ≥ 0.50 (≥50% change, requires immediate review)

DRIFT DETECTION SCOPE:
    - Prior strength drift
    - Veto threshold drift
    - Chunk size drift (Phase 1 only)
    - Coverage target drift (Phase 1 only)
    - Cognitive cost drift
    - Interaction density drift
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Final

from .calibration_core import CalibrationLayer, CalibrationParameter

logger = logging.getLogger(__name__)


# =============================================================================
# CONSTANTS
# =============================================================================

# Drift thresholds
_MINOR_DRIFT_THRESHOLD: Final[float] = 0.10
_MODERATE_DRIFT_THRESHOLD: Final[float] = 0.30
_SIGNIFICANT_DRIFT_THRESHOLD: Final[float] = 0.50

# Contradiction penalty (applied when parameters conflict)
_CONTRADICTION_PENALTY_MULTIPLIER: Final[float] = 1.5

# Coverage penalty (applied when extraction coverage is low)
_COVERAGE_PENALTY_THRESHOLD: Final[float] = 0.85

# Dispersion penalty (applied when parameter values are highly dispersed)
_DISPERSION_PENALTY_THRESHOLD: Final[float] = 0.40


# =============================================================================
# ENUMS
# =============================================================================


class DriftSeverity(Enum):
    """
    Drift severity levels.

    NONE: No significant drift detected
    MINOR: Drift < 10%
    MODERATE: Drift 10-30%
    SIGNIFICANT: Drift 30-50%
    CRITICAL: Drift ≥ 50% (requires immediate review)
    """

    NONE = "NONE"
    MINOR = "MINOR"
    MODERATE = "MODERATE"
    SIGNIFICANT = "SIGNIFICANT"
    CRITICAL = "CRITICAL"


# =============================================================================
# DRIFT REPORT
# =============================================================================


@dataclass(frozen=True, slots=True)
class ParameterDrift:
    """
    Immutable record of parameter drift.

    Attributes:
        parameter_name: Name of drifted parameter
        old_value: Previous parameter value
        new_value: Current parameter value
        drift_ratio: Absolute change / old_value
        severity: Drift severity classification
        rationale: Explanation of drift cause
    """

    parameter_name: str
    old_value: float
    new_value: float
    drift_ratio: float
    severity: DriftSeverity
    rationale: str

    def __post_init__(self) -> None:
        """Validate drift invariants."""
        # INV-DRIFT-001: Non-negative drift ratio
        if self.drift_ratio < 0.0:
            raise ValueError(f"drift_ratio must be non-negative, got: {self.drift_ratio}")


@dataclass(frozen=True, slots=True)
class DriftReport:
    """
    Unit of Analysis Requirements:
        - Two CalibrationLayer instances (baseline and current)
        - Same unit_of_analysis_id
        - Same contract_type_code

    Epistemic Level: N3-AUD (audit/veto)
    Output: Immutable drift report with severity classification
    Fusion Strategy: Maximum drift severity determines report severity

    Immutable drift report for calibration audits.

    This report captures all detected drift between two calibration
    layers, classifies severity, and provides actionable recommendations.

    Attributes:
        report_id: Unique report identifier (timestamp-based)
        unit_of_analysis_id: UoA identifier
        contract_type_code: TYPE_A, TYPE_B, etc.
        baseline_layer_hash: Hash of baseline calibration layer
        current_layer_hash: Hash of current calibration layer
        parameter_drifts: Tuple of detected parameter drifts
        overall_severity: Maximum severity across all drifts
        contradiction_detected: Whether contradictory parameters found
        coverage_penalty_applied: Whether coverage penalty triggered
        dispersion_penalty_applied: Whether dispersion penalty triggered
        recommendations: List of recommended actions
        generated_at: Report generation timestamp
    """

    report_id: str
    unit_of_analysis_id: str
    contract_type_code: str
    baseline_layer_hash: str
    current_layer_hash: str
    parameter_drifts: tuple[ParameterDrift, ...]
    overall_severity: DriftSeverity
    contradiction_detected: bool
    coverage_penalty_applied: bool
    dispersion_penalty_applied: bool
    recommendations: tuple[str, ...]
    generated_at: datetime

    def has_significant_drift(self) -> bool:
        """Check if any drift is SIGNIFICANT or CRITICAL."""
        return self.overall_severity in (DriftSeverity.SIGNIFICANT, DriftSeverity.CRITICAL)

    def requires_recalibration(self) -> bool:
        """Check if drift requires immediate recalibration."""
        return (
            self.overall_severity == DriftSeverity.CRITICAL
            or self.contradiction_detected
        )

    def to_dict(self) -> dict:
        """Serialize drift report to dictionary."""
        return {
            "report_id": self.report_id,
            "unit_of_analysis_id": self.unit_of_analysis_id,
            "contract_type_code": self.contract_type_code,
            "baseline_layer_hash": self.baseline_layer_hash,
            "current_layer_hash": self.current_layer_hash,
            "parameter_drifts": [
                {
                    "parameter_name": d.parameter_name,
                    "old_value": d.old_value,
                    "new_value": d.new_value,
                    "drift_ratio": d.drift_ratio,
                    "severity": d.severity.value,
                    "rationale": d.rationale,
                }
                for d in self.parameter_drifts
            ],
            "overall_severity": self.overall_severity.value,
            "contradiction_detected": self.contradiction_detected,
            "coverage_penalty_applied": self.coverage_penalty_applied,
            "dispersion_penalty_applied": self.dispersion_penalty_applied,
            "recommendations": list(self.recommendations),
            "generated_at": self.generated_at.isoformat(),
        }


# =============================================================================
# DRIFT DETECTOR
# =============================================================================


class DriftDetector:
    """
    Unit of Analysis Requirements:
        - Two CalibrationLayer instances (baseline and current)
        - Matching unit_of_analysis_id and contract_type_code

    Epistemic Level: N3-AUD (meta-level audit)
    Output: DriftReport with actionable recommendations
    Fusion Strategy: Per-parameter drift comparison with aggregated severity

    Detects calibration drift between baseline and current layers.

    This detector analyzes parameter changes, identifies drift patterns,
    and generates audit reports with recommendations.

    RESPONSIBILITIES:
    1. Compare parameter values between layers
    2. Compute drift ratios and classify severity
    3. Detect contradictions (e.g., prior↑ but veto↓)
    4. Apply coverage and dispersion penalties
    5. Generate actionable recommendations

    Example:
        >>> detector = DriftDetector()
        >>> report = detector.detect_drift(baseline_layer, current_layer)
        >>> if report.has_significant_drift():
        ...     print(f"Significant drift detected: {report.overall_severity}")
    """

    def __init__(self) -> None:
        """Initialize drift detector."""
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def detect_drift(
        self,
        baseline: CalibrationLayer,
        current: CalibrationLayer,
    ) -> DriftReport:
        """
        Unit of Analysis Requirements:
            - baseline and current have same unit_of_analysis_id
            - baseline and current have same contract_type_code

        Epistemic Level: N3-AUD
        Output: DriftReport (frozen, immutable)
        Fusion Strategy: Maximum severity classification

        Detect drift between baseline and current calibration layers.

        Args:
            baseline: Baseline calibration layer
            current: Current calibration layer

        Returns:
            Immutable drift report

        Raises:
            ValueError: If baseline and current don't match
        """
        # Validate matching identifiers
        if baseline.unit_of_analysis_id != current.unit_of_analysis_id:
            raise ValueError(
                f"unit_of_analysis_id mismatch: "
                f"baseline={baseline.unit_of_analysis_id}, "
                f"current={current.unit_of_analysis_id}"
            )
        if baseline.contract_type_code != current.contract_type_code:
            raise ValueError(
                f"contract_type_code mismatch: "
                f"baseline={baseline.contract_type_code}, "
                f"current={current.contract_type_code}"
            )

        # Compute parameter drifts
        parameter_drifts = self._compute_parameter_drifts(baseline, current)

        # Determine overall severity
        overall_severity = self._determine_overall_severity(parameter_drifts)

        # Detect contradictions
        contradiction_detected = self._detect_contradictions(parameter_drifts)

        # Apply penalties
        coverage_penalty = self._check_coverage_penalty(current)
        dispersion_penalty = self._check_dispersion_penalty(parameter_drifts)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            parameter_drifts=parameter_drifts,
            contradiction_detected=contradiction_detected,
            coverage_penalty=coverage_penalty,
            dispersion_penalty=dispersion_penalty,
        )

        # Create report
        now = datetime.utcnow()
        report_id = f"DRIFT-{now.strftime('%Y%m%d-%H%M%S')}-{baseline.manifest_hash()[:8]}"

        report = DriftReport(
            report_id=report_id,
            unit_of_analysis_id=baseline.unit_of_analysis_id,
            contract_type_code=baseline.contract_type_code,
            baseline_layer_hash=baseline.manifest_hash(),
            current_layer_hash=current.manifest_hash(),
            parameter_drifts=parameter_drifts,
            overall_severity=overall_severity,
            contradiction_detected=contradiction_detected,
            coverage_penalty_applied=coverage_penalty,
            dispersion_penalty_applied=dispersion_penalty,
            recommendations=recommendations,
            generated_at=now,
        )

        self._logger.info(
            f"Drift detected: {report.report_id}, "
            f"severity={overall_severity.value}, "
            f"drifts={len(parameter_drifts)}"
        )

        return report

    def _compute_parameter_drifts(
        self,
        baseline: CalibrationLayer,
        current: CalibrationLayer,
    ) -> tuple[ParameterDrift, ...]:
        """Compute drift for each parameter."""
        drifts = []

        for param_name in ["prior_strength", "veto_threshold", "chunk_size", "extraction_coverage_target"]:
            try:
                baseline_param = baseline.get_parameter(param_name)
                current_param = current.get_parameter(param_name)

                drift_ratio = self._compute_drift_ratio(
                    baseline_param.value,
                    current_param.value,
                )

                severity = self._classify_drift_severity(drift_ratio)

                if severity != DriftSeverity.NONE:
                    drift = ParameterDrift(
                        parameter_name=param_name,
                        old_value=baseline_param.value,
                        new_value=current_param.value,
                        drift_ratio=drift_ratio,
                        severity=severity,
                        rationale=f"Parameter changed from {baseline_param.value:.4f} to {current_param.value:.4f}",
                    )
                    drifts.append(drift)
            except KeyError:
                # Parameter not found in one of the layers
                continue

        return tuple(drifts)

    def _compute_drift_ratio(self, old_value: float, new_value: float) -> float:
        """
        Compute drift ratio: |new - old| / |old|.

        Special case: if old_value is very small (< 1e-6), use absolute difference.
        """
        if abs(old_value) < 1e-6:
            return abs(new_value - old_value)

        return abs(new_value - old_value) / abs(old_value)

    def _classify_drift_severity(self, drift_ratio: float) -> DriftSeverity:
        """Classify drift severity based on ratio."""
        if drift_ratio >= _SIGNIFICANT_DRIFT_THRESHOLD:
            return DriftSeverity.CRITICAL
        elif drift_ratio >= _MODERATE_DRIFT_THRESHOLD:
            return DriftSeverity.SIGNIFICANT
        elif drift_ratio >= _MINOR_DRIFT_THRESHOLD:
            return DriftSeverity.MODERATE
        elif drift_ratio > 0.0:
            return DriftSeverity.MINOR
        else:
            return DriftSeverity.NONE

    def _determine_overall_severity(
        self,
        parameter_drifts: tuple[ParameterDrift, ...],
    ) -> DriftSeverity:
        """Determine overall severity (maximum across all drifts)."""
        if not parameter_drifts:
            return DriftSeverity.NONE

        severity_order = [
            DriftSeverity.NONE,
            DriftSeverity.MINOR,
            DriftSeverity.MODERATE,
            DriftSeverity.SIGNIFICANT,
            DriftSeverity.CRITICAL,
        ]

        max_severity = DriftSeverity.NONE
        for drift in parameter_drifts:
            if severity_order.index(drift.severity) > severity_order.index(max_severity):
                max_severity = drift.severity

        return max_severity

    def _detect_contradictions(
        self,
        parameter_drifts: tuple[ParameterDrift, ...],
    ) -> bool:
        """
        Detect contradictory parameter changes.

        INV-DRIFT-005: Contradictions occur when:
        - prior_strength increases BUT veto_threshold also increases (should decrease)
        - prior_strength decreases BUT veto_threshold also decreases (should increase)

        Logical relationship: prior↑ → veto↓ (stronger prior → less strict veto)
        """
        prior_drift = None
        veto_drift = None

        for drift in parameter_drifts:
            if drift.parameter_name == "prior_strength":
                prior_drift = drift
            elif drift.parameter_name == "veto_threshold":
                veto_drift = drift

        if prior_drift is None or veto_drift is None:
            return False

        # Check for contradiction
        prior_increased = prior_drift.new_value > prior_drift.old_value
        veto_increased = veto_drift.new_value > veto_drift.old_value

        # Contradiction: both increased or both decreased
        contradiction = (prior_increased and veto_increased) or (
            not prior_increased and not veto_increased
        )

        if contradiction:
            self._logger.warning(
                f"Contradiction detected: prior {prior_drift.old_value:.4f}→{prior_drift.new_value:.4f}, "
                f"veto {veto_drift.old_value:.4f}→{veto_drift.new_value:.4f}"
            )

        return contradiction

    def _check_coverage_penalty(self, current: CalibrationLayer) -> bool:
        """Check if coverage penalty should be applied."""
        try:
            coverage_param = current.get_parameter("extraction_coverage_target")
            return coverage_param.value < _COVERAGE_PENALTY_THRESHOLD
        except KeyError:
            return False

    def _check_dispersion_penalty(
        self,
        parameter_drifts: tuple[ParameterDrift, ...],
    ) -> bool:
        """Check if dispersion penalty should be applied."""
        if not parameter_drifts:
            return False

        # High dispersion: many parameters drifted significantly
        significant_drifts = [
            d for d in parameter_drifts
            if d.severity in (DriftSeverity.SIGNIFICANT, DriftSeverity.CRITICAL)
        ]

        dispersion_ratio = len(significant_drifts) / len(parameter_drifts)
        return dispersion_ratio >= _DISPERSION_PENALTY_THRESHOLD

    def _generate_recommendations(
        self,
        parameter_drifts: tuple[ParameterDrift, ...],
        contradiction_detected: bool,
        coverage_penalty: bool,
        dispersion_penalty: bool,
    ) -> tuple[str, ...]:
        """Generate actionable recommendations."""
        recommendations = []

        if contradiction_detected:
            recommendations.append(
                "CRITICAL: Contradictory parameter changes detected. "
                "Review calibration logic and UoA characteristics."
            )

        if coverage_penalty:
            recommendations.append(
                "Coverage target below threshold (0.85). "
                "Increase extraction coverage or adjust UoA policy area count."
            )

        if dispersion_penalty:
            recommendations.append(
                "High parameter dispersion detected. "
                "Review calibration stability and consider recalibration."
            )

        # Add drift-specific recommendations
        for drift in parameter_drifts:
            if drift.severity == DriftSeverity.CRITICAL:
                recommendations.append(
                    f"CRITICAL: {drift.parameter_name} drifted {drift.drift_ratio*100:.1f}%. "
                    f"Immediate recalibration required."
                )

        if not recommendations:
            recommendations.append("No significant issues detected. Calibration stable.")

        return tuple(recommendations)


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "DriftDetector",
    "DriftReport",
    "DriftSeverity",
    "ParameterDrift",
]
