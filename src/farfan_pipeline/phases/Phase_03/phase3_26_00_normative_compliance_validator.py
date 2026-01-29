"""Phase 3 Normative Compliance Validator

Validates normative references against empirical baseline from corpus_empirico_normatividad.json.
Implements CC_COHERENCIA_NORMATIVA scoring by checking mandatory norms per Policy Area.

Key Functions:
- validate_normative_compliance: Check if mandatory norms are cited
- calculate_compliance_score: Compute score = 1.0 - SUM(penalties)
- get_contextual_norms: Apply contextual validation rules (PDET, ethnic, coastal)

EMPIRICAL BASELINE: 14 PDT Colombia 2024-2027
SOURCE: canonic_questionnaire_central/_registry/entities/normative_compliance.json
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 3
__stage__ = 10
__order__ = 5
__author__ = "F.A.R.F.A.N Core Team - Empirical Corpus Integration"
__created__ = "2026-01-12"
__modified__ = "2026-01-12"
__criticality__ = "HIGH"
__execution_pattern__ = "On-Demand"

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

__all__ = [
    "NormativeComplianceValidator",
    "load_normative_compliance_corpus",
    "validate_policy_area_compliance",
]

# =============================================================================
# CORPUS LOADING
# =============================================================================


def load_normative_compliance_corpus(corpus_path: Path | str | None = None) -> dict[str, Any]:
    """Load normative compliance corpus from registry.

    Args:
        corpus_path: Optional path to normative_compliance.json.
                    Defaults to canonic_questionnaire_central/_registry/entities/

    Returns:
        Parsed JSON corpus with mandatory norms per Policy Area

    Raises:
        FileNotFoundError: If corpus file not found
        json.JSONDecodeError: If corpus file is malformed
    """
    if corpus_path is None:
        # Default path: canonic_questionnaire_central/_registry/entities/normative_compliance.json
        # Try multiple potential repository root locations
        current_file = Path(__file__).resolve()

        # Try different levels of parent directories
        for parent_level in [4, 5, 3]:
            try:
                repo_root = current_file.parents[parent_level]
                potential_path = (
                    repo_root
                    / "canonic_questionnaire_central"
                    / "_registry"
                    / "entities"
                    / "normative_compliance.json"
                )
                if potential_path.exists():
                    corpus_path = potential_path
                    break
            except (IndexError, OSError):
                continue

        # If still None, try working directory
        if corpus_path is None:
            cwd_path = Path.cwd() / "canonic_questionnaire_central" / "_registry" / "entities" / "normative_compliance.json"
            if cwd_path.exists():
                corpus_path = cwd_path
            else:
                # Last resort: use parent[4] and let the FileNotFoundError happen below
                repo_root = current_file.parents[4]
                corpus_path = (
                    repo_root
                    / "canonic_questionnaire_central"
                    / "_registry"
                    / "entities"
                    / "normative_compliance.json"
                )

    corpus_path = Path(corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(f"Normative compliance corpus not found: {corpus_path}")

    logger.info(f"Loading normative compliance corpus from: {corpus_path}")

    with corpus_path.open("r", encoding="utf-8") as f:
        corpus = json.load(f)

    logger.info(
        f"Loaded normative compliance corpus v{corpus.get('normative_mapping_version', 'unknown')} "
        f"from {corpus.get('source', 'unknown')}"
    )

    return corpus


# =============================================================================
# NORMATIVE COMPLIANCE VALIDATOR
# =============================================================================


class NormativeComplianceValidator:
    """Validates normative references against empirical baseline.

    Implements CC_COHERENCIA_NORMATIVA cross-cutting theme scorer.

    Attributes:
        corpus: Loaded normative compliance corpus
        mandatory_norms_by_pa: Mandatory norms per Policy Area
        universal_norms: Universal mandatory norms (apply to all PAs)
        contextual_rules: Contextual validation rules (PDET, ethnic, coastal)
    """

    def __init__(self, corpus_path: Path | str | None = None):
        """Initialize validator with normative compliance corpus.

        Args:
            corpus_path: Optional path to normative_compliance.json
        """
        self.corpus = load_normative_compliance_corpus(corpus_path)
        self.mandatory_norms_by_pa = self.corpus.get("mandatory_norms_by_policy_area", {})
        self.universal_norms = self.corpus.get("universal_mandatory_norms", [])
        self.contextual_rules = self.corpus.get("contextual_validation_rules", {})
        self.scoring_algorithm = self.corpus.get("scoring_algorithm", {})

        logger.info(
            f"NormativeComplianceValidator initialized: "
            f"{len(self.mandatory_norms_by_pa)} Policy Areas, "
            f"{len(self.universal_norms)} universal norms, "
            f"{len(self.contextual_rules)} contextual rules"
        )

    def get_mandatory_norms_for_policy_area(
        self,
        policy_area: str,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Get mandatory norms for a Policy Area.

        Args:
            policy_area: Policy Area ID (e.g., "PA01_mujeres_genero")
            context: Optional context dict with keys:
                     - is_pdet_municipality: bool
                     - ethnic_population_percentage: float
                     - has_coastal_zone: bool

        Returns:
            List of mandatory norm dicts with fields:
            - norm_id: str
            - name: str
            - reason: str
            - penalty_if_missing: float
        """
        mandatory_norms = []

        # 1. Universal mandatory norms (apply to all PAs)
        mandatory_norms.extend(self.universal_norms)

        # 2. Policy Area specific mandatory norms
        pa_data = self.mandatory_norms_by_pa.get(policy_area, {})
        pa_mandatory = pa_data.get("mandatory", [])
        mandatory_norms.extend(pa_mandatory)

        # 3. Contextual norms (PDET, ethnic, coastal)
        if context:
            contextual_norms = self._get_contextual_norms(context)
            mandatory_norms.extend(contextual_norms)

        return mandatory_norms

    def _get_contextual_norms(self, context: dict[str, Any]) -> list[dict[str, Any]]:
        """Get contextual mandatory norms based on municipality characteristics.

        Args:
            context: Context dict with:
                     - is_pdet_municipality: bool
                     - ethnic_population_percentage: float
                     - has_coastal_zone: bool

        Returns:
            List of additional mandatory norms
        """
        contextual_norms = []

        # PDET municipalities
        if context.get("is_pdet_municipality"):
            pdet_rule = self.contextual_rules.get("pdet_municipalities", {})
            additional = pdet_rule.get("additional_mandatory", [])
            contextual_norms.extend(additional)
            logger.debug(f"Added {len(additional)} PDET contextual norms")

        # Ethnic territories (>10% indigenous or afro)
        ethnic_pct = context.get("ethnic_population_percentage", 0.0)
        if ethnic_pct > 10.0:
            ethnic_rule = self.contextual_rules.get("ethnic_territories", {})
            additional = ethnic_rule.get("additional_mandatory", [])
            contextual_norms.extend(additional)
            logger.debug(f"Added {len(additional)} ethnic territory norms (population={ethnic_pct:.1f}%)")

        # Coastal municipalities
        if context.get("has_coastal_zone"):
            coastal_rule = self.contextual_rules.get("coastal_municipalities", {})
            additional = coastal_rule.get("additional_mandatory", [])
            contextual_norms.extend(additional)
            logger.debug(f"Added {len(additional)} coastal norms")

        return contextual_norms

    def validate_compliance(
        self,
        policy_area: str,
        extracted_norms: list[str],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Validate normative compliance for a Policy Area.

        Args:
            policy_area: Policy Area ID (e.g., "PA01_mujeres_genero")
            extracted_norms: List of norm IDs extracted from the plan
                            (e.g., ["Ley 1257 de 2008", "Ley 1448 de 2011"])
            context: Optional context for contextual validation rules

        Returns:
            Compliance result dict with:
            - score: float (0.0-1.0) computed as 1.0 - SUM(penalties)
            - quality_level: str (EXCELENTE/BUENO/ACEPTABLE/DEFICIENTE)
            - missing_norms: list of missing mandatory norms with penalties
            - total_penalty: float (sum of all penalties)
            - cited_norms: list of cited mandatory norms
            - recommendation: str (actionable feedback)
        """
        # Get mandatory norms for this PA (including contextual)
        mandatory_norms = self.get_mandatory_norms_for_policy_area(policy_area, context)

        # Normalize extracted norms for matching
        extracted_norms_normalized = {self._normalize_norm_id(n) for n in extracted_norms}

        missing_norms = []
        cited_norms = []
        total_penalty = 0.0

        for norm in mandatory_norms:
            norm_id = norm.get("norm_id", "")
            norm_id_normalized = self._normalize_norm_id(norm_id)

            if norm_id_normalized in extracted_norms_normalized:
                cited_norms.append(
                    {
                        "norm_id": norm_id,
                        "name": norm.get("name", ""),
                        "reason": norm.get("reason", ""),
                    }
                )
            else:
                penalty = norm.get("penalty_if_missing", 0.2)
                total_penalty += penalty
                missing_norms.append(
                    {
                        "norm_id": norm_id,
                        "name": norm.get("name", ""),
                        "penalty": penalty,
                        "severity": self._classify_penalty_severity(penalty),
                        "reason": norm.get("reason", ""),
                    }
                )

        # Calculate score: 1.0 - SUM(penalties)
        score = max(0.0, 1.0 - total_penalty)

        # Determine quality level
        quality_level = self._determine_quality_level(score)

        # Generate recommendation
        recommendation = self._generate_recommendation(policy_area, missing_norms)

        result = {
            "policy_area": policy_area,
            "score": score,
            "quality_level": quality_level,
            "missing_norms": missing_norms,
            "cited_norms": cited_norms,
            "total_penalty": total_penalty,
            "total_mandatory_norms": len(mandatory_norms),
            "total_cited": len(cited_norms),
            "total_missing": len(missing_norms),
            "recommendation": recommendation,
        }

        logger.info(
            f"Normative compliance for {policy_area}: "
            f"score={score:.3f}, quality={quality_level}, "
            f"cited={len(cited_norms)}/{len(mandatory_norms)}, "
            f"penalty={total_penalty:.3f}"
        )

        return result

    def _normalize_norm_id(self, norm_id: str) -> str:
        """Normalize norm ID for matching.

        Args:
            norm_id: Raw norm ID (e.g., "Ley 1257 de 2008")

        Returns:
            Normalized norm ID (lowercase, stripped, spaces normalized)
        """
        # Normalize: lowercase, strip, collapse whitespace
        normalized = " ".join(norm_id.lower().strip().split())
        return normalized

    def _classify_penalty_severity(self, penalty: float) -> str:
        """Classify penalty severity.

        Args:
            penalty: Penalty value (0.0-1.0)

        Returns:
            Severity level: CRITICAL/HIGH/MEDIUM/LOW
        """
        if penalty >= 0.30:
            return "CRITICAL"
        elif penalty >= 0.20:
            return "HIGH"
        elif penalty >= 0.10:
            return "MEDIUM"
        else:
            return "LOW"

    def _determine_quality_level(self, score: float) -> str:
        """Determine quality level from compliance score.

        Args:
            score: Compliance score (0.0-1.0)

        Returns:
            Quality level: EXCELENTE/BUENO/ACEPTABLE/DEFICIENTE
        """
        interpretation = self.scoring_algorithm.get("interpretation", {})

        # Parse thresholds from interpretation dict
        # Format: {"EXCELENTE": ">= 0.90", "BUENO": "0.75 - 0.89", ...}
        excelente_threshold = 0.90
        bueno_threshold = 0.75
        aceptable_threshold = 0.60

        if score >= excelente_threshold:
            return "EXCELENTE"
        elif score >= bueno_threshold:
            return "BUENO"
        elif score >= aceptable_threshold:
            return "ACEPTABLE"
        else:
            return "DEFICIENTE"

    def _generate_recommendation(self, policy_area: str, missing_norms: list[dict[str, Any]]) -> str:
        """Generate actionable recommendation based on missing norms.

        Args:
            policy_area: Policy Area ID
            missing_norms: List of missing mandatory norms

        Returns:
            Actionable recommendation string
        """
        if not missing_norms:
            return f"Cumplimiento normativo excelente para {policy_area}. Todas las normas obligatorias citadas."

        # Sort missing norms by severity (CRITICAL first)
        missing_sorted = sorted(missing_norms, key=lambda n: n["penalty"], reverse=True)

        critical = [n for n in missing_sorted if n["severity"] == "CRITICAL"]
        high = [n for n in missing_sorted if n["severity"] == "HIGH"]

        recommendation_parts = []

        if critical:
            critical_ids = ", ".join([n["norm_id"] for n in critical])
            recommendation_parts.append(f"🔴 CRÍTICO: Debe incluir {critical_ids}")

        if high:
            high_ids = ", ".join([n["norm_id"] for n in high])
            recommendation_parts.append(f"⚠️ IMPORTANTE: Recomienda incluir {high_ids}")

        if not critical and not high:
            # Only medium/low severity
            first_missing = missing_sorted[0]
            recommendation_parts.append(f"Recomienda incluir {first_missing['norm_id']}")

        return " | ".join(recommendation_parts)


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def validate_policy_area_compliance(
    policy_area: str,
    extracted_norms: list[str],
    context: dict[str, Any] | None = None,
    corpus_path: Path | str | None = None,
) -> dict[str, Any]:
    """Convenience function to validate compliance for a single Policy Area.

    Args:
        policy_area: Policy Area ID (e.g., "PA01_mujeres_genero")
        extracted_norms: List of norm IDs extracted from the plan
        context: Optional context for contextual validation
        corpus_path: Optional path to normative_compliance.json

    Returns:
        Compliance validation result dict
    """
    validator = NormativeComplianceValidator(corpus_path=corpus_path)
    return validator.validate_compliance(policy_area, extracted_norms, context)
