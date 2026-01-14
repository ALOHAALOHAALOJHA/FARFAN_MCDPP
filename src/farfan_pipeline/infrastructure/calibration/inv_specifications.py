"""
INV-CAL-00x Calibration Invariant Specifications
=================================================
Formal specifications for all calibration invariants with grep enforcement.

DESIGN PRINCIPLE:
    Every calibration invariant must be:
    1. Documented with a unique INV-CAL-00x identifier
    2. Enforceable via grep-based code inspection
    3. Testable with adversarial test cases
    4. Auditable in calibration manifests

Module: inv_specifications.py
Owner: farfan_pipeline.infrastructure.calibration
Purpose: Calibration invariant specifications and grep enforcement
Schema Version: 1.0.0

GREP ENFORCEMENT:
    Use this command to verify invariant coverage:
    ```bash
    grep -r "INV-CAL-" src/farfan_pipeline/infrastructure/calibration/ | wc -l
    ```

    To check for missing UoA docstrings:
    ```bash
    grep -L "Unit of Analysis Requirements" src/farfan_pipeline/infrastructure/calibration/*.py
    ```

    To verify epistemic level documentation:
    ```bash
    grep -c "Epistemic Level:" src/farfan_pipeline/infrastructure/calibration/*.py
    ```
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


# =============================================================================
# INVARIANT SEVERITY
# =============================================================================


class InvariantSeverity(Enum):
    """
    Invariant violation severity levels.

    ADVISORY: Suggestion for improvement (non-blocking)
    WARNING: Potential issue (logged but allowed)
    ERROR: Violation detected (blocks calibration)
    CRITICAL: Severe violation (triggers veto cascade)
    """

    ADVISORY = "ADVISORY"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


# =============================================================================
# INVARIANT SPECIFICATIONS
# =============================================================================


@dataclass(frozen=True, slots=True)
class InvariantSpecification:
    """
    Formal specification for a calibration invariant.

    Attributes:
        id: Unique invariant identifier (INV-CAL-00x)
        name: Human-readable invariant name
        description: Detailed invariant description
        severity: Violation severity level
        grep_pattern: Regex pattern for grep enforcement
        enforcement_location: File/module where invariant is enforced
        test_location: Test file covering this invariant
        rationale: Why this invariant exists
    """

    id: str
    name: str
    description: str
    severity: InvariantSeverity
    grep_pattern: str
    enforcement_location: str
    test_location: str
    rationale: str

    def __post_init__(self) -> None:
        """Validate specification."""
        if not self.id.startswith("INV-CAL-"):
            raise ValueError(f"Invariant ID must start with 'INV-CAL-', got: {self.id}")


# =============================================================================
# CORE CALIBRATION INVARIANTS
# =============================================================================

INV_CAL_001 = InvariantSpecification(
    id="INV-CAL-001",
    name="Prior Strength Bounds",
    description="Prior strength must be within TYPE-specific bounds defined in type_defaults.py",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-001.*prior_strength.*bounds",
    enforcement_location="calibration_core.py:CalibrationParameter.__post_init__",
    test_location="tests/calibration/test_calibration_core_adversarial.py",
    rationale=(
        "Prior strength controls Bayesian update weight. Out-of-bounds values "
        "can cause epistemic drift or incorrect fusion. TYPE-specific bounds "
        "ensure priors match epistemic requirements."
    ),
)

INV_CAL_002 = InvariantSpecification(
    id="INV-CAL-002",
    name="Veto Threshold Bounds",
    description="Veto threshold must be within TYPE-specific bounds defined in type_defaults.py",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-002.*veto_threshold.*bounds",
    enforcement_location="calibration_core.py:CalibrationParameter.__post_init__",
    test_location="tests/calibration/test_calibration_core_adversarial.py",
    rationale=(
        "Veto threshold gates N3-AUD validation. Too lenient → uncaught errors, "
        "too strict → false positives. TYPE-specific bounds balance sensitivity."
    ),
)

INV_CAL_003 = InvariantSpecification(
    id="INV-CAL-003",
    name="No Prohibited Operations",
    description="Fusion strategy must not use operations in PROHIBITED_OPERATIONS for this TYPE",
    severity=InvariantSeverity.CRITICAL,
    grep_pattern=r"INV-CAL-003.*prohibited.*operations",
    enforcement_location="phase2_calibrator.py:Phase2Calibrator.calibrate",
    test_location="tests/calibration/test_type_defaults_adversarial.py",
    rationale=(
        "TYPE_E forbids averaging operations (must use MIN logic). "
        "Violating this causes epistemic category errors and invalid results."
    ),
)

INV_CAL_004 = InvariantSpecification(
    id="INV-CAL-004",
    name="Validity Window Constraint",
    description="Calibration validity window must be ≤ UoA.data_validity_days",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-004.*validity.*UoA",
    enforcement_location="calibration_regime.py:_create_phase1_layer",
    test_location="tests/calibration/test_calibration_regime.py",
    rationale=(
        "Calibration cannot outlive the UoA data it's based on. "
        "Using expired UoA data leads to miscalibration."
    ),
)

INV_CAL_005 = InvariantSpecification(
    id="INV-CAL-005",
    name="Cognitive Cost Factored",
    description="Cognitive cost must be factored into prior strength (higher cost → stronger priors)",
    severity=InvariantSeverity.WARNING,
    grep_pattern=r"INV-CAL-005.*cognitive.*cost.*prior",
    enforcement_location="calibration_regime.py:_create_phase1_layer",
    test_location="tests/calibration/test_cognitive_cost.py",
    rationale=(
        "Complex methods require conservative calibration (stronger priors) "
        "to prevent drift under cognitive load."
    ),
)

INV_CAL_006 = InvariantSpecification(
    id="INV-CAL-006",
    name="Interaction Density Capped",
    description="Interaction density must be capped per TYPE (TYPE_E: 0.5, TYPE_D: 0.9, etc.)",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-006.*interaction.*density.*cap",
    enforcement_location="interaction_density.py:InteractionDensityTracker.compute_density",
    test_location="tests/calibration/test_interaction_density.py",
    rationale=(
        "High interaction density causes error propagation and fusion instability. "
        "TYPE-specific caps maintain epistemic coherence."
    ),
)

INV_CAL_007 = InvariantSpecification(
    id="INV-CAL-007",
    name="Immutable Manifests",
    description="Calibration manifests must be immutable and deterministically hashed (SHA-256)",
    severity=InvariantSeverity.CRITICAL,
    grep_pattern=r"INV-CAL-007.*immutable.*manifest.*hash",
    enforcement_location="calibration_regime.py:UnifiedCalibrationManifest.__post_init__",
    test_location="tests/calibration/test_calibration_manifest.py",
    rationale=(
        "Immutability ensures audit trail integrity. Deterministic hashing "
        "enables cryptographic verification and change detection."
    ),
)

INV_CAL_008 = InvariantSpecification(
    id="INV-CAL-008",
    name="Drift Reports Generated",
    description="Drift reports must be generated when calibration parameters change",
    severity=InvariantSeverity.WARNING,
    grep_pattern=r"INV-CAL-008.*drift.*report",
    enforcement_location="drift_detector.py:DriftDetector.detect_drift",
    test_location="tests/calibration/test_drift_detector.py",
    rationale=(
        "Parameter drift indicates UoA changes or recalibration. "
        "Reports enable auditors to track calibration stability."
    ),
)

INV_CAL_009 = InvariantSpecification(
    id="INV-CAL-009",
    name="Coverage and Dispersion Penalties",
    description="Coverage < 0.85 or high parameter dispersion must trigger penalties",
    severity=InvariantSeverity.WARNING,
    grep_pattern=r"INV-CAL-009.*coverage.*dispersion.*penalty",
    enforcement_location="drift_detector.py:DriftDetector._check_coverage_penalty",
    test_location="tests/calibration/test_drift_detector.py",
    rationale=(
        "Low coverage indicates incomplete extraction. High dispersion "
        "indicates unstable calibration. Penalties flag these issues."
    ),
)

INV_CAL_010 = InvariantSpecification(
    id="INV-CAL-010",
    name="Contradiction Penalties",
    description="Contradictory parameter changes (e.g., prior↑ AND veto↑) must be penalized",
    severity=InvariantSeverity.CRITICAL,
    grep_pattern=r"INV-CAL-010.*contradiction.*penalty",
    enforcement_location="drift_detector.py:DriftDetector._detect_contradictions",
    test_location="tests/calibration/test_drift_detector.py",
    rationale=(
        "Contradictions (prior↑ but veto↑) violate epistemic logic. "
        "Prior↑ should mean veto↓ (stronger prior → less strict validation)."
    ),
)


# =============================================================================
# UNIT OF ANALYSIS INVARIANTS
# =============================================================================

INV_CAL_011 = InvariantSpecification(
    id="INV-CAL-011",
    name="UoA Complexity Score Bounds",
    description="UnitOfAnalysis.complexity_score() must return value in [0.0, 1.0]",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-011.*complexity.*score.*\[0.*1\]",
    enforcement_location="unit_of_analysis.py:UnitOfAnalysis.complexity_score",
    test_location="tests/calibration/test_unit_of_analysis.py",
    rationale=(
        "Complexity score drives calibration parameter scaling. "
        "Out-of-bounds values cause miscalibration."
    ),
)

INV_CAL_012 = InvariantSpecification(
    id="INV-CAL-012",
    name="UoA Municipality Code Format",
    description="Municipality code must match pattern [A-Z]{2,6}-[0-9]{4,12}",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-012.*municipality.*code.*pattern",
    enforcement_location="unit_of_analysis.py:UnitOfAnalysis.__post_init__",
    test_location="tests/calibration/test_unit_of_analysis.py",
    rationale=(
        "Municipality codes are used as UoA identifiers. "
        "Invalid format breaks traceability and audit trails."
    ),
)


# =============================================================================
# METHOD BINDING INVARIANTS
# =============================================================================

INV_CAL_013 = InvariantSpecification(
    id="INV-CAL-013",
    name="Epistemic Layer Ratios",
    description="N1:N2:N3 method ratios must match TYPE-specific requirements",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-013.*layer.*ratio.*TYPE",
    enforcement_location="method_binding_validator.py:MethodBindingValidator._validate_layer_ratios",
    test_location="tests/calibration/test_method_binding_validator.py",
    rationale=(
        "Each TYPE has required epistemic balance (e.g., TYPE_E: N3-dominant). "
        "Wrong ratios violate epistemic architecture."
    ),
)

INV_CAL_014 = InvariantSpecification(
    id="INV-CAL-014",
    name="Mandatory Patterns Present",
    description="Each TYPE must have certain mandatory method patterns (e.g., TYPE_C needs DAG validation)",
    severity=InvariantSeverity.CRITICAL,
    grep_pattern=r"INV-CAL-014.*mandatory.*pattern.*TYPE",
    enforcement_location="method_binding_validator.py:MethodBindingValidator._validate_mandatory_patterns",
    test_location="tests/calibration/test_method_binding_validator.py",
    rationale=(
        "Mandatory patterns ensure TYPE-specific epistemic requirements. "
        "Missing patterns cause validation gaps."
    ),
)

INV_CAL_015 = InvariantSpecification(
    id="INV-CAL-015",
    name="Dependency Chain Validity",
    description="N2.requires ⊆ N1.provides (dependencies must be satisfied)",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-015.*dependency.*chain.*valid",
    enforcement_location="method_binding_validator.py:MethodBindingValidator._validate_dependency_chain",
    test_location="tests/calibration/test_method_binding_validator.py",
    rationale=(
        "Broken dependency chains cause runtime failures. "
        "N2 methods cannot execute if required N1 outputs are missing."
    ),
)


# =============================================================================
# INTERACTION GOVERNANCE INVARIANTS
# =============================================================================

INV_CAL_016 = InvariantSpecification(
    id="INV-CAL-016",
    name="Acyclic Dependency Graph",
    description="Method dependency graph must be acyclic (DAG)",
    severity=InvariantSeverity.CRITICAL,
    grep_pattern=r"INV-CAL-016.*acyclic.*DAG",
    enforcement_location="interaction_governor.py:CycleDetector.find_cycles",
    test_location="tests/calibration/test_interaction_governor_adversarial.py",
    rationale=(
        "Cycles in dependency graph cause infinite loops and deadlocks. "
        "DAG structure ensures topological execution order."
    ),
)

INV_CAL_017 = InvariantSpecification(
    id="INV-CAL-017",
    name="No Level Inversions",
    description="N3 methods cannot depend on N2 outputs (level inversion forbidden)",
    severity=InvariantSeverity.CRITICAL,
    grep_pattern=r"INV-CAL-017.*level.*inversion",
    enforcement_location="interaction_governor.py:LevelInversionDetector.detect_inversions",
    test_location="tests/calibration/test_interaction_governor_adversarial.py",
    rationale=(
        "N3 (audit) depends on N1 (evidence), not N2 (inference). "
        "Inversions violate epistemic architecture."
    ),
)

INV_CAL_018 = InvariantSpecification(
    id="INV-CAL-018",
    name="Bounded Multiplicative Fusion",
    description="Multiplicative fusion results must be bounded in [0.01, 10.0]",
    severity=InvariantSeverity.ERROR,
    grep_pattern=r"INV-CAL-018.*bounded.*fusion.*\[0\.01.*10",
    enforcement_location="interaction_governor.py:bounded_multiplicative_fusion",
    test_location="tests/calibration/test_interaction_governor_adversarial.py",
    rationale=(
        "Unbounded multiplication causes overflow/underflow. "
        "Bounds prevent numerical instability in fusion."
    ),
)


# =============================================================================
# DOCUMENTATION INVARIANTS
# =============================================================================

INV_CAL_019 = InvariantSpecification(
    id="INV-CAL-019",
    name="UoA Requirements Documented",
    description="Every public method must document Unit of Analysis Requirements",
    severity=InvariantSeverity.WARNING,
    grep_pattern=r"Unit of Analysis Requirements:",
    enforcement_location="All calibration modules (docstrings)",
    test_location="tests/calibration/test_documentation_compliance.py",
    rationale=(
        "UoA requirements clarify input expectations and enable "
        "grep-based verification of calibration coverage."
    ),
)

INV_CAL_020 = InvariantSpecification(
    id="INV-CAL-020",
    name="Epistemic Level Documented",
    description="Every public method must document Epistemic Level (N1/N2/N3)",
    severity=InvariantSeverity.WARNING,
    grep_pattern=r"Epistemic Level: N[1-3]",
    enforcement_location="All calibration modules (docstrings)",
    test_location="tests/calibration/test_documentation_compliance.py",
    rationale=(
        "Epistemic level classification is fundamental to FARFAN architecture. "
        "Missing documentation obscures method purpose."
    ),
)

INV_CAL_021 = InvariantSpecification(
    id="INV-CAL-021",
    name="Fusion Strategy Documented",
    description="Every calibration method must document its Fusion Strategy",
    severity=InvariantSeverity.WARNING,
    grep_pattern=r"Fusion Strategy:",
    enforcement_location="All calibration modules (docstrings)",
    test_location="tests/calibration/test_documentation_compliance.py",
    rationale=(
        "Fusion strategy determines how evidence is combined. "
        "Missing documentation prevents TYPE-specific validation."
    ),
)


# =============================================================================
# ALL SPECIFICATIONS REGISTRY
# =============================================================================

ALL_INVARIANT_SPECIFICATIONS: Final[tuple[InvariantSpecification, ...]] = (
    INV_CAL_001,  # Prior strength bounds
    INV_CAL_002,  # Veto threshold bounds
    INV_CAL_003,  # No prohibited operations
    INV_CAL_004,  # Validity window constraint
    INV_CAL_005,  # Cognitive cost factored
    INV_CAL_006,  # Interaction density capped
    INV_CAL_007,  # Immutable manifests
    INV_CAL_008,  # Drift reports generated
    INV_CAL_009,  # Coverage and dispersion penalties
    INV_CAL_010,  # Contradiction penalties
    INV_CAL_011,  # UoA complexity score bounds
    INV_CAL_012,  # UoA municipality code format
    INV_CAL_013,  # Epistemic layer ratios
    INV_CAL_014,  # Mandatory patterns present
    INV_CAL_015,  # Dependency chain validity
    INV_CAL_016,  # Acyclic dependency graph
    INV_CAL_017,  # No level inversions
    INV_CAL_018,  # Bounded multiplicative fusion
    INV_CAL_019,  # UoA requirements documented
    INV_CAL_020,  # Epistemic level documented
    INV_CAL_021,  # Fusion strategy documented
)


# =============================================================================
# GREP ENFORCEMENT UTILITIES
# =============================================================================


def get_specification_by_id(inv_id: str) -> InvariantSpecification | None:
    """
    Get invariant specification by ID.

    Args:
        inv_id: Invariant ID (e.g., "INV-CAL-001")

    Returns:
        InvariantSpecification or None if not found
    """
    for spec in ALL_INVARIANT_SPECIFICATIONS:
        if spec.id == inv_id:
            return spec
    return None


def get_specifications_by_severity(
    severity: InvariantSeverity,
) -> tuple[InvariantSpecification, ...]:
    """
    Get all specifications with given severity.

    Args:
        severity: Severity level to filter by

    Returns:
        Tuple of matching specifications
    """
    return tuple(spec for spec in ALL_INVARIANT_SPECIFICATIONS if spec.severity == severity)


def generate_grep_enforcement_script() -> str:
    """
    Generate bash script for grep-based invariant enforcement.

    Returns:
        Bash script as string
    """
    script_lines = [
        "#!/bin/bash",
        "# Automated invariant enforcement via grep",
        "# Generated from inv_specifications.py",
        "",
        "CALIBRATION_DIR='src/farfan_pipeline/infrastructure/calibration'",
        "FAILURES=0",
        "",
    ]

    for spec in ALL_INVARIANT_SPECIFICATIONS:
        script_lines.extend([
            f"# Check {spec.id}: {spec.name}",
            f"echo 'Checking {spec.id}...'",
            f"grep -r '{spec.grep_pattern}' \"$CALIBRATION_DIR\" > /dev/null",
            "if [ $? -ne 0 ]; then",
            f"  echo '  ❌ FAILED: {spec.id} - {spec.name}'",
            "  FAILURES=$((FAILURES + 1))",
            "else",
            f"  echo '  ✅ PASSED: {spec.id}'",
            "fi",
            "",
        ])

    script_lines.extend([
        "if [ $FAILURES -gt 0 ]; then",
        "  echo \"\"",
        "  echo \"❌ $FAILURES invariant(s) failed enforcement\"",
        "  exit 1",
        "else",
        "  echo \"\"",
        "  echo \"✅ All invariants passed enforcement\"",
        "  exit 0",
        "fi",
    ])

    return "\n".join(script_lines)


# =============================================================================
# MODULE EXPORTS
# =============================================================================


__all__ = [
    "InvariantSeverity",
    "InvariantSpecification",
    "ALL_INVARIANT_SPECIFICATIONS",
    "INV_CAL_001",
    "INV_CAL_002",
    "INV_CAL_003",
    "INV_CAL_004",
    "INV_CAL_005",
    "INV_CAL_006",
    "INV_CAL_007",
    "INV_CAL_008",
    "INV_CAL_009",
    "INV_CAL_010",
    "INV_CAL_011",
    "INV_CAL_012",
    "INV_CAL_013",
    "INV_CAL_014",
    "INV_CAL_015",
    "INV_CAL_016",
    "INV_CAL_017",
    "INV_CAL_018",
    "INV_CAL_019",
    "INV_CAL_020",
    "INV_CAL_021",
    "get_specification_by_id",
    "get_specifications_by_severity",
    "generate_grep_enforcement_script",
]
