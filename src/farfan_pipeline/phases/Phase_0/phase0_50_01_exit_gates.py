"""
Phase 0 Exit Gate Validators
=============================

Implements the 7 strict exit gates defined in P00-EN v2.0 specification (extended).

Exit gates are MANDATORY checkpoints that must pass before proceeding to Phase 1.
Each gate validates a specific aspect of Phase 0 initialization.

Contract:
    Gate 1 (Bootstrap): Runtime config loaded, artifacts dir created
    Gate 2 (Input Verification): PDF and questionnaire hashed
    Gate 3 (Boot Checks): Dependencies validated (PROD: fatal, DEV: warn)
    Gate 4 (Determinism): All required seeds applied to RNGs
    Gate 5 (Questionnaire Integrity): SHA256 validation against known-good
    Gate 6 (Method Registry): Expected method count validation
    Gate 7 (Smoke Tests): Sample methods from major categories

Author: Phase 0 Compliance Team
Version: 2.0.0
Specification: P00-EN v2.0 + P1 Hardening
"""
from __future__ import annotations

# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__phase__ = 0
__stage__ = 50
__order__ = 1
__author__ = "F.A.R.F.A.N Core Team"
__created__ = "2026-01-10"
__modified__ = "2026-01-10"
__criticality__ = "CRITICAL"
__execution_pattern__ = "On-Demand"

import os
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Protocol

if TYPE_CHECKING:
    from farfan_pipeline.phases.Phase_0.phase0_10_01_runtime_config import RuntimeConfig


class Phase0Runner(Protocol):
    """Protocol defining the interface for Phase 0 runners."""

    errors: list[str]
    _bootstrap_failed: bool
    runtime_config: RuntimeConfig | None
    seed_snapshot: dict[str, int]
    input_pdf_sha256: str
    questionnaire_sha256: str
    method_executor: Any | None
    questionnaire: Any | None


@dataclass
class GateResult:
    """Result of a Phase 0 exit gate check.

    Attributes:
        passed: True if gate passed, False otherwise
        gate_name: Name of the gate (bootstrap, input_verification, boot_checks, determinism)
        gate_id: Numeric gate ID (1-4)
        reason: Human-readable failure reason (None if passed)
    """

    passed: bool
    gate_name: str
    gate_id: int
    reason: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary for logging."""
        return {
            "passed": self.passed,
            "gate_name": self.gate_name,
            "gate_id": self.gate_id,
            "reason": self.reason,
        }


def check_bootstrap_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 1: Bootstrap - Runtime configuration and initialization.

    Validates:
        - Runtime config loaded successfully
        - No bootstrap failures during __init__
        - No errors accumulated during bootstrap

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        Section 3.1 P0.0 - Bootstrap must complete without errors
    """
    gate_id = 1
    gate_name = "bootstrap"

    if runner._bootstrap_failed:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="Bootstrap failed during initialization",
        )

    if runner.runtime_config is None:
        return GateResult(
            passed=False, gate_name=gate_name, gate_id=gate_id, reason="Runtime config not loaded"
        )

    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Bootstrap errors detected: {'; '.join(runner.errors)}",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_input_verification_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 2: Input Verification - Cryptographic hashing of inputs.

    Validates:
        - Input PDF exists and is hashed (SHA-256)
        - Questionnaire exists and is hashed (SHA-256)
        - No errors during hashing

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        Section 3.2 P0.1 - Inputs must be cryptographically verified
    """
    gate_id = 2
    gate_name = "input_verification"

    pdf_hash = getattr(runner, "input_pdf_sha256", "") or ""
    if not (
        isinstance(pdf_hash, str)
        and len(pdf_hash) == 64
        and all(c in "0123456789abcdef" for c in pdf_hash.lower())
    ):
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="Input PDF not hashed with valid SHA-256",
        )

    questionnaire_hash = getattr(runner, "questionnaire_sha256", "") or ""
    if not (
        isinstance(questionnaire_hash, str)
        and len(questionnaire_hash) == 64
        and all(c in "0123456789abcdef" for c in questionnaire_hash.lower())
    ):
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="Questionnaire not hashed with valid SHA-256",
        )

    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Input verification errors: {'; '.join(runner.errors)}",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_boot_checks_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 3: Boot Checks - Dependency validation.

    Validates:
        - Boot checks executed successfully
        - No errors in PROD mode (DEV mode allows warnings)
        - Critical dependencies available

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        Section 3.3 P0.2 - Boot checks must pass in PROD, warn in DEV

    Note:
        In DEV mode, boot check warnings do NOT populate runner.errors,
        allowing the gate to pass with degraded quality.
    """
    gate_id = 3
    gate_name = "boot_checks"

    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Boot check errors: {'; '.join(runner.errors)}",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_determinism_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 4: Determinism - RNG seeding validation.

    Validates:
        - Seed snapshot created
        - Python seed applied (MANDATORY)
        - NumPy seed applied (MANDATORY)
        - Additional seeds present for advanced components
        - No errors during seeding

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        Section 3.4 P0.3 - Deterministic seeds must be applied

    Critical Seeds:
        - python: Python random module (MANDATORY)
        - numpy: NumPy random state (MANDATORY)
        - quantum: Quantum optimizer (optional if unused)
        - neuromorphic: Neuromorphic controller (optional if unused)
        - meta_learner: Meta-learner strategy (optional if unused)
    """
    gate_id = 4
    gate_name = "determinism"

    if not hasattr(runner, "seed_snapshot"):
        return GateResult(
            passed=False, gate_name=gate_name, gate_id=gate_id, reason="Seed snapshot not created"
        )

    # MANDATORY seeds (system cannot run without these)
    MANDATORY_SEEDS = ["python", "numpy"]
    missing_mandatory = [s for s in MANDATORY_SEEDS if runner.seed_snapshot.get(s) is None]

    if missing_mandatory:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Missing mandatory seeds: {missing_mandatory}",
        )

    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Determinism errors: {'; '.join(runner.errors)}",
        )

    # OPTIONAL seeds (log warning if missing, but don't fail gate)
    OPTIONAL_SEEDS = ["quantum", "neuromorphic", "meta_learner"]
    missing_optional = [s for s in OPTIONAL_SEEDS if runner.seed_snapshot.get(s) is None]

    if missing_optional:
        # Don't fail gate, but note in reason for observability
        return GateResult(
            passed=True,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Optional seeds missing (non-fatal): {missing_optional}",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_questionnaire_integrity_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 5: Questionnaire Integrity - SHA256 validation against known-good.

    Validates:
        - Questionnaire SHA256 hash computed correctly
        - Hash matches expected/configured value (from env or RuntimeConfig)
        - No corruption detected in questionnaire data

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        P1 Hardening - Questionnaire must match cryptographic fingerprint

    Note:
        Expected hash can be set via:
        - Environment variable: EXPECTED_QUESTIONNAIRE_SHA256
        - RuntimeConfig.expected_questionnaire_sha256
        - If not set, gate passes with warning (legacy compatibility)
    """
    gate_id = 5
    gate_name = "questionnaire_integrity"

    # Get expected hash from environment or RuntimeConfig
    expected_hash = os.getenv("EXPECTED_QUESTIONNAIRE_SHA256", "").strip()

    if runner.runtime_config and hasattr(runner.runtime_config, "expected_questionnaire_sha256"):
        config_hash = getattr(runner.runtime_config, "expected_questionnaire_sha256", "")
        if config_hash:
            expected_hash = config_hash

    # If no expected hash configured, pass with warning (legacy mode)
    if not expected_hash:
        return GateResult(
            passed=True,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="No expected questionnaire hash configured (legacy mode)",
        )

    # Validate format of expected hash
    if not (
        isinstance(expected_hash, str)
        and len(expected_hash) == 64
        and all(c in "0123456789abcdef" for c in expected_hash.lower())
    ):
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Invalid expected hash format: {expected_hash[:16]}...",
        )

    # Get actual questionnaire hash
    actual_hash = getattr(runner, "questionnaire_sha256", "")

    if not actual_hash:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="Questionnaire hash not computed",
        )

    # Compare hashes (case-insensitive)
    if actual_hash.lower() != expected_hash.lower():
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Questionnaire hash mismatch: expected {expected_hash[:16]}..., got {actual_hash[:16]}...",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_method_registry_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 6: Method Registry - Expected method count validation.

    Validates:
        - MethodRegistry/MethodExecutor is available
        - Expected number of methods are registered and loadable
        - Method registry statistics are accessible

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        P1 Hardening - All expected methods must be loadable

    Critical Thresholds:
        - EXPECTED_METHOD_COUNT from environment (default: 416)
        - Registered classes must match expected count
        - Failed classes count must be zero in PROD mode
    """
    gate_id = 6
    gate_name = "method_registry"

    # Get expected method count from environment or RuntimeConfig
    expected_count = int(os.getenv("EXPECTED_METHOD_COUNT", "416"))

    if runner.runtime_config and hasattr(runner.runtime_config, "expected_method_count"):
        config_count = getattr(runner.runtime_config, "expected_method_count", None)
        if config_count:
            expected_count = config_count

    # Check if method executor is available
    method_executor = getattr(runner, "method_executor", None)

    if method_executor is None:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="MethodExecutor not initialized",
        )

    # Get method registry from executor
    method_registry = None
    if hasattr(method_executor, "_method_registry"):
        method_registry = method_executor._method_registry
    elif hasattr(method_executor, "method_registry"):
        method_registry = method_executor.method_registry

    if method_registry is None:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="MethodRegistry not accessible from MethodExecutor",
        )

    # Get registry statistics
    try:
        stats = method_registry.get_stats()
    except Exception as exc:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Failed to get registry stats: {exc}",
        )

    # Validate method count
    registered_count = stats.get("total_classes_registered", 0)
    failed_count = stats.get("failed_classes", 0)

    if registered_count < expected_count:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Method count mismatch: expected {expected_count}, registered {registered_count}",
        )

    # In PROD mode, no failed classes allowed
    if runner.runtime_config and hasattr(runner.runtime_config, "mode"):
        from farfan_pipeline.phases.Phase_0.phase0_10_01_runtime_config import RuntimeMode

        if runner.runtime_config.mode == RuntimeMode.PROD and failed_count > 0:
            failed_names = stats.get("failed_class_names", [])
            return GateResult(
                passed=False,
                gate_name=gate_name,
                gate_id=gate_id,
                reason=f"PROD mode: {failed_count} failed classes: {failed_names[:3]}",
            )

    # Pass with warning if failed classes in DEV mode
    if failed_count > 0:
        return GateResult(
            passed=True,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"DEV mode: {failed_count} failed classes (non-fatal)",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_smoke_tests_gate(runner: Phase0Runner) -> GateResult:
    """
    Gate 7: Smoke Tests - Sample methods from major categories.

    Validates:
        - Ingest category: Sample method can be instantiated
        - Scoring category: Sample method can be instantiated
        - Aggregation category: Sample method can be instantiated

    Args:
        runner: Phase 0 runner instance

    Returns:
        GateResult with pass/fail status

    Specification:
        P1 Hardening - Critical method categories must be operational

    Smoke Test Categories:
        - Ingest: PDFChunkExtractor or similar (Phase 1 dependency)
        - Scoring: SignalEnrichedScorer or similar (Phase 3 dependency)
        - Aggregation: DimensionAggregator or similar (Phase 4 dependency)
    """
    gate_id = 7
    gate_name = "smoke_tests"

    method_executor = getattr(runner, "method_executor", None)

    if method_executor is None:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="MethodExecutor not available for smoke tests",
        )

    # Define smoke test samples (class_name, category)
    smoke_tests = [
        ("PDFChunkExtractor", "ingest"),
        ("SemanticAnalyzer", "scoring"),
        ("DimensionAggregator", "aggregation"),
    ]

    failed_tests = []

    for class_name, category in smoke_tests:
        try:
            # Check if method exists in registry
            if hasattr(method_executor, "instances"):
                # Try to access instance (will instantiate if not cached)
                if hasattr(method_executor.instances, "get"):
                    instance = method_executor.instances.get(class_name)
                    if instance is None:
                        failed_tests.append(f"{category}:{class_name}")
            # Fallback: try has_method
            elif hasattr(method_executor, "has_method"):
                # Pick a common method name to check
                if not method_executor.has_method(class_name, "__init__"):
                    failed_tests.append(f"{category}:{class_name}")
        except Exception as exc:
            failed_tests.append(f"{category}:{class_name}({type(exc).__name__})")

    if failed_tests:
        # In PROD mode, any smoke test failure is fatal
        if runner.runtime_config and hasattr(runner.runtime_config, "mode"):
            from farfan_pipeline.phases.Phase_0.phase0_10_01_runtime_config import RuntimeMode

            if runner.runtime_config.mode == RuntimeMode.PROD:
                return GateResult(
                    passed=False,
                    gate_name=gate_name,
                    gate_id=gate_id,
                    reason=f"Smoke tests failed: {', '.join(failed_tests)}",
                )

        # In DEV mode, pass with warning
        return GateResult(
            passed=True,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"DEV mode: smoke tests failed (non-fatal): {', '.join(failed_tests)}",
        )

    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_all_gates(runner: Phase0Runner) -> tuple[bool, list[GateResult]]:
    """
    Check all 7 Phase 0 exit gates in sequence.

    Gates are checked in order:
        1. Bootstrap
        2. Input Verification
        3. Boot Checks
        4. Determinism
        5. Questionnaire Integrity (NEW - P1 Hardening)
        6. Method Registry (NEW - P1 Hardening)
        7. Smoke Tests (NEW - P1 Hardening)

    If any gate fails, subsequent gates are NOT checked (fail-fast).

    Args:
        runner: Phase 0 runner instance

    Returns:
        Tuple of (all_passed, results)
        - all_passed: True only if all gates passed
        - results: List of GateResult objects (may be incomplete if fail-fast)

    Example:
        >>> all_passed, results = check_all_gates(runner)
        >>> if not all_passed:
        ...     failed_gate = next(r for r in results if not r.passed)
        ...     print(f"Gate {failed_gate.gate_id} failed: {failed_gate.reason}")
    """
    gates = [
        check_bootstrap_gate,
        check_input_verification_gate,
        check_boot_checks_gate,
        check_determinism_gate,
        check_questionnaire_integrity_gate,
        check_method_registry_gate,
        check_smoke_tests_gate,
    ]

    results = []
    for gate_func in gates:
        result = gate_func(runner)
        results.append(result)

        if not result.passed:
            # Fail-fast: don't check remaining gates
            return False, results

    return True, results


def get_gate_summary(results: list[GateResult]) -> str:
    """
    Generate human-readable summary of gate results.

    Args:
        results: List of GateResult objects from check_all_gates()

    Returns:
        Formatted summary string

    Example:
        >>> _, results = check_all_gates(runner)
        >>> print(get_gate_summary(results))
        Phase 0 Exit Gates: 7/7 passed
          ✓ Gate 1 (bootstrap): PASS
          ✓ Gate 2 (input_verification): PASS
          ✓ Gate 3 (boot_checks): PASS
          ✓ Gate 4 (determinism): PASS
          ✓ Gate 5 (questionnaire_integrity): PASS
          ✓ Gate 6 (method_registry): PASS
          ✓ Gate 7 (smoke_tests): PASS
    """
    passed = sum(1 for r in results if r.passed)
    total = 7  # There are now 7 Phase 0 gates (4 original + 3 new)

    lines = [f"Phase 0 Exit Gates: {passed}/{total} passed"]

    for result in results:
        status = "✓" if result.passed else "✗"
        gate_desc = f"Gate {result.gate_id} ({result.gate_name})"

        if result.passed:
            if result.reason:
                # Passed with warning
                lines.append(f"  {status} {gate_desc}: PASS (⚠️  {result.reason})")
            else:
                lines.append(f"  {status} {gate_desc}: PASS")
        else:
            lines.append(f"  {status} {gate_desc}: FAIL - {result.reason}")

    return "\n".join(lines)


__all__ = [
    "GateResult",
    "Phase0Runner",
    "check_all_gates",
    "check_boot_checks_gate",
    "check_bootstrap_gate",
    "check_determinism_gate",
    "check_input_verification_gate",
    "check_method_registry_gate",
    "check_questionnaire_integrity_gate",
    "check_smoke_tests_gate",
    "get_gate_summary",
]
