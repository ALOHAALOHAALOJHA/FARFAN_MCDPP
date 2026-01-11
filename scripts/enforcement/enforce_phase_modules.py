#!/usr/bin/env python3
"""
Phase Module Nomenclature Enforcer
Enforces rigid naming policies for phase modules in the FARFAN pipeline
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
import shutil


class PhaseModuleEnforcer:
    """Enforces naming policies for phase modules."""

    def __init__(self):
        self.phase_pattern = re.compile(r"^phase(\d+)_(\d{2})_(\d{2})_([a-z][a-z0-9_]+)\.py$")
        self.violations = []

    def scan_phase_modules(self, phases_dir: str) -> List[Dict]:
        """Scan phase modules for naming violations."""
        violations = []

        phases_path = Path(phases_dir)
        if not phases_path.exists():
            return violations

        for phase_dir in phases_path.iterdir():
            if phase_dir.is_dir() and phase_dir.name.startswith("Phase_"):
                for py_file in phase_dir.rglob("*.py"):
                    if not py_file.name.startswith("__"):  # Skip __init__.py
                        violations.extend(self._check_phase_module_naming(py_file, phase_dir))

        return violations

    def _check_phase_module_naming(self, file_path: Path, phase_dir: Path) -> List[Dict]:
        """Check if a phase module follows the correct naming convention."""
        violations = []

        # Extract expected phase number from directory name
        phase_match = re.search(r"Phase_(\w+)", phase_dir.name)
        if not phase_match:
            return violations

        phase_name = phase_match.group(1)
        expected_phase_num = self._convert_phase_name_to_number(phase_name)

        if not expected_phase_num:
            return violations

        # Check if filename matches the pattern
        if not self.phase_pattern.match(file_path.name):
            violations.append(
                {
                    "type": "INVALID_NAMING_PATTERN",
                    "file": str(file_path),
                    "severity": "ERROR",
                    "message": f"File {file_path.name} does not match required pattern: phaseX_YY_ZZ_name.py",
                    "expected_phase": expected_phase_num,
                }
            )
        else:
            # Check if the phase number in filename matches the directory
            filename_match = self.phase_pattern.match(file_path.name)
            if filename_match:
                actual_phase = filename_match.group(1)
                if (
                    actual_phase != expected_phase_num[0]
                ):  # Compare first digit for multi-digit phases
                    violations.append(
                        {
                            "type": "PHASE_MISMATCH",
                            "file": str(file_path),
                            "severity": "ERROR",
                            "message": f"File {file_path.name} has phase {actual_phase} but is in Phase_{phase_name} directory",
                            "expected_phase": expected_phase_num,
                            "actual_phase": actual_phase,
                        }
                    )

        # Check for required metadata in the file
        violations.extend(self._check_file_metadata(file_path))

        return violations

    def _convert_phase_name_to_number(self, phase_name: str) -> str:
        """Convert phase name to number."""
        phase_map = {
            "zero": "0",
            "one": "1",
            "two": "2",
            "three": "3",
            "four_five_six_seven": "4567",
            "eight": "8",
            "nine": "9",
        }
        return phase_map.get(phase_name.lower(), phase_name)

    def _check_file_metadata(self, file_path: Path) -> List[Dict]:
        """Check if the file contains required metadata."""
        violations = []

        try:
            content = file_path.read_text(encoding="utf-8")

            # Check for required metadata fields
            required_fields = [
                "__version__",
                "__phase__",
                "__stage__",
                "__order__",
                "__criticality__",
                "__execution_pattern__",
            ]

            for field in required_fields:
                if f"{field} = " not in content and f"{field}=" not in content:
                    violations.append(
                        {
                            "type": "MISSING_METADATA",
                            "file": str(file_path),
                            "severity": "WARNING",
                            "message": f"Missing required metadata field {field} in {file_path.name}",
                        }
                    )

        except Exception as e:
            violations.append(
                {
                    "type": "FILE_READ_ERROR",
                    "file": str(file_path),
                    "severity": "ERROR",
                    "message": f"Could not read file {file_path}: {str(e)}",
                }
            )

        return violations

    def enforce_phase_modules(self, phases_dir: str, dry_run: bool = True) -> Dict:
        """Enforce compliance for phase modules."""
        violations = self.scan_phase_modules(phases_dir)

        if not violations:
            print("✅ All phase modules are compliant!")
            return {"violations_found": 0, "violations_fixed": 0, "dry_run": dry_run}

        print(f"Found {len(violations)} violations in phase modules:")
        for i, violation in enumerate(violations, 1):
            print(f"  {i}. [{violation['severity']}] {violation['message']}")

        if not dry_run:
            fixed_count = self._fix_phase_module_violations(violations)
            print(f"Fixed {fixed_count} violations")

        return {
            "violations_found": len(violations),
            "violations_fixed": self._fix_phase_module_violations(violations) if not dry_run else 0,
            "dry_run": dry_run,
        }

    def _fix_phase_module_violations(self, violations: List[Dict]) -> int:
        """Attempt to fix phase module violations."""
        fixed_count = 0

        for violation in violations:
            if violation["type"] == "INVALID_NAMING_PATTERN":
                # Try to fix by renaming the file to follow the correct pattern
                file_path = Path(violation["file"])
                if self._attempt_rename_phase_file(file_path, violation.get("expected_phase")):
                    fixed_count += 1

        return fixed_count

    def _attempt_rename_phase_file(self, file_path: Path, expected_phase: str) -> bool:
        """Attempt to rename a phase file to follow correct naming."""
        if not expected_phase:
            return False

        # Extract stem without extension
        stem = file_path.stem

        # Create a valid name: phaseX_YY_ZZ_basename.py
        # For now, use default stage/order values
        new_name = f"phase{expected_phase[0]}_10_00_{stem.replace('-', '_').lower()}.py"
        new_path = file_path.parent / new_name

        print(f"    Renaming {file_path.name} → {new_name}")

        # Actually rename the file
        try:
            file_path.rename(new_path)
            return True
        except Exception as e:
            print(f"    Failed to rename {file_path}: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Phase Module Nomenclature Enforcer")
    parser.add_argument(
        "--path",
        default="./src/farfan_pipeline/phases",
        help="Path to phases directory (default: ./src/farfan_pipeline/phases)",
    )
    parser.add_argument("--fix", action="store_true", help="Apply fixes (otherwise dry run)")

    args = parser.parse_args()

    enforcer = PhaseModuleEnforcer()
    result = enforcer.enforce_phase_modules(args.path, dry_run=not args.fix)

    print(f"\n📊 Phase Module Enforcement Summary:")
    print(f"   Violations found: {result['violations_found']}")
    print(f"   Violations fixed: {result['violations_fixed']}")
    print(f"   Dry run: {result['dry_run']}")


if __name__ == "__main__":
    main()
