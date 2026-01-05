"""
Calibration Auditor
===================
N3-AUD level auditor for calibration choices. 

DESIGN PATTERN: Specification Pattern
- Each invariant is a specification that can be composed
- Auditor evaluates manifest against specifications

VETO CAPABILITY:
- This is an N3-AUD component with VETO GATE behavior
- Can invalidate calibration if invariants violated
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Final, Protocol, Sequence, cast

from .calibration_manifest import CalibrationManifest, DriftIndicator, DriftReport
from .type_defaults import (
    PROHIBITED_OPERATIONS,
    get_type_defaults,
    PRIOR_STRENGTH_MIN,
    PRIOR_STRENGTH_MAX,
)

logger = logging.getLogger(__name__)


class CalibrationSpecification(Protocol):
    """Protocol for calibration specifications."""
    
    def is_satisfied_by(self, manifest: CalibrationManifest) -> bool:
        """Check if manifest satisfies this specification."""
        ... 
    
    def get_violation_message(self) -> str:
        """Get message describing violation."""
        ...


@dataclass(frozen=True)
class CalibrationViolation:
    """Record of calibration invariant violation."""
    invariant_id: str
    severity: str  # "WARNING" or "FATAL"
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass
class AuditResult:
    """Result of calibration audit."""
    passed: bool
    violations: list[CalibrationViolation]
    veto_triggered: bool
    auditor_id: str
    timestamp: datetime
    manifest_hash: str


class PriorStrengthSpecification:
    """INV-CAL-001: Prior strength must be in valid range."""
    
    _VALID_RANGE:  Final[tuple[float, float]] = (PRIOR_STRENGTH_MIN, PRIOR_STRENGTH_MAX)
    _violation_message: str = ""
    
    def is_satisfied_by(self, manifest: CalibrationManifest) -> bool:
        ing_prior = manifest.ingestion_layer.get_parameter("prior_strength").value
        ph2_prior = manifest.phase2_layer.get_parameter("prior_strength").value
        
        ing_valid = self._VALID_RANGE[0] <= ing_prior <= self._VALID_RANGE[1]
        ph2_valid = self._VALID_RANGE[0] <= ph2_prior <= self._VALID_RANGE[1]
        
        if not ing_valid: 
            self._violation_message = (
                f"Ingestion prior strength {ing_prior} outside "
                f"[{self._VALID_RANGE[0]}, {self._VALID_RANGE[1]}]"
            )
        elif not ph2_valid:
            self._violation_message = (
                f"Phase-2 prior strength {ph2_prior} outside "
                f"[{self._VALID_RANGE[0]}, {self._VALID_RANGE[1]}]"
            )
        
        return ing_valid and ph2_valid
    
    def get_violation_message(self) -> str:
        return self._violation_message


class VetoThresholdSpecification:
    """INV-CAL-002: Veto threshold must match TYPE specification."""
    
    _violation_message: str = ""
    
    def is_satisfied_by(self, manifest: CalibrationManifest) -> bool:
        contract_type = manifest.contract_type_code
        try:
            type_defaults = get_type_defaults(contract_type)
        except Exception:
            # Fallback if validation fails or type unknown
            self._violation_message = f"Unknown contract type: {contract_type}"
            return False
        
        expected_bounds = type_defaults.veto_threshold
        actual_value = manifest.phase2_layer.get_parameter("veto_threshold").value
        
        is_valid = expected_bounds.lower <= actual_value <= expected_bounds.upper
        
        if not is_valid: 
            self._violation_message = (
                f"Veto threshold {actual_value} outside TYPE {contract_type} bounds "
                f"[{expected_bounds.lower}, {expected_bounds.upper}]"
            )
        
        return is_valid
    
    def get_violation_message(self) -> str:
        return self._violation_message


class FusionStrategySpecification:
    """INV-CAL-003: Fusion strategy must not use prohibited operations."""
    
    _violation_message: str = ""
    
    def is_satisfied_by(self, manifest: CalibrationManifest) -> bool:
        contract_type = manifest.contract_type_code
        try:
            defaults = get_type_defaults(contract_type)
            prohibited = defaults.prohibited_operations
        except Exception:
            # Fallback if defaults unavailable (should not happen if validated earlier)
            from .type_defaults import PROHIBITED_OPERATIONS
            prohibited = PROHIBITED_OPERATIONS.get(contract_type, frozenset())
        
        # Check all decisions for prohibited operations
        for decision in manifest.decisions:
            if any(p in decision.parameter_name.lower() for p in prohibited):
                self._violation_message = (
                    f"Decision '{decision.decision_id}' uses prohibited operation "
                    f"for TYPE {contract_type}"
                )
                return False
        
        return True
    
    def get_violation_message(self) -> str:
        return self._violation_message


class CalibrationAuditor:
    """
    N3-AUD auditor for calibration manifests.
    
    VETO GATE: Can invalidate entire calibration on FATAL violations. 
    """
    
    _AUDITOR_ID: Final[str] = "CalibrationAuditor_N3_AUD_v1.0"
    
    def __init__(self) -> None:
        self._specifications: list[tuple[str, str, CalibrationSpecification]] = [
            ("INV-CAL-001", "FATAL", PriorStrengthSpecification()),
            ("INV-CAL-002", "FATAL", VetoThresholdSpecification()),
            ("INV-CAL-003", "FATAL", FusionStrategySpecification()),
        ]
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def audit(self, manifest: CalibrationManifest) -> AuditResult:
        """
        Audit calibration manifest against all specifications.
        
        Returns:
            AuditResult with pass/fail status and violations
        """
        self._logger.info(f"Auditing manifest {manifest.manifest_id}")
        
        violations:  list[CalibrationViolation] = []
        veto_triggered = False
        
        for invariant_id, severity, spec in self._specifications:
            if not spec.is_satisfied_by(manifest):
                violation = CalibrationViolation(
                    invariant_id=invariant_id,
                    severity=severity,
                    message=spec.get_violation_message(),
                    details={"manifest_id": manifest.manifest_id},
                )
                violations.append(violation)
                if severity == "FATAL":
                    veto_triggered = True
                    self._logger.error(
                        f"FATAL violation: {invariant_id}: {spec.get_violation_message()}"
                    )
            else:
                self._logger.info(f"Invariant {invariant_id} satisfied.")
        
        passed = not veto_triggered
        
        return AuditResult(
            passed=passed,
            violations=violations,
            veto_triggered=veto_triggered,
            auditor_id=self._AUDITOR_ID,
            timestamp=datetime.now(timezone.utc),
            manifest_hash=manifest.compute_hash(),
        )

    def audit_drift(
        self,
        manifest: CalibrationManifest,
        runtime_observations: Sequence[dict[str, object]],
        expected_coverage: float,
        expected_credible_width: float | None,
    ) -> DriftReport:
        """
        Detects calibration drift between design and runtime.
        """
        drift_indicators: list[DriftIndicator] = []
        
        # Coverage drift
        actual_coverage = sum(1 for obs in runtime_observations if cast(bool, obs.get("covered"))) / max(1, len(runtime_observations))
        deviation = abs(actual_coverage - expected_coverage)
        # Thresholds justified by Audit Policy v2.1 (docs/audit/SPEC_SIGNAL_NORMALIZATION.md):
        # > 0.1 (10%): Warning level drift, requires manual review.
        # > 0.2 (20%): Fatal drift, indicates structural change in data or extraction failure.
        severity = "FATAL" if deviation > 0.2 else "WARNING" if deviation > 0.1 else "INFO"
        if severity != "INFO":
            drift_indicators.append(
                DriftIndicator(
                    parameter="extraction_coverage",
                    expected_value=expected_coverage,
                    actual_value=actual_coverage,
                    deviation=deviation,
                    severity=severity,
                    detection_timestamp=datetime.now(timezone.utc),
                )
            )
        
        # Credible interval drift (Bayesian only)
        if expected_credible_width is not None:
            actual_width = sum(cast(float, obs.get("credible_interval_width", 0)) for obs in runtime_observations if "credible_interval_width" in obs) / max(1, len(runtime_observations))
            deviation = abs(actual_width - expected_credible_width)
            # Thresholds:
            # > 0.15: Warning (statistically significant shift)
            # > 0.30: Fatal (model uncertainty mismatch, potential prior miscalibration)
            severity = "FATAL" if deviation > 0.3 else "WARNING" if deviation > 0.15 else "INFO"
            if severity != "INFO":
                drift_indicators.append(
                    DriftIndicator(
                        parameter="credible_interval_width",
                        expected_value=expected_credible_width,
                        actual_value=actual_width,
                        deviation=deviation,
                        severity=severity,
                        detection_timestamp=datetime.now(timezone.utc),
                    )
                )
        
        drift_detected = bool(drift_indicators)
        return DriftReport(indicators=drift_indicators, drift_detected=drift_detected)
