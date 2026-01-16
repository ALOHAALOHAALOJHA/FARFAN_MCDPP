"""
PDM Structural Recognition Contracts.

This module defines enforcement contracts for PDM (Plan de Desarrollo Municipal)
structural recognition according to Ley 152/94.

CONSTITUTIONAL REQUIREMENTS:
- PDMStructuralProfile MUST exist before Phase 1 execution
- SP2 MUST consume PDMStructuralProfile (obligatory)
- SP4 MUST respect semantic integrity rules (obligatory)
- Phase 1 → Phase 2 handoff MUST include PDM metadata

Author: FARFAN Engineering Team
Version: PDM-2025.1
"""

from pathlib import Path
from typing import Any

from farfan_pipeline.pdm.profile.pdm_structural_profile import (
    PDMStructuralProfile,
    get_default_profile,
)


class PrerequisiteError(Exception):
    """Raised when a prerequisite for execution is not met."""

    pass


class ValidationError(Exception):
    """Raised when validation fails."""

    pass


class PDMProfileContract:
    """
    Contract enforcement for PDMStructuralProfile presence.

    RULE: Profile MUST be present before SP2 execution.
    FAILURE MODE: PrerequisiteError → ABORT Phase 1

    This contract ensures that the constitutional object (PDMStructuralProfile)
    exists and is valid before Phase 1 begins structural analysis.
    """

    DEFAULT_PROFILE_PATH = Path(
        "src/farfan_pipeline/infrastructure/parametrization/pdm_structural_profile.py"
    )

    @staticmethod
    def enforce_profile_presence(
        profile_path: Path | None = None,
    ) -> PDMStructuralProfile:
        """
        Verify that PDMStructuralProfile exists and is valid.

        Args:
            profile_path: Optional path to profile module. If None, uses default.

        Returns:
            Valid PDMStructuralProfile instance

        Raises:
            PrerequisiteError: If profile missing or invalid
        """
        if profile_path is None:
            profile_path = PDMProfileContract.DEFAULT_PROFILE_PATH

        # Check file exists
        if not profile_path.exists():
            raise PrerequisiteError(
                f"ABORT: PDMStructuralProfile not found at {profile_path}. "
                "Phase 1 cannot execute without structural profile. "
                "Run: python -m farfan_pipeline.infrastructure.parametrization.pdm_structural_profile"
            )

        # Import and get default profile
        try:
            profile = get_default_profile()
        except Exception as e:
            raise PrerequisiteError(
                f"ABORT: Failed to load PDMStructuralProfile: {e}"
            ) from e

        # Validate profile integrity
        is_valid, errors = profile.validate_integrity()

        if not is_valid:
            raise ValidationError(
                f"ABORT: Invalid PDMStructuralProfile: {errors}. "
                "Profile must pass integrity validation before Phase 1 execution."
            )

        return profile

    @staticmethod
    def validate_profile_version(profile: PDMStructuralProfile) -> bool:
        """
        Verify profile version is compatible.

        Args:
            profile: PDMStructuralProfile to validate

        Returns:
            True if version compatible

        Raises:
            ValidationError: If version incompatible
        """
        expected_version = "PDM-2025.1"
        if profile.profile_version != expected_version:
            raise ValidationError(
                f"Profile version mismatch: expected {expected_version}, "
                f"got {profile.profile_version}"
            )
        return True


class SP2Obligations:
    """
    Contract obligations for SP2 (Structural Analysis).

    CRITICAL OBLIGATION: SP2 MUST consume PDMStructuralProfile.

    Failure modes:
    - Profile not provided → PrerequisiteError (ABORT)
    - Profile invalid → ValidationError (ABORT)
    - Profile present but not used → CONTRACT VIOLATION (ABORT)
    """

    @staticmethod
    def validate_sp2_execution(
        profile: PDMStructuralProfile,
        sp2_output: Any,  # StructureData from phase1_03_00_models
    ) -> tuple[bool, list[str]]:
        """
        Verify that SP2 correctly used PDMStructuralProfile.

        Required outputs from SP2:
        1. Hierarchy detected and labeled (H1-H5)
        2. Canonical sections identified with boundaries
        3. Tables detected with schema validation
        4. Structural transitions verified
        5. Semantic integrity rules applied

        Args:
            profile: PDMStructuralProfile used
            sp2_output: StructureData output from SP2

        Returns:
            (is_valid, violations) - True if SP2 met obligations, else list of violations

        Raises:
            PrerequisiteError: If profile not provided
        """
        if profile is None:
            raise PrerequisiteError(
                "SP2-ABORT: PDMStructuralProfile required but not provided"
            )

        violations = []

        # Check 1: Hierarchy detection
        if not hasattr(sp2_output, "hierarchy") or not sp2_output.hierarchy:
            violations.append("SP2-OB-01: Hierarchy not detected (H1-H5 required)")

        # Check 2: Section boundaries
        if not hasattr(sp2_output, "sections") or len(sp2_output.sections) == 0:
            violations.append(
                "SP2-OB-02: No canonical sections detected (DIAGNOSTICO, PARTE_ESTRATEGICA, PPI required)"
            )

        # Check 3: Tables detection
        if not hasattr(sp2_output, "tables"):
            violations.append("SP2-OB-03: Table detection not performed")
        else:
            # Verify expected tables
            expected_tables = set(profile.table_schemas.keys())
            detected_tables = {
                t.get("name", "") for t in sp2_output.tables if isinstance(t, dict)
            }

            # At least one table should be detected
            if len(detected_tables) == 0:
                violations.append(
                    f"SP2-OB-03: No tables detected (expected: {expected_tables})"
                )

        # Check 4: Profile metadata attached
        if not hasattr(sp2_output, "_pdm_profile_used"):
            violations.append(
                "SP2-OB-04: PDM profile metadata not attached to output"
            )

        return (len(violations) == 0, violations)

    @staticmethod
    def enforce_sp2_preconditions(profile: PDMStructuralProfile | None) -> None:
        """
        Enforce SP2 preconditions before execution.

        Args:
            profile: PDMStructuralProfile to use

        Raises:
            PrerequisiteError: If preconditions not met
        """
        if profile is None:
            raise PrerequisiteError(
                "SP2-ABORT: PDMStructuralProfile is mandatory for SP2 execution. "
                "Cannot proceed without structural profile."
            )

        # Validate profile
        is_valid, errors = profile.validate_integrity()
        if not is_valid:
            raise ValidationError(f"SP2-ABORT: Invalid profile: {errors}")


class SP4Obligations:
    """
    Contract obligations for SP4 (PA×Dim Grid Specification).

    CRITICAL OBLIGATION: SP4 MUST respect semantic integrity rules.

    SP4 assigns content to the 60-chunk PA×Dim grid. It must:
    1. Use hierarchy detected by SP2 (H1-H5)
    2. Respect section boundaries (Diagnóstico vs Estrategia vs PPI)
    3. Apply causal dimension patterns (D1-D6)
    4. Preserve P-D-Q context
    5. NEVER violate semantic integrity rules (e.g., Meta+Indicador atomic)
    """

    @staticmethod
    def validate_sp4_assignment(
        sp2_output: Any,  # StructureData
        profile: PDMStructuralProfile,
        sp4_output: list[Any],  # List of Chunk objects
    ) -> tuple[bool, list[str]]:
        """
        Verify that SP4 respected PDM structure when assigning chunks.

        Args:
            sp2_output: StructureData from SP2
            profile: PDMStructuralProfile used
            sp4_output: List of Chunk objects from SP4

        Returns:
            (is_valid, violations) - True if SP4 met obligations, else violations
        """
        violations = []

        # CONSTITUTIONAL INVARIANT: Must produce exactly 60 chunks
        if len(sp4_output) != 60:
            violations.append(
                f"SP4-CONST-01: CRITICAL - Must produce 60 chunks, got {len(sp4_output)}"
            )

        # Check 1: All chunks have PDM metadata
        chunks_without_metadata = [
            c.chunk_id
            for c in sp4_output
            if not hasattr(c, "pdm_metadata") or c.pdm_metadata is None
        ]

        if chunks_without_metadata:
            violations.append(
                f"SP4-OB-01: {len(chunks_without_metadata)} chunks missing PDM metadata: "
                f"{chunks_without_metadata[:5]}..."
            )

        # Check 2: Semantic integrity rules not violated
        for rule in profile.semantic_integrity_rules:
            if rule.violation_severity == "CRITICAL":
                # Check each chunk
                for chunk in sp4_output:
                    if hasattr(chunk, "text") and rule.check_violation(chunk.text):
                        violations.append(
                            f"SP4-OB-02: CRITICAL semantic rule violated in {chunk.chunk_id}: "
                            f"{rule.rule_id} - {rule.description}"
                        )

        # Check 3: Section context preserved
        for chunk in sp4_output:
            if hasattr(chunk, "pdm_metadata") and chunk.pdm_metadata is not None:
                # Verify source section is valid
                if not hasattr(chunk.pdm_metadata, "source_section"):
                    violations.append(
                        f"SP4-OB-03: Chunk {chunk.chunk_id} missing source_section"
                    )

        return (len(violations) == 0, violations)

    @staticmethod
    def enforce_sp4_preconditions(
        sp2_output: Any, profile: PDMStructuralProfile | None
    ) -> None:
        """
        Enforce SP4 preconditions before execution.

        Args:
            sp2_output: StructureData from SP2
            profile: PDMStructuralProfile

        Raises:
            PrerequisiteError: If preconditions not met
        """
        if profile is None:
            raise PrerequisiteError(
                "SP4-ABORT: PDMStructuralProfile required for semantic validation"
            )

        if sp2_output is None:
            raise PrerequisiteError(
                "SP4-ABORT: SP2 output (StructureData) required for PA×Dim assignment"
            )


class Phase1Phase2HandoffContract:
    """
    Contract for Phase 1 → Phase 2 handoff with PDM sensitivity.

    POSTCONDITIONS (Phase 1):
    - POST-01: Exactly 60 chunks
    - POST-02: All chunks have PDM structural metadata
    - POST-03: Semantic integrity preserved
    - POST-04: Calibration metadata included (if calibrated)

    PRECONDITIONS (Phase 2):
    - PRE-01: CPP validates against schema CPP-2025.1
    - PRE-02: PDM structural metadata present
    - PRE-03: 60-chunk invariant verified
    """

    @staticmethod
    def validate_cpp_for_phase2(cpp: Any) -> tuple[bool, list[str]]:
        """
        Verify that CPP is ready for Phase 2 consumption.

        Args:
            cpp: CanonPolicyPackage from Phase 1

        Returns:
            (is_valid, violations) - True if CPP meets all postconditions
        """
        violations = []

        # Check 1: Constitutional invariant (60 chunks)
        chunk_count = len(cpp.chunk_graph.chunks) if cpp.chunk_graph else 0
        if chunk_count != 60:
            violations.append(
                f"POST-01: CRITICAL - Expected 60 chunks, got {chunk_count}"
            )

        # Check 2: PDM structural metadata present
        for chunk_id, chunk in cpp.chunk_graph.chunks.items():
            if not hasattr(chunk, "pdm_metadata"):
                violations.append(f"POST-02: Chunk {chunk_id} missing PDM metadata")

            # Verify metadata completeness
            if hasattr(chunk, "pdm_metadata") and chunk.pdm_metadata is not None:
                if not hasattr(chunk.pdm_metadata, "hierarchy_level"):
                    violations.append(
                        f"POST-02: Chunk {chunk_id} PDM metadata missing hierarchy_level"
                    )
                if not hasattr(chunk.pdm_metadata, "source_section"):
                    violations.append(
                        f"POST-02: Chunk {chunk_id} PDM metadata missing source_section"
                    )

        # Check 3: Semantic integrity verified
        if hasattr(cpp, "semantic_integrity_verified"):
            if not cpp.semantic_integrity_verified:
                violations.append("POST-03: Semantic integrity not verified")

            # If violations exist, they should be documented
            if hasattr(cpp, "semantic_violations") and cpp.semantic_violations:
                violations.append(
                    f"POST-03: {len(cpp.semantic_violations)} semantic violations detected"
                )

        # Check 4: Calibration metadata (if applied)
        if hasattr(cpp, "calibration_applied") and cpp.calibration_applied:
            if not hasattr(cpp, "calibration_metadata") or cpp.calibration_metadata is None:
                violations.append("POST-04: Calibration applied but metadata missing")

        # Check 5: PDM profile version recorded
        if not hasattr(cpp, "pdm_profile_version") or cpp.pdm_profile_version is None:
            violations.append("POST-02: PDM profile version not recorded")

        return (len(violations) == 0, violations)

    @staticmethod
    def enforce_phase2_preconditions(cpp: Any) -> None:
        """
        Enforce Phase 2 preconditions before consumption.

        Args:
            cpp: CanonPolicyPackage to validate

        Raises:
            PrerequisiteError: If CPP not ready for Phase 2
        """
        is_valid, violations = Phase1Phase2HandoffContract.validate_cpp_for_phase2(cpp)

        if not is_valid:
            raise PrerequisiteError(
                f"Phase 2 preconditions not met. CPP invalid:\n"
                + "\n".join(f"  - {v}" for v in violations)
            )


# =============================================================================
# CONTRACT VERIFICATION SUMMARY
# =============================================================================


def verify_all_pdm_contracts(
    profile: PDMStructuralProfile,
    sp2_output: Any,
    sp4_output: list[Any],
    cpp: Any,
) -> dict[str, tuple[bool, list[str]]]:
    """
    Verify all PDM contracts in one call.

    Args:
        profile: PDMStructuralProfile used
        sp2_output: StructureData from SP2
        sp4_output: List of Chunks from SP4
        cpp: CanonPolicyPackage final output

    Returns:
        Dict mapping contract name to (is_valid, violations)
    """
    results = {}

    # SP2 Obligations
    try:
        sp2_valid, sp2_violations = SP2Obligations.validate_sp2_execution(
            profile, sp2_output
        )
        results["SP2Obligations"] = (sp2_valid, sp2_violations)
    except Exception as e:
        results["SP2Obligations"] = (False, [str(e)])

    # SP4 Obligations
    try:
        sp4_valid, sp4_violations = SP4Obligations.validate_sp4_assignment(
            sp2_output, profile, sp4_output
        )
        results["SP4Obligations"] = (sp4_valid, sp4_violations)
    except Exception as e:
        results["SP4Obligations"] = (False, [str(e)])

    # Phase 1 → Phase 2 Handoff
    try:
        cpp_valid, cpp_violations = Phase1Phase2HandoffContract.validate_cpp_for_phase2(
            cpp
        )
        results["Phase1Phase2Handoff"] = (cpp_valid, cpp_violations)
    except Exception as e:
        results["Phase1Phase2Handoff"] = (False, [str(e)])

    return results
