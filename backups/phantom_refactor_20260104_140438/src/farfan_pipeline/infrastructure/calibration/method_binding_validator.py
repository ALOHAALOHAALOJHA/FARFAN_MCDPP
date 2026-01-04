"""
Method Binding Validator
========================
Validates that method bindings satisfy TYPE-specific epistemic requirements.

DESIGN PATTERN: Chain of Responsibility
- Multiple validators chained together
- Each validator can PASS, WARN, or FAIL
- Any FAIL stops the chain

INVARIANTS:
- INV-BIND-001: Layer ratios must be within TYPE-specified bounds
- INV-BIND-002: Mandatory patterns must have at least one matching method
- INV-BIND-003: Prohibited operations must not appear in any method
- INV-BIND-004: N2.requires ⊆ N1.provides (dependency chain)
"""
from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Callable

from .calibration_core import ValidationError
from .type_defaults import get_type_defaults, is_operation_prohibited

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity of validation result."""

    PASS = auto()
    WARNING = auto()
    FATAL = auto()


@dataclass(frozen=True)
class ValidationResult:
    """Single validation check result."""

    check_name: str
    severity: ValidationSeverity
    message: str
    details: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class MethodBinding:
    """Represents a method bound to a contract."""

    method_id: str  # e.g., "BayesianNumericalAnalyzer.evaluate_policy_metric"
    level: str  # N1-EMP, N2-INF, N3-AUD
    provides: frozenset[str]  # What this method provides
    requires: frozenset[str]  # What this method requires
    fusion_behavior: str  # additive, multiplicative, veto_gate


@dataclass
class MethodBindingSet:
    """Complete set of method bindings for a contract."""

    contract_id: str
    contract_type_code: str
    bindings: dict[str, list[MethodBinding]]  # level -> list of bindings

    def get_level_count(self, level: str) -> int:
        return len(self.bindings.get(level, []))

    def get_total_count(self) -> int:
        return sum(len(b) for b in self.bindings.values())

    def get_all_provides(self, level: str) -> frozenset[str]:
        """Get union of all provides from a level."""
        provides: set[str] = set()
        for binding in self.bindings.get(level, []):
            provides.update(binding.provides)
        return frozenset(provides)

    def get_all_requires(self, level: str) -> frozenset[str]:
        """Get union of all requires from a level."""
        requires: set[str] = set()
        for binding in self.bindings.get(level, []):
            requires.update(binding.requires)
        return frozenset(requires)


class EpistemicViolation(Exception):
    """Raised when epistemic constraints are violated."""

    pass


class MethodBindingValidator:
    """
    Validates method bindings against TYPE-specific requirements.

    CHAIN OF RESPONSIBILITY: Validators execute in order, first FATAL stops chain.
    """

    def __init__(self) -> None:
        self._validators: list[Callable[[MethodBindingSet], ValidationResult]] = [
            self._validate_layer_ratios,
            self._validate_mandatory_patterns,
            self._validate_prohibited_operations,
            self._validate_dependency_chain,
            self._validate_veto_coverage,
        ]

    def validate(self, binding_set: MethodBindingSet) -> list[ValidationResult]:
        """
        Run all validations on binding set.

        Returns list of all results (including PASS).
        Raises EpistemicViolation if any FATAL result.
        """
        results: list[ValidationResult] = []

        for validator in self._validators:
            result = validator(binding_set)
            results.append(result)

            if result.severity == ValidationSeverity.FATAL:
                logger.error(
                    f"FATAL validation failure: {result.check_name} - {result.message}"
                )
                raise EpistemicViolation(
                    f"Validation failed: {result.check_name}\n"
                    f"Message: {result.message}\n"
                    f"Details: {result.details}"
                )

        return results

    def _validate_layer_ratios(
        self, binding_set: MethodBindingSet
    ) -> ValidationResult:
        """INV-BIND-001: Layer ratios within bounds."""
        type_defaults = get_type_defaults(binding_set.contract_type_code)
        total = binding_set.get_total_count()

        if total == 0:
            return ValidationResult(
                check_name="layer_ratios",
                severity=ValidationSeverity.FATAL,
                message="No methods bound to contract",
            )

        n1_count = binding_set.get_level_count("N1-EMP")
        n2_count = binding_set.get_level_count("N2-INF")
        n3_count = binding_set.get_level_count("N3-AUD")

        n1_ratio = n1_count / total
        n2_ratio = n2_count / total
        n3_ratio = n3_count / total

        violations: list[str] = []
        ratios = type_defaults.epistemic_ratios

        if not ratios.n1_empirical.contains(n1_ratio):
            violations.append(
                f"N1 ratio {n1_ratio:.2f} outside "
                f"[{ratios.n1_empirical.lower}, {ratios.n1_empirical.upper}]"
            )

        if not ratios.n2_inferential.contains(n2_ratio):
            violations.append(
                f"N2 ratio {n2_ratio:.2f} outside "
                f"[{ratios.n2_inferential.lower}, {ratios.n2_inferential.upper}]"
            )

        if not ratios.n3_audit.contains(n3_ratio):
            violations.append(
                f"N3 ratio {n3_ratio:.2f} outside "
                f"[{ratios.n3_audit.lower}, {ratios.n3_audit.upper}]"
            )

        if violations:
            return ValidationResult(
                check_name="layer_ratios",
                severity=ValidationSeverity.FATAL,
                message="; ".join(violations),
                details={"n1": n1_ratio, "n2": n2_ratio, "n3": n3_ratio},
            )

        return ValidationResult(
            check_name="layer_ratios",
            severity=ValidationSeverity.PASS,
            message="Layer ratios within bounds",
            details={"n1": n1_ratio, "n2": n2_ratio, "n3": n3_ratio},
        )

    def _validate_mandatory_patterns(
        self, binding_set: MethodBindingSet
    ) -> ValidationResult:
        """INV-BIND-002: Mandatory patterns satisfied."""
        minima_path = Path(
            "artifacts/data/epistemic_inputs_v4/epistemic_minima_by_type.json"
        )

        if not minima_path.exists():
            return ValidationResult(
                check_name="mandatory_patterns",
                severity=ValidationSeverity.WARNING,
                message=f"Epistemic minima file not found: {minima_path}",
            )

        with open(minima_path, "r") as f:
            minima = json.load(f)

        type_spec = minima.get("type_specifications", {}).get(
            binding_set.contract_type_code, {}
        )
        mandatory_patterns = type_spec.get("mandatory_patterns", {})

        missing: list[str] = []
        level_map = {"N1": "N1-EMP", "N2": "N2-INF", "N3": "N3-AUD"}

        for level_short, patterns in mandatory_patterns.items():
            level_code = level_map.get(level_short, level_short)
            bindings = binding_set.bindings.get(level_code, [])
            method_ids = [b.method_id for b in bindings]

            for pattern in patterns:
                if not any(
                    re.search(pattern, mid, re.IGNORECASE) for mid in method_ids
                ):
                    missing.append(f"{level_short}: pattern '{pattern}' has no match")

        if missing:
            return ValidationResult(
                check_name="mandatory_patterns",
                severity=ValidationSeverity.FATAL,
                message="Missing mandatory patterns: " + "; ".join(missing),
                details={"missing": missing},
            )

        return ValidationResult(
            check_name="mandatory_patterns",
            severity=ValidationSeverity.PASS,
            message="All mandatory patterns satisfied",
        )

    def _validate_prohibited_operations(
        self, binding_set: MethodBindingSet
    ) -> ValidationResult:
        """INV-BIND-003: No prohibited operations."""
        violations: list[str] = []

        for level, bindings in binding_set.bindings.items():
            for binding in bindings:
                if is_operation_prohibited(
                    binding_set.contract_type_code, binding.fusion_behavior
                ):
                    violations.append(
                        f"{binding.method_id}: fusion_behavior '{binding.fusion_behavior}' "
                        f"is PROHIBITED for {binding_set.contract_type_code}"
                    )

        if violations:
            return ValidationResult(
                check_name="prohibited_operations",
                severity=ValidationSeverity.FATAL,
                message="Prohibited operations detected: " + "; ".join(violations),
                details={"violations": violations},
            )

        return ValidationResult(
            check_name="prohibited_operations",
            severity=ValidationSeverity.PASS,
            message="No prohibited operations",
        )

    def _validate_dependency_chain(
        self, binding_set: MethodBindingSet
    ) -> ValidationResult:
        """INV-BIND-004: N2.requires ⊆ N1.provides."""
        n1_provides = binding_set.get_all_provides("N1-EMP")
        n2_requires = binding_set.get_all_requires("N2-INF")

        unmet = n2_requires - n1_provides

        if unmet:
            return ValidationResult(
                check_name="dependency_chain",
                severity=ValidationSeverity.FATAL,
                message=f"N2 requires not provided by N1: {unmet}",
                details={"unmet_dependencies": list(unmet)},
            )

        return ValidationResult(
            check_name="dependency_chain",
            severity=ValidationSeverity.PASS,
            message="Dependency chain satisfied",
        )

    def _validate_veto_coverage(
        self, binding_set: MethodBindingSet
    ) -> ValidationResult:
        """All N3 methods must have veto capability."""
        n3_bindings = binding_set.bindings.get("N3-AUD", [])

        if not n3_bindings:
            return ValidationResult(
                check_name="veto_coverage",
                severity=ValidationSeverity.FATAL,
                message="No N3-AUD methods bound (veto capability required)",
            )

        non_veto = [
            b.method_id for b in n3_bindings if b.fusion_behavior != "veto_gate"
        ]

        if non_veto:
            return ValidationResult(
                check_name="veto_coverage",
                severity=ValidationSeverity.WARNING,
                message=f"N3 methods without veto_gate fusion: {non_veto}",
                details={"non_veto_methods": non_veto},
            )

        return ValidationResult(
            check_name="veto_coverage",
            severity=ValidationSeverity.PASS,
            message="All N3 methods have veto capability",
        )


__all__ = [
    "ValidationSeverity",
    "ValidationResult",
    "MethodBinding",
    "MethodBindingSet",
    "MethodBindingValidator",
    "EpistemicViolation",
]
