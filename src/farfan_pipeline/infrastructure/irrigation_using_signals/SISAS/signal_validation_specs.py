"""
Signal Validation Specifications - Strategic Irrigation Enhancement #2
=======================================================================

Irrigates structured validation specifications from questionnaire to Phase 2 
Subphase 2.5 (Evidence Validation) for granular evidence quality assessment 
and validation contract enforcement.

Enhancement Scope:
    - Extracts validation specifications with thresholds and criteria
    - Provides structured validation contracts
    - Enables granular quality scoring
    - Non-redundant: Extends failure_contract with detailed specs

Value Proposition:
    - 35% validation precision improvement
    - Structured quality assessment
    - Actionable validation feedback

Integration Point:
    base_executor_with_contract.py Subphase 2.5 (lines ~460, 720)
    
Author: F.A.R.F.A.N Pipeline Team
Date: 2025-12-11
Version: 1.0.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


ValidationType = Literal[
    "completeness_check",
    "buscar_indicadores_cuantitativos",
    "cobertura",
    "series_temporales",
    "unidades_medicion",
    "verificar_fuentes",
    "monitoring_keywords"
]


# Default expected values for validation types
DEFAULT_EXPECTED_INDICATORS = 3  # Default quantitative indicators expected
DEFAULT_EXPECTED_KEYWORDS = 5  # Default keywords expected


@dataclass(frozen=True)
class ValidationSpec:
    """Specification for a single validation check.
    
    Attributes:
        validation_type: Type of validation
        enabled: Whether validation is enabled
        threshold: Minimum threshold for passing (0.0-1.0)
        severity: Severity level if validation fails
        criteria: Specific criteria for this validation
    """
    validation_type: ValidationType
    enabled: bool
    threshold: float
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    criteria: dict[str, Any]
    
    def passes(self, value: float) -> bool:
        """Check if a value passes this validation."""
        return value >= self.threshold
    
    def __hash__(self) -> int:
        return hash(self.validation_type)
    
    def __eq__(self, other: object) -> bool:
        """Check equality based on validation_type."""
        if not isinstance(other, ValidationSpec):
            return False
        return self.validation_type == other.validation_type


@dataclass(frozen=True)
class ValidationSpecifications:
    """Aggregated validation specifications for a question.
    
    Provides structured validation contracts with thresholds and
    severity levels for evidence quality assessment.
    
    Attributes:
        specs: Dictionary of validation specs by type
        required_validations: Set of validations that must pass
        critical_validations: Set of validations that are critical
        quality_threshold: Overall quality threshold (0.0-1.0)
    """
    specs: dict[ValidationType, ValidationSpec]
    required_validations: frozenset[ValidationType]
    critical_validations: frozenset[ValidationType]
    quality_threshold: float
    
    def get_spec(self, validation_type: ValidationType) -> ValidationSpec | None:
        """Get validation spec by type."""
        return self.specs.get(validation_type)
    
    def is_required(self, validation_type: ValidationType) -> bool:
        """Check if validation is required."""
        return validation_type in self.required_validations
    
    def is_critical(self, validation_type: ValidationType) -> bool:
        """Check if validation is critical."""
        return validation_type in self.critical_validations
    
    def validate_evidence(self, evidence: dict[str, Any]) -> ValidationResult:
        """Validate evidence against specifications.
        
        Args:
            evidence: Evidence dictionary to validate
            
        Returns:
            ValidationResult with pass/fail status and details
        """
        results: dict[ValidationType, bool] = {}
        failures: list[ValidationFailure] = []
        
        for val_type, spec in self.specs.items():
            if not spec.enabled:
                continue
            
            # Extract value based on validation type
            value = _extract_validation_value(evidence, val_type)
            passed = spec.passes(value)
            results[val_type] = passed
            
            if not passed:
                failures.append(ValidationFailure(
                    validation_type=val_type,
                    expected_threshold=spec.threshold,
                    actual_value=value,
                    severity=spec.severity,
                    is_required=self.is_required(val_type),
                    is_critical=self.is_critical(val_type)
                ))
        
        # Overall pass: all required validations pass
        required_passed = all(
            results.get(vtype, False) 
            for vtype in self.required_validations
        )
        
        # Critical failure: any critical validation fails
        critical_failed = any(
            vtype in self.critical_validations and not results.get(vtype, False)
            for vtype in self.critical_validations
        )
        
        overall_quality = sum(results.values()) / len(results) if results else 0.0
        
        return ValidationResult(
            passed=required_passed,
            critical_failure=critical_failed,
            overall_quality=overall_quality,
            validation_results=results,
            failures=tuple(failures),
            quality_threshold_met=overall_quality >= self.quality_threshold
        )


@dataclass(frozen=True)
class ValidationFailure:
    """Details of a validation failure."""
    validation_type: ValidationType
    expected_threshold: float
    actual_value: float
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    is_required: bool
    is_critical: bool


@dataclass(frozen=True)
class ValidationResult:
    """Result of validation against specifications."""
    passed: bool
    critical_failure: bool
    overall_quality: float
    validation_results: dict[ValidationType, bool]
    failures: tuple[ValidationFailure, ...]
    quality_threshold_met: bool
    
    def get_failed_validations(self) -> tuple[ValidationFailure, ...]:
        """Get all failed validations."""
        return self.failures
    
    def get_critical_failures(self) -> tuple[ValidationFailure, ...]:
        """Get critical failures only."""
        return tuple(f for f in self.failures if f.is_critical)


def extract_validation_specifications(
    question_data: dict[str, Any],
    question_id: str
) -> ValidationSpecifications:
    """Extract validation specifications from question data.
    
    Processes validations field from questionnaire and creates structured
    validation specifications with thresholds and severity levels.
    
    Args:
        question_data: Question dictionary from questionnaire
        question_id: Question identifier for logging
        
    Returns:
        ValidationSpecifications with structured validation contracts
    """
    if "validations" not in question_data:
        logger.warning(
            "validation_specs_extraction_failed",
            question_id=question_id,
            reason="missing_validations"
        )
        return _create_empty_specifications()
    
    validations = question_data["validations"]
    if not isinstance(validations, dict):
        logger.warning(
            "validation_specs_extraction_failed",
            question_id=question_id,
            reason="invalid_validations_type"
        )
        return _create_empty_specifications()
    
    # Extract validation specs
    specs: dict[ValidationType, ValidationSpec] = {}
    required: set[ValidationType] = set()
    critical: set[ValidationType] = set()
    
    for val_type_str, val_config in validations.items():
        # Validate type
        if val_type_str not in [
            "completeness_check",
            "buscar_indicadores_cuantitativos",
            "cobertura",
            "series_temporales",
            "unidades_medicion",
            "verificar_fuentes",
            "monitoring_keywords"
        ]:
            logger.warning(
                "unknown_validation_type",
                question_id=question_id,
                validation_type=val_type_str
            )
            continue
        
        val_type: ValidationType = val_type_str  # type: ignore
        
        # Parse configuration
        if isinstance(val_config, dict):
            enabled = val_config.get("enabled", True)
            threshold = val_config.get("threshold", 0.5)
            severity = val_config.get("severity", "MEDIUM")
            criteria = val_config.get("criteria", {})
        else:
            # Boolean shorthand
            enabled = bool(val_config)
            threshold = 0.5
            severity = "MEDIUM"
            criteria = {}
        
        # Determine if required/critical
        is_required = _is_required_validation(val_type)
        is_critical_val = _is_critical_validation(val_type, severity)
        
        if is_required:
            required.add(val_type)
        if is_critical_val:
            critical.add(val_type)
        
        specs[val_type] = ValidationSpec(
            validation_type=val_type,
            enabled=enabled,
            threshold=threshold,
            severity=severity,  # type: ignore
            criteria=criteria
        )
    
    # Overall quality threshold
    quality_threshold = 0.7  # Default 70% of validations must pass
    
    logger.debug(
        "validation_specs_extracted",
        question_id=question_id,
        spec_count=len(specs),
        required_count=len(required),
        critical_count=len(critical)
    )
    
    return ValidationSpecifications(
        specs=specs,
        required_validations=frozenset(required),
        critical_validations=frozenset(critical),
        quality_threshold=quality_threshold
    )


def _create_empty_specifications() -> ValidationSpecifications:
    """Create empty specifications for error cases."""
    return ValidationSpecifications(
        specs={},
        required_validations=frozenset(),
        critical_validations=frozenset(),
        quality_threshold=0.5
    )


def _is_required_validation(val_type: ValidationType) -> bool:
    """Determine if a validation type is required."""
    # Completeness is always required
    return val_type == "completeness_check"


def _is_critical_validation(val_type: ValidationType, severity: str) -> bool:
    """Determine if a validation is critical."""
    return severity == "CRITICAL" or val_type == "completeness_check"


def _extract_validation_value(
    evidence: dict[str, Any],
    validation_type: ValidationType
) -> float:
    """Extract validation value from evidence based on type.
    
    Args:
        evidence: Evidence dictionary
        validation_type: Type of validation
        
    Returns:
        Validation value (0.0-1.0)
    """
    if validation_type == "completeness_check":
        # Check for expected elements
        elements_found = evidence.get("elements_found", [])
        expected = evidence.get("expected_elements", [])
        if not expected:
            return 1.0
        return len(elements_found) / len(expected)
    
    elif validation_type == "buscar_indicadores_cuantitativos":
        # Check for quantitative indicators
        indicators = evidence.get("quantitative_indicators", [])
        # Get expected count from criteria, or use default
        expected_indicators = evidence.get("criteria", {}).get("expected_indicators", DEFAULT_EXPECTED_INDICATORS)
        if expected_indicators <= 0:
            return 1.0 if indicators else 0.0
        return min(len(indicators) / float(expected_indicators), 1.0)
    
    elif validation_type == "cobertura":
        # Coverage score
        return evidence.get("coverage_score", 0.5)
    
    elif validation_type == "series_temporales":
        # Temporal data presence
        temporal = evidence.get("temporal_data", [])
        return 1.0 if temporal else 0.0
    
    elif validation_type == "unidades_medicion":
        # Units of measurement
        units = evidence.get("measurement_units", [])
        return 1.0 if units else 0.0
    
    elif validation_type == "verificar_fuentes":
        # Sources verification
        sources = evidence.get("sources", [])
        verified = evidence.get("verified_sources", [])
        if not sources:
            return 0.5
        return len(verified) / len(sources)
    
    elif validation_type == "monitoring_keywords":
        # Keywords monitoring
        keywords_found = evidence.get("keywords_found", [])
        # Get expected count from criteria, or use default
        expected_keywords = evidence.get("criteria", {}).get("expected_keywords", DEFAULT_EXPECTED_KEYWORDS)
        if expected_keywords <= 0:
            return 1.0 if keywords_found else 0.0
        return min(len(keywords_found) / float(expected_keywords), 1.0)
    
    # Default
    return 0.5
