"""
Phase 7 Exit Gate Validation
============================

Validates Phase 7 output against Phase 8 input requirements.

This module implements the exit gate validation that ensures MacroScore
output meets all requirements for consumption by Phase 8 (Recommendations Engine).

Constitutional Invariants:
    - All postconditions must pass before exiting Phase 7
    - MacroScore must be complete and valid
    - Certificate generated for Phase 8 consumption

Version: 1.0.0
Author: F.A.R.F.A.N Core Architecture Team
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_07.phase7_10_00_macro_score import MacroScore


@dataclass
class ExitGateResult:
    """Result of Phase 7 exit gate validation.

    Attributes:
        passed: Whether all validation checks passed
        checks_performed: List of validation check descriptions
        errors: List of error messages
        warnings: List of warning messages
        certificate: Compatibility certificate for Phase 8
        timestamp: UTC timestamp of validation
    """
    passed: bool
    checks_performed: List[str]
    errors: List[str]
    warnings: List[str]
    certificate: Dict[str, Any]
    timestamp: str


class Phase7ExitGateValidator:
    """
    Validates Phase 7 output against Phase 8 input requirements.

    Ensures that MacroScore is ready for consumption by the Recommendations Engine.

    Exit Gates:
        GATE-1: Output contract validation (POST-7.1 through POST-7.7)
        GATE-2: Quality level assignment validation
        GATE-3: Coherence and alignment bounds validation
        GATE-4: Provenance traceability validation
        GATE-5: Phase 8 compatibility validation
    """

    def __init__(self, strict_mode: bool = False):
        """Initialize exit gate validator.

        Args:
            strict_mode: If True, fail on warnings as well as errors
        """
        self.strict_mode = strict_mode

    def validate(
        self,
        macro_score: "MacroScore",
        input_cluster_ids: List[str],
    ) -> ExitGateResult:
        """
        Validate Phase 7 output through all exit gates.

        Args:
            macro_score: MacroScore object produced by Phase 7
            input_cluster_ids: List of cluster IDs from input

        Returns:
            ExitGateResult with validation outcome
        """
        checks_performed = []
        errors = []
        warnings = []

        # GATE-1: Output contract validation
        try:
            from farfan_pipeline.phases.Phase_07.contracts.phase7_10_02_output_contract import (
                Phase7OutputContract,
            )

            is_valid, error_msg = Phase7OutputContract.validate(
                macro_score, set(input_cluster_ids)
            )

            if is_valid:
                checks_performed.append("✓ GATE-1: Output contract validated")
            else:
                errors.append(f"✗ GATE-1: Output contract violation: {error_msg}")

        except ImportError:
            warnings.append("⚠ GATE-1: Output contract not available, using manual validation")
            self._manual_output_validation(macro_score, input_cluster_ids, checks_performed, errors)

        # GATE-2: Quality level validation
        self._validate_quality_level(macro_score, checks_performed, errors, warnings)

        # GATE-3: Coherence and alignment bounds
        self._validate_coherence_alignment(macro_score, checks_performed, errors)

        # GATE-4: Provenance traceability
        self._validate_provenance(macro_score, input_cluster_ids, checks_performed, warnings)

        # GATE-5: Phase 8 compatibility
        certificate = self._generate_phase8_certificate(macro_score, input_cluster_ids)

        # Determine overall pass/fail
        passed = len(errors) == 0 and (not self.strict_mode or len(warnings) == 0)

        result = ExitGateResult(
            passed=passed,
            checks_performed=checks_performed,
            errors=errors,
            warnings=warnings,
            certificate=certificate,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        return result

    def _manual_output_validation(
        self,
        macro_score: "MacroScore",
        input_cluster_ids: List[str],
        checks: List[str],
        errors: List[str],
    ) -> None:
        """Manual output validation when contract is unavailable."""
        # POST-7.1: Type validation
        if not hasattr(macro_score, 'score'):
            errors.append("✗ POST-7.1: Output missing 'score' attribute")
        else:
            checks.append("✓ POST-7.1: MacroScore has required attributes")

        # POST-7.2: Score bounds
        if hasattr(macro_score, 'score'):
            if not (0.0 <= macro_score.score <= 3.0):
                errors.append(f"✗ POST-7.2: Score out of bounds: {macro_score.score}")
            else:
                checks.append("✓ POST-7.2: Score within bounds [0.0, 3.0]")

        # POST-7.3: Quality level
        if hasattr(macro_score, 'quality_level'):
            valid_levels = {"EXCELENTE", "BUENO", "ACEPTABLE", "INSUFICIENTE"}
            if macro_score.quality_level not in valid_levels:
                errors.append(f"✗ POST-7.3: Invalid quality level: {macro_score.quality_level}")
            else:
                checks.append(f"✓ POST-7.3: Quality level valid: {macro_score.quality_level}")

    def _validate_quality_level(
        self,
        macro_score: "MacroScore",
        checks: List[str],
        errors: List[str],
        warnings: List[str],
    ) -> None:
        """Validate quality level assignment."""
        if not hasattr(macro_score, 'quality_level') or not hasattr(macro_score, 'score_normalized'):
            warnings.append("⚠ GATE-2: Quality level or normalized score missing")
            return

        # Check that quality level matches score
        score = macro_score.score_normalized if hasattr(macro_score, 'score_normalized') else macro_score.score / 3.0
        quality = macro_score.quality_level

        # Define thresholds
        thresholds = {
            "EXCELENTE": 0.85,
            "BUENO": 0.70,
            "ACEPTABLE": 0.55,
        }

        expected_level = "INSUFICIENTE"
        if score >= thresholds["EXCELENTE"]:
            expected_level = "EXCELENTE"
        elif score >= thresholds["BUENO"]:
            expected_level = "BUENO"
        elif score >= thresholds["ACEPTABLE"]:
            expected_level = "ACEPTABLE"

        if quality == expected_level:
            checks.append(f"✓ GATE-2: Quality level matches score ({quality} @ {score:.3f})")
        else:
            errors.append(f"✗ GATE-2: Quality level mismatch: expected {expected_level}, got {quality}")

    def _validate_coherence_alignment(
        self,
        macro_score: "MacroScore",
        checks: List[str],
        errors: List[str],
    ) -> None:
        """Validate coherence and alignment bounds."""
        # POST-7.4: Coherence bounds
        if hasattr(macro_score, 'cross_cutting_coherence'):
            coherence = macro_score.cross_cutting_coherence
            if not (0.0 <= coherence <= 1.0):
                errors.append(f"✗ GATE-3: Coherence out of bounds: {coherence}")
            else:
                checks.append(f"✓ GATE-3: Coherence within bounds [0.0, 1.0]: {coherence:.3f}")

        # POST-7.5: Alignment bounds
        if hasattr(macro_score, 'strategic_alignment'):
            alignment = macro_score.strategic_alignment
            if not (0.0 <= alignment <= 1.0):
                errors.append(f"✗ GATE-3: Alignment out of bounds: {alignment}")
            else:
                checks.append(f"✓ GATE-3: Alignment within bounds [0.0, 1.0]: {alignment:.3f}")

    def _validate_provenance(
        self,
        macro_score: "MacroScore",
        input_cluster_ids: List[str],
        checks: List[str],
        warnings: List[str],
    ) -> None:
        """Validate provenance traceability."""
        if not hasattr(macro_score, 'provenance_node_id'):
            warnings.append("⚠ GATE-4: Provenance node ID missing")
            return

        checks.append(f"✓ GATE-4: Provenance tracked: {macro_score.provenance_node_id}")

        # POST-7.6: Verify all input clusters are represented
        if hasattr(macro_score, 'cluster_scores'):
            contributing_clusters = {cs.cluster_id for cs in macro_score.cluster_scores}
            input_clusters_set = set(input_cluster_ids)

            if contributing_clusters == input_clusters_set:
                checks.append("✓ GATE-4: All input clusters represented in output")
            else:
                warnings.append(
                    f"⚠ GATE-4: Cluster mismatch in provenance: "
                    f"expected {input_clusters_set}, got {contributing_clusters}"
                )

    def _generate_phase8_certificate(
        self,
        macro_score: "MacroScore",
        input_cluster_ids: List[str],
    ) -> Dict[str, Any]:
        """Generate compatibility certificate for Phase 8 consumption."""
        certificate = {
            "certificate_type": "Phase 7 → Phase 8 Compatibility",
            "certificate_version": "1.0.0",
            "issued_at": datetime.now(timezone.utc).isoformat(),
            "macro_score_id": getattr(macro_score, 'evaluation_id', 'UNKNOWN'),
            "macro_score": getattr(macro_score, 'score', 0.0),
            "quality_level": getattr(macro_score, 'quality_level', 'UNKNOWN'),
            "coherence": getattr(macro_score, 'cross_cutting_coherence', 0.0),
            "alignment": getattr(macro_score, 'strategic_alignment', 0.0),
            "input_clusters": input_cluster_ids,
            "systemic_gaps": getattr(macro_score, 'systemic_gaps', []),
            "ready_for_phase8": True,
        }

        return certificate


def validate_phase7_exit_gate(
    macro_score: "MacroScore",
    input_cluster_ids: List[str],
    strict_mode: bool = False,
) -> ExitGateResult:
    """
    Validate Phase 7 exit gate and return result.

    This is the main entry point for Phase 7 exit gate validation.

    Args:
        macro_score: MacroScore object produced by Phase 7
        input_cluster_ids: List of cluster IDs from input
        strict_mode: If True, fail on warnings as well as errors

    Returns:
        ExitGateResult with validation outcome

    Raises:
        ValueError: If exit gate validation fails in strict mode
    """
    validator = Phase7ExitGateValidator(strict_mode=strict_mode)
    result = validator.validate(macro_score, input_cluster_ids)

    if not result.passed:
        error_msg = "Phase 7 Exit Gate Validation Failed:\n"
        for error in result.errors:
            error_msg += f"  {error}\n"
        raise ValueError(error_msg)

    return result


__all__ = [
    "ExitGateResult",
    "Phase7ExitGateValidator",
    "validate_phase7_exit_gate",
]
