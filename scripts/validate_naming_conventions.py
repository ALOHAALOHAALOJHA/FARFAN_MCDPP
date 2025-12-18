r"""
Naming Convention Validator for F.A.R.F.A.N Phase 2

Enforces SECTION 3: NAMING CONVENTION ENFORCEMENT (STABILIZATION PHASE)

Rules Enforced:
- Rule 3.1.1: Phase-Root Python Files (^phase2_[a-z]_[a-z0-9_]+\.py$)
- Rule 3.1.2: Package-Internal Python Files (^[a-z][a-z0-9_]*\.py$)
- Rule 3.1.3: Schema Files (^[a-z][a-z0-9_]*\.schema\.json$)
- Rule 3.1.4: Certificate Files (^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$)
- Rule 3.1.5: Test Files (^test_phase2_[a-z0-9_]+\.py$)

Exit Codes:
- 0: All files comply with naming conventions
- 1: Violations found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class NamingRule(NamedTuple):
    """Naming convention rule specification."""

    name: str
    pattern: str
    locations: list[str]
    examples_valid: list[str]
    examples_invalid: list[str]


# Define naming rules according to SECTION 3
NAMING_RULES = {
    "phase2_root_files": NamingRule(
        name="Rule 3.1.1: Phase-Root Python Files",
        pattern=r"^phase2_[a-z]_[a-z0-9_]+\.py$",
        locations=[
            "src/farfan_pipeline/phases/Phase_two",
            "src/canonic_phases/phase_2",
        ],
        examples_valid=["phase2_a_arg_router.py", "phase2_b_carver.py"],
        examples_invalid=["arg_router.py", "Phase2Router.py", "phase2-router.py"],
    ),
    "package_internal_files": NamingRule(
        name="Rule 3.1.2: Package-Internal Python Files",
        pattern=r"^[a-z][a-z0-9_]*\.py$",
        locations=[
            "src/farfan_pipeline/phases/Phase_two/json_files_phase_two/executor_contracts",
            "src/orchestration",
            "src/farfan_pipeline/infrastructure/contractual",
            "src/cross_cutting_infrastructure",
        ],
        examples_valid=["base_executor_with_contract.py", "phase2_routing_contract.py"],
        examples_invalid=["BaseExecutor.py", "routing-contract.py"],
    ),
    "schema_files": NamingRule(
        name="Rule 3.1.3: Schema Files",
        pattern=r"^[a-z][a-z0-9_]*\.schema\.json$",
        locations=["schemas", "system/config"],
        examples_valid=["executor_config.schema.json"],
        examples_invalid=["ExecutorConfig.json", "executor_config.json"],
    ),
    "certificate_files": NamingRule(
        name="Rule 3.1.4: Certificate Files",
        pattern=r"^CERTIFICATE_[0-9]{2}_[A-Z][A-Z0-9_]*\.md$",
        locations=["contracts/certificates"],
        examples_valid=["CERTIFICATE_01_ROUTING_CONTRACT.md"],
        examples_invalid=["certificate_01.md", "CERT_01.md"],
    ),
    "test_files": NamingRule(
        name="Rule 3.1.5: Test Files",
        pattern=r"^test_phase2_[a-z0-9_]+\.py$",
        locations=["tests"],
        examples_valid=["test_phase2_carver_300_delivery.py"],
        examples_invalid=["test_carver.py", "phase2_test_carver.py"],
    ),
}


class NamingViolation(NamedTuple):
    """Represents a naming convention violation."""

    file_path: Path
    rule_name: str
    pattern: str
    suggestion: str | None = None


def validate_file_name(file_path: Path, rule: NamingRule) -> NamingViolation | None:
    """Validate a single file name against a naming rule.

    Args:
        file_path: Path to the file to validate
        rule: Naming rule to check against

    Returns:
        NamingViolation if file doesn't match pattern, None otherwise
    """
    file_name = file_path.name
    pattern = re.compile(rule.pattern)

    if not pattern.match(file_name):
        return NamingViolation(
            file_path=file_path, rule_name=rule.name, pattern=rule.pattern, suggestion=None
        )

    return None


def find_files_in_locations(
    repo_root: Path, locations: list[str], extensions: list[str]
) -> list[Path]:
    """Find all files with given extensions in specified locations.

    Args:
        repo_root: Root directory of the repository
        locations: List of directory paths relative to repo_root
        extensions: List of file extensions to match (e.g., ['.py', '.json'])

    Returns:
        List of Path objects for matching files
    """
    files: list[Path] = []

    for location in locations:
        location_path = repo_root / location
        if not location_path.exists():
            continue

        for ext in extensions:
            # Find files directly in the location directory
            files.extend(location_path.glob(f"*{ext}"))

    return [f for f in files if f.is_file() and f.name != "__init__.py"]


def validate_naming_conventions(repo_root: Path) -> list[NamingViolation]:
    """Validate all files in the repository against naming conventions.

    Args:
        repo_root: Root directory of the repository

    Returns:
        List of naming violations found
    """
    violations: list[NamingViolation] = []

    # Rule 3.1.1: Phase-Root Python Files
    rule = NAMING_RULES["phase2_root_files"]
    files = find_files_in_locations(repo_root, rule.locations, [".py"])
    for file_path in files:
        violation = validate_file_name(file_path, rule)
        if violation:
            violations.append(violation)

    # Rule 3.1.2: Package-Internal Python Files
    rule = NAMING_RULES["package_internal_files"]
    files = find_files_in_locations(repo_root, rule.locations, [".py"])
    for file_path in files:
        violation = validate_file_name(file_path, rule)
        if violation:
            violations.append(violation)

    # Rule 3.1.3: Schema Files
    rule = NAMING_RULES["schema_files"]
    files = find_files_in_locations(repo_root, rule.locations, [".json"])
    # Only check files that should be schema files
    for file_path in files:
        if "schema" in file_path.name.lower():
            violation = validate_file_name(file_path, rule)
            if violation:
                violations.append(violation)

    # Rule 3.1.4: Certificate Files
    rule = NAMING_RULES["certificate_files"]
    # Find all contracts/certificates directories
    cert_dirs = list(repo_root.glob("**/contracts/certificates"))
    for cert_dir in cert_dirs:
        files = list(cert_dir.glob("*.md"))
        for file_path in files:
            violation = validate_file_name(file_path, rule)
            if violation:
                violations.append(violation)

    # Rule 3.1.5: Test Files
    rule = NAMING_RULES["test_files"]
    files = find_files_in_locations(repo_root, rule.locations, [".py"])
    # Only check test files that mention phase2
    for file_path in files:
        if "phase2" in file_path.name and file_path.name.startswith("test_"):
            violation = validate_file_name(file_path, rule)
            if violation:
                violations.append(violation)

    return violations


def print_violations(violations: list[NamingViolation], repo_root: Path) -> None:
    """Print naming violations in a readable format.

    Args:
        violations: List of violations to print
        repo_root: Repository root for relative path calculation
    """
    if not violations:
        print("✅ All files comply with naming conventions")
        return

    print(f"❌ Found {len(violations)} naming convention violation(s):\n")

    # Group violations by rule
    violations_by_rule: dict[str, list[NamingViolation]] = {}
    for violation in violations:
        if violation.rule_name not in violations_by_rule:
            violations_by_rule[violation.rule_name] = []
        violations_by_rule[violation.rule_name].append(violation)

    for rule_name, rule_violations in violations_by_rule.items():
        print(f"\n{rule_name}")
        print("=" * 80)
        for violation in rule_violations:
            rel_path = violation.file_path.relative_to(repo_root)
            print(f"  ❌ {rel_path}")
            print(f"     Expected pattern: {violation.pattern}")
            if violation.suggestion:
                print(f"     Suggestion: {violation.suggestion}")
        print()


def load_legacy_exemptions(repo_root: Path) -> set[str]:
    """Load list of legacy files exempt from naming conventions.

    Args:
        repo_root: Repository root directory

    Returns:
        Set of relative file paths (as strings) that are exempt
    """
    exemption_file = repo_root / ".naming_exemptions"
    if not exemption_file.exists():
        return set()

    with open(exemption_file) as f:
        return {line.strip() for line in f if line.strip() and not line.startswith("#")}


def filter_legacy_violations(
    violations: list[NamingViolation], exemptions: set[str], repo_root: Path
) -> list[NamingViolation]:
    """Filter out violations for files that are legacy-exempt.

    Args:
        violations: List of all violations
        exemptions: Set of exempt file paths (relative to repo root)
        repo_root: Repository root directory

    Returns:
        Filtered list of violations excluding exempted files
    """
    filtered = []
    for violation in violations:
        rel_path = str(violation.file_path.relative_to(repo_root))
        if rel_path not in exemptions:
            filtered.append(violation)
    return filtered


def main() -> int:
    """Main entry point for naming convention validation.

    Returns:
        Exit code: 0 if all files comply, 1 if violations found
    """
    parser = argparse.ArgumentParser(
        description="Validate F.A.R.F.A.N naming conventions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path.cwd(),
        help="Root directory of the repository (default: current directory)",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI mode: exit with code 1 if violations found",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: ignore legacy exemptions",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Report violations but always exit with code 0",
    )

    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    if not repo_root.exists():
        print(f"❌ Repository root not found: {repo_root}", file=sys.stderr)
        return 1

    print(f"Validating naming conventions in: {repo_root}\n")

    violations = validate_naming_conventions(repo_root)

    # Filter legacy exemptions unless in strict mode
    if not args.strict:
        exemptions = load_legacy_exemptions(repo_root)
        if exemptions:
            print(f"ℹ️  Loaded {len(exemptions)} legacy exemptions\n")
            original_count = len(violations)
            violations = filter_legacy_violations(violations, exemptions, repo_root)
            exempted_count = original_count - len(violations)
            if exempted_count > 0:
                print(f"ℹ️  Exempted {exempted_count} legacy file(s)\n")

    print_violations(violations, repo_root)

    if violations:
        print(f"\n❌ {len(violations)} violation(s) found")
        if args.ci and not args.report_only:
            print("\nCI MODE: Blocking PR due to naming convention violations")
            return 1
        if args.report_only:
            print("\nREPORT MODE: Violations reported but not blocking")
            return 0
        return 1

    print("\n✅ All naming conventions validated successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
