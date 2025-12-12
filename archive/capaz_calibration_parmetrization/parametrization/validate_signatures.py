#!/usr/bin/env python3
"""
Signature Validation Tool

Validates the integrity and consistency of extracted method signatures:
- Checks JSON schema compliance
- Validates normalized notation
- Detects duplicates
- Verifies cross-references
- Reports anomalies

Usage:
    python validate_signatures.py
    python validate_signatures.py --signatures method_signatures.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


class SignatureValidator:
    def __init__(self, signatures_path: Path) -> None:
        self.signatures_path = signatures_path
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.signatures_data: dict[str, Any] = {}

    def validate(self) -> bool:
        if not self.signatures_path.exists():
            self.errors.append(f"Signatures file not found: {self.signatures_path}")
            return False

        try:
            with open(self.signatures_path, "r", encoding="utf-8") as f:
                self.signatures_data = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

        self._validate_metadata()
        self._validate_signatures_structure()
        self._validate_normalized_names()
        self._validate_parameter_consistency()
        self._detect_duplicates()
        self._validate_hardcoded_params()

        return len(self.errors) == 0

    def _validate_metadata(self) -> None:
        if "_metadata" not in self.signatures_data:
            self.errors.append("Missing _metadata section")
            return

        metadata = self.signatures_data["_metadata"]
        required_fields = ["cohort_id", "creation_date", "wave_version", "total_signatures"]

        for field in required_fields:
            if field not in metadata:
                self.errors.append(f"Missing metadata field: {field}")

        if "cohort_id" in metadata and metadata["cohort_id"] != "COHORT_2024":
            self.warnings.append(f"Unexpected cohort_id: {metadata['cohort_id']}")

    def _validate_signatures_structure(self) -> None:
        if "signatures" not in self.signatures_data:
            self.errors.append("Missing signatures section")
            return

        signatures = self.signatures_data["signatures"]
        if not isinstance(signatures, dict):
            self.errors.append("Signatures section must be a dictionary")
            return

        required_fields = [
            "module", "class_name", "method_name", "required_inputs",
            "optional_inputs", "critical_optional", "output_type",
            "output_range", "hardcoded_parameters", "docstring", "line_number"
        ]

        for sig_name, sig_data in signatures.items():
            if not isinstance(sig_data, dict):
                self.errors.append(f"Invalid signature data for {sig_name}")
                continue

            for field in required_fields:
                if field not in sig_data:
                    self.errors.append(f"Missing field '{field}' in signature {sig_name}")

            if "module" in sig_data and not sig_data["module"]:
                self.errors.append(f"Empty module name in signature {sig_name}")

            if "method_name" in sig_data and not sig_data["method_name"]:
                self.errors.append(f"Empty method name in signature {sig_name}")

            if "line_number" in sig_data and not isinstance(sig_data["line_number"], int):
                self.errors.append(f"Invalid line_number in signature {sig_name}")

    def _validate_normalized_names(self) -> None:
        signatures = self.signatures_data.get("signatures", {})

        for sig_name, sig_data in signatures.items():
            module = sig_data.get("module", "")
            class_name = sig_data.get("class_name")
            method_name = sig_data.get("method_name", "")

            if class_name:
                expected_name = f"{module}.{class_name}.{method_name}"
            else:
                expected_name = f"{module}.{method_name}"

            if sig_name != expected_name:
                self.errors.append(
                    f"Normalized name mismatch: key='{sig_name}', expected='{expected_name}'"
                )

            if ".." in sig_name:
                self.errors.append(f"Invalid normalized name (double dots): {sig_name}")

            if sig_name.startswith(".") or sig_name.endswith("."):
                self.errors.append(f"Invalid normalized name (leading/trailing dot): {sig_name}")

    def _validate_parameter_consistency(self) -> None:
        signatures = self.signatures_data.get("signatures", {})

        for sig_name, sig_data in signatures.items():
            required = set(sig_data.get("required_inputs", []))
            optional = set(sig_data.get("optional_inputs", []))
            critical = set(sig_data.get("critical_optional", []))

            overlap = required & optional
            if overlap:
                self.errors.append(
                    f"Parameters in both required and optional in {sig_name}: {overlap}"
                )

            not_in_optional = critical - optional
            if not_in_optional:
                self.errors.append(
                    f"Critical parameters not in optional list in {sig_name}: {not_in_optional}"
                )

            all_params = required | optional
            if "self" in all_params:
                self.warnings.append(f"'self' parameter found in {sig_name}")
            if "cls" in all_params:
                self.warnings.append(f"'cls' parameter found in {sig_name}")

    def _detect_duplicates(self) -> None:
        signatures = self.signatures_data.get("signatures", {})

        method_locations: dict[str, list[str]] = {}

        for sig_name, sig_data in signatures.items():
            module = sig_data.get("module", "")
            class_name = sig_data.get("class_name", "")
            method_name = sig_data.get("method_name", "")

            key = f"{module}:{class_name}:{method_name}"
            if key not in method_locations:
                method_locations[key] = []
            method_locations[key].append(sig_name)

        for key, locations in method_locations.items():
            if len(locations) > 1:
                self.warnings.append(f"Possible duplicate method: {locations}")

    def _validate_hardcoded_params(self) -> None:
        signatures = self.signatures_data.get("signatures", {})

        for sig_name, sig_data in signatures.items():
            hardcoded = sig_data.get("hardcoded_parameters", [])

            if not isinstance(hardcoded, list):
                self.errors.append(f"Invalid hardcoded_parameters type in {sig_name}")
                continue

            for param in hardcoded:
                if not isinstance(param, dict):
                    self.errors.append(f"Invalid hardcoded parameter entry in {sig_name}")
                    continue

                required_fields = ["function", "variable", "value", "line", "type"]
                for field in required_fields:
                    if field not in param:
                        self.errors.append(
                            f"Missing field '{field}' in hardcoded parameter in {sig_name}"
                        )

    def print_report(self) -> None:
        print("=" * 70)
        print("SIGNATURE VALIDATION REPORT")
        print("=" * 70)
        print()

        if not self.signatures_data:
            print("No data loaded")
            return

        metadata = self.signatures_data.get("_metadata", {})
        print(f"Cohort ID:        {metadata.get('cohort_id', 'N/A')}")
        print(f"Wave Version:     {metadata.get('wave_version', 'N/A')}")
        print(f"Total Signatures: {metadata.get('total_signatures', 0)}")
        print()

        if self.errors:
            print(f"❌ ERRORS FOUND: {len(self.errors)}")
            print("-" * 70)
            for i, error in enumerate(self.errors, 1):
                print(f"  {i}. {error}")
            print()
        else:
            print("✅ No errors found")
            print()

        if self.warnings:
            print(f"⚠️  WARNINGS: {len(self.warnings)}")
            print("-" * 70)
            for i, warning in enumerate(self.warnings, 1):
                print(f"  {i}. {warning}")
            print()
        else:
            print("✅ No warnings")
            print()

        print("=" * 70)
        if self.errors:
            print("VALIDATION FAILED")
        else:
            print("VALIDATION PASSED")
        print("=" * 70)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate method signatures JSON")
    parser.add_argument(
        "--signatures",
        type=Path,
        default=None,
        help="Path to method_signatures.json (default: auto-detect)"
    )

    args = parser.parse_args()

    if args.signatures:
        signatures_path = args.signatures.resolve()
    else:
        repo_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        signatures_path = repo_root / "src" / "cross_cutting_infrastrucuture" / "capaz_calibration_parmetrization" / "parametrization" / "method_signatures.json"

    validator = SignatureValidator(signatures_path)
    is_valid = validator.validate()
    validator.print_report()

    return 0 if is_valid else 1


if __name__ == "__main__":
    sys.exit(main())
