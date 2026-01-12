"""
Normative Compliance Validator - Phase 3 Critical Component

Validates normative compliance for Colombian municipal policy documents based on
empirical calibration from 14 PDT plans.

This validator implements the scoring algorithm defined in normative_compliance.json
and fulfills the CC_COHERENCIA_NORMATIVA cross-cutting theme requirement.

Key Features:
- Validates mandatory norms by policy area
- Applies contextual rules (PDET, ethnic territories)
- Calculates penalties for missing norms
- Generates gap reports with recommendations
- Supports universal mandatory norms (applicable to all PAs)

Author: F.A.R.F.A.N Pipeline Team - Phase 3 Enhancement
Version: 1.0.0
Date: 2026-01-12
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class NormGap:
    """Represents a missing mandatory norm."""

    norm_id: str
    norm_name: str
    policy_area: str
    reason: str
    penalty: float
    severity: str  # "CRITICAL", "HIGH", "MEDIUM"
    recommendation: str


@dataclass
class ValidationResult:
    """Result of normative compliance validation."""

    policy_area: str
    score: float  # 0.0-1.0
    cited_norms: list[str]
    mandatory_norms: list[str]
    missing_norms: list[NormGap]
    contextual_rules_applied: list[str]
    total_penalty: float
    interpretation: str  # "EXCELENTE", "BUENO", "ACEPTABLE", "DEFICIENTE"
    recommendations: list[str]
    validation_passed: bool
    metadata: dict[str, Any] = field(default_factory=dict)


class NormativeComplianceValidator:
    """
    Validator for normative compliance based on empirical calibration.

    Loads mandatory norms from normative_compliance.json and validates that
    policy documents cite the required legal framework.

    Usage:
        validator = NormativeComplianceValidator()
        result = validator.validate(
            plan_id="cajibio_2024",
            policy_area="PA05",
            cited_norms=["Ley 1448 de 2011", "Decreto 893 de 2017"],
            context={"is_pdet": True}
        )
    """

    def __init__(self, compliance_file: Path | None = None):
        """
        Initialize validator with normative compliance data.

        Args:
            compliance_file: Path to normative_compliance.json (optional)
        """
        if compliance_file is None:
            compliance_file = (
                Path(__file__).resolve().parent.parent.parent.parent.parent
                / "canonic_questionnaire_central"
                / "_registry"
                / "entities"
                / "normative_compliance.json"
            )

        self.compliance_file = compliance_file
        self.compliance_data = self._load_compliance_data()

        # Extract key components
        self.mandatory_by_pa = self.compliance_data.get("mandatory_norms_by_policy_area", {})
        self.universal_mandatory = self.compliance_data.get("universal_mandatory_norms", [])
        self.contextual_rules = self.compliance_data.get("contextual_validation_rules", {})
        self.scoring_algorithm = self.compliance_data.get("scoring_algorithm", {})

        logger.info(
            f"NormativeComplianceValidator initialized with {len(self.mandatory_by_pa)} policy areas"
        )

    def _load_compliance_data(self) -> dict[str, Any]:
        """Load normative compliance JSON."""
        try:
            with open(self.compliance_file, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Normative compliance file not found: {self.compliance_file}")
            raise RuntimeError(
                f"Cannot initialize NormativeComplianceValidator without compliance data at: {self.compliance_file}"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in normative compliance file: {e}")
            raise

    def validate(
        self,
        plan_id: str,
        policy_area: str,
        cited_norms: list[str],
        context: dict[str, Any] | None = None,
    ) -> ValidationResult:
        """
        Validate normative compliance for a policy area.

        Args:
            plan_id: Plan identifier
            policy_area: Policy area code (PA01-PA10)
            cited_norms: List of norm IDs cited in the document
            context: Optional context (is_pdet, ethnic_territory, etc.)

        Returns:
            ValidationResult with score and gap analysis
        """
        context = context or {}

        # Get mandatory norms for this PA
        mandatory_norms = self._get_mandatory_norms(policy_area)

        # Apply contextual rules
        contextual_rules_applied = []
        if context:
            additional_norms, rules_applied = self._apply_contextual_rules(policy_area, context)
            mandatory_norms.extend(additional_norms)
            contextual_rules_applied = rules_applied

        # Add universal mandatory norms
        for norm in self.universal_mandatory:
            if norm not in mandatory_norms:
                mandatory_norms.append(norm)

        # Normalize cited norms for comparison
        cited_norms_normalized = [self._normalize_norm_id(n) for n in cited_norms]

        # Find missing norms
        missing_norms = []
        total_penalty = 0.0

        for norm in mandatory_norms:
            norm_id = norm.get("norm_id", "")
            norm_id_normalized = self._normalize_norm_id(norm_id)

            # Check if cited
            if not any(norm_id_normalized in cited for cited in cited_norms_normalized):
                penalty = norm.get("penalty_if_missing", 0.2)
                severity = self._calculate_severity(penalty)

                gap = NormGap(
                    norm_id=norm_id,
                    norm_name=norm.get("name", ""),
                    policy_area=policy_area,
                    reason=norm.get("reason", "Norma obligatoria no citada"),
                    penalty=penalty,
                    severity=severity,
                    recommendation=self._generate_recommendation(norm, policy_area),
                )

                missing_norms.append(gap)
                total_penalty += penalty

        # Calculate score using algorithm from JSON
        score = self._calculate_score(total_penalty)

        # Interpret score
        interpretation = self._interpret_score(score)

        # Generate recommendations
        recommendations = self._generate_recommendations(missing_norms, policy_area, context)

        # Validation passes if score >= 0.60 (ACEPTABLE)
        validation_passed = score >= 0.60

        result = ValidationResult(
            policy_area=policy_area,
            score=score,
            cited_norms=cited_norms,
            mandatory_norms=[n.get("norm_id", "") for n in mandatory_norms],
            missing_norms=missing_norms,
            contextual_rules_applied=contextual_rules_applied,
            total_penalty=total_penalty,
            interpretation=interpretation,
            recommendations=recommendations,
            validation_passed=validation_passed,
            metadata={
                "plan_id": plan_id,
                "total_mandatory": len(mandatory_norms),
                "total_cited": len(cited_norms),
                "total_missing": len(missing_norms),
                "compliance_percentage": (1 - len(missing_norms) / len(mandatory_norms)) * 100
                if mandatory_norms
                else 100,
            },
        )

        logger.info(
            f"Validation complete for {plan_id}/{policy_area}: "
            f"score={score:.2f}, missing={len(missing_norms)}"
        )

        return result

    def _get_mandatory_norms(self, policy_area: str) -> list[dict[str, Any]]:
        """Get mandatory norms for a policy area."""
        pa_data = self.mandatory_by_pa.get(policy_area, {})
        mandatory = pa_data.get("mandatory", [])
        return [norm.copy() for norm in mandatory]

    def _apply_contextual_rules(
        self, policy_area: str, context: dict[str, Any]
    ) -> tuple[list[dict[str, Any]], list[str]]:
        """Apply contextual validation rules."""
        additional_norms = []
        rules_applied = []

        # Rule 1: PDET municipalities
        if context.get("is_pdet", False):
            pdet_rule = self.contextual_rules.get("pdet_municipalities", {})
            for norm in pdet_rule.get("additional_mandatory", []):
                additional_norms.append(norm)
                rules_applied.append("pdet_municipalities")

        # Rule 2: Ethnic territories
        ethnic_pct = context.get("ethnic_population_pct", 0.0)
        if ethnic_pct > 0.10:  # >10% indigenous or afro
            ethnic_rule = self.contextual_rules.get("ethnic_territories", {})
            for norm in ethnic_rule.get("additional_mandatory", []):
                additional_norms.append(norm)
                rules_applied.append("ethnic_territories")

        # Rule 3: Conflict-affected zones
        if context.get("conflict_affected", False):
            conflict_rule = self.contextual_rules.get("conflict_affected_zones", {})
            for norm in conflict_rule.get("additional_mandatory", []):
                additional_norms.append(norm)
                rules_applied.append("conflict_affected_zones")

        return additional_norms, list(set(rules_applied))

    def _normalize_norm_id(self, norm_id: str) -> str:
        """Normalize norm ID for comparison."""
        return norm_id.lower().strip().replace("  ", " ")

    def _calculate_severity(self, penalty: float) -> str:
        """Calculate severity based on penalty."""
        if penalty >= 0.30:
            return "CRITICAL"
        elif penalty >= 0.20:
            return "HIGH"
        else:
            return "MEDIUM"

    def _calculate_score(self, total_penalty: float) -> float:
        """
        Calculate compliance score using algorithm from JSON.

        Formula: score = max(0.0, 1.0 - SUM(penalties))
        """
        score = max(0.0, 1.0 - total_penalty)
        return round(score, 3)

    def _interpret_score(self, score: float) -> str:
        """Interpret score according to thresholds."""
        interpretation_rules = self.scoring_algorithm.get("interpretation", {})

        # Default thresholds if not in JSON
        thresholds = {
            "EXCELENTE": 0.90,
            "BUENO": 0.75,
            "ACEPTABLE": 0.60,
            "DEFICIENTE": 0.0,
        }

        # Try to parse from JSON
        for level, threshold_str in interpretation_rules.items():
            if ">=" in threshold_str:
                threshold_val = float(threshold_str.split(">=")[1].strip())
                thresholds[level] = threshold_val

        if score >= thresholds.get("EXCELENTE", 0.90):
            return "EXCELENTE"
        elif score >= thresholds.get("BUENO", 0.75):
            return "BUENO"
        elif score >= thresholds.get("ACEPTABLE", 0.60):
            return "ACEPTABLE"
        else:
            return "DEFICIENTE"

    def _generate_recommendation(self, norm: dict[str, Any], policy_area: str) -> str:
        """Generate recommendation for a missing norm."""
        norm_id = norm.get("norm_id", "")
        norm_name = norm.get("name", "")

        return (
            f"Se recomienda incluir referencia explícita a {norm_id} ({norm_name}) "
            f"en el capítulo correspondiente a {policy_area}, dado que constituye "
            f"el marco normativo fundamental para esta área de política."
        )

    def _generate_recommendations(
        self,
        missing_norms: list[NormGap],
        policy_area: str,
        context: dict[str, Any],
    ) -> list[str]:
        """Generate comprehensive recommendations."""
        recommendations = []

        # Group by severity
        critical_gaps = [g for g in missing_norms if g.severity == "CRITICAL"]
        high_gaps = [g for g in missing_norms if g.severity == "HIGH"]

        if critical_gaps:
            critical_norms = ", ".join([g.norm_id for g in critical_gaps])
            recommendations.append(
                f"CRÍTICO: Incluir inmediatamente las siguientes normas fundamentales: {critical_norms}"
            )

        if high_gaps:
            high_norms = ", ".join([g.norm_id for g in high_gaps])
            recommendations.append(
                f"ALTA PRIORIDAD: Fortalecer marco normativo con: {high_norms}"
            )

        if missing_norms and len(missing_norms) > 5:
            recommendations.append(
                "Se recomienda realizar una revisión exhaustiva del marco normativo vigente "
                "para garantizar coherencia con la legislación nacional."
            )

        # Contextual recommendations
        if context.get("is_pdet") and any("893" in g.norm_id for g in missing_norms):
            recommendations.append(
                "Como municipio PDET, es fundamental incluir el Decreto 893 de 2017 "
                "que regula los Programas de Desarrollo con Enfoque Territorial."
            )

        if not recommendations:
            recommendations.append(
                "El marco normativo citado es completo y cumple con los estándares requeridos."
            )

        return recommendations


# Convenience function


def validate_normative_compliance(
    plan_id: str,
    policy_area: str,
    cited_norms: list[str],
    context: dict[str, Any] | None = None,
) -> ValidationResult:
    """
    Convenience function to validate normative compliance.

    Args:
        plan_id: Plan identifier
        policy_area: Policy area code (PA01-PA10)
        cited_norms: List of norm IDs cited
        context: Optional context

    Returns:
        ValidationResult
    """
    validator = NormativeComplianceValidator()
    return validator.validate(plan_id, policy_area, cited_norms, context)


__all__ = [
    "NormativeComplianceValidator",
    "ValidationResult",
    "NormGap",
    "validate_normative_compliance",
]
