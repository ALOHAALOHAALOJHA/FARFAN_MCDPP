#!/usr/bin/env python3
"""
Canonic Questionnaire Central Enforcer
Enforces rigid naming policies for questionnaire files
"""
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple
import shutil


class QuestionnaireEnforcer:
    """Enforces naming policies for questionnaire files."""

    def __init__(self):
        self.questionnaire_pattern = re.compile(r"^Q\d{3}_.*\.json$")
        self.violations = []

    def scan_questionnaire_files(self, questionnaire_dir: str) -> List[Dict]:
        """Scan questionnaire files for naming violations."""
        violations = []

        q_dir = Path(questionnaire_dir)
        if not q_dir.exists():
            return violations

        # Check all JSON files in the directory
        for json_file in q_dir.rglob("*.json"):
            violations.extend(self._check_questionnaire_naming(json_file))

        return violations

    def _check_questionnaire_naming(self, file_path: Path) -> List[Dict]:
        """Check if a questionnaire file follows the correct naming convention."""
        violations = []

        # Check if filename matches the QXXX pattern
        if not self.questionnaire_pattern.match(file_path.name):
            violations.append(
                {
                    "type": "INVALID_QUESTIONNAIRE_NAMING",
                    "file": str(file_path),
                    "severity": "ERROR",
                    "message": f"Questionnaire file {file_path.name} does not match required pattern: QXXX_*.json",
                }
            )

        # Check for required content structure in questionnaire files
        violations.extend(self._check_questionnaire_content(file_path))

        return violations

    def _check_questionnaire_content(self, file_path: Path) -> List[Dict]:
        """Check if questionnaire file has required content structure."""
        violations = []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)

            # Check for required questionnaire structure
            required_fields = ["questions", "metadata", "schema_version"]
            for field in required_fields:
                if field not in content:
                    violations.append(
                        {
                            "type": "MISSING_QUESTIONNAIRE_FIELD",
                            "file": str(file_path),
                            "severity": "ERROR",
                            "message": f'Missing required field "{field}" in questionnaire {file_path.name}',
                        }
                    )

        except json.JSONDecodeError:
            violations.append(
                {
                    "type": "INVALID_JSON",
                    "file": str(file_path),
                    "severity": "CRITICAL",
                    "message": f"Invalid JSON in questionnaire file {file_path.name}",
                }
            )
        except Exception as e:
            violations.append(
                {
                    "type": "FILE_READ_ERROR",
                    "file": str(file_path),
                    "severity": "ERROR",
                    "message": f"Could not read questionnaire file {file_path}: {str(e)}",
                }
            )

        return violations

    def enforce_questionnaires(self, questionnaire_dir: str, dry_run: bool = True) -> Dict:
        """Enforce compliance for questionnaire files."""
        violations = self.scan_questionnaire_files(questionnaire_dir)

        if not violations:
            print("✅ All questionnaire files are compliant!")
            return {"violations_found": 0, "violations_fixed": 0, "dry_run": dry_run}

        print(f"Found {len(violations)} violations in questionnaire files:")
        for i, violation in enumerate(violations, 1):
            print(f"  {i}. [{violation['severity']}] {violation['message']}")

        if not dry_run:
            fixed_count = self._fix_questionnaire_violations(violations)
            print(f"Fixed {fixed_count} violations")

        return {
            "violations_found": len(violations),
            "violations_fixed": (
                self._fix_questionnaire_violations(violations) if not dry_run else 0
            ),
            "dry_run": dry_run,
        }

    def _fix_questionnaire_violations(self, violations: List[Dict]) -> int:
        """Attempt to fix questionnaire violations."""
        fixed_count = 0

        for violation in violations:
            if violation["type"] == "INVALID_QUESTIONNAIRE_NAMING":
                # Try to fix by renaming the file to follow the correct pattern
                file_path = Path(violation["file"])
                if self._attempt_rename_questionnaire_file(file_path):
                    fixed_count += 1
            elif violation["type"] == "INVALID_JSON":
                # Try to fix by creating a minimal valid questionnaire
                file_path = Path(violation["file"])
                if self._attempt_fix_invalid_json(file_path):
                    fixed_count += 1

        return fixed_count

    def _attempt_rename_questionnaire_file(self, file_path: Path) -> bool:
        """Attempt to rename a questionnaire file to follow correct naming."""
        # Extract potential question number from filename
        stem = file_path.stem
        # Look for any 3-digit number in the stem
        import re

        matches = re.findall(r"\d{3}", stem)

        if matches:
            # Use the first 3-digit number found
            q_num = matches[0]
        else:
            # If no 3-digit number found, use a default
            q_num = "999"

        new_name = f"Q{q_num}_{stem.replace('-', '_').lower()}.json"
        new_path = file_path.parent / new_name

        print(f"    Renaming {file_path.name} → {new_name}")

        # Actually rename the file
        try:
            file_path.rename(new_path)
            return True
        except Exception as e:
            print(f"    Failed to rename {file_path}: {e}")
            return False

    def _attempt_fix_invalid_json(self, file_path: Path) -> bool:
        """Attempt to fix an invalid JSON file by creating a minimal valid questionnaire."""
        minimal_q = {
            "schema_version": "1.0.0",
            "metadata": {
                "created": "2025-01-07T00:00:00Z",
                "updated": "2025-01-07T00:00:00Z",
                "source": "auto-generated",
                "status": "draft",
            },
            "questions": [],
            "validation_rules": {},
        }

        print(f"    Fixing invalid JSON in {file_path.name}")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(minimal_q, f, indent=2)
            return True
        except Exception as e:
            print(f"    Failed to fix JSON in {file_path}: {e}")
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Canonic Questionnaire Central Enforcer")
    parser.add_argument(
        "--path",
        default="./canonic_questionnaire_central",
        help="Path to questionnaire directory (default: ./canonic_questionnaire_central)",
    )
    parser.add_argument("--fix", action="store_true", help="Apply fixes (otherwise dry run)")

    args = parser.parse_args()

    enforcer = QuestionnaireEnforcer()
    result = enforcer.enforce_questionnaires(args.path, dry_run=not args.fix)

    print(f"\n📊 Questionnaire Enforcement Summary:")
    print(f"   Violations found: {result['violations_found']}")
    print(f"   Violations fixed: {result['violations_fixed']}")
    print(f"   Dry run: {result['dry_run']}")


if __name__ == "__main__":
    main()
