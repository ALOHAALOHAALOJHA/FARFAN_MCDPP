Refactor CalibrationPolicy to Method-Delegating, Uncertainty-Propagating, Empirically-Grounded Calibration Coordinator


## Executive Diagnosis

The current `phase2_calibration.py` implements a **threshold ladder classifier** that: 

1. **Ignores method-specific calibration infrastructure** already present in `financiero_viabilidad_tablas.py`, `policy_processor.py`, `analyzer_one. py`
2. **Destroys uncertainty information** by collapsing posterior distributions to point estimates before classification
3. **Uses unvalidated thresholds** (0.85/0.70/0.55/0.00) with no empirical calibration study
4. **Conflates semantic domains** by applying causal-edge priors (PROBABILITY_PRIORS) as quality-classification thresholds
5. **Produces non-auditable outputs** with no provenance chain from method output to final label


SPECIFIC ORDERS TO FULLY BE EXECUTED BY COPILOT:

**MAIN:** COPILOT MUST REFACTOR THE FILE AND WILL MAKE EXPLICIT EMPIRICAL PROOF FOR EACH ONE OF THE FOLLOWING CONDITIONS:

|-----------|---------------------|
| Method delegation works when `CalibrableMethod` protocol satisfied | Unit test:  mock method with protocol, verify `calibration_source == "method_delegation"` |
| Posterior propagation preserves samples | Unit test: pass 10000 samples in, verify output has 10000 samples |
| Label probabilities sum to 1.0 | Property assertion in `LabelProbabilityMass.__post_init__` |
| Uncertainty modulates weight | Unit test: entropy > 1.0 → weight < base_weight |
| Provenance hash is deterministic | Unit test:  same inputs → same hash |
| Audit log captures all calibrations | Integration test: 10 calibrations → 10 audit entries |
| Central path generates synthetic posterior | Unit test: None samples in → 10000 samples out |
| Thresholds loaded from monolith | Integration test: mock provider, verify threshold values |

**COLLATERAL** BUT SENSITIVE AND MANDATORY:

REFACTOR THIS FILES IN THE TERMS DESCRIBED, IN ANY CASE, COPILOT IS EXPECTED TO ADD VALUE BY FINDING OTHER ELEMENTS IN CODE THAT SHOULD BE CHANGE TO GAIN ALLIGNMEMT 
WITH THE ETHOS OF CALIBRATION EMBEDDED IN THE EXPECTD VERSION OF CALIBRATION POLICY:
|------|---------|
| `src/farfan_pipeline/methods/financiero_viabilidad_tablas.py` | Add `calibration_params` and `calibrate_output()` |
| `src/farfan_pipeline/methods/policy_processor.py` | Add `calibration_params` and `calibrate_output()` |
| `src/farfan_pipeline/methods/analyzer_one.py` | Add `calibration_params` and `calibrate_output()` |
| `tests/test_calibration_policy.py` | New test file with comprehensive coverage |


---

## Technical Specification

### 1. Architecture:  Coordinator Pattern with Method Sovereignty

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CalibrationPolicy                                │
│                    (Coordinator, NOT Dictator)                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ Method A         │    │ Method B         │    │ Method C         │  │
│  │ (has calibration │    │ (has calibration │    │ (no calibration  │  │
│  │  infrastructure) │    │  infrastructure) │    │  infrastructure) │  │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘  │
│           │                       │                       │             │
│           ▼                       ▼                       ▼             │
│  ┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐  │
│  │ DELEGATE to      │    │ DELEGATE to      │    │ APPLY central    │  │
│  │ method. apply_    │    │ method.apply_    │    │ MicroLevel       │  │
│  │ calibration()    │    │ calibration()    │    │ thresholds       │  │
│  └────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘  │
│           │                       │                       │             │
│           └───────────────────────┴───────────────────────┘             │
│                                   │                                      │
│                                   ▼                                      │
│                    ┌──────────────────────────┐                         │
│                    │ CalibratedOutput         │                         │
│                    │ - posterior_distribution │                         │
│                    │ - label_probabilities    │                         │
│                    │ - provenance_chain       │                         │
│                    └──────────────────────────┘                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2. Data Structures

```python
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Protocol, runtime_checkable

import numpy as np


class QualityLabel(str, Enum):
    """Quality labels with exact threshold semantics from questionnaire_monolith. json."""
    EXCELENTE = "EXCELENTE"      # score >= 0.85
    BUENO = "BUENO"              # 0.70 <= score < 0.85
    ACEPTABLE = "ACEPTABLE"      # 0.55 <= score < 0.70
    INSUFICIENTE = "INSUFICIENTE"  # score < 0.55


@dataclass(frozen=True, slots=True)
class MicroLevelThresholds:
    """Empirically calibrated thresholds. 
    
    Source: questionnaire_monolith.json -> scoring. micro_levels
    Validation: Must be loaded from monolith, not hardcoded. 
    """
    excelente: float
    bueno: float
    aceptable: float
    insuficiente: float = 0.0
    
    # Provenance
    source_file: str = ""
    calibration_date: str = ""
    calibration_study_id: str = ""
    
    def __post_init__(self) -> None:
        if not (self.excelente > self.bueno > self.aceptable > self.insuficiente):
            raise ValueError(
                f"Threshold monotonicity violated: "
                f"{self.excelente} > {self. bueno} > {self.aceptable} > {self. insuficiente}"
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
        total = self.excelente + self.bueno + self.aceptable + self. insuficiente
        if abs(total - 1.0) > 1e-6:
            raise ValueError(f"Probability mass must sum to 1.0, got {total}")
    
    @property
    def modal_label(self) -> QualityLabel:
        """Return label with highest probability mass."""
        masses = {
            QualityLabel.EXCELENTE: self.excelente,
            QualityLabel. BUENO: self.bueno,
            QualityLabel.ACEPTABLE: self.aceptable,
            QualityLabel. INSUFICIENTE:  self.insuficiente,
        }
        return max(masses, key=masses.get)
    
    @property
    def modal_probability(self) -> float:
        """Return probability of modal label."""
        return max(self.excelente, self.bueno, self.aceptable, self. insuficiente)
    
    @property
    def entropy(self) -> float:
        """Shannon entropy of label distribution.  Higher = more uncertain."""
        probs = [self. excelente, self.bueno, self.aceptable, self.insuficiente]
        return -sum(p * np. log2(p) if p > 0 else 0.0 for p in probs)


@dataclass(frozen=True, slots=True)
class CalibrationProvenance:
    """Complete audit trail for a single calibration decision."""
    
    # Input identification
    question_id: str
    method_id: str
    method_class_name: str
    
    # Raw input
    raw_score: float
    raw_score_semantics: str  # "probability", "normalized_score", "count", "logit"
    
    # Posterior (if available)
    posterior_mean: float | None
    posterior_std:  float | None
    credible_interval_95: tuple[float, float] | None
    posterior_sample_size: int | None
    
    # Calibration pathway
    calibration_source: str  # "method_delegation" or "central_threshold"
    transformation_applied: str  # "logit_beach", "isotonic", "identity", etc.
    transformation_parameters: dict[str, Any]
    
    # Domain context
    domain:  str  # "semantic", "temporal", "financial", "structural", "causal"
    domain_weight: float | None
    contract_priority: int | None
    
    # Output
    label_probabilities: LabelProbabilityMass
    assigned_label: QualityLabel
    assigned_weight: float
    
    # Audit metadata
    timestamp_utc: str
    provenance_hash: str = ""
    
    def __post_init__(self) -> None:
        if not self.provenance_hash:
            # Compute deterministic hash of all fields except hash itself
            payload = {
                "question_id": self.question_id,
                "method_id":  self.method_id,
                "raw_score": self. raw_score,
                "calibration_source": self.calibration_source,
                "transformation_applied": self. transformation_applied,
                "assigned_label": self. assigned_label. value,
                "timestamp_utc": self.timestamp_utc,
            }
            import json
            hash_input = json.dumps(payload, sort_keys=True, ensure_ascii=False)
            object.__setattr__(
                self, 
                "provenance_hash", 
                hashlib.sha256(hash_input.encode("utf-8")).hexdigest()[:16]
            )


@dataclass(frozen=True, slots=True)
class CalibratedOutput: 
    """Complete output of calibration with uncertainty and provenance."""
    
    # Point estimates (for backward compatibility)
    label:  QualityLabel
    weight: float
    calibrated_score: float
    
    # Uncertainty quantification
    label_probabilities: LabelProbabilityMass
    credible_interval_95: tuple[float, float] | None
    posterior_samples: np.ndarray | None
    
    # Provenance
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
```

### 3. Method Protocol for Delegation

```python
@runtime_checkable
class CalibrableMethod(Protocol):
    """Protocol that method classes must implement for calibration delegation. 
    
    Methods in methods_dispensary/ that want control over their own calibration
    MUST implement this protocol.  CalibrationPolicy will delegate to 
    calibrate_output() when this protocol is satisfied.
    
    Implementation Contract:
    - calibration_params MUST be a class attribute (not instance)
    - calibration_params MUST contain at minimum:  {"domain":  str, "output_semantics": str}
    - calibrate_output() MUST return MethodCalibrationResult
    - calibrate_output() MUST NOT raise exceptions for valid inputs in [0. 0, 1.0]
    - calibrate_output() SHOULD propagate posterior if available
    """
    
    calibration_params: dict[str, Any]
    
    def calibrate_output(
        self,
        raw_score: float,
        posterior_samples: np. ndarray | None = None,
        context: dict[str, Any] | None = None,
    ) -> "MethodCalibrationResult":
        """Apply method-specific calibration. 
        
        Args:
            raw_score: The uncalibrated score in [0.0, 1.0]
            posterior_samples: Optional posterior samples if method does Bayesian inference
            context: Optional context dict with question_id, policy_area_id, etc. 
            
        Returns: 
            MethodCalibrationResult with full uncertainty quantification
        """
        ... 


@dataclass(frozen=True, slots=True)
class MethodCalibrationResult:
    """Result returned by CalibrableMethod. calibrate_output()."""
    
    calibrated_score: float
    label_probabilities: LabelProbabilityMass
    transformation_name: str
    transformation_parameters: dict[str, Any]
    posterior_samples: np. ndarray | None = None
    credible_interval_95: tuple[float, float] | None = None
```

### 4. Example Method Implementation:  FinancieroViabilidadTablas

```python
class PDETMunicipalPlanAnalyzer:
    """Example implementation of CalibrableMethod protocol. 
    
    This is how financiero_viabilidad_tablas.py should implement calibration.
    """
    
    calibration_params:  dict[str, Any] = {
        "domain": "financial",
        "output_semantics": "bayesian_posterior",
        "prior_alpha": 2.0,
        "prior_beta": 5.0,
        "logit_transform": False,
        "thresholds_source": "questionnaire_monolith.json",
    }
    
    def calibrate_output(
        self,
        raw_score: float,
        posterior_samples: np.ndarray | None = None,
        context: dict[str, Any] | None = None,
    ) -> MethodCalibrationResult:
        """Financial domain calibration with Bayesian posterior propagation.
        
        This method already does PyMC sampling in _bayesian_risk_inference().
        We propagate those samples through calibration instead of discarding them.
        """
        
        # If we have posterior samples, compute label probabilities directly
        if posterior_samples is not None and len(posterior_samples) > 0:
            label_probs = self._compute_label_probabilities_from_posterior(
                posterior_samples
            )
            calibrated_score = float(np.mean(posterior_samples))
            ci_95 = (
                float(np.percentile(posterior_samples, 2.5)),
                float(np.percentile(posterior_samples, 97.5)),
            )
        else:
            # Fallback:  construct synthetic posterior from point estimate
            # using prior parameters
            alpha = self.calibration_params["prior_alpha"]
            beta = self.calibration_params["prior_beta"]
            
            # Beta posterior update with pseudo-observation
            alpha_post = alpha + raw_score * 10  # pseudo-count = 10
            beta_post = beta + (1 - raw_score) * 10
            
            posterior_samples = np.random.beta(alpha_post, beta_post, size=10000)
            label_probs = self._compute_label_probabilities_from_posterior(
                posterior_samples
            )
            calibrated_score = alpha_post / (alpha_post + beta_post)
            ci_95 = (
                float(np.percentile(posterior_samples, 2.5)),
                float(np.percentile(posterior_samples, 97.5)),
            )
        
        return MethodCalibrationResult(
            calibrated_score=calibrated_score,
            label_probabilities=label_probs,
            transformation_name="beta_posterior_propagation",
            transformation_parameters={
                "prior_alpha": self.calibration_params["prior_alpha"],
                "prior_beta": self.calibration_params["prior_beta"],
                "sample_size": len(posterior_samples),
            },
            posterior_samples=posterior_samples,
            credible_interval_95=ci_95,
        )
    
    def _compute_label_probabilities_from_posterior(
        self,
        samples: np.ndarray,
    ) -> LabelProbabilityMass: 
        """Compute probability mass in each quality band from posterior samples."""
        
        n = len(samples)
        
        # Thresholds from questionnaire_monolith.json (loaded, not hardcoded)
        # For this example, using canonical values
        t_excelente = 0.85
        t_bueno = 0.70
        t_aceptable = 0.55
        
        p_excelente = np.sum(samples >= t_excelente) / n
        p_bueno = np. sum((samples >= t_bueno) & (samples < t_excelente)) / n
        p_aceptable = np.sum((samples >= t_aceptable) & (samples < t_bueno)) / n
        p_insuficiente = np. sum(samples < t_aceptable) / n
        
        return LabelProbabilityMass(
            excelente=float(p_excelente),
            bueno=float(p_bueno),
            aceptable=float(p_aceptable),
            insuficiente=float(p_insuficiente),
        )
```

### 5. Example Method Implementation: PolicyProcessor (Semantic Domain)

```python
class IndustrialPolicyProcessor:
    """Semantic domain calibration for pattern-based evidence scoring. 
    
    This method uses BayesianEvidenceScorer with entropy-weighted confidence.
    Calibration should respect the entropy component, not discard it.
    """
    
    calibration_params:  dict[str, Any] = {
        "domain": "semantic",
        "output_semantics": "entropy_weighted_confidence",
        "entropy_weight": 0.3,
        "prior_confidence": 0.5,
        "tf_idf_normalized": True,
    }
    
    def calibrate_output(
        self,
        raw_score: float,
        posterior_samples: np.ndarray | None = None,
        context: dict[str, Any] | None = None,
    ) -> MethodCalibrationResult: 
        """Semantic domain calibration with entropy-aware uncertainty.
        
        The raw_score from BayesianEvidenceScorer already incorporates: 
        - TF-IDF term frequency normalization
        - Shannon entropy diversity penalty  
        - Bayesian posterior update
        
        We propagate uncertainty by modeling residual entropy.
        """
        
        entropy_weight = self.calibration_params["entropy_weight"]
        
        # Extract entropy from context if available
        match_entropy = 0.5  # default
        if context and "match_entropy" in context:
            match_entropy = context["match_entropy"]
        
        # Uncertainty is proportional to entropy
        # High entropy = high diversity in matches = uncertain classification
        uncertainty_std = 0.1 + (match_entropy * 0.2)
        
        # Generate synthetic posterior incorporating entropy-based uncertainty
        posterior_samples = np.clip(
            np. random.normal(raw_score, uncertainty_std, size=10000),
            0.0,
            1.0,
        )
        
        label_probs = self._compute_label_probabilities_from_posterior(
            posterior_samples
        )
        
        return MethodCalibrationResult(
            calibrated_score=raw_score,  # Already calibrated by BayesianEvidenceScorer
            label_probabilities=label_probs,
            transformation_name="entropy_aware_gaussian",
            transformation_parameters={
                "entropy_weight": entropy_weight,
                "match_entropy": match_entropy,
                "uncertainty_std":  uncertainty_std,
            },
            posterior_samples=posterior_samples,
            credible_interval_95=(
                float(np.percentile(posterior_samples, 2.5)),
                float(np.percentile(posterior_samples, 97.5)),
            ),
        )
    
    def _compute_label_probabilities_from_posterior(
        self,
        samples: np.ndarray,
    ) -> LabelProbabilityMass: 
        """Identical to financial domain implementation."""
        n = len(samples)
        t_excelente, t_bueno, t_aceptable = 0.85, 0.70, 0.55
        
        return LabelProbabilityMass(
            excelente=float(np.sum(samples >= t_excelente) / n),
            bueno=float(np.sum((samples >= t_bueno) & (samples < t_excelente)) / n),
            aceptable=float(np.sum((samples >= t_aceptable) & (samples < t_bueno)) / n),
            insuficiente=float(np.sum(samples < t_aceptable) / n),
        )
```

### 6. CalibrationPolicy:  The Coordinator

```python
class CalibrationPolicy: 
    """Coordinator for method-level calibration with uncertainty propagation. 
    
    Architecture Principles:
    1.  DELEGATE to method-specific calibration when CalibrableMethod protocol is satisfied
    2.  PROPAGATE posterior distributions, do not collapse to point estimates
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
            default_domain_weights:  Default weights when contract doesn't specify
                Keys:  "semantic", "temporal", "financial", "structural"
                Values:  Weights summing to 1.0
        """
        self._thresholds = thresholds
        self._default_domain_weights = default_domain_weights
        self._audit_log: list[CalibrationProvenance] = []
        
        # Validate domain weights
        if abs(sum(default_domain_weights.values()) - 1.0) > 1e-6:
            raise ValueError("Domain weights must sum to 1.0")
    
    @classmethod
    def from_questionnaire_provider(
        cls,
        questionnaire_provider: Any,
    ) -> "CalibrationPolicy": 
        """Factory:  Create from QuestionnaireProvider. 
        
        Loads thresholds from questionnaire_monolith.json via provider.
        This is the preferred construction method for production. 
        """
        scoring = questionnaire_provider. get_scoring_levels()
        micro_levels = scoring.get("micro_levels", [])
        
        thresholds_dict:  dict[str, float] = {}
        for level in micro_levels:
            if isinstance(level, dict):
                name = level.get("level", "").upper()
                min_score = level.get("min_score")
                if name and min_score is not None:
                    thresholds_dict[name] = float(min_score)
        
        thresholds = MicroLevelThresholds(
            excelente=thresholds_dict. get("EXCELENTE", 0.85),
            bueno=thresholds_dict.get("BUENO", 0.70),
            aceptable=thresholds_dict. get("ACEPTABLE", 0.55),
            insuficiente=0.0,
            source_file="questionnaire_monolith. json",
            calibration_date=datetime.now(timezone.utc).isoformat(),
        )
        
        # Default domain weights from CDAF framework
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
        method_instance: Any | None = None,
        posterior_samples: np. ndarray | None = None,
        context: dict[str, Any] | None = None,
    ) -> CalibratedOutput: 
        """Main entry point:  Calibrate a method output with full uncertainty propagation. 
        
        Decision tree:
        1. If method_instance implements CalibrableMethod protocol → DELEGATE
        2. Else → Apply central MicroLevelThresholds with synthetic posterior
        
        Args:
            question_id: The question being answered (e.g., "Q001")
            method_id: The method that produced the score (e. g., "FINANCIERO: bayesian_risk")
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
        
        # Validate input
        if not 0.0 <= raw_score <= 1.0:
            raise ValueError(f"raw_score must be in [0.0, 1.0], got {raw_score}")
        
        # Determine calibration pathway
        if self._implements_calibrable_protocol(method_instance):
            # DELEGATION PATH
            result = self._delegate_to_method(
                method_instance=method_instance,
                raw_score=raw_score,
                posterior_samples=posterior_samples,
                context=context,
            )
            calibration_source = "method_delegation"
            transformation_applied = result.transformation_name
            transformation_parameters = result. transformation_parameters
            label_probabilities = result.label_probabilities
            calibrated_score = result.calibrated_score
            posterior_samples = result. posterior_samples
            credible_interval = result.credible_interval_95
            method_class_name = type(method_instance).__name__
        else:
            # CENTRAL THRESHOLD PATH
            result = self._apply_central_calibration(
                raw_score=raw_score,
                posterior_samples=posterior_samples,
            )
            calibration_source = "central_threshold"
            transformation_applied = "micro_level_threshold_with_synthetic_posterior"
            transformation_parameters = {
                "thresholds":  {
                    "excelente": self._thresholds.excelente,
                    "bueno":  self._thresholds.bueno,
                    "aceptable": self._thresholds.aceptable,
                },
            }
            label_probabilities = result["label_probabilities"]
            calibrated_score = result["calibrated_score"]
            posterior_samples = result["posterior_samples"]
            credible_interval = result["credible_interval_95"]
            method_class_name = "None"
        
        # Determine label and weight from probability mass
        label = label_probabilities.modal_label
        weight = self._label_to_weight(label, label_probabilities. modal_probability)
        
        # Extract domain from context or method
        domain = context. get("domain", "unknown")
        if method_instance and hasattr(method_instance, "calibration_params"):
            domain = method_instance.calibration_params.get("domain", domain)
        
        domain_weight = self._default_domain_weights.get(domain)
        contract_priority = context. get("contract_priority")
        
        # Build provenance
        provenance = CalibrationProvenance(
            question_id=question_id,
            method_id=method_id,
            method_class_name=method_class_name,
            raw_score=raw_score,
            raw_score_semantics=context.get("output_semantics", "normalized_score"),
            posterior_mean=float(np.mean(posterior_samples)) if posterior_samples is not None else None,
            posterior_std=float(np. std(posterior_samples)) if posterior_samples is not None else None,
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
        
        # Append to audit log
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
    
    def _implements_calibrable_protocol(self, instance: Any) -> bool:
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
        method_instance: Any,
        raw_score:  float,
        posterior_samples: np. ndarray | None,
        context: dict[str, Any],
    ) -> MethodCalibrationResult:
        """Delegate calibration to method's calibrate_output()."""
        return method_instance.calibrate_output(
            raw_score=raw_score,
            posterior_samples=posterior_samples,
            context=context,
        )
    
    def _apply_central_calibration(
        self,
        raw_score:  float,
        posterior_samples: np. ndarray | None,
    ) -> dict[str, Any]: 
        """Apply central MicroLevelThresholds with synthetic posterior. 
        
        Used when method does not implement CalibrableMethod protocol. 
        Generates synthetic posterior to avoid false certainty.
        """
        
        if posterior_samples is None or len(posterior_samples) == 0:
            # Generate synthetic posterior centered on raw_score
            # Use moderate uncertainty (std=0.1) to reflect lack of method-specific info
            posterior_samples = np.clip(
                np. random.normal(raw_score, 0.1, size=10000),
                0.0,
                1.0,
            )
        
        # Compute label probabilities from posterior
        n = len(posterior_samples)
        t_e, t_b, t_a = self._thresholds. excelente, self._thresholds. bueno, self._thresholds.aceptable
        
        label_probabilities = LabelProbabilityMass(
            excelente=float(np.sum(posterior_samples >= t_e) / n),
            bueno=float(np. sum((posterior_samples >= t_b) & (posterior_samples < t_e)) / n),
            aceptable=float(np.sum((posterior_samples >= t_a) & (posterior_samples < t_b)) / n),
            insuficiente=float(np.sum(posterior_samples < t_a) / n),
        )
        
        return {
            "calibrated_score": float(np.mean(posterior_samples)),
            "label_probabilities": label_probabilities,
            "posterior_samples": posterior_samples,
            "credible_interval_95": (
                float(np. percentile(posterior_samples, 2.5)),
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
        
        Modulation:  weight *= (0.7 + 0.3 * modal_probability)
        This reduces weight when classification is uncertain.
        """
        base_weights = {
            QualityLabel. EXCELENTE: 1.0,
            QualityLabel.BUENO:  0.90,
            QualityLabel.ACEPTABLE: 0.75,
            QualityLabel. INSUFICIENTE:  0.40,
        }
        
        base = base_weights[label]
        confidence_modulation = 0.7 + 0.3 * modal_probability
        
        return base * confidence_modulation
    
    @property
    def audit_log(self) -> list[CalibrationProvenance]:
        """Return audit log (read-only copy)."""
        return list(self._audit_log)
    
    def export_audit_log(self) -> list[dict[str, Any]]:
        """Export audit log as JSON-serializable list."""
        return [
            {
                "question_id": p.question_id,
                "method_id": p.method_id,
                "method_class_name": p.method_class_name,
                "raw_score": p.raw_score,
                "calibration_source": p.calibration_source,
                "transformation_applied": p. transformation_applied,
                "domain": p.domain,
                "assigned_label": p. assigned_label. value,
                "assigned_weight": p. assigned_weight,
                "modal_probability": p. label_probabilities.modal_probability,
                "entropy": p.label_probabilities.entropy,
                "uncertainty_flag": (
                    "LOW" if p.label_probabilities.entropy < 0.5 else
                    "MODERATE" if p.label_probabilities.entropy < 1.0 else
                    "HIGH"
                ),
                "timestamp_utc": p. timestamp_utc,
                "provenance_hash": p.provenance_hash,
            }
            for p in self._audit_log
        ]
```

---

## Failure Modes

| Failure Mode | Detection | Mitigation |
|--------------|-----------|------------|
| Method claims protocol but `calibrate_output()` raises | `try/except` in `_delegate_to_method()` with fallback to central | Log error, do NOT silently succeed |
| Posterior samples contain NaN/Inf | Validate in `_apply_central_calibration()` | `np.isfinite()` check, raise `ValueError` |
| Label probabilities don't sum to 1.0 | `__post_init__` assertion | Constructor fails loudly |
| Thresholds not monotonic | `__post_init__` assertion | Constructor fails loudly |
| Domain weight missing | Return `None`, log warning | Do not invent weight |

## Termination Conditions

- **Delegation terminates** when method's `calibrate_output()` returns `MethodCalibrationResult`
- **Central calibration terminates** when posterior sampling completes (fixed 10000 samples)
- **No fallback cascades**:  If method delegation fails, raise exception, do not silently fall back

## Verification Strategy

1. **Unit tests**: Each data class, each method, each edge case
2. **Property-based tests**: Hypothesis for probability mass properties
3. **Integration tests**: Full pipeline from raw score to `CalibratedOutput`
4. **FMEA trace**: Each failure mode has explicit test
5. **Benchmark**:  Compare against current threshold ladder on held-out labels

---


## References

- `src/farfan_pipeline/methods/financiero_viabilidad_tablas.py`: Lines 344-354 (`PDETMunicipalPlanAnalyzer.__init__`), Lines 800-841 (`_bayesian_risk_inference`)
- `src/farfan_pipeline/methods/policy_processor.py`: Lines 991-1163 (`BayesianEvidenceScorer`)
- `src/farfan_pipeline/methods/analyzer_one.py`: Lines 1099-1466 (`SemanticAnalyzer`)
- `questionnaire_monolith.json`: `scoring. micro_levels` (source of truth for thresholds)

---

**Owner**: Phase 2 Analysis Team  
**Lifecycle**: Draft Proposal  
**Priority**: Critical (blocks accurate scoring across 300 contract executors)  
**Estimated Effort**: 3-5 days  
**Last Updated**: 2025-12-22
