"""
Epistemic Structure Validator for FARFAN Contracts

Specification Source: episte_refact.md PARTE VII (Checklist)
Purpose: Enforce epistemological validity before contract execution

This validator implements the remediation strategy for the FARFAN Method Selection System,
addressing the critical issues identified in the deep critique:

1. N1-EMP Contamination: Enforces ontological purity
2. N2-INF Under-Representation: Ensures TYPE-specific layer ratios
3. N3-AUD Sovereignty Deficit: Implements terminal verdict mode
4. Fusion Strategy Misapplication: Validates type-aware fusion
5. Cross-Question Homogeneity: Enforces method diversity

Author: F.A.R.F.A.N Epistemic Remediation Team
Version: 1.0.0
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class ViolationSeverity(Enum):
    """Severity levels for epistemic violations"""
    FATAL = auto()  # Contract must be regenerated or aborted
    WARNING = auto()  # Logged but execution continues


class EpistemicValidationError(Exception):
    """Raised when fatal epistemic violations are detected"""

    def __init__(self, code: str, violations: list[str], message: str):
        self.code = code
        self.violations = violations
        self.message = message
        super().__init__(f"[{code}] {message}: {violations}")


@dataclass
class ValidationResult:
    """Result of epistemic validation"""
    is_valid: bool
    violations: list[dict] = field(default_factory=list)
    warnings: list[dict] = field(default_factory=list)
    severity: ViolationSeverity = ViolationSeverity.WARNING

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "violations": self.violations,
            "warnings": self.warnings,
            "severity": self.severity.name
        }


class EpistemicStructureValidator:
    """
    Validates epistemic structure of FARFAN contracts against canonical specifications.

    Loads configuration from artifacts/data/methods/ and enforces rules from episte_refact.md
    """

    def __init__(self, config_base_path: str | None = None):
        """
        Initialize validator with configuration files.

        Args:
            config_base_path: Base path for configuration files
        """
        if config_base_path is None:
            # Default to artifacts/data/methods/
            config_base_path = str(
                Path(__file__).parent.parent.parent / "artifacts" / "data" / "methods"
            )

        self.config_path = Path(config_base_path)

        # Load configuration files
        self.n1_subtypes = self._load_config("n1_subtype_classification.json")
        self.epistemic_minima = self._load_config("epistemic_minima_by_type.json")
        self.n3_verdict = self._load_config("n3_terminal_verdict_config.json")
        self.fusion_validation = self._load_config("fusion_strategy_validation.json")
        self.diversity_constraints = self._load_config("diversity_constraints.json")

        self.logger = logging.getLogger(self.__class__.__name__)

    def _load_config(self, filename: str) -> dict:
        """Load configuration JSON file"""
        config_path = self.config_path / filename
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file not found: {config_path}")
            return {}
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {filename}: {e}")
            return {}

    def validate_contract(
        self,
        contract: dict,
        terminal_verdict_mode: bool = True
    ) -> ValidationResult:
        """
        Validate complete contract epistemic structure.

        Args:
            contract: Contract dictionary to validate
            terminal_verdict_mode: If True, N3 violations are fatal

        Returns:
            ValidationResult with violations and warnings
        """
        violations = []
        warnings = []

        # Extract contract metadata
        question_type = contract.get("type", "")
        base_slot = contract.get("base_slot", "UNKNOWN")
        methods = contract.get("methods", [])

        # 1. Validate N1 subtype classification
        n1_result = self._validate_n1_subtypes(methods)
        violations.extend(n1_result["violations"])
        warnings.extend(n1_result["warnings"])

        # 2. Validate TYPE-specific epistemic minima
        minima_result = self._validate_epistemic_minima(question_type, methods)
        violations.extend(minima_result["violations"])
        warnings.extend(minima_result["warnings"])

        # 3. Validate N3 terminal verdict (fatal if terminal_verdict_mode enabled)
        n3_result = self._validate_n3_authority(question_type, methods)
        if terminal_verdict_mode:
            violations.extend(n3_result["violations"])
        else:
            warnings.extend(n3_result["violations"])
        warnings.extend(n3_result["warnings"])

        # 4. Validate fusion strategy
        fusion_result = self._validate_fusion_strategy(question_type, methods)
        violations.extend(fusion_result["violations"])
        warnings.extend(fusion_result["warnings"])

        # 5. Validate method diversity
        diversity_result = self._validate_method_diversity(question_type, methods)
        warnings.extend(diversity_result["warnings"])

        # Determine overall severity
        has_fatal = any(
            v.get("severity") == "FATAL" or "N3" in v.get("layer", "")
            for v in violations
        )
        severity = ViolationSeverity.FATAL if has_fatal else ViolationSeverity.WARNING

        is_valid = len(violations) == 0

        return ValidationResult(
            is_valid=is_valid,
            violations=violations,
            warnings=warnings,
            severity=severity
        )

    def _validate_n1_subtypes(self, methods: list) -> dict:
        """Validate N1 methods are not contaminated by model state"""
        violations = []
        warnings = []

        n1_methods = [m for m in methods if m.get("layer") == "N1-EMP"]

        for method in n1_methods:
            method_id = method.get("method_id", "")

            # Check for rejection patterns
            for pattern in self.n1_subtypes.get("n1_rejection_criteria", {}).get("reject_patterns", []):
                if re.search(pattern, method_id, re.IGNORECASE):
                    violations.append({
                        "layer": "N1",
                        "method": method_id,
                        "violation": f"Method matches N1 rejection pattern: {pattern}",
                        "severity": "FATAL",
                        "correct_action": "Reclassify as N2-INF or N3-AUD",
                        "specification": "episte_refact.md Section 2.2"
                    })

            # Check for N1b-CTX patterns (model state, not observation)
            for pattern in self.n1_subtypes.get("n1b_ctx_criteria", {}).get("valid_patterns", []):
                if re.search(pattern, method_id, re.IGNORECASE):
                    warnings.append({
                        "layer": "N1",
                        "method": method_id,
                        "warning": f"Method is N1b-CTX (model state), not N1a-OBS (observation)",
                        "penalty": "0.6 confidence multiplier",
                        "specification": "episte_refact.md Section 2.2"
                    })

        return {"violations": violations, "warnings": warnings}

    def _validate_epistemic_minima(self, question_type: str, methods: list) -> dict:
        """Validate TYPE-specific epistemic requirements"""
        violations = []
        warnings = []

        if question_type not in self.epistemic_minima.get("type_specifications", {}):
            warnings.append({
                "type": question_type,
                "warning": f"Unknown TYPE {question_type} - cannot validate epistemic minima"
            })
            return {"violations": violations, "warnings": warnings}

        type_spec = self.epistemic_minima["type_specifications"][question_type]
        mandatory_patterns = type_spec.get("mandatory_patterns", {})

        # Check each layer for mandatory patterns
        for layer, patterns in mandatory_patterns.items():
            layer_methods = [
                m for m in methods
                if m.get("layer", "").upper().replace("-", "_") == f"N{layer[1]}_{'EMP' if layer == 'N1' else 'INF' if layer == 'N2' else 'AUD'}"
            ]

            # Check if any method matches mandatory pattern
            pattern_found = False
            for method in layer_methods:
                method_id = method.get("method_id", "")
                if any(re.search(pattern, method_id, re.IGNORECASE) for pattern in patterns):
                    pattern_found = True
                    break

            if not pattern_found:
                violations.append({
                    "layer": layer,
                    "type": question_type,
                    "violation": f"Missing required pattern from {patterns}",
                    "severity": "FATAL" if layer == "N3" else "WARNING",
                    "specification": "episte_refact.md Section 1.1"
                })

        return {"violations": violations, "warnings": warnings}

    def _validate_n3_authority(self, question_type: str, methods: list) -> dict:
        """Validate N3 terminal verdict authority"""
        violations = []
        warnings = []

        if question_type not in self.n3_verdict.get("n3_veto_conditions", {}):
            return {"violations": violations, "warnings": warnings}

        veto_condition = self.n3_verdict["n3_veto_conditions"][question_type]
        n3_methods = [m for m in methods if m.get("layer", "") == "N3-AUD"]

        # Check for fatal violation patterns
        fatal_patterns = self.n3_verdict.get("fatal_violation_patterns", {}).get("patterns", [])

        for pattern in fatal_patterns:
            pattern_match = any(
                re.search(pattern, m.get("method_id", ""), re.IGNORECASE)
                for m in n3_methods
            )
            if not pattern_match:
                violations.append({
                    "layer": "N3",
                    "type": question_type,
                    "violation": f"N3 missing method matching fatal pattern: {pattern}",
                    "severity": "FATAL",
                    "action": "REGENERATE_CONTRACT",
                    "specification": "episte_refact.md PARTE V Section 5.2"
                })

        return {"violations": violations, "warnings": warnings}

    def _validate_fusion_strategy(self, question_type: str, methods: list) -> dict:
        """Validate fusion strategy matches TYPE and output type"""
        violations = []
        warnings = []

        if question_type not in self.fusion_validation.get("type_fusion_strategies", {}):
            return {"violations": violations, "warnings": warnings}

        type_strategy = self.fusion_validation["type_fusion_strategies"][question_type]
        prohibited_combinations = type_strategy.get("prohibited_combinations", [])

        for method in methods:
            layer = method.get("layer", "")
            merge_behavior = method.get("merge_behavior", "concat")

            # Check against prohibited combinations
            for prohibited in prohibited_combinations:
                if prohibited["layer"] == layer and prohibited["merge"] == merge_behavior:
                    violations.append({
                        "layer": layer,
                        "method": method.get("method_id", ""),
                        "violation": f"Invalid merge_strategy '{merge_behavior}' for {question_type}",
                        "rationale": prohibited.get("rationale", ""),
                        "severity": "FATAL",
                        "correction": f"Use {type_strategy.get(f'{layer}_merge_strategy', 'unknown')} instead",
                        "specification": "episte_refact.md PARTE III Section 3.2"
                    })

        return {"violations": violations, "warnings": warnings}

    def _validate_method_diversity(self, question_type: str, methods: list) -> dict:
        """Validate method diversity prevents ontological flattening"""
        warnings = []

        if question_type not in self.diversity_constraints.get("type_method_profiles", {}):
            return {"violations": [], "warnings": warnings}

        type_profile = self.diversity_constraints["type_method_profiles"][question_type]

        # Check for excluded methods
        for layer in ["n1", "n2", "n3"]:
            excluded = type_profile.get(f"preferred_{layer}_methods", {}).get("excluded_patterns", [])
            layer_name = f"N{layer[1].upper()}-{'EMP' if layer == 'n1' else 'INF' if layer == 'n2' else 'AUD'}"

            for method in methods:
                if method.get("layer", "") == layer_name:
                    method_id = method.get("method_id", "")
                    for pattern in excluded:
                        if re.search(pattern, method_id, re.IGNORECASE):
                            warnings.append({
                                "layer": layer_name,
                                "method": method_id,
                                "warning": f"Method matches excluded pattern for {question_type}: {pattern}",
                                "rationale": f"TYPE_{question_type} should use {question_type}-specific methods",
                                "specification": "episte_refact.md Section 1.1"
                            })

        return {"violations": [], "warnings": warnings}

    def validate_and_regenerate(
        self,
        contract: dict,
        regenerate_func: callable,
        max_attempts: int = 3
    ) -> dict:
        """
        Validate contract and regenerate if needed.

        Args:
            contract: Initial contract to validate
            regenerate_func: Function to regenerate contract with constraints
            max_attempts: Maximum regeneration attempts

        Returns:
            Validated contract (may be regenerated)

        Raises:
            EpistemicValidationError: If max attempts exceeded or fatal unfixable violation
        """
        for attempt in range(max_attempts):
            result = self.validate_contract(contract)

            if result.is_valid:
                self.logger.info(f"Contract validated successfully on attempt {attempt + 1}")
                return contract

            # Check for fatal violations
            fatal_violations = [v for v in result.violations if v.get("severity") == "FATAL"]

            # Check if any violation is unfixable
            unfixable = any(
                "N3" in v.get("layer", "") and "missing" in v.get("violation", "").lower()
                for v in fatal_violations
            )

            if unfixable:
                raise EpistemicValidationError(
                    code=f"ABORT-{contract.get('base_slot', 'UNKNOWN')}-EPISTEMIC",
                    violations=[v.get("violation", "") for v in fatal_violations],
                    message="N3 terminal verdict: Contract epistemically invalid and cannot be auto-fixed"
                )

            # Attempt regeneration with constraints
            self.logger.warning(
                f"Contract validation failed on attempt {attempt + 1}. "
                f"Regenerating with {len(fatal_violations)} constraints."
            )

            contract = regenerate_func(contract, result.violations)

        raise EpistemicValidationError(
            code=f"ABORT-{contract.get('base_slot', 'UNKNOWN')}-MAX_ATTEMPTS",
            violations=["Max regeneration attempts exceeded"],
            message="Could not validate contract after maximum attempts"
        )


def main():
    """CLI entry point for epistemic validation"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="Validate FARFAN contract epistemic structure"
    )
    parser.add_argument(
        "contract_file",
        type=str,
        help="Path to contract JSON file"
    )
    parser.add_argument(
        "--terminal-verdict",
        action="store_true",
        help="Enable N3 terminal verdict mode (fatal violations)"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        default=None,
        help="Path to configuration files directory"
    )

    args = parser.parse_args()

    # Load contract
    with open(args.contract_file, "r") as f:
        contract = json.load(f)

    # Validate
    validator = EpistemicStructureValidator(args.config_path)
    result = validator.validate_contract(contract, args.terminal_verdict)

    # Output results
    print(json.dumps(result.to_dict(), indent=2))

    # Exit with error code if invalid
    sys.exit(0 if result.is_valid else 1)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
