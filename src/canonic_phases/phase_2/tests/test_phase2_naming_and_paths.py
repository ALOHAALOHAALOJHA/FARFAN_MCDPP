"""
Module: src.canonic_phases.phase_2.tests.test_phase2_naming_and_paths
Purpose: Enforce naming conventions and path constraints for Phase 2
Owner: phase2_orchestration
Lifecycle: ACTIVE
Version: 1.0.0
Effective-Date: 2025-12-18

Contracts-Enforced:
    - NamingContract: All files follow declared naming patterns
    - PathContract: All Phase 2 files exist only under canonical root

Determinism: 
    Seed-Strategy: NOT_APPLICABLE
    State-Management: Stateless file system scan

Inputs:
    - file_system: PathLike — Repository root path

Outputs:
    - validation_result: bool — True if all constraints satisfied

Failure-Modes:
    - NamingViolation: AssertionError — File name does not match pattern
    - PathViolation: AssertionError — Phase 2 file outside canonical root
    - LegacyArtifactFound: AssertionError — Forbidden file exists
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Final, List, Set

import pytest

# === CONSTANTS ===
CANONICAL_ROOT: Final[Path] = Path("src/canonic_phases/phase_2")

PHASE_ROOT_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^phase2_[a-z]_[a-z0-9_]+\.py$"
)

PACKAGE_INTERNAL_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9_]*\.py$"
)

SCHEMA_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^[a-z][a-z0-9_]*\.schema\.json$"
)

CERTIFICATE_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$"
)

TEST_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^test_phase2_[a-z0-9_]+\.py$"
)

FORBIDDEN_LEGACY_NAMES: Final[Set[str]] = frozenset({
    "executors.py",
    "batch_executor.py",
    "batch_generate_all_configs.py",
    "EXECUTOR_CALIBRATION_INTEGRATION_README.md",
    "INTEGRATION_IMPLEMENTATION_SUMMARY.md",
})

FORBIDDEN_LEGACY_PATTERNS: Final[List[re.Pattern[str]]] = [
    re.compile(r".*_v\d+\.py$"),      # version suffixes
    re.compile(r".*_final.*\.py$"),   # "final" in name
    re.compile(r".*_old.*\.py$"),     # "old" in name
    re.compile(r".*_backup.*\.py$"),  # backup files
]


class TestPhase2NamingEnforcement:
    """
    SUCCESS_CRITERIA: All Phase 2 files pass naming validation
    FAILURE_MODES: [NamingViolation, PathViolation, LegacyArtifactFound]
    TERMINATION_CONDITION: All files scanned, all assertions passed
    CONVERGENCE_RULE: N/A (single-pass validation)
    VERIFICATION_STRATEGY: pytest execution in CI
    """

    @pytest.fixture
    def phase2_root(self) -> Path:
        """Return the canonical Phase 2 root path."""
        root = Path(__file__).parent.parent
        assert root.name == "phase_2", f"Expected phase_2, got {root.name}"
        return root

    def test_canonical_root_exists(self, phase2_root: Path) -> None:
        """Phase 2 canonical root directory must exist."""
        assert phase2_root.exists(), f"Canonical root missing: {phase2_root}"
        assert phase2_root.is_dir(), f"Canonical root not a directory: {phase2_root}"

    def test_phase_root_files_naming(self, phase2_root: Path) -> None:
        """All .py files directly under phase_2/ must match phase2_[a-z]_*.py pattern."""
        violations: List[str] = []
        
        for file_path in phase2_root.glob("*.py"):
            if file_path.name == "__init__.py":
                continue
            if not PHASE_ROOT_PATTERN.match(file_path.name):
                violations.append(f"NAMING_VIOLATION: {file_path.name}")
        
        assert not violations, "\n".join(violations)

    def test_schema_files_naming(self, phase2_root: Path) -> None:
        """All files in schemas/ must match *.schema.json pattern."""
        schemas_dir = phase2_root / "schemas"
        if not schemas_dir.exists():
            pytest.skip("schemas/ directory not yet created")
        
        violations: List[str] = []
        for file_path in schemas_dir.glob("*"):
            if file_path.name == "__init__.py":
                continue
            if file_path.suffix == ".json" and not SCHEMA_PATTERN.match(file_path.name):
                violations.append(f"SCHEMA_NAMING_VIOLATION: {file_path.name}")
        
        assert not violations, "\n".join(violations)

    def test_certificate_files_naming(self, phase2_root: Path) -> None:
        """All files in contracts/certificates/ must match CERTIFICATE_XX_*.md pattern."""
        certs_dir = phase2_root / "contracts" / "certificates"
        if not certs_dir.exists():
            pytest.skip("contracts/certificates/ directory not yet created")
        
        violations: List[str] = []
        for file_path in certs_dir.glob("*.md"):
            if not CERTIFICATE_PATTERN.match(file_path.name):
                violations.append(f"CERTIFICATE_NAMING_VIOLATION: {file_path.name}")
        
        assert not violations, "\n".join(violations)

    def test_no_forbidden_legacy_artifacts(self, phase2_root: Path) -> None:
        """No forbidden legacy files may exist anywhere in the repository."""
        repo_root = phase2_root.parent.parent.parent  # src/canonic_phases/phase_2 -> repo root
        violations: List[str] = []
        
        for forbidden_name in FORBIDDEN_LEGACY_NAMES:
            matches = list(repo_root.rglob(forbidden_name))
            for match in matches:
                violations.append(f"LEGACY_ARTIFACT_FOUND: {match}")
        
        for pattern in FORBIDDEN_LEGACY_PATTERNS:
            for py_file in repo_root.rglob("*.py"):
                if pattern.match(py_file.name):
                    violations.append(f"LEGACY_PATTERN_MATCH: {py_file}")
        
        assert not violations, "\n".join(violations)

    def test_no_phase2_files_outside_canonical_root(self) -> None:
        """No Phase 2 related files may exist outside the canonical root."""
        repo_root = Path(__file__).parent.parent.parent.parent.parent
        canonical_root = repo_root / "src" / "canonic_phases" / "phase_2"
        violations: List[str] = []
        
        # Search for phase2-related files outside canonical root
        phase2_pattern = re.compile(r"phase.?2", re.IGNORECASE)
        
        for py_file in repo_root.rglob("*.py"):
            if canonical_root in py_file.parents or py_file.is_relative_to(canonical_root):
                continue
            if phase2_pattern.search(py_file.name):
                violations.append(f"PHASE2_FILE_OUTSIDE_CANONICAL: {py_file}")
        
        assert not violations, "\n".join(violations)

    def test_required_subfolders_exist(self, phase2_root: Path) -> None:
        """All required subfolders must exist."""
        required_subfolders: List[str] = [
            "constants",
            "schemas",
            "executors",
            "executors/implementations",
            "executors/tests",
            "contracts",
            "contracts/certificates",
            "orchestration",
            "sisas",
            "tests",
            "tools",
        ]
        
        missing: List[str] = []
        for subfolder in required_subfolders:
            path = phase2_root / subfolder
            if not path.exists():
                missing.append(f"MISSING_SUBFOLDER: {subfolder}")
        
        assert not missing, "\n".join(missing)
