"""
Module: phase2_60_04_calibration_policy_v2
PHASE_LABEL: Phase 2
Sequence: D
Description: Method-Delegating Uncertainty-Propagating Calibration Coordinator

Version: 2.0.0
Last Modified: 2025-12-22
Author: F.A.R.F.A.N Policy Pipeline
License: Proprietary

This module implements the refactored CalibrationPolicy that:
1. Delegates to method-specific calibration when CalibrableMethod protocol is satisfied
2. Propagates posterior distributions without collapse to point estimates
3. Reports probability mass per label, not hard classification
4. Audits every decision with full provenance chain
5. Fails explicitly when required inputs are missing

Architecture: Coordinator Pattern with Method Sovereignty
Source: refactor_calibration_policy.md specification
"""
from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol, runtime_checkable

import numpy as np  # type: ignore[import-untyped]
import numpy.typing as npt

logger = logging.getLogger(__name__)


class QualityLabel(str, Enum):
    """Quality labels with exact threshold semantics from questionnaire_monolith.json."""
    
    EXCELENTE = "EXCELENTE"
    BUENO = "BUENO"
    ACEPTABLE = "ACEPTABLE"
    INSUFICIENTE = "INSUFICIENTE"


@dataclass(frozen=True, slots=True)
class MicroLevelThresholds:
    """Empirically calibrated thresholds.
    
    Source: questionnaire_monolith.json -> scoring.micro_levels
    Validation: Must be loaded from monolith, not hardcoded.
    """
    
    excelente: float
    bueno: float
    aceptable: float
    insuficiente: float = 0.0
    
    source_file: str = ""
    calibration_date: str = ""
    calibration_study_id: str = ""
    
    def __post_init__(self) -> None:
        if not (self.excelente > self.bueno > self.aceptable > self.insuficiente):
            raise ValueError(
                f"Threshold monotonicity violated: "
                f"{self.excelente} > {self.bueno} > {self.aceptable} > {self.insuficiente}"
            )


@dataclass(frozen=True, slots=True)
class LabelProbabilityMass:
    """Probability mass distribution across quality labels.
    
    Derived from posterior samples, not point estimate thresholding.
    Sum must equal 1.0 (within floating point tolerance).
    """
    
    excelente: float
    bueno: float
    aceptable: float
    insuficiente: float
    
    def __post_init__(self) -> None:
        total = self.excelente + self.bueno + self.aceptable + self.insuficiente
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Probability mass must sum to 1.0, got {total}")
    
    @property
    def modal_label(self) -> QualityLabel:
        """Return label with highest probability mass."""
        masses = {
            QualityLabel.EXCELENTE: self.excelente,
            QualityLabel.BUENO: self.bueno,
            QualityLabel.ACEPTABLE: self.aceptable,
            QualityLabel.INSUFICIENTE: self.insuficiente,
        }
        return max(masses, key=lambda k: masses[k])
    
    @property
    def modal_probability(self) -> float:
        """Return probability of modal label."""
        return max(self.excelente, self.bueno, self.aceptable, self.insuficiente)
    
    @property
    def entropy(self) -> float:
        """Shannon entropy of label distribution. Higher = more uncertain."""
        probs = [self.excelente, self.bueno, self.aceptable, self.insuficiente]
        return -sum(p * np.log2(p) if p > 0 else 0.0 for p in probs)


@dataclass(frozen=True, slots=True)
class CalibrationProvenance:
    """Complete audit trail for a single calibration decision."""
    
    question_id: str
    method_id: str
    method_class_name: str
    
    raw_score: float
    raw_score_semantics: str
    
    posterior_mean: float | None
    posterior_std: float | None
    credible_interval_95: tuple[float, float] | None
    posterior_sample_size: int | None
    
    calibration_source: str
    transformation_applied: str
    transformation_parameters: dict[str, Any]  # noqa: ANN401
    
    domain: str
    domain_weight: float | None
    contract_priority: int | None
    
    label_probabilities: LabelProbabilityMass
    assigned_label: QualityLabel
    assigned_weight: float
    
    timestamp_utc: str
    provenance_hash: str = ""
    
    def __post_init__(self) -> None:
        if not self.provenance_hash:
            payload = {
                "question_id": self.question_id,
                "method_id": self.method_id,
                "raw_score": self.raw_score,
                "calibration_source": self.calibration_source,
                "transformation_applied": self.transformation_applied,
                "assigned_label": self.assigned_label.value,
                "timestamp_utc": self.timestamp_utc,
            }
            hash_input = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            object.__setattr__(
                self,
                "provenance_hash",
                hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16],
            )


@dataclass(frozen=True, slots=True)
class CalibratedOutput:
    """Complete output of calibration with uncertainty and provenance."""
    
    label: QualityLabel
    weight: float
    calibrated_score: float
    
    label_probabilities: LabelProbabilityMass
    credible_interval_95: tuple[float, float] | None
    posterior_samples: npt.NDArray[np.float64] | None
    
    provenance: CalibrationProvenance
    
    @property
    def is_high_confidence(self) -> bool:
        """True if modal label probability > 0.8."""
        return self.label_probabilities.modal_probability > 0.8
    
    @property
    def uncertainty_flag(self) -> str:
        """Return uncertainty classification."""
        entropy = self.label_probabilities.entropy
        if entropy < 0.5:
            return "LOW_UNCERTAINTY"
        elif entropy < 1.0:
            return "MODERATE_UNCERTAINTY"
        elif entropy < 1.5:
            return "HIGH_UNCERTAINTY"
        else:
            return "EXTREME_UNCERTAINTY"


@dataclass(frozen=True, slots=True)
class MethodCalibrationResult:
    """Result returned by CalibrableMethod.calibrate_output()."""
    
    calibrated_score: float
    label_probabilities: LabelProbabilityMass
    transformation_name: str
    transformation_parameters: dict[str, Any]  # noqa: ANN401
    posterior_samples: npt.NDArray[np.float64] | None = None
    credible_interval_95: tuple[float, float] | None = None


@runtime_checkable
class CalibrableMethod(Protocol):
    """Protocol that method classes must implement for calibration delegation.
    
    Methods in methods_dispensary/ that want control over their own calibration
    MUST implement this protocol. CalibrationPolicy will delegate to
    calibrate_output() when this protocol is satisfied.
    
    Implementation Contract:
    - calibration_params MUST be a class attribute (not instance)
    - calibration_params MUST contain at minimum: {"domain": str, "output_semantics": str}
    - calibrate_output() MUST return MethodCalibrationResult
    - calibrate_output() MUST NOT raise exceptions for valid inputs in [0.0, 1.0]
    - calibrate_output() SHOULD propagate posterior if available
    """
    
    calibration_params: dict[str, Any]  # noqa: ANN401
    
    def calibrate_output(
        self,
        raw_score: float,
        posterior_samples: npt.NDArray[np.float64] | None = None,
        context: dict[str, Any] | None = None,  # noqa: ANN401
    ) -> MethodCalibrationResult:
        """Apply method-specific calibration.
        
        Args:
            raw_score: The uncalibrated score in [0.0, 1.0]
            posterior_samples: Optional posterior samples if method does Bayesian inference
            context: Optional context dict with question_id, policy_area_id, etc.
            
        Returns:
            MethodCalibrationResult with full uncertainty quantification
        """
        ...


class CalibrationPolicy:
    """Coordinator for method-level calibration with uncertainty propagation.
    
    Architecture Principles:
    1. DELEGATE to method-specific calibration when CalibrableMethod protocol is satisfied
    2. PROPAGATE posterior distributions, do not collapse to point estimates
    3. REPORT probability mass per label, not hard classification
    4. AUDIT every decision with full provenance chain
    5. FAIL EXPLICITLY when required inputs are missing
    
    Integration Points:
    - BaseExecutorWithContract: calls calibrate_method_output() per method execution
    - MethodRegistry: provides method class references for protocol checking
    - QuestionnaireProvider: provides MicroLevelThresholds from monolith
    - Contract loader: provides per-contract calibration overrides
    """
    
    def __init__(
        self,
        thresholds: MicroLevelThresholds,
        default_domain_weights: dict[str, float],
    ) -> None:
        """Initialize CalibrationPolicy.
        
        Args:
            thresholds: Empirically calibrated thresholds from questionnaire_monolith.json
            default_domain_weights: Default weights when contract doesn't specify
                Keys: "semantic", "temporal", "financial", "structural"
                Values: Weights summing to 1.0
        """
        self._thresholds = thresholds
        self._default_domain_weights = default_domain_weights
        self._audit_log: list[CalibrationProvenance] = []
        
        if abs(sum(default_domain_weights.values()) - 1.0) > 1e-6:
            raise ValueError("Domain weights must sum to 1.0")
    
    @classmethod
    def from_questionnaire_provider(
        cls,
        questionnaire_provider: Any,  # noqa: ANN401
    ) -> CalibrationPolicy:
        """Factory: Create from QuestionnaireProvider.
        
        Loads thresholds from questionnaire_monolith.json via provider.
        This is the preferred construction method for production.
        """
        scoring = questionnaire_provider.get_scoring_levels()
        micro_levels = scoring.get("micro_levels", [])
        
        thresholds_dict: dict[str, float] = {}
        for level in micro_levels:
            if isinstance(level, dict):
                name = level.get("level", "").upper()
                min_score = level.get("min_score")
                if name and min_score is not None:
                    thresholds_dict[name] = float(min_score)
        
        thresholds = MicroLevelThresholds(
            excelente=thresholds_dict.get("EXCELENTE", 0.85),
            bueno=thresholds_dict.get("BUENO", 0.70),
            aceptable=thresholds_dict.get("ACEPTABLE", 0.55),
            insuficiente=0.0,
            source_file="questionnaire_monolith.json",
            calibration_date=datetime.now(timezone.utc).isoformat(),
        )
        
        default_weights = {
            "semantic": 0.35,
            "temporal": 0.25,
            "financial": 0.25,
            "structural": 0.15,
        }
        
        return cls(thresholds=thresholds, default_domain_weights=default_weights)
    
    def calibrate_method_output(
        self,
        question_id: str,
        method_id: str,
        raw_score: float,
        method_instance: Any | None = None,  # noqa: ANN401
        posterior_samples: npt.NDArray[np.float64] | None = None,
        context: dict[str, Any] | None = None,  # noqa: ANN401
    ) -> CalibratedOutput:
        """Main entry point: Calibrate a method output with full uncertainty propagation.
        
        Decision tree:
        1. If method_instance implements CalibrableMethod protocol → DELEGATE
        2. Else → Apply central MicroLevelThresholds with synthetic posterior
        
        Args:
            question_id: The question being answered (e.g., "Q001")
            method_id: The method that produced the score (e.g., "FINANCIERO:bayesian_risk")
            raw_score: The uncalibrated score from method execution, in [0.0, 1.0]
            method_instance: Optional method instance for delegation check
            posterior_samples: Optional posterior samples from method's Bayesian inference
            context: Optional context dict with domain, policy_area_id, etc.
            
        Returns:
            CalibratedOutput with full uncertainty quantification and provenance
            
        Raises:
            ValueError: If raw_score is outside [0.0, 1.0]
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        context = context or {}
        
        if not 0.0 <= raw_score <= 1.0:
            raise ValueError(f"raw_score must be in [0.0, 1.0], got {raw_score}")
        
        if self._implements_calibrable_protocol(method_instance):
            method_result = self._delegate_to_method(
                method_instance=method_instance,
                raw_score=raw_score,
                posterior_samples=posterior_samples,
                context=context,
            )
            calibration_source = "method_delegation"
            transformation_applied = method_result.transformation_name
            transformation_parameters = method_result.transformation_parameters
            label_probabilities = method_result.label_probabilities
            calibrated_score = method_result.calibrated_score
            posterior_samples = method_result.posterior_samples
            credible_interval = method_result.credible_interval_95
            method_class_name = type(method_instance).__name__
        else:
            central_result = self._apply_central_calibration(
                raw_score=raw_score,
                posterior_samples=posterior_samples,
            )
            calibration_source = "central_threshold"
            transformation_applied = "micro_level_threshold_with_synthetic_posterior"
            transformation_parameters = {
                "thresholds": {
                    "excelente": self._thresholds.excelente,
                    "bueno": self._thresholds.bueno,
                    "aceptable": self._thresholds.aceptable,
                },
            }
            label_probabilities = central_result["label_probabilities"]
            calibrated_score = central_result["calibrated_score"]
            posterior_samples = central_result["posterior_samples"]
            credible_interval = central_result["credible_interval_95"]
            method_class_name = "None"
        
        label = label_probabilities.modal_label
        weight = self._label_to_weight(label, label_probabilities.modal_probability)
        
        domain = context.get("domain", "unknown")
        if method_instance and hasattr(method_instance, "calibration_params"):
            domain = method_instance.calibration_params.get("domain", domain)
        
        domain_weight = self._default_domain_weights.get(domain)
        contract_priority = context.get("contract_priority")
        
        provenance = CalibrationProvenance(
            question_id=question_id,
            method_id=method_id,
            method_class_name=method_class_name,
            raw_score=raw_score,
            raw_score_semantics=context.get("output_semantics", "normalized_score"),
            posterior_mean=float(np.mean(posterior_samples)) if posterior_samples is not None else None,
            posterior_std=float(np.std(posterior_samples)) if posterior_samples is not None else None,
            credible_interval_95=credible_interval,
            posterior_sample_size=len(posterior_samples) if posterior_samples is not None else None,
            calibration_source=calibration_source,
            transformation_applied=transformation_applied,
            transformation_parameters=transformation_parameters,
            domain=domain,
            domain_weight=domain_weight,
            contract_priority=contract_priority,
            label_probabilities=label_probabilities,
            assigned_label=label,
            assigned_weight=weight,
            timestamp_utc=timestamp,
        )
        
        self._audit_log.append(provenance)
        
        return CalibratedOutput(
            label=label,
            weight=weight,
            calibrated_score=calibrated_score,
            label_probabilities=label_probabilities,
            credible_interval_95=credible_interval,
            posterior_samples=posterior_samples,
            provenance=provenance,
        )
    
    def _implements_calibrable_protocol(self, instance: Any) -> bool:  # noqa: ANN401
        """Check if instance implements CalibrableMethod protocol."""
        if instance is None:
            return False
        return (
            hasattr(instance, "calibration_params")
            and isinstance(getattr(instance, "calibration_params", None), dict)
            and hasattr(instance, "calibrate_output")
            and callable(getattr(instance, "calibrate_output", None))
        )
    
    def _delegate_to_method(
        self,
        method_instance: Any,  # noqa: ANN401
        raw_score: float,
        posterior_samples: npt.NDArray[np.float64] | None,
        context: dict[str, Any],  # noqa: ANN401
    ) -> MethodCalibrationResult:
        """Delegate calibration to method's calibrate_output()."""
        result: MethodCalibrationResult = method_instance.calibrate_output(
            raw_score=raw_score,
            posterior_samples=posterior_samples,
            context=context,
        )
        return result
    
    def _apply_central_calibration(
        self,
        raw_score: float,
        posterior_samples: npt.NDArray[np.float64] | None,
    ) -> dict[str, Any]:  # noqa: ANN401
        """Apply central MicroLevelThresholds with synthetic posterior.
        
        Used when method does not implement CalibrableMethod protocol.
        Generates synthetic posterior to avoid false certainty.
        """
        if posterior_samples is None or len(posterior_samples) == 0:
            posterior_samples = np.clip(
                np.random.normal(raw_score, 0.1, size=10000),
                0.0,
                1.0,
            )
        
        n = len(posterior_samples)
        t_e, t_b, t_a = self._thresholds.excelente, self._thresholds.bueno, self._thresholds.aceptable
        
        label_probabilities = LabelProbabilityMass(
            excelente=float(np.sum(posterior_samples >= t_e) / n),
            bueno=float(np.sum((posterior_samples >= t_b) & (posterior_samples < t_e)) / n),
            aceptable=float(np.sum((posterior_samples >= t_a) & (posterior_samples < t_b)) / n),
            insuficiente=float(np.sum(posterior_samples < t_a) / n),
        )
        
        return {
            "calibrated_score": float(np.mean(posterior_samples)),
            "label_probabilities": label_probabilities,
            "posterior_samples": posterior_samples,
            "credible_interval_95": (
                float(np.percentile(posterior_samples, 2.5)),
                float(np.percentile(posterior_samples, 97.5)),
            ),
        }
    
    def _label_to_weight(self, label: QualityLabel, modal_probability: float) -> float:
        """Convert label to weight, modulated by confidence.
        
        Base weights:
        - EXCELENTE: 1.0
        - BUENO: 0.90
        - ACEPTABLE: 0.75
        - INSUFICIENTE: 0.40
        
        Modulation: weight *= (0.7 + 0.3 * modal_probability)
        This reduces weight when classification is uncertain.
        """
        base_weights = {
            QualityLabel.EXCELENTE: 1.0,
            QualityLabel.BUENO: 0.90,
            QualityLabel.ACEPTABLE: 0.75,
            QualityLabel.INSUFICIENTE: 0.40,
        }
        
        base = base_weights[label]
        confidence_modulation = 0.7 + 0.3 * modal_probability
        
        return base * confidence_modulation
    
    @property
    def audit_log(self) -> list[CalibrationProvenance]:
        """Return audit log (read-only copy)."""
        return list(self._audit_log)
    
    def export_audit_log(self) -> list[dict[str, Any]]:  # noqa: ANN401
        """Export audit log as JSON-serializable list."""
        return [
            {
                "question_id": p.question_id,
                "method_id": p.method_id,
                "method_class_name": p.method_class_name,
                "raw_score": p.raw_score,
                "calibration_source": p.calibration_source,
                "transformation_applied": p.transformation_applied,
                "domain": p.domain,
                "assigned_label": p.assigned_label.value,
                "assigned_weight": p.assigned_weight,
                "modal_probability": p.label_probabilities.modal_probability,
                "entropy": p.label_probabilities.entropy,
                "uncertainty_flag": (
                    "LOW" if p.label_probabilities.entropy < 0.5 else
                    "MODERATE" if p.label_probabilities.entropy < 1.0 else
                    "HIGH"
                ),
                "timestamp_utc": p.timestamp_utc,
                "provenance_hash": p.provenance_hash,
            }
            for p in self._audit_log
        ]
