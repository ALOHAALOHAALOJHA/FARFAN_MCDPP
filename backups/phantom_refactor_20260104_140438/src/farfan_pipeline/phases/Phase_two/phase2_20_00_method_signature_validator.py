"""
Module: phase2_20_00_method_signature_validator
PHASE_LABEL: Phase 2
Sequence: G

"""
"""
Method Signature Chain Layer Validation

Implements chain layer validation for method signatures to ensure:
- Required inputs are properly declared (hard failure if missing)
- Optional inputs are classified (nice to have)
- Critical optional inputs are identified (penalize if missing)
- Output types and ranges are properly specified
- Signature completeness across all methods

This module provides signature governance for the analysis pipeline.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, TypedDict


class MethodSignature(TypedDict):
    required_inputs: list[str]
    optional_inputs: list[str]
    critical_optional: list[str]
    output_type: str
    output_range: list[float] | None
    description: str


class SignatureValidationResult(TypedDict):
    is_valid: bool
    missing_fields: list[str]
    issues: list[str]
    warnings: list[str]


class ValidationReport(TypedDict):
    validation_timestamp: str
    signatures_version: str
    total_methods: int
    valid_methods: int
    invalid_methods: int
    incomplete_methods: int
    methods_with_warnings: int
    validation_details: dict[str, SignatureValidationResult]
    summary: dict[str, Any]


class MethodSignatureValidator:
    """
    Validates method signatures for chain layer compliance.

    Ensures all methods have proper signature declarations with:
    - Required fields: required_inputs, output_type
    - Recommended fields: optional_inputs, critical_optional, output_range
    """

    REQUIRED_SIGNATURE_FIELDS = {"required_inputs", "output_type"}
    RECOMMENDED_SIGNATURE_FIELDS = {
        "optional_inputs",
        "critical_optional",
        "output_range",
    }
    ALL_SIGNATURE_FIELDS = (
        REQUIRED_SIGNATURE_FIELDS | RECOMMENDED_SIGNATURE_FIELDS | {"description"}
    )

    VALID_OUTPUT_TYPES = {"float", "int", "dict", "list", "str", "bool", "tuple", "Any"}

    def __init__(self, signatures_path: Path | str) -> None:
        self.signatures_path = Path(signatures_path)
        self.signatures_data: dict[str, Any] = {}
        self.validation_cache: dict[str, SignatureValidationResult] = {}

    def load_signatures(self) -> None:
        """Load method signatures from JSON file."""
        if not self.signatures_path.exists():
            raise FileNotFoundError(
                f"Signatures file not found: {self.signatures_path}"
            )

        with open(self.signatures_path) as f:
            self.signatures_data = json.load(f)

        if "methods" not in self.signatures_data:
            raise ValueError("Invalid signatures file: missing 'methods' key")

    def validate_signature(
        self, method_id: str, signature: dict[str, Any]
    ) -> SignatureValidationResult:
        """
        Validate a single method signature.

        Classification:
        - required_inputs: MUST be present, hard failure if missing at runtime
        - optional_inputs: Nice to have, no penalty if missing
        - critical_optional: Penalize if missing, but don't fail hard
        """
        is_valid = True
        missing_fields = []
        issues = []
        warnings = []

        # Check required fields
        for field in self.REQUIRED_SIGNATURE_FIELDS:
            if field not in signature:
                is_valid = False
                missing_fields.append(field)
                issues.append(f"Missing required field: {field}")

        # Check recommended fields
        for field in self.RECOMMENDED_SIGNATURE_FIELDS:
            if field not in signature:
                warnings.append(f"Missing recommended field: {field}")

        # Validate required_inputs
        if "required_inputs" in signature:
            if not isinstance(signature["required_inputs"], list):
                is_valid = False
                issues.append("required_inputs must be a list")
            elif len(signature["required_inputs"]) == 0:
                warnings.append(
                    "required_inputs is empty - method has no mandatory inputs"
                )
            else:
                # Validate input names
                for inp in signature["required_inputs"]:
                    if not isinstance(inp, str):
                        is_valid = False
                        issues.append(f"Invalid required input (not a string): {inp}")

        # Validate optional_inputs
        if "optional_inputs" in signature:
            if not isinstance(signature["optional_inputs"], list):
                is_valid = False
                issues.append("optional_inputs must be a list")
            else:
                for inp in signature["optional_inputs"]:
                    if not isinstance(inp, str):
                        is_valid = False
                        issues.append(f"Invalid optional input (not a string): {inp}")

        # Validate critical_optional
        if "critical_optional" in signature:
            if not isinstance(signature["critical_optional"], list):
                is_valid = False
                issues.append("critical_optional must be a list")
            else:
                # Check that critical_optional items are in optional_inputs
                optional_inputs = signature.get("optional_inputs", [])
                for inp in signature["critical_optional"]:
                    if not isinstance(inp, str):
                        is_valid = False
                        issues.append(
                            f"Invalid critical_optional input (not a string): {inp}"
                        )
                    elif inp not in optional_inputs:
                        warnings.append(
                            f"critical_optional input '{inp}' not found in optional_inputs"
                        )

        # Validate output_type
        if "output_type" in signature:
            output_type = signature["output_type"]
            if not isinstance(output_type, str):
                is_valid = False
                issues.append("output_type must be a string")
            elif output_type not in self.VALID_OUTPUT_TYPES:
                warnings.append(
                    f"output_type '{output_type}' not in standard types: {self.VALID_OUTPUT_TYPES}"
                )

        # Validate output_range
        if "output_range" in signature:
            output_range = signature["output_range"]
            if output_range is not None:
                if not isinstance(output_range, list):
                    is_valid = False
                    issues.append("output_range must be a list or null")
                elif len(output_range) != 2:
                    is_valid = False
                    issues.append(
                        "output_range must have exactly 2 elements [min, max]"
                    )
                else:
                    try:
                        min_val, max_val = float(output_range[0]), float(
                            output_range[1]
                        )
                        if min_val >= max_val:
                            is_valid = False
                            issues.append("output_range min must be less than max")
                    except (ValueError, TypeError):
                        is_valid = False
                        issues.append("output_range values must be numeric")

        # Check for unknown fields
        unknown_fields = set(signature.keys()) - self.ALL_SIGNATURE_FIELDS
        if unknown_fields:
            warnings.append(f"Unknown fields in signature: {unknown_fields}")

        return SignatureValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            issues=issues,
            warnings=warnings,
        )

    def validate_all_signatures(self) -> ValidationReport:
        """Validate all method signatures and generate comprehensive report."""
        if not self.signatures_data:
            self.load_signatures()

        methods = self.signatures_data.get("methods", {})
        validation_details: dict[str, SignatureValidationResult] = {}

        valid_count = 0
        invalid_count = 0
        incomplete_count = 0
        warnings_count = 0

        for method_id, method_data in methods.items():
            # Handle both flat structure and nested signature structure
            if "signature" in method_data:
                signature = method_data["signature"]
            else:
                signature = method_data

            result = self.validate_signature(method_id, signature)
            validation_details[method_id] = result

            if result["is_valid"]:
                valid_count += 1
            else:
                invalid_count += 1

            if result["missing_fields"]:
                incomplete_count += 1

            if result["warnings"]:
                warnings_count += 1

        # Generate summary statistics
        total_methods = len(methods)
        completeness_rate = (
            (valid_count / total_methods * 100) if total_methods > 0 else 0.0
        )

        # Analyze input patterns
        required_inputs_stats: dict[str, int] = {}
        optional_inputs_stats: dict[str, int] = {}
        critical_optional_stats: dict[str, int] = {}
        output_type_stats: dict[str, int] = {}

        for method_id, method_data in methods.items():
            if "signature" in method_data:
                signature = method_data["signature"]
            else:
                signature = method_data

            # Count required inputs
            for inp in signature.get("required_inputs", []):
                required_inputs_stats[inp] = required_inputs_stats.get(inp, 0) + 1

            # Count optional inputs
            for inp in signature.get("optional_inputs", []):
                optional_inputs_stats[inp] = optional_inputs_stats.get(inp, 0) + 1

            # Count critical optional
            for inp in signature.get("critical_optional", []):
                critical_optional_stats[inp] = critical_optional_stats.get(inp, 0) + 1

            # Count output types
            output_type = signature.get("output_type", "unknown")
            output_type_stats[output_type] = output_type_stats.get(output_type, 0) + 1

        summary = {
            "completeness_rate": round(completeness_rate, 2),
            "methods_with_required_fields": valid_count,
            "methods_missing_required_fields": invalid_count,
            "methods_with_incomplete_signatures": incomplete_count,
            "most_common_required_inputs": sorted(
                required_inputs_stats.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "most_common_optional_inputs": sorted(
                optional_inputs_stats.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "most_common_critical_optional": sorted(
                critical_optional_stats.items(), key=lambda x: x[1], reverse=True
            )[:5],
            "output_type_distribution": output_type_stats,
        }

        return ValidationReport(
            validation_timestamp=datetime.utcnow().isoformat() + "Z",
            signatures_version=self.signatures_data.get(
                "signatures_version", "unknown"
            ),
            total_methods=total_methods,
            valid_methods=valid_count,
            invalid_methods=invalid_count,
            incomplete_methods=incomplete_count,
            methods_with_warnings=warnings_count,
            validation_details=validation_details,
            summary=summary,
        )

    def generate_validation_report(self, output_path: Path | str) -> None:
        """Generate and save validation report to JSON file."""
        report = self.validate_all_signatures()
        output_path = Path(output_path)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        print(f"Validation report generated: {output_path}")
        print(f"Total methods: {report['total_methods']}")
        print(f"Valid methods: {report['valid_methods']}")
        print(f"Invalid methods: {report['invalid_methods']}")
        print(f"Completeness rate: {report['summary']['completeness_rate']}%")

    def check_signature_completeness(self, method_id: str) -> bool:
        """
        Check if a method has complete signature with all required fields.

        Returns:
            True if signature has all required fields, False otherwise
        """
        if not self.signatures_data:
            self.load_signatures()

        methods = self.signatures_data.get("methods", {})
        if method_id not in methods:
            return False

        method_data = methods[method_id]
        signature = method_data.get("signature", method_data)

        result = self.validate_signature(method_id, signature)
        return result["is_valid"]

    def get_method_signature(self, method_id: str) -> MethodSignature | None:
        """Retrieve method signature by ID."""
        if not self.signatures_data:
            self.load_signatures()

        methods = self.signatures_data.get("methods", {})
        if method_id not in methods:
            return None

        method_data = methods[method_id]
        if "signature" in method_data:
            return method_data["signature"]
        return method_data


def validate_signatures_cli() -> None:
    """CLI entry point for signature validation."""
    import sys

    signatures_path = "config/json_files_ no_schemas/method_signatures.json"
    output_path = "signature_validation_report.json"

    if len(sys.argv) > 1:
        signatures_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    validator = MethodSignatureValidator(signatures_path)
    validator.generate_validation_report(output_path)


if __name__ == "__main__":
    validate_signatures_cli()
