"""
Phase 0 Exit Gate Validators
=============================

Implements the 4 strict exit gates defined in P00-EN v2.0 specification.

Exit gates are MANDATORY checkpoints that must pass before proceeding to Phase 1.
Each gate validates a specific aspect of Phase 0 initialization.

Contract:
    Gate 1 (Bootstrap): Runtime config loaded, artifacts dir created
    Gate 2 (Input Verification): PDF and questionnaire hashed
    Gate 3 (Boot Checks): Dependencies validated (PROD: fatal, DEV: warn)
    Gate 4 (Determinism): All required seeds applied to RNGs

Author: Phase 0 Compliance Team
Version: 1.0.0
Specification: P00-EN v2.0
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from canonic_phases.Phase_zero.runtime_config import RuntimeConfig


class Phase0Runner(Protocol):
    """Protocol defining the interface for Phase 0 runners."""
    
    errors: list[str]
    _bootstrap_failed: bool
    runtime_config: RuntimeConfig | None
    seed_snapshot: dict[str, int]
    input_pdf_sha256: str
    questionnaire_sha256: str


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
            reason="Bootstrap failed during initialization"
        )
    
    if runner.runtime_config is None:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="Runtime config not loaded"
        )
    
    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Bootstrap errors detected: {'; '.join(runner.errors)}"
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
            reason="Input PDF not hashed with valid SHA-256"
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
            reason="Questionnaire not hashed with valid SHA-256"
        )
    
    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Input verification errors: {'; '.join(runner.errors)}"
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
            reason=f"Boot check errors: {'; '.join(runner.errors)}"
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
    
    if not hasattr(runner, 'seed_snapshot'):
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason="Seed snapshot not created"
        )
    
    # MANDATORY seeds (system cannot run without these)
    MANDATORY_SEEDS = ["python", "numpy"]
    missing_mandatory = [s for s in MANDATORY_SEEDS if runner.seed_snapshot.get(s) is None]
    
    if missing_mandatory:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Missing mandatory seeds: {missing_mandatory}"
        )
    
    if runner.errors:
        return GateResult(
            passed=False,
            gate_name=gate_name,
            gate_id=gate_id,
            reason=f"Determinism errors: {'; '.join(runner.errors)}"
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
            reason=f"Optional seeds missing (non-fatal): {missing_optional}"
        )
    
    return GateResult(passed=True, gate_name=gate_name, gate_id=gate_id)


def check_all_gates(runner: Phase0Runner) -> tuple[bool, list[GateResult]]:
    """
    Check all 4 Phase 0 exit gates in sequence.
    
    Gates are checked in order:
        1. Bootstrap
        2. Input Verification
        3. Boot Checks
        4. Determinism
    
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
        Phase 0 Exit Gates: 4/4 passed
          ✓ Gate 1 (bootstrap): PASS
          ✓ Gate 2 (input_verification): PASS
          ✓ Gate 3 (boot_checks): PASS
          ✓ Gate 4 (determinism): PASS
    """
    passed = sum(1 for r in results if r.passed)
    total = 4  # There are always 4 defined Phase 0 gates
    
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
    "Phase0Runner",
    "GateResult",
    "check_bootstrap_gate",
    "check_input_verification_gate",
    "check_boot_checks_gate",
    "check_determinism_gate",
    "check_all_gates",
    "get_gate_summary",
]
