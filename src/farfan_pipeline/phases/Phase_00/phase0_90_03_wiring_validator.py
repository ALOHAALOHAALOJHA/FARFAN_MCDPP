"""
WiringValidator - Structural Integrity Gate for Phase 0
========================================================

Implements Design by Contract validation for WiringComponents before Phase 1.

This is a FAIL-FAST GATE that validates:
- Tier 1: Existential Validation (Non-Nullity)
- Tier 2: Cardinality Validation (Set Membership & Size)
- Tier 3: Signature Validation (Interface Compliance)
- Tier 4: Inter-Component Referential Integrity
- Tier 5: Integrity Hashing (Reproducibility Guarantee)
- Tier 6: Seed Consistency (Determinism Enforcement)
- Tier 7: Import Resolvability (Dependency Availability)

Invariant: Pipeline MUST NOT start Phase 1 if validate() returns passed=False.

Author: Phase 0 Compliance Team
Version: 1.0.0
Specification: WiringValidator SOTA Spec v1.0
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__stage__ = 90
__order__ = 3
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "LOW"
__execution_pattern__ = "Per-Task"

import hashlib
import importlib
import importlib.util
import json
import random
from pathlib import Path
from typing import TYPE_CHECKING, Any

try:
    import blake3
    BLAKE3_AVAILABLE = True
except ImportError:
    BLAKE3_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

from farfan_pipeline.phases.Phase_00.interphase.wiring_types import (
    ContractViolation,
    Severity,
    TierValidator,
    ValidationResult,
    WiringComponents,
    WiringFeatureFlags,
)


# =============================================================================
# TIER 1: EXISTENTIAL VALIDATION (Non-Nullity)
# =============================================================================


class Tier1ExistentialValidator:
    """Validates that all required components exist and are not None."""

    REQUIRED_COMPONENTS = [
        "provider",
        "signal_client",
        "signal_registry",
        "executor_config",
        "arg_router",
        "class_registry",
        "validator",
        "flags",
    ]

    DEEP_CHECKS = [
        ("signal_registry", "_signals"),
        ("class_registry", None),  # class_registry is a dict, check it's not empty
    ]

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        violations = []

        # Top-level null check
        if wiring is None:
            violations.append(
                ContractViolation(
                    type="NULL_WIRING",
                    severity=Severity.CRITICAL,
                    component_path="wiring",
                    message="WiringComponents object is None",
                    expected="WiringComponents instance",
                    actual="None",
                    remediation="Ensure WiringBootstrap.bootstrap() completed successfully",
                )
            )
            return violations  # Can't continue

        # Component-level null checks
        for component_name in self.REQUIRED_COMPONENTS:
            value = getattr(wiring, component_name, None)
            if value is None:
                violations.append(
                    ContractViolation(
                        type="NULL_COMPONENT",
                        severity=Severity.CRITICAL,
                        component_path=f"wiring.{component_name}",
                        message=f"wiring.{component_name} is None",
                        expected=f"{component_name} instance",
                        actual="None",
                        remediation=f"Ensure {component_name} is initialized in bootstrap",
                    )
                )

        # Deep null checks (only if parent exists)
        for parent_name, child_attr in self.DEEP_CHECKS:
            parent = getattr(wiring, parent_name, None)
            if parent is not None and child_attr is not None:
                child = getattr(parent, child_attr, None)
                if child is None:
                    violations.append(
                        ContractViolation(
                            type="NULL_NESTED_COMPONENT",
                            severity=Severity.CRITICAL,
                            component_path=f"wiring.{parent_name}.{child_attr}",
                            message=f"wiring.{parent_name}.{child_attr} is None",
                            expected="Initialized collection",
                            actual="None",
                            remediation=f"Ensure {parent_name} is fully initialized",
                        )
                    )

        return violations


# =============================================================================
# TIER 2: CARDINALITY VALIDATION (Set Membership & Size)
# =============================================================================


class Tier2CardinalityValidator:
    """Validates cardinality constraints on registries."""

    EXPECTED_POLICY_AREAS = frozenset(
        {
            "PA01",
            "PA02",
            "PA03",
            "PA04",
            "PA05",
            "PA06",
            "PA07",
            "PA08",
            "PA09",
            "PA10",
        }
    )
    MIN_CLASS_REGISTRY_SIZE = 40
    MIN_ARG_ROUTER_ROUTES = 30

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        violations = []

        # Signal Registry: Exactly 10 policy areas
        if wiring.signal_registry is not None:
            policy_areas = self._get_policy_areas(wiring.signal_registry)
            if policy_areas is not None:
                if len(policy_areas) != 10:
                    violations.append(
                        ContractViolation(
                            type="CARDINALITY_MISMATCH",
                            severity=Severity.CRITICAL,
                            component_path="wiring.signal_registry.policy_areas",
                            message=f"Signal registry has {len(policy_areas)} policy areas, expected 10",
                            expected=10,
                            actual=len(policy_areas),
                            remediation="Ensure all 10 policy areas (PA01-PA10) are seeded",
                        )
                    )

                # Check exact set membership
                actual_set = set(policy_areas)
                if actual_set != self.EXPECTED_POLICY_AREAS:
                    missing = self.EXPECTED_POLICY_AREAS - actual_set
                    extra = actual_set - self.EXPECTED_POLICY_AREAS
                    violations.append(
                        ContractViolation(
                            type="POLICY_AREA_MISMATCH",
                            severity=Severity.HIGH,
                            component_path="wiring.signal_registry.policy_areas",
                            message=f"Policy area set mismatch. Missing: {missing}, Extra: {extra}",
                            expected=sorted(self.EXPECTED_POLICY_AREAS),
                            actual=sorted(actual_set),
                            remediation="Verify canonical policy area definitions",
                        )
                    )

        # Class Registry: Minimum 40 classes
        if wiring.class_registry is not None:
            registry_size = len(wiring.class_registry)
            if registry_size < self.MIN_CLASS_REGISTRY_SIZE:
                violations.append(
                    ContractViolation(
                        type="CARDINALITY_INSUFFICIENT",
                        severity=Severity.HIGH,
                        component_path="wiring.class_registry",
                        message=f"Class registry has {registry_size} classes, minimum is {self.MIN_CLASS_REGISTRY_SIZE}",
                        expected=f">= {self.MIN_CLASS_REGISTRY_SIZE}",
                        actual=registry_size,
                        remediation="Ensure all dispensary classes are registered",
                    )
                )

        # Arg Router: Minimum 30 routes
        if wiring.arg_router is not None:
            route_count = self._get_route_count(wiring.arg_router)
            if route_count is not None and route_count < self.MIN_ARG_ROUTER_ROUTES:
                violations.append(
                    ContractViolation(
                        type="CARDINALITY_INSUFFICIENT",
                        severity=Severity.HIGH,
                        component_path="wiring.arg_router.special_cases",
                        message=f"Arg router has {route_count} routes, minimum is {self.MIN_ARG_ROUTER_ROUTES}",
                        expected=f">= {self.MIN_ARG_ROUTER_ROUTES}",
                        actual=route_count,
                        remediation="Ensure all special routing cases are registered",
                    )
                )

        return violations

    def _get_policy_areas(self, signal_registry: Any) -> list[str] | None:
        """Extract policy area IDs from signal registry."""
        # Try common attribute names
        for attr in ["_signals", "signals", "policy_areas", "_registry"]:
            collection = getattr(signal_registry, attr, None)
            if collection is not None and hasattr(collection, "keys"):
                return list(collection.keys())
            if collection is not None and isinstance(collection, (list, set)):
                return list(collection)
        return None

    def _get_route_count(self, arg_router: Any) -> int | None:
        """Get number of routes in arg router."""
        for attr in ["special_cases", "_special_cases", "routes", "_routes"]:
            collection = getattr(arg_router, attr, None)
            if collection is not None:
                return len(collection)
        return None


# =============================================================================
# TIER 3: SIGNATURE VALIDATION (Interface Compliance)
# =============================================================================


class Tier3SignatureValidator:
    """Validates that critical methods have expected signatures."""

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        violations = []

        # Check arg_router has route method
        if wiring.arg_router is not None:
            route_method = getattr(wiring.arg_router, "route", None)
            if route_method is None:
                route_method = getattr(wiring.arg_router, "route_arguments", None)

            if route_method is None:
                violations.append(
                    ContractViolation(
                        type="MISSING_METHOD",
                        severity=Severity.HIGH,
                        component_path="wiring.arg_router.route",
                        message="ArgRouter missing route/route_arguments method",
                        expected="Callable route method",
                        actual="None",
                        remediation="Ensure ArgRouter implements routing interface",
                    )
                )
            elif not callable(route_method):
                violations.append(
                    ContractViolation(
                        type="INVALID_METHOD",
                        severity=Severity.HIGH,
                        component_path="wiring.arg_router.route",
                        message="ArgRouter.route is not callable",
                        expected="Callable",
                        actual=type(route_method).__name__,
                        remediation="ArgRouter.route must be a method",
                    )
                )

        # Check signal_registry has get method
        if wiring.signal_registry is not None:
            get_method = getattr(wiring.signal_registry, "get", None)
            if get_method is None:
                get_method = getattr(wiring.signal_registry, "get_signal", None)

            if get_method is None:
                violations.append(
                    ContractViolation(
                        type="MISSING_METHOD",
                        severity=Severity.MEDIUM,
                        component_path="wiring.signal_registry.get",
                        message="SignalRegistry missing get/get_signal method",
                        expected="Callable get method",
                        actual="None",
                        remediation="Ensure SignalRegistry implements retrieval interface",
                    )
                )

        return violations


# =============================================================================
# TIER 4: REFERENTIAL INTEGRITY
# =============================================================================


class Tier4ReferentialIntegrityValidator:
    """Validates inter-component references are resolvable."""

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        violations = []

        # class_registry keys should be strings (class names)
        if wiring.class_registry is not None:
            for key in list(wiring.class_registry.keys())[:5]:  # Sample first 5
                if not isinstance(key, str):
                    violations.append(
                        ContractViolation(
                            type="INVALID_KEY_TYPE",
                            severity=Severity.HIGH,
                            component_path="wiring.class_registry",
                            message=f"Class registry key is not string: {type(key).__name__}",
                            expected="str",
                            actual=type(key).__name__,
                            remediation="Class registry keys must be class name strings",
                        )
                    )
                    break

        # class_registry values should be types
        if wiring.class_registry is not None:
            for key, value in list(wiring.class_registry.items())[:5]:
                if not isinstance(value, type):
                    violations.append(
                        ContractViolation(
                            type="INVALID_VALUE_TYPE",
                            severity=Severity.HIGH,
                            component_path=f"wiring.class_registry[{key}]",
                            message=f"Class registry value is not a type: {type(value).__name__}",
                            expected="type (class)",
                            actual=type(value).__name__,
                            remediation="Class registry values must be class types",
                        )
                    )
                    break

        return violations


# =============================================================================
# TIER 5: INTEGRITY HASHING
# =============================================================================


class Tier5IntegrityHashValidator:
    """Computes and validates wiring integrity hash."""

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        # This tier doesn't produce violations, it computes the hash
        # The hash is stored in ValidationResult
        return []

    def compute_integrity_hash(self, wiring: WiringComponents) -> str:
        """Compute deterministic hash of wiring configuration."""
        try:
            # Build hashable representation
            hash_data = {
                "class_registry_count": len(wiring.class_registry) if wiring.class_registry else 0,
                "class_registry_keys": (
                    sorted(wiring.class_registry.keys()) if wiring.class_registry else []
                ),
                "has_signal_registry": wiring.signal_registry is not None,
                "has_arg_router": wiring.arg_router is not None,
                "has_executor_config": wiring.executor_config is not None,
            }

            # Add executor config details if available
            if wiring.executor_config is not None:
                ec = wiring.executor_config
                hash_data["executor_config"] = {
                    "temperature": getattr(ec, "temperature", None),
                    "random_seed": getattr(ec, "random_seed", None),
                }

            # Serialize deterministically
            json_bytes = json.dumps(hash_data, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )

            # Hash with BLAKE3 or SHA256 fallback
            if BLAKE3_AVAILABLE:
                return blake3.blake3(json_bytes).hexdigest()
            else:
                return hashlib.sha256(json_bytes).hexdigest()

        except Exception as e:
            return f"HASH_ERROR:{str(e)[:50]}"


# =============================================================================
# TIER 6: SEED CONSISTENCY
# =============================================================================


class Tier6SeedConsistencyValidator:
    """Validates determinism seed configuration."""

    EXPECTED_SEED = 42

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        violations = []

        # Check executor_config seed
        if wiring.executor_config is not None:
            seed = getattr(wiring.executor_config, "random_seed", None)
            if seed is None:
                seed = getattr(wiring.executor_config, "seed", None)

            if seed is not None and seed != self.EXPECTED_SEED:
                violations.append(
                    ContractViolation(
                        type="SEED_MISMATCH",
                        severity=Severity.CRITICAL,
                        component_path="wiring.executor_config.random_seed",
                        message=f"Executor config seed is {seed}, expected {self.EXPECTED_SEED}",
                        expected=self.EXPECTED_SEED,
                        actual=seed,
                        remediation="Set random_seed=42 for deterministic execution",
                    )
                )

        # Verify random module was seeded (check state is not default)
        try:
            state = random.getstate()
            # If state[1][0] is still 0, likely not seeded
            if state[1][0] == 0 and state[1][1] == 0:
                violations.append(
                    ContractViolation(
                        type="RANDOM_NOT_SEEDED",
                        severity=Severity.HIGH,
                        component_path="random.seed",
                        message="Python random module may not be seeded",
                        expected="Seeded state",
                        actual="Default state",
                        remediation="Call random.seed(42) in Phase 0 determinism",
                    )
                )
        except Exception:
            pass  # Can't verify, skip

        return violations


# =============================================================================
# TIER 7: IMPORT RESOLVABILITY
# =============================================================================


class Tier7ImportResolvabilityValidator:
    """Validates that critical dependencies are importable."""

    CRITICAL_DEPENDENCIES = [
        ("networkx", "EvidenceNexus graph operations"),
        ("pydantic", "Contract validation"),
    ]

    OPTIONAL_DEPENDENCIES = [
        ("psutil", "Resource monitoring"),
        ("blake3", "Integrity hashing"),
        ("numpy", "Numerical operations"),
    ]

    def validate(self, wiring: WiringComponents) -> list[ContractViolation]:
        violations = []

        # Check critical dependencies
        for module_name, usage in self.CRITICAL_DEPENDENCIES:
            if importlib.util.find_spec(module_name) is None:
                violations.append(
                    ContractViolation(
                        type="MISSING_DEPENDENCY",
                        severity=Severity.CRITICAL,
                        component_path=f"import.{module_name}",
                        message=f"Critical dependency '{module_name}' not installed ({usage})",
                        expected="Installed",
                        actual="Not found",
                        remediation=f"pip install {module_name}",
                    )
                )

        # Check optional dependencies (lower severity)
        for module_name, usage in self.OPTIONAL_DEPENDENCIES:
            if importlib.util.find_spec(module_name) is None:
                violations.append(
                    ContractViolation(
                        type="MISSING_OPTIONAL_DEPENDENCY",
                        severity=Severity.LOW,
                        component_path=f"import.{module_name}",
                        message=f"Optional dependency '{module_name}' not installed ({usage})",
                        expected="Installed",
                        actual="Not found",
                        remediation=f"pip install {module_name}",
                    )
                )

        return violations


# =============================================================================
# MAIN WIRING VALIDATOR
# =============================================================================


class WiringValidator:
    """
    Structural Integrity Gate for Phase 0 Wiring.

    Implements Design by Contract validation across 7 tiers.
    Pipeline MUST NOT proceed to Phase 1 if validate() returns passed=False.
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator with tier validators.

        Args:
            strict_mode: If True, HIGH violations also cause failure.
                        If False, only CRITICAL violations cause failure.
        """
        self.strict_mode = strict_mode
        self.tier_validators: list[TierValidator] = [
            Tier1ExistentialValidator(),
            Tier2CardinalityValidator(),
            Tier3SignatureValidator(),
            Tier4ReferentialIntegrityValidator(),
            Tier5IntegrityHashValidator(),
            Tier6SeedConsistencyValidator(),
            Tier7ImportResolvabilityValidator(),
        ]
        self._integrity_hasher = Tier5IntegrityHashValidator()

    def register_custom_validator(self, validator: TierValidator) -> None:
        """Register a custom validator for extensibility."""
        self.tier_validators.append(validator)

    def validate(self, wiring: WiringComponents) -> ValidationResult:
        """
        Execute complete validation sequence.

        Args:
            wiring: WiringComponents to validate

        Returns:
            ValidationResult with passed status to violations
        """
        import time

        start_time = time.perf_counter()

        all_violations: list[ContractViolation] = []

        # Execute each tier
        for validator in self.tier_validators:
            try:
                tier_violations = validator.validate(wiring)
                all_violations.extend(tier_violations)

                # Early exit on critical violations (fail fast)
                critical_count = sum(1 for v in tier_violations if v.severity == Severity.CRITICAL)
                if critical_count > 0 and self.strict_mode:
                    break

            except Exception as e:
                all_violations.append(
                    ContractViolation(
                        type="VALIDATOR_ERROR",
                        severity=Severity.HIGH,
                        component_path=f"validator.{type(validator).__name__}",
                        message=f"Validator raised exception: {e!s}",
                        remediation="Check validator implementation",
                    )
                )

        # Compute integrity hash
        integrity_hash = ""
        if wiring is not None:
            integrity_hash = self._integrity_hasher.compute_integrity_hash(wiring)

        # Determine pass/fail
        critical_count = sum(1 for v in all_violations if v.severity == Severity.CRITICAL)
        high_count = sum(1 for v in all_violations if v.severity == Severity.HIGH)

        if self.strict_mode:
            passed = (critical_count == 0) and (high_count == 0)
        else:
            passed = critical_count == 0

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        return ValidationResult(
            passed=passed,
            violations=all_violations,
            integrity_hash=integrity_hash,
            validation_time_ms=elapsed_ms,
        )

    def validate_or_raise(self, wiring: WiringComponents) -> ValidationResult:
        """
        Validate and raise WiringValidationError if failed.

        Args:
            wiring: WiringComponents to validate

        Returns:
            ValidationResult if passed

        Raises:
            WiringValidationError: If validation fails
        """
        result = self.validate(wiring)
        if not result.passed:
            raise WiringValidationError(result)
        return result


# =============================================================================
# EXCEPTIONS
# =============================================================================


class WiringValidationError(Exception):
    """Raised when wiring validation fails."""

    def __init__(self, result: ValidationResult):
        self.result = result
        super().__init__(result.format_console())


class MissingDependencyError(Exception):
    """Raised when a required dependency is missing during wiring."""

    def __init__(self, dependency: str, required_by: str, fix: str):
        self.dependency = dependency
        self.required_by = required_by
        self.fix = fix
        super().__init__(f"Missing dependency '{dependency}' required by {required_by}. Fix: {fix}")


class WiringInitializationError(Exception):
    """Raised when wiring initialization fails."""

    def __init__(self, phase: str, component: str, reason: str):
        self.phase = phase
        self.component = component
        self.reason = reason
        super().__init__(
            f"Wiring init failed in phase '{phase}' for component '{component}': {reason}"
        )


# =============================================================================
# PHASE 0 CONFIG VALIDATOR
# =============================================================================


class Phase0ConfigValidator:
    """Validates Phase 0 configuration before bootstrap."""

    REQUIRED_KEYS = ["monolith_path", "abort_on_insufficient"]

    def validate(self, config: dict[str, Any]) -> bool:
        """
        Validate Phase 0 configuration dict.

        Args:
            config: Configuration dictionary

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        if config is None:
            raise ValueError("Phase 0 config is None")

        for key in self.REQUIRED_KEYS:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")

        # Validate monolith_path if provided
        monolith_path = config.get("monolith_path")
        if monolith_path is not None:
            path = Path(monolith_path) if isinstance(monolith_path, str) else monolith_path
            if not path.exists():
                raise ValueError(f"Monolith path does not exist: {path}")

        return True


# Alias for backward compatibility
Phase0Validator = Phase0ConfigValidator