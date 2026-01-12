"""
Normative Compliance Validator - Policy Area Mandatory Norms

This validator consumes NORMATIVE_REFERENCE signals and validates that
mandatory norms are present for each Policy Area based on empirical data
from normative_compliance.json.

Key Features:
- Validates mandatory norms per Policy Area
- Calculates penalty scores for missing norms
- Tracks compliance rates across the document
- Integrates with SignalIrrigator for signal consumption

Author: FARFAN Pipeline Team
Date: 2026-01-07
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class NormativeRequirement:
    """Represents a mandatory normative requirement for a Policy Area."""
    norm_id: str
    name: str
    penalty_if_missing: float
    farfan_questions: List[str] = field(default_factory=list)
    found: bool = False


@dataclass
class ComplianceResult:
    """Result of normative compliance validation."""
    policy_area: str
    compliant: bool
    compliance_score: float  # 0.0-1.0, with penalties applied
    mandatory_norms_found: int
    mandatory_norms_total: int
    missing_norms: List[str] = field(default_factory=list)
    penalties_applied: float = 0.0
    citation_rate: float = 0.0
    meets_threshold: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class NormativeComplianceValidator:
    """
    Validates normative compliance for Policy Areas.

    Consumes NORMATIVE_REFERENCE signals and checks if mandatory norms
    are cited according to empirical compliance data.

    Usage:
        validator = NormativeComplianceValidator()

        # Validate a single policy area
        result = validator.validate_policy_area(
            policy_area="PA01",
            detected_norms=["Ley 1257 de 2008", "CEDAW"]
        )

        # Validate from signal deliveries
        result = validator.validate_from_signals(
            policy_area="PA01",
            signal_deliveries=normative_deliveries
        )
    """

    def __init__(self, compliance_file: Optional[Path] = None):
        """
        Initialize validator with normative compliance data.

        Args:
            compliance_file: Path to normative_compliance.json. If None, uses default.
        """
        if compliance_file is None:
            compliance_file = self._default_compliance_path()

        self.compliance_file = compliance_file
        self.policy_area_requirements: Dict[str, List[NormativeRequirement]] = {}
        self.compliance_thresholds: Dict[str, float] = {}
        self.empirical_citation_rates: Dict[str, float] = {}

        # Load compliance data
        self._load_compliance_data()

        logger.info(f"NormativeComplianceValidator initialized for {len(self.policy_area_requirements)} policy areas")

    def _default_compliance_path(self) -> Path:
        """Get default path to normative_compliance.json."""
        return Path(__file__).parent.parent.parent.parent / \
               "canonic_questionnaire_central" / "_registry" / "entities" / \
               "normative_compliance.json"

    def _load_compliance_data(self) -> None:
        """Load normative compliance data from JSON file."""
        if not self.compliance_file.exists():
            logger.warning(f"Normative compliance file not found: {self.compliance_file}")
            # Load from integration_map.json as fallback
            self._load_from_integration_map()
            return

        try:
            with open(self.compliance_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            pa_requirements = data.get("policy_area_requirements", {})

            for pa_id, pa_config in pa_requirements.items():
                requirements = []
                for norm_config in pa_config.get("mandatory_norms", []):
                    requirements.append(NormativeRequirement(
                        norm_id=norm_config.get("norm_id", ""),
                        name=norm_config.get("name", ""),
                        penalty_if_missing=norm_config.get("penalty_if_missing", 0.15),
                        farfan_questions=norm_config.get("farfan_questions", [])
                    ))

                self.policy_area_requirements[pa_id] = requirements
                self.empirical_citation_rates[pa_id] = pa_config.get("empirical_citation_rate", 0.50)
                self.compliance_thresholds[pa_id] = pa_config.get("compliance_threshold", 0.70)

            logger.info(f"Loaded normative requirements for {len(self.policy_area_requirements)} policy areas")
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to load normative_compliance.json: {e}, using fallback")
            self._load_from_integration_map()

    def _load_from_integration_map(self) -> None:
        """Load normative requirements from integration_map.json as fallback."""
        integration_map_path = Path(__file__).parent.parent.parent.parent / \
                               "canonic_questionnaire_central" / "_registry" / \
                               "questions" / "integration_map.json"

        if not integration_map_path.exists():
            logger.error("Neither normative_compliance.json nor integration_map.json found")
            return

        try:
            with open(integration_map_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract from signal_type_catalog
            normative_config = data.get("signal_type_catalog", {}).get("NORMATIVE_REFERENCE", {})
            normative_mapping = normative_config.get("normative_mapping", {})
            pa_specific = normative_mapping.get("policy_area_specific", {})

            for pa_id, pa_config in pa_specific.items():
                requirements = []
                for norm_config in pa_config.get("mandatory", []):
                    requirements.append(NormativeRequirement(
                        norm_id=norm_config.get("norm_id", ""),
                        name=norm_config.get("norm_id", ""),  # Use ID as name fallback
                        penalty_if_missing=norm_config.get("penalty_if_missing", 0.30),
                        farfan_questions=norm_config.get("farfan_questions", [])
                    ))

                self.policy_area_requirements[pa_id] = requirements
                self.compliance_thresholds[pa_id] = 0.70  # Default threshold
                self.empirical_citation_rates[pa_id] = 0.50  # Default rate

            logger.info(f"Loaded {len(self.policy_area_requirements)} policy areas from integration_map.json")
        except Exception as e:
            logger.error(f"Failed to load from integration_map.json: {e}")

    def validate_policy_area(
        self,
        policy_area: str,
        detected_norms: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Validate normative compliance for a policy area.

        Args:
            policy_area: Policy area ID (e.g., "PA01")
            detected_norms: List of detected norm strings
            metadata: Optional additional metadata

        Returns:
            ComplianceResult with validation details
        """
        if policy_area not in self.policy_area_requirements:
            logger.warning(f"No requirements defined for {policy_area}")
            return ComplianceResult(
                policy_area=policy_area,
                compliant=True,  # No requirements = pass
                compliance_score=1.0,
                mandatory_norms_found=0,
                mandatory_norms_total=0,
                metadata={"warning": "No requirements defined"}
            )

        requirements = self.policy_area_requirements[policy_area]
        threshold = self.compliance_thresholds.get(policy_area, 0.70)
        empirical_rate = self.empirical_citation_rates.get(policy_area, 0.50)

        # Normalize detected norms for matching
        detected_normalized = {self._normalize_norm(norm) for norm in detected_norms}

        # Check each requirement
        missing_norms = []
        total_penalty = 0.0
        found_count = 0

        for req in requirements:
            norm_normalized = self._normalize_norm(req.name)

            # Check if norm is present
            if any(norm_normalized in detected or detected in norm_normalized
                   for detected in detected_normalized):
                req.found = True
                found_count += 1
            else:
                req.found = False
                missing_norms.append(req.name)
                total_penalty += req.penalty_if_missing

        # Calculate compliance score (1.0 - penalties)
        compliance_score = max(0.0, 1.0 - total_penalty)

        # Calculate citation rate
        citation_rate = found_count / len(requirements) if requirements else 1.0

        # Check if meets threshold
        meets_threshold = compliance_score >= threshold

        return ComplianceResult(
            policy_area=policy_area,
            compliant=meets_threshold,
            compliance_score=compliance_score,
            mandatory_norms_found=found_count,
            mandatory_norms_total=len(requirements),
            missing_norms=missing_norms,
            penalties_applied=total_penalty,
            citation_rate=citation_rate,
            meets_threshold=meets_threshold,
            metadata={
                "threshold": threshold,
                "empirical_citation_rate": empirical_rate,
                "above_empirical": citation_rate >= empirical_rate,
                **(metadata or {})
            }
        )

    def validate_from_signals(
        self,
        policy_area: str,
        signal_deliveries: List[Any],  # List[SignalDelivery]
        metadata: Optional[Dict[str, Any]] = None
    ) -> ComplianceResult:
        """
        Validate normative compliance from signal deliveries.

        Args:
            policy_area: Policy area ID
            signal_deliveries: List of SignalDelivery objects with NORMATIVE_REFERENCE signals
            metadata: Optional additional metadata

        Returns:
            ComplianceResult with validation details
        """
        # Extract detected norms from signal deliveries
        detected_norms = set()

        for delivery in signal_deliveries:
            if delivery.signal_type == "NORMATIVE_REFERENCE":
                payload = delivery.signal_payload
                matches = payload.get("matches", [])

                for match in matches:
                    # Get norm text or ID
                    norm_text = match.get("text") or match.get("norm_id") or match.get("title")
                    if norm_text:
                        detected_norms.add(norm_text)

        return self.validate_policy_area(
            policy_area=policy_area,
            detected_norms=list(detected_norms),
            metadata={
                "signal_count": len(signal_deliveries),
                "detected_count": len(detected_norms),
                **(metadata or {})
            }
        )

    def _normalize_norm(self, norm_str: str) -> str:
        """Normalize norm string for matching."""
        return norm_str.lower().strip()

    def get_requirements_for_policy_area(self, policy_area: str) -> List[NormativeRequirement]:
        """Get normative requirements for a policy area."""
        return self.policy_area_requirements.get(policy_area, [])

    def get_all_policy_areas(self) -> List[str]:
        """Get list of all policy areas with requirements."""
        return list(self.policy_area_requirements.keys())

    def validate_all_policy_areas(
        self,
        detected_norms_by_pa: Dict[str, List[str]]
    ) -> Dict[str, ComplianceResult]:
        """
        Validate all policy areas in batch.

        Args:
            detected_norms_by_pa: Dict mapping PA IDs to detected norms

        Returns:
            Dict mapping PA IDs to ComplianceResult
        """
        results = {}

        for pa_id in self.get_all_policy_areas():
            detected = detected_norms_by_pa.get(pa_id, [])
            results[pa_id] = self.validate_policy_area(pa_id, detected)

        return results

    def generate_compliance_report(
        self,
        results: Dict[str, ComplianceResult]
    ) -> Dict[str, Any]:
        """
        Generate a compliance report from validation results.

        Args:
            results: Dict of PA ID to ComplianceResult

        Returns:
            Dict with aggregated compliance metrics
        """
        total_pas = len(results)
        compliant_pas = sum(1 for r in results.values() if r.compliant)
        total_norms_expected = sum(r.mandatory_norms_total for r in results.values())
        total_norms_found = sum(r.mandatory_norms_found for r in results.values())

        avg_compliance_score = (
            sum(r.compliance_score for r in results.values()) / total_pas
            if total_pas > 0
            else 0.0
        )

        avg_citation_rate = (
            sum(r.citation_rate for r in results.values()) / total_pas
            if total_pas > 0
            else 0.0
        )

        return {
            "total_policy_areas": total_pas,
            "compliant_policy_areas": compliant_pas,
            "compliance_rate": compliant_pas / total_pas if total_pas > 0 else 0.0,
            "average_compliance_score": avg_compliance_score,
            "average_citation_rate": avg_citation_rate,
            "total_norms_expected": total_norms_expected,
            "total_norms_found": total_norms_found,
            "norm_coverage": total_norms_found / total_norms_expected if total_norms_expected > 0 else 0.0,
            "non_compliant_policy_areas": [
                {"pa_id": pa_id, "missing_norms": result.missing_norms}
                for pa_id, result in results.items()
                if not result.compliant
            ]
        }


__all__ = [
    'NormativeComplianceValidator',
    'NormativeRequirement',
    'ComplianceResult',
]
